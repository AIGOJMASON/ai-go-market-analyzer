# INHERITANCE CONTRACT

## What it is

Governed ingress contract for `contractor_proposals_core`.

## Why it is there

Defines the bounded conditions under which a PM inheritance packet may enter
contractor proposal child-core execution state.

## Lawful Entry Rule

This child core may only activate from:
- a PM-produced inheritance packet
- a lawful PM child-core ingress receipt
- an active registry state

## Required Ingress Truth

A valid ingress receipt must include:
- `packet_id`
- `target_core_id`
- `target_core_path`
- `inheritance_packet_path`
- `domain_focus`
- `status = delivered`

## Illegal Entry Conditions

The child core must reject:
- raw research packets
- incomplete PM artifacts
- unverified runtime artifacts
- direct engine output as authority
- ingress receipts addressed to another core
- inheritance packets whose domain focus is not `contractor_proposals`