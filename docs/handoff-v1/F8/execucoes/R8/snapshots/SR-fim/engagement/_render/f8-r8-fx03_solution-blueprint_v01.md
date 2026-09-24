# Architecture Blueprint — Pedido de Equipamento Informático

> A projecção legível da **camada de arquitectura registada**. Audience: solution architect / lead
> developer / tech lead.
>
> **Projecta; não decide.** Autorização, modo de experiência, autoridade de registo, composição,
> relocação de âmbito e padrão são **lidos** do registo — nunca derivados, escolhidos, pontuados,
> promovidos ou rebaixados aqui. Nenhuma arquitectura candidata é selecionada. Nenhum lado externo
> de uma fronteira é desenhado.
>
> **Altitudes que este documento não carrega**: sumário executivo (→ Relatório Executivo), esforço
> ou estimativa (→ Estimativa), comparação de alternativas (→ Relatório Executivo, altitude de
> decisão).

## Orientação

O-002 é uma aplicação orientada a registos (model-driven) sobre a loja de dados governada da
plataforma imposta, cobrindo pedido → aprovação → passagem a compras (`C-008`) com ecrãs gerados
pela shell orientada a registos em vez de desenhados um a um.

## Base de decisão

**Âmbito e resultado (não colapsado)**: solução completa — intervenção tecnológica viável dentro
da plataforma imposta (`C-001`), condicional ao mesmo trio de O-001 (`U-006`, `U-011`, `U-012`)
mais o forfeit de acesso móvel (`U-002`/`U-013`).

**Condições**: mecanismo de auditoria confirmado (`U-006`, antes do blueprint fechar) ·
entitlement das 5 populações confirmado (`U-011`) · interface do ERP-X confirmada (`U-012`, antes
de fechar `U-004`) · acesso não predominantemente móvel ou app nativa instalável/licenciada
(`U-002`, `U-013`). **Pré-condições**: as mesmas quatro; nenhuma satisfeita à data.

**Obrigações de prova**: viabilidade do mecanismo de duplicados e da base de segurança/auditoria
de O-002 — nível not named, método bounded pilot (mesma UAT de O-001, submissão concorrente),
dono director de sistemas de informação, financiada não avaliado.

**Tripwires**: `TW-1` (acesso móvel confirmado → rever para O-001) · `TW-2` (auditoria reprova
registo → rever) · `TW-3` (licenças em falta → rever) · `TW-4` (pedido urgente acima do limiar
antes de `X-001` fechar → travar automação, forçar aprovação manual).

## Arquitectura

**Versão lida**: `v01` (`_blueprint/ux-blueprint_v01.yaml`) — a mais recente autorizada.
**Estado**: **não aprovada — 1 escolha estrutural em aberto** (a autoridade de registo do
catálogo de preços, `U-004`/`U-012`); nenhum `D-NNN` de aprovação do blueprint existe em
`decisions.md`.

### A1 — Autorização e âmbito

Um único par `(âmbito, resultado)`: **solução completa** — `authorization: authorized`. Base de
outcome (verbatim, `decisions.md#D-002`): "intervenção tecnológica viável dentro da plataforma
imposta (`C-001`), condicional ao mesmo trio de O-001 (`U-006`, `U-011`, `U-012`) mais o forfeit
de acesso móvel (`U-002`/`U-013`)". Base de arquitectabilidade: a solução escolhida é uma
aplicação da plataforma imposta, arquitectável por este pacote em qualquer modo de experiência
(`architecture-templates/README.md` §4). Não há âmbito `authorized-bounded` nesta versão — nada
fica fora por relocação.

### A2 — Intenção arquitectural

Cobrir pedido → aprovação → passagem a compras (`C-008`) com a shell orientada a registos a gerar
os ecrãs em vez de os desenhar um a um, herdando segurança de linha/coluna e auditoria da loja
governada. Composição por omissão: `direct` (sem composição fora da plataforma, `compositions: []`).
Nenhuma escalada foi forçada por requisito nomeado nesta versão.

### A3 — Contexto e fronteiras

