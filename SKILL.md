---
name: xmind-reader
description: Read and parse XMind mind map files (.xmind). Use this skill whenever the user wants to read, view, or extract content from an XMind file, mentions a .xmind file, references a mind map or思维导图 file, or asks to understand the structure of an XMind document. Also use when the user shares an XMind file path and asks questions about its contents.
---

# XMind Reader

Read XMind mind map files and present their structure as readable text.

## When to use

The user provides an XMind file path or asks to read/understand a mind map. This skill parses the file and returns the full topic hierarchy.

## How to read an XMind file

Run the bundled script:

```bash
python3 scripts/read_xmind.py <file.xmind>
```

Optional format flag: `--format json|markdown|text` (default: text)

### Output formats

**text** (default): Indented outline with labels in `[...]`, notes prefixed with `>`, markers in `<...>`
```
- Central Topic
  - Subtopic 1 [label1, label2]
    > This is a note
  - Subtopic 2
    - Child topic
```

**markdown**: Hierarchical headings with notes as block text.

**json**: Raw parsed JSON structure from the XMind file.

## IMPORTANT: Hierarchical relationships

**The parent-child hierarchy is the most critical data in a mind map.** When reading an XMind file, you MUST preserve and present the full hierarchy — flat lists of topics lose the meaning of the map.

- **Always use the default `text` format** unless the user explicitly requests another format, because it best represents hierarchy through indentation.
- Do not flatten or summarize topics into a bullet list without showing their nesting depth.
- When the user asks about the content of a mind map, present the structure with its full depth so they can see which topics belong to which branches.
- If the map is large and you need to summarize, summarize by branch (subtree), not by stripping hierarchy.

## What gets extracted

- Topic titles (all levels, recursive)
- Labels attached to topics
- Plain text notes
- Markers/icons
- Sheet names (XMind files can have multiple sheets)
- **Parent-child hierarchical relationships** (the core structure of the map)

## Technical details

XMind files are ZIP archives. The script auto-detects the format:
- XMind Zen / 2020+ / 2026: parses `content.json`
- XMind 8 (legacy): parses `content.xml`

No external dependencies — uses only Python standard library.
