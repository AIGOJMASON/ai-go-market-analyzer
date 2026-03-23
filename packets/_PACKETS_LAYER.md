# PACKETS LAYER

## What it is
The packets layer stores governed packet artifacts produced by authority layers.

## Why it is there
It separates durable packet artifacts from runtime orchestration logic and prevents `wr.py` or `core/runtime/router.py` from becoming the owner of packet storage policy.

## Where it connects
- `RESEARCH_CORE/packets/packet_builder.py`
- `AI_GO/packets/research/`
- future watcher verification in `core/monitoring/`
- future continuity reflection in `core/continuity/`

## Active Phase One rule
- RESEARCH_CORE owns research packet construction
- RESEARCH_CORE owns research packet persistence
- runtime router may call persistence
- runtime router does not define packet storage policy
- watcher and SMI integration happen only after real packet files exist