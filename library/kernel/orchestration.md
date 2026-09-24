# Orchestration — Kernel v0.2.0

## Mode declaration

Each phase declares its mode in [`phases.md`](phases.md):

- **`inline`**: one integrated analysis in the current thread applies the six perspectives of `lens-checklists.md`, with the whole accumulated context. Used in Discovery (`/round`); an independent reviewer reads the coverage record when the round closes (*Inline mode* below).
- **`analyst + reviewer`** (handoff-v1 F3): the integrated analyst proposes inline; one independent reviewer, a subagent with fresh context, contests; the chairman's evidence rules settle the synthesis. Used in Framing (*Framing mode* below).
- **`author + specialist reviewers`** (handoff-v1 F5): the technical author writes the candidates inline and publishes them; an explainable router selects the specialists the risk calls for; each reviews the published revision as a subagent, on its published mandate; the chairman disposes the findings. Used in Options (*Options mode* below). Decision is interactive (user-driven). The persona council is retired (F5.4).

**When a subagent is justified** (handoff-v1; README → *Regras de execução*). A subagent is defined only when both hold: the task does **not** need the context of whoever launches it, and its detail does **not** have to come back — only its verdict. Independence between an author and a reviewer is the typical case, and the subagent is the only way to get it. Everything else runs inline; in doubt, inline. Parallelism is a further choice, taken only when the subagents are independent of each other and the gain is real; a reviewer runs after what it reviews, never beside it.

## Evidence contract — parse once, reason many

*This section was previously titled "Reading input documents". Existing pointers to that name — lens skills, persona agents, `aisa-capture`/`aisa-frame`/`aisa-options`, `docs/PROCESS_CAPTURE_SPEC.md` — resolve here; they are updated in Phases C–E, no migration required.*

```text
raw inputs
    ↓
ingest/extract once
    ↓
shared usable evidence
    ↓
multiple lenses reason
    ↓
raw source inspected selectively when needed
```

**Parse once. Reason many.** The capture pass — not the lens — is what must open and PARSE every file under `<engagement>/inputs/`. It runs once per engagement (and again only on a stale hash, see `aisa-capture`), and its normalized output is the evidence surface every lens and council persona reads. No lens is required to enumerate or re-parse `inputs/`.

**Shared evidence surface.** Normalized evidence lives in `<engagement>/_capture/`; its entry point is `_capture/evidence-index.md` — one table for the engagement: source · format · normalized file · status · provenance unit. The orchestrator carries that index into every lens and persona invocation. When an engagement has no `_capture/` yet, the invocation says so and raw `inputs/` is the surface.

**Capture tiers.**

| Source | Tier | What the lens gets |
|---|---|---|
| `.xlsx`, `.xlsm` | specialized deterministic capture (L1 extraction + L3 replay + L2 process model — `docs/PROCESS_CAPTURE_SPEC.md`) | `process-model.md` (`PM-NNN` business rules with cell citations) + `*.replay.md` |
| `.docx`, `.pdf`, `.vtt`, `.srt`, `.txt`, `.md`, `.csv` | **capture-lite** (`library/kernel/tools/text_extract.py`, deterministic) | `_capture/<file>.text.md` — loss-minimizing text extraction with provenance markers (`§<heading> ¶NN`, `p.N`, `[HH:MM:SS] <speaker>`, `¶NN`, `linha N`); where the source carries process semantics, the L2 pass folds them into the cross-source synopsis (`process-model.md` §4) with those locators |
| anything else | not captured (not a failure) | raw inspection per the format table below |

Capture-lite is **loss-minimizing extraction with provenance, never semantic summarization**: everything the source said, plus where it said it. No LLM in the text path. The **L2 process model** (LLM, `aisa-capture` step 5) is the one comprehension pass and reads **all** normalized evidence — extraction JSON, replay reports and `*.text.md` — selected through `evidence-index.md`: **source-complete in coverage, never source-total in simultaneous context**. Every process-bearing source receives a disposition (`USED` / `CHECKED` / `TARGETED`) in `_capture-log.md`; there is no source count, size or length threshold — the contract is *enough evidence inspected to reconstruct the material process*. Its §4 is the engagement's durable process synopsis: normalized evidence, richer than the Shared Understanding, never authoritative over it. A source whose extraction is `failed`, `skipped` or `empty` — the index says which, and why — is read raw with the table below; so is any format outside the tiers.

