---
name: aisa-options
description: Transition Framing → Options. Checks Framing's exit gate, flips _state.json to phase=options/round=O-NN, has the technical author write and publish the candidates by route (review.py), routes the independent review to the specialists the risk calls for (one specialist-reviewer subagent per published mandate), then invokes chairman-synthesis to dispose the findings and write options.md and the Shared Understanding rows.
---

# aisa-options

## Usage

`/options [--override "<reason>"] [--reopen "<justificação>"]`

- No argument: runs the soft gate check; if any criterion is red and no override is provided, stop with a clear summary and ask the user before proceeding.
- `--override "<reason>"`: bypass the soft gate. The reason is logged in `decisions.md`.

## Phase model

- **From**: `phase: framing`.
- **To**: `phase: options`, `round: O-01` (subsequent options rounds become `O-02`, `O-03`, …).
- **Mode** (handoff-v1 F5): the technical author (`solution-architect` mandate) writes the candidates **inline** and publishes them; an explainable router picks the specialist reviewers the risk calls for; each runs as a subagent on its published mandate; `chairman-synthesis` disposes the findings. This is where vendor/product naming becomes allowed (via `lens-technology`).

## Inputs (read)

- `<engagement>/_state.json`, `<engagement>/context.json`, `<engagement>/shared-understanding.md`, `<engagement>/decisions.md`, `<engagement>/council-log.md`.
- `<engagement>/frame.md` (the agreed problem sentence from Framing).
- `<engagement>/lens-outputs/*.md` (incl. any prior chairman-synthesis logs).
- `library/kernel/phases.md` (Options entry criteria).
- `<engagement>/_capture/evidence-index.md` (the shared evidence surface).
- `<engagement>/_design/candidates.json` and `_design/reviews/` (published by `review.py`).
- `library/kernel/specialists.md` (roles, router rules, output contract).
- `decision-tree.md` and `domain-knowledge/*.md` are the technical author's to pull, selectively, for the option it is actually evaluating (`library/kernel/orchestration.md` → *Pack context*).

## Outputs (written, via chairman-synthesis except where noted)

- `<engagement>/_state.json` — through the coordinator (this skill; `library/kernel/orchestration.md` → *Writing an authority*).
- `<engagement>/_design/candidates.json` (+ `_design/history/`), `_design/reviews/REV-NNNN.mandate.json`, `REV-NNNN.json` and `ledger.json` — only through `review.py` (this skill and chairman-synthesis).
- `<engagement>/options.md` (chairman-synthesis).
- New rows in `<engagement>/shared-understanding.md` (chairman-synthesis).
- `<engagement>/lens-outputs/chairman-synthesis-O-<NN>.md` (chairman-synthesis).
- `<engagement>/council-log.md` summary lines (this skill + chairman-synthesis).

## Execution steps

### 1. Pre-flight

1. Resolve the engagement root and read `_state.json`. Run the motor once —
   `python library/kernel/tools/dashboard.py --engagement <slug> --json <tmp>/model.json --quiet` —
   and read `frame`, `reopen` and `options_history` from it. Then, by phase:
   - `framing` or `options` → normal path (a second `options` run is a re-run);
   - **`decision` → reopening the alternatives** (`library/kernel/phases.md` → *Transition rules*).
     Allowed when `reopen.verdict == "REABRIR"` (the latest `/revisit` recommended it) **or**
     the user passed `--reopen "<justificação>"`. Neither → stop:
     ```user-output
     Já há uma decisão registada (D-00x). Voltar a pôr as alternativas na mesa exige uma condição de revisão que tenha disparado, ou uma razão tua.
     A seguir: `/revisit TW-n` para ver o que mudou → ou `/options --reopen "<a tua razão>"` para reabrir na mesma.
     ```
     `--reopen` without a justification stops the same way: the reason is the record.
     When `reopen.decision` names a decision that is not the one in force
     (`status.tripwires.source_decision`), stop and say which is the current one.
   - any other phase → stop with: "/options transitions Framing → Options; current phase is `<phase>`. Use /frame first."
