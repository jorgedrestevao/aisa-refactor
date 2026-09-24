# F8 — Desenho dos pilotos adversariais e da aceitação do destinatário

Plano: `../plan/05_FASES.md` F8; `../plan/06_VALIDACAO.md` (protocolo de piloto, gates de qualidade, T43–T46); `../plan/08_HANDOFF.md` (revisão do destinatário, critério de fecho). Gate: T43–T46 e critérios quantitativos de 06 (confirmados pelo mantenedor na F0, antes de observar resultados). Uma simulação sozinha permite continuar experimental; não reivindica aceitação humana nem eficácia de produção.

Objectivo: demonstrar utilidade, continuidade e custo do perfil `handoff-v1` executado por uma sessão de agente, para além de schemas válidos.

Estado: **decidido** — Q1, Q2, Q4 e Q5 decididas pelo mantenedor (2026-09-24), na opção recomendada. Q3 decidida a seguir, a pedido de sugestão: o mantenedor, que tem experiência em Power Platform, é o destinatário real do T46; T45 fica fora.

## Ponto de partida (levantamento, 2026-09-24)

| Tema | O que existe | Lacuna para a F8 |
| --- | --- | --- |
| Percursos ponta a ponta | F5/F6: `test_hv1_vertical.py`, `test_hv1_release_paths.py` percorrem fx-hv1-02/04/05 pelos motores. **Os candidatos, pareceres e FC são escritos pelo teste a partir do `expected` da fixture** (limite declarado em `test_hv1_vertical.py`) | Nenhuma sessão de agente executou o perfil novo ponta a ponta. A qualidade do que o analista, o autor técnico e o `/blueprint` produzem nunca foi medida. É o núcleo da F8 |
| Destinatário (T43) | 3 ensaios simulados (subagente, só pacote) sobre o pacote da fx-hv1-02 escrito por teste (`F5/`, `F6/T43-ENSAIO.md`) | Nenhum ensaio sobre um pacote produzido por agente; nenhuma segunda leitura depois de uma ronda de correcção |
| Retoma a frio (T09) | `workflow.py resume` (F2.4), testes por processo | Nunca um agente sem histórico a retomar um engagement produzido por outro agente, a meio de uma tarefa |
| Mudança de premissa | `impact.py` (F7) sobre fixtures escritas por teste | Nenhuma medição de detecção e retrabalho numa execução real |
| Fixtures | 5 source packs sintéticos (F0) com `expected`. fx-hv1-03 traz a baseline B1–B5 (respostas do cliente às perguntas da fx-hv1-02) e as mudanças X1–X3 | Sem ficha do cliente (respostas) para fx-01, fx-04, fx-05; sem fonte de mudança a meio para fx-01, fx-02, fx-04, fx-05 |
| Medição | `docs/evolution/p8/compare.py` (`truth`/`check`/`leak`/`oracle`/`summary`; F0: adaptar como mecanismo da F8). O resultado de cada chamada de agente traz tokens, usos de ferramenta e duração | Comparação por E-item (`expected`, `must_not`) e verificação de retoma no perfil novo |
| T45 / T46 | — | Sem sandbox Power Platform autorizada nem equipa destinatária conhecidas nesta sessão |

Verificado nesta sessão, por sonda (subagentes de uma chamada, sem escrita):

- **Hooks disparam dentro de subagentes**: um `Write` em `projects/<x>/_work/` feito por um subagente foi recusado pelo `pre-authority-guard.py`. Fecha o item «a verificar» da F0 §7.
- Um subagente tem `Skill` (as skills carregam), mas **não tem `AskUserQuestion` nem `Agent`**: não pergunta ao utilizador e não lança os revisores que `/round`, `/frame`, `/options` e `/blueprint` definem como subagentes.
- Suite no arranque: full 111/111 (3033), stdlib 92/92 (2235), depois de instalar `cffi` no contentor (`pypdf` → `cryptography` sem `_cffi_backend`: ambiente, não código).