**Raw inspection.** `inputs/` is read-only primary evidence and is always openable — no gate, no manifest, no permission step. Pick the tool by format:

| Format | How to read |
|---|---|
| `.json` | read directly |
| `.xlsx`, `.xlsm` | the `xlsx` skill, or `openpyxl` with `data_only=False` **and** `data_only=True` (two passes: formulas, then cached values). Data profile: sheets, columns, row counts, value distributions, date ranges. **Logic profile** (obrigatório quando a folha tem colunas derivadas): grafo de dependências entre folhas, histograma de funções, intervalos nomeados agrupados por prefixo, células com `#REF!`, fórmulas que quebram o padrão da coluna |
| `.pdf` | the `pdf` skill |
| `.docx` | the `docx` skill |
| `.pptx` | the `pptx` skill |
| images | read directly (vision) |

**Raw verification is materiality-based.** Shared extraction is the normal evidence surface. Inspect the raw source when it is **material to confidence**: extraction may have lost relevant detail; a material claim depends on interpretation; evidence conflicts; provenance is insufficient; or the lens needs context the extraction did not preserve. **Verify raw evidence when material to confidence, not to satisfy a quota.** There is no per-round spot-check quota, for any lens or persona. Isto limita o **spot-check**, não a compreensão: onde a captura declarou `TO-READ` (`aisa-capture` princípio 1) ou o process-model não tem §4bis para uma fonte estruturada, abrir a fonte **é** a acção material — não é quota, é a leitura em falta.

**Evidence integrity** (invariant — the one evidence rule that stays visible in every lens file):

- Never record a `Confirmed` or `Assumed` row citing evidence you have not opened. Cite the specific value, column or passage — never a filename alone. Citing `PM-NNN` counts as opened (PM rows carry cell citations; SU evidence format `PM-NNN → Sheet1!D2:D400`). A text locator is a plain string in the `evidência` column (`<file> · §<heading> ¶12`, `<file> · p.7`, `<file> · [00:12:34] <speaker>`) — no new id namespace.
- **A lens must not claim stronger evidential support than the evidence it actually inspected supports.** Weaker support → `Assumed` with the basis declared, or `Unknown`. What `Confirmed` requires — locator class, claim level, who may confirm — is owned by `states.md` → *Confirmed threshold*.
- Raw sources are **authoritative on conflict**: a mismatch between the extraction and the raw source becomes a `Conflicted` row citing both, and flags a capture re-run in `_capture-log.md`.
- Anonymized or obfuscated input is still evidence: structure (columns, counts, dates, distributions) is valid.

Epistemic semantics of what gets written (`verificado_em`, `validade`, `custo`, `swing`, transitions, expiry) are owned by [`states.md`](states.md) and are not restated here or in lens files.

## Comprehension survival — what must not be silently lost

```text
reason deeply → persist selectively → claim conservatively → rehydrate selectively → revalidate when premises change
```

aisa does not replace natural reasoning with deterministic cognition. Determinism governs **what must survive**, **what authority owns it**, **what may not be silently promoted or dropped**, **what must be revalidated** and **what a fresh session must reload** — never the order of hypotheses, the number of passes, or how a lens reads a transcript. **Constrain semantic survival, not internal cognition.**

**Compression is allowed.** Every boundary (capture → SU → Framing → Options → Decision → Architecture → deliverables) compresses. The boundary question is: *what material meaning could be lost if this representation replaces the richer one for downstream reasoning?* A downstream artefact may omit detail, never the obligation. Semantic classes that may not be lost **silently**:

| Class | Owner | Durable carrier | Projections |
|---|---|---|---|
| business invariant — a behaviour that must remain valid regardless of the chosen solution | SU row (`Confirmed`/`Assumed`, phrased as behaviour) | `process-model.md` §4 | `frame.md` survival block → Options personas → blueprint |
| structural constraint — a confirmed or unresolved condition whose truth could materially eliminate, reshape or gate whole solution classes | SU row (`Confirmed`, or `Unknown` with `swing: decisivo`) | SU | `frame.md` survival block → Options blocking set → architecture |
| decision-changing Unknown | SU `Unknown`, `swing: decisivo` | SU | `frame.md` survival block, `/status` agenda, `/simulate` |
| material scope / output family · material user task · material transformation obligation · material exception | SU row, projected from the synopsis by disposition | `process-model.md` §4 | frame → options → blueprint → spec |
| material control obligation | SU row / Options concern / decision condition | `decisions.md` | blueprint (structural choice when the store moves) |

