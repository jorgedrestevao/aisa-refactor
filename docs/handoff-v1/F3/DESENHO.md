# F3 — Desenho da análise integrada e materialidade funcional

Plano: `../plan/05_FASES.md` F3, `../plan/03_AGENTES_E_PACK.md` (analista integrado, matriz de cobertura das lentes), `../plan/02_CONTRATOS.md` §6. Gate: T05–T08, T18, T19 e a fixture com arredondamento e valor factual ausente (`../plan/06_VALIDACAO.md`).

Decisões do mantenedor (2026-09-23), todas na opção recomendada:

| # | Decisão | Escolha |
| --- | --- | --- |
| Q1 | Forma da análise de Discovery | O `/round` corre **uma** análise integrada, que aplica as seis *checklists*. As *checklists* vivem num ficheiro do kernel, com o conteúdo das 6 skills de lente e sem duplicação. `/round <perspectiva>` aprofunda uma dimensão com o mesmo analista. As 6 skills de lente de Discovery saem em F3; os agentes-persona ficam até F5 |
| Q2 | Onde fica a cobertura e o que fecha a passagem | Na etapa `lens` do coverage (`_coverage/coverage_vNN.json`), publicada pelo coordenador. Seis dimensões, cada uma `assessed`, `gap` ou `not_applicable`, com referências e justificação. A passagem fecha com o registo válido e actual. Saem o `pre-lens-order-check` e a regra dos seis cabeçalhos |
| Q3 | T19, a revisão semântica | Um revisor independente (subagente de contexto novo) dá um veredicto por dimensão, registado no `semantic_review`. Há também uma regra fixa: as referências apontam linhas da SU ou localizadores, e um título não conta. Sem revisão, a passagem fecha como «cobertura por rever», com gate suave |
| Q5 | Ronda de antítese no `/frame` | Retirada: divergência de facto sem localizador → `Conflicted`; divergência de recomendação → o dono decide por `AskUserQuestion`. O limite da dialéctica (`orchestration.md`) continua a valer para o conselho de Options até F5 |
| Q4 | `/frame` | O analista integrado, em modo enquadramento, propõe; um revisor independente contesta; as regras de evidência do chairman mantêm-se. As seis personas deixam de ser lançadas. Os especialistas chegam com o router, em F5 |

## 0. Subagentes e paralelismo — avaliados antes de definidos

Critério do mantenedor (README → *Regras de execução*, estendido ao framework em 2026-09-23). Um subagente só se define quando reúne duas condições: a tarefa não precisa do contexto de quem a lança, e o detalhe dela não volta a ser preciso, só o veredicto. Na dúvida, corre inline.

| Uso em F3 | Precisa do contexto de quem lança? | O detalhe volta a ser preciso? | Benefício | Veredicto |
| --- | --- | --- | --- | --- |
| Análise integrada (`/round`, `/frame`) | sim: fontes, SU, decisões, enquadramento | sim: as linhas e a cobertura são o produto | — | **inline**, uma execução |
| Revisor semântico da cobertura (T19) | não: tem de **não** ter o contexto do autor | não: volta só o veredicto por dimensão | independência autor/revisor (03; T19) — o único benefício, e só o subagente o dá | **subagente**, 1 chamada sequencial por passagem |
| Revisor do enquadramento (`/frame`) | não, pela mesma razão | não: volta a lista de achados | independência numa decisão material (a frase aprovada) | **subagente**, 1 chamada sequencial |
| Seis personas em paralelo no `/frame` (antes de F3) | sim: recebiam excertos da SU montados pelo orquestrador | sim: o detalhe alimentava a síntese | nenhum que a análise integrada + revisor não dê | **retiradas** (Q4) |
| Ronda de antítese da dialéctica (2 chamadas por divergência) no `/frame` | sim: cada lado precisa das teses | sim: volta à síntese | baixo com dois intervenientes | **retirada** (Q5) |
| Conselho de `/options` (7 personas) e especialistas | — | — | — | fora de F3; avaliados em F5 pelo mesmo critério |

