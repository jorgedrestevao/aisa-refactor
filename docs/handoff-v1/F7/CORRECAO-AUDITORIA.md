# Correcção pós-auditoria dos gates da F6 e da F7 (A1–A5)

Estado: **em curso** — os cinco casos reproduzidos (2026-09-24); correcção por fazer. Os gates da F6 (T33, T39, aceitação do destinatário) e da F7 (T41) ficam **reabertos** até a correcção ter evidência e o mantenedor os aceitar de novo.

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

## 2. Correcção

Por fazer. Cada caso entra primeiro como teste que nasce vermelho.
