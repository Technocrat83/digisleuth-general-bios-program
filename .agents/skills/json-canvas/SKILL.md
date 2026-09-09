---
name: json-canvas
description: Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use for Obsidian Canvas, visual topology, mind maps, flowcharts, and Digisleuth computational morphology projections.
---

# JSON Canvas Skill — Digisleuth Vendored Instantiation

Upstream: `kepano/obsidian-skills` → `skills/json-canvas/SKILL.md`
Pinned upstream commit: `a1dc48e68138490d522c04cbf5822214c6eb1202`
License: MIT. See `LICENSE_UPSTREAM.md`.

This repo-local skill preserves the operational semantics of the upstream JSON Canvas skill and is constitutionally bound by `DIGISLEUTH_BINDING.md`.

## File structure

A `.canvas` file is JSON Canvas Spec 1.0 with two top-level arrays:

```json
{
  "nodes": [],
  "edges": []
}
```

## Create a canvas

1. Create a `.canvas` file with valid JSON.
2. Generate a unique 16-character lowercase hexadecimal ID for every node and edge.
3. Add node fields: `id`, `type`, `x`, `y`, `width`, `height`.
4. Add type-specific fields:
   - `text` node → `text`
   - `file` node → `file` and optional `subpath`
   - `link` node → `url`
   - `group` node → optional `label`, `background`, `backgroundStyle`
5. Add edges using valid `fromNode` and `toNode` references.
6. Validate JSON, ID uniqueness, required fields, and edge referential integrity before commit.

## Edit a canvas

1. Read and parse the existing `.canvas` file.
2. Preserve existing IDs unless object identity itself is intentionally replaced.
3. Locate the target node/edge by ID.
4. Modify only authorized attributes.
5. Write valid JSON.
6. Re-run all validation checks.

## Node types

Allowed node `type` values:

- `text`
- `file`
- `link`
- `group`

Generic node attributes:

- `id`: unique 16-char lowercase hex
- `type`
- `x`, `y`: integer coordinates; negative values allowed
- `width`, `height`: integer dimensions
- optional `color`: preset `"1"` through `"6"` or hex color

### Text nodes

Use Markdown text. JSON newlines must use `\n`, not a literal escaped `\\n` sequence intended for display.

### File nodes

`file` must be a path resolvable from the Obsidian vault. Prefer Markdown-backed Digisleuth objects for computational morphology.

### Group nodes

Groups are visual containers only. Grouping does not confer authority, standing, admission, or execution rights.

## Edges

Required:

- `id`
- `fromNode`
- `toNode`

Optional:

- `fromSide`, `toSide`: `top`, `right`, `bottom`, `left`
- `fromEnd`, `toEnd`: `none`, `arrow`
- `color`
- `label`

## Layout guidance

- Canvas extends infinitely; coordinates may be negative.
- `x` increases right; `y` increases down.
- Leave roughly 50–100 px between peer nodes.
- Align to a stable grid where useful.
- Avoid overlap unless overlap is intentionally meaningful topology.

## Validation checklist

Before every Git write:

1. JSON parses successfully.
2. All node and edge IDs are unique.
3. Every edge endpoint resolves to an existing node.
4. Every node has all required generic and type-specific fields.
5. Node types are valid.
6. Edge side/end values are valid.
7. File nodes reference intended vault-relative objects.
8. No Digisleuth authority, evidence, or transition edge is invented by visualization.

## Digisleuth invocation

When writing under the Obsidian Organ, read `DIGISLEUTH_BINDING.md` before creating or editing any `.canvas` file.

The Canvas skill is a rendering/compilation capability only:

`Canvas Write Authority != Constitutional Authority != Admission Authority != Execution Authority`.
