# DOMAIN POLICY

domain: {{DOMAIN_FOCUS}}

allowed_actions:
- analyze
- classify
- filter
- recommend

forbidden_actions:
- execute trades
- external API calls
- bypass approval

approval_gate:
{{APPROVAL_RECORD_TYPE}}