| Componente | Papel | Governação da plataforma | Fronteira de confiança atravessada | Owner | Classificação de dados |
|---|---|---|---|---|---|
| pedido-aprovacao (loja governada) | autoridade de registo — Pedido, LinhaPedido, RegistoAprovacao | in-platform | não | director de sistemas de informação (Assumed, `C-008`) | dados de negócio (pedido/aprovação); financeiro (valor_total) |
| ItemCatalogo | referência de catálogo — sem autoridade de registo decidida | não determinado — pendente | não determinado | não determinado | preço/catálogo (sensibilidade não declarada) |

Nenhuma composição fora da plataforma nesta versão. A única fronteira ainda por decidir é a do
catálogo de preços — se resolver para leitura em tempo real do ERP-X, essa composição ainda não
foi desenhada.

**Imagem de contexto / sequência**: `not applicable — nenhum caminho composto ou assíncrono existe
nesta versão (compositions: [])`.

### A4 — Aplicação e responsabilidades de superfície

*(fragmento `owned-internal`)*

#### A4.1 — Superfície e audiência interna

**Superfície primária**: aplicação orientada a registos (model-driven) — `app.name: "Pedido de
Equipamento Informático"`; alvos de dispositivo registados: desktop browser, tablet browser
(`app.device_targets`). Cinco personas usam a superfície: requerente (registos próprios, `C-002`,
`U-002`), chefia (equipa/departamento, `M-1`, `C-002`), compras (organização, `C-002`, `C-004`),
direcção financeira (organização, `M-2`, `C-006`), auditoria interna (organização, leitura
apenas, `M-3`).

#### A4.2 — Arquitectura de ecrãs (handoff)

Três ecrãs registados no blueprint aprovado-candidato:

| Ecrã | Padrão | Persona primária | Entidade | Estado UI |
|---|---|---|---|---|
| PedidoListScreen | Gallery/List | requerente, chefia, compras, direcção financeira | Pedido | loading, empty, error |
| PedidoFormScreen | Form (subgrid LinhaPedido + RegistoAprovacao) | requerente, chefia, direcção financeira, compras | Pedido | loading, empty (sem linhas), error |
| RegistoAprovacaoListScreen | Gallery/List (read-only) | auditoria interna, compras | RegistoAprovacao | loading, empty, error |

Navegação: cada persona entra por `PedidoListScreen`, filtrada por papel (próprios / pendentes de
aprovação / aprovados por encomendar / pendentes acima do limiar); auditoria interna entra
directamente em `RegistoAprovacaoListScreen`. `PedidoListScreen → PedidoFormScreen →
RegistoAprovacaoListScreen` (subgrid/relacionado, mesmo pedido). Aprovação é acção no formulário —
nunca um ecrã dedicado. Este é um **handoff** para o desenho aprovado; a Especificação de
Implementação e o Claude Design Brief permanecem bloqueados enquanto a versão não for aprovada
(§ Arquitecturas candidatas).

#### A4.3 — Caminhos de acesso delegation-safe

**Gap — não registado nesta versão do desenho.** O blueprint não nomeia, por caminho de acesso,
o que é delegation-safe contra a loja seleccionada nem a consequência de cada caminho não-delegável.
Owner: `architecture`.

#### A4.4 — Distribuição

`not applicable — não registado nesta versão do desenho (modelo de partilha, concessão de acesso
e o que acontece a um utilizador que muda de papel não constam do blueprint)`.

#### A4.5 — Offline e capacidade de dispositivo

`not applicable — sem requisito de offline registado`.

#### A4.6 — Forfeits da superfície escolhida

Browser de telemóvel não suportado pela shell orientada a registos — trade-off aceite na decisão
(`D-002`, risco `U-013`), condicional ao fecho de `U-002`; gatilho de revisão `TW-1`.

#### A7 (especialização) — modelo de papéis do utilizador humano

Cinco papéis, âmbito próprio cada: requerente (registos próprios), chefia (equipa/departamento,
aprovação limitada ao limiar `M-2`), direcção financeira (organização, aprovação acima do
limiar), compras (organização, regista encomenda), auditoria interna (organização, leitura
apenas, sem escrita).

#### A8 (especialização) — ciclo de vida próprio

