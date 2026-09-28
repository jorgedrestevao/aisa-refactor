# M5.1 — Mapa legível e parágrafos de fontes curtas

Estado: pronto para revisão
Base: `claude/claim-credit-endpoint-e2oqht`. As mudanças estão em `5eb7ab2` e neste commit (linha própria das exceções, faixa «Canal»).
Origem: M5, os achados K2 (mapa denso) e K3 (omissão sem detecção). Decisão do mantenedor: «Tratar omissões primeiro», mais o pedido de legibilidade com o exemplo do dono como referência de desenho.

**Dados reais:** este relatório leva só veredictos, ids e contagens. Ficam fora do git:
- as fontes;
- os mapas;
- as expectativas;
- a comparação detalhada.

## Resultado

- **Desenho do mapa**, a partir do mesmo `map.json`:
  - faixas agrupadas por tipo, só as que têm passos: *Humano* · *Ferramenta* · *Canal* · *Quem recebe* · *Sistema a jusante*;
  - colunas pela posição no fluxo;
  - exceções laterais em linhas próprias, por baixo do caminho principal, na coluna de onde saem;
  - ligações em ângulo recto;
  - numeração pelo caminho principal e depois pelas exceções.
- **Nova verificação `MAP-PASSAGE-UNPLACED`:** cada parágrafo com conteúdo de uma fonte de texto curta tem destino no mapa, citado num elemento ou disposto em órfãos. A publicação é recusada enquanto faltar algum.
- **Corrida 2 do piloto:** autor novo e isolado, as mesmas 6 fontes. Cobre todas as expectativas já na primeira versão, e o dono não fez correcções.

## 1. Alterações

| Ficheiro | O quê |
|---|---|
| `library/kernel/tools/process_map.py` | O desenho: `layout` e `render_svg` reescritos, `_ranks`, `_edge_path`, `BAND_ORDER` e `BAND_TITLE`. A verificação: `passage_units`, `MAP-PASSAGE-UNPLACED`, `MAP-SOURCE-UNITEMIZED` e as âncoras `¶N–M` em `resolve_ref`; o veredicto passa a contar os parágrafos (`passages`) |
| `library/kernel/tools/dashboard.py` | CSS `.ns` (quem faz o passo) no separador Mapa |
| `library/kernel/capture-templates/process-map.guide.md` | Secção «Fontes curtas: parágrafo a parágrafo»; âncora em intervalo |
| `.claude/skills/aisa-capture/SKILL.md` | 5d.a: a regra dos parágrafos |
| `.claude/tests/test_process_map_capture.py` | `MAP24_DesenhoLegivel` (6 testes) |
| `.claude/tests/test_process_map_passages.py` | 8 testes novos |

**Regras do desenho:**
- Os nomes das faixas vêm do tipo (`lane.kind`), não da tecnologia. Um processo sem Excel desenha-se igual.
- Numa faixa com vários membros, cada passo mostra quem o faz, excepto o membro com mais passos, que vai em primeiro no subtítulo.
- O conteúdo do mapa não muda, e o mesmo mapa dá sempre os mesmos bytes.

**Regras da verificação:**
- Só entram fontes curtas: extracção LT `ok`, até 60 parágrafos, excluindo `.vtt` e `.srt`.
- Uma fonte mais longa fica como lacuna explícita (`MAP-SOURCE-UNITEMIZED`), não passa em silêncio.
- A âncora simples `¶N` mantém o digest, por isso os mapas já publicados continuam actuais.
- Uma exclusão material continua a exigir `D-NNN`.

## 2. Demonstração

### 2.1 Réplica local da corrida 1

Réplica feita na sessão avaliadora com as 3 notas curtas e os mapas reais v02/v03, fora do git.

| Mapa | Parágrafos por dispor | Inclui a omissão da corrida 1? |
|---|---|---|
| v02 (antes da correcção) | 64 de 68 | Sim: os parágrafos da omissão aparecem nomeados, e **a v02 seria recusada** |
| v03 | 60 de 68 | Não. Mas uma nota inteira continuava sem nenhum parágrafo citado no mapa |

### 2.2 Desenho

| Mapa | Faixas | Largura × altura |
|---|---|---|
| Corrida 1, v03 (desenho antigo) | 10 | 3130 × 1156 |
| Corrida 1, v03 (desenho novo) | 4 | 2574 × 684 |
| Corrida 2, v01 (desenho novo, 26 nós) | 5 | 1974 × 1460 |

