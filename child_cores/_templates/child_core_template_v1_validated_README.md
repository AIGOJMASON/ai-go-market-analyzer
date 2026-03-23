# CHILD CORE TEMPLATE v1 (VALIDATED)

This template represents a **fully validated child-core architecture** derived from a working, probe-passing implementation.

Purpose:
- eliminate rebuild overhead
- enforce structural + governance consistency
- accelerate new core creation (contractor_builder, GIS, etc.)

Status:
- validated
- probe-compliant
- not bound to any domain

Usage:
1. copy scaffold/ into new core directory
2. replace all {{TOKENS}}
3. implement domain-specific execution + outputs
4. register core in:
   - child_core_registry.json
   - pm registry
5. run probes
6. move to validated → activation

This template guarantees:
- lawful inheritance
- watcher enforcement
- approval gating
- structured output
- CLI/UI testability