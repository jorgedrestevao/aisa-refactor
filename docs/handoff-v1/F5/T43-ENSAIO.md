# T43 — Primeiro ensaio do destinatário em contexto novo (F5.5)

Estado: **ensaio assistido documentado, simulado** — não é aceitação (plano 06: T43 exige julgamento humano ou avaliação assistida documentada; plano 08 → *Critério de fecho*: sem equipa disponível, rotular a revisão como simulada).

## 1. Montagem

| Item | Valor |
| --- | --- |
| Pacote | `docs/handoff-v1/F5/pacote-fx-hv1-02/` — 19 ficheiros com `sha256` em `handoff-index.json` (`handoff-index/1`) |
| Gerado por | `python .claude/tests/test_hv1_vertical.py --write <pasta>` (percurso vertical pelos motores; candidatos, pareceres e FC escritos pelo teste a partir do `expected` da fixture) |
| Versão do código / pack | `ce218ce` · `pp` 1.10.0 |
| Nível | `delivery_level: preliminary`, rótulo «preliminary · incompleto — não é pronto para construção»; `receiver_acceptance: null` |
| Exclusões declaradas | `implementation-spec`, `estimate` (DESENHO Q9), `FC-0002` (bloqueado por U-001), gestão de stock, recepção física |
| Destinatário | um subagente `general-purpose`, uma chamada, contexto novo; instrução: ler só a pasta do pacote, não escrever, não inventar; as seis tarefas do plano 08 → *Revisão de destinatário* |
| Custo medido | 1 chamada · 4 usos de ferramenta · ~79 k tokens do subagente · 90,6 s |
| Retrabalho | nenhum ainda (as lacunas sistémicas vão ao mantenedor, abaixo) |

Limite do ensaio: o subagente recebe, como qualquer subagente desta sessão, o `CLAUDE.md` do repositório — contexto que uma equipa real não teria. Declarou não ter aberto nada fora da pasta.

## 2. Resultado, em números

- Leu os 19 ficheiros do índice e conferiu os 19 `sha256`.
- Identificou o âmbito, as exclusões e as quatro decisões (D-001..D-004), e que só o FC-0001 está autorizado.
- Classificou **17 lacunas**: `blocks_all` 3 · `blocks_scope` 7 · `delegated_choice` 3 · `implementation_proof` 4.
- Fez **4 perguntas bloqueantes** ao autor.
- Detectou correctamente a falta do trabalho e da estimativa (o que Q9 queria medir), e a regra de arredondamento como bloqueio do valor, com o exemplo de fronteira.

## 3. Verificação das afirmações (feita na sessão, contra o pacote)

Todas as afirmações centrais conferem:

- `FC-0001.authorization_ref = null` e `publication_status: draft`, enquanto o índice diz `authorization: current`;
- D-004 com `Timestamp` 22:00, antes do D-003 (23:00);
- os três mandatos citam `decisions.md` sha `1022c9…`, e o pacote leva `5b7ae1…`;
- `_state.json.phase = options`;
- a disposição `accepted` de REV-0002.F01 promete «no FC como exemplo negativo», e nenhum FC o tem;
- `SCOPE-0001` só aparece por referência.

## 4. Classificação das lacunas

### 4.1 Sistémicas (motor, contrato ou pacote)

São defeitos do método, e repetem-se em qualquer engagement.

