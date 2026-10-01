// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

//! The GitHub request layer (ADR-1810). SPC-1080 states the behaviour.
//!
//! Every request the `github` feature sends goes through [`Layer`], which runs
//! `gh api --include` and reads the status line, the headers and the body of
//! each response, a refused one included. It tells a replay from `--cache`
//! apart from a fresh response, turns a header into a wait through [`wait`]
//! alone, and stops the run at a throttle unless `--wait` asks it to sleep.
//! It keeps four counts for the run, primary requests, secondary points,
//! content creation and the spacing of writes, checks them before each
//! request and stops at a ceiling as at a throttle.
//!
//! The clock is the system's. Where `MEOW_GITHUB_CLOCK` names a file, the
//! layer reads the time from it and sleeps by adding the seconds to it, so the
//! unit's fixtures run without waiting in real time.

use serde_json::Value;
use std::collections::BTreeMap;
use std::process::{Command, Stdio};

/// The most a run sleeps in all: a primary reset is at most an hour away, so
/// a run still throttled after an hour has another cause.
const HOUR: u64 = 3_600;
/// A cached response whose `Date` lies this many seconds or more before the
/// call started, on GitHub's clock, is a replay.
const REPLAY: f64 = 60.0;
/// The first wait at a secondary throttle that states none, doubled for each
/// further one in the run.
const SECONDARY: u64 = 60;
/// The window GitHub counts secondary points and the minute's content
/// creation over.
const MINUTE: f64 = 60.0;
/// The secondary points a run may spend in a minute: 1 for a `GET`, 5 for
/// any other method.
const POINTS: u32 = 900;
/// The `POST` requests a run may send in a minute, and in an hour.
const CREATES_A_MINUTE: usize = 80;
const CREATES_AN_HOUR: usize = 500;
/// The least time between one write and the next.
const SPACING: f64 = 1.0;
const MONTHS: [&str; 12] = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

/// Why a request gave the caller no body.
pub(crate) enum Failure {
    /// The run is throttled: the `throttled:` line to print, after which it
    /// sends nothing more.
    Throttled(String),
    /// GitHub refused the call: the `refused:` line to print, naming the
    /// method, the endpoint and the permission (REQ-2574).
    Refused(String),
    /// GitHub rejected the credential: the `unauthenticated:` line to print,
    /// after which the run sends nothing more (REQ-3326).
    Rejected(String),
    /// Anything else, as `gh` or GitHub said it.
    Failed(String),
}

impl std::fmt::Display for Failure {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Failure::Throttled(line)
            | Failure::Refused(line)
            | Failure::Rejected(line)
            | Failure::Failed(line) => f.write_str(line),
        }
    }
}

/// A wait a response stated, or implied, before the next request may go.
#[derive(Clone)]
struct Stop {
    /// The seconds to wait from `arrived`, or `None` where the header didn't
    /// parse in its unit.
    wait: Option<u64>,
    /// The local time the response arrived.
    arrived: f64,
    /// The response's `Date`, in UTC epoch seconds.
    date: Option<i64>,
    header: String,
    value: String,
}

/// The run's request layer: one per run, so the offset, the waits slept and
/// the held resources cover the run alone.
pub(crate) struct Layer {
    wait: bool,
    sent: bool,
    /// The local clock less GitHub's, from the last uncached response.
    offset: Option<f64>,
    /// The `Date` of the run's first response, in UTC epoch seconds.
    first: Option<i64>,
    slept: u64,
    secondary: u32,
    /// Each resource a fresh response left at `remaining: 0`, with its reset.
    held: BTreeMap<String, Stop>,
    /// The requests the run sent, a replay not among them.
    requests: u64,
    /// Whether GitHub has answered 401 in this run, after which the layer
    /// sends nothing, because rejected requests count towards a lockout of
    /// the account's valid credentials too.
    rejected: bool,
    /// For each `x-ratelimit-resource`, the limit, remaining and reset the
    /// last fresh response stated.
    primary: BTreeMap<String, [String; 3]>,
    /// When each request was sent, with the secondary points it cost.
    points: Vec<(f64, u32)>,
    /// When each `POST` was sent.
    creates: Vec<f64>,
    /// The writes sent, and when the last one's answer arrived.
    writes: u64,
    last_write: Option<f64>,
}

