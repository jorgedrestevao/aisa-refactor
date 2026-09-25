# M3 — Discovery, blueprint e handoff ligados ao processo

Estado: pronto para revisão
Base: `claude/claim-credit-endpoint-e2oqht`, depois do M2 (`fc78a83`).
Plano: `docs/process-map/PLANO.md`.

**Resultado:** uma funcionalidade material que está no mapa não chega ao desenho nem à entrega em silêncio.

- **A reconciliação** tem de dar destino a cada elemento material do mapa.
- **O desenho** que o perde fica não elegível para aprovação, com a lacuna e a sua origem no mapa.
- **O release** não se declara pronto enquanto isso durar.
- **Correcção ou exclusão autorizada** fecham o achado.
- **A exclusão sem autoridade** é recusada.

## 1. O que passou a funcionar

| Tarefa do M3 | Onde |
|---|---|
| 1. Coluna `elementos` no contrato e no esqueleto da SU | `library/kernel/states.md` → *The `elementos` column*; `aisa-start` passo 8 |
| 2. Parser e escritores preservam a relação | `dashboard.parse_su`; `resolve.py` (`append_row` herda, `set_cell` e `append_cell` indexam linhas curtas certo); modelos do `aisa-decide`; `chairman-synthesis` regra 7 |
| 3. Citações e read-set | `resolve.CITED_IDS` com `MAP[LNEDG]-NNN` → `_map/map.json`, `CITED_DIRS_RE` com `_map/`; rascunhos da SU com `--reads _map/map.json` |
| 4. `project` | `process_map.py project` (CLI e função) |
| 5. `/round` e o revisor percorrem o processo | `aisa-round` 4c (processo e `elementos`); `lens-coverage-reviewer` lê o mapa |
| 6. Inventário e resolução da cobertura | `coverage.build_inventory` + `resolve_unit` (§6.1.1 do contrato) |
| 7. Antes do blueprint: AS-IS × requisitos × decisões | `aisa-blueprint` 1e + `COV-MAP-UNPLACED` |
| 8. Depois do blueprint: destinos funcionais concretos | `aisa-blueprint` 13b (um nó que só nomeia o assunto não é implementação) + regras existentes (`COV-MISSING-TARGET` / `COV-INVALID-TARGET`) |
| 9. Propagação até à entrega | `release.process_coverage` no `readiness` e no `build`; o render herda pela cadeia existente (`aisa-render` 2b); `handoff-contract.md` |
| 10. Pacote com o mapa consumido | `release.build` |

**Tarefa 1: a coluna `elementos`.** Aceita ids do mapa (vários numa linha), `GLOBAL` ou `N/A — <razão>`. Vazia significa não avaliada, e nunca é cobertura.

**Tarefa 2: parser e escritores.**
- Uma linha de um escritor antigo (uma célula a menos) lê-se com `elementos` vazio, e `ronda` e os marcadores ficam no sítio.

**Tarefa 4: `project`.** Mostra:
- as linhas por elemento, com a contagem por estado;
- as linhas sem avaliação, `GLOBAL` e `N/A`;
- elementos sem linhas: sinal, não bloqueio (um início não precisa de linha);
- ids desconhecidos e retirados, com os sucessores, sem reapontar.

**Tarefa 6: inventário e resolução.**
- **Unidades novas:** cada passo, ligação, detalhe e dúvida do mapa, cada `CALC-NNN` qualificado pelo workbook e cada etiqueta da §4.
- **Fora da base:** a vista e o histórico do mapa.
- **Identidade:** a da obrigação não muda. Uma obrigação servida por dois elementos é um só item.

**Tarefa 7: antes do blueprint.** O autor lê o mapa com as decisões e declara cada necessidade como preservada, alterada, excluída ou pendente. Um elemento lido como material ou por determinar sem item é `COV-MAP-UNPLACED`, que bloqueia. Uma necessidade TO-BE nova entra com `source_unit_refs` vazio.

**Tarefa 9: propagação até à entrega.**
- **Com mapa:** reconciliação ou revisão do desenho aprovado ausente, `stale`, inválida ou com lacunas mantém o nível `preliminary`, e cada lacuna traz a origem no mapa.
- **Sem mapa:** capacidade não avaliada, e o comportamento anterior mantém-se.