| # | Lacuna (L- do destinatário) | Onde nasce | Correcção possível |
| --- | --- | --- | --- |
| S1 | A autorização do FC não se lê no FC: `authorization_ref`/`publication_status` ficam `null`/`draft` depois do bloco D-NNN, e três fontes discordam para quem não corre o motor (L-07). A canonicalização do `item_sha256` não vem no pacote | `functional.py` (a autorização é derivada, por desenho F4); pacote sem o contrato | projectar o estado de autorização no pacote (ficheiro `functional-state.json` de `functional.show`) e incluir o contrato/esquemas que permitem verificar o hash |
| S2 | `SCOPE-0001` é referido (FC, D-004, índice) e nunca definido (L-06) | não há artefacto de âmbito autorizado no pacote | o índice leva a definição do âmbito (itens incluídos, com as linhas da SU), ou aponta o bloco que o define |
| S3 | Uma disposição `accepted` regista-se sem que a correcção exista (REV-0002.F01; L-03) | `review.dispose` aceita qualquer justificação | `accepted` passa a exigir a referência do que corrige (revisão do candidato, `FC-NNNN`, ou versão do desenho), a verificar pelo motor |
| S4 | Os pareceres apontam versões de inputs que o pacote não leva (L-16) | o pacote copia só a revisão corrente | o índice declara, por parecer, a base que leu e se continua corrente, ou o pacote leva as cópias históricas usadas |
| S5 | As unidades do pack citadas nos mandatos não vêm no pacote (L-14) | pacote | incluir as `knowledge_refs` dos mandatos (caminho + `sha256`) |
| S6 | A convenção dos localizadores `#¶n` não está declarada (L-15) | kernel (convenção implícita) | o índice ou um LEIA-ME declara a convenção |
| S7 | Uma autorização datada antes da aprovação do desenho passa (D-004 22:00 < D-003 23:00) | `functional.authorization_block` não verifica a ordem; as horas do teste estavam fixas | exigir que o bloco de autorização seja posterior à aprovação do desenho em que assenta |

### 4.2 Artefactos da fixture (não são defeitos do método)

- `phase: options` e o cabeçalho da SU «Discovery» — o teste não fez as transições de fase.
- Requisitos que estão nas entradas e não na SU (duplicação [C6], auditoria M5, retenção D3, ERP-X; L-05, L-10): a análise da F3 foi escrita pelo teste e é parcial. Mesmo assim, o destinatário encontrou-os: é a prova de que um pacote com a SU incompleta se denuncia.
- Blueprint sem modelo de linhas nem origem do preço (L-09), e só dois FC (sem aprovação, segregação ou passagem a compras; L-03): fixture da F4, escrita para provar os motores.
- Sem trabalho nem estimativa (L-08): esperado (Q9) e detectado.

### 4.3 Esperadas e bem classificadas

- L-01 e L-02 (`blocks_scope`, regras do dono).
- L-11, L-12 e L-17 (`delegated_choice`).

## 5. Relatório do destinatário (transcrição; conteúdo integral, formatação simplificada)

<details><summary>Relatório devolvido pelo subagente</summary>

