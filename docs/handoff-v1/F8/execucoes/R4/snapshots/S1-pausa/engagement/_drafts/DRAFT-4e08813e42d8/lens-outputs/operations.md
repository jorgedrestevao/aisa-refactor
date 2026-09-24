## R-01 — operations

**What matters**: o fluxo real tem duas transcrições manuais — a folha do colaborador (email) → "outra folha" da contabilidade → ERP-X (C-001) — antes de qualquer sistema de registo, sem validação automática entre passos. Duas pessoas da contabilidade gastam parte do dia nisto (C-003), mas ninguém sabe quantificar quantas horas (U-004). Os problemas do dia-a-dia — duplicados, recibos ilegíveis, atrasos (C-002) — nascem directamente do canal actual (email) e da ausência de validação entre passos.

**Tensions / risks**: sem tempo por passo medido (U-004), qualquer estimativa de esforço poupado por uma solução fica sem base — a mesma lacuna bloqueia a baseline financeira (ver `financial`). O volume mensal (~300, A-002) é uma memória, não um registo — não dá para planear capacidade com confiança nesse número sozinho.

**Open evidence**:
- `chain: email → folha intermédia → ERP-X → pagamento` → ADOPT → C-001
- `chain: reenvio de email → duplicado` → ADOPT → C-002
- `chain: posição da aprovação no fluxo, por confirmar` → DISMISS — detalhe de sequenciamento que se resolve no desenho (blueprint); não muda viabilidade nem a escolha agora
