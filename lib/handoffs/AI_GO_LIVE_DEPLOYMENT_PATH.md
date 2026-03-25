# AI_GO — LIVE DEPLOYMENT PATH

## Purpose

This document defines the path from a validated local AI_GO child-core system to a live, externally accessible product.

It is based on the current state of the system:

- governed architecture
- unified `system_view` delivery pattern
- canonical `/operator` route
- validated probe ladder
- multiple child-core inheritance confirmed

The goal is not to redesign the system for production.

The goal is to **deploy the existing system safely and correctly**.

---

## Core Principle

Deployment does not change the system’s architecture.

It only changes:

- where the system runs
- who can access it
- what data it consumes

The following must remain unchanged:

- unified `system_view`
- `/operator` entrypoint
- governance invariants
- advisory-only posture (unless explicitly redesigned)
- probe-validated behavior

---

## What “Live” Means in AI_GO

A system is considered live when:

1. It is reachable outside localhost
2. It exposes:
   - API routes
   - operator UI
3. Access is controlled
4. Governance remains intact
5. The system behaves identically to its tested local form

---

## Deployment Phases

---

## Phase 1 — Local to Networked Service

### Objective

Make the system accessible beyond localhost.

### Action

Run the app with a public host binding:

```bash
uvicorn AI_GO.app:app --host 0.0.0.0 --port 8000
Result

The system becomes reachable at:

http://<machine-ip>:8000/operator
Notes
This is sufficient for internal testing across devices
No architecture changes are required
Phase 2 — Cloud Hosting
Objective

Move the system to a publicly accessible environment.

Options
VPS (DigitalOcean, Linode, etc.)
AWS EC2
Render / Railway (simpler managed platforms)
Requirements
Python runtime
project files
ability to run:
uvicorn AI_GO.app:app --host 0.0.0.0 --port 8000
Result

Public endpoints:

https://yourdomain.com/operator
https://yourdomain.com/<child-core>/run
https://yourdomain.com/<child-core>/run/live
Phase 3 — Access Control Layer
Objective

Prevent uncontrolled public access.

Required Controls
1. API Key Protection

All API routes should require:

x-api-key: <secret>
2. Operator UI Protection

Protect /operator using:

basic authentication, or
session-based login (future)
3. Rate Limiting

Limit request frequency to:

prevent abuse
maintain system stability
Important Rule

Access control wraps the system.

It does not change:

response structure
governance logic
delivery pattern
Phase 4 — Real Data Integration
Objective

Replace static or simulated inputs with real-world data.

Examples
Market Analyzer
price feeds
news APIs
macroeconomic data
Contractor Builder
material pricing
labor estimates
contractor profiles
Critical Constraint

The following must not change:

system_view structure
/operator behavior
outward delivery model

Only:

runtime inputs
refinement signals

are enhanced.

Phase 5 — Operator Experience Upgrade
Objective

Improve usability without changing system structure.

Current State
JSON-based panels
raw data rendering
Future Enhancements
formatted cards
highlighted signals
risk indicators
simplified summaries
Constraint

UI improvements must not:

fragment the system into multiple surfaces
expose internal layers as separate products
alter the canonical section structure
Phase 6 — Multi-Core Operator Hub
Objective

Unify multiple child cores under one operator interface.

Current State

Each child core has:

/operator
Future State

Single hub:

/operator
  → select child core

Example:

/operator?core=market-analyzer
/operator?core=contractor-builder
Why This Works

All child cores share:

identical outward structure
identical section model
identical governance presentation

This allows clean aggregation without translation layers.

Governance Requirements (Non-Negotiable)

The following must remain true in live deployment:

mode remains advisory unless explicitly redesigned
execution is not allowed by default
approval is required where defined
watcher and closeout signals remain visible
no hidden mutation of runtime or PM state
no autonomous action pathways are introduced
What Deployment Does NOT Do

Deployment does not:

add intelligence
change domain logic
alter PM structure
grant authority
remove safeguards
replace testing

It only exposes the system.

Minimal Viable Live Setup

A minimal, correct live deployment consists of:

Hosted FastAPI app
API key protection
/operator UI access
At least one child core active

No additional frontend is required.

Why AI_GO Is Ready for Deployment

The system already satisfies:

stable outward contract (system_view)
consistent operator interface (/operator)
governance enforcement
repeatable delivery pattern
validated probe ladder
multi-core compatibility

This eliminates the usual risks of:

inconsistent outputs
unclear UI
broken integration layers
uncontrolled system behavior
Strategic Outcome

AI_GO is structured such that:

deployment is a surface change, not a system rewrite
new child cores inherit deployment readiness
operator experience remains consistent across domains
system governance survives exposure
Final Statement

AI_GO goes live by exposing the system exactly as it exists:

governed internally, unified outwardly, and controlled at the boundary

No redesign is required.

Only controlled exposure.