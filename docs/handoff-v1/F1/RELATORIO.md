# Relatório de fase — F1

Estado: **completed** (2026-09-23). Gate cumprido; a excepção do T07 (metade de cobertura por lente) foi aceite pelo mantenedor e passa para o gate de F3 (§5). F2 autorizado.

- Data e responsável: 2026-09-23 · Claude Code, sessão `session_0156MuyJemPPrVqRKiDrAsct`, por autorização do mantenedor (F0 §13: «Sim, avançar para F1», começando pelo nascimento do `/start` e pelo ambiente de CI).
- Repositório, branch e SHA: `jorgedrestevao/aisa-refactor`, branch `claude/clone-repo-awui-7mmi37`. Início de F1: `d7afc5d` (fecho de F0). Último commit: ver `git log` da branch.
- Plano e fase: handoff-v1 **v1.2** ([plan/](../plan/README.md)), fase F1 — congelar contratos e perfil opt-in ([05_FASES.md](../plan/05_FASES.md)).
- Perfil/schema/pack afectados:
  - perfil `handoff-v1` (novo, experimental);
  - bloco `workflow` em `_state.json` (`handoff-state/1`);
  - grafo `schema_version` 2;
  - pack PP 1.10.0;
  - schemas novos em `library/kernel/schemas/`.
- Edição de `library/`: por script administrativo com commit por incremento (decisão do mantenedor, 2026-09-23). O hook `pre-write-guard.py` e o `deny` de `settings.json` ficam intactos.

## 1. Resultado

Passou a ser possível:
- CI verde e reproduzível. O job `suite` instala `requirements-dev.txt` e corre a suite inteira. O job `stdlib` não instala nada e corre a lista explícita `.github/stdlib-tests.txt`, que é a evidência de ADR-001.
- Criar um engagement pela ordem da skill em `AISA_GUARD_MODE=enforce` sem recusa do guarda (D01 fechado).
- Criar um engagement `handoff-v1` com perfil e rota escolhidos explicitamente no `/start` (Q5). Um pack que não declare o perfil ou a rota é recusado, sem fallback (T04).
- Um engagement da versão histórica é identificado e fica só leitura em todas as camadas: Skill, Write/Edit, coordenador, migrate, bootstrap. A leitura continua possível (T03, opção A).
- A versão histórica recusa escrever num engagement novo, pelos seus próprios guardas (T36, provado com o código real de `ba0c27b`; decisão Q1).
- `/status`, `/resume` e `aisa-orient` não escrevem (D02, Q6).
- Uma pergunta entra quando a resposta pode mudar um de cinco aspectos, e traz tipo, impacto, âmbito, quem responde, fecho, bloqueio e referências. Uma regra de arredondamento que não muda tecnologia é admitida (T05); um facto em falta não precisa de alternativas (T06); sem impacto demonstrável fica estacionada com motivo (T07, SU); prioridade ≠ bloqueio (Q3/Q4).
- Concordância entre personas não sobe o estado. O guarda recusa `Confirmed` sem localizador, incluindo promoção no lugar (T08, F0 D03/D19).
- Contratos congelados para F2–F6 (`library/kernel/handoff-contract.md`, `phases.md`, `orchestration.md`, 6 schemas), com a tabela leitor/escritor/schema e as alterações incompatíveis em [LEITOR-ESCRITOR.md](LEITOR-ESCRITOR.md).

Fora do âmbito de F1 (fases seguintes): publicação do checkpoint pelo coordenador (F2); cobertura por lente e fim das guardas de ordem fixa (F3); especialistas, revisão e Options por rota no gate (F4); FC, WP, dependências tipadas (F5); prontidão e índice de entrega (F6).

## 2. Alterações