**Gap — não registado nesta versão do desenho** (ambientes ocupados, rota de release). Owner:
`architecture`.

### A5 — Autoridade de dados e stores

Um domínio de autoridade de registo nesta versão: `pedido-aprovacao` (loja governada,
`access_mode: owned`), cobrindo Pedido, LinhaPedido e RegistoAprovacao. `ItemCatalogo` **não tem
autoridade de registo definida** — `authority: none — pendente da escolha estrutural em
open_architecture_choices (U-004/U-012)` — lacuna nomeada, não um conjunto vazio silencioso.

| Domínio (`key`) | access_mode | Entidades | Estado |
|---|---|---|---|
| pedido-aprovacao | owned | Pedido, LinhaPedido, RegistoAprovacao | 2 `Confirmed` (`valor_total`, `valor_linha` — fórmula `C-005`/`C-007`), demais `Assumed`; `schema_owner`: director de sistemas de informação (Assumed, `C-008`) |
| (nenhum — ItemCatalogo) | — | referenciada por `LinhaPedido.item_catalogo` | entidade sem autoridade — ⚠️ lacuna — entidade sem autoridade de registo — dono: architecture — resolve-se com: `key` do domínio ou racionalização, condicional a `U-004`/`U-012` |

**Dicionário — Pedido** (owned): `requerente` (reference, required, Assumed) · `data_pedido`
(datetime, computed, Assumed) · `urgente` (boolean, default false, Assumed) ·
`justificacao_urgencia` (text, obrigatório se `urgente=true`, Assumed) · `estado` (choice —
Rascunho/Submetido/Aprovado chefia/Aprovado direcção financeira/Rejeitado/Encomendado, Assumed;
regra: "Aprovado direcção financeira" só acima do limiar `C-006`, caminho de urgência face a este
estado por fechar — `X-001`; transição Rascunho→Submetido bloqueada por verificação atómica de
duplicado, plug-in síncrono/custom API em transacção, mitigação `R-003`) · `valor_total` (number,
computed, **Confirmed**, `C-005`/`C-007`).

**Dicionário — LinhaPedido** (owned): `pedido` (reference, Assumed) · `item_catalogo` (reference,
**Unknown** — "a proveniência do catálogo fica em aberto — ver open_architecture_choices",
depende de `U-004`/`U-012`) · `quantidade` (number, >0, Assumed) · `preco_unitario` (number,
snapshot no momento do pedido — não sincroniza com alterações posteriores, Assumed, depende de
`U-004`/`U-012` para o mecanismo de cópia) · `valor_linha` (number, computed, **Confirmed**,
`C-005`).

**Dicionário — RegistoAprovacao** (owned): `pedido` (reference, Assumed) · `aprovador` (reference,
utilizador autenticado, Assumed) · `papel` (choice — chefia/direcção financeira, Assumed) ·
`decisao` (choice — aprovado/rejeitado, Assumed) · `data_hora` (datetime, computed, **Confirmed**,
`M-3` exige quando) · `comentario` (text, opcional, Assumed).

**Conditional — responsabilidade analítica**: `not applicable — nenhum reporting força uma
segunda loja ou cópia nesta versão`.

### A6 — Automação e integração

Nenhuma integração confirmada nesta versão. A única candidata (leitura do catálogo de preços do
ERP-X) depende de dois factos por confirmar: existe interface programável (`U-012`)? e, se
existir, lê-se em tempo real ou mantém-se cópia própria (`U-004`)? Perguntados directamente ao
dono nesta ronda — resposta literal "não sei" às duas (`council-log.md`). Mecanismo de
verificação de duplicados: regra de correspondência (mesmo requerente + conteúdo semelhante +
janela curta), mitigação `R-003` — nomear mecanismo exacto (regra activada nas escritas Web
API/fluxo, ou verificação+criação atómica num plug-in síncrono/custom API em transacção) fica
como obrigação antes da aprovação; comportamento de retry: nunca reencomendar cegamente em erro
de servidor. Guarantee/idempotência: por decidir (ver escolha estrutural).

### A7 — Identidade e ponto de imposição da autorização