Nenhum paralelismo em F3: os dois revisores correm em sequência, depois do autor, porque revêem o que ele publicou.

**Inventário do framework actual** (levantamento de 2026-09-23 sobre skills, agentes, comandos e kernel). Os usos fora de F3 recebem aqui uma avaliação provisória; decide-os a fase dona, com o mantenedor:

| Onde | Hoje | Avaliação pelo critério | Fase dona |
| --- | --- | --- | --- |
| `/frame` | 6 personas em paralelo + antítese | falha o critério: contexto montado pelo orquestrador, e o detalhe alimenta a síntese | **F3** — retirado (Q4, Q5) |
| `/options` | 7 personas em paralelo + antítese | as personas falham o critério pela mesma razão. Passam: o arquitecto como **autor** (inline, porque o detalhe é o produto) e **revisores** independentes de candidatos já publicados (03 → *Sequência de Options*), escolhidos pelo router só onde um trigger dispara | F5 |
| `/decide --consult` | 1 `solution-architect` que revê a opção escolhida | passa: revisão independente de uma escolha já escrita; volta só o parecer | manter |
| `/retro` | 7 personas em paralelo a escrever diários | passa no critério (sem contexto da sessão; o detalhe vai para a memória das personas, não volta) — mas o benefício depende de as personas sobreviverem a F5 | F5 (com a retirada das personas) |
| Texto normativo | `orchestration.md` (*Council-independent mode*, *Why parallel*), `phases.md:101`, `glossary.md` (*Council*, *Mode*), `CLAUDE.md` princípio 4 | descreve o paralelismo como regra da fase, sem avaliação de benefício | F3.4 (enquadramento) e F5 (Options): o texto passa a dizer quando um subagente se justifica |

Nenhum motor novo. A cobertura entra no `coverage.py`, o único dono da conferência e da frescura, e publica pelo coordenador de F2. As escritas na SU seguem o protocolo *Writing an authority*.

## 1. Checklists (Q1)

`library/kernel/lens-checklists.md` é o dono único das seis perguntas centrais (03 → matriz) e da evidência de cobertura de cada lente. Para cada lente leva:

- as perguntas;
- os sinais das skills de lente de hoje;
- as regras próprias: `step_duration` em operações, `data_shape` em dados, varrimento de conflitos em governação (corre depois das seis), `funding_gate` e aritmética da *baseline* em financeiro.

A admissão de uma pergunta e o limiar de `Confirmed` não se repetem: apontam para `states.md`. Os sinais do pack (`lenses_config.<lente>.extra_signals`) continuam a ser pistas, não *checklist* obrigatória (`orchestration.md`). As 6 skills `lens-*` de Discovery são retiradas. `lens-technology` fica: é a lente de Options, encarnada pelo `solution-architect` (F5).

## 2. Etapa `lens` do coverage (Q2)

Uma etapa nova, sem alvo, como a `reconciliation`: vale o registo mais recente. O registo tem os campos de raiz de sempre (`source_review` e `coverage` como listas vazias) e mais:

```json
"lens_coverage": {
  "round": "R-02",
  "author": {"kind": "agent", "name": "analista integrado (/round)"},
  "dimensions": {
    "business":   {"status": "assessed",       "refs": ["C-012", "U-004"], "justification": "…"},
    "operations": {"status": "gap",            "refs": ["U-007"],          "justification": "…"},
    "user":       {"status": "not_applicable", "refs": [],                 "justification": "sem utilizador humano: integração headless"},
    "data": {…}, "governance": {…}, "financial": {…}
  },
  "conflict_scan": {"refs": ["X-002"], "note": "…"}
}
```

Regras fixas, a parte determinística da T19:

- as seis dimensões estão todas presentes; o estado é um dos três;
- a justificação nunca é vazia, e `not_applicable` sem motivo é inválido (T07);
- `assessed` exige pelo menos uma referência resolvível: um id da SU que existe, ou um localizador das classes do limiar. Um título, uma secção de `lens-outputs` ou uma referência que não resolve **não contam**;
- `gap` exige uma referência a uma pergunta aberta (`U-`/`X-`/`R-`) ou a uma obrigação de prova;
- o `conflict_scan` é obrigatório. Pode não ter referências, mas nesse caso leva a nota que o diz.

