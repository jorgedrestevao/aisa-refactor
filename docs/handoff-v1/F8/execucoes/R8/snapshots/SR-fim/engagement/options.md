# Options — f8-r8-fx03 / Round O-02

## The decision, in one table

| # | Option | Technology | Verdict | Order of magnitude | Reversibility | Blocked by |
|---|---|---|---|---|---|---|
| O-006 | Pedido, aprovação e encomenda — model-driven, revisto (delta pós-aprovação) | Power Apps (model-driven) + Dataverse + Power Automate | viable with preconditions | 30–38 dias (base O-002, inalterada) + 0.25–3.6 dias de delta · `PACK MODEL` | high (delta); unchanged from O-002 for the rest | U-004 (pré-existente, alheio a este delta) |

Id order, não é ranking — há um só candidato nesta passagem.

## Summary

Reabertura por mudança de negócio pós-aprovação (`inputs/mudancas.md`), não por `/revisit`. O único candidato desta passagem é o delta sobre a arquitectura já decidida (D-002/O-002): nenhuma forma nova, nenhuma alternativa de plataforma reconsiderada. Duas mudanças materiais — arredondamento (linha-a-linha, meio-para-par) e limiar de aprovação financeira (5 000€ → 3 000€) — ficam contidas dentro da forma escolhida; uma terceira (correcção de gralha) não tem consequência. Cinco pareceres especializados independentes (arquitectura, dados/integração, segurança/operação, experiência, custo) reviram o delta; convergência forte, sem divergência material, sobre um ponto: `C-006` (limiar) precisava de revalidação explícita, e a condição de revisão `TW-4` cita o valor antigo por número literal. Ambos endereçados nesta síntese (ver *Recommendation*).

## Comparison

### O-006 — Pedido, aprovação e encomenda — model-driven, revisto   ·   esta plataforma, mesma forma de O-002   ·   Power Apps (model-driven) + Dataverse
- **Scope**: whole solution — herda por inteiro o modelo de dados, ecrãs e fluxos de O-002.
- **Verdict**: viable with preconditions — (whole solution, viable with preconditions).
- **Why**: o delta é regra de cálculo (arredondamento por linha) + valor de configuração (limiar) — nenhum dos dois eixo técnico que bloqueiam decisão (U-004 continua o único, pré-existente); o mecanismo exacto de arredondamento/recálculo síncrono ainda não está confirmado (U-015).
- **Preconditions**: mecanismo de arredondamento/recálculo confirmado — fonte: teste técnico em sandbox Dataverse — não financiado ainda — antes de `/blueprint --refresh` (U-015). TW-4/decisions.md#D-002 emendado para citar C-006/A-007 por id — role: director de sistemas de informação — por fazer.
- **Risks**: A-008 (arredondamento, terceiro sem papel nomeado — mesmo padrão de A-006); X-001 mais exposto com o limiar mais baixo (mais pedidos na zona de conflito).
- **Proof required**: engineered test harness (sandbox Dataverse, valores em meio-cêntimo exacto + gravação/leitura imediata do total) — funded? não.
- **Decides against the others**: (omitido — sem irmã nesta passagem; O-001/O-003/O-004/O-005 retirados, ver *Out of play*).

## Out of play

- O-001, O-003, O-004, O-005 — retirados nesta reabertura (`retired_ids`, história imutável em `_design/history/`). Nenhuma das duas mudanças de negócio toca o que já as separava de O-002 em O-01 (contexto/dispositivo, segurança de coluna, disciplina de processo vs sistema construído) — não reconsiderados; reabrir essa escolha exigiria evidência nova sobre essas razões, que `mudancas.md` não traz.

## Recommendation

- **Recommended**: O-006 (manter O-002/D-002, absorver o delta).
- **Against its siblings**: sem irmã nesta passagem — a comparação é contra o que já estava decidido (D-002), não entre formas.
- **Rests on**: A-007 (limiar 3 000€, was C-006), A-008 (arredondamento linha-a-linha/meio-para-par, was C-007) — ambas Assumed, documento entregue pelo cliente sem papel nomeado (mesmo padrão de A-006, não Confirmed).
- **Would flip it**: U-015 (Critical) — se o mecanismo exigir plug-in síncrono em vez de coluna calculada, o custo e a arquitectura de baixo nível mudam, não a forma; nenhuma resposta prevista muda a escolha de O-002.
- Terminal: **conditionally preferred** — condicional a fechar U-015 (mecanismo técnico) e à emenda de TW-4/decisions.md#D-002 (citar C-006/A-007 por id, não o número literal) antes de `/decide` ou `/blueprint --refresh` fecharem sobre isto.

## Comparator status

- Não aplicável — rota `platform-constrained` (mecanicamente; ver anomalia em `council-log.md#O-02`), um só candidato, sem comparador de mercado nesta passagem.

## Achados por fechar (deferred, não bloqueiam esta passagem)

Onze achados dos cinco pareceres ficam `deferred` — impacto registado, sem correcção ainda feita; nenhum impede esta síntese, todos ficam nomeados para o passo que os fecha (`/blueprint --refresh`, `/synthesize` ou decisão do dono):

- REV-0006.F02, REV-0006.F03, REV-0007.F01, REV-0007.F02 — mecanismo de arredondamento/recálculo síncrono → **U-015**.
- REV-0007.F03 — sequenciar mecanismo de R-003 antes de fixar custo do delta.
- REV-0007.F04 — confirmar com a contabilidade que meio-para-par bate com a reconciliação dela.
- REV-0007.F06 — nota de frescura para `frame.md` no próximo `/synthesize`.
- REV-0008.F01 — X-001 mais exposto com o limiar mais baixo (sem mudança de estado da linha).
- REV-0009.F04 — critério de aceitação de fronteira do arredondamento.
- REV-0009.F05 — aviso pré-submissão de limiar → **U-016**.
- REV-0009.F06 — nota de cobertura de R-003/A-002 no próximo `/synthesize`.

Ver `lens-outputs/chairman-synthesis-O-02.md` para o registo completo (13 achados fechados — `accepted`/`delegated` — e os onze acima, um por um, com dono e critério de fecho).

## A seguir

`/blueprint --refresh` quando U-015 fechar e a emenda de TW-4 estiver feita; entretanto, `/answer U-016 "..."` resolve o aviso de ecrã. `/decide` continua por correr sobre esta reabertura.
