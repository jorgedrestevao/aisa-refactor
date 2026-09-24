# Synthesis checks — f8-r3-fx02

Um registo por validação de um topic pack, escrito pelo hook
`synthesis-validate.py`. **Isto é história, não é o veredicto**: os testes
dependem também da SU, do pacote e do desenho aprovado, por isso o veredicto
é recalculado quando alguém pergunta (`dashboard.py --json` → `synthesis_checks`).
Cada linha traz o `sha` do texto validado e o `deps` das fontes de que dependia.
Ficheiro append-only; a última linha por tópico é a mais recente. Nada bloqueia.

check · 2026-09-24T13:03:29Z · business-story · sha:c80597ead1e1 · deps:17abba48c1fb · SYN-DEAD-ID (id citado sem linha na SU nem bloco em decisions.md: R-01)
check · 2026-09-24T13:03:48Z · as-is · sha:bb9d33488b60 · deps:17abba48c1fb · SYN-DEAD-ID (id citado sem linha na SU nem bloco em decisions.md: R-01)
check · 2026-09-24T13:04:24Z · risks-and-assumptions · sha:e810bf0c3be6 · deps:17abba48c1fb · SYN-DEAD-ID (id citado sem linha na SU nem bloco em decisions.md: R-01, R-02), SYN-VENDOR (termo de solução num tópico neutro: dataverse)
check · 2026-09-24T13:04:52Z · financial-story · sha:a9378c12426f · deps:17abba48c1fb · SYN-DEAD-ID (id citado sem linha na SU nem bloco em decisions.md: R-01), SYN-VENDOR (termo de solução num tópico neutro: dataverse)
check · 2026-09-24T13:31:10Z · architecture-story · sha:f204ee2f561e · deps:17abba48c1fb · ok
check · 2026-09-24T13:42:16Z · as-is · sha:b094e116b5dc · deps:c6198e8556bc · ok
check · 2026-09-24T13:42:20Z · as-is · sha:065de8bbd64d · deps:c6198e8556bc · ok
check · 2026-09-24T13:42:26Z · as-is · sha:2b8888480a3b · deps:c6198e8556bc · ok
check · 2026-09-24T13:42:37Z · risks-and-assumptions · sha:ff9f6bcd0777 · deps:c6198e8556bc · SYN-DEAD-ID (id citado sem linha na SU nem bloco em decisions.md: D-01)
check · 2026-09-24T13:42:47Z · risks-and-assumptions · sha:c0bf36e97a50 · deps:c6198e8556bc · SYN-DEAD-ID (id citado sem linha na SU nem bloco em decisions.md: D-01)
check · 2026-09-24T13:43:36Z · risks-and-assumptions · sha:5a6637009418 · deps:c6198e8556bc · ok
