# Relatório — pacote de handoff `f8-r3-fx02` (R3-r0002)

Pasta lida na íntegra (52 ficheiros indexados em `handoff-index.json`, todos com sha256 conferido por script — nenhum mismatch, nenhum ficheiro em falta face ao índice). Nada lido fora da pasta.

## 1. Âmbito, exclusões, decisões autorizadas

**Dentro**: pedido, aprovação e passagem a compras de equipamento informático (`inputs/pedido.md`, `shared-understanding.md#C-008`). Plataforma Power Platform imposta pelo director de SI, deliberação DSI-SINT-07 (`C-001`, rota `platform-constrained`, `_state.json.workflow`).

**Fora**: gestão de stock e recepção física (`C-008`, `enquadramento.md#T7`).

**Decisão adoptada**: `decisions.md#D-002` — O-002, app orientada a registos (model-driven) sobre Dataverse. `D-001` fechou o frame com **override**: `X-001` (caminho urgente salta aprovação financeira?) ficou Conflicted e crítico, avançado mesmo assim por decisão do dono — "fecha antes de qualquer entrega final que dependa dele" (ainda não fechou).

**Quem autorizou o quê**: `D-001` — dono (director de SI, via AskUserQuestion) aprova o frame com override de `X-001`. `D-002` — dono escolhe O-002 por custo (30–38 vs 40–50 dias) e por acesso móvel não confirmado como necessário (`U-002`). **`D-002` tem `Sponsor confirmation: pending — ainda não confirmado`** — a decisão em si não está confirmada pelo dono no estado em que o pacote foi cortado.

**O pacote prova corresponder ao âmbito autorizado? Não.** O próprio `handoff-index.json` declara:
```
"readiness": {"delivery": "blocked", "ready": false}
"delivery_level": "preliminary"
"receiver_acceptance": null
"blueprint_approval": "missing"
```
com 6 bloqueios de gate (`BLOCKS_ALL_OPEN` ×1, `PROOF_WITHOUT_WORK` ×1, `UNLINKED_BLOCKING_QUESTION` ×4 — `scope-gate.json`). Os hashes conferem estruturalmente (nada foi adulterado), mas o conteúdo prova o oposto de "pronto": o índice lista as suas próprias lacunas como razão de bloqueio. Adicionalmente, `handoff-index.json#authorization_refs` só cita `decisions.md#D-002` — omite `D-001` (frame), a autoridade da rota (`C-001`) e qualquer aprovação de blueprint/scope, contra o que `library/kernel/handoff-contract.md` ("Release index") exige que o índice cite.

## 2. Ordem de construção

**Não existe inventário de trabalho no pacote.** Não há `_design/scope.json` (`SCOPE-NNNN`) nem `_design/work-packages.json` (`WP-NNNN`) — só os schemas, sem ficheiro de dados correspondente. `functional-state.json` mostra `revision: 0`, `items: {}`, `blueprint: ""` — zero `FC-NNNN` publicados. `scope-gate.json` e `trace.json` referenciam `_blueprint/ux-blueprint_v01.yaml`, que **não está no pacote**.

Sem `scope → FC → blueprint → WP → acceptance/proof` (a cadeia que `trace.py` exigiria), não há ordem de construção rastreável. O que existe é só a descrição textual da arquitectura de O-002 em `_design/candidates.json`.

Se tivesse de sequenciar só com isto, usaria a estrutura de fases genérica do pack (`craft/estimation-model.md`, não específica deste engagement): 0 — formalizar regras + resolver `U-006`/`U-011`/`U-012`/`U-002`/`U-013` (as 4 condições de `D-002`); 1 — camada de dados; 2 — integração ERP-X; 3 — ecrãs + fluxo de aprovação; 7 — UAT com submissão concorrente. **Isto é inventado a partir de craft genérico do pack — não é um plano deste engagement.**

## 3. Jornada e caminho de falha

**Jornada feliz**: requerente submete linhas (qtd × preço + IVA, `C-005`); sistema calcula total com arredondamento só no total, meio-para-cima (`C-007`); se ≤ 5.000€ vai só à chefia (nunca a própria, `M-1`); acima do limiar vai também à direcção financeira; aprovado → compras regista/encomenda; registo de aprovação alimenta auditoria (mecanismo por desenhar, `U-006`). Caminho urgente: avaria → vai direto a compras, chefia tem até fim do dia útil seguinte para validar, se não validar compras suspende a encomenda (`C-003`/`A-006`).

