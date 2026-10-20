<role>
What a reviewer of GDScript and Godot scenes checks that no command reports.
Read it when you review a Godot project, after `status` has named the engine
version. A clean `gdlint` says the linter found nothing in what it checks, and
each point here asks what it can't see.
</role>

<rules name="reviewing GDScript and scenes">
- R1. Report untyped GDScript, because static typing changes the generated code
  as well as the checking and the linter doesn't require it.
- R2. Check node lifetime: `_init` against `_ready`, `queue_free` and any
  reference that outlives the node, because a freed node's reference fails
  later and far from the cause.
- R3. Check who owns each signal connection, because a connection nobody
  disconnects is a reference nobody released.
- R4. Check scene ownership and `PackedScene` instancing, because the same scene
  is a template and an instance and the script doesn't show which.
- R5. Check what `@export` lets the inspector set, because it can set a value
  the code never expects.
- R6. Check that nothing touches the scene tree from another thread except
  through `call_deferred`, because the tree isn't thread-safe.
- R7. Look for a resource two nodes edit as if each owned a copy, because
  resources are shared mutable state.
- R8. For a `.gdshader`, check the render mode, the work placed in the vertex
  stage against the fragment stage, and the uniform names.
- R9. Read a `.tscn` change as a diff, because a node reparented is visible
  there and nowhere else.
- R10. Look for a second toolchain under a GDExtension, because a C++ build
  sits beneath the project and no Godot command reports it.
</rules>