A largura depende do número de posições do fluxo. A corrida 2 mostrou um defeito face à regra: exceções numa coluna vazia subiam ao topo e liam-se como caminho principal. Está corrigido (linhas próprias de exceção), com teste.

### 2.3 Corrida 2 do piloto

**Montagem:** sessão `session_01UwZr9A4JE1HrXU1P4cLCco`, sobre `5eb7ab2`, com checkout parcial e sem referência; as mesmas 6 fontes.

| Métrica | Corrida 1 (v01) | Corrida 2 (v01) |
|---|---|---|
| Nós · dúvidas | 16 · 7 | 26 · 24 |
| Expectativas cobertas na 1.ª versão | 11 de 14 (2 omissões materiais) | 14 de 14 |
| Correcções do dono | 2 versões de correcção (v02, v03) | 0 (validou a v01) |
| Contradição de fonte (regra da média mais baixa vs MAX nas folhas) | não levantada | levantada como dúvida |
| `MAP-PASSAGE-UNPLACED` na 1.ª tentativa | não existia | 0 de 86 (o autor dispôs tudo de antemão; 7 blocos de metadados) |
| Vendor/produto antes de Opções | — | nenhum; só sistemas actuais |

## 3. Leitura crítica

- **n = 1.** Uma corrida não prova o efeito; outra corrida pode variar.
- **Efeito misturado.** A verificação não recusou nada na corrida 2: o autor cumpriu a regra de antemão, porque o guia e a skill lha dão. Não se separa o efeito da verificação do efeito do texto do guia.
- **O guia traz uma lição da corrida 1.** Menciona, em termos genéricos, uma exceção dita pelo dono que ficou fora do mapa. Não é a resposta, mas é um empurrão derivado do piloto: a corrida 2 **não é uma réplica cega**.
- **Custo.** A extracção trata cada linha quebrada de um `.md` como um parágrafo: 86 unidades em 4 notas curtas. O custo real é baixo com intervalos (7 entradas de metadados na corrida 2), mas cresce com fontes mais longas até ao limite de 60.
- **O que a verificação não garante.** Garante uma disposição explícita, não uma disposição correcta. Um parágrafo citado num detalhe genérico passa. Para o casar com um elemento certo é preciso julgamento: o revisor C, não implementado.

## 4. Verificação A (saída ou cálculo absorvido): não implementada

No piloto, os 60 cálculos são «terminais» em 6 folhas, incluindo folhas intermédias. A regra «folha de saída sem nó» daria falsos positivos.

A regra certa é detectar quando um passo absorve cadeias de cálculo independentes, mas depende da v01 da corrida 1 (`mp-v01.json` + calc-chain), que não chegou. A corrida 2 não serve: já tem o passo em causa. **Fica pendente.**

## 5. Verificação

Com `AISA_GUARD_MODE=enforce`:

| Suite | Ficheiros | Testes | Falhas / erros | Skips | Falhas esperadas |
|---|---|---|---|---|---|
| Completa | 122/122 | 3227 | 0 / 0 | 34 | 3 |
| Stdlib | 103/103 | 2429 | 0 / 0 | 28 | 0 |

Testes novos:
- **Desenho:**
  - faixas por tipo e sem faixas vazias;
  - quem faz o passo só quando não é o de omissão;
  - colunas pelo fluxo;
  - exceções laterais por baixo;
  - ligações sem curvas;
  - determinismo.
- **Parágrafos:**
  - parágrafo sem destino recusado e nomeado;
  - intervalo cobre;
  - intervalo inválido não resolve;
  - âncora simples mantém o digest;
  - exclusão material pede autoridade;
  - `.vtt` e extracção falhada ficam de fora;
  - fonte longa gera lacuna;
  - contagem no veredicto.


## 6. Limitações

- A verificação A está pendente (§4).
- O revisor C não foi implementado. A decisão 2 da adenda mantém-se até haver evidência de disposições erradas.
- O desenho legível continua largo num fluxo longo: não há quebra em várias linhas.
- A tabela da nota de risco (linhas de tabela sem `¶`) não é vista pela verificação. O autor registou-o.

## Decisão do mantenedor

Pendente:
1. Aceitar o M5.1.
2. A verificação A: trazer a v01 da corrida 1, ou abandonar a verificação.
3. Seguimento do M5 (tarefas 3–7) sobre a corrida 2, que tem o autor limpo.

## Retoma

1. Ler este relatório e `docs/process-map/M5/RELATORIO.md`.
2. A sessão do autor da corrida 2 tem o engagement `pricing-marinha` validado (D-001, v01), pronto para a descoberta.