**Tarefa 10: pacote com o mapa consumido.** Leva `_map/map.json`, o seu snapshot, `process-map.html` e os dois registos de cobertura lidos.

### Desvios ao plano, com razão

- **`elementos` é a penúltima coluna, antes de `ronda`, e não a última.** O v3 dizia «no fim das secções». Mas a última coluna leva os marcadores `— resolved →`, de retirada e de estacionamento, que `detect_resolution` e `mark_resolved` procuram lá. Pôr `elementos` no fim partia a leitura de todas as SUs.
- **O motor do render não mudou.** A revisão de render já é validada contra a revisão a montante (`upstream_health`), e as obrigações vindas do mapa chegam-lhe por essa cadeia. Mudou só a instrução da skill: uma lacuna volta ao autor e o render nunca a preenche.
- **A exclusão parcial foi demonstrada ao nível da reconciliação.** Um elemento excluído com decisão é aceite; sem autoridade é recusado (`COV-EXCLUSION-NO-DECISION`). O âmbito parcial ao nível do release continua a ser o do `scope.json`, que já existia e não foi alterado.

## 2. Verificação

- **Ambiente:** `requirements-dev.txt` + `cffi`, clone completo.
- **Override de `library/`:** pelo procedimento aprovado, reposto no fecho (§5).

| Execução | Resultado |
|---|---|
| `test_process_map_coverage.py` | 23 OK |
| Mutações (4): regra `COV-MAP-UNPLACED`, razões do release, herança de `elementos` na transição, linha curta de escritor antigo | 7 testes falham; repostas, 23 OK |
| Suite completa, 1.ª execução (`enforce`) | `files=120 ok=117`: 4 falhas em 3 ficheiros, analisadas abaixo |
| Suite completa, fecho (`enforce`) | ver §2.1 |

**As 4 falhas da primeira execução:**
- `test_state_scaffold` (2) e `test_handoff_skill_writes` (1) fixavam a largura antiga das secções da SU.
  - A mudança de contrato é intencional, e por isso os testes passaram a exigir a forma nova: `Unknown` com `elementos` antes de `ronda`.
  - A linha D-NNN do `/decide` tem de ter **a largura do cabeçalho `Confirmed` do esqueleto**, o que prende as duas uma à outra.
  - Nenhuma asserção foi retirada.
- `test_handoff_f0` (1): o `demo.py` do M3 ainda não estava inventariado, e ficou registado.

**Um defeito no meu próprio teste e na demo:** a exclusão com decisão dava `gaps`. O motor tinha razão: uma exclusão tem de constar de `semantic_review.findings` (§4.7). Corrigi o teste e a demo, e o teste passou a exigir `complete` nesse caso.

### 2.1 Fecho

Preenchido depois da última execução.

### Testes de fecho do plano

| Caso | Teste |
|---|---|
| MAP-17 | `MAP17_OmissaoNoDesenho`: a lacuna C-007 chega ao release com a origem `MAPN-007 «Resumo Aditivos»` e `MAPG-001`; a v01 tem 0 bloqueios estruturais e não é elegível |
| MAP-18 | `MAP18_CorrigidaOuExcluida`: a v03 revista fecha o achado; excluída com `D-002` fica completa, e sem autoridade dá `COV-EXCLUSION-NO-DECISION` |
| MAP-19 (estrutural) | `MAP19_ElementoSemDestino`: elemento material sem item → `COV-MAP-UNPLACED`; com o item, completa |
| MAP-20 | `MAP20_RequisitoNovo`: item com `source_unit_refs` vazio e requisito da SU; completa |
| MAP-21 (3 variantes, separadas) | `MAP21_Variantes`: sobre o cenário «pronto» com um mapa, a cobertura é a **única** razão — «reconciliação ausente», «reconciliação inválida», «reconciliação desactualizada» |
| MAP-13 | `MAP13_ElementosNaSU`: dois passos numa linha, `GLOBAL`, `N/A — razão`, escritor antigo; SU sem coluna → `ausente`; a transição do `/answer` herda `MAPN-007` e `ronda` |
| MAP-12 | `ProjeccaoSUMapa`: `MAPN-002` dividido em `MAPN-009`/`MAPN-010` → a linha que o cita é listada com os sucessores e o texto da SU não muda |
| MAP-14 | `ProjeccaoSUMapa`: um início sem linhas não é «às escuras» e um passo é |
| MAP-08 | incluído em MAP-18 |
| MAP-22 | `MAP22_MudancaDoMapa`: renomear uma saída deixa a reconciliação desactualizada; regenerar a vista não muda nada |
| MAP-27 | `MAP21_Variantes.test_MAP27…`: o índice do pacote lista `_map/map.json`, `_map/history/mp-v01.json` e `process-map.html` |
| Obrigação partilhada | `ObrigacaoPartilhada`: C-007 é um item com `MAPN-007` e `MAPG-001` |
| Citações | `rows_citing_map_ids…`: `MAPN-…` exige `_map/map.json` no read-set e não é lido como decisão |

