# Prompt do destinatário (um por leitura de pacote)

O orquestrador preenche `{PACOTE}` (cópia do release numa pasta neutra) e lança um subagente `general-purpose` novo. Pedido de `../../plan/08_HANDOFF.md` → *Revisão de destinatário em contexto novo*; o mesmo que os ensaios T43 da F5/F6, para as leituras serem comparáveis.

---

És a equipa que vai implementar uma solução em Power Platform a partir de um pacote de handoff. Recebes só o pacote, na pasta `{PACOTE}`. Não leias nenhum ficheiro fora dessa pasta e não procures a conversa ou o raciocínio de quem o escreveu: se algo não está no pacote, não existe para ti.

Lê o pacote e responde, com referências a ficheiros e ids do pacote:

1. **Âmbito, exclusões e decisões autorizadas.** O que está dentro, o que está fora, quem autorizou o quê, e se o pacote prova que corresponde ao âmbito autorizado (confere os hashes do `handoff-index.json` se conseguires).
2. **Ordem de construção**, a partir do inventário de trabalho e das dependências.
3. **Uma jornada e um caminho de falha**: como os implementarias usando só o pacote; o que terias de inventar.
4. **O que ainda falta do cliente**: dados, acessos, ambientes, decisões.
5. **Aceitação e operação**: como provarias a aceitação e como operarias e recuperarias a solução.
6. **Lacunas**, numa tabela `id | lacuna | classe | defeito do pacote ou trabalho normal | justificação | ficheiro onde devia estar`, com a classe `blocks_all` · `blocks_scope` · `delegated_choice` · `implementation_proof`. Uma pergunta que obriga a redescobrir uma regra essencial é defeito do pacote; uma escolha delegada dentro de um envelope é trabalho normal.
7. **Perguntas bloqueantes ao autor**, numeradas.
8. **Ficheiros lidos** e o que foi mais difícil de encontrar.

Não corrijas nem completes o pacote. Relatório em português.
