# Handoff contract — profile `handoff-v1`

Owner of what the `handoff-v1` profile adds and no other kernel contract owns: the functional contract, the work units, the release index, the work checkpoint, the review policy and the typed dependencies. What already has an owner stays there and is only pointed to:

- epistemic states and the admission of a question: [`states.md`](states.md);
- the four phases, Options by route and the readiness predicates inside Decision: [`phases.md`](phases.md);
- the dialectic limits and session continuity: [`orchestration.md`](orchestration.md);
- the blueprint: [`blueprint-contract.md`](blueprint-contract.md);
- coverage and freshness: [`coverage-contract.md`](coverage-contract.md);
- deliverables: [`render-contract.md`](render-contract.md).

The profile and route of an engagement live in `_state.json.workflow`, checked by `library/kernel/tools/workflow.py`; an engagement without that block belongs to the historical version and is read-only here. Plan of record: `docs/handoff-v1/plan/` (02, 04, 08).

## Authorities

| Content | Authority | Consumers |
|---|---|---|
| Original evidence | Preserved sources and the evidence index | SU, analysis, reviewers |
| Claim and epistemic state | SU, mirrored in the graph | Decision, design, readiness |
| Authorised choice, reason, alternatives, triggers | `decisions.md` | Blueprint, functional contract, revisit |
| Topology, responsibilities, boundaries, architectural obligations, logical definition of an entity or field | Approved blueprint | Functional contract, implementation-spec |
| Detailed TO-BE behaviour | `_design/functional-contracts.json` | Blueprint by reference, implementation-spec, tests |
| Build/config work, sequence, migration/cutover, acceptance | Implementation-spec | Backlog, estimate |
| Effort | Estimate (the only source of effort) | Planning, executive summary |
| The aisa's own work in flight | `_work/checkpoint.json` | Resume, dispatch, observability |
| Delivery index | Projection of one consistent revision | Receiver, release check |

The SU keeps claims, questions and links — not the whole functional specification. The blueprint references functional ids and never duplicates a rule. The implementation-spec turns authorised contracts into work and acceptance and never redefines behaviour. The backlog is a projection, never a second source of effort or design. Any other place that states an effort is a labelled preliminary band (mode B), never a competing estimate.

## Identifiers and revisions

- Existing ids are reused: sources, SU rows (`C-`, `A-`, `U-`, `X-`, `R-`), decisions (`D-`), tripwires (`TW-`), invariants (`M-`), capture (`PM-`), blueprint keys.
- New ids: functional contracts `FC-NNNN`, journeys `J-NNNN`, work packages `WP-NNNN`, tasks `TASK-NNN`, scopes `SCOPE-NNNN`. They are stamped by the coordinator when an artefact is published — never by the renderer — are stable in the engagement, and **are never reused** after withdrawal (`retired_ids`). A `SCOPE-NNNN` has no file of its own: it is defined by the `FC` that carry it as `scope_id` and by the authorisation blocks that name it, and a release index projects that definition (`scope_definition`), never adds to it.
- Every new canonical artefact carries `schema_version` (`handoff-<name>/<N>`), `engagement_id`, `revision`, `based_on` (revisions or hashes of its inputs, not names) and `items`. Published content is immutable per revision; the current-revision pointer moves only through the coordinator. A schema migration never changes meaning silently, and a field a reader does not know is preserved, never dropped.
- Schemas: `library/kernel/schemas/` — `handoff-state`, `handoff-pack`, `handoff-response`, `handoff-work`, `handoff-functional`, `handoff-index`; F5 adds `handoff-candidates` and `handoff-review`; F6 adds `handoff-scope` and `handoff-work-packages`.

## Functional contract (`FC`)

Each `FC` carries:

- identity, scope or journey, purpose, owner role and revision;
- references to requirements and SU rows, authorising decisions and blueprint elements;
- actors and rights, preconditions and trigger;
- inputs with domain, obligation, validation and authorised defaults;
- rule, algorithm or transition, postconditions and invariants;
- observable results, relevant messages and side effects;
- exceptions, duplication and repetition, cancellation, concurrency and recovery, where they apply;
- positive, negative and boundary acceptance examples, with units and rounding where there is a calculation;
- dependencies, delegated choices, open questions and required proofs.

A field that does not apply is listed in `not_applicable` **with its reason**; a reason left empty is invalid (the schema refuses it). No number is invented to fill a field. The logical definition of an entity or field stays with the blueprint's data owner: the `FC` references it and says how the behaviour uses it. A parameter still to be chosen needs an envelope, an owner and an acceptance test, or it stays a blocker. `semantic_origin` is `observed_as_is`, `proposed_to_be` or `authorized_to_be` — markers, not epistemic states.

