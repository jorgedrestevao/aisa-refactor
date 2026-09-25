# M2 — Captura, visualização e validação pelo dono

Estado: pronto para revisão
Base: `claude/claim-credit-endpoint-e2oqht`, depois do M1 (`8d969ed`).
Resultado:
- o mapa nasce da captura (passo 5d, inline);
- desenha-se como fluxograma por faixas, com a vista tabular completa;
- o dono revê-o por perguntas agrupadas e valida uma versão concreta, com as dúvidas que ficam;
- o `/round` avisa quando o mapa não está validado.

Plano: `docs/process-map/PLANO.md`.

## 1. O que passou a funcionar

| Tarefa do M2 | Estado | Onde |
|---|---|---|
| 1. Índice actual antes da L2; estados de extracção falhada preservados | ✓ | O índice já vinha do M1. Agora `incomplete_sources` + `MAP-SOURCE-INCOMPLETE` no `check`, e a secção *Leitura incompleta* no render |
| 2. Passo 5d: autoria inline depois da L2 | ✓ | `aisa-capture/SKILL.md` 5d (autor → `stamp` → `check` → `publish` → `render`). A fronteira de execução estende-se ao mapa |
| 3. Guia de autoria | ✓ | `library/kernel/capture-templates/process-map.guide.md`: entradas por ordem (P-0 primeiro), elementos, profundidade, evidência, transferência, órfãos, linhagem, ciclo, e o que nunca fazer para passar no `check` |
| 4. Renderer SVG/HTML | ✓ | `process_map.py render` → `process-map.html` |
| 5. Perguntas agrupadas; respostas verbatim; correcção = nova versão; validação pelo escritor existente | ✓ | `process_map.py questions` (estrutura · saídas e quem recebe · exceções · âmbito, com a pergunta fixa de cada grupo); `aisa-capture` 5e; `resolve.py draft/publish` para `answers.md` e `decisions.md` |
| 6. Leitura da validação | ✓ | `validation()` + `approval_block()` |
| 7. Aviso no início do `/round` | ✓ | `aisa-round/SKILL.md` 2b: `AskUserQuestion` (validar primeiro ou continuar com justificação), justificação em `council-log.md` |

**Renderer** (tarefa 4):
- faixas por linha, `order` por coluna, desempate pelo id;
- passos numerados; decisão em losango, exceção a tracejado, saída com contorno forte;
- marcas em linguagem de negócio; `?` onde há dúvida;
- ligações da mesma coluna por fora e ligações de retorno por baixo;
- escape de todos os rótulos, sem script nem recursos externos, tema claro e escuro;
- **sem limite de nós**, e a tabela de passos é a vista completa;
- sem relógio: os mesmos inputs dão os mesmos bytes.

**Leitura da validação** (tarefa 6):
- `validated` só com um bloco completo, um dono humano (`validator_problem` do `functional.py`) e o digest da versão que o bloco nomeia igual ao mapa publicado agora;
- versão anterior → `stale`;
- campo em falta, validador não humano ou digest forjado → `invalid`;
- o mapa nunca é alterado para levar a aprovação.

**Kernel:** `phases.md` ganha a secção *Process map validation* (o que se valida, como, o registo normativo, a leitura e o portão suave). `glossary.md` ganha três termos, com a frase de negócio de cada um.

`phase-gate-check.py` não foi alterado: o portão é suave e vive no `/round`, e o hook só actua nas transições de fase.

## 2. Verificação

- **Ambiente:** `requirements-dev.txt` + `cffi`, clone completo.
- **Override de `library/`:** aprovado pelo mantenedor (modo com aprovação, `settings.local.json` com `AISA_GUARD_MODE=log`, `deny` retirado localmente). Reposto antes do commit (§5).

| Execução | Resultado |
|---|---|
| `test_process_map_validation.py` | 18 OK |
| `test_process_map_capture.py` | 12 OK |
| `test_process_map_core.py` (M1) | 29 OK (o render não o partiu) |
| Mutação: render sem escape; leitura sem verificar o digest | `MAP-24` e `MAP-15` (forjado) falham; repostos, OK |
| Suite completa, `AISA_GUARD_MODE=enforce` | `files=119 ok=119 tests=3174 failures=0 errors=0 skips=34 expected_failures=3` |
| Subset stdlib, `enforce` | `files=100 ok=100 tests=2376 failures=0 errors=0 skips=28` |

Skips e falhas esperadas iguais à baseline (34/3 e 28/0). Not-run: nenhum. Os testes das guardas falham com o override activo, como devem, e por isso a suite corre com `enforce`.

Testes de fecho do plano:

| Caso | Teste |
|---|---|
| MAP-07 | `MAP07_OrfaoMaterial`: órfão material por avaliar publica-se, aparece na página e no `check` dá exit 4, nunca 0 |
| MAP-15 | `MAP15_ValidacaoNaoAplicavel`: versão anterior → `stale`; digest forjado, campo em falta, `executor` e data inválida → `invalid`; só o título não chega |
| MAP-16 | `MAP16_HipoteseAberta`: validado com uma hipótese, a marca e a dúvida ficam, no mapa, nas perguntas e na página |
| MAP-24 | `MAP24_RenderDeterminista`: bytes iguais (também noutra pasta); `<script>`, `<img onerror>` e `<b>` escapados; página autónoma com os dois temas |
| MAP-22 (parte) | `CorrecaoPeloDono`: a correcção gera `mp-v02`, a validação de `mp-v01` fica `stale` e só um bloco novo valida `mp-v02`; histórico intacto |
| Texto sem Excel | `TextoSemExcel`: mapa a partir de `*.text.md#¶3`; `¶3` não apanha `¶30` |
| Excel com extracção incompleta | `ExtraccaoIncompleta`: `status: failed` à vista no `check` e na página, com a razão |
| Incompletude sem aprovação | `IncompletudeVisivel`: todos os nós, ligações e dúvidas na página por validar; 43 nós desenhados, sem limite |
| Perguntas agrupadas | `PerguntasAgrupadas`: estrutura primeiro; exceção, `GLOBAL` e detalhe caem no grupo certo; órfão aberto perguntado e exclusão não |
| Ligação das skills | `LigacaoDasSkills`: 5d depois da L2, 5e com as perguntas e o bloco, 2b do `/round` antes da passagem |

## 3. Demonstração

```bash
python docs/process-map/M2/demo.py      # escreve demo-output.txt e os HTML das duas versões
```

Sobre uma cópia temporária da fixture `fx-calc-bancas`:
- **Captura determinista real:** 6 folhas, 15 blocos de cálculo, 21 unidades a colocar.
- **Sintético e declarado como tal:** o process-model e o mapa escritos pelo script, e o dono simulado com dados de teste.
- **Escritor real:** `answers.md` e `decisions.md` escritos por `resolve.py`.

1. **Mapa `mp-v01`:** válido, 0 unidades sem destino, 2 lacunas. Validação `not_validated`.
2. **Perguntas por grupo**, numa só chamada:
   - *Passos e ligações*: «O que se faz quando não há cotações suficientes?»;
   - *Saídas e quem as recebe*: «Quem recebe o preço BIOS e com que cadência?»;
   - *Âmbito*.
3. **Resposta verbatim em `answers.md`:** «Falta o passo em que o preço mínimo é carregado no sistema de vendas pela outra equipa.»
4. **Correcção → `mp-v02`:** faixa *Sistema de vendas* e passo 7, citando `answers.md#MAPA-mp-v01`. O histórico guarda as duas versões; a validação continua `not_validated`.
5. **Validação registada em `decisions.md`:** `validated D-001 mp-v02`, com as condições «MAPG-001 e MAPG-002 ficam por esclarecer; a decisão «Cotações suficientes?» é hipótese». A decisão continua `HYPOTHESIS`.

**Evidência visual** (Chromium): `process-map-v02.png` (página inteira, claro) e `process-map-v02-flow-dark.png` (fluxograma, escuro). A 390 px de largura a página não tem scroll horizontal (`scrollWidth 390`); o fluxograma desliza dentro da moldura. A imagem não prova cobertura semântica.

## 4. Limitações

- **Validação semântica** (o dono reconhece o processo; a L2 usou o P-0): só no piloto M5, com os ficheiros reais do Pricing Marinha. A demonstração usa autoria e dono sintéticos.
- **O `calc-chain.json` grava `generated_at`.** Uma nova captura sobre o mesmo workbook muda o digest do ficheiro em `based_on` sem mudar conteúdo, e o `check` passa a acusar `MAP-SOURCE-STALE`.
  - O digest por âncora (`#CALC-NNN`) não muda, porque o bloco é o mesmo.
  - A revalidação proporcional (M4 tarefa 7, MAP-22) tem de tratar isto sem pedir reautoria por uma mudança só de carimbo. Fica para o M4.
- **Layout determinista simples:** ligações podem cruzar-se em processos com muitos ramos. Mitigações: a tabela completa e a regra de profundidade da guia. Uma biblioteca de layout fica fora de âmbito (v3 §13).
- **Âncoras de respostas:** `answers.md` usa `## MAPA-<versão> — …` e `## MAPG-NNN — …`. `CITED_IDS` ainda não conhece estes ids, o que é trabalho do M3 (citações).

## 5. Override de `library/`

- **Durante a fase:** `.claude/settings.local.json` com `AISA_GUARD_MODE=log` (ignorado pelo git) e `deny` retirado do `.claude/settings.json`, com aprovação do mantenedor.
- **No fecho:** `git checkout .claude/settings.json` (`git diff` vazio) e a chave `env` retirada do `settings.local.json`.
- **As regras `allow` que o mantenedor aprovou nesse ficheiro ficam:** são dele, não do override.

## 6. Decisão do mantenedor

Pendente:
1. Aceitar o M2.
2. Autorizar o M3.

## Retoma

**Próxima acção:** revisão do M2.

**Pré-condições do M3:**
- override pelo mesmo procedimento;
- a fixture de aceitação do M0 §5: requisito omitido do desenho, necessidade TO-BE nova.

**Primeira tarefa do M3:** coluna `elementos` no contrato e no esqueleto da SU (`states.md`, `aisa-start`), e depois o parser e os escritores.
