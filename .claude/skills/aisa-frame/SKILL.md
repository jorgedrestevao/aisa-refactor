---
name: aisa-frame
description: Transition Discovery → Framing. Checks Discovery's soft exit gate, flips _state.json to phase=framing/round=F-01, has the integrated analyst propose the frame inline, one independent reviewer (subagent) contest it, and the chairman-synthesis skill write frame.md and the synthesised Shared Understanding rows. On user validation, registers the frame approval (next free D-NNN, with the sentence's fingerprint) in decisions.md.
---

# aisa-frame

## Usage

`/frame [--override "<reason>"]`

- No argument: runs the soft gate check; if any criterion is red and no override is provided, stop with a clear summary and ask the user before proceeding.
- `--override "<reason>"`: bypass the soft gate. The reason is logged in `decisions.md`.

## Phase model

- **From**: `phase: discovery`.
- **To**: `phase: framing`, `round: F-01` (subsequent framing rounds become `F-02`, `F-03`, …, by re-running `/frame`).
- **Mode**: integrated analyst + one independent reviewer (`library/kernel/orchestration.md` → *Framing mode*). Nothing else runs in Framing: no other role, no antithesis round.

The analyst proposes inline — it needs the whole engagement, and its detail is the product. The reviewer is the one subagent: it must not have the analyst's context, and only its findings come back. The synthesis applies the chairman's evidence rules to both (`CLAUDE.md` → *Delegação a subagentes*; `docs/handoff-v1/F3/DESENHO.md` §0).

## Inputs (read)

