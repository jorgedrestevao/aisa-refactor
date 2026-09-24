# Relatório de fase — F0

Estado: **completed** — gate cumprido e decisões do mantenedor registadas em §13 (2026-09-23).

- Data e responsável: 2026-09-23 · Claude Code, sessão `session_0156MuyJemPPrVqRKiDrAsct`, por autorização do mantenedor.
- Repositório, branch e SHA: `jorgedrestevao/aisa-refactor`, branch `claude/clone-repo-awui-7mmi37`. Início de F0 (v1.2): `262fa70`, árvore igual à baseline. Último commit: ver `git log` da branch (este relatório entra no commit de fecho).
- Plano e fase: handoff-v1 **v1.2** ([plan/](../plan/README.md); zip sha256 `70aa0f4a…`), fase F0.
- Perfil/schema/pack afectados: **nenhum**. F0 não altera runtime, contratos, hooks, skills, agentes nem pack.

## 1. Resultado

Passou a ser possível:
- Retomar o programa só a partir do repositório: [README](../README.md) → plano → este relatório.
- Saber quem cria, escreve, lê, valida, guarda, alimenta ou concorre com cada uma das 7 autoridades, com evidência `ficheiro:linha` ([consumer-matrix.json](consumer-matrix.json), 503 linhas). O T02 falha se aparecer um consumidor novo sem inventário.
- Consultar a disposição proposta de 164 componentes legados e dos 75 ficheiros de teste da baseline ([disposition-matrix.json](disposition-matrix.json)).
- Repetir a baseline de testes nos dois ambientes e compará-la com o CI ([test-baseline.json](test-baseline.json)).
- Saber que cobertura existente serve cada um dos 46 cenários ([scenario-coverage.json](scenario-coverage.json)).
- Reutilizar mecanismos de validação e métricas base ([mechanisms-metrics.json](mechanisms-metrics.json)).
- Usar 5 fixtures sintéticas dos cenários obrigatórios ([fixture-registry.json](fixture-registry.json)).

Fora do âmbito: qualquer mudança de comportamento; aplicar disposições; fechar contratos de F1; migrar engagements; pilotos.

Método: varrimento determinístico por padrão, inventário por agentes de leitura (uma autoridade ou grupo por agente), críticos adversariais de completude, revisão adversarial das disposições e adjudicação manual. Os agentes só leram; todas as escritas no repositório são deste relatório e dos artefactos listados em §3.

## 2. Delta ao plano

| ID | Plano assume | Estado real | Tratamento |
| --- | --- | --- | --- |
| P1 | `jorgedrestevao/aisa`, branch `master`, SHA `85baf10` | Trabalho em `jorgedrestevao/aisa-refactor` (`main`). A árvore é idêntica byte a byte a `85baf10` (`diff -rq` contra um clone externo), mas o histórico não é partilhado: `85baf10` não existe neste object store. | A referência histórica para comparação ou leitura legada vive em `jorgedrestevao/aisa@85baf10`, não neste repo. Tag histórica neste repo: decisão D-F1-15. |
| P2 | Instruções em `AGENTS.md` | Não existe `AGENTS.md`. Aplicam-se `CLAUDE.md` e `.claude/rules/*.md`. | Registado. |
| P3 | — | Os hooks do projecto (`.claude/settings.json`) correm também na sessão que implementa. Em F0, P15 e a guarda de runtime apanharam referências partidas criadas pelo próprio F0. | Qualquer mudança de hooks em F1 muda a sessão que a faz. Testar antes de activar. |
| P4 | Nomes de ficheiros e grupos do plano | A1–A12 são secções de `architecture-templates/architecture-core.md` e dos fragments. "research" é uma classe (11 subpastas de `domain-knowledge/`); craft é `domain-knowledge/craft/`. `estimation-model.md` está em `domain-knowledge/craft/`. Os modos A/B estão em `estimate.template.md:73-129`. `lens-*` são 7 skills. `chairman` é skill + agente. `blueprint` são 3 coisas (artefacto, entregável, comando). `/resume` é comando sem skill; `aisa-orient` é skill sem comando. | 62 resoluções em `consumer-matrix.json` e no resultado de caminhos. Não renomear. |
| P5 | `operation.py` é o mecanismo de publicação | Só `resolve.py` e `migrate.py` publicam pelo coordenador. Lentes, chairman, decide, frame, options, status, start e blueprint escrevem com Edit/Write. `coverage.py finalize` publica por reserva `O_EXCL`. Os extractores e `fields_draft` escrevem com os seus próprios `os.replace`. | F2 (D-F1-07, D-F1-08). |
| P6 | Coverage por lente (`assessed`/`gap`/`not_applicable`) | Não existe. `coverage-contract` cobre requisito→artefacto em 3 etapas. | D-F1-10. |
| P7 | — | Não existem perfil, rota, schema de workflow, FC/J/WP, `_work/` ou `_design/`. Só o grafo e o coverage têm `schema_version`. | D-F1-04, D-F1-11. |
| P8 | Snapshot do bootstrap | Snapshot de 6 autoridades (`bootstrap.py:76-77`). Blueprint, spec, estimate, frame, options, pack e `_capture` estão fora do read-set. `operation.run` não aceita inputs só de leitura como pré-condição (`operation.py:501-508`). | F2. |
| P9 | IDs T01–T46 | Testes antigos usam IDs "T34/T35", "T39/T41" e "T-D1..T-D22" de outros planos. | Não mapear por nome. |
| P10 | Vocabulário "rota"/"router" | Testes do pack proíbem a chave `routes:` e "router" no manifest e no orquestrador (`test_pp_pack_integrity.py:125-139`, `test_pp_deliverable_templates.py:1332-1344`). | D-F1-05. |
| P12 | "Legado" = engagement sem perfil persistido (07:5) | No código, `LEGACY_MODE` significa "sem `_graph/`" (`bootstrap.py:306-314`). Nenhum código detecta hoje o legado do plano; todos os engagements existentes são "sem perfil". | D-F1-04: não reutilizar `LEGACY_MODE`. |
| P11 | Pilotos anteriores | O plano v1.2 retira a dependência. `test_p8_*` e `compare.py` são mecanismo reutilizável em F8, não pendência (disposição: adaptar/isolar). | Registado. |

