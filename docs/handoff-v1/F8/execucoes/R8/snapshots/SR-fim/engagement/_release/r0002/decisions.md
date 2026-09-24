# Decisions — f8-r3-fx02

## D-001 — Frame agreed (F-01)

- **Frame sentence**: O problema é a falta de um sistema único para pedir, aprovar e encomendar equipamento informático — hoje tudo corre por email e por uma folha de cálculo, sem preço sempre actualizado e, segundo o responsável de compras, sem confirmação de recepção que evite reenvios (assumido, ainda por confirmar com o requerente) —, sentido por compras (retrabalho com encomendas a dobrar) e, na reconciliação, por divergências de arredondamento reportadas à contabilidade (ainda por confirmar se a contabilidade sente o mesmo impacto); custa hoje pedidos duplicados e divergências reais já ocorridas, ainda sem envelope quantificado (falta o volume, o tempo por passo e a taxa horária carregada); a evidência vem da entrevista ao responsável de compras e da nota sobre os dados do catálogo.
- **Agreed in round**: F-01
- **Frame sha256**: 2f253b41a1cd9fcaae8571fe13d3cd4aa540a6f8650a7448fdf2314b74010bdf
- **Supersedes**: —
- **Anchors**: falta de sistema único/email/folha de cálculo → C-002; preço nem sempre actualizado → C-004; sem confirmação de recepção (assumido) → A-002; sentido por compras → R-001; divergências reportadas na reconciliação com a contabilidade → A-001; custa hoje (sem envelope quantificado) → A-004, A-005 (bloqueado por U-001, U-009, U-010); regras do negócio → M-1, M-2, M-3, M-4; limiar financeiro → C-006; âmbito autorizado → C-008
- **Override used at /frame**: X-001 fica em aberto e crítico, sem resposta do dono nem evidência que o resolva (confirmado após passagem R-02 e revisão independente); a passagem R-01 continua sem convergência (10 criadas, 2 fechadas). Decisão do dono: avançar mesmo assim — X-001 não fica dado por resolvido, fecha antes de qualquer entrega final que dependa dele.
- **Validated by**: owner (director de sistemas de informação, via AskUserQuestion)
- **Timestamp**: 2026-09-24T12:10:00Z

## D-002 — Adopt O-002 — Pedido, aprovação e encomenda, app orientada a registos (model-driven) sobre o Dataverse

