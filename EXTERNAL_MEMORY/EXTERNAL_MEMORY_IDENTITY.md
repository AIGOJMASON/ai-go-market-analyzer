# EXTERNAL MEMORY IDENTITY

Name:
EXTERNAL_MEMORY

Authority Type:
Governed external-memory admission authority

System Role:
Determine whether already-governed external information deserves durable
storage for future retrieval and child-core use.

Core Definition:
EXTERNAL_MEMORY is the bounded authority that sits between governed
external informational ingress and durable persistence.

It does not decide whether signal is true in the abstract.
It decides whether signal has paid enough cost to deserve storage.

Primary Inputs:
- governed research packets
- governed live/source packets
- governed operator-submitted external packets

Primary Outputs:
- qualification decisions
- rejection receipts
- persistence receipts
- durable external-memory records

Relationship to SMI:
SMI governs system self-memory from closed internal history.
EXTERNAL_MEMORY governs storage admission for external weighted input.

SMI remembers what the system has lived through.
EXTERNAL_MEMORY remembers what the system has lawfully accepted from the world.

Relationship to RESEARCH_CORE:
RESEARCH_CORE transforms raw signal into governed research packets.
EXTERNAL_MEMORY does not replace that work.
It begins only after governed input exists.

Relationship to PM_CORE:
PM_CORE decides strategic posture and downstream use.
EXTERNAL_MEMORY decides whether a record deserves durable storage for
future retrieval.

Authority Boundaries:
EXTERNAL_MEMORY may:
- inspect governed input metadata
- score persistence worthiness
- reject weak persistence candidates
- commit qualified records through the persistence gate
- emit bounded receipts

EXTERNAL_MEMORY may not:
- bypass RESEARCH_CORE
- bypass PM_CORE
- execute child-core logic
- mutate runtime state
- mutate SMI continuity
- promote records directly into training-grade memory without later phases

Design Law:
Durable storage is not a default outcome.
It is a governed privilege granted only after qualification.

Why It Exists:
The system already contains strong return-side governance for committed
memory. What is missing is an admission-side gate that decides whether
external input deserves storage before the database accumulates entropy.

Success Condition:
A governed external record enters durable storage only when:
- source quality clears floor
- total persistence weight clears threshold
- contamination or redundancy does not disqualify it
- decision and write are both receipted

Failure Condition:
Weak, noisy, low-quality, redundant, or contaminated records are rejected
before durable storage and remain visible only through explicit receipts.