## 3. Alterações

| Ficheiro/componente | Mudança | Requisito | Compatibilidade |
| --- | --- | --- | --- |
| `docs/handoff-v1/plan/**` | Cópia validada do pacote v1.2 | Retoma pelo repo | Só documentação |
| `docs/handoff-v1/README.md` | Ponto de entrada do programa | Retoma pelo repo | Só documentação |
| `docs/handoff-v1/F0/*.json`, `RELATORIO.md` | Matrizes, baseline, registry, mapas | Entregáveis F0 | Só documentação |
| `.claude/tests/fixtures/handoff-v1/**` | 5 fixtures sintéticas (source packs + resultados esperados) | F0 item 4 | Dados de teste; nenhum teste antigo os lê |
| `.claude/tests/test_handoff_f0.py` | T02 (11 casos, 4 negativos) + integridade das fixtures (6 casos) | T02 | Teste novo; suite 75→76 ficheiros |

Nenhum ficheiro de `library/`, `.claude/{skills,hooks,commands,agents,rules}`, `CLAUDE.md`, `.claude/settings.json` ou `.github/` foi alterado.

## 4. Matriz de consumidores (resumo)

| Autoridade | Linhas | Escritores (creator/writer/appender/mirror) | Notas |
| --- | --- | --- | --- |
| SU (+answers, espelho `_graph/`) | 97 | 35 | Só `resolve`/`migrate` usam o coordenador; os restantes escrevem com Edit e o espelho é feito depois por hook |
| Decisões | 86 | 16 | `aisa-start` não consegue criar o ficheiro na ordem prescrita (D01) |
| Blueprint + arquitectura | 76 | 7 | A aprovação liga-se ao nome da versão, não ao conteúdo (D11) |
| Coverage | 53 | 10 | `finalize` é um segundo mecanismo de publicação (D07) |
| Implementation-spec | 55 | 4 (+6 `feeds`) | Só `aisa-render` produz o spec |
| Estimate | 61 | 9 (+8 `competes`) | 8 fontes de esforço concorrentes fora do Estimate (D12) |
| `_state.json` + `_ops/` + `_migration/` | 75 | 18 | `_migration/` não está guardado (D05) |

Papéis adicionados na adjudicação: `feeds` (escreve uma autoridade a montante) e `competes` (produz conteúdo do mesmo tipo fora da autoridade).

## 5. Disposição de componentes e testes (resumo)

