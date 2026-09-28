# M4 — Contexto, retoma e observabilidade

Estado: pronto para revisão
Base: `claude/claim-credit-endpoint-e2oqht`, depois do M3 (`95453d5`).
Plano: `docs/process-map/PLANO.md`.

**Resultado:**
- **Retoma sem conversa:** uma sessão nova recupera o processo a partir dos ficheiros (passos, validação, actualidade, bloqueios e próxima acção), lido dos mesmos bytes que a retoma validou.
- **Revalidação proporcional:** uma fonte que muda entre sessões fica por revalidar. A revalidação é proporcional e explícita, e trocar um hash nunca repõe o estado actual.
- **Separador Mapa:** o dashboard passa a mostrá-lo.

## 1. O que passou a funcionar

| Tarefa do M4 | Onde |
|---|---|
| 1. `summary` | `process_map.summary` + CLI `summary --task …` |
| 2. Mapa nos inputs do bootstrap e leitura consistente | `workflow.resume` → `bootstrap(inputs=(checkpoint, "_map/map.json"))` e `_process_map_context` |
| 3. Orçamento | `summary(budget=…)` |
| 4. Retoma real | `workflow.resume` (`process_map`, próxima acção); `aisa-status` 2b e bloco de alerta; `.claude/commands/resume.md` |
| 5. Pontos de leitura por fase | `aisa-frame` (framing), `aisa-options` (options), `aisa-blueprint` 1e (blueprint); handoff via `release.process_coverage` (M3) |
| 6. Separador Mapa | `dashboard.py` (`process_map_state`, `TAB_SPEC`, painel, `INDEX_DIRS`, CSS); `on-su-change.py`; `aisa-capture` 5d |
| 7. Fonte alterada entre sessões e revalidação proporcional | `process_map.freshness`, `revalidate`, `structural_digest`, validação transportada |

**Tarefa 1: `summary`.**
- Dá versão, digest, validação do dono, actualidade por fonte, bloqueios e o estado de cada bloco.
- O estado de cada bloco inclui as linhas da SU por estado e as dúvidas; um bloco sem linhas é marcado como sinal para investigar.
- O detalhe só aparece para o que a tarefa pede:

| Tarefa | Detalhe incluído |
|---|---|
| `resume` | só o nível 0 |
| `framing` | saídas |
| `options` | saídas, exceções e decisões |
| `blueprint` | todos os blocos, com evidência |
| `handoff` | saídas e exceções |

**Tarefa 2: leitura consistente.**
- O resumo sai dos bytes cujo digest o snapshot validou.
- Se o mapa mudar a meio (`retry`), nada se resume e nunca se mostra estado misto.

**Tarefa 3: orçamento.**
- O mapa usa o orçamento que sobra do contexto da retoma, e não o grafo.
- Acima do orçamento, o resumo sai `partial`, com o que ficou de fora e o comando para expandir.
- Os bloqueios nunca se truncam.

**Tarefa 4: retoma real.**
- Com fontes mudadas, a próxima acção é o `revalidate` com as fontes e os elementos afectados.
- Com o mapa por validar, é `/capture` para rever com o dono.

**Tarefa 5: pontos de leitura por fase.**
- **Framing:** a frase do problema tem de aguentar as saídas e os consumidores do mapa.
- **Options:** cálculos, volumes, exceções e decisões.
- **Blueprint:** jornada a jornada.

**Tarefa 6: separador Mapa.**
- Lê o motor do mapa e não o reconstrói.
- Mostra o mesmo SVG da vista, os bloqueios em linguagem de negócio e uma tabela por passo com o que se sabe e as dúvidas.
- Regenera-se explicitamente depois da publicação: a publicação em Python não dispara o hook de edição.

**Tarefa 7: revalidação proporcional.**
- **Âncoras iguais:** a fonte mudou fora do que o mapa cita, por exemplo o carimbo de uma recaptura. O `revalidate` regista a reavaliação, e a validação do dono transporta-se porque a representação é a mesma.
- **Âncoras mudadas:** só os elementos declarados como revistos recebem o digest novo. Os outros ficam `MAP-REF-STALE` e o `check` recusa. Com os elementos revistos, a validação do dono fica `stale` e pede nova validação.
- **Troca de digest sem registo em `revalidations`:** o mapa fica actual, mas a validação não se transporta.

**Mudanças de suporte:**
- Schema `process-map/1`: campo opcional `revalidations`, compatível com os mapas já publicados.
- Render: rótulos de faixa compridos quebram em duas linhas, em vez de ficarem cortados.

## 2. Verificação

