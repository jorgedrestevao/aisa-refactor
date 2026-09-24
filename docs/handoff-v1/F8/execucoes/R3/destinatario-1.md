Relatório sobre pacote `R3-r0001` (engagement `f8-r3-fx02`, revision 1). Só ficheiros dentro da pasta lidos. 52 ficheiros no `handoff-index.json`, hashes verificados por script — **todos batem** (incl. `_design/candidates.json` em `based_on`). Isso prova integridade byte-a-byte do que está no pacote; não prova que o pacote corresponde ao âmbito autorizado — ver §1.

## 1. Âmbito, exclusões, decisões autorizadas

**Dentro**: pedido, aprovação, passagem a compras (`shared-understanding.md#C-008`, `inputs/pedido.md` [P2], `enquadramento.md` T7). **Fora**: gestão de stock, recepção física (mesmos locators).

**Plataforma imposta**: Power Platform, por decisão do director de sistemas de informação (`shared-understanding.md#C-001`, `answers.md#ROTA`, `_state.json.workflow.route = platform-constrained`, `authority_ref: C-001`). A deliberação `DSI-SINT-07` citada em `inputs/pedido.md` [P1] **não está no pacote** — é uma declaração do dono, `Confirmed` por autoridade (`states.md` regra 3), não um documento verificável.

**Exclusões autorizadas** (`_design/candidates.json#exclusions`): outras plataformas, estender o ERP-X, capacidade nativa da ferramenta de colaboração — todas justificadas por C-001 e por ausência de gatilho no `alternatives-register.md`.

**Decisão**: `decisions.md#D-002` adopta O-002 (model-driven/Dataverse). O aisa **não recomendou** entre O-001/O-002 (`options.md#Recommendation`: "multiple defensible options"); o dono escolheu por custo (30–38 vs 40–50 dias) aceitando o forfeit de acesso móvel sem ter confirmado U-002. `Sponsor confirmation: pending` — **ainda não confirmado**, mesmo classificado como decisão tomada.

**`handoff-index.json#authorization_refs`** lista só `decisions.md#D-002`. Coerente com o que existe: não há aprovação de blueprint, nem FC, nem scope — porque nenhum foi produzido (ver §2/§6).

**Prova de correspondência ao âmbito autorizado**: parcial. Hashes provam que nada foi alterado depois de construído. Mas `handoff-index.json#reviews_basis` mostra, para as 5 reviews, `shared-understanding.md` e `decisions.md` marcados `"now": "changed since the review"` — as 5 revisões especializadas leram uma SU/decisions **anteriores** às que o pacote entrega agora, sem registo de revalidação (`_design/reviews/ledger.json` não tem nenhum `PIN_UNREVALIDATED`/revalidation record para isto, ao contrário do que `library/kernel/handoff-contract.md` → *Pinned dependencies* exige). `handoff-index.json#readiness.delivery = "blocked"`, `ready: false` — o próprio pacote declara que não corresponde a um âmbito fechado.

## 2. Ordem de construção

**Não há inventário de trabalho.** `_design/scope.json` e `_design/work-packages.json` não existem no pacote (nem constam do `handoff-index.json#files`). `functional-state.json` está vazio (`revision: 0, items: {}`) — nenhum `FC-NNNN` foi autorizado. Não há `_blueprint/` no pacote, apesar de `trace.json` e `scope-gate.json` citarem `_blueprint/ux-blueprint_v01.yaml#architecture/proof_obligations[0]` — **o ficheiro do blueprint não foi entregue**. Logo: nenhum `WP-NNNN` existe para sequenciar. `handoff-index.json#readiness.reasons` confirma: "implementation-spec não renderizada", "estimativa não renderizada", "aprovação do desenho missing".

Ordem reconstruída só a partir de `decisions.md#D-002` (Conditions/Tripwires), `options.md` e `library/packs/pp/domain-knowledge/craft/estimation-model.md`:

