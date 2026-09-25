# M1 — Compreensão orientada e fundação do mapa

Estado: pronto para revisão — **com instalação pendente em `library/`** (§2)
Base: `claude/claim-credit-endpoint-e2oqht`. É `2474a41` + `42f539b` (cherry-pick `ede7814`, a correcção de cobertura da `main`), por decisão do mantenedor.
Resultado: o P-0 e o índice entram antes da L2; o schema `process-map/1` e o motor `check`/`stamp`/`publish`/`status` estão escritos e testados; `_map/` é estado coordenado.
Plano: `docs/process-map/PLANO.md`.

## 1. O que passou a funcionar

| Tarefa do M1 | Estado | Onde |
|---|---|---|
| 1. P-0 antes da L2; divergências preservadas | ✓ em vigor | `aisa-capture/SKILL.md`: passo 5a0 (lê `enquadramento.md` antes de interpretar; orienta, nunca filtra; divergências citam os dois lados; P-0 ausente declarado), regra 11. Linha `P-0` no cabeçalho do template: patch |
| 1b. Índice antes da L2 (defeito do M0) | ✓ em vigor | `aisa-capture/SKILL.md`: o passo 5 só corre depois dos passos 5b e 6, e o passo 6 é reconstruído antes da L2 |
| 2. Schema `process-map/1` | ✓ staging | `staging/kernel/schemas/process-map.schema.json`: envelope, faixas, nós, arestas, detalhes, dúvidas, órfãos, `retired_ids`, `was`, digests. Validado pelo `workflow.validate`, sem dependências |
| 3. Resolvedores de referências qualificadas | ✓ staging | `resolve_ref`: `calc-chain.json#CALC-NNN` por ficheiro, `extraction.json#sheets[name=…]`, `process-model.md#PM-NNN · #PM-U-NNN · #§4:<etiqueta>`, `#CALC-NNN` só quando não é ambíguo; secção `.md` por título; ficheiro inteiro como último recurso, com aviso "âncora não verificada". Recusa `_map/`, `_ops/`, `_graph/`, … e caminhos fora do engagement |
| 4. `check` | ✓ staging | Schema, ids únicos, ligações, evidência, `UNKNOWN` sem dúvida, referências (resolúveis, não ambíguas, com digest, actuais), `based_on` completo e actual, P-0 consumido, base, transferência PM/PM-U/CALC/§4, órfãos (exclusão material exige `D-NNN` existente) e linhagem. Erros e lacunas estão separados |
| 4b. `stamp` | ✓ staging | Preenche só o que falta (`base`, digest de uma referência, fonte consumida) e nunca substitui um valor existente |
| 5. `publish` | ✓ staging | Uma operação do `operation.run`: `map.json` + `history/mp-vNN.json`; `expected` = base; `read_set` = `based_on`; id de operação estável (repetir = mesmo recibo); versão derivada da base, sob o lock |
| 6. Guarda de `_map/` + schema nos leitores versionados | ✓ guarda em vigor · schema por patch | `pre-authority-guard.py` + `HOOKS.md` em vigor; `workflow.py SUPPORTED`: patch |
| 7. Documentação e inventário | ✓ | `orchestration.md`: patch (publicação, códigos, rascunho desactualizado). Inventário F0 e lista stdlib actualizados |

A publicação não aprova o mapa nem mexe na SU: nenhum dos dois caminhos existe no motor.

## 2. Bloqueio e caminho seguido

**O que o M1 precisava:** o override administrativo autorizado (adenda v3.1, decisão 1), ou seja, remover o `deny` de `library/` e pôr `AISA_GUARD_MODE=log` no `.claude/settings.json` local.

**O que aconteceu:**
- O classificador de segurança do Claude Code recusou duas vezes a alteração do `AISA_GUARD_MODE`, como auto-modificação.
- Chegou a esvaziar-se o `deny`, mas o `settings.json` foi reposto logo a seguir: `git diff .claude/settings.json` está vazio.
- A recusa não foi contornada por outra via (Bash, script, subagente).

**Caminho seguido:** o previsto pelo mantenedor para o caso de recusa, staging fora de `library/`.
- `docs/process-map/M1/staging/kernel/…`: ficheiros novos. O caminho não contém `library/`, porque a rede de segurança do `pre-write-guard.py` recusa qualquer caminho com esse segmento.
- `docs/process-map/M1/staging/*.patch`: alterações a ficheiros existentes.
- `docs/process-map/M1/staging/install.py`: instalador para o mantenedor.

**Instalação (mantenedor, fora do runtime):**

```bash
python docs/process-map/M1/staging/install.py --check   # confere, não escreve
python docs/process-map/M1/staging/install.py           # aplica 3 patches, copia motor + schema, regista no F0
python .github/run_tests.py
git diff --stat && git commit
```

Os testes carregam o motor de `library/kernel/tools/process_map.py` quando existe, e do staging quando não. Depois da instalação, o staging pode ser removido num commit à parte.

## 3. Verificação

Ambiente: `requirements-dev.txt` + `cffi`, clone completo.

| Execução | Resultado |
|---|---|
| `python .claude/tests/test_process_map_core.py` | 29 testes OK |
| `python .claude/tests/test_process_map_guard.py` | 3 testes OK. Falha com a guarda antiga (confirmado) |
| Mutação: desligar a transferência e a verificação de digest actual | 3 testes falham, depois de reposto 29 OK: os testes detectam a regressão |
| **Instalação simulada** (worktree limpa + `install.py`), suite completa | `files=117 ok=117 tests=3144 failures=0 errors=0 skips=34 expected_failures=3` |
| Instalação simulada, subset stdlib | `files=98 ok=98 tests=2346 failures=0 errors=0 skips=28` |
| Repositório sem instalação (motor lido do staging) | ver §3.1 |

