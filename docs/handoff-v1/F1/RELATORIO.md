# Relatório de fase — F1

Estado: **in_progress** — F1.1 (CI) e F1.2 (nascimento do `/start`) integrados; desenho dos contratos (F1.3) em curso; nenhum contrato de `library/` alterado ainda.

- Data e responsável: 2026-09-23 · Claude Code, sessão `session_0156MuyJemPPrVqRKiDrAsct`, por autorização do mantenedor (F0 §13: «Sim, avançar para F1», começando pelo nascimento do `/start` e pelo ambiente de CI).
- Repositório, branch e SHA: `jorgedrestevao/aisa-refactor`, branch `claude/clone-repo-awui-7mmi37`. Início de F1: `d7afc5d` (fecho de F0). Último commit: ver `git log` da branch.
- Plano e fase: handoff-v1 **v1.2** ([plan/](../plan/README.md)), fase F1 — congelar contratos e perfil opt-in ([05_FASES.md](../plan/05_FASES.md)).
- Perfil/schema/pack afectados até agora: **nenhum**. F1.1 muda só o CI; F1.2 muda a ordem de uma skill.
- Edição de `library/`: por script administrativo com commit por incremento (decisão do mantenedor, 2026-09-23). O hook `pre-write-guard.py` e o `deny` de `settings.json` ficam intactos.

## 1. Resultado

Passou a ser possível:
- CI verde e reproduzível. O job `suite` instala `requirements-dev.txt` e corre a suite inteira. O job `stdlib` não instala nada e corre a lista explícita `.github/stdlib-tests.txt`, que é a evidência de ADR-001.
- Criar um engagement pela ordem da skill em `AISA_GUARD_MODE=enforce` sem recusa do guarda (D01 fechado).

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

## 3. Decisões e evidência

- **D-F1-01 (CI)**, decidida pelo mantenedor: dois jobs. Os mínimos de versão em `requirements-dev.txt` são as versões com que a baseline correu (`test-baseline.json` → `environments.devdeps`), não versões escolhidas por conveniência.
- **D01**: a ordem nova foi provada com os hooks reais antes de mudar a skill (simulação em diretório temporário: a ordem antiga é recusada por `pre-authority-guard.py` no Write da SU; a ordem nova passa todos os passos, o bootstrap fica `ready` e `M-1` chega ao grafo com `mirror_of = SU:M-1`). `docs/ONBOARDING.md` §3.2 descreve uma sequência sem linhas `M-n` (SU, estado, `init`) que não é recusada. Fica por alinhar com a documentação de F7, não com este incremento.

## 4. Testes

| ID | Comando/procedimento | Revisão/fixture | Resultado observado | pass/fail/not-run | Evidência |
| --- | --- | --- | --- | --- | --- |
| Regressão devdeps | `python .github/run_tests.py` (venv com as 4 dependências, Python 3.11.15) | `7989bdf` | 76/76 ficheiros, 2641 testes, 0 falhas, 3 falhas esperadas, 34 skips | pass | execução local |
| Regressão stdlib | `python .github/run_tests.py --list .github/stdlib-tests.txt` (venv sem pacotes) | `7989bdf` | 57/57 ficheiros, 1843 testes, 52 skips | pass | execução local |
| Lista com ficheiro inexistente | `run_tests.py --list` com uma entrada que não existe | `ec97ee3` | `FAIL nao/existe.py listado em … mas nao existe`, exit 1 | pass | execução local |
| CI F1.1 | GitHub Actions, run 35892296681 (Python 3.12) | `ec97ee3` | jobs `suite` e `stdlib` com sucesso | pass | Actions run #13 |
| CI F1.2 | GitHub Actions, run 35892799995 | `7989bdf` | em fila à data desta versão do relatório | not-run | Actions run #14 |
| D01 / W8d | `python .claude/tests/test_graph_birth.py` | `7989bdf` | 20/20. Com o texto antigo da skill, `test_the_skill_creates_the_graph_before_the_first_authority` falha | pass | execução local e mutante |

## 5. Gate de saída

Por cumprir (05_FASES F1): contratos e schemas versionados; engagement legado identificado sem migração implícita (T03, opção A: recusa segura de escrita); pack incompatível falha claramente (T04); materialidade e evidência (T05–T08); T35/T36; testes classic adaptados ou eliminados no mesmo incremento.

## 6. Blockers e riscos

| ID/referência | Âmbito | Impacto | Responsável | Condição de fecho |
| --- | --- | --- | --- | --- |
| P3 (F0) | Guardas por perfil | Os hooks do projecto correm na sessão que implementa. Uma guarda nova mal ordenada bloqueia a própria sessão. | Implementação | Guardas testadas em diretório temporário antes de ligar em `settings.json` |

## 7. Recuperação e rollback

F1.1 e F1.2 revertem com `git revert` do commit respectivo. Não há dados de engagement nem schema alterados.

## 8. Retoma

- Última operação integrada: F1.2 (`7989bdf`).
- Inputs/revisões necessários: plano v1.2; F0/RELATORIO.md §11 (decisões D-F1-02..17) e §17 (proposta de F1).
- Drafts/resultados recebidos ainda não integrados: desenho dos contratos F1 (workflow de leitura e desenho, sem escrita no repositório).
- Próxima ação segura: fechar o desenho dos contratos e apresentar ao mantenedor as decisões materiais antes de qualquer mudança em `library/`.
- Autorização necessária antes de continuar: decisões materiais de contrato (perfil/rota/schema, capacidades do pack, materialidade, evidência).
