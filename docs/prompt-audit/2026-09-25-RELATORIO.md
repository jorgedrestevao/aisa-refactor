# Prompt audit — 2026-09-25

Estado: aplicado (commits `fb5ba85`, `d2dc2a4` em `claude/claim-credit-endpoint-e2oqht`).
Método: `/claude-api prompt-audit` (guia `shared/prompt-audit.md`): relatório + diff proposto, aprovado pelo mantenedor, aplicado.

## Resultado da aplicação

- **Aplicado:** todos os blocos H1–H5, M1–M21 e D1 (49 edições em 22 ficheiros).
  - **Excepção em M4:** `**solution-architect is NOT invoked in Framing.**` mantém o «NOT». `test_council_wiring.py` verifica a frase, e o ênfase tem o motivo ao lado (keep-list 5).
- **Extra, a pedido do mantenedor** (`d2dc2a4`): `aisa-frame` → Notes. «`/options` personas read the block» passou a «In Options the technical author reads the block (`aisa-options` step 4)».
- **Verificação:**
  - com `AISA_GUARD_MODE=enforce`: completa 3227/0 falhas, stdlib 2429/0 falhas;
  - greps finais do plano sem resultados.
- **`library/`:** só M10 (o guia do mapa), pelo override administrativo, reposto antes do commit.
- **Pendentes:** estão em «Fora deste plano», no fim, e são tratados um a um a seguir a este relatório.

---


## Contexto

O utilizador pediu `/claude-api prompt-audit`. O guia (`shared/prompt-audit.md`) procura instruções datadas, escritas para versões anteriores (do modelo ou do próprio aisa), que hoje degradam o comportamento. Não mede comprimento.

Entregáveis:
1. o relatório (abaixo);
2. o diff proposto (abaixo).

O diff abaixo foi aprovado e aplicado (ver *Resultado da aplicação*, acima).

### Pressupostos (Step 0)

- **Âmbito:**
  - Incluído: a superfície que chega ao modelo como instrução, ou seja, `CLAUDE.md`, `.claude/rules/*.md` (4), `.claude/skills/*/SKILL.md` (18, 3256 linhas), `.claude/agents/*.md` (6), `.claude/commands/*.md` (17).
  - Incluído por excepção: `library/kernel/capture-templates/process-map.guide.md`, porque a captura manda o autor segui-lo e foi alterado nesta sessão.
  - Fora: o resto de `library/kernel/*.md` (contratos de referência), `.claude/agent-memory/` (dados, não instruções) e os testes.
- **Modelo-alvo:** Claude Opus 5.5. O repo não fixa modelo nenhum (nenhum ID em skills, agentes ou settings) e não tem código da API Anthropic. É o modelo configurado desta sessão Claude Code, que é o runtime que executa as skills.
- **Proveniência (Step 2):** o clone foi aprofundado no M0. O `git blame` não foi corrido por linha. A datação é por idioma e por comparação com a regra actual do repo.
- **Cobertura:** sinais do guia por grep sobre toda a superfície, mais leitura dirigida dos trechos que os sinais apontaram. As 3 skills maiores (`chairman-synthesis` 453 l, `aisa-render` 406 l, `aisa-blueprint` 373 l) **não** foram lidas linha a linha (ver L5).

## Relatório

### Resumo

| Grupo | Achados (alta / média / baixa) |
|---|---|
| 1a Pressão | 0 / 0 / 1 (revisto e mantido) |
| 1c Coreografia | 0 / 0 / 1 |
| 1d Fósseis (frases relativas a versões anteriores) | 0 / 9 / 1 |
| 1f Tectos numéricos | 0 / 5 / 1 |
| 2 Skills frágeis (narrativas de histórico) | 0 / 6 / 1 |
| 3 Descrições (o contrato não bate com o comportamento) | 5 / 2 / 0 |
| 4 Configuração de pedido | nada: não há código de API |

(Alguns achados contam em dois grupos.)

**Maior impacto:**
1. **Descrições de 4 comandos contradizem as skills que invocam.** São texto de encaminhamento que aparece na lista de comandos de cada sessão:
   - `/round`: diz «all lenses in the mandatory order», mas é uma análise integrada sem ordem.
   - `/retro`: diz «the 7 personas», mas escrevem os papéis (analista, arquitecto, especialistas).
   - `/frame`: diz «council-independent», mas é um analista integrado mais um revisor independente.
   - `/options`: diz «3-5 options», mas a contagem depende da rota e não tem máximo.
2. **O agente `chairman` aplica as regras a «personas» que já não existem.** O mandato fala em *returns*; as regras de sobreposição, lacuna e contradição falam em *personas*. O modelo tem de adivinhar a correspondência.
3. **Frases sobre o que o aisa deixou de fazer.** «Personas no longer launched», «order guard retired», «migrated memories» descrevem uma versão anterior do aisa que o modelo nunca viu, e põem alternativas fantasma (o conselho de personas) no contexto de quem executa.