Componentes (164), depois da revisão adversarial: adaptar 82 · manter 30 · consolidar 22 · isolar 9 · eliminar 10 · indeciso 11. Testes da baseline (75 ficheiros, 2621 casos): manter 52 · adaptar 20 · consolidar 2 · indeciso 1. Tudo é **proposta**: cada disposição é aplicada pela fase responsável, com cobertura e justificação no mesmo incremento.

Pontos principais:
- **Motores**: `operation`, `bootstrap`, `graph`, `resolve`, `coverage` e `projection` são reutilizados e estendidos. Nenhum motor novo concorre com eles; o `workflow.py` proposto chama-os.
- **Agentes de lente**: consolidar em checklists do analista integrado (F3) ou em mandatos de especialista (F5). Só o classic os invoca (`aisa-frame:149`, `aisa-options:134`, `aisa-retro:14`). `solution-architect` fica como autor técnico; a regra de evidência do chairman é corrigida.
- **Hooks**: `pre-write-guard` mantém-se. `blueprint-validate` é consolidado nos passos 13/13b do `aisa-blueprint`. `pre-lens-order-check` é eliminado em F3, condicionado à decisão classic A (o substituto é a coverage das seis perspectivas). `phase-completeness` é eliminado no perfil novo, porque a readiness tem um só avaliador. `on-su-mirror` e `su-confirmed-guard` são adaptados nos dois perfis (D19). Os restantes passam a dispatch por perfil, com um resolver único em `_common.py`.
- **Eliminar (proposta)**: escrita do cabeçalho de saúde da SU no `/status`; contador `capture_run`; `/retro` e `aisa-retro` (depende de D-F1-16); `.claude/output-styles/` vazio; scripts de aceitação de planos anteriores.
- **Testes**: os que exigem seis execuções ou ordem fixa passam a coverage de seis perspectivas (F1/F3). Os de integridade, crash, concorrência e evidência mantêm-se. Os dos extractores mantêm-se (congelados). `test_p8_*` são adaptados como mecanismo de F8.
- **Indeciso** (precisa do mantenedor): decisão classic; `migrate.py` legado→grafo; diários, `/retro` e memória de tenant; `aisa-render --html`; portador durável do "não autorizado" entre `/decide` e `/synthesize`; `resolve.finding`; fixtures step8c derivadas de piloto real.

Revisão adversarial das disposições: 13 contestações, todas aceites e registadas em `review_adjudication` na matriz. Mudam a decisão em `pre-lens-order-check` (isolar→eliminar, condicionado), `phase-completeness` (adaptar→eliminar no perfil novo), `blueprint-validate` (manter→consolidar) e `on-su-mirror` (adaptar nos dois perfis). O revisor não chegou a ver as linhas de motores depois de `dashboard.py: modelo de estado e gates`, porque o input foi truncado; essas linhas ficam sem segunda leitura.

## 6. Cenários T01–T46 (resumo)

2 com cobertura total (T13, T14: coordenador reutilizado sem mudança), 32 parcial e 12 sem cobertura (T04, T05, T06, T15, T18, T21, T25, T28, T30, T40, T43, T45). A cobertura reutilizável mais forte está em F2 (T11–T14, T16, T17). T19, T43, T44 e T46 exigem juízo humano; T45 exige uma sandbox real. Detalhe e fase de fecho: [scenario-coverage.json](scenario-coverage.json).

## 7. Defeitos actuais relevantes para este programa

Classificados só pela relevância actual (plano 09, *Gates e dívida antiga*). F0 não corrige nenhum; cada um tem fase proposta.

