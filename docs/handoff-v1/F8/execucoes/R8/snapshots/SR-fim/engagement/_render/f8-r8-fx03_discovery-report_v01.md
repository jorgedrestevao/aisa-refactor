# Relatório de Descoberta — ⚠️ missing: solution_name (ver render-gaps.md)

> Documento de descoberta para o sponsor e stakeholders. Projecta o estado do conhecimento da
> iniciativa — o que está confirmado, o que é assumido, o que continua aberto, o que está em
> conflito e o que é arriscado — no estado em que o Shared Understanding o registou.
>
> **Neutro em tecnologia por construção.** Não recomenda, não decide, não descreve arquitectura
> e não nomeia fornecedores ou produtos (`.claude/rules/no-tech-mention-before-options.md`).
>
> **Compressão é permitida; promoção epistémica não.** Onde linhas abertas foram omitidas por
> imaterialidade, o número residual é declarado — a compressão é visível, nunca silenciosa.

## 1. Contexto de negócio

O pedido chegou tal como está escrito: "Queremos digitalizar os pedidos de equipamento
informático (portáteis, monitores, acessórios)" (`context.json#literal_request`), do director de
sistemas de informação, que já tinha decidido a plataforma por deliberação interna
(DSI-SINT-07, `C-001`). A frase que resume o problema (`D-001`): falta um sistema único para
pedir, aprovar e encomendar equipamento — hoje tudo corre por email e por uma folha de cálculo
(`C-002`), sem preço sempre actualizado (`C-004`) e, segundo o responsável de compras, sem
confirmação de recepção que evite reenvios (assumido, `A-002`).

Quem pede (director de SI) não é quem sente a dor. A dor concreta é sentida por compras —
retrabalho com encomendas a dobrar (`R-003`, was `R-001`) — e, na reconciliação, por divergências
de arredondamento reportadas à contabilidade (`A-001`; ainda por confirmar se a contabilidade
sente o mesmo impacto). Cinco populações distintas usam o processo: requerente, chefia, compras,
direcção financeira, auditoria interna, cada uma com tarefa e regra próprias (`M-1`, `M-2`,
`M-3`; os documentos de compra têm de ser conservados 10 anos, `M-4`).

## 2. Estado actual — resumo

1. O colaborador (requerente) pede equipamento por email (`C-002`).
2. A chefia aprova ou rejeita por email — nunca aprova o seu próprio pedido (`M-1`).
3. Compras regista o pedido numa folha de cálculo e faz a encomenda (`C-002`), usando uma cópia
   manual do catálogo de preços que vive de facto no ERP-X (`C-004`).
4. Acima do limiar de 5 000 €/pedido (`C-006`), o pedido tem de ir à direcção financeira
   (`M-2`) — o ponto exacto em que isso acontece no fluxo normal não está descrito para além do
   limiar em si.
5. Excepção: pedidos urgentes (avaria que impede trabalhar) vão directamente a compras; a chefia
   tem até ao fim do dia útil seguinte para validar — já não no mesmo dia — e, sem validação
   dentro desse prazo, compras suspende a encomenda até haver validação (`A-006`, was `C-003`).
   Não está declarado se esta via também salta a validação da direcção financeira quando o valor
   ultrapassa o limiar — conflito aberto, `X-001`, sem resposta nesta nota.

**Volume e tempo de ciclo**: nem o volume (pedidos por dia/semana/mês, `U-001`) nem o tempo de
ciclo por passo (`U-009`) foram medidos — ambos ficam em aberto, sem número inventado. A fórmula
do custo as-is já está escrita (`A-005`: volume × tempo por passo × taxa horária carregada +
custo dos duplicados + custo das divergências), mas os três factores (`U-001`, `U-009`, `U-010`)
continuam por preencher. Sem total de ciclo — nenhum dos quatro passos regulares tem duração
medida.

## 3. Processos identificados

Um único processo, ponta a ponta: pedido → aprovação → registo e encomenda em compras, com um
ramo de excepção para avarias urgentes. Cinco populações participam sem nenhuma tarefa
estruturada de ecrã — tudo corre hoje por email e folha de cálculo: requerente, chefia, compras,
direcção financeira, auditoria interna. O contexto real de uso do requerente (secretária vs
terreno, dispositivo, ligação) não foi declarado e fica em aberto (`U-002`).

## 4. Inventário de dados
> Uma linha por elemento de dados: elemento · onde vive hoje · dono · sensibilidade · id · estado
> (`Confirmed`/`Assumed`) · `verificado_em` / `validade`. Um valor volátil sem selo não é facto.

