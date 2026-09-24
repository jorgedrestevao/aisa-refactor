# F4 — Desenho da autoria funcional e do primeiro desenho coerente

Plano: `../plan/05_FASES.md` F4; `../plan/02_CONTRATOS.md` §7 (contrato funcional) e §8 (bloqueios); `../plan/03_AGENTES_E_PACK.md` (autor/revisor); `../plan/08_HANDOFF.md` (rastreio requisito → FC → trabalho → prova). Contrato do kernel: `library/kernel/handoff-contract.md` → *Functional contract*, *Review policy*. Gate: T20–T24; o render recusa preencher uma regra em falta; uma referência ou aprovação desactualizada bloqueia a publicação final (`../plan/06_VALIDACAO.md`).

Objectivo: preencher a semântica que o render está proibido de inventar.

Decisões do mantenedor (2026-09-23), todas na opção recomendada:

| # | Decisão | Escolha |
| --- | --- | --- |
| Q1 | Onde trabalha o autor funcional | Um passo do `/blueprint`: depois de uma versão do desenho, o mesmo comando escreve os contratos funcionais (`FC-NNNN`) do âmbito, com rascunho, revisão e autorização. Nenhum comando nem pipeline novo |
| Q2 | Como se publica `_design/functional-contracts.json` | Um motor próprio (`library/kernel/tools/functional.py`) valida e publica pelo coordenador (`operation.run`, com base e read-set), como o checkpoint da F2. Cada revisão fica imutável em `_design/history/`. As seis autoridades continuam seis; `_design/` já é guardado e não é rascunhável |
| Q3 | Onde fica a autorização do dono | Um bloco `D-NNN` em `decisions.md` que lista cada FC autorizado com a revisão e o `sha256` do item; o FC aponta para o `D-NNN`. Se o item muda, a autorização deixa de valer (T24). Só o dono, por `AskUserQuestion`; um agente nunca autoriza |
| Q4 | A quem o render devolve um detalhe funcional em falta | A um dono novo, `functional`, acrescentado ao conjunto de donos da classe 3 (*open work item*) do `render-contract.md`. Não é uma classe nova |
| Q5 | Quem revê um FC antes de ir ao dono | Um revisor próprio, o subagente `fc-reviewer` (Read/Grep/Glob, contexto novo, uma chamada por revisão publicada), com o contrato de achados do plano 03 |
| Q6 | Como se detecta a contradição desenho ↔ FC (T21) | O motor compara as facetas estruturadas que os dois declaram sobre o mesmo campo ou entidade; uma divergência é um conflito visível (linha `Conflicted`) e bloqueia a publicação afectada até reconciliar. O texto livre fica para o revisor. O desenho aponta `fc_refs` e não repete regras |

## 0. Subagentes e paralelismo — avaliados antes de definidos

Critério: README → *Regras de execução*; `library/kernel/orchestration.md` → *When a subagent is justified*.

| Uso em F4 | Precisa do contexto de quem lança? | O detalhe volta a ser preciso? | Benefício | Veredicto |
| --- | --- | --- | --- | --- |
| Autor funcional (passo do `/blueprint`) | sim: SU, decisões, desenho, fontes | sim: os FC são o produto | — | **inline** |
| Revisor do FC (`fc-reviewer`) | não: tem de **não** ter o contexto do autor | não: voltam só os achados | independência autor/revisor (plano 03; *Review policy*) | **subagente**, 1 chamada sequencial por revisão publicada do conjunto de FC |
| Autorização do dono | — | — | não é trabalho de agente: é o dono, por `AskUserQuestion` | **nenhum subagente** |
| Verificação desenho ↔ FC | — | — | mecânica, no motor | **nenhum subagente** |

Nenhum paralelismo: o revisor lê o que o autor publicou.

## 1. O artefacto e o motor (Q2)

`_design/functional-contracts.json` (`handoff-functional/1`) é a autoridade do comportamento TO-BE detalhado (`handoff-contract.md` → *Authorities*). Publica-o apenas `functional.py`, pelo coordenador:

- `functional.py draft --engagement <slug>` — escreve em `_drafts/<FCDRAFT-id>/functional-contracts.json` a cópia da revisão corrente (ou um esqueleto), com a base registada. O autor edita a cópia; nunca o ficheiro publicado.
- `functional.py check --engagement <slug> [--draft <id>]` — valida sem escrever, com resposta estruturada (`handoff-response/1`).
- `functional.py publish --engagement <slug> --draft <id>` — numa operação: a revisão nova em `_design/functional-contracts.json` e a cópia imutável em `_design/history/functional-contracts.r<NNNN>.json`, com base e read-set como pré-condição (`STALE_INPUT`), e recibo em `_ops/`.
- `functional.py show --engagement <slug> [--json]` — o estado por FC: revisão, completude, autorização (actual, desactualizada ou em falta), conflitos com o desenho.