Achados menores, fora do gate: `CLAUDE.md` → *Key paths* nomeia `_graph/`, `_ops/`, `_migration/` como estado coordenado, mas o guarda cobre também `_work/` e `_design/` desde a F1.4 (deriva de documentação); `workflow.py resume` sobre um slug inexistente responde `INTEGRITY_FAILURE` «sem `_state.json`» em vez de «não existe».

## Decisões para o mantenedor

| # | Decisão | Escolha (decidida) | Alternativas rejeitadas |
| --- | --- | --- | --- |
| Q1 | Veículo de execução e papel do cliente | **A — executor = subagente novo por segmento; o orquestrador (esta sessão) faz de relé literal das perguntas ao cliente e dos revisores; cliente simulado** por fixture (ficha congelada antes da execução, só o que as fontes sustentam; o resto é «não sei»). Todas as aprovações ficam rotuladas como simuladas | **B** — sessões remotas independentes (`create_session`), o mantenedor responde a cada pergunta como cliente; estado dos engagements em branches de piloto. **C** — A nas execuções todas + uma execução B de realismo |
| Q2 | Matriz de execuções | **7 execuções**: solution-choice ×2 (fx-01, duas vezes com os mesmos inputs), platform-constrained ×3 (fx-02, fx-04 headless, fx-05 migração), change-impact ×2 (fx-03 sobre duas cópias da baseline aprovada produzida pela execução de fx-02) | 6 execuções (headless ou migração como extensão parcial de outra execução); fixture nova de solution-choice em vez da repetição |
| Q3 | Recursos reais | **O mantenedor é o destinatário real do T46**: revê um pacote congelado, só o pacote, com as seis perguntas de 08, e aceita ou recusa explicitamente (versão, âmbito, condições). Pacote de uma fixture sem ensaios anteriores (fx-01 ou fx-05), no fim do F8.3. Limite declarado: aceitação pelo mantenedor-autor do método, não por uma equipa externa. **T45 `not-run`**, declarado. Os restantes destinatários são simulados (subagente só com o pacote) | T46 sobre o pacote da fx-02 no fim do F8.2 (já leu a fixture em três ensaios); T45 com um ambiente do mantenedor; T45 e T46 ambos `not-run` |
| Q4 | Avaliação da qualidade (T44) | **Avaliação assistida documentada**: código confere o que é estrutural e o canário de contaminação; um avaliador independente (subagente com o `expected` e o estado final, sem o histórico do executor) dá veredicto por E-item com locators que o código verifica; o mantenedor valida a tabela | O mantenedor avalia tudo |
| Q5 | Orçamento e paragem | **Por etapas**: primeiro uma execução completa (fx-02), com o custo real medido; o mantenedor confirma as restantes com esse número | Correr as sete sem paragem; tecto de tokens fixado já |

Por omissão, sem pergunta (detalhe reversível; plano: «escolhe a alternativa mais simples compatível e documenta»): **sem comparação histórica com o runtime anterior** — exigiria correr o fluxo classic com personas sobre as mesmas fixtures, e o plano torna-a opcional; o custo compara-se pelas execuções obrigatórias por passagem (seis lentes → um analista). Evidências versionadas (§5). Correcção da deriva do `CLAUDE.md` no F8.1.

## 0. Subagentes — avaliados antes de definidos

Critério: README → *Regras de execução*; `library/kernel/orchestration.md` → *When a subagent is justified*.

