# Lens checklists — the six Discovery perspectives

The single owner of the six Discovery perspectives (`business` · `operations` · `user` · `data` · `governance` · `financial`): the central question of each, what it privileges, its cues, its own rules, and the evidence that proves it was covered. `handoff-v1` F3 (`docs/handoff-v1/F3/DESENHO.md` Q1) replaced the six lens skills with this file. **One** integrated analyst applies all six in a `/round`; `/round <perspective>` goes deeper on one with the same analyst. Six perspectives never mean six documents or six executions.

The analyst does not restate the rules this file points to. Admission of a question and the `Confirmed` threshold live in `library/kernel/states.md`; the coverage record lives in `library/kernel/coverage-contract.md` §4.8. The Options perspective (`lens-technology`) is not here: it names vendors, and Discovery never does.

## How the analyst works

**Inputs.** Shared evidence first: `_capture/evidence-index.md` is a **source map** — what sources exist, which are normalized, where that evidence lives, what failed or was skipped. Read the normalized evidence bearing on each perspective, not every file. Raw sources in `inputs/` stay openable: inspect one when material to confidence, never to fill a quota. Contract: `library/kernel/orchestration.md` → *Evidence contract*. The invocation carries the round context: round id, next free SU ids, the Shared Understanding, the enquadramento, and any pack attention cues.

**Outputs.**

1. **SU rows** — atomic material findings, one per row, with evidence and round. The `lens` column names the perspective the row answers.
2. **One coverage entry per perspective** — `assessed`, `gap` or `not_applicable`, with the references that prove it and a justification (*Coverage evidence* below).

Both go into the **draft copies** the caller opened (`_drafts/<id>/`), never in place; the caller publishes them in one operation (`library/kernel/orchestration.md` → *Writing an authority*).

**Pack cues.** The active pack may hand the round a list of extra cues per perspective (`lenses_config.<lens>.extra_signals`). They are cues, not coverage — same status as the cues below.

**Steps, for every perspective.**

1. **Understand the relevant evidence.** Shared first; raw when material to confidence. Expired `Confirmed`/`Assumed` rows are weak `Assumed`, not settled coverage.
2. **Apply the perspective** — its section below.
3. **Probe** material gaps, unstated assumptions and contradictions. A tension between perspectives goes to the governance conflict scan, which runs last.
4. **Contribute** the material findings: SU rows, stamped and priced.
5. **Expose uncertainty** — thin evidence becomes `Unknown` or `Assumed` with its basis, never a manufactured `Confirmed`. Every `Unknown` passes admission, whole, as the common rules state it: nothing is restated in the perspective sections. A question whose answers all lead to the same requirement is `cosmético` or is not written; a gap that is the organisation's and not the target's is not written at all.
6. **Record coverage** — one entry per perspective, from the evidence the rows cite.

**Order.** The five perspectives run in any order; the governance **conflict scan** runs after all of them, because it reads what the others stated. Its result is the coverage record's `conflict_scan`.

## Common rules

They bind every perspective.

