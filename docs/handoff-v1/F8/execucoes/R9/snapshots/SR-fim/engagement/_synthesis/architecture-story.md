# Architecture Story — f8-r3-fx02
<!-- authority: _blueprint/ux-blueprint_v01.yaml#architecture @ sha256:35ed268189e920e1baeb83b505a50fe479248bc2ea5027ca3d88d1e49b3061b5 -->

## Authorized scope and outcome basis

- whole solution — intervenção tecnológica viável dentro da plataforma imposta (C-001), condicional ao mesmo trio de O-001 (U-006, U-011, U-012) mais o forfeit de acesso móvel (U-002/U-013). (D-002)

`authorization: authorized`. Base do outcome: a frase acima, verbatim de `decisions.md#D-002`. Base de arquitectabilidade: a solução escolhida é uma aplicação da plataforma imposta (Power Apps model-driven + Dataverse) — arquitectável por este pacote em qualquer modo de experiência (`architecture-templates/README.md` §4). Nenhuma das duas bases é reavaliada aqui — são projectadas, não reinterpretadas.

## Chosen architecture

Opção escolhida: O-002 — Pedido, aprovação e encomenda, app orientada a registos (model-driven) sobre a loja de dados governada da plataforma imposta. Intenção arquitectural: cobrir pedido → aprovação → passagem a compras (C-008) com a shell orientada a registos a gerar os ecrãs em vez de os desenhar um a um, herdando segurança de linha/coluna e auditoria da loja. Justificação registada na decisão (D-002, verbatim em substância): cumpre as três regras que não se podem quebrar (segregação da chefia M-1, limiar da direcção financeira M-2/C-006, registo para auditoria M-3/U-006, conservação M-4), pelas mesmas condições de O-001, por menos dias (30–38 vs 40–50); o acesso móvel extra de O-001 não está confirmado como necessário (U-002, ainda "não sei"). Nenhuma comparação nova é feita aqui — as alternativas rejeitadas (O-001, O-003, O-004, O-005) e o porquê de cada uma constam de `decisions.md#D-002 — Alternatives considered`.

## Composition, components and boundaries

Nenhuma composição fora da plataforma nesta versão (`compositions: []`) — toda a lógica (registo do pedido, transições de aprovação, verificação de duplicados) corre dentro da loja governada, em regras/transacções síncronas, sem cruzar fronteira de confiança. A única fronteira ainda por decidir é a do catálogo de preços (ver Escolhas em aberto): se resolver para leitura em tempo real do ERP-X, essa composição ainda não foi desenhada — é, por natureza, uma decisão que falta um facto técnico para poder ser tomada.

## Imported obligations

Não aplicável — nenhum componente qualificado (`boundary: outside-platform` ou composição além de `direct`) existe nesta versão; nenhuma responsabilidade foi realocada para fora da plataforma.

## Data

Um domínio de autoridade de registo nesta versão: `pedido-aprovacao` (loja governada, `access_mode: owned`), cobrindo as entidades Pedido, LinhaPedido e RegistoAprovacao — 17 campos desenhados, todos `state: Assumed` ou `Confirmed` (source: design/SU, nunca L1 — não há workbook `.xlsx` neste engagement). O domínio do catálogo de preços (ItemCatalogo) não tem autoridade de registo definida (`authority: none — pendente da escolha estrutural`, U-004/U-012) — lacuna nomeada, não silenciosa.

| Domínio (`key`) | access_mode | Campos/Contrato | Relações | Estado |
|---|---|---|---|---|
| pedido-aprovacao | owned | 17 campos (Pedido: 6, LinhaPedido: 4, RegistoAprovacao: 6, sendo 2 computed) | LinhaPedido→Pedido, RegistoAprovacao→Pedido | 2 Confirmed (valor_total, valor_linha — fórmula C-005/C-007), 15 Assumed, 0 Unknown na loja governada; `schema_owner`: director de sistemas de informação (Assumed, C-008) |
| (nenhum — ItemCatalogo) | — | — | LinhaPedido→ItemCatalogo (referência) | entidade sem autoridade — lacuna: dono `architecture`, resolve-se com `key` do domínio ou racionalização, condicional a U-004/U-012 |

## Integrations

Nenhuma confirmada. A única candidata (leitura do catálogo de preços do ERP-X) depende de dois factos por confirmar: existe interface programável (U-012)? e, se existir, lê-se em tempo real ou mantém-se cópia própria (U-004)? Perguntados directamente ao dono nesta ronda — resposta literal "não sei" às duas (council-log.md). Sem classificação de política DLP possível enquanto o mecanismo não for escolhido.

## Security model

Cinco papéis (personas), cada um com âmbito próprio: requerente (registos próprios), chefia (equipa/departamento, aprovação limitada ao limiar M-2), direcção financeira (organização, aprovação acima do limiar), compras (organização, regista encomenda), auditoria interna (organização, leitura apenas). Plano de imposição: segurança de linha/coluna herdada da loja governada (row/column security inherited from the store — application-surfaces.md §3), mais uma entidade de negócio dedicada (RegistoAprovacao) que regista explicitamente quem aprovou o quê e quando (M-3), independente do log de auditoria de sistema. Sem separação de permissões adicional além dos cinco papéis; sem assinatura — a aprovação é comportamento do processo (estados e transições, papel autorizado em cada uma), não um ecrã de assinatura.

## Watch-list constraints

- Browser de telemóvel não suportado pela shell orientada a registos (`application-surfaces.md` §3, "running it in a phone browser is not supported") — trade-off aceite na decisão (D-002, risco U-013), com condição de revisão: se U-002 confirmar necessidade de acesso móvel e U-013 não resolver a favor → rever para O-001 (TW-1).
- Entitlement/licenciamento das 5 populações não verificado (U-011) — incerteza, aceite como risco em D-002 (TW-3): se confirmarem faltar licenças, rever a opção.
- Autoridade de registo do catálogo de preços por decidir (U-004/U-012) — escolha estrutural em aberto, bloqueia a aprovação desta versão (não a produção).
