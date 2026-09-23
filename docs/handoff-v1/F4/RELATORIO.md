# F4 — Relatório da fase (autoria funcional e primeiro desenho coerente)

Estado: **gate avaliado, aguarda aceitação do mantenedor** (2026-09-23). Desenho e decisões Q1–Q6: [DESENHO.md](DESENHO.md). O gate (T20–T24; o render recusa preencher uma regra em falta; referência ou aprovação desactualizada bloqueia a publicação final) está cumprido, com os limites declarados (§5).

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F4.1 `functional.py` + completude | integrado | `405f3f9` | `library/kernel/tools/functional.py`: `draft`, `check`, `publish`, `show`. Publica pelo coordenador numa operação: a revisão corrente e a cópia imutável em `_design/history/`. A integridade recusa com `INTEGRITY_FAILURE` (schema, ids nunca reutilizados nem largados fora de `retired_ids`, revisão +1, referências a SU, `D-` e desenho que resolvem, desenho de opção recusado). A frescura vem antes da integridade (`STALE_INPUT`). Um replay devolve o mesmo recibo. A completude dá `BLOCKING_GAP` sem recusar: essenciais, cálculo sem unidades, arredondamento ou os três tipos de exemplo, delegação incompleta, pergunta bloqueante aberta. Schema aditivo sem mudar de versão. `handoff-contract.md` descreve o motor e corrige a tabela F1 (FC em F4, pelo plano 05). Matriz F0: 3 entradas. `test_functional_contracts.py` 19 casos (T20). Full 91/91, 2863; stdlib 72/72, 2065; ambos exit 0 |
| F4.2 Autorização | integrado | `475fbb4` | `functional.py`: leitura dos blocos `D-NNN — Contratos funcionais autorizados`; estado por FC (`current` · `stale` · `invalid` · `missing`) por impressão digital do item; `authorization-block` gera o bloco com as impressões do motor e recusa FC com lacunas e validador não humano (`AUTHORIZATION_REQUIRED`); `show` lista as premissas `Assumed` e se o FC é autorizável. Contrato no `handoff-contract.md`. `test_functional_authorization.py` 7 casos (T22, T24, item 6). Full 92/92, 2870; stdlib 73/73, 2072; ambos exit 0 |
| F4.3 Coerência desenho ↔ FC | integrado | `6e96f75` | `functional.py conflicts`: por `field_ref`, compara `required`, `values` (sem ordem), `default` e `type` entre o desenho e o FC; divergência = `FC_BLUEPRINT_CONFLICT` com os dois lados e os localizadores, sem escolher um. O FC afectado sai não autorizável (`show`, `check`, `authorization-block`); `conflicts --blueprint <versão>` compara uma versão em aprovação com os FC correntes (exit 4). Faceta *calculado* deixada ao revisor (nota no desenho §3). `test_functional_coherence.py` 6 casos (T21). Full 93/93, 2876; stdlib 74/74, 2078; ambos exit 0 |
| F4.4 Passo funcional do `/blueprint` + `fc-reviewer` | integrado | `cb3d4f3` | `/blueprint` passo 13c: autor inline dos FC do âmbito autorizado (draft → check → publish), conflito com o desenho como linha `Conflicted` sem escolher um lado, um revisor `fc-reviewer` depois da publicação com disposição por achado; linha no resultado (`Contratos do comportamento`); passo 15 com a verificação (iii) `functional.py conflicts --blueprint`; passo 16 autorização só pelo dono por `AskUserQuestion`, bloco gerado pelo motor; regra 11 (o comportamento vive nos contratos). Agente `fc-reviewer` (Read/Grep/Glob, achados do plano 03). `test_blueprint_functional_step.py` 8 casos. Full 94/94, 2884; stdlib 75/75, 2086; ambos exit 0 |
| F4.5 Render | integrado | `4998d95` | `functional.py render-gate`: para os FC citados num deliverable, verifica existência, autorização sobre o item corrente, lacunas, conflitos e que assentam no desenho aprovado; um bloqueio impede a versão final (pré-visualização permitida); cada lacuna volta com `owner: functional`. `render-contract.md`: dono `functional` na classe 3 e a regra da versão final; `/render` passo 7b; template do `implementation-spec` com a fonte `_design/functional-contracts.json` e o dono `functional`. `test_functional_render.py` 8 casos (T23; referência e aprovação desactualizadas). Full 95/95, 2892; stdlib 76/76, 2094; ambos exit 0 |
| F4.6 Percurso, relatório e gate | integrado | (este) | `test_hv1_design_path.py` 6 casos. `fx-hv1-02`: FC-0001 (submissão sem duplicar: jornada, dados, automação, recuperação, aceitação) autorizado com dados de teste e publicável; FC-0002 (valor) bloqueado pela regra de arredondamento em aberto (U-001), não autorizável, e devolvido ao autor funcional pelo render; rastreio requisito → FC → desenho. `fx-hv1-04`: FC-0010 headless (envio ao ERP-X sem duplicar, reagendamento, reprocessamento, escolha delegada com envelope, prova pendente) completo e autorizável sem nenhum ecrã. Full 96/96, 2898; stdlib 77/77, 2100; ambos exit 0. CI #50–#55 verdes |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F4.0 | levantamento e desenho | precisa do contexto da sessão (plano, contratos, motores); o detalhe volta a ser preciso | na sessão |
| F4.1 | motor, schema, testes | idem | na sessão |
| F4.2 | autorização, testes | idem | na sessão |
| F4.3 | coerência, testes | idem | na sessão |
| F4.4 (execução) | skill, agente, testes | idem | na sessão |
| F4.5 | render, testes | precisa do contexto; o detalhe é o produto | na sessão |
| F4.6 | percurso, gate | idem | na sessão |
| F4.4 (desenho do framework) | revisor dos FC | não precisa do contexto do autor; voltam só os achados | subagente `fc-reviewer`, 1 chamada sequencial por revisão publicada |