2. **Is the sentence on file the approved one?** Read `frame.verdict` (`library/kernel/phases.md`
   → *Frame approval record*). This replaces the old existence check for a `D-001` line, which
   could not tell an approval of THIS sentence from an approval of a previous one (F05):

   | `frame.verdict` | What it means | What this skill does |
   |---|---|---|
   | `match` | approved, in the current framing round | continue |
   | `match-other-round` | same sentence, approved in an earlier round (only the anchors were redone) | continue; say so in one line |
   | `none` | there is a sentence, and nobody approved it | ask (below) |
   | `mismatch` | the sentence changed since the last approval | ask (below), showing **both** sentences |
   | `legacy` | the approval predates the fingerprint rule — it cannot be verified | ask (below) |
   | `no-frame` | there is no sentence yet | stop: *"Ainda não há uma frase do problema. A seguir: → `/frame`."* |

   For `none` / `mismatch` / `legacy`, show the current sentence (and, for `mismatch`, the
   approved one under it) and ask via `AskUserQuestion` — never a prose question:
   *Aprovar a frase actual* (description: escrevo a aprovação como decisão própria (D-NNN) com a impressão digital da frase; em `mismatch`/`legacy` leva `Supersedes: D-00x`) ·
   *Refazer a frase* (description: volto ao passo da frase do problema — `/frame`) ·
   *Avançar sem aprovação* (description: escreve a razão em "Other"; fica registada e a frase continua por aprovar).
   Approving here writes exactly the record of `phases.md` → *Frame approval record*, by the
   same order as `aisa-frame` step 8 (sentence in `frame.md` first, fingerprint from the motor,
   then the block). "Avançar sem aprovação" writes `## O-NN — gate override (frame <verdict>) — <ts>`
   with the justification into `council-log.md` and **never fabricates an approval**; `/status`
   keeps showing the sentence as unapproved.
3. Read `library/kernel/phases.md` (Options entry criteria).

### 2. Soft gate check

**The mechanical verdict is in `<engagement>/gate-log.md`** (id `G-framing-options-...`), written by `phase-gate-check.py` before this skill loaded. Repeat it and add the judgement; a criterion recorded as `n/a` is not OK.


- Frame approval covers the current sentence (`frame.verdict` ∈ {`match`, `match-other-round`}) → checked in pre-flight 2; an override there is this criterion's override.
- Sponsor confirmation captured in the approval record (`Validated by`).

If a soft criterion is red and no `--override` was passed → stop with a one-line-per-criterion summary and ask the user. If `--override` is set, log the reason — it goes into `decisions.md` alongside D-NNN.

### 3. Flip state to Options (through the coordinator)

1. Compute the options round **from history, never from `_state.json` alone**: use
   `options_history.next` from the motor (highest of `lens-outputs/chairman-synthesis-O-NN.md`,
   the `## O-NN` headings of `council-log.md`, and the state when it holds an `O-`). After a
   decision the state holds `D-01`, and deriving `O-01` from it would overwrite the very round
   that produced the decision being revisited (F07).
2. Update `_state.json`: `phase = options`, `round = <options_history.next>`, `round_in_progress = ""`
   (a Discovery passagem left open never crosses a phase boundary). Items 2, 2b and 3 are one
   draft — `resolve.py draft --engagement <slug> --files _state.json shared-understanding.md
   council-log.md story.md --json`, edit the copies, `resolve.py publish` (`library/kernel/orchestration.md` → *Writing an authority*);
   never `mv` a `.tmp` over `_state.json`.
2b. **When this is a reopening**, also append to `council-log.md`:
   `## O-NN — reabertura da decisão D-00x — <ISO ts>` with what triggered it
   (`_simulation/<revisit file>`, `TW-n`) or the `--reopen` justification, and the line
   `_state.json → phase=options, round=O-NN (era decision/D-NN)`. The previous decision is
   **not touched**: `/decide` will write the new block with `Supersedes: D-00x`. Append one
   episode to `story.md` ("voltámos a pôr as alternativas na mesa — <porquê>").
