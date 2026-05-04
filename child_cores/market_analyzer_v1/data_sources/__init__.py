"""
Real data source surfaces for market_analyzer_v1.

This package is intentionally narrow:
- fetch external data
- normalize external data
- hand off to sealed AI_GO ingress

It does not:
- create PM packets outside canonical ingress
- mutate runtime logic
- admit memory
- shape dashboard output
"""