struct Response {
    status: u16,
    headers: Vec<(String, String)>,
    body: Value,
}

impl Response {
    fn header(&self, name: &str) -> Option<&str> {
        self.headers
            .iter()
            .find(|(n, _)| n.eq_ignore_ascii_case(name))
            .map(|(_, v)| v.as_str())
    }
}

impl Layer {
    /// A layer that sleeps at a throttle where `wait` is set, and otherwise
    /// stops the run there.
    pub(crate) fn new(wait: bool) -> Self {
        Layer {
            wait,
            sent: false,
            offset: None,
            first: None,
            slept: 0,
            secondary: 0,
            held: BTreeMap::new(),
            requests: 0,
            rejected: false,
            primary: BTreeMap::new(),
            points: Vec::new(),
            creates: Vec::new(),
            writes: 0,
            last_write: None,
        }
    }

    /// The four counts, one line each, as the last lines of a run's report
    /// (REQ-2568).
    pub(crate) fn budget(&self) -> Vec<String> {
        let at = now();
        let resources = if self.primary.is_empty() {
            "no response stated a limit".to_string()
        } else {
            self.primary
                .iter()
                .map(|(resource, [limit, remaining, reset])| {
                    format!(
                        "{resource} limit {}, {} remaining, resets {}",
                        grouped(limit),
                        grouped(remaining),
                        reset
                            .trim()
                            .parse::<i64>()
                            .map_or_else(|_| reset.clone(), utc)
                    )
                })
                .collect::<Vec<_>>()
                .join("; ")
        };
        vec![
            format!(
                "primary requests: {} sent; {resources}",
                grouped(&self.requests.to_string())
            ),
            format!(
                "secondary points: {} of {POINTS} this minute",
                self.points_within(at)
            ),
            format!(
                "content creation: {} of {CREATES_A_MINUTE} this minute, {} of {CREATES_AN_HOUR} this hour",
                within(&self.creates, at, MINUTE),
                within(&self.creates, at, HOUR as f64)
            ),
            format!(
                "spacing: {} {}, each at least one second after the previous one",
                self.writes,
                if self.writes == 1 { "write" } else { "writes" }
            ),
        ]
    }

    fn points_within(&self, at: f64) -> u32 {
        self.points
            .iter()
            .filter(|(sent, _)| *sent > at - MINUTE)
            .map(|(_, cost)| cost)
            .sum()
    }

    /// The ceiling `method` would pass if it were sent now, as the wait until
    /// the count frees enough and the count's name, or `None` where it passes
    /// none.
    fn ceiling(&self, method: &str, at: f64) -> Option<(f64, String)> {
        let cost = if method == "GET" { 1 } else { 5 };
        let spent = self.points_within(at);
        if spent + cost > POINTS {
            let mut left = spent + cost - POINTS;
            let mut frees = at;
            for (sent, points) in self.points.iter().filter(|(s, _)| *s > at - MINUTE) {
                frees = sent + MINUTE;
                left = left.saturating_sub(*points);
                if left == 0 {
                    break;
                }
            }
            return Some((
                frees - at,
                format!("secondary points: {spent} of {POINTS} this minute"),
            ));
        }
        if method != "POST" {
            return None;
        }
        for (window, most, name) in [
            (MINUTE, CREATES_A_MINUTE, "this minute"),
            (HOUR as f64, CREATES_AN_HOUR, "this hour"),
        ] {
            let inside: Vec<f64> = self
                .creates
                .iter()
                .copied()
                .filter(|s| *s > at - window)
                .collect();
            if inside.len() >= most {
                let frees = inside[inside.len() - most] + window;
                return Some((
                    frees - at,
                    format!("content creation: {} of {most} {name}", inside.len()),
                ));
            }
        }
        None
    }

