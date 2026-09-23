"""pre-authority-guard.py — PreToolUse guard for Write/Edit on engagement authorities.

W2 of P7.5. Refuses to let the agent write to an engagement's authoritative files while
that engagement's bootstrap is NOT ready — a pending operation, an unreadable graph, an
incoherent pair. The refusal names the limitation and the recovery.

WHY A HOOK AND NOT A STEP IN EACH SKILL

The obvious shape would be a "run the bootstrap first" step in each of the fourteen
`SKILL.md` files. It fails on both counts W2 asks for:

  - `ACCEPTANCE.md` §1: «Um teste de estrutura de prompts é insuficiente para provar
    comportamento de runtime.» A test could only assert the sentence is in the file.
  - W2 itself asks to prove «que nenhum entrypoint contorna o bootstrap por uma chamada
    indirecta». Prose does not prevent a bypass; it asks for one not to happen.

So the enforcement is programmatic, the same way `library/` read-only already is.

WHAT IT COVERS, AND WHAT IT DOES NOT

Covers the AGENT's writes through `Write`/`Edit` — which is exactly the path that bypasses
the kernel today, since none of the 24 skills invokes `bootstrap.py`.

Does NOT cover writes by subprocess: a documented limitation of the hook surface
(`on-su-change.py` says the same about `PostToolUse`). The motors that write by subprocess
— `resolve`, `migrate` — already go through the coordinator, which refuses to mutate over a
pending operation. The two layers do not replace each other: this guard catches the agent,
the coordinator catches the motors.

FAILS CLOSED, LIKE ITS NEIGHBOUR

If the bootstrap cannot be evaluated at all, the write is refused rather than waved
through: not being able to verify is not the same as having verified.
`AISA_GUARD_MODE=log` is the explicit administrative override, the same switch
`pre-write-guard.py` honours.

Standalone use (no stdin):
    python .claude/hooks/pre-authority-guard.py --engagement <slug>
"""

from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path

# <repo>/.claude/hooks/pre-authority-guard.py -> <repo>
REPO_ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = REPO_ROOT / "library" / "kernel" / "tools" / "bootstrap.py"

# As autoridades do engagement, à raiz. Escrever numa destas muda o que o aisa SABE — e por
# isso exige que o estado tenha sido reconstruído primeiro. `_capture/`, `_render/`,
# `_simulation/` e companhia são derivados: ficam de fora de propósito.
AUTORIDADES = {"shared-understanding.md", "decisions.md", "answers.md", "_state.json",
               # O padrão das skills é `_state.json.tmp` → `mv`. Sem este nome, a escrita
               # passava pelo ficheiro temporário sem guarda (handoff-v1 F1.4).
               "_state.json.tmp"}
ESTADO = ("_state.json", "_state.json.tmp")

# Autoridade que não vive à raiz, e que quatro nomes de ficheiro não apanhavam.
#
# O grafo É autoridade operacional desde que o bootstrap constrói o contexto a partir dele
# e o `drift` o compara com a SU: uma edição à mão aqui muda o que o sistema julga saber,
# tal como uma edição na SU. O `_ops/` é a barreira — marcador de pendência e recibos; uma
# edição à mão neste sítio apaga a prova de que uma operação aconteceu, ou inventa uma que
# não aconteceu.
#
# Nenhum dos dois é escrito por um agente no seu trabalho normal: quem lá escreve é
# `operation.py`, em Python, que não passa por este hook. Uma escrita pela ferramenta Write
# ou Edit nestes caminhos é, por construção, uma edição à mão de estado coordenado.
DIRECTORIOS_AUTORIDADE = ("_graph/", "_ops/", "_migration/", "_work/", "_design/")

# `_migration/` (manifesto e backups do `migrate.py`), `_work/` (checkpoint) e `_design/`
# (contratos funcionais) juntaram-se em handoff-v1 F1.4: todos têm um escritor em Python
# pelo coordenador. E a recusa passou a ser SEMPRE, não só com o bootstrap por pronto
# (F0 D05): uma escrita por ferramenta nestes caminhos é edição à mão de estado
# coordenado, esteja o engagement reconstruído ou não.


