# Correcção pós-auditoria dos gates da F6 e da F7 (A1–A5)

Estado: **concluída — gates da F6 e da F7 aceites de novo pelo mantenedor** (2026-09-24), depois do CI #93 verde (`c93ff75`: jobs `suite` e `stdlib` com sucesso). Os cinco casos reproduzidos e corrigidos. Os gates da F6 (T33, T39, aceitação do destinatário) e da F7 (T41) ficam **reabertos** até a correcção ter evidência e o mantenedor os aceitar de novo.

Origem: auditoria externa trazida pelo mantenedor, sobre `claude/clone-repo-awui-7mmi37` em `1dcdb61` (suite 111/111, 3033 casos, CI verde): quatro falhas nos gates de entrega. A reprodução desta sessão confirmou as quatro e encontrou a quinta (A5), no próprio cenário «pronto» dos testes do release. O mantenedor separou A3 de A5 e fixou o princípio da correcção: a actualidade das dependências verifica-se também ao consumir, ao renderizar e ao construir o release, não só ao publicar; o hash identifica a mudança, uma revalidação explícita decide se o artefacto tem de mudar.

## 1. Reprodução (antes de qualquer correcção)

Pastas temporárias, pelo cenário `pronto()` de `.claude/tests/test_release.py`; nenhuma escrita no repositório.

| Caso | Passos | Observado | Devia |
| --- | --- | --- | --- |
| A1 | build `ready_for_receiver_review`; publicar em `decisions.md`, por draft/publish, um bloco só com `## D-NNN — Aceitação do destinatário (release r0001)` e `**Release sha256**` | `release.status` → `accepted_by_receiver` (`simulated: False` por ausência do campo) | bloco sem `Validated by` humano, `Scope`, `Conditions`, `Simulated` explícito ou `Timestamp` não promove |
| A2 | republicar o âmbito com `authorized_by: null` | `inventory.check` → `BLOCKING_GAP` `SCOPE_NOT_AUTHORIZED`; `release.readiness` → `ready: True`, sem motivos | o gate de entrega vê as lacunas que o motor do âmbito e do inventário já vê |
| A3 | FC-0001 ganha uma pós-condição (SMS ao fornecedor), republicado com o sha do desenho actual e reautorizado; inventário, spec e estimativa ficam | FC `current`; inventário r1 com `based_on` = `_design/functional-contracts.json` sem versão; `readiness` → `ready: True` | trabalho, spec e estimativa por revalidar não passam |
| A4 | entre `readiness()` e a cópia dos ficheiros, a estimativa é reescrita | pacote `ready_for_receiver_review`, `verify` ok, estimativa no pacote «sem inventário nem esforço»; `readiness` recalculada → `False` | o pacote contém exactamente o que foi validado, ou não se publica |
| A5 | o desenho muda no mesmo caminho e a aprovação é renovada (é o que o `pronto()` já faz); os FC ficam com o sha anterior em `based_on` | aprovação `current`; FC `based_on` ≠ sha do desenho; `readiness` → `ready: True`; `render_gate` só compara o nome da versão | FC assentes num conteúdo de desenho que já não existe não passam |

## 2. Decisões do mantenedor (2026-09-24)

| # | Decisão |
| --- | --- |
| Princípio | A actualidade das dependências verifica-se ao consumir, ao renderizar e ao construir o release, não só ao publicar. Um sha diferente prova uma alteração de conteúdo, mas não a classifica: mover uma dependência exige uma avaliação registada, e trocar o hash não pode, por si só, equivaler a revalidar o conteúdo |
| T42 | A intenção fica: alteração editorial → revalidação registada, sem reabrir decisões; alteração material → dependentes afectados bloqueados até serem actualizados; unidade do pack não consumida → sem impacto |
| Registo | No próprio artefacto (`revalidations` nos FC, no âmbito e no inventário), escrito pelo motor na mesma operação que o pin |
| Alcance | Todas as dependências fixadas: sha do desenho, impressão de cada FC que um WP consome, impressão de cada linha citada |
| Sem pin | Um artefacto que consome algo sem o fixar bloqueia a versão final (`DEPENDENCY_UNPINNED`) |
| Avaliador | O autor do artefacto, por papel; `updated` num FC continua a pedir nova autorização do dono, `still_valid` não reabre decisões |
| `library/` | Edição administrativa por script, com commit (decisão da F1, reconfirmada quando uma permissão foi recusada a meio) |

## 3. Correcção