    /// Reads `endpoint`, through `gh`'s cache for an hour where `cache` is set,
    /// except on the run's first call, which is always sent fresh.
    pub(crate) fn get(&mut self, endpoint: &str, cache: bool) -> Result<Value, Failure> {
        self.exchange("GET", endpoint, &[], cache, false)
            .map(|r| r.body)
    }

    /// Reads `endpoint`, an object the record says exists, so a 404 on it is
    /// reported as a refusal that may be the object hidden from the credential.
    pub(crate) fn get_mapped(&mut self, endpoint: &str) -> Result<Value, Failure> {
        self.exchange("GET", endpoint, &[], false, true)
            .map(|r| r.body)
    }

    /// Sends `method` to `endpoint` with each field as `-f name=value`. A
    /// `PATCH` goes to an object the record says exists.
    pub(crate) fn write(
        &mut self,
        method: &str,
        endpoint: &str,
        fields: &[(&str, &str)],
    ) -> Result<Value, Failure> {
        self.exchange(method, endpoint, fields, false, method == "PATCH")
            .map(|r| r.body)
    }

    /// When the run began on GitHub's clock, as the `Date` of its first
    /// response, written as `2026-09-29T14:30:37Z`; `None` until a response
    /// states one.
    pub(crate) fn began(&self) -> Option<String> {
        self.first.map(utc)
    }

    /// Reads one page of a listing, through `gh`'s cache where `cache` is set,
    /// returning its body and the address of the next page that its `Link`
    /// header names.
    pub(crate) fn page(
        &mut self,
        endpoint: &str,
        cache: bool,
    ) -> Result<(Value, Option<String>), Failure> {
        self.exchange("GET", endpoint, &[], cache, false).map(|r| {
            let next = r.header("link").and_then(next_page);
            (r.body, next)
        })
    }