| Uso na F8 | Precisa do contexto de quem lança? | O detalhe volta a ser preciso? | Veredicto |
| --- | --- | --- | --- |
| Executor de um segmento | **não, por definição**: a retoma sem histórico é o que se mede | não: o produto fica no repositório; volta o estado e os pedidos de relé | **subagente novo por segmento** |
| Revisores do runtime (`lens-coverage-reviewer`, `frame-reviewer`, `specialist-reviewer`, `fc-reviewer`) | não: a skill só lhes passa caminhos | só os achados, que a skill grava | **subagente**, lançado pelo orquestrador com o `subagent_type` e o prompt que a skill define, a pedido do executor (o executor não tem `Agent`) |
| Cliente simulado | não: só a ficha e as fontes | só as respostas, literais | **subagente**, uma instância por execução, continuada por `SendMessage` (memória das respostas já dadas; não vê o engagement) |
| Destinatário (T43) | não: só o pacote congelado | o relatório de lacunas é a evidência, e volta inteiro | **subagente**, uma chamada por leitura |
| Avaliador (T44) | não: `expected` + estado final | a tabela de veredictos, que o código verifica | **subagente**, uma chamada por execução |
| Relé, run-log, snapshots, medições | sim: estado da execução | sim | **na sessão** (código e orquestração) |
| Fichas do cliente, fontes de mudança, ferramentas de avaliação | sim: decisões da F8 | sim | **na sessão** |

O orquestrador conhece os `expected`. Por isso não escreve no engagement, não compõe respostas nem achados, e todo o relé fica no run-log, literal e auditável.

## 1. Papéis e isolamento

| Papel | Vê | Não vê |
| --- | --- | --- |
| Executor | o repositório, as fontes da fixture em `inputs/`, o protocolo | `scenario.json`, `docs/handoff-v1/`, fichas de avaliação, histórico de outros segmentos |
| Cliente simulado | fontes da fixture + ficha do cliente (papel, autoridade, respostas congeladas com a fonte de cada uma) | `expected`, o engagement |
| Revisores | o que a skill lhes passa | o resto |
| Destinatário | só o pacote congelado, numa pasta neutra | tudo o resto |
| Avaliador | `scenario.json` + estado final e pacote | histórico do executor |

O isolamento dos ficheiros é por instrução (os agentes podem ler o disco). Compensação: **canário de contaminação** — o código procura no engagement frases que só existem no `expected` (e não nas fontes); uma ocorrência invalida a execução.

**Relé** (Q1-A). Quando uma skill manda perguntar (`AskUserQuestion`) ou lançar um subagente (`Agent`), o executor pára e devolve um pedido estruturado (tipo, pergunta com as opções que a skill define, ou `subagent_type` e prompt). O orquestrador entrega-o ao cliente simulado ou lança o revisor e devolve a resposta **literal** por `SendMessage`. O executor nunca infere a resposta; sem resposta, o tema fica aberto, como `CLAUDE.md` já manda para um subagente. Aprovações: `validated-by` leva o papel e «cliente simulado F8»; o bloco de aceitação do release leva `**Simulated**`.

## 2. Protocolo por execução (06 → *Protocolo de piloto*)

Segmentos. Cada um começa com um executor novo, que corre primeiro `/resume` e declara o que reconstruiu (retoma a frio medida em cada fronteira):

| Segmento | Trabalho |
| --- | --- |
| S1 | `/start` (respostas do cliente por relé; fontes entregues em `inputs/`), `/capture`, `/round` e `/answer` até ao fecho da Discovery |
| S2 | `/frame` (revisor), `/options` (autor, router, especialistas, chairman); `/premortem`/`/simulate` só se a skill os pedir |
| S3 | `/decide` (o cliente escolhe), `/synthesize`, `/blueprint` com contratos funcionais, `fc-reviewer` e autorização |
| S4 | âmbito e inventário, `/render --all`, `release.py build` |

Em cada execução:

1. **Interrupção a meio de uma tarefa**, num ponto fixado no cartão da execução antes de correr (varia entre execuções: rascunho da passagem por publicar; candidatos publicados antes dos pareceres; FC em rascunho; render a meio). O executor pára nesse ponto e é descartado; um executor novo retoma. Em duas execuções a interrupção é dura (`TaskStop` sem ponto combinado).
2. **Mudança material injectada** depois do S3: uma fonte nova entregue pelo cliente (fx-01, fx-02, fx-04, fx-05: redigidas no F8.1 com o resultado esperado). Mede-se detecção (`impact.py stale`, `/answer` passo 7) e retrabalho (republicações, reautorizações, itens não afectados preservados).
3. **Congelar o release**; o destinatário recebe só o pacote e responde às seis perguntas de 08 → *Revisão de destinatário*, com lacunas `blocks_all` · `blocks_scope` · `delegated_choice` · `implementation_proof`.
4. **Uma ronda de correcção**: o autor (executor novo) responde por revisão canónica; novo release; um destinatário novo relê. Conta-se o que fica sem resposta.
5. **Avaliação** (Q4) e registo das perguntas essenciais, contradições, exclusões e escolhas delegadas.

