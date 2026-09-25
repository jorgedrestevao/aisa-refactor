# Guia de autoria — mapa de conhecimento do processo (AS-IS)

Quem usa: `aisa-capture` passo 5d, **inline**, na sessão principal, logo depois da L2
(`process-model.md`). A autoria não é delegável: o detalhe alimenta a validação pelo dono e o
Discovery (`CLAUDE.md` → *Delegação a subagentes*).
Contrato: `library/kernel/schemas/process-map.schema.json` (`process-map/1`).
Motor: `library/kernel/tools/process_map.py`. Plano: `docs/process-map/PLANO.md`.

## Para que serve

O mapa é a representação do processo que a captura compreendeu: quem faz o quê, por que
ordem, com que decisões e exceções, o que sai e para quem. É o **esqueleto** do engagement.
O Discovery trabalha sobre ele, e o blueprint e o handoff verificam contra ele.

O mapa **organiza** conhecimento e referências, mas não é autoridade de factos: esses vivem
na Shared Understanding. O mapa também não decide âmbito: isso vive em `decisions.md`.

## Entradas, por esta ordem

1. **`enquadramento.md` (P-0).** Os actores, o gatilho, as actividades e os resultados que o
   dono declarou. Orientam o que procurar e **nunca filtram**. Uma divergência com os
   ficheiros é um elemento ou uma dúvida (`MAPG`), não um descarte.
2. **`_capture/process-model.md`.**
   - §4 é a síntese: dá passos, saídas, consumidores, exceções e invariantes.
   - §4bis é a cadeia de cálculo.
   - §2 é a classificação de colunas (uma coluna manual indica um passo humano).
   - §6 são as perguntas `PM-U`.
3. **`_capture/*.calc-chain.json`.** Um `CALC-NNN` por saída calculada, **por workbook**.
4. **`_capture/evidence-index.md`.** Diz que fontes existem e em que estado. Uma extracção
   falhada aparece no mapa como leitura incompleta; nunca como se tivesse sido lida.
5. **Fontes originais**, só onde a síntese não chega: células, fórmulas, passagens de
   entrevista.

## Elementos

| Coleção | Id | Quando |
|---|---|---|
| Faixa | `MAPL-NNN` | Quem faz (`actor`), ferramenta (`tool`), canal (`channel`), quem recebe (`consumer`), sistema a jusante (`downstream`) |
| Nó | `MAPN-NNN` | Início (`trigger`), passo (`step`), decisão (`decision`), exceção (`exception`), saída (`output`) |
| Aresta | `MAPE-NNN` | Passagem entre nós: `normal`, `exception` ou `branch` (ramo de decisão, com `label`); `carries` diz o que passa |
| Detalhe | `MAPD-NNN` | O que existe num nó ou aresta: `workflow`, `table`, `column`, `calculation`, `intermediate`, `output`, `rule`. Um só `ref` para a evidência; `count` para volume agrupado |
| Dúvida | `MAPG-NNN` | O que falta saber, preso ao elemento (ou `GLOBAL`), com quem responde e `pm_u_ref` quando já existe um `PM-U` |
| Órfão | — | Unidade que a captura produziu e que não tem lugar no mapa, com razão e materialidade |

A ordem (`order`) é a sequência no tempo. A mesma ordem em duas faixas significa passos em
paralelo.

## Profundidade

- **Nível 0**: os passos que o dono reconhece como seus, numa linguagem que ele usaria. Uma
  sequência de fórmulas é um passo ("aplica margem, prémio, transporte, desconto"), não
  vários.