| elemento | onde vive hoje | dono | sensibilidade | id | estado | verificado_em / validade |
|---|---|---|---|---|---|---|
| catálogo de equipamento com preços em vigor | fonte de verdade: ERP-X; cópia mantida à mão na folha de compras | não declarado | não declarada | `C-004` | Confirmed | 2026-09-24 / organizacional |
| valor do pedido (regra de cálculo) | não aplicável — regra de cálculo (quantidade × preço unitário por linha, somado, mais IVA à taxa normal), não um dado armazenado | não declarado | financeiro (implícito) | `C-005` | Confirmed | 2026-09-24 / financeiro |
| arredondamento (regra) | aplicado só ao total do pedido, ao cêntimo, meio-para-cima | não declarado | financeiro (implícito) | `C-007` | Confirmed | 2026-09-24 / organizacional |
| registo dos pedidos | disperso entre email e a folha de cálculo de compras — sem sistema único hoje | não declarado | não declarada | `A-003` | Assumed | 2026-09-24 / organizacional |

## 5. Pontos de fricção identificados

- Pedidos duplicados por reenvio — o requerente julga que o email não chegou e reenvia, sem
  confirmação de recepção (`R-003`, causa em `A-002`).
- Cópia manual do catálogo de preços, sem cadência de actualização definida — risco de preços
  desactualizados na encomenda (`R-004`).
- Arredondamento indefinido até esta ronda — já causou divergências reais com a contabilidade
  antes de ser resolvido (`C-007`).
- Via de urgência sem regra clara face ao controlo financeiro (`X-001`) — ainda aberta.
- Ausência de rasto fiável de aprovações para a auditoria interna — email e folha de cálculo não
  garantem o registo que `M-3` exige (`U-006`).
- Nenhum critério de sucesso declarado para o projecto (`U-008`).

## 6. Perspectivas e tensões
> As conclusões por perspectiva e as tensões que **sobreviveram** — não resolvidas aqui. Uma
> tensão continua tensão; escolher um lado é proibido neste documento.

O impacto é qualitativo, não quantificado: sem número de frequência, tempo ou custo (`A-001`). O
caso de negócio fica dependente do que ainda não foi apurado: frequência (`U-001`), envelope
orçamental do projecto (`U-007`), tempo por passo (`U-009`) e taxa horária carregada (`U-010`) —
os três últimos alimentam a fórmula do custo as-is já escrita (`A-005`), sem os valores ainda por
dentro.

O que conta como sucesso para o sponsor **ainda não está definido** — o director de SI respondeu
"não sei dizer" quando confrontado com a pergunta central de sucesso; sem critério explícito, a
aprovação final do desenho corre o risco de ser julgada por padrões implícitos e divergentes
entre o dono e os utilizadores (`U-008`).

A tensão que sobrevive sem resolução: o caminho de urgência (`A-006`, was `C-003`) salta a
aprovação prévia da chefia por desenho — mas não está escrito se também salta o controlo
financeiro do limiar de 5 000 € (`M-2`/`C-006`) quando o valor ultrapassa o limiar. Nenhuma fonte
resolve nas duas direcções; o dono respondeu que não tem essa informação (`X-001`). Nenhum dos
dois lados é escolhido aqui.

## 7. Questões abertas (Unknown)
> Uma linha por `U-NNN` material: a pergunta · criticidade · quem pode responder · o que muda se
> resolver.

| id | pergunta | criticidade | quem responde | o que muda se resolver |
|---|---|---|---|---|
| `U-001` | Com que frequência ocorre o processo (pedidos por dia/semana/mês)? | Low | responsável de compras | dimensiona o esforço e o tamanho do desenho pelo volume real |
| `U-002` | Em que contexto os colaboradores fazem hoje o pedido (secretária, terreno, dispositivo, ligação)? | Med | requerente | muda o desenho da interacção e o que o ecrã tem de suportar |
| `U-006` | Que mecanismo regista quem aprovou o quê e quando, de forma fiável (a auditoria exige-o e hoje não existe)? | Med | auditoria interna / director de SI | muda o desenho do mecanismo de registo de aprovações |
| `U-007` | Qual é o envelope orçamental, o modelo de financiamento e o limiar de aprovação para este projecto? | Med | direcção financeira / director de SI | muda a dimensão viável do projecto e o esforço que pode ser gasto |
| `U-008` | Como se sabe que este processo, e o projecto que o digitaliza, correu bem — qual é o critério de sucesso? | Med | director de SI | define o critério de aceitação do desenho final |
| `U-009` | Quanto tempo demora hoje cada passo do processo? | Low | responsável de compras / requerente | muda o envelope de custo as-is (`A-005`) e a estimativa de esforço |
| `U-010` | Qual é a taxa horária carregada de quem hoje faz cada passo? | Low | direcção financeira | muda o valor quantificado do envelope de custo as-is |
| `U-011` | As 5 populações têm entitlement/licenciamento suficiente, ou é preciso adquirir licenciamento adicional? | Med | director de SI | muda o custo e pode mudar a viabilidade das opções |
| `U-012` | O ERP-X expõe uma interface programável para ler o catálogo de preços, ou o acesso é só pela folha copiada à mão? | Med | ERP-X (documentação técnica) / director de SI | decide se a leitura em tempo real é exequível ou se cai em fallback |