1. No vendor/product names; an existing system may be named as *current state* (`.claude/rules/no-tech-mention-before-options.md`).
2. No `Confirmed` without a **machine-resolvable locator** of one of the classes in `library/kernel/states.md` → *Confirmed threshold*: a cell, formula or extractor locator; a transcript timestamp; a document paragraph; a dated declaration of the process owner (`answers.md#<secção>`, `enquadramento.md#M-n`); or a direct extraction over the raw source **persisted in `_capture/` under its own name** — the locator points at that file, never at the method, and what you did to the raw file that is not written there does not exist as evidence. Human confirmation counts only from the owner or an authority they named; anyone else is an attributed source. Uncertain → `Unknown`; inferred → `Assumed`, basis declared.
3. **Claim at the level of the evidence.** A formula supports "the artefact calculates"; a transcript supports "X said at [t]"; the owner supports a business fact within their authority. A business rule read out of a formula, a fact from a third party's statement, a technical fact about another team's system confirmed by business, a conclusion from a chain of rows, a policy generalized from two snapshots — is `Assumed` with the locators as basis. Cite what you opened — value, passage or locator, never a filename alone.
4. Append-only: never rewrite a row; a transition adds a row carrying `was <id>`.
5. Stamp and price: `Confirmed`/`Assumed` → `verificado_em` + `validade`; `Unknown` → `custo` + `swing`. In doubt `validade = organizacional`; never blank. Semantics: `library/kernel/states.md`.
6. An expired row reads as weak `Assumed` — never cite it as `Confirmed`.
7. **Admission** — the rule lives in `library/kernel/states.md` → *Admission of a question*; this is the checklist, not the rule. Before writing any `Unknown`:
   - its answer moves at least one of the five aspects — `solucao` · `funcional` · `aceitacao` · `operacao` · `viabilidade`;
   - fill `tipo`, `impacto` (`aspecto[, aspecto]: o que muda`), `âmbito`, `quem responde`, `fecho`, `bloqueio` and `referências`;
   - a missing fact is `fact_gap` and needs no invented second answer; a `design_choice` names its real alternatives in `swing`;
   - `âmbito` carries the origin marker where it matters — `observed_as_is` · `proposed_to_be` · `authorized_to_be` (`library/kernel/states.md` → *Admission of a question*). A marker is not a state: approving the TO-BE never turns an AS-IS premise into `Confirmed`;
   - no demonstrable impact → do not write it. `decisivo` also names the option or branch it eliminates, else `dimensionante`.

   Not every uncertainty is a question: changes only detail, configuration or a band → `Assumed` with basis and revision condition; settles only at implementation and cannot invalidate feasibility → no row.

   **Form of `quem responde`**: `role: <role>` or `fonte: <artefacto/sistema>`, one prefix per part, never a person and never a council persona. Neither known → leave the cell empty. Full rule: `library/kernel/states.md` → *The form of `quem responde`*.
8. **You write the technical fact; the organisation's ignorance is not pending work.** That nobody knows who does it, that there is no written policy, no inventory and no demonstrated maturity, describes the organisation — not the system to be built. Where the target must define what the organisation never defined, that is a **requirement** of the to-be, written `Assumed` with its basis, not a question waiting on somebody. Only a divergence that moves one of the five aspects becomes an `Unknown`.
9. **Cues, not coverage.** The cue lists below, and the pack's, point at what is often material. Follow what is material here; an uncovered cue is not a gap and never becomes an `Unknown`. Coverage is the central question answered with evidence, not the list ticked.

## Coverage evidence

What proves that a perspective was covered (plan 03 → *Matriz de cobertura das lentes*). The analyst records one entry per perspective in the `lens` coverage record (`library/kernel/coverage-contract.md` §4.8):

| Perspective | Central question | Evidence of coverage |
| --- | --- | --- |
| business | Which outcome, rule and exception define success? | Objectives, rules and acceptance linked to journeys |
| operations | Who runs it, supports it and recovers it when it fails? | Responsibilities, exceptions and recovery |
| user | Can the user finish the task under real conditions? | Actors, path, constraints and pertinent accessibility |
| data | Where is the truth, and how does it stay consistent? | Model, ownership, quality and interfaces |
| governance | Which authorisation, risk and control apply? | Enforcement, traceability and approvals |
| financial | What are the cost/benefit and the material uncertainty? | Economic drivers, effort and verifiable assumptions |

- `assessed` — the central question is answered. The references are SU rows that exist or locators of the threshold classes; a heading, a section title or a reference that does not resolve **does not count**.
- `gap` — the central question is not answered, and the gap is routed: a reference to an open question (`U-`/`X-`/`R-`) or to a proof obligation. A gap does not trigger another full round by itself.
- `not_applicable` — the perspective does not apply to this process, and the justification says why (e.g. no human user: a headless integration). Without a reason it is invalid.

An independent reviewer reads the record afterwards and gives a verdict per perspective (`treated` · `not_treated` · `not_applicable_ok`). A perspective listed but not treated is a visible gap, never a pass.

## Business

**Central question:** which outcome, rule and exception define success?

Sceptical of declared impact and declared urgency — both are usually the requester's, not the organisation's. Notices what the other perspectives take for granted: whether this is worth doing at all, for whom, and on whose authority.

1. **What is the real impact?** (declared vs evidenced)
2. **Who senses it?** (the requester is rarely the affected party)
3. **What is the real urgency?** (a date someone gave vs a consequence that lands)
4. **Who else has a stake?** (shadow stakeholders, gatekeepers, veto-holders)

**Privileges** what people said about consequence: what hurts, what it costs, who decided, by when.