| ID | Defeito | Evidência | Critério afectado | Fase |
| --- | --- | --- | --- | --- |
| D01 | `/start` na ordem prescrita falha em `AISA_GUARD_MODE=enforce` (default). Depois de `_state.json` (passo 7), o guarda nega o Write da SU e das decisões (passos 8–9), porque o grafo só nasce no passo 9c. O `migrate.py init` recusa com `NOT_EMPTY` depois das linhas M-n do passo 9b. | Reproduzido: `pre-authority-guard.py:138-140` → exit 2 com `_state.json` sem grafo; `aisa-start/SKILL.md:82-136` | Nascimento de todo o engagement; T03 | F1 (ordem de nascimento) |
| D02 | `/status`, `/resume` e `aisa-orient` escrevem na SU (passo 3 do `aisa-status`), apesar de o `aisa-orient` declarar que nunca escreve | `aisa-status/SKILL.md:27,53`; `resume.md:6`; `aisa-orient/SKILL.md:3,49,73` | T09 (retoma como leitura) | F2 |
| D03 | Concordância de personas promove a Confirmed | `chairman.md:17`; `chairman-synthesis/SKILL.md:115,148` vs `states.md:21-37` | T08 | F1 (regra) / F5 |
| D04 | `/options` lança o arquitecto e os revisores em paralelo; os revisores não vêem os candidatos | `aisa-options/SKILL.md:130-160,227` | T25, T26 | F5 |
| D05 | `CLAUDE.md:41,96` diz que o guarda recusa Write/Edit em `_graph/`, `_ops/` e `_migration/`. Na verdade `_migration/` nunca é guardado, e `_graph/`/`_ops/` só são negados quando o bootstrap **não** está pronto: com o engagement pronto, a edição à mão passa | `pre-authority-guard.py:69,137-156` (revisão adversarial, sonda em cópia sintética) | T12, T17 | F1/F2 |
| D06 | `render-validate` acrescenta blocos a cada execução; `gap_count` infla (3→6→9) | resultado dos hooks; `render-validate.py:502-517` | Verdade da readiness (F6), T33 | F6 |
| D07 | `coverage finalize` não é idempotente (mesmo rascunho → v01 e depois v02), e `next_version` reutiliza o número livre mais baixo | `test_coverage_integration.py:403-407`; `coverage.py:3606-3612` | T13, T12 | F2 |
| D08 | `operation.run` só compara digests do write set; um input só de leitura não pode ser pré-condição | `operation.py:501-508` | T10, T11 | F2 |
| D09 | `aisa-decide` 4b escreve uma linha de 5 células numa tabela Confirmed de 7 colunas | `aisa-decide/SKILL.md:131-135` vs esqueleto em `aisa-start` | Integridade da SU | F2 |
| D10 | `migrate restore --force` apaga D-NNN acrescentados depois da migração | `migrate.py:400,427-429` | Append-only das decisões; T35 | F7 |
| D11 | A aprovação do blueprint liga-se ao nome da versão; a do frame usa sha256 | `status_model`/`frame_identity`; `blueprint-contract.md` | T24 | F4 |
| D12 | 8 fontes de esforço fora do Estimate (options, simulate, revisit, decide, cfo-lens, solution-architect, chairman) | `consumer-matrix.json` → estimate `competes` | T32; um único dono do esforço | F5/F6 |
| D13 | 5 métodos de `test_options_artefact.TestRenderedArtefacts` passam vazios sem engagements | `test_options_artefact.py:469-478,530-592` | Regra 06 "not-run ≠ pass" | F1 |
| D14 | Contradições normativas: `orchestration.md:90` (sem grafo de dependências) vs `resolve.impact_of`; `orchestration.md:92` (sem artefacto de retoma) vs checkpoint; `orchestration.md:112,125` (sinais ≠ checklist) vs checklists; `phases.md:99` (3–4 lentes) vs `aisa-frame` (6); `states.md:58` (6 edições sancionadas) vs `aisa-answer` ("só duas") | ficheiros citados | F1 normativa | F1 |
| D15 | Vocabulário `routes`/`router` proibido por testes do pack | P10 | Rotas do plano | F1 |
| D16 | CI vermelho desde a baseline: o workflow não instala nada, mas a suite precisa de PyYAML, openpyxl, python-docx e pypdf; `requirements-dev.txt` omite os dois últimos | `test-baseline.json` (BL-DOC-1); runs 35851556146, 35855064560 | Gate de release (suite aplicável verde) | D-F1-01 |
| D17 | `projection.operational_state` lê `build_model` fora da janela de `consistent_read` | `projection.py:137,179` | T12 ("nunca mistura") | F2 |
| D19 | Uma edição in-place que muda o estado de uma linha existente da SU (ex.: Unknown→Confirmed) é espelhada em silêncio pelo `on-su-mirror`/`sync_mirror`. O `su-confirmed-guard` só selecciona ids `C-`, por isso a promoção passa sem sinal | revisão adversarial (sonda em cópia de `fx-coverage-f06`); `su-confirmed-guard.py:129`; `resolve.py:688-803` | T08, T17 | F2 |
| H1 | Fixture versionada com caminho local absoluto, nome de utilizador e nome de cliente | `fx-coverage-f06/_capture/*.extraction.json:12` | Higiene de dados | F1 (limpeza só de teste) |
| H2 | Slugs de engagements reais citados em ficheiros normativos (ex.: `aisa-start/SKILL.md:132`) | `consumer-matrix.json`, classic | Higiene | F1/F9 |