    fn exchange(
        &mut self,
        method: &str,
        endpoint: &str,
        fields: &[(&str, &str)],
        cache: bool,
        mapped: bool,
    ) -> Result<Response, Failure> {
        if self.rejected {
            return Err(Failure::Rejected(format!(
                "unauthenticated: {method} {endpoint} not sent, because GitHub rejected this run's credential"
            )));
        }
        loop {
            if let Some(stop) = self.held.get(resource_of(endpoint)).cloned() {
                self.stop(method, endpoint, &stop)?;
                self.held.remove(resource_of(endpoint));
            }
            if let Some((wait, count)) = self.ceiling(method, now()) {
                let arrived = now();
                self.stop(
                    method,
                    endpoint,
                    &Stop {
                        wait: Some(wait.max(0.0).ceil() as u64),
                        arrived,
                        date: None,
                        header: count,
                        value: String::new(),
                    },
                )?;
                continue;
            }
            if method != "GET"
                && let Some(last) = self.last_write
            {
                let left = last + SPACING - now();
                if left > 0.0 {
                    sleep(left);
                }
            }
            let cached = cache && self.sent;
            self.sent = true;
            let mut args = vec!["api".to_string(), endpoint.to_string()];
            if method != "GET" {
                args.extend(["-X".to_string(), method.to_string()]);
            }
            for (name, value) in fields {
                args.extend(["-f".to_string(), format!("{name}={value}")]);
            }
            args.push("--include".to_string());
            if cached {
                args.extend(["--cache".to_string(), "1h".to_string()]);
            }
            let started = now();
            let out = Command::new("gh")
                .args(&args)
                .env("GH_PROMPT_DISABLED", "1")
                .stdin(Stdio::null())
                .output()
                .map_err(|e| {
                    Failure::Failed(format!(
                        "gh couldn't run ({e}); install GitHub's client, gh, and sign in with `gh auth login`"
                    ))
                })?;
            let arrived = now();
            if method != "GET" {
                self.writes += 1;
                self.last_write = Some(arrived);
            }
            let said = String::from_utf8_lossy(&out.stderr).trim().to_string();
            let response = match parse(&String::from_utf8_lossy(&out.stdout)) {
                Ok(response) => response,
                Err(e) if out.status.success() || said.is_empty() => {
                    return Err(Failure::Failed(format!(
                        "gh exited with {}: {e}",
                        out.status
                    )));
                }
                Err(_) => return Err(Failure::Failed(said)),
            };
            let date = response.header("date").and_then(http_date);
            self.first = self.first.or(date);
            let fresh = if cached {
                match (self.offset, date) {
                    (Some(offset), Some(date)) => date as f64 > started - offset - REPLAY,
                    _ => true,
                }
            } else {
                if let Some(date) = date {
                    self.offset = Some(arrived - date as f64);
                }
                true
            };
            if fresh {
                self.requests += 1;
                self.points
                    .push((started, if method == "GET" { 1 } else { 5 }));
                if method == "POST" {
                    self.creates.push(started);
                }
                let stated = [
                    "x-ratelimit-limit",
                    "x-ratelimit-remaining",
                    "x-ratelimit-reset",
                ]
                .map(|name| response.header(name).unwrap_or("").trim().to_string());
                if let Some(resource) = response.header("x-ratelimit-resource")
                    && !stated[0].is_empty()
                {
                    self.primary.insert(resource.trim().to_string(), stated);
                }
            }
            let stop = |header: &str, value: &str| Stop {
                wait: wait(
                    "github",
                    header,
                    value,
                    response.header("date").unwrap_or(""),
                ),
                arrived,
                date,
                header: header.to_string(),
                value: value.to_string(),
            };
            let spent = response.header("x-ratelimit-remaining").map(str::trim) == Some("0");
            let reset = response.header("x-ratelimit-reset").unwrap_or("");
            let message = response
                .body
                .get("message")
                .and_then(Value::as_str)
                .unwrap_or("");
            let retry_after = response.header("retry-after");
            let throttled = response.status == 429
                || (response.status == 403
                    && (retry_after.is_some()
                        || spent
                        || message.to_lowercase().contains("secondary rate limit")));
            if throttled {
                let stop = if let Some(value) = retry_after {
                    stop("retry-after", value)
                } else if spent {
                    stop("x-ratelimit-reset", reset)
                } else {
                    let wait = SECONDARY << self.secondary.min(6);
                    self.secondary += 1;
                    Stop {
                        wait: Some(wait),
                        arrived,
                        date,
                        header: "a secondary rate limit, which states no wait".to_string(),
                        value: String::new(),
                    }
                };
                self.stop(method, endpoint, &stop)?;
                continue;
            }
            if fresh && (200..300).contains(&response.status) {
                let resource = response
                    .header("x-ratelimit-resource")
                    .unwrap_or(resource_of(endpoint))
                    .to_string();
                if spent {
                    self.held.insert(resource, stop("x-ratelimit-reset", reset));
                } else {
                    self.held.remove(&resource);
                }
            }
            if (200..300).contains(&response.status) {
                return Ok(response);
            }
            let why = if message.is_empty() {
                said
            } else {
                message.to_string()
            };
            // GitHub's own reason, where the line doesn't already quote it
            // (REQ-3324).
            let reason = |quoted: bool| {
                if quoted || message.is_empty() {
                    String::new()
                } else {
                    format!("; GitHub said \"{}\"", printable(message))
                }
            };
            return Err(match response.status {
                401 => {
                    self.rejected = true;
                    Failure::Rejected(format!(
                        "unauthenticated: {method} {endpoint}{}",
                        reason(false)
                    ))
                }
                403 => {
                    let (needs, quoted) = permission(&response, &why);
                    Failure::Refused(format!(
                        "refused: {method} {endpoint} needs {needs}{}",
                        reason(quoted)
                    ))
                }
                404 if mapped => {
                    let (needs, quoted) = permission(&response, &why);
                    Failure::Refused(format!(
                        "refused: {method} {endpoint} needs {needs}, or it is hidden from this credential{}",
                        reason(quoted)
                    ))
                }
                status => Failure::Failed(format!("HTTP {status}: {}", one_line(&why))),
            });
        }
    }