Pelo caminho, a instalação simulada revelou duas falhas, ambas corrigidas antes do commit:
- `test_windows_console`: o CLI tem de proteger a consola; acrescentado `utf8_console()`.
- `test_handoff_f0`: o motor em `library/` tem de estar no inventário; é o `install.py` que o regista.

### 3.1 Repositório sem instalação

| Execução | Resultado |
|---|---|
| Suite completa (1.ª execução) | `files=117 ok=116 tests=3144 failures=1`: `test_pp_pack_integrity` P15 viu uma referência de runtime partida, porque a docstring de `test_process_map_core.py` citava o caminho do motor em `library/`, que ainda não existe |
| Correcção | docstring reformulada; `test_pp_pack_integrity.py` e `test_process_map_core.py` OK |
| Subset stdlib | `files=98 ok=98 tests=2346 failures=0 errors=0 skips=28` |

Skips e falhas esperadas iguais à baseline do M0 (34/3 e 28/0). Not-run: nenhum.

Testes de fecho do plano:

| Caso | Teste |
|---|---|
| MAP-03 | `MAP03_Ligacoes` (faixa, extremo de aresta, `attaches_to`; prefixo errado; recusa sem rasto em `_map/`) |
| MAP-04 | `MAP04_Evidencia` (nó observado sem evidência; detalhe com `ref` sem `evidence`; UNKNOWN exige dúvida; referência inexistente; estado coordenado não é evidência) |
| MAP-05 | `MAP05_CalcPorFicheiro` |
| MAP-06 | `MAP06_Transferencia` (cada unidade nomeada; órfão explícito fica aberto; exclusão material exige decisão existente e justificação) |
| MAP-09 | `MAP09_Repeticao` |
| MAP-10 | `MAP10_Concorrencia` (segundo autor na mesma base; o coordenador recusa a base desactualizada mesmo sem o check; queda real a meio da publicação → pendência visível → `RECOVERY_REQUIRED` → recuperação completa a operação original) |
| MAP-11 | `MAP11_FonteMuda` (recusa no check e recusa no coordenador; o rascunho fica intacto) |
| MAP-12 | `MAP12_Linhagem` (desaparecer sem retirar; divisão com `was`, histórico intacto; id retirado não volta; `was` para o que não existia) |
| MAP-25 | `test_process_map_guard.py` |
| MAP-01/02 (estrutural) | `MAP01_P0Consumido`: o `enquadramento.md` tem de constar de `based_on` |
| Versão futura | `VersaoFutura`: `process-map/2` lê-se como não suportado e nunca se sobrescreve |

## 4. Demonstração

```bash
python docs/process-map/M1/demo.py      # escreve docs/process-map/M1/demo-output.txt
```

1. O mapa é publicado como `mp-v01` (`map.json` + `history/mp-v01.json`), com 5 unidades e nenhuma sem destino.
2. A fonte (`process-model.md`) é alterada depois do rascunho: nada é publicado (`MAP-SOURCE-STALE`) e o mapa continua em `mp-v01`.
3. A operação original repetida é reconhecida como repetição: nenhuma versão nova, o histórico fica só com `mp-v01.json`.
4. `CALC-001` existe em dois workbooks: cada referência resolve para o seu bloco, com digests diferentes. `process-model.md#CALC-001` sem ficheiro é `ambiguous`.

## 5. Desvios ao plano

- **Citações em `resolve.py`** (`CITED_IDS`/`CITED_DIRS_RE` para `MAP*` e `_map/`): o relatório M0 punha-as no M1, mas a tabela de ficheiros do v3 põe-nas no M3 (tarefa 3). As citações de ids do mapa só aparecem com a coluna `elementos` da SU (M3), e o read-set da publicação do mapa já é o `based_on`. Ficam no M3.
- **Vista `process-map.html`**: guarda preparada; o render é do M2.
- **Etiquetas de §4**: lidas na forma `- MARCADOR — \`etiqueta\`: …`, a mesma que `aisa-round` e os testes step-8c usam. Uma linha material sem essa forma não é enumerada: a regra 5 da captura já a trata como violação do template.

## 6. Limitações

- O MAP-01 e o MAP-02 semânticos (a L2 usa realmente o P-0 para orientar e regista divergências) só se provam no piloto M5. O M1 só garante a instrução e a prova estrutural (o P-0 nas fontes consumidas).
- Uma âncora em `inputs/<wb>.xlsx#Folha!B2` vale o ficheiro inteiro (sem `openpyxl` no runtime). A verificação da célula faz-se pela extracção (`extraction.json#sheets[…]`).
- As fixtures de aceitação completas do M0 §5 (TO-BE novo, requisito omitido do desenho) servem o M3. O M1 usa a fixture mínima do teste.

## 7. Decisão do mantenedor

Pendente:
1. Correr o `install.py` e confirmar a suite.
2. Aceitar o M1.
3. Autorizar o M2.

## Retoma

**Próxima acção:** instalação pelo mantenedor (§2) e revisão.

**Pré-condições do M2:** motor em `library/`, clone completo, `requirements-dev.txt` + `cffi`.

**Primeira tarefa do M2:** passo 5d da captura (autoria inline do mapa depois da L2) + `process-map.guide.md`.

**Nota para o M2:** a guia e o render vivem em `library/`. Sem um procedimento de escrita que o classificador aceite, voltam a precisar de staging.
