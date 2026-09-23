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
- New ids: functional contracts `FC-NNNN`, journeys `J-NNNN`, work packages `WP-NNNN`, tasks `TASK-NNN`, scopes `SCOPE-NNNN`. They are stamped by the coordinator when an artefact is published — never by the renderer — are stable in the engagement, and **are never reused** after withdrawal (`retired_ids`).
- Every new canonical artefact carries `schema_version` (`handoff-<name>/<N>`), `engagement_id`, `revision`, `based_on` (revisions or hashes of its inputs, not names) and `items`. Published content is immutable per revision; the current-revision pointer moves only through the coordinator. A schema migration never changes meaning silently, and a field a reader does not know is preserved, never dropped.
- Schemas: `library/kernel/schemas/` — `handoff-state`, `handoff-pack`, `handoff-response`, `handoff-work`, `handoff-functional`, `handoff-index`.

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

**Authorisation** (F4.2). The owner authorises through `AskUserQuestion`; the skill then writes one `D-NNN — Contratos funcionais autorizados (functional-contracts r<NNNN>)` block in `decisions.md` (plus its decision-record row in the SU), with `**Authorizes**: FC-0001 (sha256 <item>) · …`, `**Revision**`, `**Scope**`, `**Validated by**` and `**Timestamp**`. The block text comes from `functional.py authorization-block`, which computes each item's fingerprint (the item without `authorization_ref`, `authorization` and `publication_status`) and refuses an `FC` with gaps. An `FC` is authorised only while its current fingerprint equals the one the latest block that lists it records: a changed `FC` reads `stale` and the old approval does not cover the new revision; an unchanged one keeps its approval. `Validated by` must be `owner (<role>, … via AskUserQuestion)` — the executor, an agent, a council persona or a reviewer never authorises for the client (`AUTHORIZATION_REQUIRED`; a block written by hand with one reads `invalid`), and `[ÂMBITO AUTORIZADO]` does not apply to an `FC`. Authorising an `authorized_to_be` contract confirms no AS-IS premise: the `Assumed` rows it rests on stay `Assumed`, and `functional.py show` lists them.

**Coherence with the blueprint** (F4.3). For each `inputs[].field_ref`, `functional.py` compares what the blueprint field and the `FC` both declare — `required`, `values` (order ignored), `default`, `type`. A divergence is an `FC_BLUEPRINT_CONFLICT` with both sides and their locators; nothing picks a side. The affected `FC` is not authorisable until reconciled, and `functional.py conflicts --blueprint <version>` compares a blueprint version put to approval with the current `FC`s (exit 4 on conflict). A facet only one side declares is not a conflict; *computed* is left to the reviewer.

## Work packages and completeness

A `WP` is a unit of the implementation-spec — build, configuration, migration, proof or acceptance — that references the `FC`s and blueprint obligations it serves. Its effort lives in the estimate, per `WP`. Traceability is checked both ways: a requirement without work or test, and work without a design reason, are both findings.

**Complete for handoff** (plan 08): zero unhandled essential gaps in the delivered scope; no material contradiction between views; outputs intact and current; work, tests and estimate traceable; responsibilities and authorisations present. The receiver's acceptance is recorded separately. Delivery levels: `preliminary` · `ready_for_receiver_review` · `accepted_by_receiver` · `implemented_verified` — the last only after the corresponding tests ran and left evidence; no level follows automatically from the one before.

## Release index

`handoff-index/1`: engagement, scope and exclusions, code and pack versions, input revisions, files with hashes, authorisations, readiness, proofs performed and pending, and the receiver's acceptance. It points to revisions; it is not a seventh decision register, and it carries no secret and no unnecessary production data.

## Review policy

Material semantics is reviewed by someone other than its author. A reviewer reviews **a revision** — the candidate it read, by revision — and a review of an earlier candidate does not cover a later one. A reviewer's disagreement on a recommendation is a **finding** with a disposition: accepted or corrected; rejected with evidence; delegated with an envelope; escalated; deferred with its impact. Disagreement on a fact is `Conflicted` (`states.md`). How many reviewers agree never changes an epistemic state. The mechanics are implemented in F4.

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