1. **Fechar bloqueios de âmbito** antes de desenhar (`scope-gate.json#blockers`): U-007 (envelope orçamental, `blocks_all`), U-006 (mecanismo de auditoria), U-011 (entitlement/licenciamento, verificação VC-05), U-012 (interface do ERP-X), X-001 (caminho de urgência vs limiar financeiro, `Conflicted`, crítico).
2. **U-002/U-013** — confirmar contexto de dispositivo do requerente; se móvel confirmado, TW-1 manda reabrir para O-001 antes de gastar esforço em ecrãs model-driven.
3. **Desenhar e aprovar o blueprint** (`_blueprint/ux-blueprint_v01.yaml` — ausente do pacote) — só depois disso é que os `FC-NNNN` podem ser autorizados (`handoff-contract.md` §Functional contract).
4. **Publicar scope.json + work-packages.json** (`inventory.py`), com `WP-NNNN` a realizar cada `FC`/nó de blueprint.
5. **Renderizar implementation-spec + estimate** a partir dos WPs.
6. **Construção**, por `estimation-model.md` (Fase 0→7): Fase 0 preparação/ambiente (aqui entra a verificação VC-05 de entitlement, **antes** de qualquer environment ser tornado managed — `governance-and-environments.md` §8, cadeia controlo→entitlement→população); Fase 1 camada de dados (tabelas Pedido/Linha de pedido/Registo de aprovação/Catálogo, `candidates.json#O-002.architecture`) — segurança de coluna nos campos de aprovação (estado/valor/aprovador) tem de existir **antes** dos ecrãs, porque um controlo só no fluxo (plano 5) "não é um controlo" (`security-controls.md` §4, achado `REV-0003.F03`); Fase 2 integração ERP-X (depende de U-012/U-004 resolvidos); Fase 3 aplicação (ecrãs gerados pela shell model-driven + fluxo de aprovação chefia→financeira, dependente de X-001 resolvido); mecanismo de duplicados concreto (chave alternada+upsert, ou plug-in síncrono verificação+criação atómica — não o descrito em `candidates.json`, ver §3); Fase 7 UAT com submissão concorrente (prova exigida em `decisions.md#D-002`, sem WP — `trace.json#proofs[0]`) + go-live.

## 3. Jornada e caminho de falha

**Jornada feliz** (`candidates.json#O-002`, `shared-understanding.md`): requerente submete no ecrã model-driven → chefia aprova (nunca o próprio, M-1) → se valor > 5000€ (M-2/C-006) rota para direcção financeira → aprovado → compras regista e encomenda, usando preço do catálogo (C-004, fonte ainda por decidir — U-004) → confirmação de recepção ao requerente (mitiga R-001) → registo de auditoria (mecanismo por desenhar, U-006).

**Caminho de falha**: requerente não vê/recebe a confirmação → reenvia → detecção de duplicados dispara. O mecanismo descrito em `candidates.json` ("mesmo requerente + conteúdo semelhante + janela curta") **não é idempotente** — não activa por omissão nas escritas Web API/flow do Dataverse, sofre corrida verificação-antes-de-escrita (TOCTOU), e um retry ingénuo em erro de servidor recria o duplicado que devia bloquear (`REV-0002.F01`, evidência em `library/packs/pp/domain-knowledge/data/dataverse.md` §5 e `integration/integration-mechanisms.md` §7). Isto é `R-003` (was `R-001`) na SU — aceite como risco em `decisions.md#D-002`, não resolvido.

**Caminho de urgência**: avaria bloqueante → vai directo a compras → chefia tem até fim do dia útil seguinte para validar (`A-006`, `nota-urgentes.md`) → se não validar, compras suspende a encomenda (`U-014`, mecanismo exacto — estado interno pendente vs cancelamento junto do fornecedor — ainda por dizer) → **não está declarado** se este caminho também salta o limiar financeiro (X-001, `Conflicted`, aberto há duas passagens, avançado por override em `decisions.md#D-001`).

**O que teria de inventar** (o pacote não diz): (a) mecanismo concreto de idempotência dos duplicados; (b) desenho concreto do registo de auditoria (imutabilidade, quem escreve, retenção alinhada a M-4); (c) segurança de coluna nos campos de aprovação (nenhum candidato a declara); (d) mecanismo exacto de suspensão do caminho urgente (U-014); (e) se X-001 fecha "sim" ou "não" para o limiar financeiro; (f) os próprios ecrãs — não há blueprint no pacote, só texto de arquitectura em prosa.

## 4. O que falta do cliente