3. Update the SU header `Fase actual: Options` and `Última actualização: <ISO timestamp>`.

### 4. Author the candidates (inline — the technical author)

The session runs the technical author's mandate, `.claude/agents/solution-architect.md` — inline, not as a Task subagent: it needs the whole engagement, and the candidates are the product (`docs/handoff-v1/F5/DESENHO.md` §0, Q1). It reads the **full** Shared Understanding (resolved rows and their resolutions included — closed conflicts are not re-litigated), `frame.md`, `decisions.md`, `context.json`, the shared evidence (`<engagement>/_capture/evidence-index.md`; when absent, the explicit line *"no `_capture/evidence-index.md` — raw `inputs/` is the evidence surface"*), the process synopsis when it exists (`_capture/process-model.md` §4 — the compact cross-source reconstruction; markers OBSERVED / INFERRED / HYPOTHESIS / UNKNOWN are evidence markers, not states; open its detail sections or a raw source only when material to your confidence), the process map at the depth this step needs (process-map M4: `python library/kernel/tools/process_map.py summary --engagement <slug> --task options --json` — the calculations, volumes, exceptions and decisions each candidate must support, with the references to open when material), and its memory `.claude/agent-memory/_universal/architect/*.md` — a pointer, never contents in a prompt. Its pack access is pull-based and Options-only: the `decision-tree.md` stage it is executing and the `domain-knowledge/` it actually needs, cited. The technical author receives no Discovery `extra_signals`.