The functional author proposes the `FC`; the architect checks that it can be realised and that it matches the blueprint; the business owner authorises material semantics. A later change reopens only the approvals and outputs that depend on it.

**How it is written** (F4, `docs/handoff-v1/F4/DESENHO.md`). Only `library/kernel/tools/functional.py` publishes `_design/functional-contracts.json`, through the coordinator — `_design/` is guarded and never drafted by `resolve.py`:

- `draft` opens a copy in `_drafts/FCDRAFT-…/` with the base and the inputs it reads (SU, `decisions.md`, the blueprint versions);
- `check` validates without writing;
- `publish` writes, in one operation, the new revision and its immutable copy in `_design/history/functional-contracts.r<NNNN>.json`;
- `show` gives the state per `FC`.

Integrity refuses the publication (`INTEGRITY_FAILURE`): the schema, ids never reused and never dropped outside `retired_ids`, the revision moving by one, and references that resolve (requirements to SU rows, authorisations to `D-` blocks, `architecture_refs` and `inputs[].field_ref` to the blueprint named in `based_on`). A changed base or input is `STALE_INPUT`. Completeness never refuses: an `FC` without `rule`, `acceptance_examples`, `actors`, `trigger`, `postconditions` or `exceptions` (and no reason in `not_applicable`), a calculation without units, rounding or positive/negative/boundary examples, an incomplete delegated choice, or an open `blocks_scope`/`blocks_all` question in `open_refs` is published with `BLOCKING_GAP` on its scope, and is not authorisable.

**Authorisation** (F4.2). The owner authorises through `AskUserQuestion`; the skill then writes one `D-NNN — Contratos funcionais autorizados (functional-contracts r<NNNN>)` block in `decisions.md` (plus its decision-record row in the SU), with `**Authorizes**: FC-0001 (sha256 <item>) · …`, `**Revision**`, `**Scope**`, `**Validated by**` and `**Timestamp**`. The block text comes from `functional.py authorization-block`, which computes each item's fingerprint (sha256 of the item's JSON without `authorization_ref`, `authorization` and `publication_status`, keys sorted, separators `,` and `:`, UTF-8) and refuses an `FC` with gaps, and a block dated before a decision already recorded in `decisions.md` (the block is appended; an earlier date would misstate the order — T43 S7). The published `FC` keeps `authorization_ref`/`publication_status` as authored: its authorisation is read from the blocks (`functional.py show`), and a package carries that reading (`functional-state.json`). An `FC` is authorised only while its current fingerprint equals the one the latest block that lists it records: a changed `FC` reads `stale` and the old approval does not cover the new revision; an unchanged one keeps its approval. `Validated by` must be `owner (<role>, … via AskUserQuestion)` — the executor, an agent, a council persona or a reviewer never authorises for the client (`AUTHORIZATION_REQUIRED`; a block written by hand with one reads `invalid`), and `[ÂMBITO AUTORIZADO]` does not apply to an `FC`. Authorising an `authorized_to_be` contract confirms no AS-IS premise: the `Assumed` rows it rests on stay `Assumed`, and `functional.py show` lists them.

**Coherence with the blueprint** (F4.3). For each `inputs[].field_ref`, `functional.py` compares what the blueprint field and the `FC` both declare — `required`, `values` (order ignored), `default`, `type`. A divergence is an `FC_BLUEPRINT_CONFLICT` with both sides and their locators; nothing picks a side. The affected `FC` is not authorisable until reconciled, and `functional.py conflicts --blueprint <version>` compares a blueprint version put to approval with the current `FC`s (exit 4 on conflict). A facet only one side declares is not a conflict; *computed* is left to the reviewer.

## Work packages and completeness

A `WP` is a unit of the implementation-spec — build, configuration, migration, proof or acceptance — that references the `FC`s and blueprint obligations it serves. Its effort lives in the estimate, per `WP`. Traceability is checked both ways: a requirement without work or test, and work without a design reason, are both findings.