| Caso | Onde | O que passou a acontecer |
| --- | --- | --- |
| A1 | `release.py` → `acceptance_reading`, `status` | O bloco de aceitação lê-se inteiro: sha do índice que verifica, `Scope` que é um âmbito do release, `Conditions`, `Simulated` explícito (`yes`/`no`; ausente não é «no»), `Validated by` humano (`functional.validator_problem`) e `Timestamp` ISO não anterior ao `built_at`. Falta ou invalidade → `valid: false` com os problemas nomeados, e nada sobe a `accepted_by_receiver`. Vários blocos: sobe o primeiro válido e não simulado |
| A2 | `trace.py` → `scope_gate` | O gate corre `inventory.check` sobre o âmbito e o inventário publicados e junta aos bloqueios a integridade e as lacunas (`SCOPE_NOT_AUTHORIZED`, `EMPTY_SCOPE`, `MISSING_ACCEPTANCE`, `MISSING_DEFINITION_OF_DONE`, `MISSING_REALIZES`, referências mortas); inventário sem âmbito → `NO_SCOPE`. A readiness do release nomeia os códigos (`bloqueios do gate: …`) |
| A3 | `impact.py` → `with_dependency_pins`, `pin_findings`; `inventory.py` → `publish` | O inventário fixa, ao publicar, a impressão de cada FC que um WP realiza ou em cuja aceitação assenta, e o sha de cada ficheiro do desenho cujos nós realiza ou prova (calculados pelo motor). Na leitura, FC com outra impressão → `CONTRACT_CHANGED` no WP, que bloqueia a versão final. Revalidado o WP, o inventário sobe de revisão e a spec e a estimativa ficam `STALE_INVENTORY` até nova renderização (T32, já existente): a cadeia FC → WP → derivados fecha-se |
| A4 | `release.py` → `build`, `_state_digest` | O build exige o bootstrap pronto (`RECOVERY_REQUIRED` com operação pendente, grafo ilegível ou desvio) e tira a impressão de todo o engagement (fora `_release/`, `_drafts/` e a página viva) antes da readiness e depois da cópia: qualquer diferença, ou uma cópia que não bata com o estado inicial, apaga o destino e recusa com `STALE_INPUT`. O pacote é o estado que passou a validação, ou não existe |
| A5 | `impact.py` → `pin_findings`; `functional.py` → `publish`, `render_gate` | O sha do desenho em `based_on` dos FC confere-se na leitura: outro conteúdo no mesmo caminho → `BASIS_CHANGED` em cada FC incluído; o `render_gate` e o `scope_gate` bloqueiam com o código próprio (já não se esconde em `STALE_PREMISE`). O motor preenche o sha do desenho quando o rascunho não o traz |
| RV | `impact.py` → `needed_pins`, `moved_pins`, `revalidation_record`, `history_findings`; `functional.py`/`inventory.py` → `publish` | Um pin que muda entre revisões (mesmo `ref`, outra impressão) exige no rascunho `revalidation`: cada item que depende dele com `still_valid` (conteúdo igual) ou `updated` (conteúdo mudou), a avaliação por escrito e o papel de quem avaliou; sem ela `REVALIDATION_REQUIRED`, incompleta `REVALIDATION_INCOMPLETE`, veredicto incoerente `VERDICT_MISMATCH`, registos anteriores retirados `REVALIDATION_DROPPED`. O motor acrescenta o registo (de/para, data) a `revalidations`. Na leitura: o artefacto tem de ser igual à cópia do histórico (`HISTORY_MISMATCH` — edição por fora do motor) e cada movimento de pin no histórico tem de ter o seu registo (`PIN_UNREVALIDATED`) |

Os candidatos ficam fora da regra: uma revisão nova dos candidatos já obriga a pareceres novos (T26), que são a avaliação independente.

## 4. Testes

`.claude/tests/test_audit_f6f7.py` — 27 casos, 24 nasceram vermelhos (os 3 verdes eram os caminhos que têm de continuar a passar: bloco gerado pelo motor, build estável, derivados re-renderizados). Classes `A1_AceitacaoCompleta`, `A2_LacunasNoGate`, `A3_FCMudadoDerivadosPorRevalidar`, `A4_SnapshotConsistente`, `A5_DesenhoMudadoFCNoShaAntigo`, `RV_RevalidacaoExplicita`.

### Mapa de substituição (alterações legítimas de contrato)

