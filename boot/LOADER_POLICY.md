# Loader Policy

Only core/runtime/loader.py may directly read startup authority files during bootstrap.

## Allowed reads
- _SYSTEM_IDENTITY.md
- _ROOT_AUTHORITY_MAP.md
- _BOOT_PROTOCOL.md
- _NAMING_CANON.md
- IMPLEMENTATION_MAPPING.md
- STATE_ARTIFACT_BOUNDARIES.md
- boot/AI_OS.boot.json
- boot/registry.json
- boot/registry.lock.json
- boot/plugin_map.json

## Forbidden
- direct boot reads by cli.py
- direct boot reads by lifecycle.py
- direct boot reads by router.py
- direct boot reads by status.py
- direct boot reads by child cores
- self-bootstrap by research, refinement, or pm layers