**Caminho de falha**: requerente reenvia por achar que não recebeu confirmação → duplicado (`R-001`→`R-003`). A revisão de arquitectura marcou isto `blocking` (`REV-0002.F01`): não é idempotente server-side, sofre corrida verificação-antes-de-escrita, e falha como erro de servidor que um retry ingénuo reencomenda — **nunca fechado no ledger**.

**O que teria de inventar**: mecanismo exacto de auditoria; mecanismo exacto de idempotência; critério de aceitação da jornada de excepção de reenvio; mecanismo de leitura ERP-X; todos os ecrãs concretos; mecanismo exacto de suspensão da encomenda urgente; resolução de `X-001`.

## 4. O que falta do cliente

- Despacho formal do limiar de 5.000€ (nunca entregue — só resposta verbal em `answers.md#U-005`).
- Volume de pedidos (`U-001`), tempo por passo (`U-009`), taxa horária carregada (`U-010`).
- Confirmação se o ERP-X expõe interface programável (`U-012`).
- Estado do tenant/ambientes Power Platform, políticas DLP, managed environments — nada no pacote.
- Envelope orçamental (`U-007`, `blocks_all`).
- `X-001` por fechar; confirmação de sponsor de `D-002` pendente; aprovação de blueprint inexistente; critério de sucesso (`U-008`); contexto móvel do requerente (`U-002`/`U-013`); licenciamento das 5 populações (`U-011`, VC-05).

## 5. Aceitação e operação

**Aceitação**: `handoff-index.json#receiver_acceptance: null`. Não há bloco `D-NNN — Aceitação do destinatário`. O único "proof obligation" nomeado em `D-002` é um "bounded pilot — UAT com submissão concorrente" (mitigação de `R-003`), sem financiamento avaliado e sem correr. Sem FC publicado, não há exemplos de aceitação a testar.

**Operação e recuperação**: o pacote não define nada específico deste engagement — nem operador nomeado, nem estratégia de ambiente, nem política de retenção Dataverse (fixada na criação do ambiente, não descoberta no go-live — aqui não há ambiente definido nenhum), nem plano de monitorização/alerta, nem rota de incidente. Os ficheiros de pack dão só conhecimento genérico da plataforma — nada aplicado a este engagement.

## 6. Lacunas

