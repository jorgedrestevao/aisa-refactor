# F5 — Desenho dos candidatos comuns, especialistas e primeiro percurso vertical

Plano: `../plan/05_FASES.md` F5; `../plan/03_AGENTES_E_PACK.md` (papéis e mandatos, selecção de especialistas, sequência de Options, contrato de tarefa, pack); `../plan/02_CONTRATOS.md` §5 (rotas); `../plan/08_HANDOFF.md` (revisão do destinatário). Gate: T25–T30 e o primeiro ensaio T43; todas as revisões referem a versão correcta; zero confirmação por maioria; um handoff incompleto é rotulado como tal (`../plan/06_VALIDACAO.md`).

Objectivo: provar o ciclo completo em escala pequena antes da expansão.

Decisões do mantenedor (2026-09-23), todas na opção recomendada (Q7–Q8 tomadas no início da F5.4):

| # | Decisão | Escolha |
| --- | --- | --- |
| Q1 | Como corre o `/options` | O arquitecto escreve os candidatos na sessão (inline — o detalhe é o produto) e publica-os com revisão; só depois um router explicável escolhe os revisores independentes (subagentes, contexto novo) que o risco pede. As personas deixam de ser lançadas |
| Q2 | Onde ficam candidatos e pareceres | Candidatos em `_design/candidates.json` (revisão + histórico imutável), pareceres em `_design/reviews/`, publicados pelo coordenador por um motor como o `functional.py`. Cada parecer guarda a revisão do candidato e o input set; um candidato novo torna o parecer antigo `stale`. O `options.md` continua a ser a projecção legível |
| Q3 | Forma dos especialistas | Um único agente `specialist-reviewer` (Read/Grep/Glob); papel, perguntas, inputs, conhecimento do pack e contrato de saída vêm no mandato publicado. O conteúdo de cada papel vive num ficheiro do kernel (`library/kernel/specialists.md`) |
| Q4 | Personas e `/retro` | As seis personas de Discovery são retiradas (sem consumidor), com cobertura registada. O `/retro` passa a escrever a memória por papel (analista, arquitecto, especialistas), com curadoria humana. O `solution-architect` fica como mandato do autor técnico |
| Q5 | Conhecimento do pack (T29) | O mandato publica as unidades do pack permitidas (caminho + `sha256` + versão do pack); o parecer devolve `sources_used` com as mesmas referências; o motor verifica que cada fonte usada estava no mandato e não mudou. Reusam-se os metadados existentes; um índice por competência fica para quando for preciso |
| Q6 | Primeiro ensaio T43 | Um pacote experimental da fixture `fx-hv1-02` (ficheiros + `sha256`, rotulado incompleto) e um subagente de contexto novo que só recebe os caminhos do pacote; perguntas bloqueantes e lacunas registadas no relatório. Julgamento assistido documentado; não vale como aceitação |
| Q7 | Memória das personas retiradas (F5.4) | Migrada por papel com `git mv` (história preservada): `business-analyst` + `operations-lead` → `analyst/` (ficheiros com o prefixo da persona de origem); `solution-architect` → `architect/`; `data-steward` → `data-integration/`; `compliance-officer` → `security-operation/`; `user-advocate` → `ux-process/`; `cfo-lens` → `cost-estimate/`. O `/retro` escreve nestas pastas |
| Q8 | Quem lê a memória por papel (F5.4) | Os papéis inline (analista em `/round`/`/frame`, arquitecto em `/options`) leem a sua pasta como ponteiro; um revisor especialista só a recebe se o mandato a listar em `knowledge_refs`, com `sha256` (mesma regra T29), e só a do seu papel |

## 0. Subagentes e paralelismo — avaliados antes de definidos

Critério: README → *Regras de execução*; `library/kernel/orchestration.md` → *When a subagent is justified*.