```
## 1. Âmbito, exclusões, decisões
- Nível do pacote: handoff-index.json → delivery_level: preliminary, label «não é pronto para construção», render_final_allowed: false, receiver_acceptance: null. Os 19 hashes de files[] conferem (verifiquei).
- Âmbito: SCOPE-0001 = pedido, aprovação e passagem a compras (C-001; pedido.md P2). O pacote não define SCOPE-0001 em lado nenhum; só aparece por referência.
- Exclusões (índice): implementation-spec, estimate (não renderizados), FC-0002 (bloqueado por U-001), gestão de stock, recepção física.
- Decisões (decisions.md): D-001 plataforma imposta («Plataforma X»; pedido.md P1 diz Power Platform) · D-002 escolhe O-001, descarta O-002 por reversibilidade baixa · D-003 aprova blueprint bp-v01 (sem dizer conteúdo/hash) · D-004 autoriza só FC-0001 (sha 2235b…).
- Contradições: FC-0001.authorization_ref = null e publication_status: draft, mas o índice diz authorization: current; o hash do D-004 não é reproduzível (a canonicalização não vem no pacote). D-004 (22:00) autoriza um FC baseado num blueprint que só foi aprovado em D-003 (23:00). _state.json diz phase: options e o SU diz «Discovery», mas já há decisões.

## 2. Ordem de construção
O pacote não dá inventário nem dependências (não há implementation-spec). Ordem inferida por mim, não autorizada:
1. Modelo pedidos (id_pedido, chave_submissao, valor_total, estado) — faltam as linhas (quantidade, preço unitário) exigidas por C-002.
2. FC-0001, submissão idempotente (submissao-idempotente, pattern direct) + ecrã PedidoFormScreen.
3. FC-0002, cálculo do valor — bloqueado por U-001.
4. Aprovação por papel + segregação no servidor (REV-0002.F01 aceite) — não há FC.
5. Roteamento para a direcção financeira — bloqueado por U-002, e também sem FC.
6. Passagem a compras + caminho urgente (C-003/A-001) — sem FC, sem ecrã, sem estado.
Só o passo 2 está autorizado.

## 3. Jornada e caminho de falha
Submissão (J-0001/FC-0001): o requerente preenche PedidoFormScreen → na submissão, o servidor procura chave_submissao; se existe, devolve o pedido existente; se não existe, grava com estado=submetido. Pós-condição: um só pedido por chave. Aceitação: exemplo positivo e negativo do FC-0001.
Falha: «falha de rede depois da gravação → a repetição devolve o mesmo pedido». Implementava-a com restrição de unicidade sobre a chave, gerada no cliente quando o formulário abre.
O pacote não diz: quem gera a chave, formato e tempo de vida; o que acontece com a mesma chave e conteúdo diferente; porque é que estado é input do requerente; como se captam as linhas; de onde vem o preço (nota-dados.md D1: catálogo no ERP-X, cópia manual). A causa real da duplicação (entrevista-processo.md [C6]/¶7) não tem linha no SU: FC-0001 cita C-002/C-003, que não falam de duplicação.
Falha em FC-0002: «linha sem preço → não submete» — bloqueado.

## 4. O que falta do cliente
- Decisões: regra de arredondamento por linha ou no total (U-001) e o modo (meio para cima ou bancário), que nem U-001 cobre; tratamento do urgente rejeitado depois de encomendado; escalada quando a chefia não valida no dia (A-001).
- Dados: valor do limiar do despacho da direcção financeira (U-002); taxa de IVA (os 23% só aparecem num exemplo do FC-0002, sem linha no SU); catálogo e preços do ERP-X; hierarquia chefia→equipa (matriz-papeis.md M2); pedidos históricos em email e folha (D2) — migrar ou não.
- Acessos: fonte de identidade/papéis, acesso ao ERP-X, licenciamento da plataforma.
- Ambientes: nenhum referido (dev/test/prod, gestão de alterações).

## 5. Aceitação e operação
- Aceitação possível hoje: os dois exemplos do FC-0001. proofs.performed = [].
- Provas pendentes (índice): submissão repetida; segregação C-004 recusada no servidor — esta sem FC nem exemplo, apesar de ledger.json seq 2 dizer «entra… no FC como exemplo negativo» (compromisso não cumprido; REV-0002.F01 devia constar em open_findings).
- Limite do FC-0002: o exemplo de U-001 (3×0,335 € → 1,02 contra 1,01) é o teste de fronteira previsto, mas falta MISSING_EXAMPLE_BOUNDARY (render-gate.json).
- Operação/recuperação: nada no pacote — monitorização, cópias de segurança, RPO/RTO, suporte.
- Não entrou no SU: retenção de 10 anos (nota-dados.md D3) e trilho de auditoria «quem aprovou o quê e quando» (matriz-papeis.md M5); o blueprint não tem campos de auditoria nem de aprovador.

## 6. Lacunas
| id | lacuna | classe | justificação | ficheiro onde devia estar |
|---|---|---|---|---|
| L-01 | Regra de arredondamento (U-001) + modo | blocks_scope | Regra essencial do valor; o dono não escolheu. Defeito do handoff: FC-0002 entregue sem ela | answers.md / FC-0002 calculation.rounding |
| L-02 | Limiar da direcção financeira (U-002) | blocks_scope | Muda o roteamento da aprovação. Defeito: redescobrir | answers.md, FC de aprovação |
| L-03 | Não há FC para aprovação, segregação, passagem a compras | blocks_scope | 2/3 do SCOPE-0001 sem contrato; REV-0002.F01 aceite sem ser cumprido. Defeito | _design/functional-contracts.json |
| L-04 | Caminho urgente: rejeição depois da encomenda, falta de validação no dia | blocks_scope | Regra essencial por decidir (C-003/A-001). Defeito | SU (Unknown), FC |
| L-05 | Auditoria (M5) e retenção de 10 anos (D3) fora do SU e do blueprint | blocks_scope | Requisitos de operação/conformidade perdidos. Defeito | shared-understanding.md, blueprint |
| L-06 | SCOPE-0001 não definido; D-003 sem conteúdo/hash | blocks_all | Não consigo saber o que está autorizado/aprovado | decisions.md / índice |
| L-07 | Autorização do FC-0001 contraditória (null/draft contra current); hash do D-004 não verificável | blocks_all | Não posso construir sobre uma autorização que não verifico | functional-contracts.json, contrato de hash |
| L-08 | Não há inventário, dependências, estimativa nem implementation-spec | blocks_all | Excluídos por desenho; sem eles não há plano | _render/implementation-spec, estimate |
| L-09 | Faltam o modelo de linhas, a origem do preço (ERP-X) e o estado «encomendado» | blocks_scope | C-002 e a passagem a compras não se implementam com 4 campos | blueprint record_authority |
| L-10 | Proveniência errada no blueprint (id_pedido/chave_submissao citam C-002; estado cita C-003); duplicação [C6] sem linha no SU | implementation_proof | Rasto quebrado; o requisito existe na entrevista | blueprint, SU |
| L-11 | Formato, geração e tempo de vida da chave; mesma chave com conteúdo diferente | delegated_choice | Dentro do envelope do FC-0001; trabalho normal | FC-0001 |
| L-12 | Ecrãs de chefia, compras e consulta; personas além do Requerente | delegated_choice | Com o FC dado é desenho normal; sem ele depende de L-03 | blueprint |
| L-13 | Ambientes, identidade, operação, recuperação, migração (D2) | blocks_scope | Não há deliverable de operação | pacote de operação |
| L-14 | Pack architecture-core.md citado em REV-0001, fora do pacote | implementation_proof | O revisor usou uma norma que não recebo | library/packs/pp/... |
| L-15 | Localizadores #¶n contam o título como ¶1, sem convenção declarada; D-001/route_basis citam pedido.md#¶2 (o cabeçalho «De/Data»), não P1 | implementation_proof | Rastreabilidade ambígua | índice / SU |
| L-16 | Mandatos citam decisions.md sha 1022c…, o pacote tem 5b7ae… | implementation_proof | As revisões foram feitas contra outra revisão das decisões | ledger / revisões |
| L-17 | Cor do botão (U-003) | delegated_choice | Estacionada, sem impacto | — |

## 7. Perguntas bloqueantes ao autor
1. O que é SCOPE-0001, e o FC-0001 está autorizado ou é rascunho? Como se verifica o sha 2235b… do D-004?
2. Onde estão os FC de aprovação, segregação (REV-0002.F01) e passagem a compras? Se não existem, o pacote cobre só a submissão?
3. Há inventário e dependências fora da implementation-spec excluída, ou a ordem fica a meu cargo?
4. Que blueprint aprovou o D-003 (hash)? O modelo de linhas e a origem do preço estão incluídos?

## 8. Ficheiros lidos e o mais difícil
Li os 19 do índice. Não abri nada fora da pasta. O mais difícil: a definição de SCOPE-0001 (não existe); o estado real da autorização do FC-0001 (três fontes discordam); a convenção dos ¶n contra as etiquetas [C1]/[M1]/[P1] das entradas; requisitos que só estão nas entradas e não no SU (duplicação, auditoria, retenção, ERP-X).
```

</details>
