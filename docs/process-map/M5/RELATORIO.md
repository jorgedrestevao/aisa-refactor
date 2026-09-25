# M5 — Piloto integral (primeiro corte: captura + mapa)

Estado: pronto para revisão (corte parcial autorizado)
Base: `claude/claim-credit-endpoint-e2oqht`. O piloto correu sobre `d1c3d24`; a correcção descoberta está em `27e014a`.
Plano: `docs/process-map/PLANO.md` (M5, adenda v3.1 → decisão 3).

**Âmbito autorizado pelo dono:** captura, mapa, validação e comparação com a referência. O resto do M5 (tarefas 3–7: Discovery → decisão, MAP-17 no desenho, retoma antes do handoff, pacote) **não correu**.

**Dados reais:** este relatório leva só veredictos e ids. Ficam fora do git, por decisão do dono:
- as fontes;
- o mapa;
- as expectativas;
- a avaliação detalhada.

## Resultado

Com Excel e textos reais, o autor produziu um mapa ligado à evidência, sem nunca ter visto a referência:
- as hipóteses ficaram marcadas;
- nada foi inventado;
- as correcções do dono entraram com linhagem;
- cada validação está ligada ao digest da versão que o dono validou.

A primeira execução teve **duas omissões materiais**. Uma apanhou-a o dono. A outra só a comparação externa com a referência, e **nenhuma a revisão das fontes** (MAP-19 **não demonstrado**).

## 1. Montagem (tarefa 1)

| Item | Como ficou |
|---|---|
| Independência | O autor correu numa sessão separada (`session_01R4NYHoAJtfsBpRsJMmXVG7`), com checkout parcial: `library/` e `.claude/` sem testes, e sem `docs/` nem fixtures. A referência e o oráculo do piloto 4 ficaram só na sessão avaliadora |
| Fontes | 5 ficheiros fixados por sha256 antes da execução; o autor confirmou os 5 |
| Expectativas | Fixadas antes do mapa existir: 10 passos, 1 decisão, 3 exceções, 8 dúvidas, mais o que as notas novas acrescentam |
| Referência | É um **rascunho** feito a partir de um engagement anterior. Serve de expectativa, não de gabarito |

## 2. Execução (tarefa 2)

| Versão | Publicada | Mudança | Validação |
|---|---|---|---|
| mp-v01 | captura | 10 faixas · 16 nós · 7 dúvidas · 0 erros no `check` | — |
| mp-v02 | correcção do dono | +2 nós (MAPN-017/018), +3 arestas, 1 nó corrigido, 1 pergunta reformulada | D-001 (sha = ficheiro ✓) |
| mp-v03 | correcção por comparação externa | +1 nó (MAPN-019), +1 aresta, +1 detalhe, +1 dúvida (MAPG-008). **Nada mais mudou** (diff v02→v03 verificado) | D-002 (sha = ficheiro ✓) |

### Comparação com as expectativas (mp-v03)

| Veredicto | Expectativas |
|---|---|
| Cobertas | E1–E6, E8, D, EX1, EX3 |
| Cobertas com divergência | E1, E3, E9. Justificadas pelas fontes: o que só a referência dizia não entrou no mapa como observado |
| Fundidas num só passo | E7 + E10 (MAPN-011). Não diz quem executa |
| Omissas na mp-v02, corrigidas na mp-v03 | EX2 |

**Para além da referência** (tudo com locator): 7 elementos, cobrindo controlos de auditoria, decisões de comité, saídas por tipo de cliente, regras de cálculo e fronteiras de sistema.

### Omissões (MAP-19)

| Omissão | Evidência já nas fontes capturadas | Descoberta por | Correcção a montante |
|---|---|---|---|
| Passo + saída de um cálculo inteiro (MAPN-017/018) | folhas e cadeia de cálculo já no §1/§2/§4bis do process-model | **dono**, na validação da mp-v01 | §4 + mapa, na mp-v02 ✓ |
| Exceção de recuperação e operação (MAPN-019) | citação directa numa fonte `USED` | **ninguém do circuito**: nem o autor, nem a revisão das fontes, nem o dono. Só a comparação externa | §4, §6 e mapa, na mp-v03 ✓; proveniência registada no `_capture-log` |

**Leitura:**
- A camada do dono funciona.
- A revisão das fontes da L2 e da validação não detecta omissões com evidência directa.
- A regra de admissão classifica a segunda omissão como material (recuperação e operação).