Change-impact (fx-03): parte de uma cópia da baseline aprovada da execução de fx-02 (release congelado + aprovação sintética B5), entra pela reabertura da rota (`change-impact`), recebe X1–X3 e percorre S3–S4 com a mesma interrupção, destinatário e avaliação.

## 3. Medições

| Dimensão | Como | Critério de 06 |
| --- | --- | --- |
| Qualidade | avaliador + código por E-item: cumprido · violado (`must_not`) · ausente, com locator | cobertura material satisfeita; zero confirmação sem evidência e zero aprovação inventada |
| Continuidade | em cada fronteira: `compare.py truth` antes; o que o executor novo declara depois de `/resume` contra essa verdade (autorizações, perguntas materiais, bloqueios, próxima acção) | 100% das retomas preservam autorizações e perguntas materiais |
| Mudança | dependentes esperados stale; não afectados intactos; retrabalho contado | invalidação selectiva (T41) sem reabertura indevida (T42) |
| Destinatário | lacunas por classe; essenciais sem resposta após uma ronda | zero essenciais sem resposta ou encaminhamento |
| Integridade | recusas dos guardas, pendências, `graph verify`, `release verify`, `trace`/`scope-gate` | zero bloqueios escondidos e zero contradições materiais abertas no pacote |
| Custo | chamadas de agente por papel, tokens, usos de ferramenta, duração; execuções obrigatórias por passagem | secundário; qualidade passa e custo piora → continua experimental; custo melhora e qualidade falha → NO-GO |

## 4. Gate

| Teste | Evidência prevista | Rótulo |
| --- | --- | --- |
| T43 | relatórios dos destinatários, antes e depois da ronda de correcção, por execução | simulado |
| T44 | tabelas de avaliação validadas pelo mantenedor | avaliação assistida |
| T45 | slice numa sandbox autorizada | `not-run`, por decisão (Q3) |
| T46 | bloco de aceitação real (`release.py acceptance-block`, sem `**Simulated**`) do mantenedor, sobre um pacote da fx-01 ou da fx-05 | real, com o limite de Q3 |
| Quantitativos de 06 | agregado das sete execuções | exploratório, não estatístico |

Causa sistémica → corrigir → repetir os cenários afectados; os resultados falhados ficam guardados.

## 5. Persistência

Cada execução corre em `projects/f8-<run>-<fixture>/` (raiz de runtime, fora do git). Depois de cada segmento, um snapshot completo (sintético) vai para `docs/handoff-v1/F8/execucoes/<run>/`, com o run-log (JSONL: segmento, pedidos e respostas do relé, usage de cada chamada) e o cartão da execução. Push a cada segmento: uma sessão nova recupera a execução copiando o snapshot de volta, sem esta conversa.

## 6. Incrementos

| Inc. | Trabalho | Prova |
| --- | --- | --- |
| F8.0 | Levantamento, desenho, decisões | este documento |
| F8.1 | Fichas do cliente; fontes de mudança e seu `expected`; protocolo e prompts do executor; relé e run-log; snapshots; `avaliar.py` (reutiliza `compare.py`) com testes; canário; deriva do `CLAUDE.md` | testes do avaliador e do canário; ensaio a seco de um segmento |
| F8.2 | Execução completa de fx-02 (S1–S4, interrupção, mudança, destinatário, correcção, avaliação) | run-log, snapshot, custo real → decisão do mantenedor (Q5) |
| F8.3 | Restantes execuções | idem |
| F8.4 | Correcções sistémicas e repetição dos cenários afectados | regressão full + stdlib |
| F8.5 | Relatório e gate | T43–T46 e quantitativos |