1. `python library/kernel/tools/review.py draft-candidates --engagement <slug> --json` → edit the draft's `candidates.json` (`handoff-candidates/1`): each candidate `O-NNN` with its option class, technology and form, high-level architecture, order of magnitude with its source, risks, reversibility, premises (SU ids) and sources; at the set level the criteria, the exclusions with their reason and the route.
2. The route is `_state.json.workflow.route`, and the engine enforces its rule (`library/kernel/handoff-contract.md` → *Options candidates*):

   | Route | What the candidates are |
   |---|---|
   | `solution-choice` | the options that really apply; fewer than three only with `reduction_reason` |
   | `platform-constrained` | variations of architecture and implementation **inside** the imposed platform (`imposed_platform`, `imposition_ref` = the route's authority); one viable candidate is admitted with its reason — no artificial shortlist of platforms |
   | `change-impact` | the delta on a `baseline_ref`, with its `impact_refs` and the decisions to reopen |

3. `review.py check-candidates --engagement <slug> --draft <id>` → an `INTEGRITY_FAILURE` is fixed in the draft; a `BLOCKING_GAP` (an order of magnitude without source, a missing architecture or reversibility) stays visible and may be published.
4. `review.py publish-candidates --engagement <slug> --draft <id>` — one coordinator operation, revision + immutable history. **No reviewer runs before this**: a candidate still under construction is never reviewed.

### 5. Route the review and publish the mandates

1. `review.py route --engagement <slug> --json` → every role evaluated: `selected` (with the evidence that fired it) and `not_called` (with what was checked). Both go into the synthesis log; a role is never dropped silently.
2. For each selected role, the author maps the material questions to it — each with its closing condition — and names the scope ids, the pack units it judged relevant and, when useful, files of that role's memory (`.claude/agent-memory/_universal/<role>/`): `review.py mandate --engagement <slug> --role <role> --question "<…>" [--question …] --scope <id> [--knowledge <path> …] --json`. The mandate is published **before** the reviewer runs; a `BLOCKING_GAP` refusal (no published revision, or a candidates draft open) means publish first.

### 5a. Launch one specialist reviewer per mandate

Send **one assistant message with one Task call per mandate** (they read the same published revision and do not depend on each other). Each Task call:

- `subagent_type`: `specialist-reviewer`;
- `prompt`: the engagement root and the mandate path — nothing else. No author reasoning, no other review, no summary of the candidates.

Save each return as `<engagement>/lens-outputs/_council-prep/O-<NN>-REV-NNNN.json` (audit trail) and publish it: `review.py receive --engagement <slug> --task REV-NNNN --file <that path>`. An `INTEGRITY_FAILURE` (contract, coverage, a source outside the mandate) goes back to the same reviewer once, with the refusal reason; a `STALE_INPUT` means a new mandate on the current base.

### 5b. Dialectic round (conditional, bounded by the engine)

When chairman-synthesis reports a material divergence (two findings, or a finding against the author's candidate), open it — `review.py diverge --engagement <slug> --finding <REV-NNNN.Fnn> [--finding …] --subject "<…>"` — and run the antithesis: two `specialist-reviewer` Task calls in parallel, each receiving its own mandate path and the other side's review path, with the *Antithesis mode* of its agent file. Record each call: `review.py dialectic-call --divergence DIV-NN --outcome synthesis_accepted|contested [--synthesis "<…>"] [--locator <…>]`. The engine keeps the cap (3 divergences × 2 calls per candidate revision): the fourth divergence is born `escalated`, two calls without an accepted synthesis escalate, and a factual divergence is never synthesised without a locator. An escalated divergence goes to the owner through `AskUserQuestion` — never accepted by exhaustion.

### 6. Hand off to chairman-synthesis

Invoke `chairman-synthesis` with phase = `options`, round = `O-<NN>`; it reads the published candidates and `review.py show-reviews` (*Options inputs in a handoff-v1 engagement*), disposes every finding of a current review through `review.py dispose`, and writes `options.md` and the new SU rows.

Before invoking it, **open the chairman's draft** — `python library/kernel/tools/resolve.py draft --engagement <slug> --files shared-understanding.md _state.json council-log.md --reads _map/map.json context.json decisions.md enquadramento.md answers.md frame.md options.md '_capture/*' '_design/*' 'inputs/**/*' 'lens-outputs/*.md' '_simulation/**/*' --json` — and pass its `path`: chairman-synthesis writes the SU rows, the round and its log line into those copies (`library/kernel/orchestration.md` → *Writing an authority*). When it returns, **publish** it (`resolve.py publish --engagement <slug> --draft <id>`); an `INTEGRITY_FAILURE` goes back to chairman-synthesis to fix in the copy, a `STALE_INPUT` means reopening the draft on the current base.

When a finding is accepted by changing a candidate, the author publishes the next revision (step 4); `show-reviews` then marks the old reviews `stale` and names the findings to revalidate — new mandates go only to the roles those findings belong to. A review of an earlier revision never becomes a review of the new one by copy.

Five contract checks before reporting to the user, all owned by `chairman-synthesis`:

1. **Every option names its technology**, and a platform option names its **form** — surface and store, one option per form (`decision-tree.md` §14.1; for `pp`, `decision-model/alternatives-register.md` §1.2). A round whose author produced a platform class with no form-level candidate is reported as such in `Summary` and raised as an open question — a form is never invented to fill the column.
2. **Every option carries an order of magnitude with its source marker**, or `ORDER OF MAGNITUDE UNAVAILABLE — <what is missing>`. A band with no source is invented; a blank cell is a contract breach.
3. **The round closes with the recommendation** — the option, what separates it from its siblings, what it rests on, what would flip it. Where the terminal is *decision blocked* or *multiple defensible options*, `no recommendation — <what would produce one>`. The recommendation is the aisa's; the choice is the owner's, at `/decide`.
4. **The artefact is within budget** (~1 500 words of prose, ≤120 per option). The full field set, the concern coverage and the `DO-NOTHING` / `PROCESS-CHANGE` class coverage live in `lens-outputs/chairman-synthesis-O-<NN>.md`.
5. **Every finding of a current review has a disposition** (`show-reviews` → `open_findings` holds only `deferred` / `escalated` ones, shown to the user), and every mandate was received or is reported as not received.

### 7. Present options to the user

Output to the user (business language — `CLAUDE.md` → *Duas línguas*; kernel labels and ids only between parentheses). Each line carries the option class in words (não construir nada · mudar o processo · construir …), **the technology named** — for an option built on the pack's platform, the *form*: the kind of application **and** where the data lives, in product names, because Options is the phase where that is said out loud — the effort driver and the reversibility. Same facts as the table in `options.md`, nothing added:

```user-output
Alternativas na mesa (passagem O-NN): <N>.

  - <nome> — <tipo: não construir nada · mudar o processo · construir …> — <tecnologia: <produto> sobre <onde os dados vivem> | sem tecnologia | por avaliar> — <ordem de grandeza: <banda>, <de onde vem: do ensaio · do modelo do pacote · por semelhança com <caso>> | ainda sem base: falta <o que falta>>, fácil de reverter: <pouco | médio | muito> (O-001)
  - <nome> — … (O-002)

O que o aisa recomenda, e porquê: <alternativa> — <o que a separa das irmãs, numa frase> (O-nnn). Assenta em: <pressupostos curtos> (<ids>). Mudava de ideias se: <o que a inverteria> (<ids>).
  <ou, quando não há base para recomendar: «Sem recomendação por agora: <o que falta para a haver>.»>
  A escolha é tua — isto é o parecer, não a decisão.

Alternativa que só passa se uma regra mudar: <nenhuma | <alternativa> — regra: <qual>, quem a pode mudar: <papel>, estado: <não pedido | pedido | recusado> (O-nnn)>
Perguntas em aberto que ainda pesam nas alternativas: <nenhuma | <pergunta curta> (U-nnn) …>
Onde as fontes ainda se contradizem: <nenhuma | <contradição curta> (X-nnn) …>

A seguir: lê `options.md`; ensaiar cada alternativa → `/simulate`; escrever o obituário do projecto → `/premortem`; escolher → `/decide`. Faltou uma classe de alternativa? → `/options` outra vez (sai a passagem seguinte).
```

### 7b. Story

Append one narrative episode to `<engagement>/story.md` (`## Episódio <N> — <data> — as opções na mesa`): um parágrafo curto na voz do sponsor, sem jargão de kernel, máx. 2 ids citados. Create the file with `# Story — <slug>` if missing (pre-v2.3 engagements).

### 8. Wrap-up output

```user-output
Alternativas fechadas (passagem O-NN) — <N> na mesa, <n> sem construir nada.
A seguir: ensaiar antes de escolher → `/simulate`; o obituário do projecto → `/premortem`; escolher → `/decide`.
```

## Notes

- **Subagents** (README → *Regras de execução*; `docs/handoff-v1/F5/DESENHO.md` §0): the author and the chairman run inline — they need the session's context and their detail is the product. The specialist reviewers are subagents, one per published mandate, in parallel with each other and never with the author, who publishes first; they must **not** have the author's context nor each other's, and only their findings come back. The six Discovery personas are retired (handoff-v1 F5.4, Q4); their perspectives live in `library/kernel/lens-checklists.md` (Discovery) and `library/kernel/specialists.md` (Options).
- **Reviews, not votes.** How many reviewers agree never changes an epistemic state; a factual finding changes the SU only through a locator (`chairman-synthesis` → *Framing inputs*, the same rules).
- **Domain knowledge is pulled, never preloaded.** The author pulls what it needs; a reviewer reads only the pack units its mandate lists, with their `sha256`.
- **The technical author is the lone vendor-naming surface** before the reviews; a specialist names a technology only as the candidates already name it.
- **Idempotence**: re-running `/options` produces O-02, O-03, …. The previous `options.md` is overwritten; each round's `chairman-synthesis-O-<NN>.md` is preserved; the candidates move by revision, never overwritten in place.
