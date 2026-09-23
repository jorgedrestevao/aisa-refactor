# Fixture — casos de admissão (handoff-v1, `states.md` → *Admission of a question*) e da forma de `quem responde` (F1.1)

Sintético. Nenhuma linha vem de um engagement real: `projects/` é um ponto de montagem
gitignored para o repositório privado, e nenhum engagement pode ser comitado como fixture
(a mesma regra que `test_status_model.py` declara no seu cabeçalho).

Cada linha existe para exercitar **um** caso, e o seu id diz qual. As colunas são as de
`library/kernel/states.md` → *Schema of Shared Understanding rows*.

## Unknown

| id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-901 | data | Qual é o volume mensal de pedidos? | fact_gap | viabilidade: muda a faixa de esforço, não o padrão | dimensionamento | role: dono do processo | série do histórico extraída | — | Med | email | dimensionante: entre 50 e 500 por mês o padrão é o mesmo; muda a faixa de esforço | A-901 | R-01 |
| U-902 | governance | A identidade externa que chega ao armazenamento é partilhada ou por utilizador? | design_choice | solução, segurança: muda o plano de imposição de permissões e o padrão arquitetural | acesso ao armazenamento (proposed_to_be) | fonte: configuração da ligação | configuração verificada, ou escolha registada pelo dono | blocks_scope | Critical | spike | decisivo: partilhada, ou por utilizador. Elimina o ramo «segurança por linha imposta no armazenamento» | fixture sintética | R-01 |
| U-903 | business | Serve M-2. Quem assina a acta da reunião de arranque? | fact_gap | serve M-2 | arranque | role: dono do processo | — | — | Critical | reuniao | serve M-2 | M-2 | R-01 |
| U-904 | operations | Onde está a pasta diária do ficheiro antigo? | fact_gap | nenhum contrato no alvo | ficheiro antigo | | — | — | Low | email | cosmético | — | R-01 |
| U-905 | data | O armazenamento é o A ou o B? | design_choice | solução: muda o modelo de dados e os componentes | armazenamento | role: equipa de plataforma | escolha registada | blocks_all | Critical | spike | decisivo: A ou B. Elimina o ramo «um só armazenamento» | fixture sintética | F-01 |
| U-906 | technology | Serve M-1. O padrão é simples ou composto? | design_choice | serve M-1 | padrão | role: arquitectura | — | — | Critical | reuniao | serve M-1 | M-1 | O-01 |
| U-907 | chair | Serve M-3. Quem valida a acta do enquadramento? | fact_gap | serve M-3 | enquadramento | role: dono do processo | — | — | Critical | reuniao | serve M-3 | M-3 | F-01 |

## Assumed

| id | lens | claim | base da assumption | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|
| A-901 | data | O volume mensal está entre 50 e 500 pedidos | duas observações do dono, não uma série. Condição de revisão: uma extracção do histórico contradiz a ordem de grandeza | 2026-09-10 | organizacional | R-01 |