A verificar (dependem do comportamento do harness, não do repo): se `Write\|Edit` abrange MultiEdit/NotebookEdit; se os hooks disparam em ferramentas chamadas dentro de subagentes; se hooks PostToolUse do mesmo grupo correm em paralelo.

## 8. Decisões e evidência

Decisões internas de F0 (reversíveis, alternativa mais simples compatível):

| Decisão | Alternativa rejeitada | Revisitar se |
| --- | --- | --- |
| Artefactos F0 em JSON com vista-resumo neste relatório; o JSON é a autoridade | Matriz em Markdown duplicada | A leitura humana exigir uma vista gerada |
| T02 varre a árvore de trabalho com o padrão declarado por autoridade e exige `via` para consumidores sem referência textual | Lista estática sem varrimento | Surgirem falsos positivos por padrão largo |
| Fixtures como source packs (fontes + resultados esperados), sem estado de engagement pré-construído | Engagements materializados agora | F2/F4 fixarem formatos (baseline materializada da change-impact: recomendação R1) |
| Papéis `feeds` e `competes` na matriz | Forçar "writer" | — |
| Cópia do plano no repo | Plano só em anexo | — |

Decisões que F0 **não** toma, e que são do mantenedor ou de F1: ver §11.

## 9. Testes

| ID | Comando/procedimento | Revisão/fixture | Resultado observado | pass/fail/not-run | Evidência |
| --- | --- | --- | --- | --- | --- |
| T01 | Por ficheiro (`python <f> -v`) em devdeps e stdlib; `python .github/run_tests.py`; CI | baseline + F0 | devdeps 75/75, 2621 casos, 34 skips, 3 xfail; stdlib 56/75; CI 56/75 (vermelho pré-existente, mesma assinatura antes e depois de F0) | **pass** (baseline reproduzível; falhas classificadas) | `test-baseline.json` |
| T02 | `python .claude/tests/test_handoff_f0.py` (classes T02_*) | `consumer-matrix.json` | 11/11 OK; os casos negativos detectam um skill e um hook novos não inventariados | **pass** | teste versionado |
| — | Integridade das fixtures (classe F0_FixturesSinteticas) | registry + 5 fixtures | 6/6 OK (âncoras, IDs de cenário, proveniência, sem identificadores de engagements reais) | pass | idem |
| Regressão | `python .github/run_tests.py` (devdeps) | HEAD F0 | 76/76 ficheiros, 2638 testes, 34 skips, 3 xfail, 0 falhas | pass | execução local |
| CI | job `suite` | HEAD F0 | vermelho por D16 (19 ficheiros por dependências) | fail pré-existente, não causado por F0 | runs no GitHub |
| T03–T46 | — | — | fora do âmbito de F0; cobertura existente mapeada | **not-run** | `scenario-coverage.json` |

## 10. Métricas base

Definidas em [mechanisms-metrics.json](mechanisms-metrics.json):
- chamadas de agentes: parcial, por proxy (ficheiros `_council-prep`, `council-log`);
- contexto: parcial (`bootstrap` DEFAULT_BUDGET=40 itens, truncagem declarada);
- retrabalho: parcial (contadores de versão);
- questões materiais preservadas: parcial (congelar a verdade e comparar, reutilizando o mecanismo do `compare.py`);
- inconsistências: parcial (códigos de drift);
- perguntas do destinatário: **não observável** (precisa de schema novo em F5/F6).

Valores de partida sobre engagements: **not-run**, porque `projects/` está vazio neste ambiente. Único valor medido: custo da suite (≈50 s em paralelo, 162 s somados por ficheiro).

## 11. Decisões a fechar em F1 (resumo; 41 itens com localização no resultado do scout)

