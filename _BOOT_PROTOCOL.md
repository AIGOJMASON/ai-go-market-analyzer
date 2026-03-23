# Boot Protocol

## Purpose
Constrain system startup into a single lawful authority path.

## Boot order
1. system identity
2. root authority map
3. naming canon
4. implementation mapping
5. state/artifact boundaries
6. boot manifest
7. registry validation
8. registry lock validation
9. plugin map load
10. runtime initialization
11. session lifecycle start

## Rules
- boot files define startup truth only
- no subsystem may self-bootstrap from disk directly
- runtime initialization must occur through loader.py
- unresolved or invalid startup state must terminate boot
- registry mismatch must terminate boot
- lock mismatch must terminate boot