No new state, no new field, no register, no matrix: these are existing SU semantics plus one projection slot in `frame.md`. Placement of a structural constraint: Discovery/Framing identify it generically → Options evaluates candidate-specific consequence → Architecture implements the response. Technology neutrality stays binding: user population and identity class, the existing entitlement boundary and the willingness to acquire incremental entitlement are pre-Options facts; candidate-specific entitlement is Options; exact licensing composition is Architecture. No product-licensing question is asked pre-Options because a pack is active.

**Material semantic disposition (Discovery projection boundary).** Every material synopsis line (output family, transformation obligation, invariant, user task, exception, structural constraint) and every `PM-U` row receives exactly one disposition, written in the lens's `Open evidence` block: `MAP <SU id>` — already represented · `ADOPT → <new id>` — row created · `DISMISS — <reason>` — explicitly non-material for downstream decision reasoning. No silent fourth outcome. A **Critical** `PM-U` may remain `Unknown` after adoption; it may never disappear. Visibility is mandatory, closure is not. The synopsis markers project as: `OBSERVED` → `Confirmed` when the evidence supports it — with a locator of the five classes and a claim at the level of that evidence (`states.md` → *Confirmed threshold*) · `INFERRED` → `Assumed` with basis · `HYPOTHESIS` → stays in the synopsis or projects as the `Unknown` that would settle it · `UNKNOWN` → `Unknown`. Rich reconstruction → selective material projection → compact SU: the SU grows by what changes an option's viability, scope or shape, never by the synopsis's size.

**`PM-U` about the artefact's mechanics — a content test, not a signal test.** A `PM-U` about how the old artefact is built (protection, hidden sheets, formats, range names, column or row counts, recalculation order) receives `ADOPT` only when the lens declares which **form, volume or rule of the to-be's data** changes with the answer. If the answer only changes the control or the look of the old artefact, the disposition is `DISMISS — mecânica do as-is`, with that reason written. Two sheets of the same shape are mechanics; four hidden sheets that decide whether the to-be carries 212 or 465 derived columns are data (`PM-U-003` in pilot-3) and keep rising. The L1 inventory remains the authorized draft source of fields in Architecture (P-6): dismissing a mechanics `PM-U` in Discovery loses nothing that Architecture will need, because the inventory, not the `PM-U`, carries it. A Critical `PM-U` dismissed on this ground is still a disposition — it never disappears silently.

**The coverage record is where the disposition stops being a promise.** Every class above already owes a disposition — `MAP` / `ADOPT` / `DISMISS`, the projection slot in `frame.md`, the structural choice, the proof obligation. What the coverage review adds is not a new state, a new owner or a new taxonomy: it is the **verifiable form** of the same obligation, at the two boundaries where compression has historically lost it — sources → record (`reconciliation`) and record → design (`blueprint`). The denominator is built from the sources by the motor, so omitting an obligation and its review line together no longer produces a green; `covered` needs a target that resolves; retiring a material obligation needs an authority that allows it. Definitions stay where they are (`states.md` owns the five states, this file owns the semantic classes, `coverage-contract.md` owns the record); the review cites them and redefines none. And it proves nothing about meaning: the motor verifies the **form** of the declaration, the reviewer signs the judgement, and *reviewed* is never *approved* and never *works end to end*.

**Fact ≠ fit.** A technical or configuration fact (a connection exists, a gateway is configured, a capability is documented) is never, by itself, an architecture-fit conclusion. Where a proposition is architecture-significant **and** is used to settle or materially support a structural architecture conclusion, it closes only on one sufficient basis — authoritative RESEARCH / Domain Knowledge read against the material requirements (exclusions included), engagement-verifiable technical evidence from an accountable source, or a proof / measurement / spike — otherwise the engagement fact is recorded and the structural choice stays open (`aisa-answer`, `aisa-blueprint`). Capability confirmed ≠ fit confirmed.

**Targeted revalidation.** When a new or changed material fact contradicts or materially changes a premise that downstream reasoning used, the conclusions materially based on it are named and marked for revalidation — through the references that already exist (`su_refs`, anchors, `forced_by`, conditions, proof obligations, open architecture choices, tripwires, the blueprint log), and, in a `handoff-v1` engagement, also through the typed dependencies of `handoff-contract.md` → *Dependencies*. No automatic reversal; no rerun of all phases: the motor marks what needs revalidation and never decides that new evidence confirms or refutes. Where the Decision basis may have moved: tripwire check → `/revisit`. Architecture never rewrites the Decision.