## 3. Testes adaptados

- Nenhum em F4.1–F4.3.
- F4.4, `test_step8c_semantic_continuity` (adaptar): a lista fechada de agentes ganha o `fc-reviewer` (Q5).
- F4.5, `test_pp_deliverable_templates` (adaptar): `GAP_OWNERS` ganha `functional` (Q4); o resto do teste do conjunto de donos não muda.

## 4. Limitações conhecidas

- A completude verifica a presença dos campos essenciais, não a sua qualidade: uma `rule` escrita mas errada passa. Isso é do `fc-reviewer` (F4.4) e do dono (F4.2).
- «Cálculo» é declarado pelo autor (campo `calculation`); o motor não deduz que um FC calcula. Um cálculo não declarado escapa à exigência de arredondamento e dos três exemplos — é achado do revisor.
- O validador humano é verificado por forma (`owner (<papel>, … via AskUserQuestion)`) e por uma lista fechada de nomes que nunca autorizam (executor, agentes, personas, revisores). Não prova que a pessoa respondeu: isso vem da regra do `AskUserQuestion` na sessão.
- O bloco de autorização é classificado pelo dashboard como `other` (não é aprovação de frase, solução ou desenho); fica assim até alguém precisar de outra leitura.
- A comparação desenho ↔ FC só vê o que os dois declaram de forma estruturada, por campo. Uma regra dita em prosa no desenho, ou um estado de uma máquina de estados de entidade, fica para o revisor.
- A linha `Conflicted` na SU e o bloqueio da aprovação do desenho são escritos pelo `/blueprint` (F4.4); o motor dá o conflito e a recusa de autorizar.
- O `render-gate` lê as citações `FC-NNNN` do documento composto. Um comportamento que o documento descreve **sem** citar um FC escapa ao portão; a regra do `/render` (ler o comportamento dos FC, nunca da prosa da síntese) é o que o evita, e é texto.
- O percurso das fixtures escreve os FC a partir do `expected` — o que o passo 13c produziria. Prova a cadeia dos motores, não a escrita de uma sessão; isso mede-se nos pilotos.

## 5. Gate (05_FASES F4: T20–T24; render; publicação final)

| Teste | Critério (06_VALIDACAO) | Estado | Evidência |
| --- | --- | --- | --- |
| T20 | FC sem regra essencial ou aceitação → `BLOCKING_GAP` no âmbito afectado | **cumprido** | `test_functional_contracts.T20_Completude` (6 casos: aceitação em falta publica com `BLOCKING_GAP` e não é autorizável; `not_applicable` com motivo fecha; cálculo sem arredondamento ou sem exemplos; pergunta bloqueante aberta; delegação incompleta); `test_hv1_design_path.Fx02Percurso.test_the_rounding_rule_blocks_the_calculation` |
| T21 | Blueprint e FC contradizem a mesma regra → conflito visível; não escolhe versão | **cumprido, com limite** | `test_functional_coherence` (6 casos: quatro facetas, só um lado não é conflito, ordem dos valores, reconciliar limpa, versão em aprovação apanhada). Limite: só as facetas estruturadas; prosa e *calculado* são do revisor |
| T22 | TO-BE aprovado com premissa AS-IS assumida → autorização não confirma a premissa | **cumprido** | `test_functional_authorization.T22_PremissaAssumida` (A-001 fica `Assumed`, listada em `assumed_premises`) |
| T23 | Render encontra detalhe funcional em falta → não inventa; devolve lacuna ao autor | **cumprido, com limite** | `test_functional_render.T23_NaoInventa` (lacuna com `owner: functional`; FC citado inexistente é lacuna, não valor); `test_hv1_design_path` (FC-0002 devolvido). Limite: o portão vê as citações `FC-NNNN`; comportamento descrito sem citação fica à regra textual do `/render` |
| T24 | Blueprint/FC mudam após aprovação → aprovação antiga não autoriza a nova | **cumprido** | `test_functional_authorization.T24_RevisaoNova` (FC mudado → `stale`, o outro mantém; nova autorização cobre); `test_functional_render.test_a_stale_authorisation_blocks_the_final_version`; aprovação do desenho noutra versão → `STALE_REFERENCE` |
| Render recusa preencher regra em falta | — | **cumprido** | `render-gate` bloqueia a versão final com lacuna ou contrato em falta; `/render` 7b: «Never write the missing value to make the gate pass» (`test_functional_render`) |
| Referência e aprovação desactualizadas bloqueiam a publicação final | — | **cumprido** | `test_functional_render.PortaoFinal` (autorização desactualizada; contratos sobre desenho que não é o aprovado; sem desenho aprovado) |

