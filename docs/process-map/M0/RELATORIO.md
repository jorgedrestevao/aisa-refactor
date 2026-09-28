# M0 — Fixar base, localizar integrações e preparar a prova

Estado: pronto para revisão
Base: `claude/claim-credit-endpoint-e2oqht`, a partir de `2474a414fdf82677f608173770910ae5ce910867` (`handoff-v1 F8.2 R3 S4: arranque`). Clone completo (`git fetch --unshallow`).
Resultado: base, integrações, IDs e contratos do motor confirmados neste checkout; reprodução executável; fixtures de aceitação definidas; baseline de testes registada.
Plano: `docs/process-map/PLANO.md` (v3 + adenda v3.1).

## 1. Base

| Item | Valor |
|---|---|
| Branch de trabalho | `claude/claim-credit-endpoint-e2oqht` (designada nesta sessão) |
| Base do M0 | `2474a41` |
| `origin/main` no fecho do M0 | `e64b0fc`, 78 commits à frente. Inclui `c97ee1c` (a base do diagnóstico anterior), uma correcção de cobertura (`42f539b`, `disposition: retire` com referência morta) e a remoção de `docs/handoff-v1/`, `docs/evolution/`, `docs/runtime-hardening/`, `docs/CONSOLIDATED_PLAN.md` e `docs/AISA_Evolution_Plan.zip` |
| `library/` + `.claude/` entre `2474a41` e `origin/main` | Só `42f539b`: `coverage.py` (+24/−8), `coverage-contract.md` (+12), `test_coverage_contract.py` (+29) |
| Alterações locais antes do M0 | Nenhuma |
| Engagements | `projects/` vazio neste checkout. Nenhum engagement alterado |

**A `main` actual está vermelha** (ver §6). A remoção de `docs/handoff-v1/` parte 7 ficheiros de teste, e `CLAUDE.md` continua a apontar para `docs/handoff-v1/README.md`. A escolha da base do M1 é uma decisão do mantenedor (§9).

## 2. Reprodução

```bash
python docs/process-map/M0/reproduce.py
```

O script corre sobre cópias temporárias de `.claude/tests/fixtures/coverage/fx-coverage-f06` e só escreve `observations.json`.

| Prova | Observação | Consequência para o plano |
|---|---|---|
| Inventário | O modelo recebeu `PM-901`, `CALC-901` (§4bis), `CALC-003` em dois `calc-chain.json` e a etiqueta `OUT-M0` (§4). Só `PM-901` virou unidade. As classes do modelo são só `process-question` e `process-rule`; `calc_chain_units: []` | Os seletores de `CALC` qualificado por ficheiro e das etiquetas de §4 são novos (M1 e M3). A presença do documento não prova a cobertura de cada obrigação |
| IDs | `MAP-D-001` → `{'decisions.md': ['D-001']}`. `MAPL/MAPN/MAPE/MAPD/MAPG-001` → `{}`. `_map/map.json#MAPN-004` → `{}` | Usar a família `MAPL…MAPG`. Acrescentar `CITED_IDS` e `CITED_DIRS_RE` para `_map/` (M1) |
| Âncora de cálculo | `_capture/<wb>.calc-chain.json#CALC-003` resolve para o **ficheiro inteiro**: `CITED_DIRS_RE` pára no `#` | O read-set fica certo ao nível do ficheiro. A actualidade por âncora tem de vir do digest da referência no mapa (M1) |
| F06 | A v01 tem 0 bloqueios e 0 avisos estruturais. `coverage.py check --stage blueprint` → exit 4, `coverage: gaps`, `eligible: false`. `C-007` e `C-010` estão `missing` | O mecanismo que bloqueia uma omissão **conhecida** já existe: o M3 liga o mapa a ele e não cria um gate paralelo. O registo semântico vem escrito na fixture: isto não prova descoberta pelo agente |
| Captura | A L2 lê `evidence-index.md` na linha 62 da skill; o índice só é reconstruído na linha 80 (passo 6). Nem a skill nem o template mencionam `enquadramento` | Confirma o defeito de ordem e a ausência do P-0 (M1, tarefa 1) |
| Entrega | `release.py` e `trace.py` não referem a cobertura; `functional.py` refere | A propagação da cobertura até ao release é trabalho do M3 (MAP-21) |