| Uso em F5 | Precisa do contexto de quem lança? | O detalhe volta a ser preciso? | Benefício | Veredicto |
| --- | --- | --- | --- | --- |
| Autor técnico (candidatos, `/options`) | sim: SU, frame, decisões, pack | sim: os candidatos são o produto | — | **inline** |
| Revisores escolhidos pelo router (`specialist-reviewer`, um por mandato) | não: têm de **não** ter o contexto do autor nem o de outros revisores (plano 03 → *Sequência*, passo 2) | não: voltam só os achados | independência autor/revisor e entre revisores | **subagentes**, um por mandato publicado |
| Paralelismo entre revisores | — | — | os mandatos leem a mesma revisão publicada e não dependem uns dos outros | **paralelo permitido** entre revisores do mesmo `C@r`; nunca com o autor, que publica antes |
| Ronda dialéctica (até 3 divergências × 2 chamadas) | não: cada lado recebe a tese do outro por caminho | não: volta *Concedo / Contesto / Síntese* | contestação localizada onde há desacordo material | **subagentes** (`specialist-reviewer` em modo antítese), limitados; o limite escala, nunca aceita |
| Síntese e disposição dos achados (`chairman-synthesis`) | sim: todos os pareceres e o contexto | sim: é a decisão a apresentar | — | **inline** |
| Destinatário do ensaio T43 | não: tem de ter **só** o pacote | não: voltam perguntas e lacunas | a medida do handoff é precisamente o contexto novo | **subagente**, uma chamada |
| As seis personas de Discovery, `/retro` com personas | — | — | sem consumidor depois de Q1 | **retiradas** (Q4) |

## 1. Candidatos publicados (Q2; T25, T27)

`library/kernel/tools/review.py` (motor novo, padrão do `functional.py`) publica `_design/candidates.json` (`handoff-candidates/1`) pelo coordenador, com histórico imutável em `_design/history/candidates.r<NNNN>.json`. Cada candidato `O-NNN`:

- a tecnologia e a forma (superfície e armazenamento);
- a classe de opção;
- a arquitectura de alto nível;
- a ordem de grandeza com a fonte declarada;
- riscos, reversibilidade e o que o bloqueia;
- as premissas (ids da SU) e as fontes.

Ao nível do conjunto ficam os critérios, as exclusões com motivo e a rota. Regras (fail-closed):

- ids `O-NNN` nunca reutilizados, revisão +1, referências que resolvem;
- **rota `platform-constrained`** (T27): todos os candidatos na plataforma imposta (`_state.json.workflow` / decisão de imposição), variações de arquitectura e implementação. Um candidato noutra plataforma é recusado. Não há mínimo de três, e um único candidato viável é admitido com o motivo;
- **rota `change-impact`**: os candidatos descrevem o delta, o raio de impacto e as decisões a reabrir;
- **rota `solution-choice`**: os candidatos realmente aplicáveis; uma lista reduzida exige motivo.

## 2. Router e mandatos (T28, T29; Q3, Q5)

- `library/kernel/specialists.md` é o dono único dos papéis (dados/integração, segurança/operação, UX/processo, custo/estimativa, revisor de arquitectura), dos gatilhos mínimos do plano 03 e do contrato de saída. A avaliação inicial dos riscos corre sempre, mesmo quando a resposta é «não aplicável».
- `review.py route` lê a rota, os candidatos publicados, os FC, as linhas abertas da SU e as marcas de risco, e aplica as regras. Devolve os papéis seleccionados, cada um com as questões e a razão (o gatilho e as linhas que o activaram), e os papéis não chamados com a justificação.
- `review.py mandate` publica o mandato **antes** de executar. O mandato leva:
  - `task_id`, `role`, `objective`, `scope_ids`, `questions`;
  - `input_refs` com `sha256`;
  - `candidate_revision`;
  - `knowledge_refs` (unidades do pack: caminho, `sha256`, versão do pack);
  - `output_contract`, `stop_conditions`, `budget`, `prohibited_actions`.

  Sem candidatos publicados, ou com um rascunho de candidatos aberto sobre a revisão corrente, o mandato é recusado (T25).

## 3. Pareceres, disposições e dialéctica (T26, T30; item 4 do plano)