| ID | Decisão | Depende de |
| --- | --- | --- |
| D-F1-01 | Ambiente de testes e CI (D16) | mantenedor |
| D-F1-02 | Contrato de materialidade: regra dupla por perfil ou substituição do P-26; onde vivem tipo/impacto/âmbito/dono/fecho (colunas da SU ou sidecar); classe de bloqueio separada de criticidade; SCOPE-STATEMENT v2 (8 ficheiros) ou qualificado por perfil | decisão classic |
| D-F1-03 | Regra de evidência: retirar consenso→Confirmed; o que a síntese dialéctica pode produzir; desacordo = finding ou Conflicted | — |
| D-F1-04 | Persistência de perfil e rota: nome (`profile` já é o perfil de staffing do estimate), casa (`_state.json`), `schema_version` (int ou `nome/N`), semântica da ausência (não reutilizar `LEGACY_MODE`), guarda de versão para leitores antigos | decisão classic |
| D-F1-05 | Capacidades do pack: schema de `supported_workflow_profiles`/`supported_routes`/`design_contract_version`; conflito com a proibição de `routes`; packs skeleton; bump de `pack_version` | — |
| D-F1-06 | Códigos de erro estáveis e envelope de resposta; mapa dos códigos actuais | — |
| D-F1-07 | Guardas por perfil: ordem de lentes, completude, gates, conjunto de autoridades (incl. `_migration/`, `_work/`, `_design/`); resolver único | decisão classic |
| D-F1-08 | Admitir normativamente o checkpoint (`orchestration.md:92`, `aisa-status:104`) | — |
| D-F1-09 | Predicados de readiness: estender o objecto `readiness` ou chave nova; `unverified` ↔ `not_evaluated` | — |
| D-F1-10 | Coverage por lente: nova etapa ou artefacto; vocabulário; emendar `orchestration.md:112,125` | — |
| D-F1-11 | FC/J/WP: divisão de posse com o blueprint e o spec; namespaces; "completo para handoff" | — |
| D-F1-12 | Dependências tipadas vs a prosa "sem grafo de dependências"; change-impact sobre reopen/revisit; persistência da rota platform-constrained | — |
| D-F1-13 | Limites da dialéctica num só dono; sem aceitação por esgotamento | — |
| D-F1-14 | Options por rota (cardinalidade), acesso ao pack por mandato, nomear produtos por revisores | — |
| D-F1-15 | Classic e caminhos de migração (§12); tag da ref histórica | **mantenedor** |
| D-F1-16 | Itens "indeciso" de §5 (diários, `/retro`, memória de tenant, `--html`, portador do "não autorizado", `resolve.finding`, step8c) | mantenedor |
| D-F1-17 | Corrigir D01 e D02 no início de F1/F2 (âmbito mínimo, mudança de comportamento) | autorização |

## 12. Classic

Evidência: 5 famílias de engagements reais referenciadas (`pricing-marinha*`, `pricing-bunkers*`, `kam-onboarding*`, `dpt-galp-jp*`, `cae-automation*`). Nenhuma está neste checkout. O único uso real recente por um cliente é `pricing-bunkers-v2` (registos de coverage de 15–16 Set.). A escrita mais recente é de `pricing-bancas-marinha`, braço do plano anterior. Todos os consumidores runtime dos agentes de lente são do fluxo classic.

| Opção | Impacto | Custo | Risco |
| --- | --- | --- | --- |
| **A** — sem classic na versão nova | Engagement sem perfil é identificado e a escrita é recusada com instrução; a leitura e a continuação fazem-se na ref histórica | Baixo (campo de perfil, detecção, mensagem, tag) | Um engagement activo tem de ficar na versão antiga |
| B — compatibilidade limitada | Importação única dos engagements nomeados, sem runtime duplo, reutilizando dry-run/backup do `migrate.py` | Médio por formato de origem | Promoção indevida na importação (mitigada pelo passo 7 de 07) |
| C — manter o runtime classic | Dois runtimes, hooks e suites | Alto e contínuo | Divergência de gates entre perfis |

Recomendação: **A**, com B só para os engagements que o mantenedor nomear. **Decisão do mantenedor: A** (sem importação de engagements nomeados). Factos que só o mantenedor confirma: que engagements existem e estão activos no repositório privado; se `pricing-bunkers-v2` continua; se há cópias fora de `projects/`.

## 13. Gate de saída

| Critério (05_FASES F0) | Estado |
| --- | --- |
| Baseline reproduzível e falhas conhecidas classificadas | cumprido (T01) |
| Todos os ficheiros-alvo resolvidos | cumprido (62 resoluções; ambiguidades em P4) |
| Grupos legados classificados por relevância actual | cumprido como proposta (164 componentes + 75 testes); 11 itens "indeciso" encaminhados ao mantenedor |
| T01/T02 | pass |
| Decisão classic (F0 item 6) | **decidido pelo mantenedor: opção A** (§12) |

