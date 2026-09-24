# Relatório Executivo — Pedido de Equipamento Informático

> Documento síntese para o sponsor / C-level. Projecta **a decisão** — o que foi decidido, para que
> âmbitos, sob que condições, com que riscos aceites, e o que forçaria uma revisão. Lê em ~10 minutos.
>
> **Não é um Relatório de Descoberta mais curto** nem um Blueprint de Arquitectura.
>
> **Sem nova comparação.** Reproduz a justificação que a decisão registou e as linhas de *porque não*
> por alternativa tal como ficaram registadas. Não explica porque é que uma arquitectura "ganhou".

## 1. Business case

O director de sistemas de informação respondeu "não sei dizer" quando confrontado com a pergunta
central de sucesso do projecto (`U-008`) — sem critério explícito, a aprovação final do desenho
corre o risco de ser julgada por padrões implícitos e divergentes. Essa lacuna continua aberta;
a decisão desta ronda (`D-002`) não a fechou.

O impacto de negócio é qualitativo, não quantificado: sem número de frequência, tempo ou custo
(`A-001`). O caso de negócio fica dependente do que ainda não foi apurado: frequência (`U-001`),
envelope orçamental do projecto (`U-007`), tempo por passo (`U-009`) e taxa horária carregada
(`U-010`).

## 2. A decisão

Adoptar **O-002** — Pedido, aprovação e encomenda, aplicação orientada a registos (model-driven)
sobre a loja de dados governada da plataforma imposta (Dataverse). Cobre pedido, aprovação e
passagem a compras (âmbito autorizado, `C-008`); usa o mesmo modelo de dados, regras e mecanismo
de duplicados/integração ERP-X de O-001, com ecrãs gerados automaticamente pela shell orientada a
registos em vez de desenhados um a um.

**O aisa não recomendou** entre O-001 e O-002 (`options.md#Recommendation`: "U-002 decide entre
O-001 e O-002"). O dono escolheu com base no custo mais baixo (30–38 vs 40–50 dias) e no facto de
o acesso móvel extra de O-001 não estar confirmado como necessário.

## 3. Âmbitos e resultados — pares não colapsados

| âmbito | resultado (verbatim) |
|---|---|
| solução completa | intervenção tecnológica viável dentro da plataforma imposta (`C-001`), condicional ao mesmo trio de O-001 (`U-006`, `U-011`, `U-012`) mais o forfeit de acesso móvel (`U-002`/`U-013`) |

Um único par `(âmbito, resultado)` nesta decisão — nenhum colapso a fazer.

## 4. Porquê — a justificação registada

> "Cumpre as três regras que ninguém pode quebrar (segregação da chefia [`M-1`], limiar da
> direcção financeira [`M-2`/`C-006`], registo para auditoria por desenhar — não bloqueado como em
> O-003 [`M-3`/`U-006`] — e conservação dos documentos [`M-4`]), pelas mesmas condições de O-001,
> por menos dias (30–38 vs 40–50). O acesso móvel que O-001 dá a mais não está confirmado como
> necessário — já disse não sei ao contexto/dispositivo do pedido (`U-002`) — logo não pago o
> extra sem essa confirmação." (resposta literal do dono, `decisions.md#D-002`)

## 5. Alternativas — o *porque não* registado

- **O-001** — mais caro sem que o acesso móvel esteja confirmado como necessário (`U-002`).
- **O-003** — bloqueante: não impõe o limiar de 5 000 € (`M-2`) ao nível de segurança, quebra
  regra que não se pode quebrar.
- **O-004** — não cobre de forma fiável o registo para auditoria (`M-3`) além do email actual.
- **O-005** — não muda nada; riscos abertos (`R-003`, `R-004`) continuam.

## 6. Condições e pré-condições

| condição | dono | financiada? | até quando |
|---|---|---|---|
| Mecanismo de auditoria desenhado e confirmado (`U-006`) | director de SI / auditoria interna | not named | antes do `/blueprint` fechar |
| Entitlement/licenciamento das 5 populações confirmado (`U-011`) | director de SI | not named | not named |
| Interface do ERP-X confirmada, para `U-004` (`U-012`) | director de SI / fonte: ERP-X | not named | antes de fechar `U-004` |
| Confirmar que o acesso não é predominantemente móvel, ou que a app nativa é instalável/licenciada (`U-002`, `U-013`) | director de SI | not named | not named — o dono respondeu "não sei" a `U-002` nesta ronda |

**Pré-condições**: as quatro condições acima; nenhuma adicional nomeada pelas fontes. Nenhuma
está satisfeita — todas continuam por fechar.

## 7. Riscos aceites

- `R-003` (duplicados) e `R-004` (arredondamento) — já conhecidos, mitigação registada antes do
  blueprint.
- `U-011` — licenças por verificar.
- `U-013` — público não-móvel por confirmar.

Nota do dono (literal): "Nenhum destes toca a segregação da chefia, o limiar da direcção
financeira, a auditoria ou a conservação — por isso aceito. Não acrescento nenhum novo."

## 8. Obrigações de prova que qualificam a decisão

- **Afirmação**: viabilidade do mecanismo de duplicados e da base de segurança/auditoria de O-002.
  **Nível**: not named. **Método**: bounded pilot (mesma UAT de O-001), com submissão concorrente
  do mesmo conteúdo. **Dono**: director de sistemas de informação. **Financiada?**: não avaliado.