A revisão semântica (`semantic_review`) segue o esquema de §4.7, com `dimensions`: por dimensão, `treated`, `not_treated` ou `not_applicable_ok`, e uma nota. Um `not_treated` é um achado, isto é, uma lacuna visível (T19). O revisor tem de ser diferente do autor (`performed_by.name` ≠ `author.name`). Sem revisão concluída, o registo é válido, mas «por rever».

`coverage_state(eng, "lens")`:

- frescura pela base: a impressão digital semântica da SU e as fontes;
- `coverage` fica `gaps` quando há dimensões em `gap` ou um `not_treated`;
- `eligible` (fecho revisto) exige registo válido, actual e revisão concluída.

A passagem **fecha** com o registo válido e actual para a passagem corrente. Sem revisão, fecha à mesma, mas marcada «cobertura por rever» (gate suave).

## 3. `/round` (Q1, Q2, Q3)

1. Tarefa no checkpoint (F2.3) e um rascunho da SU.
2. O analista integrado aplica as seis *checklists* às fontes. Escreve as linhas na cópia (admissão de `states.md`) e publica.
3. Monta o rascunho do registo `lens`.
4. Um **revisor independente**, um subagente com contexto novo que recebe só a SU publicada, o rascunho do registo e as *checklists*, devolve o veredicto por dimensão.
5. `coverage.py finalize`.
6. A passagem fecha se o registo for válido e actual.

`/round <perspectiva>` refaz uma dimensão e produz um registo novo, que herda as outras cinco do anterior. O revisor semântico corre **uma vez**, quando a passagem fecha, sobre o registo que a fecha — não a cada perspectiva isolada: rever registos intermédios que o seguinte substitui não traz benefício (§0). A contagem de passagens e o `round_in_progress` mantêm-se. Saem o `round_lenses` e o `pre-lens-order-check`. O dashboard lê as perspectivas corridas a partir do registo `lens`.

## 4. `/frame` (Q4)

1. O analista integrado, em modo enquadramento, propõe `frame.md` e as linhas.
2. Um revisor independente contesta, com o mesmo contrato de achados de 03 (alvo, gravidade, evidência, condição de fecho).
3. A síntese aplica as regras do chairman: a concordância não é evidência, e uma divergência factual sem localizador vai para `Conflicted`.

O que não muda: o gate, o teste de sobrevivência e a aprovação com impressão digital por `AskUserQuestion`. `phase-completeness` e o `phase-gate-check` deixam de exigir seis personas e seis lentes: o critério de Discovery passa a ser a cobertura `lens`.

## 5. AS-IS / TO-BE, captura e resposta

Os marcadores `observed_as_is`, `proposed_to_be` e `authorized_to_be` já existem desde F1, na coluna `âmbito`. O analista escreve-os, e o árbitro verifica a presença.

A captura admite `PM-U` por tipo de pergunta, com impacto, pela mesma regra de `states.md`. A resposta mantém os tipos de pergunta.

## 6. Incrementos

| Inc. | Conteúdo | Testes |
| --- | --- | --- |
| F3.1 | Etapa `lens` no coverage + contrato (`coverage-contract.md`) | T18, T19 (parte fixa), T07 N/A |
| F3.2 | `lens-checklists.md` + retirada das 6 skills de lente | contratos das checklists (`step_duration`, `data_shape`, conflitos, `funding_gate`) |
| F3.3 | `/round` integrado + revisor + fecho por cobertura; dashboard; retirada do `pre-lens-order-check` | T18, T19, testes adaptados |
| F3.4 | `/frame` integrado + revisor; `phase-completeness`/`phase-gate-check` por perfil | framing sem seis personas |
| F3.5 | Captura (PM-U), `/status`; fixture `fx-hv1-02` de ponta a ponta (arredondamento, valor ausente) | T05, T06, T08, fixture do gate |
| F3.6 | Relatório e gate | T05–T08, T18, T19 |