Regras de publicação (fail-closed, `INTEGRITY_FAILURE`):

- o schema, incluindo o motivo não vazio de cada `not_applicable`;
- ids `FC-NNNN` e `J-NNNN` nunca reutilizados (`retired_ids`); a revisão sobe sempre uma unidade;
- as referências resolvem: `requirement_refs` a linhas da SU que existem, `architecture_refs` a chaves do desenho da versão em `based_on`, `authorization_ref` a um bloco `D-NNN` que existe (ou `null`);
- nenhum FC redefine um campo: `inputs[].field_ref` aponta `<record_authority.key>.<campo>` do desenho.

**Completude** (T20) — não recusa a publicação, dá **`BLOCKING_GAP`** no âmbito afectado, e o FC fica publicado mas não autorizável:

- `rule`, `acceptance_examples`, `actors`, `trigger`, `postconditions` e `exceptions` presentes, ou em `not_applicable` com motivo;
- num FC com cálculo, exemplos positivo, negativo e de limite, com unidades e arredondamento; um cálculo sem regra de arredondamento é lacuna, nunca um valor escolhido;
- um parâmetro por escolher tem envelope, dono e teste de aceitação (`delegated_choices`), ou é bloqueio;
- uma pergunta aberta `blocks_scope` ou `blocks_all` em `open_refs` bloqueia o âmbito do FC.

O schema ganha, de forma aditiva e sem mudar de versão, o que o contrato já pede e o F1 não congelou: `inputs[].values`, `inputs[].default` (autorizado, com `default_ref`), `inputs[].validation`, `acceptance_examples[].kind` (`positive` · `negative` · `boundary`), `authorization` (`{ref, revision, sha256}`) e `conflicts`. Um leitor antigo preserva o que não conhece (`handoff-contract.md` → *Identifiers and revisions*).

## 2. Autorização (Q3; T22, T24; item 6 do plano)

- O dono autoriza por `AskUserQuestion`. O `/blueprint` escreve então **um** bloco em `decisions.md`, pelo protocolo *Writing an authority*:

  ```markdown
  ## D-NNN — Contratos funcionais autorizados (functional-contracts r<NNNN>)

  - **Authorizes**: FC-0001 (sha256 <64 hex>) · FC-0002 (sha256 <64 hex>)
  - **Revision**: r<NNNN>
  - **Scope**: <SCOPE ou jornada>
  - **Validated by**: owner (<papel do owner_role dos FC>, via AskUserQuestion)
  - **Timestamp**: <ISO-8601>
  ```

  A linha `D-NNN` correspondente entra na SU (regra do registo de decisão de `states.md`). O `sha256` é calculado pelo motor sobre o item normalizado, nunca à mão.
- **T24.** Um FC está autorizado só enquanto o `sha256` do seu item corrente é igual ao que o bloco lista. Se o item muda, a autorização passa a *desactualizada*: a da revisão antiga não cobre a nova, e o motor diz qual FC e desde que revisão. Um FC que não mudou mantém a autorização (só reabre o que depende da mudança).
- **T22.** Autorizar um FC `authorized_to_be` não confirma nenhuma premissa AS-IS. As linhas `Assumed` que o FC cita continuam `Assumed`; o motor nunca promove um estado da SU a partir de uma autorização, e o `show` lista as premissas assumidas de que o FC depende.
- **Item 6.** O `Validated by` tem de nomear um papel humano, e não um agente nem uma persona. O motor recusa um bloco de autorização de FC em que o validador é `executor`, uma persona do conselho ou um revisor. `[ÂMBITO AUTORIZADO]` não se aplica a FC. Nas fixtures, as autorizações são sintéticas e dizem-no (`Validated by: owner (dados de teste)`).

## 3. Coerência desenho ↔ FC (Q6; T21)

`functional.py` compara, por `field_ref`, as facetas que o desenho e o FC declaram de forma estruturada:

| Faceta | No desenho (`architecture.record_authority[].fields[]`) | No FC |
| --- | --- | --- |
| obrigatoriedade | `required` | `inputs[].required` |
| valores permitidos | `values` | `inputs[].values` |
| valor por omissão | `default` | `inputs[].default` |
| tipo | `type` | `inputs[].type` (quando declarado) |
| calculado | `computed: true` | um FC que escreve o campo tem `rule` |

