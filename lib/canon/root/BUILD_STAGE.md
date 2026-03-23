BUILD STAGE

Stage 1 — Boot Runtime

Tasks:

Implement ai_go boot

Boot must:
- load boot/AI_GO.boot.json
- load boot/registry.json
- load state/smi/current/smi_state.json
- initialize CORE runtime
- print system status

Expected output:

AI_GO STATUS
system booted
authorities loaded
SMI loaded

Files involved:

core/runtime/cli.py
core/runtime/lifecycle.py
core/runtime/loader.py
core/runtime/status.py
boot/AI_GO.boot.json
boot/registry.json
state/smi/current/smi_state.json