Critérios de qualidade de 06: **confirmados pelo mantenedor tal como estão**, antes de observar resultados (2026-09-23). São critérios de gate do programa.

Decisões do mantenedor registadas no fecho de F0 (2026-09-23, via pergunta explícita):

| Tema | Decisão | Consequência |
| --- | --- | --- |
| Classic | **A — sem runtime classic na versão nova**; engagements sem perfil ficam só de leitura e continuam, se preciso, na versão histórica | D-F1-02/04/07 sem ramo classic; `pre-lens-order-check` e testes de ordem de lentes vão para eliminação em F3; T35 deixa de ser obrigatório (só rejeição segura, T03/T36) |
| CI (D16) | **Dois jobs**: suite completa com dependências de teste (acrescentar python-docx e pypdf ao `requirements-dev.txt`) e job só stdlib para os testes dos motores (ADR-001) | D-F1-01 fechado; implementado em F1 |
| Critérios de qualidade (06) | Confirmados tal como estão | Gate do programa |
| F1 | **Autorizado**, começando por D01 (nascimento do `/start`) e pelo CI | Início de F1 |

## 14. Blockers e riscos

| ID | Âmbito | Impacto | Responsável | Condição de fecho |
| --- | --- | --- | --- | --- |
| B1 | Decisão classic | — | mantenedor | **fechado**: opção A |
| B2 | CI vermelho (D16) | Sem evidência de CI para gates de release até F1 aplicar a decisão | implementador | D-F1-01 decidido (dois jobs); fecha quando o CI ficar verde em F1 |
| R1 | Hooks activos na sessão de implementação (P3) | Uma mudança de hook pode bloquear a própria sessão | implementador | Testar cada hook novo por subprocesso antes de o registar |
| R2 | 30 testes dependem de dados privados e saltam aqui | Garantias não verificáveis neste ambiente | — | Reportadas como not-run, nunca como pass |
| R3 | Inventário por agentes | Erros de papel residuais | — | O T02 garante completude; os papéis têm evidência e adjudicação |

## 15. Recuperação e rollback

F0 só acrescenta ficheiros (§3). Rollback: `git revert` dos commits de F0 na branch, ou remover `docs/handoff-v1/F0/`, `.claude/tests/test_handoff_f0.py` e `.claude/tests/fixtures/handoff-v1/`. O runtime não muda, não há dados de engagement tocados e não há operações pendentes.

## 16. Retoma

- Última operação integrada: commit de fecho de F0 nesta branch.
- Inputs necessários: `docs/handoff-v1/plan/` (v1.2) e `docs/handoff-v1/F0/*`.
- Resultados recebidos e não integrados: nenhum. Os resultados brutos dos agentes ficaram fora do repo; o que conta está consolidado nos JSON.
- Ambiente: `pip install PyYAML openpyxl python-docx pypdf`; regressão com `python .github/run_tests.py` (esperado: 76/76, 2638, 34 skips, 3 xfail).
- Próxima acção segura: iniciar F1, incremento 1 (CI em dois jobs + ordem de nascimento do `/start`, D01), com relatório em `docs/handoff-v1/F1/RELATORIO.md`.
- Autorização: F1 autorizado pelo mantenedor em 2026-09-23. Push para a branch de trabalho autorizado a cada commit; sem PR nem merge sem pedido.

## 17. Proposta para F1

Objectivo (05_FASES F1): congelar contratos e perfil opt-in. Ordem proposta, em incrementos pequenos:
1. Corrigir D01 (ordem de nascimento do `/start`) e D-F1-01 (ambiente de CI), se autorizado: são pré-condições para testar qualquer coisa nova com verde honesto.
2. Contrato normativo de perfil e rota + schemas (D-F1-04/05/06), com T03/T04/T36.
3. Materialidade e evidência (D-F1-02/03) com T05–T08, incluindo a adaptação dos testes P-26 no mesmo incremento.
4. Guardas por perfil (D-F1-07) com a disposição dos testes de ordem de lentes.
5. Tabela leitor/escritor/schema e alterações incompatíveis, a partir de `consumer-matrix.json`.

Gate de F1: T03–T08, T35/T36; requisitos funcionais materiais deixam de ser descartados; pack incompatível falha claramente.
