# Options — f8-r9-fx03 / Round O-02

## The decision, in one table

| # | Option | Technology | Verdict | Order of magnitude | Reversibility | Blocked by |
|---|---|---|---|---|---|---|
| O-001 | Pedido, aprovação e encomenda — app de ecrãs (canvas) | Power Apps (canvas) sobre Dataverse | viable with preconditions — sem delta nesta ronda | 40–50 dias · `PACK MODEL` | high | — |
| O-002 | Pedido, aprovação e encomenda — app orientada a registos (adoptada em D-002) | Power Apps (model-driven) sobre Dataverse | **retirado** — sucedido por O-006 | 30–38 dias · `PACK MODEL` (histórico) | high | — |
| O-003 | Pedido, aprovação e encomenda — app de ecrãs sobre listas | Power Apps (canvas) sobre listas da ferramenta de colaboração | viable with preconditions — sem delta nesta ronda | 28–35 dias · `PACK MODEL` | medium | M-2 |
| O-004 | Mudar o processo — sem construir nada | sem tecnologia — disciplina de processo | viable with preconditions — sem delta nesta ronda | `ORDER OF MAGNITUDE UNAVAILABLE` | high | — |
| O-005 | Não fazer nada, por agora | sem tecnologia | viable — sem delta nesta ronda | `ORDER OF MAGNITUDE UNAVAILABLE` | high | — |
| O-006 | O-002 actualizado — arredondamento linha-a-linha e limiar 3 000 € | Power Apps (model-driven) sobre Dataverse | viable with preconditions | ver nota¹ · `PACK MODEL` (banda por publicar no candidato) | high (igual a O-002) | TW-4, U-015, U-017 |

¹ O candidato regista `ORDER OF MAGNITUDE UNAVAILABLE`; o modelo do pacote (`craft/estimation-model.md`, EFFORT TABLE) tem, na verdade, linhas ao grão dos componentes que o delta toca — ver **Recommendation** e o registo longo (`lens-outputs/chairman-synthesis-O-02.md`) para a banda verificada nesta síntese.

## Summary

Reabertura pós-decisão (`--reopen`, não um `/revisit`): o cliente entregou `mudancas.md` com três mudanças de negócio depois de D-002 adoptar O-002 — arredondamento linha-a-linha meio-para-o-par (X1), gralha editorial sem impacto (X2), limiar da direcção financeira descido de 5 000 € para 3 000 € (X3). O candidato desta ronda é **um só**: O-006, o delta sobre O-002 — mesma plataforma, mesma forma (model-driven/Dataverse), mesmo âmbito (C-008), regras de cálculo e de limiar actualizadas. Os quatro candidatos não escolhidos (O-001, O-003, O-004, O-005) não foram reavaliados — ficam no registo, não relitigados. O-002 é retirado do conjunto activo, sucedido por O-006. A revisão especializada (5 pareceres, 28 findings, nenhuma divergência entre revisores) convergiu fortemente em quatro pontos que o candidato, por si, não resolvia: a Shared Understanding tinha de ser revalidada para os novos valores (feito nesta síntese: A-007, A-008); a condição de revisão TW-4 (`decisions.md#D-002`) ficou calibrada ao limiar antigo e não cobre a faixa nova; o suporte nativo ao arredondamento meio-para-o-par nunca foi confirmado; e a interacção entre as duas mudanças sobre o mesmo campo Total nunca foi testada perto da fronteira dos 3 000 €.

## Comparison

### O-006 — O-002 actualizado — arredondamento linha-a-linha e limiar 3 000 €   ·   Delta sobre decisão adoptada (D-002)   ·   Power Apps (model-driven) + Dataverse + Power Automate
- **Scope**: whole solution (mesmo âmbito autorizado de O-002, C-008)
- **Verdict**: viable with preconditions
- **Why**: preserva tudo o que D-002 já decidiu (mesma forma, mesmos dados, mesma base de segurança/auditoria) e aplica só as três mudanças de `mudancas.md`; nenhuma delas muda plataforma, forma ou âmbito — mas duas abrem trabalho técnico por fechar antes do blueprint (U-015, U-017) e uma exige actualizar a condição de revisão que protege X-001 (TW-4)
- **Preconditions**: TW-4 (`decisions.md#D-002`) reescrito para o limiar de 3 000 € ou reconfirmado pelo dono — antes de `/decide` fechar O-006 (REV-0006.F01, REV-0008.F01); suporte nativo ao arredondamento meio-para-o-par confirmado, ou decisão de plug-in síncrono — antes do `/blueprint` desenhar o campo (U-015); mecanismo transaccional de escrita do Pedido+Linhas nomeado, nunca por rollup — antes de fechar o routing M-2 (U-017); caso de teste de fronteira (banda 3 000–5 000 €) e critério de aceitação financeiro reescrito, corridos antes de `/decide` (U-016); as quatro condições herdadas de O-002 continuam de pé (U-006, U-011, U-012, U-002/U-013)
- **Risks**: R-003, R-004, U-011, U-013 (herdados, inalterados); agravamento da materialidade de X-001 pelo limiar mais baixo (mais pedidos urgentes cruzam a fronteira financeira)
- **Proof required**: bounded pilot (mesma UAT de O-002) + caso de teste de fronteira dedicado à interacção X1×X3 (U-016) — funded? não avaliado
- **Decides against the others**: não se aplica — O-006 não compete com O-001/O-003/O-004/O-005 nesta ronda; sucede directamente a O-002, já escolhido em D-002