+ 3 questões abertas adicionais, imateriais a este relatório (ver `shared-understanding.md`).

## 8. Conflitos não resolvidos (Conflicted)
> Uma entrada por `X-NNN`: ambos os lados, verbatim, com a origem de cada. **Nenhum lado é
> escolhido** — nem com ressalva.

**`X-001`** — O caminho de urgência salta a aprovação prévia da chefia (valida só depois, no
mesmo dia); não está declarado se também salta a aprovação da direcção financeira quando o pedido
urgente ultrapassa o limiar do despacho.

- **Lado operações**: a via existe para dar velocidade em avarias que impedem trabalhar.
- **Lado governança**: `M-2` (o limiar da direcção financeira) foi declarado invariável pelo
  próprio dono.
- **Quem decide**: director de sistemas de informação. Nenhuma fonte resolve nas duas direcções;
  o dono respondeu "não sei; não tenho essa informação" quando questionado directamente.
- Criticidade: Critical. Continua aberto — fecha só por decisão do dono
  (`/answer X-001 "..."`).

## 9. Riscos observados (Risky)
> Uma linha por `R-NNN`: o risco · a consequência · o que o tornaria observável. A identidade de
> risco preserva-se; um risco observado não é um risco mitigado.

| id | risco | consequência | mitigação proposta (registada, não uma garantia) |
|---|---|---|---|
| `R-001` | Pedidos duplicados por reenvio (o colaborador julga que o email não chegou) levam a encomendas a dobrar, sem mecanismo de detecção hoje. | desperdício financeiro e rework em compras | detectar duplicados por regra; dar confirmação visível ao requerente |
| `R-002` | A cópia do catálogo de preços na folha de compras é actualizada à mão, sem cadência definida. | encomendas com preços errados; divergências financeiras | decidir fonte única de verdade para preços entre ERP-X e o novo sistema |
| `R-003` (was `R-001`) | Mesmo risco de duplicados; a correspondência difusa descrita não é idempotente nas escritas Web API/fluxo (corrida TOCTOU); a jornada de excepção não tem critério de aceitação nomeado. | desperdício financeiro e rework; a falha reaparece via retry ingénuo em erro de servidor | nomear mecanismo exacto antes do blueprint; testar em UAT com submissão concorrente |
| `R-004` (was `R-002`) | Mesma cópia manual do catálogo; uma "cópia local" dentro do novo sistema é cache de valor volátil/sensível — reproduz o mesmo risco sem dono, cadência e deteção de drift. | encomendas com preços errados; falsa confiança de "sistema único" | se `U-004` resolver para cópia local: dono de reconciliação, cadência e deteção de drift nomeados |

Nota: `R-003`/`R-004` são a versão corrigida de `R-001`/`R-002` (mesma identidade de risco, texto
mais preciso); as quatro linhas existem na Shared Understanding — nenhuma foi omitida aqui.

## 10. Premissas em jogo (Assumed)
> Uma linha por `A-NNN` load-bearing: a premissa · a base · quem valida · `verificado_em` /
> `validade`.