## 3. Demonstração obrigatória

```bash
python docs/process-map/M3/demo.py      # escreve demo-output.txt
```

Sobre cópias da fixture F06 com um mapa publicado (19 unidades do mapa no denominador):

1. **Reconciliação:**
   - sem destino para «Resumo Aditivos»: `gaps`, com `COV-MAP-UNPLACED` em `MAPG-001` e `MAPN-007`;
   - com destino (C-007 ← `MAPN-007`, `MAPG-001`): `complete`, actual.
2. **Desenho v01:** YAML válido com 0 bloqueios estruturais, cobertura `gaps`, não elegível.
   - Lacuna C-007 (em falta): «Concretizar a publicação diária e a consulta no desenho.» Origem: `MAPN-007 «Resumo Aditivos»` e `MAPG-001 «O Resumo Aditivos tem consumidor a jusante?»`.
   - Entrega pronta = `False` — «cobertura do processo: revisão do desenho aprovado com lacunas».
3. **Desenho v03 revisto:** cobertura do processo completa e nenhuma razão.
4. **Ramo separado, excluir «Resumo Aditivos»:**
   - com a decisão `D-002`: completa, aceite;
   - sem autoridade: `gaps`, `COV-EXCLUSION-NO-DECISION`.

## 4. Limitações

- **Registos semânticos das fixtures.** Foram escritos como um revisor os escreveria. O M3 prova o que o motor faz com eles, não que o agente encontra a omissão sozinho: isso é o MAP-19 semântico, no piloto M5. A lacuna C-010 da demo não tem origem no mapa porque o mapa sintético não modela onde a regra é imposta, e a demo di-lo («origem: —»).
- **Linhas sem `elementos`.** Os escritores que ainda montam linhas sem a coluna (as R-00 do `aisa-start`, as linhas de aprovação do blueprint) ficam «não avaliadas». O `project` lista-as, e continuam válidas.
- **Linhas curtas: tolerância só de uma célula.** Uma linha com duas ou mais células a menos continua a ser tratada como malformada, como antes.
- **Tipo de destino funcional por elemento.** Não há verificação determinista de que o destino é do tipo que o elemento precisa (um cálculo exige um componente, e não um ecrã, por exemplo). É instrução do 13b e julgamento do revisor, com as regras existentes contra o destino decorativo.
- **`calc-chain.json` com `generated_at`.** Uma nova captura muda o digest do ficheiro sem mudar conteúdo (M2 §4). A unidade `calculation` usa o digest do bloco e não muda. O ficheiro, porém, continua na base de actualidade da reconciliação, que por isso também fica `stale`. Isto é do M4.

## 5. Override de `library/`

- **Durante a fase:** `settings.local.json` com `AISA_GUARD_MODE=log` e o `deny` de `library/` retirado localmente, com aprovação do mantenedor.
- **Commits:** nunca levaram o `settings.json`.
- **No fecho:** `git checkout .claude/settings.json` e a chave `env` retirada do `settings.local.json`; as regras `allow` do mantenedor ficam.

## 6. Decisão do mantenedor

Pendente:
1. Aceitar o M3.
2. Autorizar o M4 (retoma, status, leitura por tarefa, dashboard; `generated_at` do `calc-chain.json`).

## Retoma

**Próxima acção:** revisão do M3.

**Primeira tarefa do M4:** `process_map.summary` com versão, validação, actualidade, bloqueios e estado por bloco, e a sua entrada no `bootstrap.snapshot(inputs=…)`.
