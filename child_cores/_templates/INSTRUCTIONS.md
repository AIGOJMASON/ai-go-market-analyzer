You run it by copying the scaffold into a new child core, replacing the template tokens, registering the new core, then running its probes and live harness.

For the template package itself, think of it as a starter mold, not a runnable core on its own. The raw template contains placeholders like {{CORE_ID}}, so you do not run the template directly.

How to use it
1. Copy the scaffold into a new core folder

Example:

xcopy /E /I AI_GO\child_cores\_templates\child_core_template_v1_validated\scaffold AI_GO\child_cores\contractor_builder_v1
2. Replace the template tokens

In the copied files, replace:

{{CORE_ID}} → contractor_builder_v1

{{DISPLAY_NAME}} → Contractor Builder V1

{{DOMAIN_FOCUS}} → whatever that core does

{{APPROVAL_RECORD_TYPE}} → the approval artifact that core requires

3. Fill in the domain-specific files

These are the ones you actually customize:

DOMAIN_POLICY.md

DOMAIN_REGISTRY.json

constraints/constraints.json

execution/*

outputs/*

ui/live_test_packet.py

PM interface / registry entries

4. Register the new core

Add it to:

AI_GO/child_cores/child_core_registry.json

AI_GO/PM_CORE/state/child_core_registry.json

5. Run its probes

Once the new core is real, run its probe files, for example:

python -m AI_GO.tests.stage_contractor_builder_v1_structure_probe
python -m AI_GO.tests.stage_contractor_builder_v1_ingress_validation_probe
python -m AI_GO.tests.stage_contractor_builder_v1_runtime_behavior_probe
python -m AI_GO.tests.stage_contractor_builder_v1_output_compliance_probe
python -m AI_GO.tests.stage_contractor_builder_v1_approval_gate_probe
6. Run the live harness

After the core passes, run its CLI/UI harness:

python -m AI_GO.child_cores.contractor_builder_v1.ui.live_cli_test
python -m AI_GO.child_cores.contractor_builder_v1.ui.live_ui_test
If you want to test the template package itself

You have two options.

Option A: instantiate a throwaway test core

Create something like:

AI_GO/child_cores/template_smoke_test_v1

from the scaffold, replace tokens, keep the minimal default logic, then run it.

Option B: keep the template as non-runnable infrastructure

This is cleaner. The template stays frozen, and only instantiated child cores are runnable.

The simplest mental model

_templates/child_core_template_v1_validated/ = blueprint

child_cores/market_analyzer_v1/ = built house

child_cores/contractor_builder_v1/ = next house built from same blueprint

So the answer is:

You do not run the template directly. You instantiate a new core from it, then run that instantiated core.

The next practical move is for me to turn this into a real contractor_builder_v1 instantiation in full paste.