    /// Sleeps out `stop` under `--wait`, while the run's waits stay within an
    /// hour, and otherwise stops the run as throttled.
    fn stop(&mut self, method: &str, endpoint: &str, stop: &Stop) -> Result<(), Failure> {
        let Some(wait) = stop.wait else {
            return Err(Failure::Throttled(format!(
                "throttled: {method} {endpoint}, retry after unknown ({}: `{}` doesn't parse in its unit)",
                stop.header, stop.value
            )));
        };
        let reference = stop
            .date
            .unwrap_or_else(|| (stop.arrived - self.offset.unwrap_or(0.0)) as i64);
        let line = format!(
            "throttled: {method} {endpoint}, retry after {} ({})",
            utc(reference + wait as i64),
            stop.header
        );
        if !self.wait || self.slept + wait > HOUR {
            return Err(Failure::Throttled(line));
        }
        self.slept += wait;
        let left = stop.arrived + wait as f64 - now();
        if left > 0.0 {
            sleep(left);
        }
        Ok(())
    }
}

/// The permission a refused call needed, as GitHub named it: its fine-grained
/// permissions, or else the scopes it accepts beside the credential's own, or
/// else GitHub's message, quoted, where it named neither; and whether the text
/// already quotes GitHub's message.
fn permission(response: &Response, message: &str) -> (String, bool) {
    let stated = |name: &str| {
        response
            .header(name)
            .map(str::trim)
            .filter(|value| !value.is_empty())
    };
    if let Some(permissions) = stated("x-accepted-github-permissions") {
        (permissions.to_string(), false)
    } else if let Some(scopes) = stated("x-accepted-oauth-scopes") {
        let own = stated("x-oauth-scopes").unwrap_or("none");
        (
            format!("one of the scopes {scopes}; the credential holds {own}"),
            false,
        )
    } else {
        (
            format!(
                "a permission: GitHub named no permission and said \"{}\"",
                printable(message)
            ),
            true,
        )
    }
}

/// GitHub's message as one line to quote, with a backslash and a double quote
/// escaped, so a message can't split a report's line or end its quotation.
fn printable(message: &str) -> String {
    one_line(message).replace('\\', "\\\\").replace('"', "\\\"")
}

/// GitHub's text on one line: a control character or a line or paragraph
/// separator becomes a space, so it can't split a report's line.
fn one_line(text: &str) -> String {
    text.chars()
        .map(|c| {
            if c.is_control() || c == '\u{2028}' || c == '\u{2029}' {
                ' '
            } else {
                c
            }
        })
        .collect()
}

/// The form of the credential `gh` authenticates with, from whether each
/// variable is set in the order of precedence `gh` documents, and whether the
/// run is inside a GitHub Actions workflow (REQ-2582). A token variable's
/// value is secret material, so it is never read beyond whether it is empty.
pub(crate) fn credential() -> String {
    let set = |name: &str| std::env::var_os(name).is_some_and(|v| !v.is_empty());
    let form = if set("GH_TOKEN") {
        "GH_TOKEN from the environment"
    } else if set("GITHUB_TOKEN") {
        "GITHUB_TOKEN from the environment"
    } else {
        "gh's stored credential"
    };
    if std::env::var("GITHUB_ACTIONS").as_deref() == Ok("true") {
        format!("{form}, inside a GitHub Actions workflow")
    } else {
        form.to_string()
    }
}

