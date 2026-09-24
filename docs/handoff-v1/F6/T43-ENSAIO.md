# T43 — 3.º ensaio do destinatário em contexto novo (F6.6)

Estado: **ensaio assistido documentado, simulado**. Não é aceitação (plano 06; plano 08 → *Critério de fecho*). Ensaios anteriores: `../F5/T43-ENSAIO.md`.

## 1. Montagem

| Item | Valor |
| --- | --- |
| Pacote | `docs/handoff-v1/F6/pacote-fx-hv1-02/`. Release r0001 gerado por `release.py build`: 39 ficheiros + `handoff-index.json` |
| Gerado por | `python .claude/tests/test_hv1_release_paths.py --write <pasta>`. Percurso da F5 mais âmbito (D-005), inventário (WP-0001, WP-0002) e pré-visualizações da spec e da estimativa, que só projectam o inventário e estão rotuladas |
| Código / pack | commit `51bb79e` (F6.6 parte 1; lido de `handoff-index.json`) · `pp` 1.10.0 |
| Nível | `preliminary`, **calculado**. Motivos: «1 achado de rastreabilidade» (C-001 sem contrato — N1) e «gate de âmbito bloqueado» (`valor_total` obrigatório sem produtor — N4) |
| Destinatário | subagente `general-purpose`, uma chamada, contexto novo, com o mesmo pedido dos ensaios anteriores |
| Custo | 13 usos de ferramenta · ~110 k tokens · 137,6 s |

## 2. Resultado

**17 lacunas**: 11 defeitos do handoff (`blocks_scope` 9, `blocks_all` 2), 1 `blocks_all` de compromisso (estimativa por calcular) e 5 de trabalho normal (`delegated_choice` 4, `implementation_proof` 1). **5 perguntas bloqueantes.**

**O que a F6 resolveu, visto pelo destinatário:**

- **Integridade verificada sem correr o motor.** O destinatário recalculou as impressões digitais do D-004 pelo contrato e conferiu o sha do D-003 (N2) e os 39 hashes (T39).
- **O âmbito e as suas lacunas vêm declarados.** O destinatário leu o SCOPE-0001 no `scope.json`. Encontrou C-001 (passagem a compras) sem contrato e o `valor_total` sem produtor directamente em `trace.json` e `scope-gate.json` (N1 e N4). Nos ensaios da F5 teve de cruzar as entradas à mão para os encontrar.
- **O inventário substitui a ordem inferida.** A ordem de construção vem do `depends_on` (WP-0001 → WP-0002). A estimativa diz que o esforço está «por calcular», sem número inventado.
- **O aviso N3 foi lido**: o actor «Chefia» não existe no desenho (`ACTOR_NOT_IN_DESIGN`).

## 3. Verificação das afirmações (na sessão, contra o pacote)

Confirmadas:

- `authorization_refs` só lista D-003 e D-004. O D-001 (imposição), o D-002 (escolha) e o D-005 (âmbito e exclusão) ficam de fora.
- O índice não tem `reviews_basis`, que o pacote experimental da F5 tinha (S4): é uma regressão do `release.py`.
- A U-002 (`blocks_scope`, limiar da direcção financeira) não está nos `open_refs` de nenhum FC nem excluída, por isso o gate não a vê.
- O D-005 tem a data sintética `2026-09-24T09:00Z`, e o `built_at` é o relógio real, `00:07Z`.

## 4. Classificação

### 4.1 Sistémicas (a corrigir)

| # | Lacuna (L- do destinatário) | Onde nasce | Correcção |
| --- | --- | --- | --- |
| R1 | `authorization_refs` não inclui as decisões de âmbito, de exclusão, de imposição e de escolha (L11) | `release.py build` só recolhe os blocos de autorização de FC e a aprovação do desenho | incluir `scope.authorized_by`, cada `excludes[].authorization_ref`, a autoridade da rota e a decisão que escolheu o candidato |
| R2 | O índice perdeu `reviews_basis` (L11) | regressão do `release.py` face ao pacote da F5 (S4) | repor `reviews_basis` no índice |
| R3 | Uma pergunta `blocks_scope` aberta que nenhum FC referencia e que não está excluída não bloqueia (U-002; L03) | o gate só vê bloqueios através de `open_refs` ou de `blocks_all` | o gate reporta `UNLINKED_BLOCKING_QUESTION`: pergunta `blocks_scope` aberta, não estacionada, sem FC que a cite em `open_refs` e sem exclusão |
| R4 | Uma decisão datada depois do `built_at` passa sem aviso (L11) | o `build` não confronta as datas | registar a incoerência em `limitations`. No ensaio é artefacto da fixture (datas sintéticas), mas num engagement real é sinal de relógio ou registo errado |