- `review.py receive` valida o parecer e publica-o em `_design/reviews/REV-NNNN.json`:
  - o contrato de saída: `task_id`, `input_revision`, `coverage`, `findings` (alvo, gravidade, premissa/evidência, cenário de falha, condição de fecho), `assumptions`, `unanswered`, `recommended_actions`, `sources_used`;
  - o `input_revision` é o do mandato;
  - cada fonte usada está no mandato, com o mesmo `sha256` (T29).
- **T26**: um parecer cuja `candidate_revision` já não é a corrente é `stale`. Não fecha um achado da revisão actual, e revalida-se só o que o candidato novo afecta.
- **Disposições** (plano 03 passo 4; *Review policy*): aceite/corrigido, rejeitado com evidência, delegado com envelope, escalado, adiado com impacto. Ficam registadas pelo coordenador, e nunca se apaga uma opinião minoritária.
- **Item 4**: o `chairman-synthesis` em Options lê os pareceres publicados e não votos. A concordância não promove evidência (já em F1/F3), e cada achado tem disposição e condição de fecho.
- **T30**: uma divergência material abre uma ronda dialéctica com contador. Quando chega às 2 chamadas por divergência (máximo de 3 divergências) sem síntese aceite, fica `escalated`, e nunca aceite por esgotamento.

## 4. `/options` por rota (Q1, Q4)

1. O arquitecto (inline, mandato do `solution-architect`) escreve o rascunho dos candidatos → `review.py publish-candidates`.
2. `review.py route` → os mandatos publicados → um `specialist-reviewer` por mandato (subagentes, em paralelo entre si) → `review.py receive`.
3. `chairman-synthesis` (Options) dispõe os achados e abre a dialéctica limitada onde há divergência material. Se for preciso, o autor publica `C@r+1` e revalidam-se só os pareceres afectados.
4. `options.md` é projectado dos candidatos publicados e das disposições, fechado com a recomendação do aisa (que não é a decisão).

Saem: o lançamento das sete personas e a regra dos três candidatos nos hooks (`phase-completeness`, o aviso de fase), que passam a ler a rota. As seis personas de Discovery são retiradas; o `/retro` escreve a memória por papel.

## 5. Percurso vertical e ensaio T43 (Q6; itens 6–7)

- `fx-hv1-02` (plataforma imposta) é percorrida pelos motores:
  - captura e análise (F3), com o enquadramento;
  - candidatos por rota (T27), revisão pelo router e disposições;
  - decisão, desenho e FC (F4);
  - `implementation-spec` e estimativa pelos templates existentes, em modo de pré-visualização onde a autoridade falta.
- **Pacote experimental**: a lista dos ficheiros com `sha256`, rotulada `preliminary` e **incompleta**. O índice de release formal é da F6.
- **Ensaio T43**: um subagente de contexto novo recebe só os caminhos do pacote e tenta identificar o trabalho e os testes. As perguntas bloqueantes, as lacunas, as chamadas, o contexto e o retrabalho ficam registados no relatório. As lacunas sistémicas são corrigidas antes de se aumentar a cobertura.

## 6. Incrementos

| Inc. | Conteúdo | Testes |
| --- | --- | --- |
| F5.1 | `review.py` candidatos (draft/publish/show), schema `handoff-candidates/1`, regras por rota | T27; integridade; T25 (parte do motor) |
| F5.2 | `specialists.md`, `review.py route` e `mandate`, `knowledge_refs` | T28, T29 (mandato) |
| F5.3 | `review.py receive`, `stale`, disposições, dialéctica com contador; `chairman-synthesis` em Options | T26, T29 (parecer), T30 |
| F5.4 | `/options` reescrito por rota; agente `specialist-reviewer`; retirada das personas; `/retro` por papel; hooks por rota; texto normativo | contrato textual; hooks |
| F5.5 | Percurso vertical `fx-hv1-02`, pacote experimental, ensaio T43 (subagente) | percurso de ponta a ponta; registo do ensaio |
| F5.6 | Relatório e gate | T25–T30, T43 (primeiro ensaio) |