**Phase ≠ session.** A phase may span many sessions; several phases may run in one. Session context is a **disposable cache**; repository engagement state is the **durable memory**. A fresh session must not depend on the previous transcript and reloads **selectively**: phase authority + SU material state + the process synopsis where relevant + the current phase artefact + targeted evidence / Domain Knowledge pulls — never all raw evidence, all transcripts, all lens outputs or all Domain Knowledge (`aisa-status` → *Read to resume*). No handoff-summary artefact: the canonical artefacts are the memory. The one work file a `handoff-v1` engagement keeps is `_work/checkpoint.json` (`handoff-contract.md` → *Checkpoint*): references to tasks, results and authorities by id and revision — never a copy of their content, never a summary of what is known.

## Orchestrator boundaries

`aisa-round`, `aisa-frame`, `aisa-options`, `aisa-capture`, `aisa-status` and `aisa-start` are execution machinery. **Orchestrator = context provisioning + execution coordination, not domain reasoning.**

An orchestrator **may**:

- provision shared evidence (the `_capture/` index above) and the engagement files a lens would otherwise enumerate;
- resolve the active pack (`_state.json.pack` → `library/packs/<pack>/pack.yaml`);
- inject that pack's relevant `lenses_config.<lens>.extra_signals` as attention cues;
- make `question-bank.md` available at the one step that formulates questions;
- carry round bookkeeping (current round id, next free SU id per section);
- provide the return schema (owned by `chairman-synthesis`) and, in Options, the published mandate a reviewer runs on.

An orchestrator **must not**:

- decide what evidence means, or which evidence is relevant;
- classify findings on behalf of a lens (no state assignment, no claim phrasing);
- select architecture, or perform any domain reasoning;
- convert signals into mandatory checklist coverage;
- become a routing or rules engine.