- `<engagement>/_state.json`, `<engagement>/context.json`, `<engagement>/shared-understanding.md`, `<engagement>/decisions.md`, `<engagement>/council-log.md`.
- `<engagement>/lens-outputs/*.md` (the perspectives' interpretation of earlier passagens).
- `library/kernel/phases.md` (Framing entry criteria).
- `<engagement>/_capture/evidence-index.md` (the shared evidence surface for the analyst and the reviewer).
- `<engagement>/_capture/process-model.md` §4 (the process synopsis) and §6 (PM-U) — for the comprehension-survival soft gate (step 2) and the chairman's survival block; when absent, the gate runs on the SU alone and says so.
- The process map, **global view** (process-map M4): `python library/kernel/tools/process_map.py summary --engagement <slug> --task framing --json` — objective, actors, steps, outputs and who receives them, and the scope gaps still open. The problem sentence must hold against it: an output or consumer of the map that the frame leaves out is named, not dropped. Absent map → the frame runs as before and says so.
- `<engagement>/lens-outputs/*.md` `Open evidence` blocks — where the dispositions (`MAP` / `ADOPT` / `DISMISS`) live.
- `library/packs/<pack>/pack.yaml` — `lenses_config.<lens>.extra_signals` only, as attention cues.
- `library/kernel/lens-checklists.md` — the six perspectives the analyst frames across.

`<engagement>` resolves to `$AISA_ENGAGEMENTS_ROOT/<slug>` if set, otherwise `projects/<slug>`. `<pack>` is read from `_state.json.pack`.

## Outputs (written, via chairman-synthesis except where noted)

- `<engagement>/_state.json` (through the coordinator — this skill; `library/kernel/orchestration.md` → *Writing an authority*).
- `<engagement>/frame.md` (chairman-synthesis).
- New rows in `<engagement>/shared-understanding.md` (chairman-synthesis).
- `<engagement>/lens-outputs/chairman-synthesis-F-<NN>.md` (chairman-synthesis).
- `<engagement>/lens-outputs/_council-prep/F-<NN>-analyst.md` (the analyst's proposal, this skill) and `F-<NN>-reviewer.md` (the reviewer's findings, verbatim) — the audit trail of what the synthesis read.
- A `D-NNN — Frame agreed (F-NN)` record in `<engagement>/decisions.md` after the user validates the frame sentence (this skill, on validation), carrying `Frame sha256` — the fingerprint of the sentence approved.
- `<engagement>/council-log.md` summary lines (this skill + chairman-synthesis).

## Execution steps

### 1. Pre-flight

1. Resolve the engagement root and read `_state.json`. If `phase != discovery` → stop with: "/frame transitions Discovery → Framing; current phase is `<phase>`. Use /options or /decide instead." Exception: if `phase == framing` already, treat this as a re-run (subsequent framing round).
2. Read `library/kernel/phases.md`, section "Phase 2: Framing — Entry criteria".

### 2. Soft gate check (Discovery exit criteria, advisory)

**The mechanical verdict already exists.** The `phase-gate-check.py` hook evaluated Discovery's criteria before this skill loaded and wrote them to `<engagement>/gate-log.md` (id `G-discovery-framing-...`, coverage *n de m por codigo*). Read that line, repeat it to the user, and add what the motor does not do: the comprehension test below is recorded there as `juizo`, and it is yours. A criterion recorded as `n/a` is never re-stated as OK.


Compute from `shared-understanding.md`:

- `confirmed_count` — rows in `## Confirmed`.
- `unknown_critical_count` — rows in `## Unknown` with `criticidade = Critical`.
- `conflicted_critical_count` — rows in `## Conflicted` with `criticidade = Critical`.
- `perspectives_covered` — the `lens` coverage record of the last completed Discovery round (`python library/kernel/tools/coverage.py round-state --engagement <slug> --round <round> --json`): valid for that round, current or not, reviewed or not. The gate log already carries it.

Soft criteria from `phases.md`:
- `confirmed_count ≥ 10`.
- `unknown_critical_count == 0`.
- `conflicted_critical_count == 0`.
- the last completed round has a valid `lens` coverage record (the six perspectives recorded — `library/kernel/coverage-contract.md` §4.8).
- `_state.json.round_in_progress` empty. Non-empty and ahead of `round` means a passagem is still open: part of the lenses ran and the round never closed (`library/kernel/phases.md` → *Rounds — in progress vs completed*). Soft, like the rest — report it as a red criterion naming the open round and what its coverage record says (`engagement.lentes_ronda_aberta`: `fecha`, `revista`, `motivos`, from the motor), and offer `/round --close` (or a full `/round`) before the transition. The flip in step 5 clears `round_in_progress` either way: Framing does not inherit an open Discovery round.

**Comprehension survival test** (same gate, same soft doctrine — no score, no completeness percentage, no fixed question count). Read the SU and, where it exists, `_capture/process-model.md` §4/§6 plus the lens `Open evidence` blocks, and answer each question with the ids that make it true or with the concrete missing understanding:

1. Can the material process be explained without naming the future solution?
2. Is every materially important output family traceable (inputs → transformations → consumer) or explicitly `Unknown`?
3. Are the behaviours the business cannot lose represented as rows?
4. Are the known structural constraints represented as rows?
5. Are the suspected decision-changing structural constraints explicit `Unknown`s (`swing: decisivo`)?
6. Are the material scope / user-task obligations visible as rows?
7. Has every Critical `PM-U` row and every labelled material synopsis line received a disposition (`aisa-round` step 5b — `undisposed` must be empty)?

A failing question is a red criterion. **Do not pretend comprehension is sufficient**: name the missing understanding concretely — shape: `output X has no identified consumer`, `material calculation chain Y is not reconstructed`, `structural question Z (where must the data live?) is still absent`, `PM-U-NNN (Critical) undisposed` — and route it through the existing mechanisms: another `/round <perspective>` to adopt or dismiss it into the SU, or `/answer` when the sponsor already answered. Never manufacture an SU row, a process model or an Options set from this gate. Few open Unknowns ≠ deep understanding: a 100% epistemic health with an untraced material output family still fails question 2.

If any criterion is red AND no `--override` was passed → stop with a one-line-per-criterion summary and ask the user: "Proceed anyway (re-run with `--override "<reason>"`)? Or run more Discovery rounds (`/round`)?" Do not transition yet.

If `--override` is set, log the override reason — it goes into `decisions.md` as part of the frame approval's metadata (`Override used at /frame`, the existing soft-gate record; no new field). An override of the comprehension survival test names the failing question(s) in the reason.

**Override ≠ evidence · override ≠ resolution · override ≠ absence.** An override changes whether execution may proceed; it never changes what is known. The gate output therefore records, and the chairman reads:

```text
gate: FAIL
missing understanding: <category> — <specific gap>   (one line per gap)
override: YES
override reason: <reason>
proceed: allowed under existing soft-gate doctrine
```

The missing item stays visible as what it honestly is — an SU `Unknown` (written first, through the existing authority model, if it does not yet exist), an unresolved material trace, or an `undisposed` line named by `aisa-round` step 5b — and the chairman projects **that id** into the survival block. The chairman never writes `(none) — <override reason>`: `(none) — <reason>` is reserved for the substantive conclusion that **no material item of that semantic class exists for this engagement** (`chairman-synthesis` → rules for the survival block). An override that hides a missing material trace behind `(none)` is a defect, not a projection.

### 3. Flip state to Framing (through the coordinator)

1. Determine the framing round:
   - If `_state.json.round` does not yet start with `F-` → set `round = F-01`.
   - Else → increment (`F-01` → `F-02`).
2. Update `_state.json`: `phase = framing`, `round = <F-NN>`, `round_in_progress = ""` (an open Discovery passagem does not cross the phase boundary; it stays in the log, not in the state). Items 2 and 3 are one draft — `resolve.py draft --engagement <slug> --files _state.json shared-understanding.md --json`, edit the copies, `resolve.py publish` (`library/kernel/orchestration.md` → *Writing an authority*); never `mv` a `.tmp` over `_state.json`.
3. Update the SU header `Fase actual: Framing` and `Última actualização: <ISO timestamp>` (same draft).

### 4. Assemble the framing context

Bookkeeping only — the same resolution `aisa-round` step 3.6 performs, reused here. The orchestrator
resolves paths and one manifest key; it decides nothing about what any of it means.

a. **Shared evidence** — `<engagement>/_capture/evidence-index.md`. Present → carry its path to the
   analyst and to the reviewer. Absent → carry the explicit line
   *"no `_capture/evidence-index.md` — raw `inputs/` is the evidence surface"*; never assume a shared
   capture exists. Name likewise any source reported `failed` or `skipped`. Do **not** rank, assign,
   summarize or bundle sources: the index is a source map.
b. **Pack attention cues** — read `_state.json.pack`, resolve `library/packs/<pack>/pack.yaml` →
   `lenses_config.<lens>.extra_signals` for the six perspectives. Missing `pack` key, missing
   `lenses_config.<lens>`, missing `extra_signals` or an empty list → inject nothing for that
   perspective and omit the cue line. A `pack.yaml` that does not parse is a visible failure — report
   it and stop. Pass the tokens through **verbatim**: no scoring, ranking, filtering, reordering or rewriting.
c. **Resolutions already closed** — the rows marked `resolved →` and the `C-` rows carrying `(was …)`:
   neither the analyst nor the reviewer re-litigates them.

**solution-architect is NOT invoked in Framing.** Framing is pre-technology — no vendor or product names anywhere in this skill.

### 5. The integrated analyst proposes (inline)

Framing mode of the same analyst that runs `/round`. Read the SU (the whole of it, with the closed
resolutions of 4c), `enquadramento.md`, the shared evidence of 4a, the earlier `lens-outputs/`, the
process synopsis when it exists, and the perspectives of `library/kernel/lens-checklists.md`. Then write
the proposal to `<engagement>/lens-outputs/_council-prep/F-<NN>-analyst.md`, in the return schema that
`chairman-synthesis` parses (*Return schema* → the six sections), under
`## analista integrado — Round F-<NN> / Phase Framing`:

- **Headline** — the proposed single sentence: *the problem is X, felt by Y, costs Z today, evidence is W*.
- **Evidence anchors** — per clause, the SU ids or locators that carry it; per `M-n`, confirmed or
  corrected, with the evidence (a corrected invariant is a transition, `was C-nnn`, written by the
  synthesis).
- **Proposal** — the survival candidates (process meaning, invariants, structural constraints,
  decision-changing Unknowns, scope obligations), as ids.
- **Open questions / Unknowns flagged** · **Conflicts seen** · **Risks** — each by id.

A clause with no anchor says so; the analyst never manufactures one. Pack cues from 4b are cues, not a
checklist. The analyst does not write the SU here: the synthesis does (step 6).

### 5b. One independent reviewer contests (subagent)

Launch **one** subagent with the Agent tool — `subagent_type: frame-reviewer` — with fresh context, in
sequence, after the proposal exists. Pass only paths: the engagement root, the proposal file,
`shared-understanding.md`, `enquadramento.md` and the evidence pointer of 4a. No summary of the analysis
and no opinion on the sentence: its independence is its only value. It returns findings (target,
severity, kind `fact` | `recommendation`, premise/evidence, failure scenario, closing condition), the
coverage of its review, and optionally an alternative sentence. Save the return **verbatim** to
`<engagement>/lens-outputs/_council-prep/F-<NN>-reviewer.md`.

Reviewer unavailable or it fails → proceed; log `F-<NN> — revisão independente não feita (<razão>)` in
`council-log.md` and say so in step 7. A frame that was not reviewed is never presented as reviewed.

### 6. Synthesis (chairman-synthesis, Framing mode)

Invoke the `chairman-synthesis` skill with the two returns — the analyst's proposal and the reviewer's
findings —, the `<engagement>` paths, phase = `framing`, round = `F-<NN>`. It applies the chairman's
evidence rules (`chairman-synthesis` → *Framing inputs*): agreement between the two is not evidence; a
factual finding with a locator is a correction by evidence; a factual divergence without a locator
becomes `Conflicted` (`partes = analista∧revisor`); a recommendation divergence (wording, scope,
emphasis of the sentence) is **not** settled by the synthesis — it is listed for the owner and asked in
step 7. There is no antithesis round. It writes `frame.md`, the new SU rows and the synthesis log.

Before invoking it, **open the chairman's draft** — `python library/kernel/tools/resolve.py draft --engagement <slug> --files shared-understanding.md _state.json council-log.md --reads _map/map.json context.json decisions.md enquadramento.md answers.md frame.md options.md '_capture/*' 'inputs/**/*' 'lens-outputs/*.md' 'lens-outputs/_council-prep/*' '_simulation/**/*' --json` — and pass its `path`: chairman-synthesis writes the SU rows, the round and its log line into those copies (`library/kernel/orchestration.md` → *Writing an authority*). When it returns, **publish** it (`resolve.py publish --engagement <slug> --draft <id>`); an `INTEGRITY_FAILURE` goes back to chairman-synthesis to fix in the copy, a `STALE_INPUT` means reopening the draft on the current base.

### 7. Present the frame to the user and ask for validation

Output to the user (business language — `CLAUDE.md` → *Duas línguas*; kernel labels and ids only between parentheses). The contract block *What must survive into Options (projection of SU ids — `frame.md`)* renders as «O que tem de sobreviver até às alternativas»: same five sub-lists, same `(none) — <reason>` semantics, ids projected from the SU.

```user-output
Proposta de frase do problema (passagem F-NN):

  <a frase, de `frame.md`>

Em que se apoia:
  - <uma linha por cláusula, com os factos que a sustentam (ids)>

Perguntas em aberto que ainda pesam: <nenhuma | <pergunta curta> (U-nnn) …>
Onde as fontes ainda se contradizem: <nenhuma | <contradição curta> (X-nnn) …>
O que o revisor independente contestou: <nada de material | <n> — <achado curto> (alvo) … | a revisão não foi feita — <razão>>

O que tem de sobreviver até às alternativas (frame.md):
  O que o processo significa:        <uma linha (ids)> | nada — <porquê>
  Regras do negócio que não mudam:   <uma linha cada (ids)> | nada — <porquê>
  Restrições estruturais:            <uma linha cada (ids)> | nada — <porquê>
  Perguntas que mudam o caminho:     <uma linha cada (ids)> | nada — <porquê>
  Obrigações de âmbito e tarefas:    <uma linha cada (ids)> | nada — <porquê>

Compreensão suficiente para avançar: <sim | não — falta: <categoria — lacuna>, … · avançar mesmo assim: sim — <razão> (D-NNN)>

A seguir: valida a frase — a pergunta vem já a seguir (aceitar · editar · mais passagens).
```

**Before asking, check whether this sentence is already approved.** Run
`python library/kernel/tools/dashboard.py --engagement <slug> --json <tmp>/model.json --quiet`
and read `frame.verdict` (`library/kernel/phases.md` → *Frame approval record*). `match` or
`match-other-round` → the sentence did not change since approval `frame.latest.id`: **do not
ask again and do not write a new block**. Append one line to `council-log.md` —
`F-<NN> — frame unchanged since <D-00x> (sha256 match) — aprovação mantida` — and tell the
user:

```user-output
A frase do problema não mudou desde que foi aprovada (D-00x) — continua aprovada; nesta passagem só as âncoras foram refeitas.
A seguir: → `/options` para pôr as alternativas na mesa.
```

Otherwise ask via `AskUserQuestion` (never a prose question): *Aceitar a frase* (description: registo a aprovação como uma decisão própria (D-NNN) em `decisions.md`, com a impressão digital da frase) · *Usar a frase do revisor* (only when the reviewer proposed one; description: a alternativa do revisor independente, e porquê) · *Editar a frase* (description: escreve a tua versão em "Other"; escrevo-a em `frame.md` e registo essa) · *Mais passagens de descoberta* (description: volto à etapa de ouvir e perguntar; `/round` corre de novo). Every recommendation divergence the synthesis listed for the owner is decided here, by the owner — never by the synthesis.

### 8. On validation, write the approval (this skill)

**Order matters**: the final sentence goes into `frame.md` FIRST, then the motor computes
its fingerprint, then the block is written. The fingerprint in `decisions.md` is therefore
always the fingerprint of a sentence that really is on file — never of the text typed into
the block (a pilot held an English sentence in `frame.md` and a
Portuguese one in `D-001`: that drift is what this ordering closes).

1. If the user edited the sentence, write it into `frame.md` under `## Single problem sentence`.
2. Run the motor (`--json`) and read `frame.sha256` — never compute a hash by hand.
3. Read the next free id: `max(D-NNN in decisions.md) + 1`, zero-padded to 3 digits. It is
   **not** always `D-001`; frame, solution and blueprint approvals share one counter.
4. Append to `<engagement>/decisions.md` — through a draft that declares the frame as read (`resolve.py draft --engagement <slug> --files decisions.md council-log.md --reads frame.md shared-understanding.md enquadramento.md --json`, then `resolve.py publish`; a `frame.md` changed after its fingerprint was read is `STALE_INPUT`) — the record contracted in
   `library/kernel/phases.md` → *Frame approval record*:

```markdown

## D-NNN — Frame agreed (F-NN)

- **Frame sentence**: <final agreed sentence, verbatim as written in frame.md>
- **Agreed in round**: F-<NN>
- **Frame sha256**: <frame.sha256 from the motor>
- **Supersedes**: <D-00x (frame F-0y) — the previous frame approval, if any | —>
- **Anchors**: <list of clause → SU ids>
- **Override used at /frame**: <reason or "—">
- **Validated by**: owner (<name/role>, via AskUserQuestion) | executor [ÂMBITO AUTORIZADO]
- **Timestamp**: <ISO-8601>
```

Never edit an existing block: `decisions.md` is append-only, and `Supersedes` in the new
block is the only pointer written (the motor derives the reverse one).

Then append a one-line summary to `council-log.md`: "F-<NN> — frame agreed (D-NNN)".

### 8a. On "more rounds"

Roll back `_state.json.phase` to `discovery` and leave `round` at the last completed Discovery round (`R-NN`). Tell the user:
```user-output
Voltámos a ouvir e perguntar (Discovery, ronda R-NN) — a frase do problema fica para depois.
A seguir: outra passagem das perspectivas pelo material → `/round`.
```

### 8b. On "edit: <new sentence>"

Overwrite the single-sentence line of `frame.md` with the user's edit (preserve all other sections), then proceed with step 8 using the edited sentence.

### 8c. Story

Append one narrative episode to `<engagement>/story.md` (`## Episódio <N> — <data> — o problema ganhou uma frase (frame)`): um parágrafo curto na voz do sponsor, sem jargão de kernel, máx. 2 ids citados. Create the file with `# Story — <slug>` if missing (pre-v2.3 engagements).

### 9. Wrap-up output

```user-output
Frase do problema fixada e aprovada (D-NNN, passagem F-NN).
A seguir: comparar alternativas — aqui entra pela primeira vez a perspectiva tecnológica → `/options`; ou `/status` para ver onde estamos.
```

## Notes

- **Subagents** (`CLAUDE.md` → *Delegação a subagentes*): the analysis runs inline; the reviewer is the one subagent, launched once, in sequence, after the proposal exists. No parallelism: the reviewer reviews what the analyst wrote.
- **One return schema.** The analyst writes its proposal in the schema `chairman-synthesis` owns (*Return schema* → the six sections), so the synthesis reads Framing as it reads any return.
- **Only the synthesis writes the SU.** The reviewer has `tools: [Read, Grep, Glob]` and returns findings as text — it cannot write even if it tried.
- **The survival block is a projection, not a second truth.** Semantic ownership of invariants, constraints, obligations and Unknowns stays in the SU; `frame.md` names ids. If the chairman notices a missing material item while framing, the SU row is written first and projected second (`chairman-synthesis` step 6). In Options the technical author reads the block (`aisa-options` step 4); the Options blocking set remains the primary candidate-specific check.
- **Idempotence**: re-running `/frame` is allowed (produces F-02, F-03, …). The previous `frame.md` is overwritten; chairman-synthesis-F-<NN>.md from each round is preserved.
