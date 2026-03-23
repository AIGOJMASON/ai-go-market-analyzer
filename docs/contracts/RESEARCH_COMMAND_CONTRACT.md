# RESEARCH COMMAND CONTRACT

## Purpose

This document defines the canonical runtime input and output contract for the governed `research` command.

It exists to eliminate ambiguous command handling and prevent router from acting as an indefinite compatibility shim.

---

## Canonical Input Shape

The canonical research command payload is:

```json
{
  "command": "research",
  "args": {
    "title": "string",
    "summary": "string",
    "source_refs": ["string"],
    "scope": "core",
    "tags": ["research"],
    "notes": "optional string"
  }
}