**Scope and inventory as artefacts** (F6.1; DESENHO Q1/Q3). `_design/scope.json` (`handoff-scope/1`) defines each `SCOPE-NNNN`: `includes` (SU rows and `J-NNNN` of existing `FC`, each with its reason), `excludes` (each with its reason and an `authorization_ref` to an existing `D-NNN`) and `authorized_by`. `_design/work-packages.json` (`handoff-work-packages/1`) holds each `WP-NNNN`: `scope_id`, `purpose`, `realizes` (`FC-NNNN`, SU rows, decisions, or blueprint nodes as unit keys `<file>#<selector>` resolved by the coverage selector grammar to exactly one node), `proves` (proof obligations of the blueprint), `depends_on`, `acceptance` (conditions, with the `FC` whose examples they use), `skills`, `definition_of_done`, `not_applicable` with reasons. Only `library/kernel/tools/inventory.py` publishes them (`draft` · `check` · `publish` · `show`, `--kind scope|work-packages`), through the coordinator, each revision kept in `_design/history/`. Integrity refuses: the schema, ids never reused nor dropped outside `retired_ids`, the revision moving by one, references that resolve, a `depends_on` cycle, an exclusion without an authorisation, and any effort field (`effort`, `duration`, `days`, `hours`, `estimate`…) — effort belongs to the estimate alone. A `WP` without `realizes`, `acceptance` or `definition_of_done` (and no reason) and an unauthorised scope are published with visible gaps. The implementation-spec remains the owner of the inventory and renders it from this file.

**Traceability** (F6.2). `library/kernel/tools/trace.py show` (read-only) builds `scope → requirement/rule → FC → blueprint node → WP → acceptance/proof` from the published authorities and the approved blueprint (else the latest non-draft, said so), and reports both ways: `NO_CONTRACT` (an included item with no `FC` and no `WP` realising it directly), `NO_WORK`, `NO_TEST` (the work that realises it carries no acceptance), `NO_DESIGN_REASON` (a `WP` that realises nothing and says not why), `PROOF_WITHOUT_WORK` / `PROOF_WITHOUT_ACCEPTANCE` (every blueprint proof obligation is proved by a `WP` with an acceptance condition — T31), `VIABILITY_PROOF_OPEN` (an open `Unknown` of `tipo` `proof_obligation` can invalidate feasibility, `states.md`, so it blocks the commitment of its scope and is named, never left in an implementation checklist — T34) and `UI_IN_HEADLESS`; a headless design owes no screen (`applicability.ui: not_applicable (headless)` — T37). An authorised exclusion produces no finding. A finding is a structural fact; whether a requirement is material is the owner's judgement.

**Estimate, backlog and the scope gate** (F6.3). `trace.py estimate-check` / `backlog-check` read the deliverable's table rows that cite `WP-NNNN` and the inventory revision it cites (`inventário rNNNN`): a stale or missing revision, a `WP` cited that does not exist, a `WP` without a unit, and — in the estimate — a `WP` estimated twice (competing effort) are findings; with `--spec`, a duration in an inventory row of the implementation-spec is `EFFORT_IN_SPEC` (effort belongs to the estimate alone — T32). `trace.py scope-gate` returns `complete` · `partial` · `blocked`: any traceability finding, an included `FC` not authorisable or not currently authorised, an open `blocks_all` question, or an open `blocks_scope` question that no `FC` cites in `open_refs` and no authorised exclusion covers (`UNLINKED_BLOCKING_QUESTION`, T43 R3) blocks the delivery; a partial passes only with authorised exclusions and coherent dependencies — no `WP` working for an excluded item or depending on one, and no required blueprint field left without an included `FC` that produces it (T33, N4). `functional.py show` adds `warnings` (not gaps): a `<domain>.<field>` named in the rule text that the blueprint does not define, and an actor that is not a blueprint persona when the blueprint declares personas (N3; concepts in prose stay the `fc-reviewer`'s).

**Complete for handoff** (plan 08): zero unhandled essential gaps in the delivered scope; no material contradiction between views; outputs intact and current; work, tests and estimate traceable; responsibilities and authorisations present. The receiver's acceptance is recorded separately. Delivery levels: `preliminary` · `ready_for_receiver_review` · `accepted_by_receiver` · `implemented_verified` — the last only after the corresponding tests ran and left evidence; no level follows automatically from the one before.

## Release index

`handoff-index/1`: engagement, scope and exclusions, code and pack versions, input revisions, files with hashes, authorisations, readiness, proofs performed and pending, and the receiver's acceptance. It points to revisions; it is not a seventh decision register, and it carries no secret and no unnecessary production data.

The experimental package of F5.5 (`docs/handoff-v1/F5/pacote-fx-hv1-02/`, `delivery_level: preliminary`) adds, after the first receiver rehearsal (T43): `scope_definition` (projected, see *Identifiers*), `reviews_basis` (per review, the input versions its mandate pinned and whether each is still current), `locator_convention` and `verification` (pointers to the contracts), and it ships those contracts (`handoff-contract.md`, `states.md`, `specialists.md`, the schemas), the engine's reading of the contracts (`functional-state.json`) and every knowledge unit a mandate gave a reviewer. The formal release index is F6's.