**Dispatch is not routing** (`handoff-v1`). Choosing which step or role runs next from the profile and route the engagement declares (`_state.json.workflow`, checked by `library/kernel/tools/workflow.py` against the pack's `supported_workflow_profiles` and `supported_routes`) is allowed. Choosing by content — which evidence matters, which architecture, which template for which outcome — stays on the list above.

If a revision has the orchestrator scoring evidence relevance, ranking signals, or selecting questions, that is the line being crossed.

## Writing an authority (`handoff-v1`)

The six authorities — `_state.json`, `shared-understanding.md`, `answers.md`, `decisions.md`, `context.json`, `enquadramento.md` — are written **through the coordinator**, never in place (`docs/handoff-v1/F2/DESENHO.md` §3). One protocol, every skill:

1. **Open a draft** for everything the step writes, authorities and their companions together (`lens-outputs/<lens>.md`, `council-log.md`, `story.md`), declaring what the step read to decide: `python library/kernel/tools/resolve.py draft --engagement <slug> --files <rel>... --reads <rel|glob>... --json`. The draft copies the files to `_drafts/<id>/` and records their base.
2. **Edit the copies** under the returned `path` — Edit/Write on `_drafts/<id>/<rel>`, never on the engagement file. A draft is nobody's truth: no reader, gate or render consumes it.
3. **Publish**: `python library/kernel/tools/resolve.py publish --engagement <slug> --draft <id>`. One operation writes the changed files and, when the SU changed, its graph mirror, with one receipt. Publishing the same draft again returns the same receipt.

A refusal leaves the draft as it was and prints a structured reason:

| Code | Meaning | What the step does |
|---|---|---|
| `STALE_INPUT` | a file the draft started from, or declared as read, changed since | re-read, open a new draft on the current base, redo the edit — never force the old one |
| `INTEGRITY_FAILURE` | the new content breaks an authority rule (a SU row removed, a `Confirmed` without a resolvable locator, a `_state.json` key dropped, the `workflow` block changed) | fix the copy and publish again |
| `NOT_READY` / `RECOVERY_REQUIRED` | the engagement is not reconstructed (pending operation, divergent mirror) | follow the recovery the reason names; never write around it |
| `CONCURRENT_WRITE` | another writer holds the engagement | publish again when it finishes |

Never `mv` a `.tmp` over `_state.json`, never edit an authority with Bash, never Edit the SU in place. A direct edit that happened anyway is **preserved**: `on-su-mirror.py` reports it, the engagement stops being ready, and `python library/kernel/tools/resolve.py reconcile --engagement <slug>` shows the reconciliation (`--apply` publishes it). The `/answer` state transitions keep their own engine (`resolve.py --row …`), which publishes through the same coordinator. Phase artefacts (`frame.md`, `options.md`, `_blueprint/`, `_synthesis/`, `_render/`) stay tool-written until their phases (F4–F6).

## Pack context — Discovery vs Options

**The six Discovery lenses** (`business`, `operations`, `user`, `data`, `governance`, `financial`):

- are pack-agnostic — they never read `pack.yaml` and never resolve the active pack;
- receive a small list of pack-specific attention cues injected by the orchestrator: *"Pack attention cues (`<pack>`): a, b, c — cues, not a checklist; uncovered cues are not gaps."* Empty or absent key → nothing injected;
- stay vendor- and solution-neutral (`.claude/rules/no-tech-mention-before-options.md`).

**Signals are attention cues, not checklist items.** Universal signals belong to the lens itself; pack signals arrive by injection. Neither creates coverage obligations: no rule requires that every signal be covered, and an uncovered signal is not a gap and does not become an `Unknown`.

**`lens-technology`** is the documented exception:

- Options-only (never Discovery, never Framing);
- pack-aware — it may resolve the pack and selectively consult `decision-tree.md`, the relevant `domain-knowledge/*.md`, and `lenses_config.technology.constraints_to_check`;
- it does **not** load the complete domain-knowledge base by default. **Domain knowledge is pull-based, not push-based.**

The exception does not travel: a Discovery lens reading `pack.yaml` is a contract violation, not a precedent.

## Question bank — runtime role

`pack.yaml → question_bank` (e.g. `library/packs/pp/question-bank.md`) is a **question-generation resource**. It is **not permanent context for every Discovery lens**, and no lens or council persona loads it.

It is consulted selectively, at question-generation time, to phrase askable questions around material `Unknown` / `Conflicted` / `Risky` rows and evidence gaps. Intended single consumer: the existing question-generation step in `aisa-status` (which builds the meeting agenda from open Unknowns) — one consumer by design, since two would drift. *(Consumer not yet wired; the contract is stated here first.)*

## Inline mode

- One integrated analysis applies the six perspectives of `lens-checklists.md` (the single owner of their questions and of the evidence of their coverage); the governance conflict scan runs last inside it. No order is policed — there is one analysis, not six.
- It reads: `context.json`, `shared-understanding.md`, `enquadramento.md`, `lens-outputs/` (earlier rounds), and the shared evidence the orchestrator carries in (`_capture/evidence-index.md`).
- It writes, through one draft: rows to the Shared Understanding + a block per perspective in `lens-outputs/<perspective>.md`. Then the `lens` coverage record (`coverage-contract.md` §4.8), which is what closes the round.
- One reviewer subagent (`lens-coverage-reviewer`) reads the record once, when the round closes, and returns a verdict per perspective (T19).
- The orchestrator skill (`aisa-round`) drives the sequence.

## Framing mode (handoff-v1 F3)

- The integrated analyst, in framing mode, proposes inline: the single sentence, its anchors, the confirmation or correction of each `M-n`, the survival candidates — in the return schema `chairman-synthesis` owns.
- One reviewer subagent (`frame-reviewer`, `tools: [Read, Grep, Glob]`, fresh context, paths only) contests it with findings: target, severity, kind (`fact` | `recommendation`), premise/evidence, failure scenario, closing condition.
- `chairman-synthesis` applies the evidence rules: agreement is not evidence; a `fact` finding with a locator corrects by evidence; without one it is `Conflicted`; a `recommendation` divergence goes to the owner through `AskUserQuestion`. There is no antithesis round.
- No persona council runs (retired in handoff-v1 F5.4).

## Declared technical premises (P-25)

A technical premise the owner states in conversation — a store, a surface, an access mechanism, a
bridge between layers, a delivery convention, a reference implementation — is **recorded in the same
turn**, as a row in the Shared Understanding (`Confirmed` when it is a declaration within the owner's
authority, `Assumed` with the basis otherwise) and, in Options, as an architecture axis of the
candidates it touches. Two answers are not available: *absorbed for later* and *it enters when the
next command runs*. A premise held only in the conversation is lost at the end of it, and the command
that was supposed to absorb it has no way to know it existed — which is exactly how a declared
decision axis ends up missing from the artefact that compares the candidates. The user may decline to
record; the offer is never *we will use it without recording it*.

## Options mode (handoff-v1 F5)

- **Author, inline.** The technical author (`.claude/agents/solution-architect.md`, run by the session — it needs the whole engagement and the candidates are the product) writes the candidates and publishes them through `review.py` (`library/kernel/handoff-contract.md` → *Options candidates*). No reviewer runs on a candidate still under construction.
- **Router, explainable.** `review.py route` evaluates every role of `library/kernel/specialists.md` — selected with the evidence that fired it, or not called with what was checked.
- **Mandate before reviewer.** `review.py mandate` publishes, per selected role, the questions, the inputs and the pack units (and, when listed, the role's own memory) with their `sha256`.
- **Reviewers, subagents.** One `specialist-reviewer` per mandate (`tools: [Read, Grep, Glob]`, fresh context, the mandate path only), in parallel with each other; none sees the author's reasoning or another review. `review.py receive` publishes each return, pinned to the revision it read.
- **Chairman, inline.** `chairman-synthesis` reads the published reviews, never votes, and disposes every finding (`review.py dispose`, append-only; a minority opinion is never deleted).

**Agent = independent perspective + mandate.** An agent file carries identity, perspective, what it challenges and its output; it does **not** duplicate kernel state semantics (`states.md`), orchestration, common schemas or domain knowledge. The role's content lives in one kernel file (`specialists.md`), the task in the published mandate: one channel each, because two would drift. Only the technical author pulls pack domain knowledge on its own, Options-only (see *Pack context* above); a reviewer reads only what its mandate lists.

## Dialectic round

Options only — retired in Framing by handoff-v1 F3 (Q5), where a factual divergence without a locator becomes `Conflicted` and a recommendation divergence goes to the owner. Full peer review was rejected for cost. Its surgical replacement: when the chairman detects **material divergences** between reviews, or between a review and the author's candidate (claim vs counter-claim that would change the phase artefact), the orchestrator runs an antithesis round for those points ONLY — each side attacks the other's strongest thesis and returns `Concedo / Contesto / Síntese proposta`. Cap: **3 divergences × 2 calls = ≤6 extra passes** per candidate revision, kept by the engine (`review.py diverge` / `dialectic-call`). Divergences that survive the antithesis become Conflicted rows; the chairman never silently picks a winner. Thesis → antithesis → synthesis, only where there is real disagreement.

**What a synthesis may settle** (handoff-v1). An accepted synthesis settles a recommendation, a ranking or a disposition — never a fact. A factual divergence becomes a `Confirmed` row only when the antithesis produced a locator of the *Confirmed threshold* classes (`states.md`); otherwise it is `Conflicted`. How many reviewers agree never changes an epistemic state. The cap is a ceiling, not a verdict: divergences still open when it is reached are **escalated** — to the owner through `AskUserQuestion`, or recorded as a finding with its disposition — and never accepted by exhaustion.

## Why parallel among the Options reviewers (not sequential isolated)

The reviewers of one published revision read the same inputs and do not depend on each other: concurrent Task subagents complete the review in ~1 LLM-pass-time, versus one per reviewer in sequence; they share no writable state. The author publishes before any of them runs. Parallelism is not a phase rule: it is justified only when the subagents themselves are (*When a subagent is justified*, above). Discovery and Framing run no parallel subagents.

## Peer review (omitted in MVP)

Karpathy's full pattern includes peer review (each agent comments on the neighbor's output). aisa omits the full version by cost; the **dialectic round** above is its surgical replacement — antithesis only where reviewers materially disagree.

## Cost envelope per engagement

- Discovery: 1 integrated analysis + 1 coverage review per round × ~2-3 rounds = 4-6 passes (inline).
- Framing: 1 analysis + 1 reviewer + 1 synthesis = 3 passes (no dialectic).
- Options: 1 author (inline, technology enters) + 1 review per selected specialist (1-5, by the router) + 1 chairman = 3-7 passes + 0-6 dialectic passes.
- Decision: interactive (user-driven) + optional 1 solution-architect review (`/decide --consult`) + auto synthesize (5 topic packs) = 5-7 passes.
- Render: 6 deliverables × 1 composition pass = 6 passes.

**Total per engagement**: ~25-35 LLM passes (handoff-v1 F3/F5: no persona council in any phase).
