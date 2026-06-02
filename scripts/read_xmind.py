#!/usr/bin/env python3
"""Read XMind files and output structured text outline.

Usage:
    python read_xmind.py <file.xmind> [--format json|markdown|text]

Supports XMind Zen/2020+ (JSON) and XMind 8 (XML) formats.
Zero external dependencies — uses only Python standard library.
"""
import json
import sys
import xml.etree.ElementTree as ET
import zipfile


def read_xmind(file_path):
    with zipfile.ZipFile(file_path, "r") as zf:
        names = zf.namelist()
        if "content.json" in names:
            raw = zf.read("content.json").decode("utf-8")
            return json.loads(raw)
        elif "content.xml" in names:
            raw = zf.read("content.xml").decode("utf-8")
            return parse_xmind_xml(raw)
        else:
            raise ValueError("Not a valid XMind file: missing content.json or content.xml")


def parse_xmind_xml(xml_string):
    root = ET.fromstring(xml_string)
    sheets = []
    for sheet_elem in root.findall("sheet"):
        sheet = {"id": sheet_elem.get("id", ""), "title": _xml_text(sheet_elem, "title")}
        topic_elem = sheet_elem.find("topic")
        if topic_elem is not None:
            sheet["rootTopic"] = parse_topic_xml(topic_elem)
        sheets.append(sheet)
    return sheets


def parse_topic_xml(elem):
    topic = {"id": elem.get("id", ""), "title": _xml_text(elem, "title")}
    notes_elem = elem.find("notes/plain")
    if notes_elem is not None and notes_elem.text:
        topic["notes"] = {"plain": {"content": notes_elem.text}}
    labels_elem = elem.find("labels")
    if labels_elem is not None:
        topic["labels"] = [lbl.text for lbl in labels_elem.findall("label") if lbl.text]
    markers_elem = elem.find("marker-refs")
    if markers_elem is not None:
        topic["markers"] = [m.get("marker-id", "") for m in markers_elem.findall("marker-ref")]
    children_elem = elem.find("children/topics")
    if children_elem is not None:
        attached = [parse_topic_xml(c) for c in children_elem.findall("topic")]
        if attached:
            topic["children"] = {"attached": attached}
    return topic


def _xml_text(elem, tag):
    child = elem.find(tag)
    return child.text if child is not None and child.text else ""


def _get_labels(topic):
    return topic.get("labels", [])


def _get_notes(topic):
    return topic.get("notes", {}).get("plain", {}).get("content", "")


def _get_markers(topic):
    raw = topic.get("markers", [])
    result = []
    for m in raw:
        if isinstance(m, dict):
            result.append(m.get("markerId", str(m)))
        else:
            result.append(m)
    return result


def _get_children(topic):
    return topic.get("children", {}).get("attached", [])


def topic_to_text(topic, depth=0):
    indent = "  " * depth
    title = topic.get("title", "(untitled)")
    parts = [f"{indent}- {title}"]

    labels = _get_labels(topic)
    if labels:
        parts[0] += f"  [{', '.join(labels)}]"

    markers = _get_markers(topic)
    if markers:
        parts[0] += f"  <{' '.join(markers)}>"

    notes = _get_notes(topic)
    if notes:
        for line in notes.strip().split("\n"):
            parts.append(f"{indent}  > {line.strip()}")

    for child in _get_children(topic):
        parts.append(topic_to_text(child, depth + 1))

    return "\n".join(parts)


def topic_to_markdown(topic, depth=0):
    indent = "#" * (depth + 2)
    title = topic.get("title", "(untitled)")
    parts = [f"{indent} {title}"]

    labels = _get_labels(topic)
    if labels:
        parts.append(f"  Labels: {', '.join(labels)}")

    markers = _get_markers(topic)
    if markers:
        parts.append(f"  Markers: {', '.join(markers)}")

    notes = _get_notes(topic)
    if notes:
        parts.append("")
        parts.append(notes.strip())

    parts.append("")

    for child in _get_children(topic):
        parts.append(topic_to_markdown(child, depth + 1))

    return "\n".join(parts)


def xmind_to_text(file_path):
    sheets = read_xmind(file_path)
    parts = []
    for sheet in sheets:
        header = f"# {sheet.get('title', 'Untitled Sheet')}"
        root = sheet.get("rootTopic", {})
        if root:
            outline = topic_to_text(root, depth=0)
            parts.append(f"{header}\n{outline}")
        else:
            parts.append(header)
    return "\n\n".join(parts)


def xmind_to_markdown(file_path):
    sheets = read_xmind(file_path)
    parts = []
    for sheet in sheets:
        header = f"# {sheet.get('title', 'Untitled Sheet')}"
        root = sheet.get("rootTopic", {})
        if root:
            outline = topic_to_markdown(root, depth=0)
            parts.append(f"{header}\n{outline}")
        else:
            parts.append(header)
    return "\n\n".join(parts)


def xmind_to_json(file_path):
    return json.dumps(read_xmind(file_path), ensure_ascii=False, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python read_xmind.py <file.xmind> [--format json|markdown|text]", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    fmt = "text"
    if len(sys.argv) >= 4 and sys.argv[2] == "--format":
        fmt = sys.argv[3]

    try:
        if fmt == "json":
            print(xmind_to_json(file_path))
        elif fmt == "markdown":
            print(xmind_to_markdown(file_path))
        else:
            print(xmind_to_text(file_path))
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