## 3. Matriz de leitores e escritores

Conferida neste checkout. Cita funções e passos, não números de linha.

| Área | Dono / integração actual | Alteração mínima prevista | Fase |
|---|---|---|---|
| Interpretação L2 | `aisa-capture/SKILL.md` passos 5–6; `capture-templates/process-model.template.md` | Ler `enquadramento.md` antes de interpretar e registar a ausência ou contradição em §1. Reconstruir o índice antes da L2 | M1 |
| Autoria do mapa | — (novo) | Passo 5d inline depois da L2 + `process-map.guide.md` | M2 |
| Esqueleto da SU | `aisa-start/SKILL.md` passo 8 (esqueleto); `library/kernel/states.md` (colunas por secção) | Coluna `elementos` no fim de cada secção | M3 |
| Leitura da SU | `dashboard.py:parse_su` (as colunas desconhecidas só ficam em `raw`) | Campo canónico `elementos`; round-trip | M3 |
| Escrita e transições da SU | `resolve.py`: `draft`, `plan_publish`, `publish`, `mirror_write_set` | Preservar `elementos` nas transições `was`. Não criar nós de mapa que usem `mirror_of` | M3 |
| Citações e read-set | `resolve.py`: `CITED_IDS`, `CITED_DIRS_RE`, `cited_sources` | `MAP*` → `_map/map.json`; `_map/` em `CITED_DIRS_RE` | M1 |
| Schema | `workflow.py`: `validate`, `SUPPORTED` | `("_map/map.json", "process-map/1")` e `("_map/history/mp-v*.json", "process-map/1")` | M1 |
| Publicação | `operation.py:run(eng, operation_id, write_set, expected, read_set)`; exemplo em `coverage.py:finalize` | O mapa corrente e o histórico numa só operação. `BASE_CHANGED` para o mapa e `STALE_INPUT` para as fontes, os dois já existentes | M1 |
| Guarda | `pre-authority-guard.py:DIRECTORIOS_AUTORIDADE` (`_graph/ _ops/ _migration/ _work/ _design/`) | Acrescentar `_map/` | M1 |
| Inventário e cobertura | `coverage.py`: `build_inventory`, `compute_basis`, `_check_coverage`; `coverage-contract.md` §4–§6 | Unidades de mapa, `CALC` qualificado e etiquetas de §4. As obrigações continuam presas a ids da SU ou de decisões | M3 |
| Desenho | `aisa-blueprint/SKILL.md` (reconciliação antes, verificação `blueprint` depois) | Ler o mapa antes de desenhar e verificar os destinos depois, pelo mecanismo existente | M3 |
| Render | `aisa-render/SKILL.md`; `functional.py:render_gate` | A cobertura actual consumida | M3 |
| Release | `release.py:readiness`, `release.py:build`; `trace.py:scope_gate` | Cobertura ausente, desactualizada ou inválida recusa `ready` (MAP-21). Empacotar o mapa consumido (MAP-27) | M3 |
| Retoma | `bootstrap.py`: `snapshot(eng, inputs)`, `consistent_read`, `bootstrap`; `workflow.py:resume`; `.claude/commands/resume.md`; `aisa-status/SKILL.md` | O mapa em `inputs=` e o resumo derivado dos mesmos bytes, dentro do orçamento | M4 |
| Dashboard | `dashboard.py`: `INDEX_DIRS`, `TAB_SPEC`, `render_html`; `on-su-change.py` (só Write/Edit) | Separador Mapa; regeneração explícita depois do `publish` | M4 |
| Revisão | `.claude/agents/lens-coverage-reviewer.md` | Recebe a revisão do mapa depois da autoria | M3 |
| Inventário F0 | `docs/handoff-v1/F0/consumer-matrix.json` + `test_handoff_f0.py` (T02) | Registar cada consumidor novo. Já feito para os ficheiros do M0 | todas |