### 4.2 Artefactos da fixture (repetidos dos ensaios da F5)

- A SU está incompleta: [C6], auditoria M5, retenção D3 e o ERP-X ficam de fora (L04, L08, L09).
- O desenho é mínimo: não tem campos de requerente, decisor ou equipa, nem entidade de linha, nem A7/A8/A10 (L06, L10). O D-003 aprovou-o porque o teste escreveu a aprovação.
- O fluxo urgente e a passagem a compras não têm FC (L01, L05). O C-001 sem contrato é o N1 a funcionar: o pacote declara a falta.
- O cabeçalho da SU diz «Discovery».

### 4.3 Esperadas e bem classificadas

- L02 (N4) e L12 (estimativa por calcular) aparecem como motivos do nível `preliminary`.
- L13–L17 são trabalho normal dentro de um envelope.

## 5. Evolução nos três ensaios

| Ensaio | Pacote | Lacunas | Perguntas bloqueantes sobre verificar o próprio pacote |
| --- | --- | --- | --- |
| 1.º (F5.5) | experimental, 19 ficheiros | 17 | 2 de 4 (âmbito indefinido, autorização ilegível) |
| 2.º (F5.5b) | experimental, 28 ficheiros | 16 | 0 de 4 |
| 3.º (F6.6) | release r0001, 39 ficheiros, nível calculado | 17 | 1 de 5 (R1/R4: se este é o release do âmbito autorizado) |

O número de lacunas não desce porque a fixture continua pequena, e o destinatário lê cada vez mais fundo. Mudou a natureza das lacunas. As lacunas de estrutura do handoff passaram a vir declaradas no próprio pacote (N1, N4, estimativa por calcular). As que restam são de conteúdo da fixture, mais R1–R4.

## 6. Relatório do destinatário (transcrição; conteúdo integral, formatação simplificada)

<details><summary>Relatório devolvido pelo subagente</summary>