A pressão em maiúsculas está limpa: 7 linhas em toda a superfície, todas com o motivo ao lado ou com uma regra real de negócio ou autoridade.

### Achados — alta confiança

| # | Local | Evidência | Padrão | Porque está obsoleto | Acção |
|---|---|---|---|---|---|
| H1 | `.claude/commands/round.md:2-3` | `Run a Discovery round (all lenses in the mandatory order, or any single lens on its own).` · `argument-hint: "[lens\|--close]"` | G3: contrato ≠ comportamento | `aisa-round` e `CLAUDE.md` definem uma análise integrada das 6 perspectivas, com revisão independente e «no order to police». Uma descrição que não bate com o comportamento leva o modelo por caminhos que nenhum prompt corrige | rewrite |
| H2 | `.claude/commands/retro.md:2` | `the 7 personas write their diary entries ... make the council wiser` | G3 + 1d | `aisa-retro`: escrevem os papéis (analista, arquitecto, especialistas que reviram). As personas já não existem | rewrite |
| H3 | `.claude/commands/options.md:2` | `generate 3-5 options, each with its technology` | G3 | `handoff-contract.md` → *Options candidates*: a contagem depende da rota (`solution-choice` < 3 só com `reduction_reason`; `platform-constrained` admite 1; sem máximo). O autor técnico escreve, os especialistas revêem | rewrite |

### Achados — média confiança

