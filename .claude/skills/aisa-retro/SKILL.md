---
name: aisa-retro
description: Close-of-engagement retro — each role that worked the engagement (analyst, architect, and the specialist roles that reviewed) gets its diary entry for this engagement (what it got right, where it was naive, patterns to watch, one advice to its future self). Entries are STAGED in <engagement>/_retro/ for human curation; only after explicit user approval are they appended to .claude/agent-memory/_universal/<role>/diary.md (tracked — the append goes through the repo's normal git flow). The roles read their memory in future engagements (handoff-v1 F5.4, Q4/Q7/Q8).
---

# aisa-retro

## Usage

`/retro` — tipicamente após o render final. Qualquer fase é aceite, com aviso se cedo ("a retro captura mais depois do /render; continuar?").

## Execution

1. **Which roles.** Always `analyst` (the integrated Discovery analysis) and `architect` (the technical author of Options); plus each specialist role that has a received review in this engagement (`python library/kernel/tools/review.py show-reviews --engagement <slug> --json` → the `role` of each review). The six Discovery personas are retired: there is no persona to launch.
   **Who writes.** `analyst` and `architect` are inline roles: the session writes their entries, from the final SU, the `lens-outputs/*.md` / `options.md` and `_design/candidates.json` it produced, `answers.md`, `decisions.md`, `premortem.md` (se existir) and the role's current `diary.md`. Each specialist role is written by one `specialist-reviewer` Task call (in parallel, one message), which receives only paths: its role, its received reviews (`_design/reviews/REV-NNNN.json`) with their dispositions (`_design/reviews/ledger.json`), `decisions.md`, and its current `diary.md` — so it learns from how its findings were disposed, not from the author's reasoning. Prompt (both cases):

   ```
   Escreve a entrada de diário deste engagement para o papel <role>: 2-4 parágrafos —
   (a) o que este papel apanhou que importou;
   (b) onde falhou ou foi ingénuo (sê específico — datas, ids, o que não perguntou ou não viu);
   (c) padrões que espera rever noutros engagements;
   (d) um conselho ao seu futuro eu.
   Sem nomes de pessoas ou de cliente; domínio genérico (ex.: "procurement de mid-cap").
   Formato: ## <slug-anonimizado> — <data>. Máx. 250 palavras.
   ```

2. **Stage** each entry in `<engagement>/_retro/diary-<role>.md`. Nothing touches agent-memory yet.
3. **Present the set to the user** and ask for curation: aprovar tudo / editar entradas / excluir papéis. List each entry's (b) — the failure paragraph — explicitly: an all-wins diary is suspect and should be pushed back on.
4. **ONLY after explicit approval**: append each approved entry to `.claude/agent-memory/_universal/<role>/diary.md` (create it for a role that has none). Remind the user that agent-memory is tracked — the append lands in the repo via the normal git flow (a skill prepares the change; the human owns the commit). Tenant-proprietary detail belongs in `_tenant/` (private repo), never in `_universal/`.
5. Final episode in `story.md` ("a equipa fecha o caderno e guarda o que aprendeu") + `council-log.md` line. Output to the user, after step 2 and before the curation question (business language — `CLAUDE.md` → *Duas línguas*):
   ```user-output
   Lições do fim — <N> papéis escreveram o seu diário (analista, arquitecto<, especialistas que reviram>); as entradas estão em `_retro/`, à espera da tua curadoria.
   Onde cada um diz que falhou: <papel — uma linha> …
   A seguir: aprovar tudo · editar · excluir — a pergunta vem já a seguir, por escolha; só depois disso as entradas entram na memória de cada papel.
   ```

## Hard rules

1. **NUNCA escrever em agent-memory sem aprovação humana nesta sessão** — a regra do repo é "memória editada pelos consultores"; esta skill só reduz o custo da curadoria.
2. **Anonimização**: zero nomes de pessoas/cliente nas entradas `_universal`; domínio genérico apenas.
3. **O diário é falível por design**: registar erros é o objectivo — uma entrada só de vitórias é suspeita e a curadoria deve devolvê-la.
4. Nos engagements seguintes, cada papel cita o seu diário quando um padrão se repete (o analista e o arquitecto leem a sua pasta; um especialista só a recebe se o mandato a listar, com `sha256`) («num engagement anterior de <domínio>, vi…») — nunca detalhe proprietário fora do tenant.