```
## 1. Âmbito, exclusões, decisões
- Âmbito: SCOPE-0001 (_design/scope.json, handoff-index.json#scope_definition). Inclui a submissão (J-0001), a aprovação com segregação (J-0003) e o âmbito declarado C-001 («pedido, aprovação e passagem a compras»). Autorizado por D-005.
- Exclusão: FC-0002, o cálculo do valor, até haver regra de arredondamento (U-001). Autorizada por D-005. Fora do âmbito segundo inputs/pedido.md [P2]: stock e recepção física — esta exclusão só está na fonte, não em scope.json.
- Decisões: D-001 plataforma imposta (decisions.md diz «Plataforma X»; pedido.md [P1] diz Power Platform; pack pp 1.10.0) · D-002 escolhida O-001 (formulário + fluxo), descartada O-002 · D-003 blueprint bp-v01 aprovado, o sha confere · D-004 FC-0001 e FC-0003 autorizados (r0001); recalculei as impressões digitais pelo método de handoff-contract.md e conferem · D-005 âmbito.
- Estado do pacote: delivery_level preliminary, readiness.delivery blocked, sem provas, sem aceitação do destinatário. Os 39 hashes do índice conferem.

## 2. Ordem de construção
O pacote só dá WP-0001 (submissão idempotente) → WP-0002 (aprovação com segregação no servidor, depende do WP-0001), em _design/work-packages.json. Faltam unidades de trabalho para: modelo de dados e ambientes, a passagem a compras (C-001), o fluxo urgente (C-003), o encaminhamento para a direcção financeira, auditoria, migração e cutover.
Ordem que eu seguiria com o que existe: 0) ambiente e entidade pedidos (não há WP; por definir); 1) WP-0001; 2) WP-0002; 3) passagem a compras — não pode começar: não há FC nem WP.
A estimativa (_render/fx-hv1-02_estimate_v01.md) diz «por calcular». A única ordem de grandeza é «4–6 semanas», por analogia sintética (candidates.json O-001).

## 3. Jornada e caminho de falha
Submissão (FC-0001, WP-0001): o Requerente preenche o PedidoFormScreen (blueprint); o cliente gera pedidos.chave_submissao e o servidor grava com unicidade sobre essa chave; uma segunda submissão com a mesma chave devolve o pedido existente e o estado fica submetido. Aceitação: exemplo positivo e negativo do FC-0001.
Não consigo implementar sem inventar: as linhas do pedido (quantidade × preço, C-002) — não há entidade nem campos; o catálogo do ERP-X (nota-dados.md [D1]) — não há linha na SU nem integração; valor_total — o blueprint marca-o obrigatório, mas só o FC-0002 (excluído) o produz, e a gravação falha por construção (scope-gate.json, REQUIRED_FIELD_WITHOUT_PRODUCER); o que torna dois pedidos «o mesmo» — o caso real (entrevista-processo.md [C6]) é o utilizador reenviar, o que dá uma chave nova, e a chave técnica não o apanha; [C6] também não tem linha na SU, e o FC-0001 cita C-002 e C-003, que não tratam de duplicação.
Caminho de falha: FC-0001, «falha de rede depois da gravação» → a repetição devolve o mesmo pedido; implemento com uma chave idempotente reenviada pelo cliente; a prova tem de ser um teste de reenvio após um timeout simulado; o WP-0001 só exige o exemplo negativo, não esta excepção. FC-0003, «quem aprova é o requerente» → o servidor recusa pela interface e pela API; mas o blueprint não tem campo de requerente, de decisor ou de equipa, nem a persona Chefia (aviso ACTOR_NOT_IN_DESIGN em functional-state.json).

## 4. O que falta do cliente
Decisões: regra de arredondamento (U-001, do responsável de compras com a contabilidade); tratamento do fluxo urgente (C-003, A-001); definição de duplicado de negócio ([C6]); migrar ou não os pedidos em curso (emails e folha, [D2]); excluir formalmente a passagem a compras ou especificá-la. Dados: limiar da direcção financeira (U-002, despacho com data); fonte da hierarquia Chefia→equipa; catálogo e preços do ERP-X, com o modo de acesso; requisito de auditoria (M5) e retenção de 10 anos ([D3]), a formalizar. Acessos: identidades de teste por papel (Requerente, Chefia, Compras, direcção financeira); leitura do ERP-X. Ambientes: tenant e ambientes dev/test/prod; licenças e rota de release — nada disto aparece no pacote.

## 5. Aceitação e operação
Aceitação: exemplos positivos e negativos do FC-0001 e do FC-0003, correspondentes às condições dos WP; o FC-0003 negativo corre pela interface e pela API, como pede o ledger seq 2/3 (REV-0002.F01). Juntaria testes de limite (não os há) e o teste da excepção de rede. Não há obrigações de prova (proofs.pending: [], WP.proves: []). O destinatário regista a aceitação num bloco D-NNN «Aceitação do destinatário» (handoff-contract.md); hoje é impossível: o release está bloqueado.
Operação e recuperação: o pacote não dá nada; a spec renderizada só tem o inventário. Faltam A7 (identidade e ponto de imposição), A8 (ambientes e ALM), A10 (papel que intervém, mecanismo de detecção, alerta, procedimento de recuperação) e A12 (provas). O próprio architecture-core.md A10 diz que um modelo de operação ausente é estrutural e bloqueia a aprovação, mas o D-003 aprovou o blueprint na mesma.

## 6. Lacunas
| id | lacuna | classe | justificação | ficheiro onde devia estar |
|---|---|---|---|---|
| L01 | C-001 (passagem a compras) incluída sem FC nem WP | blocks_scope · defeito | NO_CONTRACT em trace.json; regra essencial (o que Compras recebe, estado seguinte) por descobrir | functional-contracts.json, work-packages.json ou exclusão em scope.json |
| L02 | valor_total obrigatório e só produzido pelo FC-0002, excluído | blocks_scope · defeito | D-003 contradiz D-005; J-0001 não grava | ux-blueprint_v01.yaml / scope.json |
| L03 | U-002 (limiar da direcção financeira, blocks_scope) ausente do FC-0003 e não excluída; o encaminhamento depende do valor, que está excluído | blocks_scope · defeito | J-0003 incluída com regra de encaminhamento por decidir; o gate não a vê por falta de open_refs | FC-0003 open_refs + scope.json |
| L04 | Definição de duplicado de negócio ([C6] sem linha na SU; o FC-0001 cita C-002 e C-003) | blocks_scope · defeito | a regra central do FC-0001 teria de ser redescoberta | shared-understanding.md, FC-0001 |
| L05 | Fluxo urgente (C-003, A-001) sem FC e não excluído | blocks_scope · defeito | caminho confirmado sem comportamento nem estado | functional-contracts.json / scope.json |
| L06 | Blueprint sem Chefia/Compras, sem ecrã de aprovação, sem requerente/decisor/data/equipa, sem entidade de linha | blocks_scope · defeito | o FC-0003 usa dados que a autoridade lógica não define | ux-blueprint_v01.yaml |
| L07 | Fonte da hierarquia de equipa | blocks_scope · defeito (fact_gap não registado) | sem ela, «da sua equipa» não se aplica | shared-understanding.md (Unknown) |
| L08 | Auditoria (M5) e retenção de 10 anos ([D3]) sem linha na SU nem FC | blocks_scope · defeito | controlo obrigatório da aprovação | SU + FC-0003 |
| L09 | Catálogo e preços no ERP-X sem linha na SU nem integração; data-integration não foi chamado | blocks_scope · defeito | o conteúdo do pedido fica indefinido | SU, blueprint record_authority |
| L10 | Sem modelo de operação, identidade ou ambientes (A7, A8, A10) | blocks_all · defeito | architecture-core.md A10: estrutural, afecta todas as jornadas | blueprint architecture, implementation-spec |
| L11 | D-005 às 09:00Z, depois de built_at 00:07Z; authorization_refs omite D-005; revisões recebidas depois de D-002/3/4; SU diz «Fase: Discovery» e não tem linhas de decisão; falta reviews_basis | blocks_all · defeito | não se prova que o pacote corresponde ao âmbito autorizado | handoff-index.json, decisions.md, SU |
| L12 | Estimativa por calcular | blocks_all (compromisso, não o arranque técnico) | o release fica preliminar | _render/..._estimate_v01.md |
| L13 | Mecanismo servidor da segregação | delegated_choice · normal | envelope no ledger seq 2 | — |
| L14 | Geração da chave de submissão | delegated_choice · normal (envelope implícito na regra do FC-0001, sem dono declarado) | detalhe técnico dentro da regra | FC-0001 delegated_choices |
| L15 | Idempotência sob falha de rede | implementation_proof · normal | falta a prova planeada | WP-0001 proves/acceptance |
| L16 | Exemplos de limite no FC-0001 e no FC-0003 | delegated_choice · normal | a equipa escreve-os dentro da regra | FC acceptance_examples |
| L17 | Cor do botão (U-003, estacionada) | delegated_choice · normal | sem impacto (states.md) | — |
L01 a L11 são defeitos do handoff: obrigam a redescobrir uma regra ou a confirmar autoria. L13 a L17 são trabalho normal dentro de um envelope.

## 7. Perguntas bloqueantes ao autor
1. O D-005 tem data posterior à construção do índice e não consta de authorization_refs. Este pacote é o release do âmbito autorizado? (L11)
2. A passagem a compras (C-001) é para especificar ou para excluir com autorização? (L01)
3. Como se submete sem valor_total enquanto o FC-0002 está excluído? O campo deixa de ser obrigatório ou o FC-0002 entra? (L02)
4. O encaminhamento para a direcção financeira (U-002) e o fluxo urgente (C-003) estão dentro da J-0003 ou fora? (L03, L05)
5. Que dado identifica a chefia de um requerente, e que define um duplicado de negócio? (L04, L07)

## 8. Ficheiros lidos e maior dificuldade
Lidos: handoff-index.json, _state.json, decisions.md, answers.md (vazio), shared-understanding.md, scope-gate.json, trace.json, functional-state.json, _design/{scope,functional-contracts,work-packages,candidates}.json, _design/reviews/{REV-0001..3,REV-0001..3.mandate,ledger}.json, _blueprint/ux-blueprint_v01.yaml, _render/{implementation-spec,estimate}_v01.md, inputs/{pedido,entrevista-processo,matriz-papeis,nota-dados}.md, library/kernel/handoff-contract.md, specialists.md, states.md (por grep), library/packs/pp/architecture-templates/architecture-core.md, schemas handoff-functional e handoff-index (por grep).
Mais difícil: a definição das jornadas J-0001 e J-0003 (só existem como journey_id; J-0002 não existe); onde vive a regra da direcção financeira (em lado nenhum, depois da SU); qualquer coisa sobre operação e ambientes (ausente); as lacunas L03 a L09 não aparecem no gate — só se vêem cruzando inputs/ com FC e blueprint.
```

</details>

## 7. Depois do ensaio

R1–R4 foram corrigidas (commit `70cd22d`). O pacote em `docs/handoff-v1/F6/pacote-fx-hv1-02/` foi regenerado com elas. O pacote que o destinatário leu está no histórico (commit `9b6a021`). Não houve 4.º ensaio, por decisão do mantenedor.