Cinco papéis (personas), cada um com âmbito próprio (ver A4.1/A4 especialização). Plano de
imposição: segurança de linha/coluna herdada da loja governada, mais uma entidade de negócio
dedicada (`RegistoAprovacao`) que regista explicitamente quem aprovou o quê e quando (`M-3`),
independente do log de auditoria de sistema. Sem separação de permissões adicional além dos cinco
papéis; sem ecrã de assinatura — a aprovação é comportamento do processo (estados e transições,
papel autorizado em cada uma).

### A8 — Ambientes, governação e topologia de release

**Gap — não registado nesta versão do desenho.** Ambientes, vinculação de residência, plano de
política e rota(s) de release não constam do blueprint nem da síntese de arquitectura. Owner:
`architecture`.

### A9 — Escolhas irreversíveis e saída

**Gap — não registado nesta versão do desenho** (tipo de propriedade, publisher, região/
residência, instalação de app first-party, geração de controlo, graduações unidireccionais,
custo de saída). Owner: `architecture`.

**Conditional — substituição de artefacto existente**: `not applicable — nenhum outcome de
migração obrigatória registado nesta versão`.

### A10 — Operabilidade, suporte e modelo de operação

**Gap — não registado nesta versão do desenho.** Nenhum papel, identidade, mecanismo de detecção,
destino de alerta ou procedimento de recuperação por caminho de falha consta do blueprint; nem a
rota de suporte. Owner: `architecture`. (Nota do contrato: um operador **sem nome** não seria, por
si só, uma escolha estrutural — mas a ausência do próprio modelo de operação, papel/mecanismo/
recuperação nenhum, é diferente e fica registada como lacuna, não como escolha estrutural
adicional, já que o blueprint não a nomeia sequer como tal.)

### A11 — Economia e consequências de entitlement

Driver de custo nomeado: entitlement/licenciamento das 5 populações para a loja de dados
governada da plataforma imposta — ainda por confirmar (`U-011`); se o ambiente gerido exigir
entitlement premium para toda a população, o custo muda e pode mudar a viabilidade económica do
candidato, não só o preço (`library/packs/pp/domain-knowledge/economics/licensing-and-cost-drivers.md`
§5-6 §15, VC-05; `M-3`, `M-4` despoletam a cadeia controlo-mandatado→entitlement do pacote).
Nenhum preço, SKU ou quota é declarado aqui — apenas o driver.

### A12 — Obrigações de prova e livro epistémico

**Obrigação de prova**: viabilidade do mecanismo de duplicados e da base de segurança/auditoria de
O-002 — nível not named · método bounded pilot (mesma UAT de O-001, submissão concorrente do
mesmo conteúdo) · dono director de sistemas de informação · financiada não avaliado.

**Linhas em que esta arquitectura assenta** (estado · `verificado_em` / `validade`):
`C-002`, `C-004`, `C-005`, `C-006`, `C-007`, `C-008`, `M-1`, `M-2`, `M-3`, `M-4`, `D-002` —
Confirmed, 2026-09-24, organizacional/financeiro; `U-001`, `U-002`, `U-004`, `U-006`, `U-011`,
`U-012`, `U-013` — Unknown, abertas; `X-001` — Conflicted, aberto, nenhum lado escolhido; `R-003`,
`R-004` — Risky, identidade de risco aceite preservada.

**`open_architecture_choices[]`**:

1. **Escolha**: autoridade de registo e mecanismo de integração para o Item de Catálogo (ler o
   ERP-X em tempo real, por connector, vs manter cópia própria replicada) — o preço é copiado
   (snapshot) para `LinhaPedido.preco_unitario` em qualquer dos dois casos, mas o Item de
   Catálogo em si não tem autoridade de registo decidida. **Estrutural: sim.** Resolve-se com:
   confirmação técnica de que o ERP-X expõe interface programável (`U-012`) + decisão do director
   de SI sobre tempo real vs cópia própria (`U-004`). `su_ref`: `U-004`.