**Cues:** `impact_declared_vs_evidenced`, `urgency_declared_vs_evidenced`, `who_feels_the_pain`, `shadow_stakeholders`, `decision_authority`, `business_KPIs_at_stake`, `requester_motivation`, `prior_attempts`.

**Apply.** Separate declared from evidenced impact and urgency; find who actually senses the pain and what it costs them; map decision authority and the veto-holders nobody invited; test the rationale — why this, why now, and what happened to prior attempts.

## Operations

**Central question:** who runs it, supports it and recovers it when it fails?

Distrusts the documented process and looks for what actually happens — the happy path in a diagram is the smallest part of the work.

1. **What is the work today, step by step?** (the real flow, not the diagram)
2. **Where is the friction?** (waiting, rework, handoffs, manual re-keying)
3. **What does the happy path hide?** (exceptions, discretionary decisions, escalations)
4. **What tribal knowledge keeps it running?** (the file only one person understands)

**Privileges** accounts of how the work really runs: exception passages, escalations, and the replay of what a working file actually does.

**Cues:** `as_is_steps`, `step_duration`, `handoffs`, `waiting_and_rework`, `exceptions_and_escalations`, `discretionary_decisions`, `tribal_knowledge`, `volume_and_peaks`, `cycle_time_current_vs_target`, `operational_ownership`.