## 3. Achados

| # | Achado | Tratamento |
|---|---|---|
| K1 | O passo 5e.d da captura publicava a validação sem voltar a gerar a vista: a página continuava «por validar» depois da validação | **Corrigido** em `27e014a`: a skill agora gera a página e o dashboard depois do bloco. 2 testes novos; a mutação (sem a correcção) falha. Confirmado no piloto: a mp-v03 mostra «validado pelo dono (D-002)» |
| K2 | Mapa denso (10 faixas); o dono pediu outro critério de agrupamento das faixas | Registado pelo autor como trabalho futuro; fora do M5 |
| K3 | MAP-19 sem mecanismo que detecte omissões | Aberto. Decisão 2 da adenda: reavaliar depois do M5 |
| K4 | MAPE-020 marcada `OBSERVED`, mas a fonte não diz onde a exceção começa | Menor, a rever na descoberta |
| K5 | Possível contradição nas fontes: a regra da «média mais baixa» (PM-003) versus MAX em células do relatório convencional | Não resolvido; é para a descoberta (`Conflicted` candidato) |

## 4. Isolamento

- **Barreira física:** o autor não teve `docs/` nem fixtures no checkout.
- **Não fechado:**
  - o histórico git continuava acessível;
  - os comentários do kernel citam nomes deste processo (`xlsx_extract.py`, `dashboard.py`, `process-model.template.md`);
  - o autor recebeu uma **6.ª fonte**, fora da lista fixada. O conteúdo tecnológico ficou fora por decisão do dono.
- **Exposição à referência, depois da mp-v03:**
  - O utilizador mostrou a referência ao autor duas vezes (link e imagem), depois de a mp-v03 estar publicada e antes da D-002.
  - O autor recusou usá-la e registou-o no `_capture-log`, mas o registo descreve a imagem: o conteúdo **entrou no contexto do autor**.
  - O mapa validado não foi afectado: o sha da mp-v03 é igual ao da D-002 e o diff v02→v03 é só a correcção pedida.
  - A partir daí, **aquela sessão do autor já não serve para avaliar a compreensão**.

## 5. Verificação

Com `AISA_GUARD_MODE=enforce`, sobre `27e014a`:

| Suite | Ficheiros | Testes | Falhas / erros | Skips | Falhas esperadas |
|---|---|---|---|---|---|
| Completa | 121/121 | 3213 | 0 / 0 | 34 | 3 |
| Stdlib | 102/102 | 2415 | 0 / 0 | 28 | 0 |

Não corrido: o `check` do motor sobre `_capture/` do piloto, nesta sessão, porque `_capture/` não foi transferido. Vale o `check` do autor (0 erros, 8 lacunas explícitas).

## 6. Testes de fecho

| Caso | Estado neste corte |
|---|---|
| MAP-01/02 (compreensão com P-0) | Demonstrados parcialmente sobre caso real: 2 omissões na 1.ª execução |
| MAP-19 (omissão detectada a montante) | **Não demonstrado** |
| MAP-17, MAP-21, MAP-23 no handoff, pacote | Não corridos (fora do corte) |
| Restantes MAP-* | Cobertos por testes automáticos M1–M4; não reavaliados sobre o piloto |

## 7. Critérios de aceitação da entrega

**Não satisfeitos**: o corte parou antes do desenho e do pacote. Esta entrega **não** declara:
- que as necessidades materiais do âmbito têm todas destino funcional;
- que uma omissão no desenho bloqueia;
- que a estimativa corresponde ao trabalho.

## Decisão do mantenedor

Pendente:
1. Aceitar este corte do M5.
2. Decidir o seguimento. As opções são:
   - (a) continuar o M5 (tarefas 3–7) numa **sessão de autor nova**, porque a actual viu a referência;
   - (b) tratar K3 (detecção de omissões) antes de continuar;
   - (c) parar aqui.

## Retoma

1. Ler este relatório e `PLANO.md` (M5).
2. As fontes, as expectativas e a avaliação estão fora do git. Estão com o dono e na pasta temporária da sessão avaliadora, que não persiste.
3. Para continuar as tarefas 3–7, criar uma sessão de autor nova sobre `27e014a`, com checkout parcial, e carregar outra vez as fontes e `projects/pricing-marinha/`.