- Envelope orçamental/financiamento (U-007, `blocks_all` — `context.json` sem `funding_gate`, tratado como `true` por omissão, `enquadramento.md`).
- Despacho formal do limiar financeiro (nunca entregue; só o valor 5000€ foi confirmado verbalmente, `answers.md#U-005`).
- Resposta a X-001 (urgência vs limiar financeiro).
- Mecanismo de auditoria (U-006), assinado por auditoria interna.
- Confirmação técnica do ERP-X (interface, dono, garantia — U-012).
- Verificação de entitlement/licenciamento das 5 populações (U-011, VC-05).
- Contexto de dispositivo do requerente (U-002) + instalabilidade/licenciamento da app nativa móvel (U-013).
- Volume/frequência (U-001), tempo por passo (U-009), taxa horária carregada (U-010) — dimensionam esforço e o envelope de custo as-is.
- Critério de sucesso do projecto (U-008).
- Confirmação do sponsor sobre D-002 (`pending`).
- Estado do estate/ambientes Power Platform (nenhuma linha SU cobre isto — ver Lacuna L-Env).
- Validação de A-002 (confirmação de recepção como causa dos duplicados) directamente com o requerente.

## 5. Aceitação e operação

**Aceitação**: `decisions.md#D-002` exige "bounded pilot... UAT com submissão concorrente do mesmo conteúdo" — mas essa prova **não tem WP** (`trace.json#proofs[0].wp: []`, achado `PROOF_WITHOUT_WORK`). Não há bloco `D-NNN — Aceitação do destinatário` em `decisions.md`; `handoff-index.json#receiver_acceptance: null`. Critério de aceitação da jornada de excepção (reenvio) também não está nomeado (`REV-0004.F01`). Para provar aceitação eu teria de escrever esse plano de teste do zero.

**Operação/recuperação**: os ficheiros de pack que tratam operação e ALM (`operations/operability-and-support.md`, `alm/release-and-lifecycle.md`) são citados repetidamente por `governance-and-environments.md` e `security-controls.md` como donos do assunto, mas **não fazem parte do pacote**. Retenção de auditoria (M-4 = 10 anos) excede a retenção por omissão da plataforma (7–28 dias, `governance-and-environments.md` §6) — exige arquivo próprio, nunca endereçado em nenhum artefacto do pacote. Nenhuma linha da SU cobre estado do tenant/ambientes (managed environments, contagem, ALM) — pré-condição que o próprio pack classifica como `decision-grade`.

## 6. Lacunas

| id | lacuna | classe | defeito do pacote / trabalho normal | justificação | ficheiro onde devia estar |
|---|---|---|---|---|---|
| L1 | Blueprint citado (`_blueprint/ux-blueprint_v01.yaml`) mas não entregue nem aprovado | blocks_all | defeito do pacote | `trace.json` e `scope-gate.json` citam-no como base de proof_obligations; sem ele não há desenho de ecrãs nem arquitectura aprovada para reconstruir | `_blueprint/ux-blueprint_v01.yaml` (ausente) |
| L2 | U-007 (envelope orçamental) aberto, `blocks_all`, decisão D-002 avançou sem resposta nem override registado | blocks_all | defeito do pacote | uma pergunta `blocks_all` nunca devia sobreviver a `/decide` sem override explícito; não há nenhum na SU/decisions.md | `shared-understanding.md#U-007`, `decisions.md` |
| L3 | Nenhum inventário de trabalho (`_design/scope.json`, `_design/work-packages.json`) nem FC autorizado (`functional-state.json` vazio) | blocks_all | trabalho normal (pacote é `delivery_level: preliminary`, admite-o) | `handoff-index.json#readiness.reasons` confirma "implementation-spec não renderizada" | `_design/scope.json`, `_design/work-packages.json`, `_design/functional-contracts.json` |
| L4 | Reviews (REV-0001..0005) pinadas a revisões de SU/decisions.md já mudadas (`reviews_basis` marca "changed since the review"), sem registo de revalidação | blocks_all (afecta a confiança de todas as reviews) | defeito do pacote | `handoff-contract.md` → *Pinned dependencies* exige revalidação registada quando um pin muda de hash; `ledger.json` não tem nenhuma | `handoff-index.json#reviews_basis`, `_design/reviews/ledger.json` |
| L5 | U-011 (entitlement/licenciamento, VC-05) não verificado apesar de M-3/M-4 confirmados a despoletar a obrigação | blocks_scope | defeito do pacote | 2 revisores independentes (`REV-0001.F02`, `REV-0005.F02`) apontam o mesmo achado; decisão foi tomada sem a verificação que o pack exige antes de escolher o controlo (`licensing-and-cost-drivers.md` §9) | `shared-understanding.md#U-011` |
| L6 | Texto de `candidates.json#O-002` ainda diz "auditoria vem herdada da shell" (sobrestima), correcção só `delegated` no ledger, não aplicada na revisão 1 entregue | blocks_scope | defeito do pacote | `REV-0003.F02`; o texto sobre o qual D-002 foi decidido continua incorrecto | `_design/candidates.json#items[1].architecture` |
| L7 | premise_refs de O-001/O-002/O-003 não incluem C-003 (fluxo de urgência); nenhuma banda reserva esse esforço | blocks_scope | defeito do pacote | `REV-0003.F04`, disposição `delegated`, não corrigida antes de D-002 | `_design/candidates.json#items[*].premise_refs` |
| L8 | Multiplicador de complexidade 1.2× (Medium) não justificado pela própria contagem de entidades (4 tabelas = Simple/1.0×) | delegated_choice | defeito do pacote | `REV-0005.F01`; a banda "30–38 dias" citada em D-002 assenta num número não fundamentado pelo próprio modelo | `_design/candidates.json#items[1].order_of_magnitude` |
| L9 | U-006 (mecanismo de auditoria) por desenhar | blocks_scope | trabalho normal | pergunta Options-stage correctamente admitida e rastreada até /blueprint | `shared-understanding.md#U-006` |
| L10 | U-012 (interface do ERP-X) e U-002/U-013 (contexto móvel + app nativa) por confirmar | blocks_scope / delegated_choice | trabalho normal | perguntas correctamente admitidas (M-n + eixo + ≥2 respostas), decisão aceitou o risco explicitamente | `shared-understanding.md#U-012`, `#U-002`, `#U-013` |
| L11 | Nenhuma linha SU sobre estado do tenant/ambientes Power Platform (managed environments, contagem, ALM) | blocks_scope | defeito do pacote | `governance-and-environments.md` §2/§17 trata isto como precondição `decision-grade` a verificar antes de custar; nenhum artefacto do pacote a toca | ausente de `shared-understanding.md` |
| L12 | `operations/operability-and-support.md` e `alm/release-and-lifecycle.md` citados por outros ficheiros do pack mas não incluídos no pacote | implementation_proof | defeito do pacote | impossível verificar o modelo operacional/recuperação/ALM que os revisores pressupõem | ausente de `library/packs/pp/domain-knowledge/` |
| L13 | X-001 (urgência salta ou não o limiar financeiro) continua Conflicted, avançado por override | blocks_scope | trabalho normal | correctamente disclosed em `frame.md`/`decisions.md#D-001`, com condição de fecho explícita antes de qualquer entrega final | `shared-understanding.md#X-001` |