2. **Escolha**: dimensionamento de entitlement/licenciamento das 5 populações para o ambiente
   governado — pode mudar a viabilidade económica do candidato, não só o custo. **Estrutural:
   não.** Resolve-se com: verificação VC-05 (`licensing-and-cost-drivers.md`) e resposta do
   director de SI. `su_ref`: `U-011`.

Uma entrada `structural: true` bloqueia a **aprovação** deste blueprint — não a sua produção; por
consequência, a Especificação de Implementação e o Claude Design Brief ficam bloqueados.

**Conditional — propriedade de âmbitos**: `not applicable — um único par (âmbito, resultado)
existe nesta decisão`.

## Narrativa de arquitectura

Nenhuma composição fora da plataforma nesta versão (`compositions: []`) — toda a lógica (registo
do pedido, transições de aprovação, verificação de duplicados) corre dentro da loja governada, em
regras/transacções síncronas, sem cruzar fronteira de confiança. A única fronteira ainda por
decidir é a do catálogo de preços: se resolver para leitura em tempo real do ERP-X, essa
composição ainda não foi desenhada — falta um facto técnico (`U-012`) para poder ser tomada.

Nenhuma integração está confirmada; a única candidata (leitura de preços do ERP-X) depende de dois
factos por confirmar (`U-004`, `U-012`), perguntados directamente ao dono nesta ronda — resposta
literal "não sei" às duas. Sem classificação de política DLP possível enquanto o mecanismo não for
escolhido.

## Propriedade de âmbitos — categorias de projecção

`not applicable — um único par (âmbito, resultado) existe nesta decisão; não há mais do que um
para categorizar.`

## Arquitecturas candidatas

**Escolha estrutural em aberto**: autoridade de registo e mecanismo de integração do catálogo de
preços (`ItemCatalogo`). Duas formas materialmente distintas, nenhuma escolhida:

- **Candidata A — leitura em tempo real do ERP-X, por connector directo.** Exequível apenas se o
  ERP-X expuser interface programável (`U-012`, resposta do dono: "não sei"). O preço seria lido
  no momento do pedido, sem cópia local.
- **Candidata B — cópia própria replicada (como a folha de compras faz hoje).** Reproduz o
  anti-padrão de cache já registado como risco (`R-004`) se não vier acompanhada de dono de
  reconciliação nomeado, cadência definida e método de deteção de drift diferente de contagem de
  linhas.

Resolve-se com: confirmação técnica de que o ERP-X expõe interface programável (`U-012`) +
decisão do director de SI sobre tempo real vs cópia própria (`U-004`). Nenhuma pontuação, nenhum
ranking, nenhuma recomendação nesta secção.

## Livro epistémico e validade

- **Confirmed** (2026-09-24 / organizacional ou financeiro, nenhuma expirada): `C-002`, `C-004`,
  `C-005`, `C-006`, `C-007`, `C-008`, `M-1`–`M-4`, `D-002`.
- **Assumed** (2026-09-24 / organizacional): 15 dos 17 campos do domínio `pedido-aprovacao`;
  `schema_owner` (director de sistemas de informação, `C-008`).
- **Unknown**: `LinhaPedido.item_catalogo` e `LinhaPedido.preco_unitario` (mecanismo de cópia)
  dependem de `U-004`/`U-012`; ver *Arquitecturas candidatas*.
- **Conflicted**: `X-001` — caminho de urgência vs limiar financeiro; nenhum lado carregado aqui.
- **Risky**: `R-003` (duplicados), `R-004` (cópia de catálogo) — identidade de risco preservada,
  não mitigada por esta arquitectura.
- **Obrigação de prova**: ver A12.
- **`open_architecture_choices[]`**: ver A12 (1 estrutural, 1 não estrutural).

**Itens em aberto não tornam este documento incompleto — tornam-no honesto.**

---
> **Nota de estado (§8.2, este passo)**: a revisão de blueprint a montante que este deliverable
> consome (`_coverage/coverage_v09.json`) tem `freshness: stale` / `coverage: gaps` /
> `eligible: false` — a base mudou desde a revisão; é preciso rever os impactos antes de usar.
> Este documento é produzido para discussão; não se anuncia como completo, e a aprovação continua
> bloqueada pela escolha estrutural em aberto.
