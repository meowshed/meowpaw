<role>
Release notes tell a reader who is upgrading what changes for them. The reader
needs the breaking change before anything else.
</role>

<rules name="sections, in order">
1. Header: Open with the version, the date and one sentence of summary.
2. Breaking: List breaking changes first, each with its migration path, because
   a reader who misses one learns about it in production.
3. Changes: Then features, improvements and fixes, each starting with a verb
   and naming the specific thing: "Fixed a race in token refresh when two
   requests arrived within 50 ms."
</rules>

<rules name="done">
It is done when a reader knows whether the upgrade breaks anything for them and
what to do about it.
</rules>