/// A count as GitHub's pages write it, with a comma between each group of
/// three digits; anything else as it is.
fn grouped(number: &str) -> String {
    if number.is_empty() || !number.bytes().all(|b| b.is_ascii_digit()) {
        return number.to_string();
    }
    let mut out = String::new();
    for (i, digit) in number.chars().enumerate() {
        if i > 0 && (number.len() - i).is_multiple_of(3) {
            out.push(',');
        }
        out.push(digit);
    }
    out
}

/// How many of `times` fall within `window` seconds before `at`.
fn within(times: &[f64], at: f64, window: f64) -> usize {
    times.iter().filter(|t| **t > at - window).count()
}

/// The resource GitHub counts a request against, before its answer names it.
fn resource_of(endpoint: &str) -> &'static str {
    let path = endpoint.trim_start_matches("https://api.github.com/");
    if path.starts_with("search/") {
        "search"
    } else if path.starts_with("graphql") {
        "graphql"
    } else {
        "core"
    }
}

/// The status line, the headers and the body `gh api --include` printed.
fn parse(out: &str) -> Result<Response, String> {
    let mut lines = out.split('\n');
    let status = lines
        .next()
        .filter(|l| l.starts_with("HTTP/"))
        .and_then(|l| l.split_whitespace().nth(1))
        .and_then(|s| s.parse().ok())
        .ok_or("gh printed no status line")?;
    let mut headers = Vec::new();
    for line in lines.by_ref() {
        let line = line.trim_end_matches('\r');
        if line.is_empty() {
            break;
        }
        if let Some((name, value)) = line.split_once(':') {
            headers.push((name.trim().to_string(), value.trim().to_string()));
        }
    }
    let rest = lines.collect::<Vec<_>>().join("\n");
    let body = if rest.trim().is_empty() {
        Value::Null
    } else {
        serde_json::from_str(rest.trim()).map_err(|e| format!("gh printed no JSON ({e})"))?
    };
    Ok(Response {
        status,
        headers,
        body,
    })
}

/// The address a `Link` header names as `rel="next"`, as a path `gh api` reads.
fn next_page(link: &str) -> Option<String> {
    link.split(',').find_map(|part| {
        let (address, params) = part.split_once(';')?;
        params
            .split(';')
            .any(|p| p.trim() == "rel=\"next\"")
            .then(|| {
                let address = address.trim().trim_start_matches('<').trim_end_matches('>');
                address
                    .strip_prefix("https://api.github.com/")
                    .unwrap_or(address)
                    .to_string()
            })
    })
}

/// The wait, in seconds from when the response arrived, that `header` holding
/// `value` gives under `service`'s table, measured against the response's
/// `Date`; `None` where the value doesn't parse in the table's unit. This is
/// the only conversion from a header to a duration (REQ-2578).
pub(crate) fn wait(service: &str, header: &str, value: &str, date: &str) -> Option<u64> {
    match (service, header.to_ascii_lowercase().as_str()) {
        // Seconds.
        ("github", "retry-after") => value.trim().parse().ok(),
        // UTC epoch seconds, measured to the response's `Date`.
        ("github", "x-ratelimit-reset") => {
            let reset: i64 = value.trim().parse().ok()?;
            Some(reset.saturating_sub(http_date(date)?).max(0) as u64)
        }
        _ => None,
    }
}

/// An HTTP date, such as `Tue, 29 Sep 2026 14:30:37 GMT`, in UTC epoch seconds.
fn http_date(text: &str) -> Option<i64> {
    let parts: Vec<&str> = text.split_whitespace().collect();
    let [_, day, month, year, time, "GMT"] = parts.as_slice() else {
        return None;
    };
    let month = MONTHS.iter().position(|m| m == month)? as i64 + 1;
    let clock: Vec<i64> = time
        .split(':')
        .map(|n| n.parse().ok())
        .collect::<Option<_>>()?;
    let [h, m, s] = clock.as_slice() else {
        return None;
    };
    let days = days_from_civil(year.parse().ok()?, month, day.parse().ok()?);
    Some(days * 86_400 + h * 3_600 + m * 60 + s)
}

