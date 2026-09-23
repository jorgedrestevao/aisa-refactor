# Prompt para execução faseada

Copiar o texto seguinte para a sessão de implementação, anexando este pacote e dando acesso ao repositório. Este prompt autoriza trabalho local de implementação quando o utilizador o executar; não autoriza push/deploy nem atos externos por si só.

---

Implementa o plano consolidado AISA handoff-v1 por fases, começando por F0. Lê README e todos os contratos deste pacote, as instruções AGENTS.md aplicáveis e os contratos atuais do repositório antes de editar. Baseline de referência: 85baf1018ca2b238c41745f7f13dbb539589867f. Se a branch atual divergir, documenta o delta e adapta o mapa sem apagar trabalho existente.

Objetivo: preservar kernel + PP pack e tornar o resultado um handoff implementável end-to-end, com seis lentes de coverage, autoria funcional explícita, especialistas seletivos, revisão independente, conhecimento persistente e retoma consistente.

Regras:

1. Executa apenas a fase autorizada. Começa por F0; no fecho entrega relatório e proposta da fase seguinte. Não saltes automaticamente para refatorizar tudo.
2. Mantém classic como default até aprovação de rollout. Não migres engagements existentes sem autorização específica.
3. Reutiliza operation/bootstrap/graph/resolve/coverage e os donos existentes de blueprint, implementation-spec e estimate. Não cries motores/autoridades concorrentes.
4. Não alteres os extratores neste programa. Se um bug impedir um teste, documenta-o e propõe correção de âmbito mínimo antes de expandir a tarefa.
5. Faz mudanças pequenas e reversíveis; preserva alterações do utilizador. Sem reset destrutivo, push, deploy ou uso de credenciais fora dos mecanismos configurados.
6. Distingue estados epistémicos, tarefas, resultados, autorizações e freshness. Não confirmes por consenso nem inventes aprovação de negócio.
7. Usa schemas/validações para contratos; prompts não são o único enforcement. Integridade e conflitos são fail-closed.
8. O renderer não decide arquitetura nem inventa comportamento funcional. Gaps voltam ao dono correto.
9. Em cada fase executa os testes mapeados em 06_VALIDACAO e regressões aplicáveis. Regista pass/fail/not-run com comando e evidência. Testes simulados não são pilotos humanos.
10. Mantém um relatório persistente de fase com revisões, alterações, decisões, blockers e próximo passo. Uma sessão nova deve continuar pelo repositório, não por esta conversa.
11. Não adicionas agentes por lente obrigatoriamente. Revisor usa a revisão publicada e contexto independente; limita revisão dialética e escala desacordo material.
12. No handoff, mantém um dono de inventário e um dono de esforço. Backlog e resumo executivo são projeções.
13. Quando precisares de uma escolha que mude o contrato, custo/risco material ou autorização, para e apresenta opções/impacto. Para detalhes internos reversíveis, escolhe a alternativa mais simples compatível e documenta.
14. Só declara a fase concluída quando o gate correspondente tiver evidência. Bloqueio de ambiente ou teste não executado é reportado, não contornado.

Entrega no final de cada fase: resumo do que mudou, ficheiros relevantes, testes/resultados, riscos/limitações, procedimento de rollback, estado de compatibilidade e próximo passo. Não digas que o objetivo end-to-end está provado antes dos pilotos e provas reais aplicáveis.

---