## 4. Contratos públicos do motor (a implementar no M1)

`library/kernel/tools/process_map.py`, stdlib, carregado por `runpy` como os outros motores.

| Comando / função | Entrada | Saída | Escreve |
|---|---|---|---|
| `check(eng, draft_path) -> dict` · `check --engagement --draft [--json]` | rascunho fora do engagement | `{valid, errors[], gaps[], transfer{missing[], placed[]}, stale_refs[]}`. Exit 0 válido; 2 erro estrutural; 4 válido com lacunas; 5 falha interna ("não verificado", nunca sucesso) | nada |
| `publish(eng, draft_path) -> receipt` · `publish --engagement --draft` | rascunho válido | recibo do `operation.run`. `BASE_CHANGED` (o mapa mudou) · `STALE_INPUT` (uma fonte mudou) · `PENDING_EXISTS` | `_map/map.json` + `_map/history/mp-vNN.json`, numa operação |
| `load(eng) -> dict` | — | `{status: absent\|ok\|invalid\|unsupported, map, digest}` | nada |
| `render(eng) -> path` (M2) | mapa publicado | `process-map.html` determinista | só a vista derivada |
| `project(eng) -> dict` (M3) | mapa + SU | associações por elemento, linhas sem avaliação, referências mortas, elementos retirados | nada |
| `summary(eng, task, budget) -> dict` (M4) | mapa + SU | `{version, validated, fresh, blocks[], blockers[], partial, omitted[]}` | nada |

Códigos de erro do `check`, estáveis:
- `MAP-SCHEMA`;
- `MAP-DANGLING` (faixa, src/dst ou `attaches_to` inexistentes);
- `MAP-NO-EVIDENCE`;
- `MAP-REF-UNRESOLVED`;
- `MAP-REF-STALE`;
- `MAP-ID-REUSED`;
- `MAP-TRANSFER-MISSING` (PM, PM-U, CALC ou etiqueta de §4 sem destino);
- `MAP-ORPHAN-UNJUSTIFIED`.

`MAP-TRANSFER-MISSING` é uma lacuna, não um erro estrutural.

## 5. Fixtures de aceitação (definição — construção no M1/M3)

Fixture `fx-process-map` sob `.claude/tests/fixtures/process-map/`, sintética e gerada por script (como `fixtures/coverage/build_workbooks.py`):

| Elemento | Conteúdo | Testes |
|---|---|---|
| Duas fontes com o mesmo `CALC` | Dois workbooks com um `CALC-003` cada, com cadeias diferentes | MAP-05 |
| Exceção | Passo "ficheiro corrompe → recupera à mão" com lacuna `MAPG` | MAP-07, MAP-16 |
| Saída com consumidor | Output "preço de referência" → consumidor "comerciais" (aresta `carries`) | MAP-06, MAP-17 |
| Necessidade TO-BE nova | Linha da SU declarada pelo dono, sem origem no Excel | MAP-20 |
| Requisito omitido do desenho | Blueprint v01 válido sem destino para a saída; v02 com destino; v02b com exclusão `D-NNN` | MAP-17, MAP-18, MAP-08 |
| P-0 | `enquadramento.md` com T4 a declarar uma saída que os ficheiros contradizem | MAP-02 |
| Omissão no próprio mapa | Variante em que o mapa não tem a saída e a folha de origem a tem | MAP-19 (estrutural) |

As expectativas de avaliação ficam num ficheiro separado do contexto do autor (v3, M5 tarefa 1).

## 6. Verificação

Dependências de desenvolvimento: `pip install -r requirements-dev.txt`. Também foi preciso `pip install cffi`: sem ele o `pypdf` falha a importar o `cryptography` do sistema (`_cffi_backend`).