Suites no fecho: full 96/96 ficheiros, 2898 testes; stdlib 77/77, 2100; ambos exit 0. CI #50 (desenho) a #55 (F4.5) verdes; o commit da F4.6 corre a seguir.

## 6. Itens do plano (05_FASES F4)

| # | Trabalho | Estado | Onde |
| --- | --- | --- | --- |
| 1 | Artefacto FC e fluxo draft → revisão → integração → autorização | feito | `functional.py` (F4.1), autorização (F4.2), passo 13c/16 do `/blueprint` com `fc-reviewer` (F4.4) |
| 2 | Modo autor funcional no comando de desenho existente | feito | passo 13c do `/blueprint`; nenhum comando novo (Q1) |
| 3 | Comportamento, entidades/campos, actores, direitos, excepções e aceitação por ID | feito | FC por `field_ref`, `actors`, `exceptions`, `acceptance_examples`, ids `FC-`/`J-` (F4.1); rastreio em `test_hv1_design_path` |
| 4 | Blueprint e FC sem duas versões da mesma regra; bloquear até reconciliar | feito, com limite | F4.3 (facetas) + revisor (prosa) |
| 5 | Percurso pequeno com jornada, dados, automação, recuperação e teste; sem UI quando headless | feito | F4.6 (`fx-hv1-02`, `fx-hv1-04`) |
| 6 | Permissões de aprovação ligadas a papéis reais; nenhum agente aprova pelo cliente | feito, com limite | F4.2 (validador humano por forma e lista fechada); a resposta real vem do `AskUserQuestion` |

**Entregável**: desenho funcional e arquitectural de fixture única, com autorizações sintéticas identificadas como dados de teste — feito (`fx-hv1-02`; `fx-hv1-04` headless).

## 7. Leitor, escritor e schema — o que F4 acrescenta

| Artefacto | Escritor | Leitores | Schema |
| --- | --- | --- | --- |
| `_design/functional-contracts.json` + `_design/history/functional-contracts.r<NNNN>.json` | `functional.py publish` (coordenador) | `/blueprint` 13c/15/16, `/render` 7b, `fc-reviewer` | `handoff-functional/1` (aditivo F4) |
| Bloco `D-NNN — Contratos funcionais autorizados` | `/blueprint` 16 (texto de `functional.py authorization-block`, publicado por `resolve.py`) | `functional.py` (estado da autorização, render-gate) | `handoff-contract.md` → *Authorisation* |
| `_blueprint/fc-review-r<NNNN>.md` | `/blueprint` 13c (retorno do `fc-reviewer`, verbatim) | autor funcional, dono | achados do plano 03 |
| Lacuna `owner: functional` em `render-gaps.md` | `/render` 7b | autor funcional | `render-contract.md` classe 3 |

## 8. Decisões e pontos por decidir

- Tomadas (mantenedor, 2026-09-23): Q1–Q6 do desenho.
- Desvio registado: a faceta *calculado* não é comparada pelo motor (nota no desenho §3).
- Para F5: `WP` e dependências tipadas; o conselho do `/options` pela regra dos subagentes; o dashboard pode ganhar uma leitura própria para o bloco de autorização de FC (hoje `other`).

## 9. Próxima fase

F5 — candidatos comuns, especialistas e primeiro percurso vertical (`../plan/05_FASES.md`). Arranca com o seu `DESENHO.md` (§0 dos subagentes, incluindo o conselho de Options) e as decisões de contrato levadas ao mantenedor.