**Nota de implementação (F4.3).** A faceta *calculado* não é comparada pelo motor: um FC pode ler um campo calculado como entrada legítima, e distinguir isso de uma contradição exige leitura. Fica com o `fc-reviewer`. As outras quatro são comparadas.

Uma divergência:

- é um conflito `FC_BLUEPRINT_CONFLICT` com os dois lados e os seus localizadores;
- o `/blueprint` escreve-a como linha `Conflicted` (`partes = desenho∧contrato funcional`), sem escolher uma versão;
- bloqueia a autorização do FC afectado e a aprovação da versão do desenho até reconciliar: um dos dois muda, ou o dono decide.

O desenho não repete regras: uma linha pode levar `fc_refs`, e o texto de uma regra dentro do desenho é achado do revisor. O que não é faceta estruturada fica para o `fc-reviewer`.

## 4. O passo funcional do `/blueprint` (Q1, Q5)

Depois do passo 13 (versão escrita e verificada):

1. **Rascunho** — `functional.py draft`. O autor (inline) escreve os FC do âmbito autorizado, a partir da SU, das decisões e do desenho:
   - uma jornada com o seu `J-NNNN`;
   - dados por `field_ref`;
   - automação, com gatilho, repetição e idempotência;
   - recuperação;
   - aceitação.

   Um âmbito sem interface humana não deve nenhum ecrã (T37).
2. **Publicação** — `functional.py publish` (a revisão fica `draft`/`received` por FC).
3. **Revisão** — uma chamada ao `fc-reviewer`, com contexto novo e só caminhos (a revisão publicada, o desenho, a SU e as decisões). Devolve achados: alvo, gravidade, premissa/evidência, cenário de falha, condição de fecho e a cobertura da revisão. Cada achado recebe uma disposição (*Review policy*): aceite e corrigido numa revisão nova, rejeitado com evidência, delegado com envelope, escalado ao dono, ou adiado com o impacto.
4. **Autorização** — só de FC completos, sem conflito e revistos sobre a revisão corrente. O pedido vai ao dono por `AskUserQuestion`, e o bloco é escrito conforme §2.

## 5. Render (Q4; T23; publicação final)

- O `implementation-spec` e o *solution blueprint* lêem o comportamento dos FC autorizados, e nunca da prosa da síntese.
- Um slot funcional sem FC, ou um FC com `BLOCKING_GAP` no campo que o slot pede, é uma entrada em `render-gaps.md` de classe 3 com `owner: functional`, com o FC e o campo em falta. O renderer não escreve o valor.
- A publicação final de um deliverable que cita um FC cuja autorização está desactualizada, ou um desenho cuja aprovação está desactualizada, fica bloqueada, com a razão. Rascunhos e pré-visualizações continuam permitidos.

## 6. Percurso de fixture

`fx-hv1-02` (pedido de equipamento) dá o percurso pequeno:

- **FC-0001**, submeter um pedido sem duplicação: jornada, dados, automação, idempotência, recuperação e aceitação;
- **FC-0002**, calcular o valor do pedido, com `BLOCKING_GAP` enquanto a regra de arredondamento (U-001) não for escolhida.

`fx-hv1-04` (headless) prova que um âmbito sem interface não deve ecrãs. As autorizações são sintéticas e identificadas como dados de teste.

## 7. Incrementos

| Inc. | Conteúdo | Testes |
| --- | --- | --- |
| F4.1 | `functional.py` (draft, check, publish, show), schema aditivo, completude → `BLOCKING_GAP`; contrato no `handoff-contract.md` | T20; integridade; ids; `STALE_INPUT`; histórico imutável |
| F4.2 | Autorização por `D-NNN` com `sha256` por item; validador humano; premissas assumidas não promovidas | T22, T24, item 6 |
| F4.3 | Coerência desenho ↔ FC por facetas; `fc_refs`; conflito → `Conflicted` e bloqueio | T21 |
| F4.4 | Passo funcional do `/blueprint` + agente `fc-reviewer` | contrato textual; revisor ≠ autor |
| F4.5 | Render: slots funcionais pelos FC; `owner: functional`; publicação final bloqueada por referência ou aprovação desactualizada | T23; gate do render |
| F4.6 | Percurso `fx-hv1-02` / `fx-hv1-04`, relatório e gate | T20–T24 de ponta a ponta |

A tabela *What F1 froze and what comes later* do `handoff-contract.md` põe o `FC` em F5 e o plano de registo (05) em F4. Vale o plano: F4.1 corrige a tabela.
