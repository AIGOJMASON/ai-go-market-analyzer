# CHILD CORE WATCHER POLICY (NORTHSTAR ALIGNED)

## PURPOSE

Defines watcher enforcement over child cores.

---

## WATCHER ROLE

Watcher:

- validates mutation requests
- checks workflow posture
- blocks unsafe operations

---

## WATCHER AUTHORITY

Watcher may:

- PASS
- BLOCK
- ESCALATE

Watcher may NOT:

- execute
- mutate state

---

## CHILD CORE REQUIREMENT

Child cores MUST:

- route all mutation through watcher
- accept watcher outcomes
- never bypass watcher

---

## MUTATION LAW

Watcher output is advisory.

If persisted:

Persistence = Mutation

---

## SUMMARY

Watcher = ENFORCEMENT LAYER

Child cores = SUBJECT TO IT