- **Nível 1**: o que é material para o comportamento, a aceitação, a operação ou o esforço.
  O volume repetido é **um** detalhe com `count` e referência ao grupo ("~280 intervalos ·
  101 overrides"). Nunca um elemento por célula.
- **Sem limite de nós.** Se o diagrama ficar denso, agrupa-se, mas não se omite nada: a
  tabela de passos é a vista completa.

## Evidência e marcas

- `OBSERVED` / `INFERRED` / `HYPOTHESIS` / `UNKNOWN`, com o mesmo significado que na captura.
  São marcas, não estados da SU, e nunca se promovem por estarem no mapa.
- Nós e arestas não `UNKNOWN` levam `evidence` resolúvel. `INFERRED` e `HYPOTHESIS` levam a
  **base** da inferência, o que não os torna observados.
- No detalhe, o `ref` é a evidência.
- `UNKNOWN` não leva evidência inventada: leva uma dúvida (`MAPG`) presa ao elemento.
- Referências: `<caminho>[#<âncora>]`, relativo ao engagement.
  - `_capture/process-model.md#PM-012`, `#PM-U-003`, `#§4:<etiqueta>`;
  - `_capture/<wb>.calc-chain.json#CALC-003` (**sempre** pelo ficheiro: o mesmo `CALC-003`
    existe noutros workbooks);
  - `_capture/<f>.extraction.json#sheets[name=<folha>]`;
  - `_capture/<f>.text.md#¶12`, ou um intervalo `#¶6–9` (cobre todos os parágrafos do intervalo);
  - `enquadramento.md#T4`.
- Nunca se inventa uma referência para passar no `check`.

## Transferência: nada desaparece em silêncio

Cada `PM-NNN`, cada `PM-U-NNN`, cada `CALC-NNN` de cada workbook e cada etiqueta material de
§4 fica **num elemento** (por `evidence`, `ref` ou `pm_u_ref`) **ou em `orphans`**:

| Razão | Quando | O que implica |
|---|---|---|
| `gap_in_map` | Ainda não se sabe onde entra | Fica aberto e visível até ser colocado |
| `undetermined` | Materialidade por avaliar | Fica aberto e visível |
| `out_of_scope` | Não pertence ao processo a entregar | Justificação obrigatória; se for material, só com a decisão (`D-NNN`) que a autoriza |

Um órfão não é cobertura. Os abertos acompanham a validação, o Discovery e o blueprint.

### Fontes curtas: parágrafo a parágrafo

Cada parágrafo com conteúdo de uma fonte de texto curta (extracção LT `ok`, até 60
parágrafos; as transcrições com tempo `.vtt`/`.srt` ficam de fora) também tem destino: é
citado num elemento ou disposto em `orphans` — `MAP-PASSAGE-UNPLACED` diz quais faltam, por
fonte e em intervalos. É a pergunta «o que diz esta fonte que o mapa não mostra?», feita a
todas as frases de uma nota, uma citação ou um e-mail do dono.

- Metadados (data, autor, cabeçalho) dispõem-se em bloco: `out_of_scope`, `not-material`,
  com a nota.
- Uma dor, uma exceção ou uma dependência dita pelo dono é **um elemento** (ou uma dúvida
  presa a um), não um órfão — citar o parágrafo num detalhe genérico para o calar é
  satisfazer o validador.
- Uma fonte mais longa aparece como lacuna `MAP-SOURCE-UNITEMIZED`: não foi verificada
  parágrafo a parágrafo, e a validação do dono sabe-o.

## Identidade e linhagem

- Ids estáveis entre versões e nunca reutilizados.
- Um elemento que deixa de existir fica em `retired_ids` com a razão.
- Quem o substitui diz `was: [<id antigo>]`: uma divisão tem dois sucessores e uma fusão tem
  duas origens.
- A versão anterior guarda o conteúdo histórico (`_map/history/`).

## Ciclo de autoria

```bash
python library/kernel/tools/process_map.py stamp   --engagement <slug> --draft <fora-do-engagement>.json
python library/kernel/tools/process_map.py check   --engagement <slug> --draft <f> --json
python library/kernel/tools/process_map.py publish --engagement <slug> --draft <f> --json
python library/kernel/tools/process_map.py render  --engagement <slug>
```

- **O rascunho fica fora do engagement.** Quem publica é o coordenador.
- **`stamp` só preenche o que falta** (`base`, o digest de uma referência, as fontes
  consumidas). Nunca substitui: actualizar um digest não é reavaliar o elemento.
- **Erros do `check`** (exit 2): corrige-se a **estrutura** sem mudar o significado. Uma
  ligação partida corrige-se para o id certo; um `CALC` ambíguo qualifica-se pelo ficheiro;
  uma unidade sem destino coloca-se ou vai para `orphans` com a razão verdadeira. **Nunca** se
  apaga uma dúvida, se muda uma marca ou se cita outra fonte só para o validador passar.
- **Lacunas** (exit 4) publicam-se: o mapa pode ser publicado e validado com dúvidas
  explícitas.
- **`MAP-BASE-STALE`**: reabrir sobre a versão publicada e reconciliar as diferenças. Nunca
  forçar nem incrementar.
- **`MAP-SOURCE-STALE` ou `MAP-REF-STALE`**: reler a fonte, reavaliar os elementos que a
  citam e só depois carimbar de novo.