fn days_from_civil(year: i64, month: i64, day: i64) -> i64 {
    let y = if month <= 2 { year - 1 } else { year };
    let era = y.div_euclid(400);
    let yoe = y - era * 400;
    let doy = (153 * (month + if month > 2 { -3 } else { 9 }) + 2) / 5 + day - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146_097 + doe - 719_468
}

/// UTC epoch seconds as `2026-09-29T14:31:07Z`.
fn utc(epoch: i64) -> String {
    let (days, secs) = (epoch.div_euclid(86_400), epoch.rem_euclid(86_400));
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1_460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let day = doy - (153 * mp + 2) / 5 + 1;
    let month = if mp < 10 { mp + 3 } else { mp - 9 };
    let year = yoe + era * 400 + i64::from(month <= 2);
    format!(
        "{year:04}-{month:02}-{day:02}T{:02}:{:02}:{:02}Z",
        secs / 3_600,
        secs % 3_600 / 60,
        secs % 60
    )
}

fn now() -> f64 {
    if let Some(file) = std::env::var_os("MEOW_GITHUB_CLOCK") {
        return std::fs::read_to_string(file)
            .ok()
            .and_then(|t| t.trim().parse().ok())
            .unwrap_or(0.0);
    }
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0)
}

fn sleep(seconds: f64) {
    if let Some(file) = std::env::var_os("MEOW_GITHUB_CLOCK") {
        let _ = std::fs::write(file, (now() + seconds).to_string());
        return;
    }
    std::thread::sleep(std::time::Duration::from_secs_f64(seconds));
}

#[cfg(test)]
mod tests {
    use super::{
        Failure, Layer, admits, create_issue_endpoint, governance, one_line, printable,
        update_issue_endpoint, wait,
    };

    /// TSK-2980 criterion 1, REQ-2576: a write off the allow list is refused
    /// before `gh` starts, so the answer is the layer's refusal and never
    /// anything `gh` or GitHub said.
    #[test]
    fn a_write_off_the_allow_list_starts_no_gh() {
        let writes = [
            ("PATCH", "repos/o/r"),
            ("PUT", "repos/o/r/branches/main/protection"),
            ("POST", "repos/o/r/rulesets"),
            ("PUT", "repos/o/r/actions/permissions/workflow"),
            ("PUT", "repos/o/r/contents/.github/workflows/ci.yml"),
        ];
        for (method, endpoint) in writes {
            assert!(admits(method, endpoint).is_err(), "{method} {endpoint}");
            let mut layer = Layer::new(false);
            match layer.write(method, endpoint, &[]) {
                Err(Failure::Refused(line)) => assert_eq!(
                    line,
                    format!(
                        "refused by meow-github: {method} {endpoint} isn't a write this pack makes"
                    )
                ),
                _ => panic!("{method} {endpoint} wasn't refused by the layer"),
            }
        }
    }

    /// TSK-2980 criterion 2, REQ-2576: no write on the allow list touches
    /// governance.
    #[test]
    fn no_allowed_write_is_governance() {
        for endpoint in [create_issue_endpoint("o/r"), update_issue_endpoint("o/r", 7)] {
            assert!(!governance(&endpoint), "{endpoint}");
        }
        for endpoint in [
            "repos/o/r",
            "repos/o/r/branches/main/protection",
            "repos/o/r/rulesets/1",
            "repos/o/r/actions/permissions/workflow",
            "repos/o/r/actions/workflows/9/enable",
            "repos/o/r/actions/secrets/X",
            "repos/o/r/actions/variables/X",
            "repos/o/r/environments/prod",
            "repos/o/r/hooks/3",
            "repos/o/r/collaborators/ada",
            "repos/o/r/contents/.github/workflows/ci.yml",
        ] {
            assert!(governance(endpoint), "{endpoint}");
        }
    }