| Incremento | Ficheiro/componente | Mudança | Contrato/requisito | Compatibilidade |
| --- | --- | --- | --- | --- |
| F1.1 `ec97ee3` | `.github/workflows/tests.yml` | Dois jobs: `suite` (com `pip install -r requirements-dev.txt`) e `stdlib` (sem instalação, com lista explícita) | D-F1-01; decisão do mantenedor «dois jobs»; F0 BL-DOC-1, D16 | Só CI |
| F1.1 | `.github/run_tests.py` | `--list <ficheiro>`: um ficheiro listado que não exista reprova. `expected failures=N` deixa de contar como `failures` (BL-REPORT-1). Docstring deixa de prometer a suite sem instalação. | D-F1-01 | Sem `--list`, o comportamento é o de antes |
| F1.1 | `.github/stdlib-tests.txt` (novo) | 57 ficheiros: os 56 com `verdict_stdlib = OK` na baseline T01, mais `test_handoff_f0.py` | ADR-001 | — |
| F1.1 | `requirements-dev.txt` | `python-docx>=1.2` e `pypdf>=6.19` (mínimos iguais às versões testadas); comandos do runner | BL-ENV-2 | Só ambiente de teste; o runtime continua só com a biblioteca padrão |
| F1.1 | `docs/handoff-v1/F0/consumer-matrix.json` | `.github/stdlib-tests.txt` registado como menção (nomeia `test_fields_draft.py`), não como consumidor | T02 | — |
| F1.2 `7989bdf` | `.claude/skills/aisa-start/SKILL.md` | `migrate.py init` passa do passo 9c para o novo passo 5b: logo depois de criar a pasta, antes de `_state.json`, SU, `decisions.md`, `answers.md` e linhas `M-n`. O passo 9c sai. A árvore da pasta nomeia `_graph/` e `_ops/`. | D01 | Engagements existentes não são tocados. Um engagement criado com a ordem antiga e já bloqueado continua a recuperar com `migrate.py apply`. |
| F1.2 | `.claude/tests/test_graph_birth.py` | Classe W8d: o nascimento corre pelos hooks Write/Edit reais lidos de `settings.json`, em `enforce`; um mutante com a ordem antiga tem de ser recusado; um teste de texto fixa `init` antes dos passos 7, 8, 9 e 9b | D01, T03 (nascimento) | — |
| F1.3 `2ac39fc`, `657fef0` | `docs/handoff-v1/F1/DESENHO-CONTRATOS.md` | Desenho dos contratos com evidência; decisões Q1–Q6 | D-F1-02..14 | Só documentação |
| F1.4a/b `ca9034f` | `library/kernel/tools/workflow.py` (novo) | `profile_of`, `pack_capabilities`, `validate_profile`, envelope com os 8 códigos, validador de schema (subconjunto; reporta e preserva campos desconhecidos); CLI único `check` | D-F1-04/06, I-01..I-06 | Só leitura |
| F1.4a/b | `library/kernel/schemas/*.schema.json` (6, novos) | `handoff-state`, `-pack`, `-response`, `-work`, `-functional`, `-index` | 05 F1 item 3 | Novos |
| F1.4a/b | `library/packs/pp/pack.yaml` | 1.10.0: `supported_workflow_profiles`, `supported_routes`, `design_contract_version` | Q2 | Chaves novas à raiz; nada removido |
| F1.4a/b | `library/kernel/orchestration.md` | "Dispatch is not routing" | Q2 | Emenda de fronteira |
| F1.4a/b | `test_pp_deliverable_templates.py`, `test_step8c_semantic_continuity.py` | Proibição de `routes:` com excepção só para a chave `supported_routes:`; versão do pack 1.10.0 com entrada no changelog | Q2 | Emendados no mesmo commit |
| F1.4c `102f017` | `graph.py` | `SCHEMA_VERSION = 2`; schema 1 nomeado como versão histórica (só leitura) | Q1 | **Incompatível**: a versão histórica não escreve em engagements novos (intencional) |
| F1.4c | `bootstrap.py` | Limitação de perfil que bloqueia: legado, `_state.json` ilegível, schema de perfil desconhecido, pack sem capacidade | T03/T36 | Engagements legados deixam de estar prontos para escrita |
| F1.4c | `operation.py`, `migrate.py` | `run`/`recover` e `apply`/`restore` recusam legado (o `migrate` antes de qualquer backup) | T03 | Idem |
| F1.4c | `pre-authority-guard.py` | `_state.json.tmp` guardado; `_graph/`, `_ops/`, `_migration/`, `_work/`, `_design/` sempre recusados por ferramenta (D05); `_state.json` sem perda de chaves nem mudança de `workflow` (I-07) | D05, I-07 | Mais restritivo |
| F1.4c | `pre-profile-check.py` (novo) + `settings.json` | Skill que escreve sobre legado recusada antes de começar | T03 | Novo hook |
| F1.4c | `aisa-start/SKILL.md` | Passo 3b (perfil e rota), bloco `workflow`, `answers.md#ROTA`, passo 9d (linha `C-001` da imposição, `workflow.py check`) | Q5, I-01 | — |
| F1.4c | 10 testes de motor + `fixtures/handoff-v1/estado.py` | Scaffolds passam a criar engagements `handoff-v1` | 09 (adaptar no mesmo incremento) | — |
| F1.4c | `test_handoff_legacy.py`, `test_handoff_workflow.py` (novos) | T03, T04, T36, D05, I-07, schemas | Gate F1 | — |
| F1.4c | `.github/workflows/tests.yml` | `fetch-depth: 0` (o T36 extrai o código histórico) | T36 | Só CI |
| F1.4d `d145f8a` | `aisa-status/SKILL.md`, `aisa-start/SKILL.md` | `/status` não escreve; o esqueleto da SU perde a linha de saúde | Q6, D02 | O `dashboard` lia-a só como nota |
| `bc60d2c` | `test_operation_concurrency.py` | O dono do lock segura-o até todos tentarem (flake pré-existente, provado na baseline) | 06 (evidência fiável) | Teste mais forte |
| F1.5 `cf55133` | `dashboard.py` (parser, aditivo) | Colunas da admissão lidas por cabeçalho (aliases por secção: `impacto` de pergunta ≠ `impacto` do Risky); marca `estacionada (<motivo>)`; fixture `su-schemas/handoff-v1-shared-understanding.md` | Q3 | SU antiga lê-se igual |
| F1.5 `69d0224` | `states.md`, `glossary.md`, `CLAUDE.md`, `phases.md`, 6 lentes, `aisa-round`, `chairman-synthesis`, `aisa-answer`, `aisa-capture`, `aisa-status`, `aisa-start`, memória de 7 agentes, SCOPE v2 em 8 ficheiros | Admissão handoff-v1 substitui P-26; sexta edição sancionada = estacionar; árbitro estaciona/devolve; motor 1.15.0 (modelo schema 3) | Q3, Q4, D-F1-02 | **Incompatível** (LEITOR-ESCRITOR §2, #6–#7, #9); linhas antigas nunca reclassificadas |
| F1.5 | `test_admission_rule`, `test_arbiter_declarations`, `test_swing_parse`, `test_technical_decision_refocus`, `test_state_scaffold`, `test_blueprint_yaml`, fixture `admission-cases.md` | Adaptados no mesmo commit, segundo as disposições F0 (invariantes do motor mantidos; auto-contagem e marcador TO-BE retirados) | 09 | — |
| F1.6 `2a3b412` | `chairman.md`, `chairman-synthesis`, `orchestration.md`, `pre-authority-guard.py`, `CLAUDE.md` princípio 5, `glossary.md`, `HOOKS.md` | Sem caminho de contagem para `Confirmed`; síntese resolve recomendações; guarda recusa `Confirmed` sem localizador (`audit_confirmed_locators`) | T08, D03, D19 | **Incompatível** (#8) |
| F1.6 `90d77a0` | `handoff-contract.md` (novo), `phases.md`, `orchestration.md`, `workflow.py`, `handoff-functional.schema.json`, `aisa-status`, `CLAUDE.md` | Contratos congelados (FC/J/WP, índice, checkpoint, revisão, dependências, Options por rota, prontidão); N/A com motivo no schema | 05 F1 itens 3–5 | Só contrato; implementação F2–F6 |
| F1.6 | `docs/handoff-v1/F1/LEITOR-ESCRITOR.md` | Tabela leitor/escritor/schema e 13 alterações incompatíveis | 05 F1 item 7 | — |

## 3. Decisões e evidência

- **D-F1-01 (CI)**, decidida pelo mantenedor: dois jobs. Os mínimos de versão em `requirements-dev.txt` são as versões com que a baseline correu (`test-baseline.json` → `environments.devdeps`), não versões escolhidas por conveniência.
- **Execução em paralelo** (regra do mantenedor, 2026-09-23): workflows paralelos só para tarefas que não precisam do contexto da sessão e cujo detalhe não acrescenta nada à sessão. O desenho dos contratos F1 tinha sido lançado como workflow paralelo (run `wf_a1920f13-d01`: 6 desenhadores e uma revisão cruzada, só leitura). Parado por decisão do mantenedor com 2 agentes em curso; nenhum resultado foi recebido nem integrado. O desenho passou para a sessão. Regra registada em [../README.md](../README.md) → *Regras de execução*.
- **Desenho dos contratos F1** ([DESENHO-CONTRATOS.md](DESENHO-CONTRATOS.md)), com evidência `ficheiro:linha`. Decisões do mantenedor, 2026-09-23, todas na opção recomendada:
  - Q1 vedação contra a versão histórica: grafo `schema_version = 2` nos engagements `handoff-v1`;
  - Q2 nomes do plano no pack (`supported_workflow_profiles`, `supported_routes`, `design_contract_version`), com emenda dos testes que recusam `routes:` e da fronteira do orquestrador;
  - Q3 campos da pergunta como colunas novas da SU;
  - Q4 SCOPE-STATEMENT v2;
  - Q5 `/start` pergunta sempre o perfil;
  - Q6 (D02) `/status`, `/resume` e `aisa-orient` deixam de escrever na SU.
  As escolhas internas I-01..I-14 ficam registadas para objecção.
- **Correcção de registo**: a mensagem do commit `d145f8a` diz "suite 78/78", mas essa execução teve uma falha em `test_operation_concurrency.py` (W09). O commit passou porque a cadeia de comandos verificou o código de saída do `tail`, não o da suite. Diagnóstico:
  - com CPU carregada, o W09 falha 1 em 24 execuções também na baseline `ba0c27b`;
  - causa: o dono sai, a saída liberta o `flock`, e um irmão atrasado recupera legitimamente um dono morto;
  - corrigido em `bc60d2c`: 0 em 36 depois;
  - a partir daqui os commits só seguem com código de saída 0 das duas suites.
- **I-nn aplicadas em F1.4**:
  - o coordenador recusa só o legado. `_state.json` ilegível fica a cargo do bootstrap, porque recusar no coordenador impedia a recuperação que o repara (os testes de recuperação provaram-no).
  - O `workflow.py` carrega o dashboard só para ler `pack.yaml`, e reutiliza o do bootstrap/migrate. Latência do guarda: 0,151 s → 0,162 s por escrita.
  - O hook de Skill não adivinha entre vários engagements; nesse caso, as outras camadas recusam a escrita.
- **Decisões internas de F1.5/F1.6** (revertíveis, com base no plano):
  - aspectos do impacto escritos com as palavras do próprio plano (02 §4), sem sinónimos inventados;
  - estacionar é a sexta edição sancionada, e qualquer escritor a pode fazer com motivo (a retirada P-21 continua só do dono);
  - o árbitro devolve à lente as linhas incompletas e nunca preenche um campo;
  - o `aisa-capture` preça linhas PM-U (não linhas da SU) e aponta para a regra;
  - o contrato novo `handoff-contract.md` só guarda o que não tinha dono; as regras com dono ficaram no dono (Options e prontidão no `phases.md`; checkpoint e dependências no `orchestration.md`);
  - o `resolve.dispose_finding` não muda em F1: o vocabulário de disposições está no contrato e a implementação é de F4.
- **Defeito apanhado pelos testes**: o commit aditivo do parser (`cf55133`) tratava as linhas Conflicted novas como SU antiga, porque procurava a coluna `tipo`. Corrigido em `69d0224`.
- **D01**: a ordem nova foi provada com os hooks reais antes de mudar a skill (simulação em diretório temporário: a ordem antiga é recusada por `pre-authority-guard.py` no Write da SU; a ordem nova passa todos os passos, o bootstrap fica `ready` e `M-1` chega ao grafo com `mirror_of = SU:M-1`). `docs/ONBOARDING.md` §3.2 descreve uma sequência sem linhas `M-n` (SU, estado, `init`) que não é recusada. Fica por alinhar com a documentação de F7, não com este incremento.

## 4. Testes

| ID | Comando/procedimento | Revisão/fixture | Resultado observado | pass/fail/not-run | Evidência |
| --- | --- | --- | --- | --- | --- |
| Regressão devdeps | `python .github/run_tests.py` (venv com as 4 dependências, Python 3.11.15) | `7989bdf` | 76/76 ficheiros, 2641 testes, 0 falhas, 3 falhas esperadas, 34 skips | pass | execução local |
| Regressão stdlib | `python .github/run_tests.py --list .github/stdlib-tests.txt` (venv sem pacotes) | `7989bdf` | 57/57 ficheiros, 1843 testes, 52 skips | pass | execução local |
| Lista com ficheiro inexistente | `run_tests.py --list` com uma entrada que não existe | `ec97ee3` | `FAIL nao/existe.py listado em … mas nao existe`, exit 1 | pass | execução local |
| CI F1.1 | GitHub Actions, run 35892296681 (Python 3.12) | `ec97ee3` | jobs `suite` e `stdlib` com sucesso | pass | Actions run #13 |
| CI F1.2 | GitHub Actions, run 35892799995 | `7989bdf` | jobs `suite` e `stdlib` com sucesso | pass | Actions run #14 |
| D01 / W8d | `python .claude/tests/test_graph_birth.py` | `7989bdf` | 20/20. Com o texto antigo da skill, `test_the_skill_creates_the_graph_before_the_first_authority` falha | pass | execução local e mutante |
| Regressão F1.4 devdeps | `python .github/run_tests.py` | `bc60d2c` | 78/78 ficheiros, 2691 testes, 0 falhas, 3 falhas esperadas, 34 skips; exit 0 | pass | execução local |
| Regressão F1.4 stdlib | `run_tests.py --list .github/stdlib-tests.txt` | `bc60d2c` | 59/59 ficheiros, 1893 testes, 52 skips; exit 0 | pass | execução local |
| CI F1.4 | GitHub Actions runs #20 (`ca9034f`), #21 (`102f017`), #22 (`d145f8a`) | — | jobs `suite` e `stdlib` com sucesso | pass | Actions |
| T03 | `test_handoff_legacy.py` T03_* | `bc60d2c` | legado recusado em Skill, Write/Edit (5 autoridades), coordenador (`run`, `recover`), `migrate.apply`, bootstrap; pegada dos ficheiros igual antes/depois; `build_model` lê o legado | pass | execução local e CI |
| T04 | `test_handoff_workflow.py` T04_* | `ca9034f` | packs skeleton, pack sem a rota, declaração malformada, pack inexistente e perfil desconhecido → `UNSUPPORTED_PROFILE` | pass | idem |
| T36 | `test_handoff_legacy.py` T36_*; `test_handoff_workflow.py` T36_* | `bc60d2c` | código histórico real (`ba0c27b`): o guarda recusa as 4 autoridades, o bootstrap diz `UNSUPPORTED_SCHEMA`, o `migrate.init` não substitui o grafo; schema de estado futuro → `SCHEMA_UNSUPPORTED` sem tocar no ficheiro | pass | idem |
| D05 / I-07 | `test_handoff_legacy.py` D05_*, I07_* | `102f017` | 5 directórios coordenados recusados com o engagement pronto; perda de chave, mudança de rota por Write/Edit e JSON inválido recusados; mudança de ronda passa | pass | idem |
| D02 | `test_handoff_legacy.py` D02_* | `d145f8a` | o texto antigo da skill faz o teste falhar | pass | execução local e mutante |
| W09 stress | 36 execuções com 4 CPUs ocupadas | `bc60d2c` | 0 falhas (antes 1/12; baseline 1/24) | pass | execução local |
| T05 | `test_admission_rule` `test_t05_*` (fx-hv1-02 E01) | `69d0224` | regra de arredondamento (funcional, aceitação; `blocks_scope`) admitida sem falta | pass | local e CI #26 |
| T06 | `test_admission_rule` `test_t06_*`; `test_arbiter_declarations` `test_so_a_design_choice_deve_alternativas` | `69d0224` | `fact_gap` sem alternativas não é assinalado; `design_choice` sem alternativas é | pass | idem |
| T07 (SU) | `test_handoff_questions` `Estacionada` | `cf55133` | estacionada com motivo: não aberta, não fechada; sem motivo: aberta com diagnóstico | pass | local e CI #25 |
| T07 (N/A) | `test_handoff_workflow` `test_t07_*` | `90d77a0` | N/A sem motivo recusado pelo schema do FC | pass | local |
| T07 (cobertura por lente) | — | — | "N/A inválido não fecha cobertura": a etapa de cobertura por lente não existe antes de F3 | not-run | excepção por aceitar (§5) |
| T08 | `test_handoff_evidence` (11 casos, hook real) | `2a3b412` | consenso → recusado; localizador válido → passa; alvo ausente → recusado; promoção no lugar → recusada; troca de evidência por concordância → recusada | pass | local e CI #27 |
| T30 (contrato) | `test_handoff_evidence` `test_t30_*` | `2a3b412` | síntese resolve recomendações; escala no limite, nunca aceita por esgotamento | pass (só contrato; F4 implementa) | local |
| Contratos | `test_handoff_contract` (10 casos) | `90d77a0` | schemas nomeados existem; campos do FC do plano no schema; rotas e predicados no `phases.md`; checkpoint e dependências no `orchestration.md` | pass | local |
| Regressão final | `run_tests.py` e `--list .github/stdlib-tests.txt` | `90d77a0` | 81/81 ficheiros, 2717 testes, 0 falhas, 3 falhas esperadas, 34 skips; stdlib 62/62, 1919 testes; exit 0 nas duas | pass | local; CI #28 a correr à data |

## 5. Gate de saída

Gate de F1 (05_FASES): T03–T08, T35/T36; requisitos funcionais materiais já não descartados; pack incompatível falha claramente.

| Critério | Estado | Evidência |
| --- | --- | --- |
| T03 engagement sem perfil | cumprido (opção A: identificado, só leitura, sem migração implícita) | §4 T03 |
| T04 pack sem capacidade | cumprido | §4 T04 |
| T05 regra de arredondamento material | cumprido | §4 T05 |
| T06 facto em falta sem alternativas | cumprido | §4 T06 |
| T07 estacionamento justificado; N/A inválido não fecha cobertura | **parcial**: estacionamento na SU e N/A do FC cumpridos; "não fecha cobertura por lente" depende da etapa de cobertura por lente (F3) | §4 T07 |
| T08 concordância não promove | cumprido | §4 T08 |
| T35 migração de engagement antigo | não aplicável por decisão (opção A: sem migração; recusa segura provada no T03) | §4 T03 |
| T36 leitor antigo encontra schema novo | cumprido (código real de `ba0c27b`; schema de estado futuro) | §4 T36 |
| Requisitos funcionais materiais não descartados | cumprido (admissão pelos cinco aspectos; T05) | §4 T05 |
| Pack incompatível falha claramente | cumprido | §4 T04 |
| Testes classic adaptados ou eliminados no mesmo incremento | cumprido (09) | §2 F1.5 |

Excepção: o T07 na metade de cobertura por lente. **Aceite pelo mantenedor em 2026-09-23** («Aceitar, fecha em F3»): entra no gate de F3, onde nasce a etapa de cobertura por lente.

## 6. Blockers e riscos

| ID/referência | Âmbito | Impacto | Responsável | Condição de fecho |
| --- | --- | --- | --- | --- |
| P3 (F0) | Guardas por perfil | Os hooks do projecto correm na sessão que implementa. Uma guarda nova mal ordenada bloqueia a própria sessão. | Implementação | Guardas testadas em diretório temporário antes de ligar em `settings.json` |
| SYN-VENDOR por rota | Síntese em `platform-constrained` | A plataforma imposta está na linha `C-001`; o SYN-VENDOR dos topic packs neutros pode assinalá-la | F4/F6 | Critério de vendor por rota |
| Escritas por `Bash` | Guardas | `mv` de `_state.json.tmp` e escritas por shell não passam por hooks, na versão histórica e na nova | Limitação documentada | Coordenador para todas as escritas canónicas (F2) |
| `docs/ONBOARDING.md`, `docs/COMO-USAR.md` | Documentação | O walkthrough do `/start` ainda não mostra perfil e rota | F7 | Actualizar (o `CLAUDE.md` já lista `workflow.py`, schemas e contrato) |
| `su-confirmed-guard.py` | Hooks | Com a recusa no guarda de autoridade, fica redundante em `handoff-v1` (avisa depois de uma escrita que já não acontece) | F2 | Consolidar ou eliminar com a disposição F0 |
| `CALIBRACAO` no motor | Higiene (F0 H2) | Slugs de engagements reais continuam em `dashboard.py` (`funding_gate_audit`) | F2/F7 | Remover dos ficheiros normativos |

## 7. Recuperação e rollback

Revertem com `git revert`:
- F1.1, F1.2 e F1.4d, sem dados envolvidos.
- F1.4c muda o schema do grafo dos engagements **novos**. Reverter o código depois de criar engagements `handoff-v1` deixa-os ilegíveis para escrita pela versão revertida: é a vedação a funcionar. Nesse caso o caminho é roll-forward, não restauro (07).
- Nenhum engagement existente foi migrado ou alterado.

## 8. Retoma

- Última operação integrada: `90d77a0` (F1.6; todo o trabalho de F1).
- Inputs/revisões necessários: plano v1.2; F0/RELATORIO.md §11 (decisões D-F1-02..17) e §17 (proposta de F1).
- Drafts/resultados recebidos ainda não integrados: nenhum. O workflow de desenho foi parado sem resultados (§3); o desenho dos contratos F1 corre na sessão.
- Próxima ação segura: F2, a partir da proposta de §9, com o desenho feito na sessão (regra de execução do README).
- Autorização necessária antes de continuar: nenhuma para começar F2 (autorizado em 2026-09-23). Decisões materiais de F2 voltam ao mantenedor.

## 9. Proposta para F2 — continuidade transacional mínima

Pelo plano (05_FASES F2) e pelos defeitos do F0 ainda abertos:

1. Checkpoint publicado pelo coordenador (`_work/checkpoint.json`, `handoff-work/1`), com eventos de checkpoint e reconciliação de `running` depois de uma falha (04).
2. Read-set completo no bootstrap: blueprint, spec, estimate, frame, options, pack e `_capture` entram no snapshot. `operation.run` passa a aceitar inputs só de leitura como pré-condição, e um input alterado dá `STALE_INPUT` (F0 P8, D08, D17).
3. As escritas canónicas das skills passam pelo coordenador; a limitação das escritas por `Bash` (LEITOR-ESCRITOR §3) fica fechada para os caminhos canónicos.
4. Idempotência do `render-validate` e do `coverage finalize`, e números de versão nunca reutilizados (D06, D07). `migrate restore --force` não apaga D-NNN (D10).
5. Disposição de `su-confirmed-guard` (redundante) e remoção dos slugs reais do motor (H2).
6. Gate de F2 (05_FASES): T09–T17; nenhum leitor considera um conjunto misto como revisão válida; a dupla integração é idempotente. Inclui falha injetada nos limites de publicação e concorrência de duas sessões (item 7 do plano).
