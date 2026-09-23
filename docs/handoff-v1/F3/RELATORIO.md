# F3 — Relatório da fase (análise integrada e materialidade funcional)

Estado: **in progress** (2026-09-23). Desenho e decisões Q1–Q5: [DESENHO.md](DESENHO.md). Gate: T05–T08, T18, T19 e a fixture `fx-hv1-02` (§6 do desenho).

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F3.1 Etapa `lens` no coverage + contrato | integrado | `f221d30` | `coverage.py`: quarta etapa, sem alvo como a `reconciliation` (`TARGETLESS`); `lens_coverage` com as seis dimensões, `conflict_scan` e autor; regras fixas em `_check_lens`; revisão por dimensão em `_check_lens_semantic` (revisor ≠ autor); `lens_skeleton` (herda perspectivas, nunca a revisão); `lens_round_state`; CLI `lens-draft` e `round-state` (exit 0 fecha, 4 não fecha); secção «Perspectivas» no relatório. Contrato `coverage-contract.md` §4.8, tabela de etapas e de raiz. `test_coverage_lens.py` 21 casos (T18, T19 parte fixa e veredicto do revisor, T07). Full 87/87 ficheiros, 2820 testes; stdlib 68/68, 2022; ambos exit 0 |
| F3.2 `lens-checklists.md` + retirada das 6 skills de lente | integrado | `f6f62f0` | `library/kernel/lens-checklists.md`: dono único das seis perspectivas. Leva as perguntas centrais do plano 03, as quatro perguntas, o que cada perspectiva privilegia, as pistas, as regras próprias (`step_duration`, `data_shape`, varrimento de conflitos depois das outras cinco, `funding_gate` e aritmética da *baseline*, papéis e não pessoas), a evidência de cobertura por perspectiva e as regras comuns, escritas uma vez só. Saem `lens-business`, `-operations`, `-user`, `-data`, `-governance` e `-financial`; `lens-technology` fica. Ponte no `/round` (4a, 4b): aplica a secção inline. Os agentes-persona apontam a sua secção. Matriz F0: 11 entradas retiradas, 3 novas e 1 `mention_only`. Docs de consulta anotados. `test_lens_checklists.py` 14 casos. Full 88/88, 2834; stdlib 69/69, 2036; ambos exit 0 |
| F3.3 `/round` integrado + revisor + fecho por cobertura | integrado | (este) | `/round` reescrito: uma análise, um rascunho da SU (passo 4), depois o árbitro (passo 5, antes do registo, para o registo não nascer desactualizado), depois o registo `lens` (`lens-draft` → preencher → revisor → `finalize`), depois o fecho por `round-state` (passo 7). `/round <perspectiva>` aprofunda uma, herda as outras cinco e nunca fecha. `--close` = revisor + `round-state`. Revisor: agente `lens-coverage-reviewer` (Read/Grep/Glob, contexto novo, uma chamada no fecho, devolve `semantic_review`). Dashboard 1.16.0: `lentes_ronda_aberta` lê o registo `lens` num engagement com perfil (seis ou nenhuma, mais `fonte`/`fecha`/`revista`/`motivos`); a versão histórica mantém a leitura por cabeçalhos. Sai o `pre-lens-order-check` (ficheiro, `settings.json`, `HOOKS.md`) e o `round_lenses`; `phases.md` diz a regra nova. Matriz F0: 2 entradas do hook retiradas, 2 do revisor novas. Full 88/88, 2819; stdlib 69/69, 2021; ambos exit 0 |
| F3.4 `/frame` integrado + revisor; hooks de fase por perfil | por fazer | | |
| F3.5 Captura PM-U, `/status`, fixture `fx-hv1-02` | por fazer | | |
| F3.6 Relatório e gate | por fazer | | |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F3.1 | motor, contrato, testes | precisa do contexto da sessão (decisões Q1–Q5, motor de F2); o detalhe volta a ser preciso | na sessão |
| F3.2 | fusão das 6 skills, retarget de testes | precisa do contexto (o texto das skills e os testes que o fixam); o detalhe é o produto | na sessão |
| F3.3 (execução) | `/round`, dashboard, testes | precisa do contexto; o detalhe é o produto | na sessão |
| F3.3 (desenho do framework) | revisor da cobertura em `/round` | não precisa do contexto do autor (tem de não o ter); volta só o veredicto | subagente `lens-coverage-reviewer`, 1 chamada sequencial no fecho; a análise fica inline |

## 3. Testes adaptados