### O-001, O-003, O-004, O-005 — sem delta nesta ronda

Nenhum dos quatro foi reavaliado: a reabertura pedida (`ver mudancas.md`) incide sobre a decisão em vigor (D-002/O-002), não sobre uma nova comparação de plataformas ou formas. Mantêm-se exactamente como ficaram em `options.md` da ronda O-01 (ver `lens-outputs/chairman-synthesis-O-01.md#Per-option-long-form` para o registo completo): O-001 (canvas/Dataverse, mais caro, sem forfeit móvel), O-003 (canvas/listas, mais barato, bloqueado por não impor o limiar M-2 ao nível da loja), O-004 (mudar o processo, `PROCESS-CHANGE`), O-005 (não fazer nada, `DO-NOTHING`). As mudanças de `mudancas.md` (arredondamento, limiar) tocam-nos também — todos citam C-006/C-007 nos seus `premise_refs` — mas isso é uma revalidação de premissa (agora A-007/A-008), não um convite a reabri-los como candidatos activos.

## Out of play

- O-002 — retirado do conjunto activo (`retired_ids`), sucedido por O-006; a decisão que o escolheu (D-002) fica no registo, intocada.
- Outras plataformas, extensão do ERP-X, capacidade nativa da ferramenta de colaboração — mesmas exclusões da ronda O-01 (`candidates.json#exclusions`); nenhuma reaberta.
- Reavaliar O-001/O-003/O-004/O-005 à luz de `mudancas.md` — fora do âmbito desta reabertura (`candidates.json#exclusions`).

## Recommendation

**Recommended**: no recommendation — O-006 é o único candidato activo desta ronda; não há irmãos para comparar.
**Against its siblings**: não aplicável (ver acima).
**Rests on**: A-007, A-008 (os dois factos revalidados que o delta assume); C-001, C-008 (plataforma e âmbito inalterados); as premissas herdadas de O-002 (U-006, U-011, U-012, U-002/U-013).
**Would flip it**: U-015 (se meio-para-o-par não tiver suporte nativo, o esforço sobe por um factor ~6–12× no componente afectado — `estimation-model.md`: coluna calculada 0.25d vs plug-in 3d); U-017 (se o mecanismo transaccional não for nomeado correctamente, o gate M-2 deixa de ser fiável); TW-4 por reescrever (sem isso, a base de aceitação de risco de D-002 não cobre a faixa 3 000–5 000 €).
Terminal: **decision blocked por precondições, não por alternativa** — o candidato não compete com outros; fecha quando as quatro precondições acima fecharem. Banda de esforço: o candidato declara `ORDER OF MAGNITUDE UNAVAILABLE`, mas o modelo do pacote tem linhas ao grão certo (`estimation-model.md` EFFORT TABLE, Dataverse): Calculated/rollup column 0,25d, Business rule 0,5d, Low-code plugin 3d — aplicados aos componentes já nomeados em `impact_refs`, uma banda plausível é **0,5–1 dia** se meio-para-o-par tiver suporte nativo (ajustar 2 colunas calculadas + a regra de negócio do limiar), **3,5–4 dias** se exigir plug-in síncrono (U-015 decide qual) — verificado nesta síntese (REV-0010.F01), não publicado no candidato (`_design/candidates.json` fica por corrigir na próxima revisão, para não obrigar a uma segunda ronda de revisão especializada sobre um só campo).

## Comparator status

- O-001, O-003, O-004, O-005 — sem delta nesta ronda; estatuto de comparador inalterado desde O-01 (ver `options.md` histórico via `_design/history/candidates.r0001.json`).