| id | lacuna | classe | defeito do pacote ou trabalho normal | justificação | ficheiro onde devia estar |
|---|---|---|---|---|---|
| L1 | Sem `_design/work-packages.json` nem `_design/scope.json` — zero WP publicados | blocks_all | defeito do pacote | sem inventário não há ordem de construção rastreável nenhuma | `_design/work-packages.json`, `_design/scope.json` |
| L2 | Sem `_design/functional-contracts.json` — `functional-state.json` revision 0, items {} | blocks_all | defeito do pacote | sem FC não há regra formalizada nem exemplo de aceitação | `_design/functional-contracts.json` |
| L3 | Blueprint `ux-blueprint_v01.yaml` citado por `scope-gate.json`/`trace.json` mas ausente do pacote | blocks_all | defeito do pacote | não dá para inspeccionar a obrigação de prova nem a estrutura de ecrãs citada | `_blueprint/ux-blueprint_v01.yaml` |
| L4 | `U-007` (envelope orçamental) aberto, bloqueia tudo | blocks_all | defeito do pacote | `scope-gate.json` marca `BLOCKS_ALL_OPEN` | `shared-understanding.md#U-007` |
| L5 | `X-001` Conflicted desde R-01, override em `D-001`, nunca fechado | blocks_scope | defeito do pacote | pacote avança para `D-002` com regra de negócio central aberta | `decisions.md#D-001`, `shared-understanding.md#X-001` |
| L6 | Confirmação de sponsor de `D-002`: "pending" | blocks_all | defeito do pacote | decisão de arquitectura entregue sem confirmação formal | `decisions.md#D-002` |
| L7 | `R-003` (duplicados) achado `blocking` (`REV-0002.F01`) nunca fechado no ledger — mecanismo exacto nunca nomeado | blocks_scope | defeito do pacote | achado de severidade blocking sem disposição de fecho | `shared-understanding.md#R-003` |
| L8 | `U-006` (mecanismo de auditoria) aberto, sem FC que o cite | blocks_scope | trabalho normal | `scope-gate.json` `UNLINKED_BLOCKING_QUESTION` | `shared-understanding.md#U-006` |
| L9 | `U-011` (licenciamento) aberto, VC-05 nunca corrida | blocks_scope | trabalho normal | risco de inviabilidade económica não descartado | `shared-understanding.md#U-011` |
| L10 | `U-012` (ERP-X expõe interface?) aberto | blocks_scope | trabalho normal | condiciona todo o mecanismo de integração | `shared-understanding.md#U-012` |
| L11 | Multiplicador 1.2× não corresponde à contagem de entidades (4 = banda Simple/1.0×) | implementation_proof | defeito do pacote | achado `REV-0005.F01`, nunca corrigido nem justificado | `_design/candidates.json#O-002.order_of_magnitude` |
| L12 | `handoff-index.json#authorization_refs` só cita `D-002` — omite `D-001`, `C-001`, aprovação de scope/blueprint | implementation_proof | defeito do pacote | inconsistente com `handoff-contract.md` §"Release index" | `handoff-index.json` |
| L13 | `scope_refs`/`exclusions` vazios no topo de `handoff-index.json` apesar de `candidates.json#exclusions` ter 3 exclusões justificadas | implementation_proof | defeito do pacote | inconsistência interna | `handoff-index.json` vs `_design/candidates.json#exclusions` |
| L14 | `inputs/nota-urgentes.md` datada 2026-10-01 — posterior a "hoje" e à resposta que a cita | implementation_proof | defeito do pacote | cronologia de evidência inconsistente | `inputs/nota-urgentes.md` vs `answers.md#C-003` |
| L15 | `U-002`/`U-013` (contexto móvel) aberto — decide reversão de `D-002` para O-001 (`TW-1`) | delegated_choice | trabalho normal | crítico porque pode inverter a própria decisão entregue | `shared-understanding.md#U-002`, `#U-013` |
| L16 | `U-014` (mecanismo exacto de suspensão) aberto | delegated_choice | trabalho normal | envelope bem definido | `shared-understanding.md#U-014` |

## 7. Perguntas bloqueantes ao autor

1. Onde está `ux-blueprint_v01.yaml`, citado mas ausente do pacote?
2. Qual é o envelope orçamental do projecto (`U-007`, bloqueia tudo)?
3. `X-001` fica definitivamente Conflicted e aceite por override, ou o dono vai responder?
4. A confirmação de sponsor de `D-002` já aconteceu depois deste corte?
5. Qual o mecanismo concreto de auditoria (`U-006`)?
6. A verificação VC-05 de licenciamento (`U-011`) foi feita? Resultado?
7. O ERP-X expõe interface programável (`U-012`)?
8. Qual o mecanismo exacto de idempotência dos duplicados (achado blocking, nunca fechado)?
9. O acesso é predominantemente móvel (`U-002`)? Se sim, reverte para O-001 (`TW-1`)?
10. Porque é que o multiplicador (1.2×) não bate com a contagem de entidades (4 = Simple/1.0×)?
11. Existe algum ambiente Power Platform já provisionado?
12. Qual o mecanismo exacto de suspensão da encomenda urgente (`U-014`)?
13. Qual o critério de sucesso do projecto (`U-008`)?

## 8. Ficheiros lidos e o que foi mais difícil de encontrar

Todos os 52 ficheiros do pacote. **Mais difícil de encontrar**: provar uma ausência — que não existe `_design/work-packages.json`, `_design/scope.json` nem `_blueprint/` no pacote, apesar de serem citados/esperados. Isso exigiu listar a árvore completa e confrontar contra o que o `handoff-contract.md` diz que deveria existir. Segundo mais difícil: a confirmação de sponsor "pending" está numa linha final discreta do bloco de decisão, fácil de passar por cima.