## 9. Escolhas estruturais em aberto

- **Escolha**: autoridade de registo e mecanismo de integração para o Item de Catálogo (ler o
  ERP-X em tempo real, por connector, vs manter cópia própria replicada) — o preço é copiado
  (snapshot) para `LinhaPedido.preco_unitario` em qualquer dos dois casos, mas o Item de Catálogo
  em si não tem autoridade de registo decidida.
  **Resolve-se com**: confirmação técnica de que o ERP-X expõe interface programável (`U-012`) +
  decisão do director de SI sobre tempo real vs cópia própria (`U-004`).
  **Bloqueia**: a aprovação da arquitectura — e por consequência a Especificação de Implementação
  e o Design Brief.

## 10. Forma da arquitectura

Autorizada para o âmbito "solução completa": aplicação da plataforma imposta — orientada a
registos (model-driven) sobre a loja de dados governada (Dataverse) — condicional ao mesmo trio
de O-001 (`U-006`, `U-011`, `U-012`) e ao forfeit de acesso móvel (`U-002`/`U-013`). Modo de
experiência: interno, próprio (owned-internal); superfície primária: aplicação orientada a
registos. A autoridade de registo cobre Pedido, Linha de Pedido e Registo de Aprovação; o Item de
Catálogo não tem autoridade de registo decidida (ver §9).

## 11. Porque não existe arquitectura nesta plataforma

Não aplicável — existe autorização de arquitectura para o âmbito "solução completa".

## 12. Economia da decisão

O custo do processo actual está escrito na forma, não no número (`A-005`): nenhum dos três
factores estruturais está medido — volume (`U-001`), tempo por passo (`U-009`), taxa horária
carregada (`U-010`) — pelo que o envelope fica sem valor monetário. Custo de não fazer nada:
qualitativo, sem valor medido (`A-004`). Envelope orçamental e financiamento: **não declarado** —
`U-007` continua aberta, sem resposta nesta ronda. A ronda de Options não produziu comparação
económica formal entre O-001/O-002; o dono escolheu por custo mais baixo em ordem de grandeza
(30–38 vs 40–50 dias). Payback/ROI: **não registado** — sem envelope de custo as-is quantificado
nem critério de sucesso decidido, não há base para calcular.

## 13. Investimento previsto

Não aplicável — a Estimativa ainda não foi produzida para este engagement (`_synthesis/financial-story.md# Investment reference`). Sem estimativa, este parágrafo não se preenche; nada se combina nem se infere.

## 14. Riscos e mitigações

- `R-003` (was `R-001`) — duplicados; mitigação: nomear mecanismo exacto antes do blueprint
  (regra activada nas escritas, ou verificação+criação atómica num plug-in síncrono/custom API em
  transacção), testado em UAT com submissão concorrente. Gatilho: `TW-2`.
- `R-004` (was `R-002`) — cópia local do catálogo como anti-padrão de cache, se `U-004` resolver
  para cópia própria; mitigação: dono de reconciliação, cadência e deteção de drift nomeados.
- `U-011` — entitlement/licenciamento ainda não confirmado; aceite como risco. Gatilho: `TW-3`.
- `U-013` — instalabilidade/licenciamento da app nativa móvel, condicional a `U-002`; aceite como
  risco. Gatilho: `TW-1`.

## 15. Pontos epistémicos abertos que qualificam a decisão

- **Premissas aceites** (`A-001`, `A-002`) — impacto qualitativo, sem medição; confirmação visível
  como causa dos duplicados. Aceites como base da decisão, sem serem testadas primeiro.
- **Conflito não resolvido** (`X-001`, Critical) — o caminho de urgência salta a aprovação prévia
  da chefia; não está declarado se também salta a aprovação da direcção financeira acima do
  limiar. Nenhum lado escolhido aqui. Fecha só por decisão do dono, antes de qualquer entrega
  final que dependa dele.
- **Unknowns críticos por resolver**: nenhuma — a única Unknown Critical (`U-005`, valor do
  limiar) já foi respondida (`C-006`).
- **Confirmed expirados**: nenhuma linha `Confirmed`/`Assumed` está fora da validade declarada
  nesta data.

## 16. O que forçaria uma revisão (tripwires)

| id | condição | resposta |
|---|---|---|
| `TW-1` | Confirmar-se que o pedido tem de ser feito a partir de telemóvel ou fora do escritório (`U-002`) | rever para O-001 (sem contrafactual congelado — sem `/simulate` nesta ronda) |
| `TW-2` | A auditoria reprovar o mecanismo de registo (`U-006`/`U-011`) | rever a opção |
| `TW-3` | Confirmar-se que as licenças necessárias não estão disponíveis (`U-011`) | rever a opção |
| `TW-4` | Chegar um pedido urgente acima do limiar de 5 000 € (`M-2`/`C-006`) antes de `X-001` fechar | travar o processamento automático, forçar aprovação manual |

## 17. O que acontece a seguir

As quatro condições da secção 6 continuam por fechar. Condições de revisão: as quatro tripwires
acima. **Confirmação do sponsor**: pending — ainda não confirmada (`decisions.md#D-002`).

---
> **Nota de estado (§8.2, este passo)**: a revisão de reconciliação a montante que este
> deliverable consome (`_coverage/coverage_v13.json`) tem `coverage: gaps` / `eligible: false` —
> ainda por fechar. Este documento é produzido para discussão; não se anuncia como completo.
