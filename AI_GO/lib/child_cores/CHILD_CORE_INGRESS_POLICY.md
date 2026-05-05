# CHILD CORE INGRESS POLICY (NORTHSTAR ALIGNED)

## PURPOSE

Defines lawful entry of information into child cores.

---

## INGESTION LAW

Child cores MUST NOT receive:

- raw provider data
- direct API responses
- external signals

All ingress must follow:

External  
→ RESEARCH_CORE  
→ Engine Curation  
→ Adapter  
→ Child Core  

---

## ADAPTER AUTHORITY

Adapter is the ONLY translator.

It ensures:

- schema enforcement
- removal of unsafe fields
- domain shaping

Child cores trust adapter ONLY.

---

## FORBIDDEN ACTIONS

Child cores may NOT:

- call providers
- fetch data
- ingest raw payloads
- reinterpret external signals

---

## MUTATION LAW

Ingress does NOT mutate.

If ingress data is stored:

Persistence = Mutation  
→ full governance chain required

---

## EXECUTION LAW

execution_allowed = false

Ingress cannot trigger execution.

---

## SUMMARY

Ingress is:

→ CONTROLLED  
→ CURATED  
→ NON-AUTHORITATIVE