def engagements_root() -> Path:
    raw = os.environ.get("AISA_ENGAGEMENTS_ROOT")
    if raw:
        p = Path(raw)
        return p if p.is_absolute() else (REPO_ROOT / p)
    return REPO_ROOT / "projects"


def block(reason: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(payload), file=sys.stderr)
    sys.exit(2)


def engagement_of(file_path: str) -> tuple[Path | None, str]:
    """`(engagement, nome do ficheiro)` quando o alvo é uma autoridade; `(None, "")` se não.

    A comparação é sobre o caminho canónico: `./projects/x/../x/decisions.md` é a mesma
    autoridade que `projects/x/decisions.md`, e um guarda que só olhasse à string deixava
    passar a primeira."""
    try:
        alvo = Path(file_path)
    except (OSError, ValueError):
        return None, ""
    partes_alvo = alvo.parts
    dentro_de_dir = any(seg.rstrip("/") in partes_alvo for seg in DIRECTORIOS_AUTORIDADE)
    if alvo.name not in AUTORIDADES and not dentro_de_dir:
        return None, ""

    base = engagements_root()
    try:
        base_real = base.resolve()
    except OSError:
        base_real = base
    for cand in {alvo, }:
        try:
            cand_real = cand.resolve()
        except OSError:
            # `resolve()` falhou: o caminho canonico tem de sair de outra forma, ou um
            # `projects/eng/x/../decisions.md` escapava por nao bater com a base.
            cand_real = Path(os.path.abspath(os.path.normpath(str(cand))))
        try:
            rel = cand_real.relative_to(base_real)
        except ValueError:
            continue
        if len(rel.parts) < 2:
            continue                      # um ficheiro solto na raiz não é engagement
        dentro = "/".join(rel.parts[1:])
        # Um ficheiro com o nome de uma autoridade mas enterrado num derivado não é a
        # autoridade: `_render/decisions.md` não é `decisions.md`.
        if len(rel.parts) == 2 and alvo.name in AUTORIDADES:
            return base_real / rel.parts[0], alvo.name
        if any(dentro.startswith(seg) for seg in DIRECTORIOS_AUTORIDADE):
            return base_real / rel.parts[0], dentro
        continue
    return None, ""


_CACHE: dict = {}


def _boot() -> dict:
    if "B" not in _CACHE:
        _CACHE["B"] = runpy.run_path(str(BOOTSTRAP))
    return _CACHE["B"]


def avalia(eng: Path) -> tuple[bool, str]:
    """`(pronto, razão)`. Um bootstrap que não se consegue avaliar NÃO conta como pronto."""
    if not (eng / "_state.json").is_file():
        # Ainda não é um engagement: é `/start` a criá-lo. Não há estado a reconstruir.
        return True, ""
    try:
        B = _boot()
        boot = B["bootstrap"](eng)
    except Exception as exc:                                  # noqa: BLE001 — fail closed
        return False, "o bootstrap de `{}` não pôde ser avaliado ({}: {}) — não é o mesmo " \
                      "que ter sido avaliado".format(eng.name, type(exc).__name__, exc)
    if boot.get("ready"):
        return True, ""

    limitacoes = boot.get("limitations") or []
    partes = []
    for lim in limitacoes:
        detalhe = lim.get("detail") or lim.get("code", "")
        recup = lim.get("recovery") or ""
        partes.append("{}{}".format(detalhe, " → " + recup if recup else ""))
    return False, "o engagement `{}` não está reconstruído: {}".format(
        eng.name, " · ".join(partes) or "bootstrap não pronto, sem limitação nomeada")