**Release** (F6.5; DESENHO Q4–Q6). `library/kernel/tools/release.py build` writes `<engagement>/_release/r<NNNN>/` — never over an existing revision — with the authorities, `_design/`, the approved blueprint, the sources, the latest rendered implementation-spec and estimate, the contracts and schemas, every knowledge unit a mandate gave a reviewer, and the engines' readings (`functional-state.json`, `trace.json`, `scope-gate.json`), indexed by `handoff-index.json`. The `delivery_level` is computed, never declared: `preliminary` while a traceability finding, a scope blocker, a missing implementation-spec or estimate, a disagreement of either with the inventory, or a blueprint approval that is not `current` remains; `ready_for_receiver_review` when all pass; `accepted_by_receiver` only through a `D-NNN — Aceitação do destinatário (release rNNNN)` block (`release.py acceptance-block`: `**Release sha256**` of the index, `**Scope**`, `**Conditions**`, `**Simulated**`, a human `**Validated by**`) over a release that verifies; `implemented_verified` never comes from the build. The index's `authorization_refs` name every decision the package rests on — `FC` authorisations, the blueprint approval, the scope and each exclusion, the route authority and the decision that chose the candidate (T43 R1); `reviews_basis` gives, per review, the input versions its mandate pinned and whether each is still current (R2); and a decision dated after `built_at` is recorded in `limitations` (R4). `release.py verify` refuses a package whose files changed, went missing or were added after the release (T39). **Secrets**: `operation.run` refuses to publish content matching a closed set of secret patterns (`SECRET_IN_CONTENT` → `INTEGRITY_FAILURE`; private keys, known vendor tokens, a password assignment with a literal value, long `Bearer` tokens), and a secure reference (`<vault:…>`, `{{…}}`, `${…}`, `@Microsoft.KeyVault…`) passes; `release.py` refuses a build and fails a `verify` on the same patterns (T40). The refusal names the path and the pattern, never the value.

## Options candidates (F5)

`_design/candidates.json` (`handoff-candidates/1`) holds the Options candidates with a revision; only `library/kernel/tools/review.py` publishes it, through the coordinator, with each revision kept immutable in `_design/history/candidates.r<NNNN>.json` (`draft-candidates` · `check-candidates` · `publish-candidates` · `show-candidates`). `options.md` stays the readable projection. Integrity refuses: the schema, ids `O-NNN` never reused nor dropped outside `retired_ids`, the revision moving by one, the route equal to `_state.json.workflow.route`, premises that are SU rows, and the route rules — `platform-constrained`: every candidate on `imposed_platform`, with `imposition_ref` equal to the route's `authority_ref`, no minimum count (one viable candidate is admitted with its reason); `solution-choice`: fewer than three only with `reduction_reason`; `change-impact`: a `baseline_ref` and, per candidate, `delta` and `impact_refs`. A candidate without an order of magnitude and its source (or declared unavailable), architecture or reversibility is published with a visible gap. Candidates are published **before** any reviewer runs, so every review is pinned to the revision it read.

## Specialist routing and mandates (F5)

