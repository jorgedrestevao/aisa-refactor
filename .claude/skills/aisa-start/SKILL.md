---
name: aisa-start
description: Start a new aisa engagement. Captures the literal request + requester, scaffolds the engagement folder, and writes the initial _state.json (phase=discovery).
---

# aisa-start

## Usage

`/start <slug> [pack]`

- `<slug>`: kebab-case slug for the engagement (e.g., `pedido-adiantamento`).
- `[pack]`: pack id (default: `pp`). Must exist as `library/packs/<pack>/pack.yaml`.

## Execution steps

1. **Resolve the engagement root**:
   - If `$AISA_ENGAGEMENTS_ROOT` is set → `<root>/<slug>/`.
   - Else → `projects/<slug>/` (assumes a symlink/junction is configured, or local MVP testing).
2. If the folder already exists → stop with: "Engagement `<slug>` already exists. Use /resume." Do not overwrite.
3. **Validate the pack**: confirm `library/packs/<pack>/pack.yaml` exists. If not, list available packs and stop.
3b. **Workflow profile and route** (handoff-v1 — `docs/handoff-v1/F1/DESENHO-CONTRATOS.md` §2.1). This version has no classic runtime: every engagement it creates is `handoff-v1`, still experimental. Asked **before anything is created**, each by `AskUserQuestion`:
   - **Profile** — *«Este trabalho segue o método novo, ainda experimental?»* — options *Sim, método novo (experimental)* (description: perfil `handoff-v1`) · *Não, usar a versão anterior* (description: continua em `jorgedrestevao/aisa@85baf10`; nada é criado aqui). *Não* → stop with that instruction; nothing is written.
   - **Route** — *«A plataforma da solução já foi decidida por quem tem autoridade para isso?»* — options *Ainda está em aberto* (description: rota `solution-choice`) · *Sim, já está decidida* (description: rota `platform-constrained`). `change-impact` is never chosen here: it enters by reopening an approved baseline (`library/kernel/phases.md` → reopening; `/revisit`).
   - *Sim* → one more `AskUserQuestion`: *«Que plataforma, e que papel a decidiu?»* — the answer comes in «Other», verbatim; the offered options are *Está escrito no pedido* (the executor quotes the literal request, verbatim) and *Ainda não sei quem decidiu*. A **role**, never a person's identity (`library/kernel/states.md` → *The role rule*). *Ainda não sei quem decidiu* → the route is `solution-choice`, and the justification says the imposition has no identified authority yet: an imposed platform needs one (plan 02 §5).
   - Then run `python library/kernel/tools/workflow.py check --pack <pack> --profile handoff-v1 --route <route>`. Exit ≠ 0 → stop and report the reasons as they came: a pack that does not declare the profile or the route is refused, with no fallback. Nothing is written before this passes.