| id | premissa | base | quem valida | verificado_em / validade |
|---|---|---|---|---|
| `A-001` | O impacto declarado (duplicados, divergências de arredondamento) é qualitativo — sem medição de frequência ou custo. | relato do responsável de compras, sem números | responsável de compras / financeiro (por quando: não nomeado) | 2026-09-24 / organizacional |
| `A-002` | O requerente precisa de confirmação visível de que o pedido foi recebido, para não reenviar por dúvida. | inferência a partir de "acha que o email não chegou" | amostra de requerentes | 2026-09-24 / organizacional |
| `A-003` | Hoje não existe um sistema único de registo dos pedidos — vivem dispersos entre email e a folha de cálculo. | nota-dados.md; entrevista-processo.md | — | 2026-09-24 / organizacional |
| `A-004` | O custo de não fazer nada é qualitativo, sem valor monetário medido. | entrevista-processo.md | — | 2026-09-24 / organizacional |
| `A-005` | Fórmula do custo as-is escrita (volume × tempo por passo × taxa horária carregada + duplicados + divergências); nenhum factor medido. | estrutura derivada dos factores observados | — | 2026-09-24 / organizacional |
| `A-006` (was `C-003`) | Pedidos urgentes vão directamente a compras; a chefia tem até ao fim do dia útil seguinte para validar; sem validação, compras suspende a encomenda. | nota-urgentes.md (responsável de compras) — resposta de terceiro, sem autoridade nomeada na linha original | confirmação do dono do processo | 2026-09-24 / organizacional |

## 11. Evidência ainda necessária

**1. Re-verificação** — nenhuma. Todas as linhas `Confirmed`/`Assumed` estão dentro da validade
declarada nesta data (2026-09-24).

**2. Critérios de bloqueio abertos**:

| id | pergunta | quem responde | forma esperada da resposta |
|---|---|---|---|
| `U-006` | mecanismo de registo de aprovações fiável | auditoria interna / director de SI | decisão de desenho em blueprint |
| `U-007` | envelope orçamental, financiamento, limiar de aprovação | direcção financeira / director de SI | resposta sobre orçamento |
| `U-008` | critério de sucesso do projecto | director de SI | decisão em `/decide` ou `/blueprint` |
| `U-011` | entitlement/licenciamento das 5 populações | director de SI / inventário de licenciamento | verificação + resposta do director de SI |
| `U-012` | interface programável do ERP-X para o catálogo | ERP-X (documentação técnica) / director de SI | confirmação técnica antes de fechar `U-004` |

**3. Plano de evidência** — as fontes não registam uma ordem de resolução priorizada; os cinco
critérios de bloqueio acima são os que impedem uma conclusão e não têm plano declarado além do
que já consta na coluna "quem responde".

## 12. Stakeholders

- Requerente do engagement: director de sistemas de informação (Organização Exemplo) — autoridade
  declarada: decidiu a plataforma (`context.json#requester`).

## 13. Fontes analisadas
> **Inventário** dos artefactos analisados. É uma lista de fontes, não uma reinterpretação de
> evidência.

| fonte | formato | estado | citar como |
|---|---|---|---|
| `entrevista-processo.md` | `.md` | `ok` | `entrevista-processo.md · §<heading> ¶NN` |
| `matriz-papeis.md` | `.md` | `ok` | `matriz-papeis.md · §<heading> ¶NN` |
| `nota-dados.md` | `.md` | `ok` | `nota-dados.md · §<heading> ¶NN` |
| `nota-urgentes.md` | `.md` | `ok` | `nota-urgentes.md · §<heading> ¶NN` |
| `pedido.md` | `.md` | `ok` | `pedido.md · §<heading> ¶NN` |

## 14. Enquadramento de âmbito
> O enquadramento registado em `frame.md` / `D-001`. Enquadramento não é decisão: não há aqui
> opção escolhida, recomendação nem arquitectura.

**Frase única do problema** (`D-001`, `frame.md`): "O problema é a falta de um sistema único para
pedir, aprovar e encomendar equipamento informático — hoje tudo corre por email e por uma folha
de cálculo, sem preço sempre actualizado e, segundo o responsável de compras, sem confirmação de
recepção que evite reenvios (assumido, ainda por confirmar com o requerente) —, sentido por
compras (retrabalho com encomendas a dobrar) e, na reconciliação, por divergências de
arredondamento reportadas à contabilidade (ainda por confirmar se a contabilidade sente o mesmo
impacto); custa hoje pedidos duplicados e divergências reais já ocorridas, ainda sem envelope
quantificado (falta o volume, o tempo por passo e a taxa horária carregada); a evidência vem da
entrevista ao responsável de compras e da nota sobre os dados do catálogo."

Âmbito autorizado (`C-008`): cobre o pedido, a aprovação e a passagem a compras; gestão de stock e
recepção física ficam fora.

---
> **Nota de estado (§8.2, este passo)**: a revisão de reconciliação a montante que este
> deliverable consome (`_coverage/coverage_v13.json`) tem `coverage: gaps` / `eligible: false` —
> ainda por fechar. Este documento é produzido para discussão; não se anuncia como completo
> (ver `_render/render-gaps.md` e `_coverage/coverage_v13.json`).
