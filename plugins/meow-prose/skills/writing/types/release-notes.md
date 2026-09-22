<role>
Release notes tell a reader who is upgrading what changes for them. The reader
needs the breaking change before anything else.
</role>

<rules name="sections, in order">
<rule id="header">Open with the version, the date and one sentence of
summary.</rule>
<rule id="breaking">List breaking changes first, each with its migration path,
because a reader who misses one learns about it in production.</rule>
<rule id="changes">Then features, improvements and fixes, each starting with a
verb and naming the specific thing: "Fixed a race in token refresh when two
requests arrived within 50 ms."</rule>
</rules>

<rules name="done">
<rule id="done">It is done when a reader knows whether the upgrade breaks
anything for them and what to do about it.</rule>
</rules>