    /// TSK-2980 criterion 3, REQ-2576: the crate builds a write only through
    /// the two allow-list endpoints, so no other module calls `write`.
    #[test]
    fn every_built_write_is_allowed() {
        assert!(admits("POST", &create_issue_endpoint("o/r")).is_ok());
        assert!(admits("PATCH", &update_issue_endpoint("o/r", 7)).is_ok());
        let src = Path::new(env!("CARGO_MANIFEST_DIR")).join("src");
        let mut files = vec![src.join("github.rs")];
        for entry in std::fs::read_dir(src.join("github")).expect("src/github reads") {
            let path = entry.expect("an entry reads").path();
            if path.extension().is_some_and(|e| e == "rs") && !path.ends_with("request.rs") {
                files.push(path);
            }
        }
        let call = concat!(".write", "(");
        for file in files {
            let text = std::fs::read_to_string(&file).expect("a source file reads");
            assert!(!text.contains(call), "{} calls write", file.display());
        }
    }

    /// TSK-4030, REQ-3324: a message quoted in a report stays on one line and
    /// inside its quotation marks.
    #[test]
    fn a_quoted_message_stays_on_its_line() {
        assert_eq!(printable("Bad credentials"), "Bad credentials");
        assert_eq!(printable("two\nlines"), "two lines");
        assert_eq!(printable("say \"no\""), "say \\\"no\\\"");
        assert_eq!(printable("a\\\"b"), "a\\\\\\\"b");
        assert_eq!(printable("C:\\"), "C:\\\\");
        assert_eq!(one_line("a\u{2028}b\rc"), "a b c");
    }
    use std::path::Path;

    /// TSK-2940 criterion 4, REQ-2578: `x-ratelimit-reset` counts UTC epoch
    /// seconds, so the pair RES-0290 observed gives 3,207 seconds. Read as
    /// milliseconds it would give about 3.2 seconds, or a reset in 1970.
    #[test]
    fn reset_is_read_in_epoch_seconds() {
        let (reset, date) = (1_790_695_444_u64, "Tue, 29 Sep 2026 14:30:37 GMT");
        assert_eq!(
            wait("github", "x-ratelimit-reset", &reset.to_string(), date),
            Some(3_207)
        );
        assert_eq!(
            wait("github", "X-Ratelimit-Reset", &reset.to_string(), date),
            Some(3_207),
            "header names compare without regard to case"
        );
        assert_eq!((reset - 1_790_692_237) / 1000, 3);
        assert!(reset / 1000 < 31_536_000, "as milliseconds it lies in 1970");
    }

    /// TSK-2940 criterion 8, REQ-2566: only `github/request.rs` starts `gh` in
    /// the `github` feature, so no call escapes the layer's reading of limits.
    #[test]
    fn only_the_layer_starts_gh() {
        let src = Path::new(env!("CARGO_MANIFEST_DIR")).join("src");
        let mut files = vec![src.join("github.rs")];
        for entry in std::fs::read_dir(src.join("github")).expect("src/github reads") {
            let path = entry.expect("an entry reads").path();
            if path.extension().is_some_and(|e| e == "rs") {
                files.push(path);
            }
        }
        let starts = concat!("Command::", "new(");
        let mut starting = Vec::new();
        for file in &files {
            let text = std::fs::read_to_string(file).expect("a source file reads");
            let gh = text.match_indices(starts).any(|(at, _)| {
                let argument = text[at + starts.len()..].trim_start();
                argument.starts_with("\"gh\"") || !argument.starts_with('"')
            });
            if gh {
                starting.push(file.strip_prefix(&src).unwrap().display().to_string());
            }
        }
        starting.sort();
        assert_eq!(starting, vec!["github/request.rs".to_string()]);
    }
}