- **Ambiente:** `requirements-dev.txt` + `cffi`, clone completo.
- **Override:** pelo procedimento aprovado, reposto no fecho.

| Execução | Resultado |
|---|---|
| `test_process_map_resume.py` | 14 OK |
| Mutações: validação transportada sem registo; leitura do mapa fora do snapshot | 2 testes falham; repostos, 14 OK |
| `test_process_map_{core,capture,validation,coverage}` e os testes de retoma, dashboard, linguagem e delegação | OK |
| Suite completa e stdlib (`enforce`) | ver §2.1 |

### 2.1 Fecho

Com `AISA_GUARD_MODE=enforce`:

| Suite | Ficheiros | Testes | Falhas / erros | Skips | Falhas esperadas |
|---|---|---|---|---|---|
| Completa (`python .github/run_tests.py`) | 121/121 OK | 3211 | 0 / 0 | 34 | 3 |
| Stdlib (`--list .github/stdlib-tests.txt`) | 102/102 OK | 2413 | 0 / 0 | 28 | 0 |

O F0 T02 passa: os ficheiros novos do M4 estão registados em `consumer-matrix.json`.

### Testes de fecho do plano

| Caso | Teste |
|---|---|
| MAP-23 | `MAP23_Retoma`: o `resume` traz o mapa com o digest do snapshot; um mapa que muda sob a leitura dá `retry`; orçamento 1 → parcial, com `omitted` e `--budget 3`, e os bloqueios iguais; orçamento 0 → blocos vazios e bloqueios presentes; `blueprint` traz o detalhe e `resume` não; sem mapa → `absent`; pendência → `RECOVERY_REQUIRED` antes do mapa |
| MAP-22 | `MAP22_Actualidade`: editorial → âncoras iguais, próxima acção `revalidate`, validação transportada; material → elementos afectados, recusa sem revisão, validação `stale` depois; digest trocado sem registo → a validação não se transporta; revalidar uma fonte que não mudou é recusado |
| MAP-24 | `MAP24_Dashboard`: o estado do separador é estável e o SVG é o do motor (o escape e o determinismo da página do mapa já estavam no M2); sem mapa, «indisponível»; o separador está declarado e `_map/` dispara a regeneração |
| SU antiga | `SUAntiga`: sem a coluna, as linhas ficam «não avaliadas» e o passo sem associação fica por investigar |

## 3. Demonstração: retoma fria

```bash
python docs/process-map/M4/demo.py      # escreve demo-output.txt
```

A retoma corre num **processo Python novo**, sem nada da execução anterior em memória. Tudo sai dos ficheiros.

1. **Retoma fria.** Processo com 3 passos: «Dia útil (Fixador) → Calcula o preço (Fixador) → Resumo diário (Comerciais)». Mapa `mp-v01`, validado (`D-002`), fontes actuais.
2. **Uma fonte muda entre sessões** (nota editorial). Na retoma, as fontes aparecem `stale` e o bloqueio diz «`_capture/process-model.md` mudou (âncoras iguais — revalidar)». A seguir: `process_map.py revalidate --engagement novo --source _capture/process-model.md …`.
3. **Revalidação registada** (`mp-v02`). Na retoma, as fontes voltam a estar actuais e a validação `D-002` transporta-se.

## 4. Limitações

- **Carimbo do `calc-chain.json`.** Do lado do mapa está resolvido: uma recaptura só muda o carimbo, as âncoras ficam iguais e basta uma revalidação registada. A **reconciliação de cobertura** continua a ler o ficheiro inteiro como fonte de actualidade, e por isso uma recaptura deixa-a `stale`, a refazer pelo circuito normal. Tornar a cobertura sensível à âncora mudaria o contrato de cobertura §6.3 e não está no âmbito do M4.
- **Página inteira do dashboard.** Não é byte-estável: tem a hora de geração, como antes. O modelo e o SVG do separador são estáveis.
- **`/resume`.** O texto do comando e do `aisa-status` foi actualizado, mas a formulação em linguagem de negócio é da skill. Os testes cobrem o motor (`workflow.resume`) e não a frase final.
- **Pontos de leitura por fase.** São instruções das skills. Nenhum motor verifica que o frame considerou cada saída do mapa: isso é julgamento do revisor (`frame-reviewer`).

## 5. Decisão do mantenedor

Pendente:
1. Aceitar o M4.
2. Autorizar o M5 (piloto integral Pricing Marinha).
   - Pré-condição: os ficheiros reais autorizados em `projects/<slug>/inputs/`.
   - O fluxograma de referência fica separado do contexto do autor.

## Retoma

**Próxima acção:** revisão do M4. Depois, disponibilizar os ficheiros do piloto M5.
