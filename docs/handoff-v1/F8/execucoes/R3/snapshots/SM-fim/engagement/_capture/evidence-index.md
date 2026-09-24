# Evidence index

Shared evidence surface for this engagement — **parse once, reason many**
(`library/kernel/orchestration.md` → *Evidence contract*).

Normalized evidence below is the normal reading surface. Raw sources stay in `inputs/`,
are always openable, and are **authoritative on conflict**. Inspect the raw source when
material to confidence — not to satisfy a quota.

| source | format | normalized evidence | status | cite as |
|---|---|---|---|---|
| `entrevista-processo.md` | `.md` | `entrevista-processo.md.text.md` | `ok` | `<file> · §<heading> ¶NN` |
| `matriz-papeis.md` | `.md` | `matriz-papeis.md.text.md` | `ok` | `<file> · §<heading> ¶NN` |
| `nota-dados.md` | `.md` | `nota-dados.md.text.md` | `ok` | `<file> · §<heading> ¶NN` |
| `nota-urgentes.md` | `.md` | `nota-urgentes.md.text.md` | `ok` | `<file> · §<heading> ¶NN` |
| `pedido.md` | `.md` | `pedido.md.text.md` | `ok` | `<file> · §<heading> ¶NN` |

**Status vocabulary** — `ok` extracted · `empty` extraction ran, the source has no content
(absence is evidence) · `failed` deterministic extraction could not run, read the raw source ·
`skipped` extraction library unavailable, read the raw source · `not captured` format outside
the capture tiers (not a failure) — read the raw source with the format table in
`library/kernel/orchestration.md` → *Evidence contract*.

Regenerate with `python library/kernel/tools/text_extract.py --index <engagement>`.