`step_duration` (P-5): when the as-is has named steps, record the **time per step** — `Assumed` with its basis (a transcript locator, an observation, the owner's statement) or `Unknown` with `custo=email` to the person who runs the step. Never a guessed figure, never a total spread evenly across steps. These rows are the contracted source of the `tempo` column in `_synthesis/as-is.md` and, through the Implementation Specification, of the operating-path change the Estimate quantifies (P-10). Fields, types and schemas are **not** this perspective's job (P-5): the L1 inventory carries them into Architecture.

**Apply.** Reconstruct one real instance end to end — who touches it, in what order, with what waits. Then hunt what the diagram omits: exceptions and their frequency, rework, manual re-keying, discretionary calls, single-person dependencies, who owns the process operationally, and how volume behaves at peak versus steady state.

## User

**Central question:** can the user finish the task under real conditions?

Represents the people who will actually use whatever gets built — not the sponsor, not the maker. When the sponsor describes the users' pain, it is second-hand.

1. **Who are the distinct user groups?** (and how many in each)
2. **What is their context of use?** (desk, field, shop floor; device; connectivity; language)
3. **What hurts today?** (the concrete friction, in their words)
4. **What would make adoption fail?** (who loses, who is asked to work harder)

**Privileges** first-person accounts of use — where people work, on what, and what they said hurts.

**Cues:** `user_populations`, `context_of_use`, `devices_and_connectivity`, `top_friction`, `accessibility_needs`, `language_needs`, `adoption_risk`, `desired_experience`.

**Apply.** Separate the distinct user populations and their contexts of use; state friction in the users' words rather than the sponsor's; check accessibility and language needs explicitly; name who gains and who is asked to work harder, because that is where adoption fails. Offline and sensitivity tensions go to the conflict scan, not resolved here.

## Data

**Central question:** where is the truth, and how does it stay consistent?

Cares about who owns the information, where it lives, how good it actually is, and how sensitive it is. Trusts a column profile over a claim about data quality.

1. **What are the data entities, and who owns each?** (master data)
2. **Where does it live today, and what is its real quality?**
3. **How sensitive is it?** (personal, financial, confidential — and how it is classified)
4. **What must it obey?** (retention, residency, audit, systems of record)

**Privileges** the column profile in the extractions — sheets, columns, types, row counts, distributions, date ranges, anomalies.

**Cues:** `data_entities`, `data_shape`, `data_owners`, `data_quality`, `sensitivity_classification`, `retention_residency`, `systems_of_record`, `volumes_growth`, `duplication_lineage`, `data_dependencies`.

`data_shape` (P-5): the **grain** (what one row is), the **dimensions** (what a row is keyed by) and the **volume** per entity — never the attribute list. Fields, types and mandatoriness are not Discovery: they enter in Architecture from the L1 inventory (`fields_draft.py`, consumed by `/blueprint`) and are judged there. A question about a column's name or type is `cosmético` here unless it changes the shape or the volume of the data the to-be will carry.

**Apply.** Name the entities and their owners; read quality off the profile (nulls, duplicates, free text where a code belongs, stale dates) rather than off an assertion; classify sensitivity; trace lifecycle and lineage — where a record is born, copied and retained, which system is the source of record, and what depends on what. Record sensitivity explicitly so the conflict scan can adjudicate it.

## Governance

**Central question:** which authorisation, risk and control apply?

Protects the organisation from regulatory, security and audit exposure — and reads the other perspectives' stated needs against what policy actually permits.

1. **What rules apply?** (regulation, sector obligation, internal policy, contract)
2. **Which role may do what?** (access control by role, separation of duties as a permission split, least privilege) — never which person.
3. **What must be provable, and by which mechanism?** (audit trail independent of the write path, whether it carries a reason, when retention is stamped, what the export path is)
4. **What does data handling constrain?** (classification, residency, sharing and offline limits)

**Privileges** stated rules and authority — policy, contractual and audit statements, sign-off and access rules wherever they appear.

**Cues:** `regulations_applicable`, `access_control`, `separation_of_duties`, `permission_enforcement_plane`, `audit_trail_mechanism`, `audit_requirements`, `retention_legal`, `data_handling_policy`, `privacy_obligations`.

**Roles, never people** (P-21). No row and no question names a person as its answer. Authority is a **role**, the operation it may perform, and the plane that enforces it. A signature, an approval, an acceptance, or a document proving a third party's position is not a governance finding here — and separation of duties is recorded as a permission split, never as which person does which task.

**Conflict scan — after the other five.** Cross the needs the other perspectives stated against policy, authority and compliance constraints. A collision — e.g. an offline need over data flagged sensitive — becomes a **Conflicted** row with `partes` (`user∧governance`) and `criticidade`. **Never resolve a conflict silently**; it stands until the owner resolves it. The coverage record's `conflict_scan` cites the `X-` rows it produced, or says, in its note, that the scan found none.

**Apply.** The conflict scan first, then authority and provability: which **role** may do what, on which plane that access is enforced, where duties must be separated **as a permission split**, and what must be evidenced at audit and by which mechanism. Approvals, signatures, acceptances and named individuals are out of scope (`library/kernel/states.md` → *Question economics*, the role rule).

## Financial

**Central question:** what are the cost/benefit and the material uncertainty?

Puts a number on what the others describe qualitatively, and is explicit that the number is an estimate with a stated basis — never a borrowed certainty.

1. **What does the as-is process cost?** (time, errors, delay, rework — and what the business does alone today that would come to depend on a delivery queue)
2. **What does doing nothing cost?** (the baseline any option must beat)
3. **What can be spent, and how is it funded?** (envelope, CAPEX/OPEX, approval thresholds) — **only when `context.json.funding_gate` is `true`** (absent → `true`). When it is `false`, the decision to proceed does not depend on a budget approval and this question is not asked in this engagement.
4. **Which assumption moves the number most?** (where the estimate is fragile)

**Privileges** anything carrying a volume, a cycle time, a rate or a stated budget.

**Cues.** Always: `as_is_cost`, `do_nothing_cost`, `cost_of_delay`, `cost_sensitivity`. Gated by `context.json.funding_gate` (absent → `true`): `budget_envelope`, `capex_opex`, `funding_model`, `payback_roi`. With `funding_gate: false` these four are **inactive** — not cues, not gaps, never an `Unknown` in this engagement.

**Apply.** Read `context.json.funding_gate` first. Build the as-is cost envelope from volume × cycle time × loaded rate, with the arithmetic and each input visible, and write it as **Assumed** with the basis declared — the baseline is written, not asked (`library/kernel/states.md` → *Question economics*, *Cost questions*). Add the cost of doing nothing and the cost of delay as the baseline to beat, and name what the business does alone today (a parameter it edits, a product family it adds) that a system would turn into a dependency on a delivery queue — that is a cost too. With `funding_gate: true`, capture the budget envelope, funding model and approval thresholds where stated; with `false`, do not build an envelope and do not ask about funding, thresholds or CAPEX/OPEX. Name the input the estimate is most sensitive to — that is the one worth an `Unknown`, and only if its `swing` names what it changes: the branch its magnitude eliminates or keeps alive (`decisivo`), or the effort or data shape of the to-be (`dimensionante`); a cost figure that changes neither is `cosmético`, including when the decision to build is already taken.