| Execução | Resultado |
|---|---|
| Suite completa em `2474a41` (durante o M0) | `files=115 ok=114 tests=3110 failures=1 errors=0 skips=34 expected_failures=3`. A falha é o T02 de `test_handoff_f0.py`, causado pelos ficheiros novos do M0 ainda por registar |
| Subset stdlib em `2474a41` (durante o M0) | `files=96 ok=95 tests=2312 failures=1 skips=28`. Mesma causa |
| `test_handoff_f0.py` depois de registar em `consumer-matrix.json` | OK (17 testes) |
| Suite completa no fecho (`a306b4e`) | ver §6.1 |
| Suite completa em `origin/main` `e64b0fc` | `files=115 ok=108 fail_files=7 tests=3002 failures=1 errors=8`. As 7 falhas vêm da remoção de docs: `test_coverage_inventory`, `test_delegation_boundary` (`docs/handoff-v1/README.md`), `test_f8_tools` (`docs/handoff-v1/F8/tools/f8.py`), `test_handoff_f0`, `test_handoff_workflow` (`docs/handoff-v1/plan/examples/*`), `test_p8_comparator` e `test_p8_report_schema` (`docs/evolution/p8/*`) |

O erro dos cartões F8 do diagnóstico anterior **não se reproduz** em `2474a41` (`test_f8_tools.py`: 28 OK). O erro de `test_f7_compat.py` num clone raso desaparece com o clone completo.

### 6.1 Fecho

Execução sobre `a306b4e` (M0 completo, sem alterações de runtime), ambiente com `requirements-dev.txt` + `cffi`:

| Execução | Resultado |
|---|---|
| `python .github/run_tests.py` | `files=115 ok=115 fail_files=0 tests=3110 failures=0 errors=0 skips=34 expected_failures=3 wall=95.5s` |
| `python .github/run_tests.py --list .github/stdlib-tests.txt` | `files=96 ok=96 fail_files=0 tests=2312 failures=0 errors=0 skips=28 wall=98.3s` |

Os skips e as falhas esperadas não mudaram face à execução inicial (34/3 e 28/0). O subset stdlib correu no ambiente instalado: não demonstra isolamento num Python sem pacotes. Not-run: nenhum.

## 7. Política para engagements sem mapa

Um engagement sem `_map/` (ou anterior ao mapa) aparece como **capacidade não avaliada**:
- nunca como coberto;
- sem migração automática.

Para declarar a nova cobertura, cria-se e valida-se o mapa (v3 §17). As linhas da SU sem `elementos` ficam "associação não avaliada" (MAP-13).

## 8. Limitações

- A reprodução do F06 usa uma revisão semântica pré-escrita: prova o bloqueio, não a descoberta.
- A fonte sintética do inventário testa o denominador, não a compreensão de um Excel.
- O MAP-19 e o MAP-01/02 semânticos só se provam no piloto M5 (Pricing Marinha, que exige os ficheiros reais autorizados em `projects/<slug>/inputs/`).
- A âncora `#CALC-NNN` não é distinguida pelo leitor de citações (§2).

## 9. Decisão do mantenedor

Pendente:
1. Aceitar o M0.
2. **Base do M1**:
   - (a) continuar sobre `2474a41` (verde);
   - (b) integrar `origin/main` `e64b0fc`, o que exige primeiro repor ou adaptar os docs removidos de que os testes e o `CLAUDE.md` dependem, fora do âmbito do mapa;
   - (c) integrar só `42f539b` (a correcção de cobertura).
3. Autorizar o M1.

## Retoma

Próxima acção: decisão do mantenedor sobre §9.

Pré-condições do M1:
- base escolhida;
- clone completo;
- `requirements-dev.txt` + `cffi` instalados;
- override administrativo de `library/` (adenda v3.1, decisão 1) activo só durante o M1 e reposto antes de cada commit.

Primeira tarefa do M1: P-0 e índice antes da L2 em `aisa-capture`.