- **The aisa recommended**: no recommendation — options.md#Recommendation: "U-002 (o contexto/dispositivo do requerente) decide entre O-001 e O-002."
- **Chosen option**: O-002 — Pedido, aprovação e encomenda — app orientada a registos (model-driven) sobre o Dataverse
- **Recommendation followed?**: n/a — o aisa não recomendou entre O-001/O-002 (multiple defensible options, options.md#Recommendation); o dono escolheu com base no custo mais baixo (30–38 vs 40–50 dias) e no facto de o acesso móvel extra de O-001 não estar confirmado como necessário.
- **Rule change decided**: — (nenhum candidato desta ronda dependia de mudar regra organizacional; a plataforma imposta, C-001, não foi questionada)
- **Selected solution / composition**: aplicação sobre a base de dados governada da plataforma imposta (Dataverse), com ecrãs gerados automaticamente pela shell orientada a registos (model-driven) em vez de desenhados um a um; cobre pedido, aprovação e passagem a compras (âmbito autorizado, C-008); mesmo modelo de dados, regras e mecanismo de duplicados/integração ERP-X de O-001.
- **(Scope, outcome) pairs — UNCOLLAPSED**:
  - whole solution — intervenção tecnológica viável dentro da plataforma imposta (C-001), condicional ao mesmo trio de O-001 (U-006, U-011, U-012) mais o forfeit de acesso móvel (U-002/U-013)
- **Conditions**:
  - Mecanismo de auditoria desenhado e confirmado (U-006) — role: director de sistemas de informação / role: auditoria interna — funded? not named — by when: antes do /blueprint fechar
  - Entitlement/licenciamento das 5 populações confirmado (U-011) — role: director de sistemas de informação — funded? not named — by when: not named (options.md dizia "antes de /decide"; não fechou — passa a precondição do blueprint)
  - Interface do ERP-X confirmada, para U-004 (U-012) — role: director de sistemas de informação / fonte: ERP-X (documentação técnica) — funded? not named — by when: antes de fechar U-004
  - Confirmar que o acesso não é predominantemente móvel, ou que a app nativa é instalável/licenciada para os requerentes (U-002, U-013) — role: director de sistemas de informação — funded? not named — by when: not named (o dono respondeu "não sei" a U-002 nesta ronda; ver tripwire TW-1)
- **Proof obligations**: bounded pilot (mesma UAT de O-001) — level not named — method: UAT com submissão concorrente do mesmo conteúdo (mitigação de R-003) — owner: role: director de sistemas de informação — funded? não avaliado
- **Preconditions**: as quatro Conditions acima; nenhuma adicional nomeada pelas fontes
- **Justification**: "Cumpre as três regras que ninguém pode quebrar (segregação da chefia [M-1], limiar da direcção financeira [M-2/C-006], registo para auditoria por desenhar — não bloqueado como em O-003 [M-3/U-006] — e conservação dos documentos [M-4]), pelas mesmas condições de O-001, por menos dias (30–38 vs 40–50). O acesso móvel que O-001 dá a mais não está confirmado como necessário — já disse não sei ao contexto/dispositivo do pedido (U-002) — logo não pago o extra sem essa confirmação." (resposta literal do dono)
- **Alternatives considered**:
  - O-001 — mais caro sem que o acesso móvel esteja confirmado como necessário (U-002).
  - O-003 — bloqueante: não impõe o limiar de 5 000€ (M-2) ao nível de segurança, quebra regra que não se pode quebrar.
  - O-004 — não cobre de forma fiável o registo para auditoria (M-3) além do email actual.
  - O-005 — não muda nada; riscos abertos (R-003, R-004) continuam.
- **Accepted assumptions**: A-001 (impacto qualitativo, sem medição de frequência/custo) — accepted; A-002 (confirmação visível como causa dos duplicados) — accepted. "Aceito ambas como base da decisão." (resposta literal do dono)
- **Accepted risks**: R-003 (duplicados), R-004 (cópia de preços), U-011 (licenças por verificar), U-013 (público não-móvel por confirmar). Nota do dono (literal): "Aceito R-003 e R-004 (duplicados e arredondamento, já conhecidos — C6/C3), e os específicos de O-002: U-011 (licenças por verificar) e U-013 (público não-móvel por confirmar). Nenhum destes toca a segregação da chefia, o limiar da direcção financeira, a auditoria ou a conservação — por isso aceito. Não acrescento nenhum novo." Nenhum risco novo acrescentado.
- **Revision conditions / Tripwires (estruturados)**:
  - TW-1: Se se confirmar que o pedido tem de ser feito a partir de telemóvel ou fora do escritório (U-002) → rever para O-001 (sem contrafactual congelado — sem `/simulate` nesta ronda; ver `/revisit` quando o tripwire disparar)
  - TW-2: Se a auditoria reprovar o mecanismo de registo (U-006/U-011) → rever a opção
  - TW-3: Se se confirmar que as licenças necessárias não estão disponíveis (U-011) → rever a opção
  - TW-4: Se chegar um pedido urgente acima do limiar de 5 000€ (M-2/C-006) antes de X-001 fechar → travar o processamento automático, forçar aprovação manual (proposto pelo premortem.md; aceite pelo dono)
  (Fontes: respostas do dono [TW-1..3] + candidato de premortem.md aceite explicitamente [TW-4].)
- **Sponsor confirmation**: pending — ainda não confirmado
- **Supersedes**: —
- **Decided in round**: D-01
- **Timestamp**: 2026-09-24T13:10:00Z
