# Relatório de fase — F1

Estado: **in_progress** — F1.1 (CI), F1.2 (nascimento do `/start`), F1.3 (desenho e decisões Q1–Q6) e F1.4 (perfil, schemas, legado só-leitura, grafo 2, D02) integrados. Por fazer: materialidade (T05–T07), evidência (T08), textos normativos de prontidão/FC/rotas, tabela leitor/escritor/schema, gate.

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

Por fazer em F1: contratos de perfil, rota e schema; materialidade; evidência; readiness e checkpoint; guardas por perfil; FC/J/WP; tabela leitor/escritor/schema; gate T03–T08 e T35/T36.

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

## 5. Gate de saída

Cumprido até agora, com evidência em §4:
- T03 (opção A: identificação e recusa segura sem migração implícita);
- T04;
- T36;
- schemas versionados de perfil, checkpoint, FC, índice e resposta.

Por cumprir (05_FASES F1): contratos e schemas versionados; engagement legado identificado sem migração implícita (T03, opção A: recusa segura de escrita); pack incompatível falha claramente (T04); materialidade e evidência (T05–T08); T35/T36; testes classic adaptados ou eliminados no mesmo incremento.

## 6. Blockers e riscos

| ID/referência | Âmbito | Impacto | Responsável | Condição de fecho |
| --- | --- | --- | --- | --- |
| P3 (F0) | Guardas por perfil | Os hooks do projecto correm na sessão que implementa. Uma guarda nova mal ordenada bloqueia a própria sessão. | Implementação | Guardas testadas em diretório temporário antes de ligar em `settings.json` |
| SYN-VENDOR por rota | Síntese em `platform-constrained` | A plataforma imposta está na linha `C-001`; o SYN-VENDOR dos topic packs neutros pode assinalá-la | F4/F6 | Critério de vendor por rota |
| Escritas por `Bash` | Guardas | `mv` de `_state.json.tmp` e escritas por shell não passam por hooks, na versão histórica e na nova | Limitação documentada | Coordenador para todas as escritas canónicas (F2) |
| `docs/ONBOARDING.md`, `CLAUDE.md` | Documentação | Ainda descrevem o `/start` sem perfil e não listam `workflow.py`/schemas | F1.8 / F7 | Actualizar |

## 7. Recuperação e rollback

Revertem com `git revert`:
- F1.1, F1.2 e F1.4d, sem dados envolvidos.
- F1.4c muda o schema do grafo dos engagements **novos**. Reverter o código depois de criar engagements `handoff-v1` deixa-os ilegíveis para escrita pela versão revertida: é a vedação a funcionar. Nesse caso o caminho é roll-forward, não restauro (07).
- Nenhum engagement existente foi migrado ou alterado.

## 8. Retoma

- Última operação integrada: `bc60d2c` (F1.4 completo).
- Inputs/revisões necessários: plano v1.2; F0/RELATORIO.md §11 (decisões D-F1-02..17) e §17 (proposta de F1).
- Drafts/resultados recebidos ainda não integrados: nenhum. O workflow de desenho foi parado sem resultados (§3); o desenho dos contratos F1 corre na sessão.
- Próxima ação segura: materialidade (Q3/Q4) em [DESENHO-CONTRATOS.md](DESENHO-CONTRATOS.md) §2.2. Inclui `states.md`, colunas novas da SU, escritores do P-26 e SCOPE v2, com testes P-26 adaptados no mesmo commit (T05–T07).
- Autorização necessária antes de continuar: nenhuma nova para F1.4–F1.8 (Q1–Q6 decididas). Uma escolha nova que mude contrato volta ao mantenedor.