def estado_novo(eng: Path, nome: str, tool: dict) -> tuple[bool, str]:
    """`(passa, razão)` para uma escrita em `_state.json` (ou no seu `.tmp`).

    Duas regras, só quando o conteúdo novo é conhecido e o `_state.json` actual se lê:
    nenhuma chave existente desaparece em silêncio, e o bloco `workflow` não muda por
    ferramenta — muda-o o `workflow.py` pelo coordenador (DESENHO-CONTRATOS.md I-07)."""
    actual_p = eng / "_state.json"
    try:
        actual = json.loads(actual_p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True, ""                    # nada a comparar: o bootstrap decide
    if not isinstance(actual, dict):
        return True, ""
    ti = tool.get("tool_input") or {}
    if tool.get("tool_name") == "Write":
        if "content" not in ti:
            return True, ""
        texto = ti.get("content") or ""
    else:
        velho, novo = ti.get("old_string"), ti.get("new_string")
        if velho is None or novo is None:
            return True, ""
        base = actual_p.read_text(encoding="utf-8") if nome == "_state.json" else ""
        if not base or velho not in base:
            return True, ""
        texto = base.replace(velho, novo) if ti.get("replace_all") else base.replace(velho, novo, 1)
    try:
        novo_obj = json.loads(texto)
    except ValueError as exc:
        return False, "o `{}` novo não é JSON ({})".format(nome, exc)
    if not isinstance(novo_obj, dict):
        return False, "o `{}` novo não é um objecto JSON".format(nome)
    perdidas = sorted(set(actual) - set(novo_obj))
    if perdidas:
        return False, "o `{}` novo deixa cair {} — campos existentes não se descartam " \
                      "em silêncio".format(nome, ", ".join("`{}`".format(k) for k in perdidas))
    if "workflow" in actual and novo_obj.get("workflow") != actual.get("workflow"):
        return False, "o bloco `workflow` (perfil e rota) não muda por ferramenta: muda-o " \
                      "o `workflow.py` pelo coordenador"
    return True, ""


def _perfil_handoff(eng: Path) -> bool:
    """O engagement é handoff-v1? (o resolver único vive em `workflow.py`)."""
    W = runpy.run_path(str(REPO_ROOT / "library" / "kernel" / "tools" / "workflow.py"))
    return W["profile_of"](eng)["kind"] == W["HANDOFF"]


def texto_novo(eng: Path, nome: str, tool: dict) -> str | None:
    """O conteúdo que a escrita deixaria no ficheiro, ou None quando não se sabe."""
    ti = tool.get("tool_input") or {}
    if tool.get("tool_name") == "Write":
        return ti.get("content") if "content" in ti else None
    velho, novo = ti.get("old_string"), ti.get("new_string")
    if velho is None or novo is None:
        return None
    try:
        base = (eng / nome).read_text(encoding="utf-8")
    except OSError:
        return None
    if velho not in base:
        return None
    return base.replace(velho, novo) if ti.get("replace_all") else base.replace(velho, novo, 1)


def confirmados_sem_prova(eng: Path, tool: dict) -> tuple[bool, str]:
    """`(passa, razão)` para uma escrita na SU de um engagement handoff-v1 (T08, F0 D19).

    Uma linha `Confirmed` nova, ou uma já existente que a escrita muda — incluindo uma
    promoção no lugar, com o mesmo id —, tem de trazer um localizador das classes de
    `states.md` → *Confirmed threshold*, com o alvo presente. Quantas personas concordam
    não conta. O verificador é o do motor (`audit_confirmed_locators`), o mesmo que o
    `/status` lê: presença e existência do alvo, nunca a verdade da afirmação."""
    novo = texto_novo(eng, "shared-understanding.md", tool)
    if novo is None:
        return True, ""
    D = _boot()["_D"]
    try:
        antes = (eng / "shared-understanding.md").read_text(encoding="utf-8")
    except OSError:
        antes = ""
    velhas = {r["id"]: (r["state"], r["raw"]) for r in D["parse_su"](antes)[1]}
    linhas = D["parse_su"](novo)[1]
    tocadas = {r["id"] for r in linhas
               if r["state"] == "Confirmed" and not r["resolved"]
               and velhas.get(r["id"]) != (r["state"], r["raw"])}
    if not tocadas:
        return True, ""
    audit = D["audit_confirmed_locators"](linhas, eng, only_ids=tocadas)
    falhas = ["{} ({})".format(x["id"], x["motivo"])
              for x in audit["sem_locator"] + audit["alvo_ausente"]]
    if not falhas:
        return True, ""
    return False, "linha(s) `Confirmed` sem prova localizável: {} — concordância entre " \
                  "personas não é evidência (`library/kernel/states.md` → *Confirmed " \
                  "threshold*); escrever como `Assumed` com a base, ou `Unknown`".format(
                      "; ".join(falhas))


def main() -> int:
    if "--engagement" in sys.argv:
        slug = sys.argv[sys.argv.index("--engagement") + 1]
        pronto, razao = avalia(engagements_root() / slug)
        print("pronto" if pronto else "BLOQUEIA: " + razao)
        return 0 if pronto else 1

    raw = sys.stdin.read()
    for i, ch in enumerate(raw):
        if ch in "{[":
            raw = raw[i:]
            break
    try:
        tool = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    if tool.get("tool_name") not in {"Write", "Edit"}:
        return 0

    file_path = (tool.get("tool_input") or {}).get("file_path") or ""
    if not file_path:
        return 0

    eng, nome = engagement_of(file_path)
    if eng is None:
        return 0

    if any(nome.startswith(seg) for seg in DIRECTORIOS_AUTORIDADE):
        razao = "`{}` é estado coordenado do engagement `{}`: escreve-o o coordenador " \
                "(`operation.py`), nunca uma ferramenta".format(nome, eng.name)
        if os.environ.get("AISA_GUARD_MODE") == "log":
            print("[pre-authority-guard] (log) {} — escrita permitida por override".format(
                razao), file=sys.stderr)
            return 0
        block("{}\n\n`AISA_GUARD_MODE=log` é o override administrativo explícito.".format(razao))
        return 2

    pronto, razao = avalia(eng)
    if pronto and nome == "shared-understanding.md" and \
            (eng / "_state.json").is_file() and _perfil_handoff(eng):
        passa, razao2 = confirmados_sem_prova(eng, tool)
        if not passa:
            if os.environ.get("AISA_GUARD_MODE") == "log":
                print("[pre-authority-guard] (log) {} — escrita permitida por override".format(
                    razao2), file=sys.stderr)
                return 0
            block("{}\n\n`AISA_GUARD_MODE=log` é o override administrativo explícito.".format(
                razao2))
            return 2
    if pronto and nome in ESTADO:
        # Pronto não chega para o estado: o conteúdo novo também não pode perder chaves nem
        # mudar o perfil. Só depois do bootstrap, para que um legado diga que é legado.
        pronto, razao = estado_novo(eng, nome, tool)
        if not pronto:
            if os.environ.get("AISA_GUARD_MODE") == "log":
                print("[pre-authority-guard] (log) {} — escrita permitida por override".format(
                    razao), file=sys.stderr)
                return 0
            block("{}\n\n`AISA_GUARD_MODE=log` é o override administrativo explícito.".format(
                razao))
            return 2
    if pronto:
        return 0

    if os.environ.get("AISA_GUARD_MODE") == "log":
        print("[pre-authority-guard] (log) {} — escrita em `{}` permitida por override".format(
            razao, nome), file=sys.stderr)
        return 0

    block("{}\n\nEscrever em `{}` sobre estado por reconstruir decide sobre estado misto. "
          "Recuperar primeiro; `AISA_GUARD_MODE=log` é o override administrativo "
          "explícito.".format(razao, nome))
    return 2


if __name__ == "__main__":
    sys.exit(main())