The specialist roles, their triggers and their output contract have one owner, `library/kernel/specialists.md`; one agent executes every role, and the mandate says which. `review.py route` evaluates **every** role on every call and is deterministic: a role is selected with the evidence that fired it (an SU row of its lens and terms — never a parked, retired or resolved row; a design flag `outside-platform` · `external-access` · `human-surface`; a candidate without an order of magnitude; a phase where it is always in), or listed as not called with what was checked; a headless design (`experience.mode: none`, no screens) makes `ux-process` not applicable. `review.py mandate` publishes `_design/reviews/REV-NNNN.mandate.json` through the coordinator **before** the reviewer runs, with `task_id`, `role`, `objective`, `scope_ids`, `questions`, `input_refs` (each with `sha256`, also the operation read-set), `candidate_revision`, `knowledge_refs` (pack units of the active pack: path, `sha256`, `pack_version`; files of the role's own memory `.claude/agent-memory/_universal/<role>/` with `sha256`), `output_contract`, `stop_conditions`, `budget` and `prohibited_actions`. It is refused with `BLOCKING_GAP` while no candidate revision is published or a candidates draft is open (a candidate under construction is never reviewed), and with `INTEGRITY_FAILURE` for a role outside `specialists.md`, a mandate without questions, or a knowledge unit outside the active pack and the role's memory, or missing. Mandate ids `REV-NNNN` are never reused.

## Specialist reviews, dispositions and the dialectic (F5)

`review.py receive` publishes the reviewer's return as `_design/reviews/REV-NNNN.json` (`handoff-review/1`) through the coordinator, once and immutable. It refuses (`INTEGRITY_FAILURE`) a return outside the output contract, an `input_revision` other than the mandate's `candidate_revision`, a mandate question neither covered nor declared unanswered with a reason, and any `sources_used` entry that is not one of the mandate's `input_refs`/`knowledge_refs` with the same `sha256`; a used source that changed after the mandate is `STALE_INPUT` (the review is redone, never published on another base). Findings carry target, severity (`blocking` · `material` · `minor`), kind (`fact` · `recommendation`), evidence, failure scenario and closing condition. A review whose candidate revision is no longer current is `stale`: it closes no finding of the current revision, a disposition on it is `STALE_INPUT`, and `show-reviews` marks for revalidation only the findings whose target candidate changed or left (or whose target names no candidate). Dispositions (`accepted` with `corrected_by` — the `FC-NNNN`, `D-NNN`, SU row or engagement file that already corrects it, verified by the engine; a correction still to come is `delegated` or `deferred` (T43 S3) · `rejected` with evidence · `delegated` with envelope and owner · `escalated` with to whom · `deferred` with impact) and divergences live in `_design/reviews/ledger.json`, append-only with immutable history; open findings are those of current reviews without a closing disposition (`accepted`, `rejected`, `delegated`). The dialectic keeps the kernel cap per candidate revision: three divergences, two calls each; the fourth is born `escalated`, two calls without an accepted synthesis escalate, and a `fact` divergence is synthesised only with a locator. Receiving or disposing a review never writes the SU.

## Review policy

Material semantics is reviewed by someone other than its author. A reviewer reviews **a revision** — the candidate it read, by revision — and a review of an earlier candidate does not cover a later one. A reviewer's disagreement on a recommendation is a **finding** with a disposition: accepted or corrected; rejected with evidence; delegated with an envelope; escalated; deferred with its impact. Disagreement on a fact is `Conflicted` (`states.md`). How many reviewers agree never changes an epistemic state. The mechanics are implemented in F4 (functional contracts) and F5 (Options reviews, below).

## Checkpoint

`_work/checkpoint.json` (`handoff-work/1`) holds references and work state, never copies of the SU, decisions or blueprint: the objective, scope and authorisation references; tasks (`planned`, `running`, `blocked`, `completed`, `cancelled`) with role, versioned inputs, dependencies, blockers and completion criteria; results (`draft`, `received`, `integrated`, `superseded`) with their freshness (`current`, `stale`, `unverified`) and why they are not yet integrated; the last integrated operation and the next actions. `completed` needs an integrated output or a justified closure. After a crash, `running` does not mean it is still running: it is reconciled before anything is relaunched. Implemented in F2: `library/kernel/tools/workflow.py task plan|start|receive|reconcile|show` publishes it through the coordinator; `resolve.py publish` of a draft that serves a task integrates result and task in the same operation as the authorities; `workflow.py resume` reads it for a cold resume, and writes nothing.

## Lens coverage

Coverage by dimension (the six Discovery lenses): `assessed`, `gap` or `not_applicable`, each with references and justification. `assessed` means examined — neither resolved nor approved. `not_applicable` without a reason is invalid and closes nothing. A text that mentions every heading does not prove coverage. Pack signals stay attention cues, not coverage (`orchestration.md`). Recorded as a coverage stage (F3).

## Dependencies

The graph (schema 2) carries typed dependencies between the new artefacts and the rows they rest on: `supports`, `constrains`, `implements`, `verifies`, `estimates`, `derived_from`. The existing relations (`was`, `depends_on`) keep their meaning and are never merged into the new types silently. A change in a premise marks dependent claims, decisions, `FC`s, work, tests and outputs for revalidation; a reviewer may record *no semantic impact* against the change. Used from F5.

## What F1 froze and what comes later

| Frozen in F1 | Implemented in |
|---|---|
| Profile, route, pack capabilities, structured responses (`workflow.py`, schemas) | F1 |
| Admission of a question, evidence rule | F1 |
| Checkpoint schema and states | F2 (publication through the coordinator) |
| Lens coverage vocabulary | F3 |
| Review policy, Options by route, `FC` and its completeness (plan 05: F4) | F4 |
| `WP`, typed dependencies | F5 |
| Readiness predicates, release index | F6 |