4. **Capture from the user** (interactive — ask, do not invent). **Invoked by `aisa-orient`** with the request, requester, enquadramento declaration, invariants, authorities, funding gate and named-artefact answers (step 3b there) already collected verbatim → **do not ask again**; carry that verbatim into steps 6 and 9b and ask only what is still missing.
   a. The literal request, verbatim, with no reformulation.
   b. The requester: name, role, authority level.
   c. Optional: documents to drop into `inputs/`.
   d. **Enquadramento — the business mechanism, declared by the process owner** (P-0, `library/kernel/phases.md` → *Enquadramento (P-0)*). Before any lens runs, the owner says in their own words how the business works at the point the request touches. **Seven themes, fixed order, one `AskUserQuestion` per theme**, "Other" for free text, answer kept **verbatim**. The ids are stable and become the anchors of `enquadramento.md`:

      | # | id | pergunta ao dono |
      |---|---|---|
      | T1 | `actors` | Quem faz parte disto — que papéis intervêm, e quem manda no processo? |
      | T2 | `trigger` | O que faz este processo começar, e com que frequência? |
      | T3 | `activities` | O que se faz, por ordem, e onde é que se decide alguma coisa? |
      | T4 | `outcomes` | O que sai no fim, para quem, e como se sabe que correu bem? |
      | T5 | `invariants` | O que tem de se manter sempre verdadeiro — as regras que ninguém pode quebrar? |
      | T6 | `failure_today` | O que corre mal hoje, e quanto custa quando corre mal? |
      | T7 | `change_requested` | O que é que o pedido quer mudar nisto? |

   d1. **Activation of the `pricing` set** — immediately after **T4**, **one** `AskUserQuestion`, asked in **every** engagement, whatever the process looks like:

      > *A saída deste processo é um preço, cotação, margem ou valorização?* — options *Sim* / *Não*

      **Never inferred** from the narrative, from the slug, or from what the request seems to be about: a process that mentions money is not a pricing process, and a pricing process that never says so still gets asked. **Only `Sim`** opens these five, each its own `AskUserQuestion`, verbatim, before T5:

      | id | pergunta ao dono |
      |---|---|
      | `P1 sold_what_when` | O que se vende, e quando? |
      | `P2 price_fixing_moment` | Quando é que o preço se fixa, e quando é que a venda acontece? |
      | `P3 cost_driver` | O que determina o custo? |
      | `P4 valuation_driver` | O que determina a valorização? |
      | `P5 uncertainty_shape` | De onde vem a incerteza, e como evolui no tempo? |

      `Não` → none of the five is asked, and `enquadramento.md` has no `## pricing` section. A pack may add themes of its own through `pack.yaml: enquadramento.extra_themes[]`; every pack declares it empty today.

      After the themes, and in this order: read the invariants back from **T5** (`M-n`, business language, one sentence each — the owner's words, never a rewrite), then ask who besides them has authority to confirm facts about this process (`library/kernel/states.md` → *Confirmed threshold*, rule 3).
   d2. **Ficheiros nomeados mas não entregues** — only when this skill was invoked directly (not via `aisa-orient`, which already did this at its step 3b). Read whatever source material the interview drew on for a concrete artefact it names — a file, a report, a system, a spreadsheet someone was working from — that was not attached in this conversation. For each one, ask by name before continuing: one `AskUserQuestion`, *"A entrevista fala de `<artefacto>` — tens esse ficheiro?"*, options *Vou arranjá-lo antes de começar* · *Ainda não tenho, começa sem ele* · *Não se aplica*. Do not let this surface for the first time in the `aisa-capture` summary (step 11) after the folder already exists. No named artefact found → skip silently.
   e. **Funding gate** (`AskUserQuestion`, one question): *"A decisão de avançar depende de aprovação orçamental de terceiros?"* — options *Sim* / *Não*. The answer is the owner's declaration, never inferred from authority text or from the SU. It becomes `context.json.funding_gate` (`true` / `false`); when the key is absent the lenses behave as `true`. The enquadramento is **not the request**: it is the invariant the request serves. Never infer an `M-n` from the literal request or from `_capture/` — record only what the human said. If the owner names a vendor, product or solution, it stays in the verbatim and does not become an `M-n`. Owner unavailable → the file says *"não declarado"* and the lenses work as before.
5. **Create the folder structure**:
   ```
   <slug>/
   ├── _graph/ · _ops/           (empty graph + its receipt — step 5b; coordinated state, never hand-edited)
   ├── _state.json
   ├── context.json
   ├── enquadramento.md          (owner-declared business mechanism — step 9b)
   ├── shared-understanding.md   (skeleton — see below)
   ├── lens-outputs/             (empty)
   ├── council-log.md            (header only)
   ├── decisions.md              (empty header)
   ├── answers.md                (header only — filled by /answer)
   ├── inputs/                   (raw source material — any captured docs)
   └── _capture/                 (deterministic shared evidence generated from supported inputs — written by step 11; raw `inputs/` stays authoritative)
   ```
5b. **O engagement nasce com grafo — antes da primeira autoridade.** Logo depois de a pasta existir, e antes de escrever `_state.json`, a SU, `decisions.md`, `answers.md` ou as linhas `M-n` (passos 7–9b), correr uma vez:

    ```
    python library/kernel/tools/migrate.py init --engagement <slug>
    ```

    Publica um grafo vazio e válido pelo coordenador (recibo em `_ops/receipts/graph-init.json`). Idempotente: correr outra vez devolve `already`, e um grafo já existente nunca é substituído. **Não é opcional**, e a ordem também não: desde a decisão de tornar o grafo obrigatório (P7.5 §2), ausência de grafo bloqueia. Com `_state.json` escrito e sem grafo, o guarda de autoridade (`pre-authority-guard.py`) recusa escrever a SU e as decisões; com linhas na SU, `init` recusa (`NOT_EMPTY`) — isso migra-se. Depois do passo 7 já não há ordem que funcione. Tudo o que os passos 6–9c escrevem vai para **um** rascunho (passo 5c) e é publicado numa só operação do coordenador (passo 9d) — autoridades, linhas `R-00` e o seu espelho no grafo, com um recibo; um Edit directo da SU já não é espelhado por hook (handoff-v1 F2). Falha aqui → parar e reportar o erro tal como veio; não continuar para o passo 6 com o engagement por nascer.
5c. **Open the birth draft.** `python library/kernel/tools/resolve.py draft --engagement <slug> --files context.json _state.json shared-understanding.md council-log.md decisions.md answers.md story.md enquadramento.md --json`. Steps 6–9c write into the copies under the returned `path` (`_drafts/<id>/<file>`) — never into the engagement folder, never a `.tmp` renamed over a file. Nothing exists for any reader until step 9d publishes it (`library/kernel/orchestration.md` → *Writing an authority*).
6. **Write `context.json`** (birth-draft copy):
   ```json
   {
     "engagement": "<slug>",
     "literal_request": "<verbatim>",
     "requester": { "name": "<name>", "role": "<role>", "authority": "<authority>" },
     "funding_gate": true | false,
     "inputs": ["<filenames in inputs/>"],
     "captured": "<ISO-8601 timestamp>"
   }
   ```
7. **Write `_state.json`** (birth-draft copy; the coordinator publishes it atomically in step 9d):
   ```json
   {
     "engagement": "<slug>",
     "pack": "<pack>",
     "phase": "discovery",
     "round": "R-00",
     "round_in_progress": "",
     "aisa_version": "0.1.0",
     "created": "<ISO-8601 timestamp>",
     "workflow": {
       "profile": "handoff-v1",
       "schema_version": "handoff-state/1",
       "route": "<solution-choice | platform-constrained>",
       "route_revision": 1,
       "route_basis": {
         "justification": "<the owner's route answer, verbatim>",
         "source_refs": ["answers.md#ROTA"],
         "authority_ref": "<C-001 when platform-constrained, else null>"
       },
       "route_history": []
     }
   }
   ```
   The `workflow` block is the engagement's profile and route (`library/kernel/schemas/handoff-state.schema.json`). It is written here once; afterwards no tool write may change it or drop a key of `_state.json` (`pre-authority-guard.py` refuses) — a route change is a new revision through `library/kernel/tools/workflow.py` and the coordinator.
   (`round` seeds at `R-00` — no round has **completed** yet. The first `/round` opens `R-01` and closes it when all six perspectives have stamped it (or on `/round --close`). `round_in_progress` seeds empty — no round open; `/round` fills it while a passagem is in flight and clears it on close (`library/kernel/phases.md` → *Rounds — in progress vs completed*).)
8. **Write the `shared-understanding.md` skeleton** (birth-draft copy; the 5 state sections with their column headers, per `library/kernel/states.md`; `verificado_em`/`validade` per its *Epistemic half-lives* section; `custo`/`swing` per its *Question economics* section; the question columns per its *Admission of a question* section; the epistemic health is computed on every read — `/status`, the dashboard — and never written into the SU):
   ```markdown
   # Shared Understanding — <slug>

   > Engagement: <name>
   > Sponsor: <requester name>
   > Iniciado: <date>
   > Fase actual: Discovery
   > Última actualização: <timestamp>

   ## Confirmed

   | id | lens | claim | evidência | verificado_em | validade | ronda |
   |----|------|-------|-----------|---------------|----------|-------|

   ## Assumed

   | id | lens | claim | base da assumption | verificado_em | validade | ronda |
   |----|------|-------|--------------------|---------------|----------|-------|

   ## Unknown

   | id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | ronda |
   |----|------|----------|------|---------|--------|---------------|-------|----------|-------------|-------|-------|-------------|-------|

   ## Conflicted

   | id | lens | conflito | partes | impacto | âmbito | quem decide | fecho | bloqueio | criticidade | referências | ronda |
   |----|------|----------|--------|---------|--------|-------------|-------|----------|-------------|-------------|-------|

   ## Risky

   | id | lens | risco | impacto | mitigação proposta | ronda |
   |----|------|-------|---------|--------------------|-------|
   ```
9. Write, in the birth-draft copies, `council-log.md` with a header (`# Council Log — <slug>`), `decisions.md` with a header (`# Decisions — <slug>`), `answers.md` with a header (`# Answers — <slug>`) followed by a section `## ROTA — <date>` holding the step-3b route questions and answers verbatim, and `story.md` with `# Story — <slug>` + **Episódio 1** (o pedido: quem pediu, o quê, porquê — 4-6 frases na voz do sponsor).
9b. **Write `enquadramento.md` and the `R-00` rows** from step 4d. File: header (owner, date, executor, literal request), then **one section per theme, in order and with the stable anchor** — `## T1 · actors`, `## T2 · trigger`, `## T3 · activities`, `## T4 · outcomes`, `## T5 · invariants`, `## T6 · failure_today`, `## T7 · change_requested` — each carrying the owner's answer **verbatim**. **`## pricing` exists only when the owner answered *Sim* at step d1**, carries the marker `<!-- INTAKE-SET: pricing -->` on its first line, and holds the five answers (`P1`..`P5`) verbatim; answered *Não*, the section is absent — never present and empty. Then a table `id · invariante · o que orienta · fonte` built from **T5 verbatim** (one `M-n` per declared sentence, nem mais nem menos), the named authorities (or *"Ninguém — só o dono"*), and the rules block (hypothesis of the owner; `/frame` confirms or corrects each `M-n`; nothing inferred; no vendor). Each `M-n` then enters the SU as `Confirmed`: `lens = enquadramento`, `ronda = R-00`, evidência = `declaração do dono do processo, <date> — enquadramento.md#M-n`, `verificado_em` = today, `validade = organizacional`. Log one line in `council-log.md` (`R-00 — enquadramento: M-1..M-n declarados pelo dono`). *"Não declarado"* → write the file with that line and no rows. Everything here goes into the birth-draft copies (step 5c), never into the engagement folder; step 9d publishes it. The **older** shape (no `Tn` sections, written before this contract) is read as it is and never rewritten; the presence of the sections is what distinguishes the shapes, never a date or a version number.
9c. **The route's authority row.** When the route is `platform-constrained`, the imposition enters the SU (the birth-draft copy) as `C-001` in `## Confirmed`: `lens = enquadramento`, `ronda = R-00`, claim = *«O dono declara que a plataforma <plataforma> foi decidida por <papel>»* (the words of `answers.md#ROTA`), evidência = `declaração do dono do processo, <date> — answers.md#ROTA`, `verificado_em` = today, `validade = organizacional`. It is a constraint that already exists, recorded as the owner declared it — not a solution chosen by a lens.
9d. **Publish the birth, then the profile check.** `python library/kernel/tools/resolve.py publish --engagement <slug> --draft <id>` (the draft of step 5c). One coordinator operation writes every file of steps 6–9c **and** the graph mirror of the `R-00` rows, with one receipt (`library/kernel/orchestration.md` → *Writing an authority*). The evidence anchors resolve against the draft itself: an `M-n` row citing `enquadramento.md#M-n`, or the `C-001` citing `answers.md#ROTA`, passes because the target is published in the same operation. A refusal prints a structured reason (`INTEGRITY_FAILURE` — e.g. a `Confirmed` row whose anchor is missing from the copy) and leaves the draft as it was: fix the copy and publish again; never write into the engagement folder instead. Then run `python library/kernel/tools/workflow.py check --engagement <slug>`: exit ≠ 0 → stop and report the reasons as they came; the engagement is not born until it passes.
10. Output (business language — `CLAUDE.md` → *Duas línguas*; kernel labels only between parentheses):
    ```user-output
    Projecto `<slug>` criado — tipo de solução em vista: <em palavras> (pack `<pack>`).
    Etapa: ouvir, ler e perguntar (Discovery).
    Como o negócio funciona, dito pelo dono: <n regras declaradas (M-1..M-n) | não declarado — cada pergunta terá de justificar-se sozinha>.
    Ficheiros para ler: <n em inputs/ | nenhum>.
    A seguir: primeira passagem das perspectivas pelo material → `/round` (ou uma perspectiva de cada vez: `/round business`).
    ```
11. **Process capture**: if `inputs/` contains any file → invoke the `aisa-capture` skill and report its summary. It owns the supported-format list (structured `.xlsx`/`.xlsm` → L1/L3/L2; capture-lite `.docx`/`.pdf`/`.vtt` → LT) and always writes `_capture/evidence-index.md`, the shared evidence surface for the engagement. Empty `inputs/` → skip silently.
