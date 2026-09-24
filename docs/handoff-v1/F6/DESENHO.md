# F6 — Desenho da rastreabilidade completa e do handoff implementável

Plano: `../plan/05_FASES.md` F6; `../plan/08_HANDOFF.md` (matriz de conteúdo, rastreabilidade vertical, níveis de entrega, revisão do destinatário); `../plan/06_VALIDACAO.md` T31–T34, T37–T40. Gate: T31–T34 e T37–T40. Além disso: zero requisito material órfão no âmbito entregue; esforço por WP coerente; um pacote parcial nunca apresentado como completo.

Objectivo: transformar o percurso vertical da F5 num pacote completo para o âmbito contratado. O ponto de partida são as lacunas abertas do ensaio T43 da F5: S6 e N1–N4 (`../F5/T43-ENSAIO.md` §6.2).

Decisões do mantenedor (2026-09-23), todas na opção recomendada:

| # | Decisão | Escolha |
| --- | --- | --- |
| Q1 | Onde vive o inventário de trabalho | `_design/work-packages.json` (`handoff-work-packages/1`), publicado pelo coordenador com revisão e histórico imutável. Cada `WP-NNNN` cita os FC, os elementos do desenho e as obrigações de prova que realiza. A `implementation-spec` continua dona do inventário e renderiza-o deste ficheiro |
| Q2 | Estimativa e backlog contra o inventário (T32) | Cada unidade de trabalho da estimativa cita `WP-NNNN` e a revisão do inventário. O motor detecta WP sem estimativa, estimado duas vezes, inexistente, e revisão desactualizada. O esforço vive só na estimativa; a spec não leva durações |
| Q3 | Âmbito entregue (T33, N1) | `_design/scope.json`: cada `SCOPE-NNNN` com os itens incluídos (linhas da SU e jornadas) e as exclusões, cada exclusão com a sua autorização (`D-NNN`). O motor confronta âmbito → FC → WP. Um item sem contrato nem exclusão é órfão. Um parcial só passa com exclusão autorizada e dependências coerentes |
| Q4 | Segredo em rascunho ou output (T40) | O coordenador recusa publicar (`INTEGRITY_FAILURE`) conteúdo com padrão de segredo. Fica a referência segura (nome do cofre ou da variável), nunca o valor. O `release.py verify` repete a verificação sobre o pacote |
| Q5 | Índice formal do pacote (T39) | Motor próprio `release.py`: `build` monta o pacote a partir das revisões correntes; `verify` confere cada `sha256` e recusa um pacote alterado. O nível de entrega é calculado, nunca declarado. O gerador experimental da F5 passa a usá-lo |
| Q6 | Aceitação do destinatário | Bloco `D-NNN — Aceitação do destinatário (release rNNNN)`: versão, âmbito, condições e quem aceita (papel real, via `AskUserQuestion`). Pronto para revisão não é aceite; aceite não é implementado. O índice aponta o bloco. Uma simulação é rotulada |
| Q7 | Lacunas S6, N2–N4 do ensaio da F5 | Todas na F6. S6: `states.md` fixa como se contam os `¶` de um `.md`. N2: a aprovação do desenho leva a impressão digital da versão. N3: aviso do motor quando a regra de um FC usa um conceito que o desenho não define (o `fc-reviewer` continua a julgar). N4: a coerência de um parcial passa pelo gate de âmbito (Q3) |
| Q8 | Ensaio do destinatário no fecho | Sim: um 3.º ensaio T43, simulado, com o mesmo pedido, sobre o pacote completo |

## 0. Subagentes e paralelismo — avaliados antes de definidos

Critério: README → *Regras de execução*; `library/kernel/orchestration.md` → *When a subagent is justified*.

| Uso em F6 | Precisa do contexto de quem lança? | O detalhe volta a ser preciso? | Veredicto |
| --- | --- | --- | --- |
| Autoria do âmbito, do inventário e da estimativa (sessão, `/blueprint` e `/render`) | sim: SU, FC, desenho, decisões | sim: são o produto | **inline** |
| Rastreabilidade, gates e release | — (motores determinísticos) | — | **código**, sem agente |
| Revisão do inventário | não é nova: o `fc-reviewer` e o `/render` já revêem. Um revisor de inventário só teria valor se o inventário tivesse juízo não coberto pelos motores | — | **nenhum agente novo**; reavaliar se o 3.º ensaio mostrar lacunas de conteúdo no inventário |
| Destinatário do 3.º ensaio T43 | não: tem de ter **só** o pacote | não: voltam as lacunas | **subagente**, uma chamada |

## 1. Âmbito e inventário (Q1, Q3; T33, N1, N4)

`library/kernel/tools/inventory.py` publica dois artefactos pelo coordenador, cada um com revisão e histórico em `_design/history/`.

**`_design/scope.json`** (`handoff-scope/1`). Cada `SCOPE-NNNN` tem:

- `includes`: linhas da SU e `J-NNNN`, com o motivo;
- `excludes`: cada exclusão com o motivo e a `authorization_ref` (`D-NNN`);
- `authorized_by`: o bloco de decisão que autoriza o âmbito.

O âmbito deixa de ser só derivado dos FC. A projecção da F5 (`scope_definition`) passa a ler este ficheiro.

**`_design/work-packages.json`** (`handoff-work-packages/1`). Cada `WP-NNNN` tem:

- `scope_id`, `purpose` e `realizes` (`FC-NNNN`, elementos do desenho, obrigações arquitecturais);
- `proves` (obrigações de prova), `depends_on` (`WP-NNNN`) e `acceptance` (condições ligadas aos exemplos dos FC);
- `skills`, `definition_of_done` e `not_applicable` com motivo.

Nunca leva duração nem esforço: é Q2.

**Integridade** (fail-closed):

- os ids nunca são reutilizados;
- as referências resolvem;
- não há ciclo em `depends_on`;
- uma exclusão sem autorização é recusada.

## 2. Rastreabilidade (plano 08 → *Rastreabilidade vertical*; T31, T34, T37)

`library/kernel/tools/trace.py` é read-only. Constrói o grafo `âmbito → requisito/regra → FC → elemento do desenho → WP → aceitação/prova` e reporta nos dois sentidos:

- requisito do âmbito sem FC, sem WP ou sem teste — órfão, a menos que esteja excluído ou tenha `not_applicable` com motivo;
- WP sem motivo de desenho — órfão, a menos que realize uma obrigação arquitectural transversal;
- obrigação de prova (T31) sem WP e condição de aceitação;
- prova futura que pode invalidar a viabilidade (T34): bloqueia o compromisso aplicável e fica nomeada no índice, fora da checklist de implementação;
- headless (T37): nenhuma obrigação de ecrã, documento de ecrãs ou WP de interface.

## 3. Estimativa, gates de âmbito e lacunas da F5 (Q2, Q7; T32, T33)

- **T32**: o `trace.py estimate-check` lê as unidades da estimativa, que citam `WP-NNNN (inventário rNNNN)`. Detecta WP sem estimativa, duplicado, inexistente, revisão antiga e duração na spec.
- **T33 / N4**: o gate de âmbito bloqueia a entrega total quando um subconjunto tem um bloqueio de build. Um parcial só passa com exclusão autorizada e dependências coerentes: nenhum WP incluído depende de um WP ou FC excluído, e nenhum campo obrigatório do desenho depende de um FC excluído sem motivo.
- **N2**: o bloco de aprovação do desenho leva `**Blueprint sha256**`. O `approved_blueprint` confere-o com a versão.
- **N3**: aviso do `functional.py` quando a regra ou a excepção de um FC nomeia um termo que é um campo ou entidade candidata não definida no desenho. É um aviso, não uma lacuna de completude.
- **S6**: `states.md` fixa a contagem dos `¶` num `.md`.

## 4. Templates (plano 08 → matriz; T37, T38)

- A `implementation-spec` renderiza o inventário de `work-packages.json`, incluindo WP, dependências, ordem, bloqueios e DoD.
- A estimativa cita `WP-NNNN` e a revisão.
- ALM, enforcement de segurança, integração/recuperação, migração/cutover (T38), operação e dependências de cliente aparecem quando aplicáveis, com N/A justificado quando não. As secções já existem e só se reforça a ligação ao inventário.
- O `render-validate` passa a verificar as citações.

## 5. Release, segredos e aceitação (Q4, Q5, Q6; T39, T40)

**`library/kernel/tools/release.py`**:

- `build`: pacote + `handoff-index/1` com hashes, revisões lidas, `scope.json`, exclusões, aprovações, provas feitas e por fazer, e limitações;
- `delivery_level`, calculado:
  - `preliminary` enquanto houver órfão, bloqueio ou exclusão sem autorização;
  - `ready_for_receiver_review` quando o gate de âmbito passa;
  - `accepted_by_receiver` só com o bloco de Q6;
- `verify`: `sha256` de cada ficheiro, recusa o pacote alterado (T39) e procura segredos (T40).

**Segredos** — o `operation.run` recusa um `write_set` com padrão de segredo. O conjunto de padrões é fechado e estrito, para não haver falso positivo em texto de negócio:

- chaves privadas;
- tokens de fornecedores conhecidos;
- `password=`/`pwd=` com valor em connection strings;
- `Bearer` com token longo.

## 6. Percurso e ensaio (Q8; T38)

- `fx-hv1-02`: pacote completo pelo `release.py` (âmbito, inventário, spec e estimativa em pré-visualização a partir do inventário), com o nível calculado.
- `fx-hv1-05` (migração de legado) prova T38: reconciliação, cutover, rollback e retenção ligados a WP e aceitação.
- `fx-hv1-04` prova T37.
- 3.º ensaio T43 com o pedido dos anteriores, registado como simulado.

## 7. Incrementos

| Inc. | Conteúdo | Testes |
| --- | --- | --- |
| F6.1 | `inventory.py`: `scope.json` e `work-packages.json`, schemas, integridade | integridade; T33 (parte do motor) |
| F6.2 | `trace.py`: grafo e órfãos nos dois sentidos; provas; headless | T31, T34, T37 |
| F6.3 | Estimativa contra o inventário; gate de âmbito; N2, N3, S6 | T32, T33 |
| F6.4 | Templates: spec projecta o inventário, estimativa cita WP; migração e operação; `render-validate` | T38; contrato textual |
| F6.5 | `release.py` build/verify; segredos no coordenador; aceitação do destinatário | T39, T40 |
| F6.6 | Percursos `fx-hv1-02`, `fx-hv1-04`, `fx-hv1-05`; 3.º ensaio T43 | ponta a ponta; registo do ensaio |
| F6.7 | Relatório e gate | T31–T34, T37–T40 |