| # | Local | Evidência | Padrão | Porque está obsoleto | Acção |
|---|---|---|---|---|---|
| M1 | `.claude/commands/frame.md:2` | `(council-independent synthesis of the single problem sentence)` | G3 + 1d | O modo é o analista integrado mais um revisor independente, com síntese do chairman (`aisa-frame` → Mode) | rewrite |
| M2 | `.claude/agents/chairman.md:17-19, 28-29, 38-39` | `when ≥2 personas independently support…` · `claims one persona made…` · `when personas disagree…` · `which persona inputs` · `a persona's evidence anchor` · `surfaced by personas` | 1d fóssil | O mandato do mesmo ficheiro (l.10-14) já diz *returns* (analista, revisor, candidatos, revisões). As regras ficaram com o vocabulário anterior e o modelo gasta esforço a conciliá-los | rewrite: *persona* → *return* |
| M3 | `.claude/agents/chairman.md:3` (description) | `(handoff-v1: Framing over …, since F3.4; Options over …, since F5.4 — no persona council runs)` | G2 narrativa de histórico | A autoridade da regra é o comportamento, não a fase em que entrou; «no persona council runs» é relativo a uma versão que o modelo não viu | rewrite |
| M4 | `.claude/skills/aisa-frame/SKILL.md:19` e `:127-128` | `The six council personas are no longer launched here, and there is no antithesis round (Q5).` · `Nor is any other persona: the council of six personas no longer runs here (Q4).` | 1d frase relativa | Descreve uma diferença face a uma versão anterior e nomeia alternativas fantasma; a linha *Mode* já diz o que corre | remove / rewrite (**inclui teste**) |
| M5 | `.claude/skills/aisa-round/SKILL.md:106` e `:108` | `**No order to police.** … The pre-lens-order-check hook and the round_lenses record are retired (handoff-v1 F3.3).` · `the retired business-analyst and operations-lead memories were migrated there with their prefix; the other perspectives' former persona memories live under the specialist role that now carries them` | 1d + G2 | Arqueologia de migração; a regra actual cabe numa frase | rewrite |
| M6 | `.claude/skills/aisa-options/SKILL.md:19` | `No persona council runs.` | 1d | Idem M4 | remove |
| M7 | `.claude/skills/aisa-answer/SKILL.md:54` | `What the engine does, and this skill therefore no longer does by hand:` | 1d | Frase relativa a uma versão anterior da skill | rewrite |
| M8 | `CLAUDE.md:51` | `The six Discovery personas are retired (handoff-v1 F5.4).` | 1d + G2 | Idem; carregado em todas as sessões | remove |
| M9 | `CLAUDE.md:91` | `Deslizes frequentes (observados na validação, step-9e):` | G2 narrativa de histórico | A lista de deslizes é contexto útil e fica; só o parêntese é arqueologia | rewrite |
| M10 | `library/kernel/capture-templates/process-map.guide.md` (secção «Fontes curtas», frase final do 1.º parágrafo) | `… — foi assim que uma exceção dita textualmente pelo dono ficou fora do mapa no piloto M5, apesar de o process-model a citar como «complexidade».` | G2 narrativa de histórico (recency trap) | Um incidente de um piloto codificado como texto permanente; já registado no M5.1 como factor que baralha a corrida 2. A regra (as bullets a seguir) chega sozinha | remove (**exige o override de library/**) |

### Achados da 2.ª passagem (sinais específicos pedidos)

**1. Narrativas de histórico**

| # | Local | Evidência | Padrão | Porque está obsoleto | Conf. | Acção |
|---|---|---|---|---|---|---|
| M11 | `.claude/skills/chairman-synthesis/SKILL.md:10` | `No persona council runs (retired in handoff-v1 F3.4 and F5.4).` | 1d + G2 | Diff face a uma versão que o modelo não viu; o parágrafo já diz o que lê | média | remove |
| M12 | `chairman-synthesis/SKILL.md:58` | `(The persona launch preamble that used to wrap it was retired with the persona council — handoff-v1 F5.4.)` | G2 narrativa | Arqueologia pura: não prescreve nada | média | remove |
| M13 | `.claude/skills/aisa-start/SKILL.md:83` | `desde a decisão de tornar o grafo obrigatório (P7.5 §2), ausência de grafo bloqueia` · `um Edit directo da SU já não é espelhado por hook (handoff-v1 F2)` | G2 + 1d | A regra vale por si; «desde a decisão» e «já não» são histórico | média | rewrite |
| M14 | `.claude/skills/aisa-blueprint/SKILL.md:296` e `:319` | `…; wired in F8.1)` | G2 narrativa | Diz quando entrou, não o que fazer | média | remove o fragmento |

**2. Referências a migrações.** A maioria é operativa e **fica**, porque são estados reais dos dados que o modelo tem de tratar:
- a versão histórica, só de leitura;
- `schema_flavour == "legacy"`;
- a impressão digital `legacy`;
- `migrate.py`;
- os engagements `pre-v2.3`: há fixture e código em `dashboard.py`, logo é uma classe de dados.

Achado novo:

| # | Local | Evidência | Padrão | Porque está obsoleto | Conf. | Acção |
|---|---|---|---|---|---|---|
| M15 | `.claude/skills/lens-technology/SKILL.md:43` | `3. In council mode, the structured proposal returned to the chairman — schema as the council invocation states (today .claude/agents/solution-architect.md; owned by chairman-synthesis, its only consumer).` | 1d fóssil + G3 contrato | O «council mode» já não existe. Em `aisa-options` passo 4 o autor técnico escreve os candidatos em `_design/candidates.json` por `review.py`, não os devolve ao chairman | média | rewrite |

**3. Limites numéricos**

| # | Local | Evidência | Padrão | Porque está obsoleto | Conf. | Acção |
|---|---|---|---|---|---|---|
| H4 | `lens-technology/SKILL.md:67` | `For each candidate (3–5; do-nothing and process change included…)` | G3: contrato ≠ comportamento | Mesma contagem velha de H3; a regra por rota está em `handoff-contract.md` | alta | rewrite |
| M16 | `.claude/agents/specialist-reviewer.md:54` | `at most 300 words` | 1f tecto numérico | Tectos de saída afinados contra modelos palavrosos; o objectivo real é uma resposta que só contesta o ponto mais forte | média | rewrite |
| M17 | `.claude/skills/aisa-retro/SKILL.md:24` | `Máx. 250 palavras.` | 1f | Idem: uma entrada de diário que o curador lê de uma vez | média | rewrite |
| M18 | 6 skills: `aisa-round:87`, `aisa-frame:266`, `aisa-options:188`, `aisa-decide:155`, `aisa-blueprint:222`, `aisa-render:306` (+ `aisa-start:157` «4-6 frases») | `4-8 frases na voz do sponsor, sem jargão de kernel, máx. 2 ids citados` | 1f (a mesma coreografia em 7 sítios) | O intervalo de frases é um tecto numérico; o que importa é o público (sponsor), a língua e os ids. **«máx. 2 ids» fica**: é uma regra de linguagem de negócio (P-13), não de comprimento | média | rewrite (um bloco por ficheiro) |
| M19 | `aisa-round:45` e `lens-technology:40` | `**What matters** (2–4 sentences)` | 1f | Idem | média | rewrite |
| M20 | `.claude/skills/aisa-simulate/SKILL.md:40` | `the projected future in 5-8 lines` | 1f | Idem | média | rewrite |

Os limites que **ficam** (e porquê):
- `~1 500 words / ≤120 per option` em chairman-synthesis e aisa-options: contrato verificado em teste (L3).
- «uma linha por X» nos registos e logs: forma do formato.
- `resumo em 3 linhas` no `/status`: 3 linhas com nome próprio, logo estrutura.
- `top-3`/`top-5`: cardinalidade do conteúdo.
- `3–6 causas` no premortem: cardinalidade.
- `truncado a 50 linhas` no render: regra de visualização do ensaio.
- `maximum 2` unidades de conhecimento no blueprint: orçamento de contexto, não saída.

**4. Coreografia de passos.** As skills com mais passos (`aisa-render` 43, `aisa-blueprint` 32, `aisa-status` 31, `aisa-capture` 28) são operações frágeis sobre estado coordenado: portões, `draft`/`publish` e recibos, onde só uma ordem é segura (keep-list 3). As de julgamento (`aisa-premortem`, `aisa-revisit`, `aisa-simulate`) numeram **artefactos a produzir**, não o método, e ficam. Um flag:

| # | Local | Nota |
|---|---|---|
| L6 | `lens-technology/SKILL.md` → *Execution steps* 1–5 | 1c: coreografia para uma tarefa de julgamento (verificar o portão → aplicar a perspectiva → sondar → contribuir → expor incerteza). O 5 é conselho de estratégia. Baixa: o conteúdo é curto e os «Five questions» são o critério de qualidade, que fica |

**Sem ocorrências:** hesitações (`try to`, `if possible`), alegações de tendência do modelo (`you tend to`), «be thorough», recaps «as stated above».

### Achados da 3.ª passagem (encaminhamento e contratos entre skills)

| # | Local | Evidência | Padrão | Porque está obsoleto | Conf. | Acção |
|---|---|---|---|---|---|---|
| H5 | `.claude/skills/aisa-capture/SKILL.md:3` (description, aparece na lista de skills de cada sessão) | `…evidence surface (entry point evidence-index.md) that lenses and council personas read.` | G3 + 1d | As personas não existem; quem lê a superfície de evidência é a análise integrada, o autor técnico e os revisores | alta | rewrite |
| M21 | `.claude/skills/aisa-decide/SKILL.md:194` | `The decision is the only point where the *user* (not the council) must say a sentence. Everything else has been council + chairman.` | 1d + contrato | O conselho já não existe, e a afirmação é falsa hoje: o dono responde no enquadramento (P-0), na validação do mapa e nas aprovações do frame e do desenho | média | rewrite |

**Contratos entre skills verificados e coerentes:** `aisa-round` escreve `lens-outputs/<perspective>.md`, e `aisa-synthesize` e `aisa-status` lêem esses mesmos ficheiros. Nada a mudar.

**Mais flags (sem diff):**
- L7: `chairman-synthesis:47` «When `_state.json` has the `workflow` block, Options runs no persona council.» é 1d. **Correcção:** `test_pp_discovery_runtime.py:192` só tem a frase num comentário, não a verifica. Tratado no ponto 3.
- L8: `.claude/rules/no-tech-mention-before-options.md` diz «Lenses in Discovery (`business`, …)» e «Lens `technology` enters…». Já não são lentes separadas, são perspectivas de uma análise; mas a regra continua certa e é carregada em todas as sessões, por isso fica. Baixa.

### Achados — baixa confiança / flag (sem diff)

| # | Local | Nota |
|---|---|---|
| L1 | ~30 citações `handoff-v1 Fx` / `decision Qn` / `P-18` / `step-3b` em skills e descrições de agentes | G2: narrativa de histórico. Servem também de ponteiro para os documentos de desenho que guardam o porquê. Remover só onde o documento não é preciso para agir. Fica para uma passagem dedicada |
| L2 | `.claude/skills/chairman-synthesis/SKILL.md:36, :54` + `<persona>` no esquema de retorno | Camada de tradução («read "persona" meaning…») sobre a nomenclatura antiga. Funciona e é consistente. Renomear mexe no esquema que outras skills escrevem → fica como está (keep-list 8) |
| L3 | `.claude/skills/chairman-synthesis/SKILL.md:295` «~1 500 words of prose, ≤120 words per option entry» | Coincide com 1f, mas é um contrato do artefacto verificado em código (`test_options_artefact.py` WORD_BUDGET), com motivo de leitura para o dono. Não é um remendo de verbosidade → mantido |
| L4 | Maiúsculas: `CLAUDE.md:121` (INVIOLÁVEL/SEMPRE AskUserQuestion), `aisa-revisit:47`, `aisa-decide:177`, `aisa-render:351`, `aisa-retro:39`, `rules/no-tech-mention-before-options.md:3` | Revistas: todas trazem o motivo ou uma regra real de autoridade ou política → mantidas (keep-list 5) |
| L5 | `chairman-synthesis` (453 l), `aisa-render` (406 l), `aisa-blueprint` (373 l) | G2: não se lêem de uma vez. Não foram auditadas linha a linha neste passe; limitação declarada |

**Não sinalizado:** as regras de preferência do utilizador repetidas em `CLAUDE.md` são redundância que funciona e não se contradiz (keep-list 8).

## Diff proposto (um achado por bloco)

```diff
# H1 — .claude/commands/round.md
-description: Run a Discovery round (all lenses in the mandatory order, or any single lens on its own).
-argument-hint: "[lens|--close]"
+description: Run a Discovery passagem — one integrated analysis of the six perspectives, reviewed by an independent coverage reader; `/round <perspective>` deepens one without closing; `--close` closes with the coverage recorded.
+argument-hint: "[perspectiva|--close]"
```

```diff
# H2 — .claude/commands/retro.md
-description: Close-of-engagement retro — the 7 personas write their diary entries (staged for human curation; approved entries feed agent-memory and make the council wiser each engagement).
+description: Close-of-engagement retro — each role that worked the engagement (analyst, architect, the specialists that reviewed) writes its diary entry, staged for human curation; approved entries feed agent-memory.
```

```diff
# H3 — .claude/commands/options.md
-description: Transition Framing → Options (generate 3-5 options, each with its technology, order of magnitude and risks; closes with the aisa's recommendation).
+description: Transition Framing → Options — the technical author writes the candidates by route (each with its technology, order of magnitude and risks), the specialists the risk calls for review them, and the synthesis closes with the aisa's recommendation.
```

```diff
# M1 — .claude/commands/frame.md
-description: Transition Discovery → Framing (council-independent synthesis of the single problem sentence).
+description: Transition Discovery → Framing — the integrated analyst proposes the single problem sentence, one independent reviewer contests it, the chairman synthesizes.
```

```diff
# M2 — .claude/agents/chairman.md (rules)
-  - **Overlap** — when ≥2 personas independently support the same claim, that is agreement, not evidence: … otherwise it is Assumed, with the personas' anchors as its basis.
-  - **Gap** — claims one persona made but no other anchored: …
-  - **Contradiction** — when personas disagree, … (`partes: <persona∧persona or lens∧lens>`, …)
+  - **Overlap** — when ≥2 returns independently support the same claim, that is agreement, not evidence: … otherwise it is Assumed, with the returns' anchors as its basis.
+  - **Gap** — claims one return made but no other anchored: …
+  - **Contradiction** — when returns disagree, … (`partes: <return∧return or lens∧lens>`, …)
 (l.28) `Lens column shows the persona origin` → `Lens column shows the return's lens`
 (l.29) `which persona inputs led to which SU rows` → `which returns led to which SU rows`
 (l.38) `point to a persona's evidence anchor; if only one persona claimed it` → `point to a return's evidence anchor; if only one return claimed it`
 (l.39) `A contradiction surfaced by personas` → `A contradiction surfaced by the returns`
```

```diff
# M3 — .claude/agents/chairman.md (description)
-description: The synthesizer of a phase (handoff-v1: Framing over the integrated analyst's proposal and one reviewer's findings, since F3.4; Options over the published candidates and the published specialist reviews, since F5.4 — no persona council runs). …
+description: The synthesizer of a phase — Framing over the integrated analyst's proposal and one reviewer's findings; Options over the published candidates and the published specialist reviews. …
```

```diff
# M4 — .claude/skills/aisa-frame/SKILL.md
- … (`library/kernel/orchestration.md` → *Framing mode*). The six council personas are no longer launched here, and there is no antithesis round (Q5).
+ … (`library/kernel/orchestration.md` → *Framing mode*). Nothing else runs in Framing: no other role, no antithesis round.
-**solution-architect is NOT invoked in Framing.** Nor is any other persona: the council of six personas
-no longer runs here (Q4). Framing is pre-technology — no vendor or product names anywhere in this skill.
+**solution-architect is not invoked in Framing.** Framing is pre-technology — no vendor or product names anywhere in this skill.
# + .claude/tests/test_frame_integrated.py:43
-        self.assertIn("The six council personas are no longer launched here", FRAME)
+        self.assertIn("Nothing else runs in Framing: no other role, no antithesis round.", FRAME)
```

```diff
# M5 — .claude/skills/aisa-round/SKILL.md
-- **No order to police.** The six perspectives are one analysis; the governance conflict scan runs last inside it (…). What closes a passagem is the coverage record, valid and current (`coverage.py round-state`), never a count of `lens-outputs` headers. The `pre-lens-order-check` hook and the `round_lenses` record are retired (handoff-v1 F3.3).
+- **One analysis.** The six perspectives are one analysis; the governance conflict scan runs last inside it (…). What closes a passagem is the coverage record, valid and current (`coverage.py round-state`), never a count of `lens-outputs` headers.
-- **Memory by role** (handoff-v1 F5.4, Q7/Q8): the integrated analysis reads the analyst's memory, `.claude/agent-memory/_universal/analyst/` — the retired `business-analyst` and `operations-lead` memories were migrated there with their prefix; the other perspectives' former persona memories live under the specialist role that now carries them (`library/kernel/specialists.md`). A pointer, never contents.
+- **Memory by role:** the integrated analysis reads the analyst's memory, `.claude/agent-memory/_universal/analyst/`; the other perspectives' memories live under the specialist role that carries them (`library/kernel/specialists.md`). A pointer, never contents.
```

```diff
# M6 — .claude/skills/aisa-options/SKILL.md:19
- … This is where vendor/product naming becomes allowed (via `lens-technology`). No persona council runs.
+ … This is where vendor/product naming becomes allowed (via `lens-technology`).
```

```diff
# M7 — .claude/skills/aisa-answer/SKILL.md:54
-   What the engine does, and this skill therefore no longer does by hand:
+   What the engine does (the skill does not repeat it by hand):
```

```diff
# M8 — CLAUDE.md:51
- … and the author/chairman mandates (`solution-architect`, `chairman`). The six Discovery personas are retired (handoff-v1 F5.4).
+ … and the author/chairman mandates (`solution-architect`, `chairman`).
```

```diff
# M9 — CLAUDE.md:91
-- Deslizes frequentes (observados na validação, step-9e): «blueprint v06» → …
+- Deslizes frequentes: «blueprint v06» → …
```

```diff
# M10 — library/kernel/capture-templates/process-map.guide.md (Fontes curtas)
-todas as frases de uma nota, uma citação ou um e-mail do dono — foi assim que uma exceção
-dita textualmente pelo dono ficou fora do mapa no piloto M5, apesar de o process-model a
-citar como «complexidade».
+todas as frases de uma nota, uma citação ou um e-mail do dono.
```

### Diff da 2.ª passagem

```diff
# H4 — .claude/skills/lens-technology/SKILL.md:67
- For each candidate (3–5; do-nothing and process change included where discovery showed them plausible, their absence declared with ids where not): …
+ For each candidate (as many as the route admits — `library/kernel/handoff-contract.md` → *Options candidates*; do-nothing and process change included where discovery showed them plausible, their absence declared with ids where not): …
```

```diff
# M11 — .claude/skills/chairman-synthesis/SKILL.md:10
- … each published specialist review (*Options inputs in a handoff-v1 engagement*). No persona council runs (retired in handoff-v1 F3.4 and F5.4). You produce:
+ … each published specialist review (*Options inputs in a handoff-v1 engagement*). You produce:
```

```diff
# M12 — chairman-synthesis/SKILL.md:58
- … (`<persona>` = `analista integrado`, `<phase>` = `Framing`). No agent file carries it. (The persona launch preamble that used to wrap it was retired with the persona council — handoff-v1 F5.4.)
+ … (`<persona>` = `analista integrado`, `<phase>` = `Framing`). No agent file carries it.
```

```diff
# M13 — .claude/skills/aisa-start/SKILL.md:83
- **Não é opcional**, e a ordem também não: desde a decisão de tornar o grafo obrigatório (P7.5 §2), ausência de grafo bloqueia.
+ **Não é opcional**, e a ordem também não: ausência de grafo bloqueia.
- … com um recibo; um Edit directo da SU já não é espelhado por hook (handoff-v1 F2).
+ … com um recibo; um Edit directo da SU não é espelhado por hook.
```

```diff
# M14 — .claude/skills/aisa-blueprint/SKILL.md:296 e :319
- (… `docs/handoff-v1/F6/DESENHO.md` §0 and Q3; wired in F8.1)
+ (… `docs/handoff-v1/F6/DESENHO.md` §0 and Q3)
- (handoff-v1 F6; … *Traceability*; wired in F8.1)
+ (handoff-v1 F6; … *Traceability*)
```

```diff
# M15 — .claude/skills/lens-technology/SKILL.md:43
-3. In council mode, the structured proposal returned to the chairman — schema as the council invocation states (today `.claude/agents/solution-architect.md`; owned by `chairman-synthesis`, its only consumer).
+3. In `aisa-options` step 4, the candidates themselves — written by the technical author (`.claude/agents/solution-architect.md`) into `_design/candidates.json` through `review.py`, never returned to the chairman as a proposal.
```

```diff
# M16 — .claude/agents/specialist-reviewer.md:54
- Return the sections `Concedo / Contesto / Síntese proposta`, at most 300 words.
+ Return the sections `Concedo / Contesto / Síntese proposta`, each only as long as the point it settles.
```

```diff
# M17 — .claude/skills/aisa-retro/SKILL.md:24
-   Formato: ## <slug-anonimizado> — <data>. Máx. 250 palavras.
+   Formato: ## <slug-anonimizado> — <data>. Curto: uma entrada que o curador lê de uma vez.
```

```diff
# M18 — (padrão, um bloco por ficheiro) aisa-round:87, aisa-frame:266, aisa-options:188, aisa-decide:155, aisa-blueprint:222, aisa-render:306
- …: 4-8 frases na voz do sponsor, sem jargão de kernel, máx. 2 ids citados.
+ …: um parágrafo curto na voz do sponsor, sem jargão de kernel, máx. 2 ids citados.
# aisa-start:157
- **Episódio 1** (o pedido: quem pediu, o quê, porquê — 4-6 frases na voz do sponsor)
+ **Episódio 1** (o pedido: quem pediu, o quê, porquê — um parágrafo curto na voz do sponsor)
```

```diff
# M19 — aisa-round:45 e lens-technology:40
- **What matters** (2–4 sentences)
+ **What matters** (a short paragraph)
```

```diff
# M20 — .claude/skills/aisa-simulate/SKILL.md:40
-   - One-pager per option: the projected future in 5-8 lines, every claim citing SU/option/tree ids.
+   - One-pager per option: the projected future, short enough to compare side by side, every claim citing SU/option/tree ids.
```

```diff
# H5 — .claude/skills/aisa-capture/SKILL.md:3 (description)
- … Produces the _capture/ shared evidence surface (entry point evidence-index.md) that lenses and council personas read.
+ … Produces the _capture/ shared evidence surface (entry point evidence-index.md) that the Discovery analysis, the technical author and the reviewers read.
```

```diff
# M21 — .claude/skills/aisa-decide/SKILL.md:194
-- The decision is the only point where the *user* (not the council) must say a sentence. Everything else has been council + chairman.
+- The decision is the user's. Before it, the analysis proposes, the reviewers contest and the chairman synthesizes; none of them chooses.
```

**Nota sobre M16–M20.** São achados de padrão documentado (1f), mas o efeito é de tom e comprimento. Validar com um engagement de fixture (`/round` e `/retro` num rascunho) antes e depois; se o texto crescer sem ganho, repor em forma mínima (Step 7: «re-add simply»). Rejeitar estes blocos um a um é legítimo.

### Decisão do mantenedor tomada durante o audit: tirar a pergunta do método (D1)

**Porque existia.** Decisão Q5 do F1 (`docs/handoff-v1/F1/DESENHO-CONTRATOS.md`): enquanto o perfil `handoff-v1` fosse experimental, o `/start` perguntava sempre, e o «Não» mandava para `jorgedrestevao/aisa@85baf10` sem criar nada. A decisão «classic A» mantém-se: não há motor antigo e um engagement sem perfil é legado, só de leitura.

**Decisão (25-09-2026):** tirar já a pergunta. O `/start` cria sempre `handoff-v1` e avisa numa linha que é experimental. A pergunta da rota fica.

```diff
# D1 — .claude/skills/aisa-start/SKILL.md:22-23 (passo 3b)
-3b. **Workflow profile and route** (handoff-v1 — `docs/handoff-v1/F1/DESENHO-CONTRATOS.md` §2.1). This version has no classic runtime: every engagement it creates is `handoff-v1`, still experimental. Asked **before anything is created**, each by `AskUserQuestion`:
-   - **Profile** — *«Este trabalho segue o método novo, ainda experimental?»* — options *Sim, método novo (experimental)* (description: perfil `handoff-v1`) · *Não, usar a versão anterior* (description: continua em `jorgedrestevao/aisa@85baf10`; nada é criado aqui). *Não* → stop with that instruction; nothing is written.
+3b. **Workflow profile and route** (`docs/handoff-v1/F1/DESENHO-CONTRATOS.md` §2.1). Every engagement this version creates is `handoff-v1`; there is no other profile to choose. Say it once, in business language, before the route question: *«Este engagement usa o método novo do aisa, ainda em validação.»* The route is asked **before anything is created**, by `AskUserQuestion`:
    - **Route** — *«A plataforma da solução já foi decidida …»* (inalterado)
```

- **O que fica igual:** `workflow.py check --pack <pack> --profile handoff-v1 --route <route>`; o bloco `workflow` em `_state.json`; o registo `## ROTA` em `answers.md` (só leva a rota).
- **Dependências verificadas:**
  - nenhum teste verifica o texto da pergunta;
  - `aisa-orient` não recolhe o perfil (o «3b» dele é outro passo, sobre ficheiros nomeados);
  - `docs/COMO-USAR.md` não a menciona.
- **Registo:** uma linha no relatório do audit e na mensagem do commit a dizer que a Q5 do F1 foi revista pelo mantenedor. O `DESENHO-CONTRATOS.md` é histórico e não se edita.
- **Linguagem (P-13):** a linha nova está em linguagem de negócio. «handoff-v1» fica só no texto para o executor, não na frase ao utilizador.

## Execução (se aprovado)

1. **Aplicar os blocos H1–H5, M1–M21 (excepto M10) e D1.** Tocam em `.claude/` e `CLAUDE.md` e não precisam de override. Os `…` do diff são o texto actual, que fica intacto. Nenhum dos textos da 2.ª passagem é verificado por testes ou hooks (grep feito).
2. **M10 é em `library/`.** Precisa do override administrativo (adenda v3.1 decisão 1): activado só localmente, reposto antes do commit.
3. **Testes que tocam o texto mudado:**
   - `test_frame_integrated.py:43`: reescrito no bloco M4.
   - Os restantes (`test_round_in_progress`, `test_council_wiring`, `test_options_by_route`, `test_lens_checklists`, `test_step8c_…`) só verificam **ausências** ou citam o texto em comentários. Não mudam.
4. **Verificação:**
   - `AISA_GUARD_MODE=enforce python .github/run_tests.py` e `--list .github/stdlib-tests.txt`.
   - `test_user_language.py` (lê os blocos de output das skills) verde depois do D1.
   - Grep final sem resultados: `método novo, ainda experimental\?|usar a versão anterior` em `.claude/skills/aisa-start/`; `council personas read|not the council|council \+ chairman` em `.claude/skills/`; `persona` em `.claude/agents/chairman.md`; `mandatory order|7 personas|3-5 options|council-independent` em `.claude/commands/`; `3–5;|council mode|wired in F8|used to wrap|retired in handoff|4-8 frases|4-6 frases|2–4 sentences|5-8 lines|at most 300|Máx. 250` em `.claude/`.
5. **Validar o comportamento (Step 7).** As mudanças são de texto de encaminhamento e de vocabulário, sem efeito esperado nos resultados. Validação mínima: correr `/status` num engagement de fixture e confirmar que a lista de comandos mostra as descrições novas. Não há suite de avaliação comportamental das skills.
6. **Commit e push** para `claude/claim-credit-endpoint-e2oqht`. `settings.json` fica fora do commit.

## Fora deste plano (pendentes, por esta ordem)

1. ~~Guardar este relatório no repo~~ — este ficheiro.
2. ~~L1 — citações de fase~~ — feito (ver *Ponto 2*, abaixo).
3. ~~L2/L7 — «persona» no `chairman-synthesis`~~ — feito (ver *Ponto 3*, abaixo).
4. L5 — auditoria linha a linha de `chairman-synthesis`, `aisa-render`, `aisa-blueprint`.
5. Validação comportamental de M16–M20 (`/round`, `/retro` num engagement de fixture).
6. Verificação A do mapa (cálculo absorvido), à espera da v01 e da calc-chain da corrida 1.

## Ponto 2 — citações de fase (L1)

- **Removidas: 30 etiquetas que só datam, em 14 ficheiros.** Eram `(handoff-v1 Fx)`, `(handoff-v1 Fx, Qn)`, `(F5.3)`, `(Q5)`, `(F0 D02: …)`, em skills, agentes e `CLAUDE.md`. Onde havia um ponteiro útil ao lado (um ficheiro de `library/kernel/…`, uma ferramenta, «read-only»), o ponteiro fica.
- **Mais um fóssil apanhado:** `aisa-options:199` «The six Discovery personas are retired (handoff-v1 F5.4, Q4); their perspectives live in…» passou a «The Discovery perspectives live in…».
- **Mantidas:**
  - referências a secções de documentos de desenho (`docs/handoff-v1/F3/DESENHO.md` Q1–Q3, `§0 and Q3`, `§0, Q1`): apontam para o porquê;
  - `handoff-v1` como valor do perfil e no nome de secção *Options inputs in a handoff-v1 engagement*, que é âncora citada;
  - os ids `P-`/`T-` (`P-0`, `P-1`, `P-21`, `T19`, `T43`…): quase todos são itens com nome no kernel ou tokens literais que se escrevem nos dados, e mexer-lhes partiria formatos.
- **Fora do âmbito:** `library/kernel/orchestration.md` e o pack mantêm `(handoff-v1 F3/F5)` nos títulos, que os testes verificam.
- **Verificação** (`enforce`): completa 3227/0, stdlib 2429/0.

## Ponto 3 — «persona» no `chairman-synthesis` (L2/L7)

- **Definição única em *Role*:** um *return* é o que um autor entregou (em Framing a proposta do analista ou os achados do revisor; em Options os candidatos do autor técnico ou uma revisão de especialista). Saíram as duas linhas de tradução («Read every step below with "persona" meaning…»).
- **Vocabulário:**
  - `persona(s)` → `return(s)` quando é o que foi entregue;
  - `<persona>` → `<author>` quando é quem o escreveu: no cabeçalho do esquema de retorno, em `partes = <author∧author>`, na coluna *Source author(s)* de `frame.md`, em `## Returns heard` e em *Anchored by*.
  - O plano previa *Source return(s)*. Ficou *Source author(s)*, porque a coluna leva nomes de autores (`analista`, `revisor`).
- **Frases que já não se aplicam, retiradas:**
  - «In Framing there is no council.»;
  - «When `_state.json` has the `workflow` block, Options runs no persona council.»;
  - «Personas in Options reason against the block», que passou a «In Options the technical author reads the block».
- **`chairman.md` alinhado:** `partes: <return∧return …>` passou a `<author∧author …>`, igual à skill.
- **Nenhum parser** lê estas estruturas (procurei em hooks, tools, templates e testes). `aisa-frame` escreve o cabeçalho como `## analista integrado — Round …`, sem mudança.
- **Pendente novo, fora deste ponto:** `library/kernel/tools/workflow.py:349` diz «concordância entre personas não é evidência». É uma mensagem do motor, verificada por `test_handoff_evidence.py:123`, e mudá-la exige o override de `library/` e o teste.
- **Verificação** (`enforce`): completa 3227/0, stdlib 2429/0; `grep -i persona` na skill não devolve nada.