## 7. Perguntas bloqueantes ao autor

1. Onde está `_blueprint/ux-blueprint_v01.yaml`, citado por `trace.json`/`scope-gate.json`? Está aprovado?
2. Há envelope orçamental aprovado (U-007)? Se sim, porque não fechou antes de D-002?
3. X-001: o caminho de urgência salta também a aprovação da direcção financeira acima de 5000€?
4. As correcções que o ledger marca `delegated` (`REV-0001.F01`, `REV-0003.F02`, `REV-0003.F04`, `REV-0005.F01`, `REV-0005.F03`) foram aplicadas nalguma revisão de `candidates.json` posterior à 1? O pacote só traz a revisão 1.
5. Porque é que `handoff-index.json#reviews_basis` regista SU e decisions.md como "changed since the review" para as 5 reviews, sem revalidação registada?
6. Qual o mecanismo concreto de registo de auditoria (U-006) — nativo, tabela própria, imutabilidade, retenção?
7. O ERP-X expõe interface programável (U-012)? Quem a detém?
8. Mecanismo exacto de suspensão no caminho de urgência (U-014)?
9. `decisions.md#D-002` diz "Sponsor confirmation: pending" — foi confirmado entretanto?
10. Porque é que `inputs/nota-urgentes.md` está datada de 2026-10-01, depois do `built_at` do pacote (2026-09-24T14:22:52Z)?

## 8. Ficheiros lidos

Todos os 52 do `handoff-index.json#files` mais `_design/reviews/*.mandate.json` (5). Mais difícil de encontrar: que o blueprint referenciado por `trace.json`/`scope-gate.json` **não existe no pacote** — só se percebe cruzando esses dois ficheiros contra a lista completa de `handoff-index.json#files` e a árvore real de directórios (não há `_blueprint/` nem `_design/scope.json`/`_design/work-packages.json`). Confirmar a integridade dos hashes exigiu escrever um script (não vem verificado no próprio pacote). Perceber o comportamento por omissão de `funding_gate` (tratado como `true` sem evidência) exigiu cruzar `context.json`, `enquadramento.md` e `library/kernel/states.md`.
