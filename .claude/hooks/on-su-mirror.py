#!/usr/bin/env python3
"""PostToolUse(Write|Edit): uma edicao directa da SU e detectada e reportada — nunca
publicada por aqui (handoff-v1 F2, DESENHO §3, T17).

Historia. Este hook nasceu escritor: as lentes editavam a SU com a ferramenta Edit, nada
espelhava, e a segunda escrita era recusada por `AUTHORITY_UNMIRRORED`. Chamar
`resolve.sync_mirror` a seguir a cada Edit tirava o bloqueio — e fazia de um hook uma
segunda via de publicacao, que espelhava em silencio ate uma promocao de estado feita no
sitio (F0 D19). O plano (04 §Escritas e hooks) fecha isso: «hooks de escrita sao guardas,
deteccao e diagnostico, nao uma segunda implementacao da transaccao».

Agora. As skills escrevem as autoridades por rascunho e `resolve.py publish` (SU e espelho
numa operacao so). Um Edit directo continua possivel: a edicao fica nos ficheiros, o
bootstrap deixa de estar pronto, o guarda recusa a escrita seguinte e o coordenador recusa
publicar sobre o estado divergente. Este hook diz o que divergiu e qual e a reconciliacao
explicita — `resolve.py reconcile` (ver) e `--apply` (publicar, com recibo).

Nunca bloqueia e nunca escreve. Um PostToolUse nao desfaz a escrita que ja aconteceu.
"""
import json
import os
import runpy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESOLVE = REPO_ROOT / "library" / "kernel" / "tools" / "resolve.py"
SU = "shared-understanding.md"


def engagements_root() -> Path:
    raw = os.environ.get("AISA_ENGAGEMENTS_ROOT")
    if raw:
        p = Path(raw)
        return p if p.is_absolute() else (REPO_ROOT / p)
    return REPO_ROOT / "projects"


def engagement_of(file_path: str):
    """O engagement cuja SU foi escrita — ou None. Caminho canonico, como o guarda."""
    try:
        alvo = Path(file_path).resolve()
        raiz = engagements_root().resolve()
    except OSError:
        return None
    if alvo.name != SU:
        return None
    try:
        rel = alvo.relative_to(raiz)
    except ValueError:
        return None
    if len(rel.parts) != 2:          # projects/<slug>/shared-understanding.md, e so isso
        return None
    return raiz / rel.parts[0]


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raw = sys.stdin.read()
    try:
        tool = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    if tool.get("tool_name") not in {"Write", "Edit"}:
        return 0
    eng = engagement_of((tool.get("tool_input") or {}).get("file_path") or "")
    if eng is None or not (eng / "_state.json").is_file():
        return 0
    try:
        R = runpy.run_path(str(RESOLVE))
        r = R["reconcile"](eng, apply=False)            # so le: plano, nunca publica
    except Exception as exc:                                   # noqa: BLE001
        print("[on-su-mirror] nao foi possivel avaliar `{}` ({}: {}). O bootstrap decide; "
              "ver: python library/kernel/tools/bootstrap.py --engagement {}".format(
                  eng.name, type(exc).__name__, exc, eng.name), file=sys.stderr)
        return 0
    if r.get("status") == "planned":
        s = r.get("summary") or {}
        print("[on-su-mirror] edicao directa da SU de `{}` preservada, e o grafo nao a "
              "acompanha — a publicacao seguinte fica bloqueada ate reconciliar.\n"
              "  estado mudado: {}\n  linhas novas: {}\n"
              "  ver:      python library/kernel/tools/resolve.py reconcile --engagement {}\n"
              "  publicar: python library/kernel/tools/resolve.py reconcile --engagement {} "
              "--apply\n"
              "  (caminho normal das skills: resolve.py draft ... && resolve.py publish)"
              .format(eng.name, s.get("estado mudado no grafo", "?"),
                      s.get("linhas novas", "?"), eng.name, eng.name), file=sys.stderr)
    elif r.get("status") == "refused":
        print("[on-su-mirror] `{}`: {} — nao se resolve por reconciliacao. "
              "Recuperar: {}".format(eng.name, ", ".join(r.get("blocking", [])),
                                     r.get("recovery", "")), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