| Teste anterior | Comportamento antigo | Comportamento novo | Garantia preservada |
| --- | --- | --- | --- |
| `test_impact.T42.test_the_byte_revision_stays_exact` | byte do desenho mudado → revisão de bytes exacta, **nenhum achado** | revisão de bytes exacta **e** `BASIS_CHANGED` até à avaliação registada | T42 pelos três casos do mantenedor: `test_an_editorial_design_change_is_revalidated_by_record_without_reopening` (autorizações e `decisions.md` intactos), `test_a_material_design_change_blocks_the_dependents_until_updated`, `test_only_a_consumed_knowledge_unit_reaches_its_review` (inalterado) |
| `test_impact.T41.test_republishing_records_no_semantic_impact_and_keeps_the_fingerprint` | linha mudada no sítio + republicação **sem avaliação** → achado limpo | recusada (`REVALIDATION_REQUIRED`); com `still_valid` → achado limpo | `test_republishing_needs_a_recorded_assessment_and_keeps_the_fingerprint`: a impressão do FC mantém-se, nenhuma autorização se perde |
| `test_impact_gates._refs` | trocava o sha do desenho em cada republicação («o `pronto` retocou o desenho depois dos FC») | sem troca: o `pronto` revalida os FC | a republicação com a sucessora continua a pedir nova autorização |
| `test_impact_gates.T41PontaAPonta.test_republishing_with_the_successor_asks_for_a_new_authorisation` | FC reautorizado → release pronto | reautorizar não basta: o WP fica `CONTRACT_CHANGED`; pronto depois de revalidar o WP e re-renderizar | T41 ponta a ponta, agora com a cadeia FC → WP → spec/estimativa (A3) |
| `test_impact_gates.com_premissa` | FC muda e é reautorizado → pronto | + revalidação do WP e re-renderização | o cenário «pronto com a premissa» continua pronto |
| `test_release.pronto` | mudava o desenho depois dos FC e deixava-os no sha anterior (era o A5) | `revalidar=True` por omissão; `revalidar=False` é o caso A5 | os testes do release continuam a medir o que mediam; `rerender` novo para os derivados |
| `test_trace.montado(prova=True)`, `test_scope_gate` T33 | idem (desenho mudado depois dos FC) | revalidação registada logo a seguir à mudança | sem ela, um teste que espera «bloqueado» passaria pelo motivo errado (`BASIS_CHANGED`) |
| `docs/handoff-v1/F0/consumer-matrix.json` | — | `impact.py` como leitor da autoridade `blueprint` | T02 |

Helpers novos partilhados em `test_inventory.py`: `revalida_fc_desenho`, `revalida_inventario`.

## 5. Sabotagem

13 mutantes, um por garantia, contra `test_audit_f6f7.py` (aplicados e revertidos por script; originais verificados byte a byte no fim):

| Mutante | Resultado |
| --- | --- |
| A1 validador humano não conferido | apanhado |
| A1 ausência de `Simulated` lida como «no» | **sobreviveu** à primeira: equivalente para o gate (o bloco já era inválido pelo campo em falta), mas a leitura reportava `simulated: false` para um bloco que não o declara. O teste passou a afirmá-lo; apanhado |
| A1 âmbito do release não conferido | apanhado |
| A2 gate não lê o inventário | apanhado |
| A3 impressão do FC não comparada | apanhado |
| A4 estado não reconferido no fim do build | apanhado |
| A4 bootstrap não exigido | apanhado |
| A5 sha do desenho não comparado | apanhado |
| RV sem avaliação passa | apanhado |
| RV veredicto não conferido | apanhado |
| RV histórico não lido | apanhado |
| RV registos anteriores podem cair | apanhado |
| RV cobertura dos dependentes não exigida | apanhado |

## 6. Regressão

Full 114/114 ficheiros, 3096 testes, 0 falhas (34 skips, 3 xfail); stdlib 95/95, 2298, 0 falhas. Antes da correcção: 113/113, 3068 e 94/94, 2270 (com o F8.1). Diferença: `test_audit_f6f7.py` (+27) e o T42 do desenho dividido em dois casos (+1).

## 7. Limites declarados

- O avaliador de uma revalidação é o autor, por papel (decisão do mantenedor). O motor confere presença, cobertura dos dependentes e coerência do veredicto com o conteúdo; não julga se a avaliação está certa — isso é dos revisores independentes (o `fc-reviewer` lê a revisão publicada, com o registo) e do dono.
- No documento dos FC, o pin do desenho é do documento: uma mudança no desenho pede a avaliação de todos os contratos, mesmo dos que não usam nada do desenho (conservador).
- A spec e a estimativa continuam a citar só a revisão do inventário. Um FC mudado chega-lhes pelo inventário: WP revalidado → revisão nova → `STALE_INVENTORY`.
- A estabilidade do build cobre os ficheiros do engagement. Os contratos e schemas que o pacote copia do repositório não entram nessa impressão (só mudam por commit).
- A verificação do histórico exige a cópia de cada revisão em `_design/history/`: um histórico apagado não se prova e bloqueia (`HISTORY_MISMATCH`).
- Os candidatos ficam fora da regra (uma revisão nova já pede pareceres novos, T26).
- O validador da aceitação reutiliza a regra das autorizações (`owner (<papel>, … via AskUserQuestion)`); o nome do papel do destinatário revê-se no T46 da F8.

## 8. Recuperação e rollback

Reverter o commit desta correcção devolve o comportamento da F7. Os artefactos publicados com `revalidations` continuam legíveis pelo código anterior (campo aditivo; o schema admite-o), que apenas deixa de impor a regra. Nenhum hook, permissão ou schema mudou.

## 9. Retoma

- Estado: correcção integrada; CI #93 verde; gates da F6 e da F7 **aceites de novo pelo mantenedor** (2026-09-24).
- Próxima acção: o F8.2 (execução R3 da fx-02), numa sessão nova, pela retoma de `../F8/RELATORIO.md`.
