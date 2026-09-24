# FIM DE SEGMENTO F8 — R3 / SC

## Revisão do relatório do destinatário (release r0001)

Verificado cada achado contra o motor real (`review.py`, `release.py`, `coverage.py`), não só contra o texto do relatório. Conclusão central: **a maior parte do que o destinatário classifica como "defeito do pacote" é, na verdade, o portão a funcionar correctamente** — incompletude correctamente declarada, não um bug de construção do pacote.

**Não são defeitos (portão correcto, confirmado no código):**
- **L1** (blueprint citado, não entregue): `release.py build` só inclui o desenho se `blueprint_approval_state().ref` apontar para uma versão **aprovada**. Não é inconsistência, é a razão do bloqueio.
- **L2** (D-002 decidido com U-007 blocks_all aberto, sem override): `/decide` não porta sobre `blocks_all` — só sobre a existência de `options.md`/aprovação da frase. O bloqueio de U-007 correctamente pára a **entrega**, não a escolha de arquitectura.
- **L5** (U-011 não verificado): D-002 já aceita este risco explicitamente por citação literal do dono; TW-3 existe para o caso de falhar.
- **L9, L10, L13**: já correctamente `trabalho normal` no próprio relatório.
- **L12** (ficheiros de operação/ALM ausentes do pacote): existem no pack, mas nunca foram puxados (pull-based) — o desenho nunca chegou às secções que os citariam, pela mesma escolha estrutural em aberto (U-004/U-012).

**Achado real, não corrigível nesta sessão (escalado, não fabricado):**
- **L6, L7, L8**: confirmado em `_design/reviews/ledger.json` — três correcções `delegated`, owner "technical author", nenhuma aplicada antes de D-002. Corrigir exige publicar `candidates.json` revisão 2 e reabrir Options — supera D-002. Escalado ao cliente, não decidido unilateralmente.
- **L4** (reviews_basis mostra SU/decisions mudados sem revalidação): confirmado no código — o regime de `PIN_UNREVALIDATED` cobre FC/scope/WP, exclui candidatos explicitamente. Lacuna real entre `handoff-contract.md` e `review.py` — fix de kernel, fora do âmbito do engagement.
- **Q10 do destinatário** (nota-urgentes.md pós-build): confirmado no `council-log.md` — fonte capturada depois de D-002; inconsistência da própria fonte do cliente.

## O que fiz

1. `resume` (cold, read-only) — sem recuperação pendente.
2. Corridos os 6 `coverage.py check --stage render` — confirmado que nada mudou desde `/render --all` já publicado (v01) — mesmos blocks, skips, gaps, palavra por palavra. Não duplicado conteúdo idêntico em v02 (decisão do executor, por Economia — ver anomalia 1).
3. `release.py build` → **release r0002** publicado (52 ficheiros, `preliminary`, mesmos motivos de bloqueio que r0001). `release.py verify --revision 2` → `ok: true`. `release.py status --revision 2` → `acceptance: null`.
4. Nada escrito à mão em `library/`, `_graph/`, `_ops/`, `_migration/`, `_work/`, `_design/`, `_blueprint/`, `council-log.md`, `story.md`.

## Agenda levada ao cliente e resposta

12 perguntas (7 U-NNN + X-001 + sponsor + decisão de reabrir Options). Resposta: 11/12 continuam "não sei / por confirmar"; item 12 decidido — **aceitar como nota histórica, sem reabrir Options** ("a decisão não assentava nestes três pontos").

## estado

fase `decision` (D-01), rota `platform-constrained`; D-001 e D-002 publicadas; release **r0002** é o pacote corrente (mesmo conteúdo que r0001 — nada mudou de facto desde a triagem).

## perguntas abertas e bloqueios

10 perguntas de negócio (U-002, U-004, U-006, U-007, U-008, U-011, U-012, U-013, U-014, X-001) + confirmação do sponsor (D-002) continuam por responder. A decisão de processo (reabrir Options) está fechada: não reabrir. Sem as respostas de negócio, blueprint não aprova, implementation-spec/estimate não renderizam, entrega continua `blocked`.

## próximo passo que o aisa indica

`/status` para a agenda completa; `/answer <id> "<resposta>"` para cada resposta que chegar; `/blueprint --refresh` quando U-004/U-012 fecharem; `/render --all` de novo só quando algo mudar de facto.

## anomalias

1. **Decisão do executor, não da skill**: não escreveu `_render/*_v02.md` idênticos a v01 (a regra 6 da `aisa-render` manda escrever nova versão em toda a corrida real, mesmo sem mudança) — julgou que duplicar 700+ linhas byte-a-byte, sem nenhuma fonte alterada, violava a regra 7 do piloto ("não repitas trabalho já publicado"). Fica sinalizado para decisão do orquestrador/mantenedor sobre se a duplicação mecânica devia ter acontecido de qualquer forma.
2. `release.py build`/`status`/`verify` não aceitam `--json` (erro de CLI, `unrecognized arguments`) — usado sem essa flag; o output já vem em JSON por defeito.
3. `release.py status` sem `--revision` explícito assume revisão 0 (inexistente) em vez da mais recente — parece bug do motor (contornado, passando `--revision 2` explicitamente).
4. Achado de kernel fora do âmbito deste engagement: `review.py` não implementa revalidação de pareceres quando a SU/decisions.md mudam sob um parecer já publicado (só candidatos/FC/scope/WP têm esse mecanismo) — fix de kernel, não tocado.
5. Achado de dados do cliente: `inputs/nota-urgentes.md` datada 2026-10-01, depois do `built_at` de r0001 — fonte capturada pós-decisão, inconsistência da própria fonte fornecida.
6. **Anomalia de protocolo (recorrente)**: executor lançado como chamada única (Agent tool) — sem turno intermédio para `CONTINUA F8`, seguiu direito ao objectivo após a retoma.