- `test_audit_round2.R2_05` (manter): toda a chamada a `compute_basis` declara `graph_consumed`. O esqueleto `lens` passa `graph_consumed=()`, porque a etapa não consome o grafo. É uma declaração explícita, não uma excepção ao teste.
- F3.2, os testes que liam as skills de lente passam a ler `lens-checklists.md`, uma vez e não seis. A garantia testada não muda:
  - `test_a5_dictionary_contract`: `step_duration` e `data_shape`;
  - `test_admission_rule`: o canal `lens-checklists` substitui os seis. A frase do passo 5 passa a «as the common rules state it»;
  - `test_orchestrator_wiring`: as perspectivas não lêem o manifesto do pack nem o banco de perguntas;
  - `test_technical_decision_refocus`: o papel e não a pessoa, e a ignorância da organização;
  - `test_council_wiring`: a persona aponta o ficheiro e não o lê. `solution-architect` continua a dizer «its `SKILL.md`».
- F3.2, os testes que usavam uma skill retirada como exemplo passam a usar uma que existe:
  - `test_handoff_skill_writes`: os escritores são os que existem;
  - `test_handoff_legacy`: `lens-technology` em vez de `lens-data` como exemplo do prefixo `lens-`.

- F3.3, `test_round_in_progress` (disposição por caso):
  - **eliminados** 19 casos que testavam o hook retirado: a sequência P-R6, a resolução do engagement pelo hook, o modo isolado autorizado pelo estado, `round_lenses` e o cabeçalho no corpo visto pelo hook. Não há ordem a policiar (Q2): as seis perspectivas são uma análise, e a passagem fecha pelo registo. A garantia que substitui é a de `RecordIsTheSourceForAProfile` e `test_coverage_lens.py`;
  - **eliminados** 3 casos de contrato do modo isolado e do `round_lenses`, substituídos por 3 do contrato novo (fecho pelo registo, revisor uma vez no fecho, hook e registo retirados);
  - **mantidos** a regra da passagem aberta no motor, a leitura por cabeçalhos da versão histórica e o contrato de `round_in_progress`;
  - **novos** 4 casos de `RecordIsTheSourceForAProfile`: sem registo, nada fica coberto e diz-se porquê; seis cabeçalhos não fecham uma passagem com perfil; o registo desta passagem cobre as seis e o de outra não conta; a leitura independente dá «revista».
- F3.3, adaptados:
  - `test_motor_identity`: a varredura de ids passa a correr «before EACH draft» (análise e árbitro), porque já não há uma por lente;
  - `test_step8c_semantic_continuity`: a lista fechada de agentes ganha o `lens-coverage-reviewer` (Q3);
  - `test_blueprint_yaml`: o motor do dashboard passa a 1.16.0.

## 4. Limitações conhecidas

- Até à F3.4 e à F3.5, dois textos ainda falam em perspectivas «em falta» uma a uma: o `/frame` (critério suave, F3.4) e o `/status` (linha da passagem a meio, F3.5). Os dados que lêem já vêm do registo, com as seis ou nenhuma, e o texto é corrigido nessas fases.
- A independência do revisor vem da instrução do `/round`, que manda contexto novo e só caminhos. O motor verifica apenas que os nomes declarados diferem.
- Uma primeira passagem aberta por `/round <perspectiva>` não tem registo até um `/round` completo cobrir as seis. É intencional: o `finalize` recusa um registo sem as seis.

- Janela de transição F3.2 → F3.3: sem skills de lente para invocar, o hook `pre-lens-order-check` não intercepta nada. A ordem de uma passagem completa depende só do ciclo do `/round`. O `round_lenses` continua a ser escrito, e a guarda de passagem (3.4) continua a ler o motor. F3.3 substitui o ciclo pela análise integrada, com fecho pelo registo `lens`, e retira o hook. Declarada no próprio `/round` (nota *Transitional*).
- `test_lens_checklists.py` prova o que o ficheiro diz e que nenhuma instrução viva aponta uma skill retirada. Não prova que o analista aplica as seis perspectivas; isso é a etapa `lens` (`test_coverage_lens.py`).
- A regra fixa da T19 prova que cada referência resolve (linha da SU que existe, `answers.md#…`, `enquadramento.md#…`, ficheiro em `_capture/` ou `inputs/`). Não prova que a linha citada trata a perspectiva. Isso fica para o revisor independente (`semantic_review.dimensions`). Sem revisão, a passagem fecha «por rever».
- A regra «revisor ≠ autor» compara nomes declarados (`performed_by.name` ≠ `lens_coverage.author.name`). Não prova que a sessão do revisor não tinha o contexto do autor. Isso vem das instruções do `/round` (F3.3).
- Ambiente: o contentor reiniciado perdeu `openpyxl` e `cffi`. Instalados de `requirements-dev.txt` e com `pip install cffi` antes da corrida. Não houve mudança de código.
