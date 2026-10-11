// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * The router's model choice and answer handling, as plain functions a test
 * drives with a stand-in registry (BUG-1620): a model the person names goes
 * first, a catalogue whose Claude models name another provider still picks
 * one, a message that answers in a string or a block list yields its text,
 * a model that fails alone is skipped, and a catalogue where every model
 * fails names the last failure.
 */

export function pickModels(models, current, preferred) {
  const isPreferred = preferred
    ? (m) =>
        Boolean(m) &&
        (String(m.provider) === preferred ||
          new RegExp(preferred, "i").test(String(m.id)) ||
          new RegExp(preferred, "i").test(String(m.provider ?? "")))
    : () => false;
  const isClaude = (m) =>
    Boolean(m) && (m.provider === "anthropic" || /claude/i.test(String(m.id)));
  const ordered = models.filter(isPreferred);
  const rest = models.filter((m) => !isPreferred(m));
  ordered.push(...rest.filter(isClaude));
  if (current && !ordered.includes(current)) ordered.push(current);
  for (const m of rest) if (!isClaude(m) && m !== current) ordered.push(m);
  return [...new Map(ordered.map((m) => [m, m])).values()];
}

export function responseText(message) {
  if (!message) return { ok: false, reason: "the call returned nothing" };
  if (message.errorMessage)
    return { ok: false, reason: String(message.errorMessage) };
  if (message.stopReason === "error")
    return { ok: false, reason: "the model returned an error" };
  const content = message.content;
  if (typeof content === "string")
    return { ok: true, text: content.trim() };
  if (Array.isArray(content)) {
    const text = content
      .filter((b) => b && b.type === "text")
      .map((b) => b.text ?? "")
      .join("\n")
      .trim();
    if (text) return { ok: true, text };
  }
  return { ok: false, reason: "the model returned no text" };
}

export async function answerWith(models, attempt) {
  let last = "no model was available";
  for (const model of models) {
    try {
      const text = await attempt(model);
      if (text) return { ok: true, text };
      last = `${nameOf(model)}: returned no text`;
    } catch (error) {
      last = `${nameOf(model)}: ${error && error.message ? error.message : error}`;
    }
  }
  return { ok: false, reason: `meow-router: no model answered: ${last}` };
}

function nameOf(model) {
  return `${model?.provider ?? "?"}/${model?.id ?? "?"}`;
}