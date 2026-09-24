# Options — f8-r3-fx02 / Round O-01

## The decision, in one table

| # | Option | Technology | Verdict | Order of magnitude | Reversibility | Blocked by |
|---|---|---|---|---|---|---|
| O-001 | Pedido, aprovação e encomenda — app de ecrãs (canvas) | Power Apps (canvas) sobre Dataverse | viable with preconditions | 40–50 dias · `PACK MODEL` | high | — |
| O-002 | Pedido, aprovação e encomenda — app orientada a registos | Power Apps (model-driven) sobre Dataverse | viable with preconditions | 30–38 dias · `PACK MODEL` | high | — |
| O-003 | Pedido, aprovação e encomenda — app de ecrãs sobre listas | Power Apps (canvas) sobre listas da ferramenta de colaboração | viable with preconditions | 28–35 dias · `PACK MODEL` | medium | M-2 |
| O-004 | Mudar o processo — sem construir nada | sem tecnologia — disciplina de processo | viable with preconditions | `ORDER OF MAGNITUDE UNAVAILABLE — sem construção, sem linha equivalente no modelo` | high | — |
| O-005 | Não fazer nada, por agora | sem tecnologia | viable | `ORDER OF MAGNITUDE UNAVAILABLE — custo do as-is ainda não quantificado` | high | — |

## Summary

Cinco candidatos: três formas dentro da plataforma imposta (C-001), mais mudar o processo e não fazer nada. A revisão especializada (5 pareceres, 16 achados, nenhuma divergência entre revisores) não elimina nenhum candidato definitivamente, mas muda o que se sabe deles: o mecanismo de detecção de duplicados descrito não é idempotente como escrito (R-003, was R-001); uma "cópia local" do catálogo é um anti-padrão de cache que precisa de dono, cadência e deteção de drift (R-004, was R-002); entitlement/licenciamento das 5 populações nunca foi verificado (U-011, nova); a capacidade de integração do ERP-X (existe interface?) nunca foi confirmada (U-012, nova); e O-003 tem um achado `blocking`: a loja (listas) não impõe o limiar de 5 000 € (M-2) ao nível de segurança — só o fluxo o faz, e isso não é um controlo.

## Comparison

### O-001 — Pedido, aprovação e encomenda — app de ecrãs (canvas)   ·   Power Apps (canvas) + Dataverse
- **Scope**: whole solution
- **Verdict**: viable with preconditions
- **Why**: segurança/auditoria ao nível da coluna na loja (Dataverse) — base sólida para M-2/M-3 uma vez desenhado o mecanismo; sem forfeit de superfície
- **Preconditions**: mecanismo de auditoria — arquitecto — antes do blueprint (U-006); entitlement verificado — director de SI — antes de /decide (U-011); interface do ERP-X confirmada (U-012)
- **Risks**: R-003, R-004, U-011
- **Proof required**: bounded pilot — funded? não avaliado

### O-002 — Pedido, aprovação e encomenda — app orientada a registos   ·   Power Apps (model-driven) + Dataverse
- **Scope**: whole solution
- **Verdict**: viable with preconditions
- **Why**: mesma base de O-001, ecrãs gerados pela shell (custo mais baixo); forfeit — browser de telemóvel não suportado
- **Preconditions**: as três de O-001 (U-006, U-011, U-012); confirmar acesso não-móvel, ou app nativa servir os requerentes — director de SI — antes de /decide (U-002, U-013)
- **Risks**: R-003, R-004, U-011, U-013
- **Proof required**: bounded pilot — funded? não avaliado
- **Decides against the others**: U-002 (dispositivo do requerente) é o único facto que separa O-002 de O-001

### O-003 — Pedido, aprovação e encomenda — app de ecrãs sobre listas   ·   Power Apps (canvas) + listas
- **Scope**: whole solution
- **Verdict**: viable with preconditions
- **Why**: custo mais baixo dos três; a loja (listas) não tem segurança de coluna — o limiar de 5 000 € (M-2) só fica imposto no fluxo, contornável (achado `blocking`)
- **Preconditions**: declaração formal de risco residual sobre M-2, assinada por um dono — antes de /decide; as três de O-001
- **Risks**: R-003, R-004, M-2 (segregação não imposta pela loja)
- **Proof required**: bounded pilot + prova do compensatório — funded? não avaliado

### O-004 — Mudar o processo — sem construir nada   ·   mudar o processo; construir nada   ·   sem tecnologia — disciplina de processo
- **Scope**: whole solution
- **Verdict**: viable with preconditions — *(whole solution, viable with preconditions)*
- **Why**: reversível sem nada a desmontar, custo de implementação mínimo; não endereça de forma fiável a obrigação de auditoria (M-3) além do que o email já oferece
- **Preconditions**: aceitar o risco residual de M-3, ou compensatório manual — director de SI/auditoria interna — antes de /decide
- **Risks**: R-003 (mitigação fraca), R-004 (idem)
- **Proof required**: (none)

### O-005 — Não fazer nada, por agora   ·   não fazer nada / adiar   ·   sem tecnologia
- **Scope**: whole solution
- **Verdict**: viable — *(whole solution, viable)*
- **Why**: sem compromisso a desfazer; nenhum ganho — R-003/R-004 continuam sem mitigação nenhuma, nem a disciplina intermédia de O-004
- **Risks**: R-003, R-004
- **Proof required**: (none)

## Out of play

- Outras plataformas (desenvolvimento à medida, cloud-native, outro low-code, produto comprado) — excluídas: plataforma imposta por decisão corporativa (C-001); só entrariam como *viável se a regra mudar*, e ninguém pediu essa reabertura.
- Estender o ERP-X — excluída: sem evidência de que suporta pedido/aprovação/registo, só o catálogo de preços vive lá.
- Capacidade nativa da ferramenta de colaboração (lista + fluxo simples, sem app dedicada) — excluída: cálculo condicional + aprovação em dois níveis + obrigação de auditoria não cabem nos gatilhos de suficiência dessa forma.

## Recommendation

**Recommended**: no recommendation — U-002 (o contexto/dispositivo do requerente) decide entre O-001 e O-002.
**Against its siblings**: O-001 e O-002 partilham o mesmo modelo de dados, as mesmas regras e a mesma base de segurança/auditoria (Dataverse) — a única diferença material é o forfeit de acesso móvel de O-002 (U-002, U-013). O-003 é o único com um achado `blocking` próprio (segregação do limiar M-2 não imposta pela loja) — mais fraco que os dois anteriores enquanto essa precondição não fechar. `COMPARATOR EVIDENCE ABSENT` entre O-004/O-005 e os três candidatos construídos: nenhum modelo de esforço comparável foi calculado para eles.
**Rests on**: A-001, A-002 (impacto e causa dos duplicados, ainda qualitativos); nenhum candidato pressupõe resposta a X-001 (caminho de urgência), ainda Conflicted.
**Would flip it**: U-002 (contexto de uso — decide O-001 vs O-002); U-006 (mecanismo de auditoria — afecta os três candidatos sobre plataforma por igual); U-011 (entitlement — pode mudar viabilidade económica, não só custo); a declaração de risco residual de O-003 (se recusada, O-003 sai da mesa).

multiple defensible options

## Comparator status

- O-004 (mudar o processo) — `ORDER OF MAGNITUDE UNAVAILABLE — sem construção, sem linha equivalente no modelo de esforço do pacote`
- O-005 (não fazer nada) — `ORDER OF MAGNITUDE UNAVAILABLE — custo do processo actual ainda não quantificado (U-001, U-009, U-010)`
