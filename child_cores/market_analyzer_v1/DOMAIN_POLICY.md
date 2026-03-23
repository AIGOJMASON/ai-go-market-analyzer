# DOMAIN_POLICY — market_analyzer_v1

## Domain

Market Intelligence — Necessity-Driven Rebound Strategy

---

## Domain Objective

Identify short-term rebound opportunities in necessity sectors following shock-driven mispricing.

---

## Domain Constraints

### 1. Market Participation Gate

Trading allowed only if:

- market regime is not unstable beyond threshold
- volatility allows structured entry/exit
- liquidity conditions are sufficient

---

### 2. Macro Filter

- provides directional bias only
- NEVER triggers trades
- NEVER overrides necessity filter

---

### 3. Necessity Filter (MANDATORY)

Allowed sectors ONLY:

- energy
- agriculture / fertilizer
- infrastructure
- critical technology

Any asset outside this set → rejected

---

### 4. Propagation Model

Events classified by:

- speed: fast / medium / slow
- depth: primary / secondary / tertiary impact

Used to determine:

- timing window
- candidate relevance

---

### 5. Rebound Validation (REQUIRED)

Trade candidates MUST show:

- stabilization after shock
- reclaim behavior (price/structure recovery)
- confirmation signal (structure or volume)
- acceptable entry window

Failure → no recommendation

---

## Disallowed Behavior

This core MUST NOT:

- generate speculative trades without shock origin
- chase momentum without validation
- recommend trades in non-necessity sectors
- hold positions beyond defined lifecycle
- produce narrative-driven output

---

## Output Discipline

Recommendations must be:

- structured
- minimal
- non-emotional
- non-predictive

---

## Risk Discipline

- small exposure per trade
- fast exit enforcement
- no averaging down logic
- no long-term holding

---

## Market Regime Classification

Allowed states:

- normal
- volatile
- crisis

Each state determines:

- participation level
- trade frequency
- allowed risk envelope

---

## Termination Conditions

Core must halt recommendation generation when:

- no valid rebound candidates exist
- propagation model invalidates timing
- market regime = unsafe