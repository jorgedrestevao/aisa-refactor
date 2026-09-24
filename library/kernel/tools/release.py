"""release.py — o pacote de handoff e o seu índice (handoff-v1 F6, DESENHO Q5/Q6).

    build     monta `<engagement>/_release/r<NNNN>/` a partir das revisões correntes: as
              autoridades, `_design/`, o desenho aprovado, as fontes, a spec e a estimativa
              renderizadas mais recentes, os contratos que tornam o pacote verificável e as
              leituras dos motores (`functional-state.json`, `trace.json`, `scope-gate.json`),
              com o índice `handoff-index.json` (`handoff-index/1`). Cada revisão é imutável:
              nunca se escreve por cima de uma que exista. Um segredo em qualquer ficheiro
              recusa o build (T40)
    verify    confere cada `sha256` do índice, ficheiros a mais ou a menos, e procura segredos:
              um pacote alterado depois do release não é aceite como intacto (T39)
    status    o nível de entrega do release agora, com a aceitação do destinatário (Q6)
    acceptance-block  o texto do bloco `D-NNN — Aceitação do destinatário (release rNNNN)`,
              com o `sha256` do índice; uma simulação é rotulada

O nível nunca é declarado: é calculado.

- `preliminary` enquanto houver achado de rastreio, bloqueio de âmbito, spec ou estimativa em
  falta ou em desacordo com o inventário.
- `ready_for_receiver_review` quando tudo isso passa.
- `accepted_by_receiver` só com o bloco de aceitação do release, não simulado.
- `implemented_verified` nunca sai do build: exige execução e evidência.

Desenho: `docs/handoff-v1/F6/DESENHO.md` §5.
"""
from __future__ import annotations

import hashlib
import json
import re
import runpy
import shutil
import subprocess
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CACHE: dict = {}
REPO = _HERE.parent.parent.parent
RELEASE_DIR = "_release"
INDEX = "handoff-index.json"
REL_RE = re.compile(r"^r(\d{4})$")
ACC_TITLE = "Aceitação do destinatário"
ACC_HEAD_RE = re.compile(r"^##\s+(D-\d+)\s+—\s+" + ACC_TITLE + r"\s+\(release r(\d{4})\)",
                         re.M)
AUTHORITIES = ["shared-understanding.md", "decisions.md", "answers.md", "_state.json",
               "context.json", "enquadramento.md", "frame.md", "options.md"]
DESIGN = ["_design/candidates.json", "_design/functional-contracts.json",
          "_design/scope.json", "_design/work-packages.json"]
CONTRACTS = ["library/kernel/handoff-contract.md", "library/kernel/states.md",
             "library/kernel/specialists.md"]


def _mod(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = runpy.run_path(str(_HERE / (name + ".py")))
    return _CACHE[name]


class ReleaseError(Exception):
    def __init__(self, message: str, code: str, detail: dict | None = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or {}


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for bloco in iter(lambda: fh.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def _latest_render(eng: Path, deliverable: str) -> str:
    vs = []
    for p in (eng / "_render").glob("*_{}_v*.md".format(deliverable)):
        m = re.search(r"_v(\d{2,3})\.md$", p.name)
        if m:
            vs.append((int(m.group(1)), p))
    return "_render/" + max(vs)[1].name if vs else ""


def _text_secrets(p: Path) -> list:
    try:
        texto = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return _mod("operation")["find_secrets"](texto)


def _next_revision(eng: Path) -> int:
    ns = [int(REL_RE.match(p.name).group(1)) for p in (eng / RELEASE_DIR).glob("r*")
          if REL_RE.match(p.name)]
    return max(ns or [0]) + 1


def _code_version() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconhecida"


def _pack_version(eng: Path) -> str:
    try:
        pack = json.loads((eng / "_state.json").read_text(encoding="utf-8")).get("pack", "")
        txt = (REPO / "library/packs" / pack / "pack.yaml").read_text(encoding="utf-8")
    except (OSError, ValueError):
        return "desconhecida"
    m = re.search(r"(?m)^pack_version:\s*(\S+)", txt)
    return "{} {}".format(pack, m.group(1)) if m else pack


def readiness(eng) -> dict:
    """O que o nível de entrega exige, lido dos motores (nunca declarado)."""
    eng = Path(eng)
    T, F = _mod("trace"), _mod("functional")
    trace = T["trace"](eng)
    gate = T["scope_gate"](eng)
    spec, est = _latest_render(eng, "implementation-spec"), _latest_render(eng, "estimate")
    motivos = []
    if not trace["ok"]:
        motivos.append("{} achado(s) de rastreabilidade".format(len(trace["findings"])))
    if gate["delivery"] == "blocked":
        motivos.append("gate de âmbito bloqueado ({} bloqueio(s), {} incoerência(s))".format(
            len(gate["blockers"]), len(gate["incoherent"])))
    checks = {}
    if not spec:
        motivos.append("implementation-spec não renderizada")
    else:
        c = T["derived_check"](eng, (eng / spec).read_text(encoding="utf-8"), "spec")
        c["findings"] += T["spec_effort_check"]((eng / spec).read_text(encoding="utf-8"))
        checks["implementation-spec"] = c["findings"]
        if c["findings"]:
            motivos.append("implementation-spec em desacordo com o inventário")
    if not est:
        motivos.append("estimativa não renderizada")
    else:
        c = T["derived_check"](eng, (eng / est).read_text(encoding="utf-8"), "estimate")
        checks["estimate"] = c["findings"]
        if c["findings"]:
            motivos.append("estimativa em desacordo com o inventário")
    ap = F["blueprint_approval_state"](eng)
    if ap["state"] != "current":
        motivos.append("aprovação do desenho {}".format(ap["state"]))
    return {"ready": not motivos, "reasons": motivos, "delivery": gate["delivery"],
            "trace_findings": trace["findings"], "gate": gate, "render_checks": checks,
            "blueprint_approval": ap, "spec": spec, "estimate": est,
            "proofs": trace["proofs"], "viability_blockers": trace["viability_blockers"]}


def build(eng, out: str | None = None) -> dict:
    eng = Path(eng)
    W, F, RV = _mod("workflow"), _mod("functional"), _mod("review")
    if W["profile_of"](eng)["kind"] != W["HANDOFF"]:
        raise ReleaseError("release só num engagement handoff-v1", W["UNSUPPORTED_PROFILE"])
    rev = _next_revision(eng)
    dest = Path(out) if out else eng / RELEASE_DIR / "r{:04d}".format(rev)
    if dest.exists():
        raise ReleaseError("{} já existe — um release nunca se reescreve".format(dest),
                           W["INTEGRITY_FAILURE"], {"path": str(dest)})
    rd = readiness(eng)
    ap = rd["blueprint_approval"]
    rels = [r for r in AUTHORITIES + DESIGN if (eng / r).is_file()]
    rels += sorted(p.relative_to(eng).as_posix() for p in (eng / "_design/reviews").glob("*.json"))
    if ap.get("ref") and (eng / ap["ref"]).is_file():
        rels.append(ap["ref"])
    rels += [r for r in (rd["spec"], rd["estimate"]) if r]
    rels += sorted(p.relative_to(eng).as_posix() for p in (eng / "inputs").glob("*")
                   if p.is_file())
    repo_rels = list(CONTRACTS) + sorted(
        "library/kernel/schemas/" + p.name for p in (REPO / "library/kernel/schemas").glob(
            "handoff-*.schema.json"))
    for m in sorted((eng / "_design/reviews").glob("REV-*.mandate.json")):
        for k in json.loads(m.read_text(encoding="utf-8")).get("knowledge_refs") or []:
            if k["ref"] not in repo_rels:
                repo_rels.append(k["ref"])
    segredos = {r: _text_secrets(eng / r) for r in rels if _text_secrets(eng / r)}
    segredos.update({r: _text_secrets(REPO / r) for r in repo_rels if _text_secrets(REPO / r)})
    if segredos:
        raise ReleaseError("segredo em {} — o pacote leva a referência, nunca o valor".format(
            ", ".join(sorted(segredos))), W["INTEGRITY_FAILURE"],
            {"code": "SECRET_IN_CONTENT", "patterns": segredos})
    dest.mkdir(parents=True)
    for r in rels:
        (dest / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(eng / r, dest / r)
    for r in repo_rels:
        (dest / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / r, dest / r)
    leituras = {"functional-state.json": F["show"](eng),
                "trace.json": {k: rd[k] for k in ("trace_findings", "proofs",
                                                  "viability_blockers")},
                "scope-gate.json": rd["gate"]}
    for nome, obj in leituras.items():
        (dest / nome).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n",
                                 encoding="utf-8", newline="\n")
    todos = sorted(rels + repo_rels + list(leituras))
    scope = json.loads((eng / "_design/scope.json").read_text(encoding="utf-8")) \
        if (eng / "_design/scope.json").is_file() else {}
    level = "ready_for_receiver_review" if rd["ready"] else "preliminary"
    based = []
    for r in DESIGN + ([ap["ref"]] if ap.get("ref") else []):
        if (eng / r).is_file():
            d = {"ref": r, "sha256": _sha(eng / r)}
            if r.endswith(".json"):
                d["revision"] = json.loads((eng / r).read_text(encoding="utf-8")).get(
                    "revision")
            based.append(d)
    index = {
        "schema_version": "handoff-index/1", "engagement_id": eng.name, "revision": rev,
        "based_on": based,
        "scope_refs": [s["id"] for s in scope.get("items") or []],
        "exclusions": [{"ref": e["ref"], "reason": "{} (autorizado: {})".format(
            e["reason"], e["authorization_ref"])}
            for s in scope.get("items") or [] for e in s.get("excludes") or []],
        "code_version": _code_version(), "pack_version": _pack_version(eng),
        "files": [{"path": r, "sha256": _sha(dest / r)} for r in todos],
        "authorization_refs": sorted({"decisions.md#" + b["id"]
                                      for b in F["authorization_blocks"](eng)}
                                     | ({"decisions.md#" + ap["block"]} if ap.get("block")
                                        else set())),
        "readiness": {"delivery": rd["delivery"], "ready": rd["ready"],
                      "reasons": rd["reasons"], "render_checks": rd["render_checks"],
                      "blueprint_approval": ap["state"]},
        "proofs": {"performed": [],
                   "pending": ["{} ({})".format(p["claim"], ", ".join(p["wp"]) or "sem WP")
                               for p in rd["proofs"]]
                   + ["{} — pode invalidar a viabilidade".format(v["id"])
                      for v in rd["viability_blockers"]]},
        "receiver_acceptance": None, "delivery_level": level,
        "scope_definition": {s["id"]: {"includes": s.get("includes"),
                                       "excludes": s.get("excludes"),
                                       "authorized_by": s.get("authorized_by")}
                             for s in scope.get("items") or []},
        "limitations": rd["reasons"] or ["nenhuma limitação estrutural; provas por executar"],
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    errors, _u = W["validate"](index, W["load_schema"]("handoff-index"))
    if errors:
        shutil.rmtree(dest)
        raise ReleaseError("índice inválido: {}".format(errors[0]), W["INTEGRITY_FAILURE"])
    (dest / INDEX).write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                              encoding="utf-8", newline="\n")
    return {"revision": rev, "path": str(dest), "delivery_level": level,
            "files": len(todos), "reasons": rd["reasons"]}


def verify(pkg) -> dict:
    """T39/T40: cada ficheiro do índice com o mesmo `sha256`, nenhum a mais nem a menos, e
    nenhum segredo."""
    pkg = Path(pkg)
    try:
        index = json.loads((pkg / INDEX).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"ok": False, "code": "INDEX_UNREADABLE", "detail": str(exc)}
    listed = {f["path"]: f["sha256"] for f in index.get("files") or []}
    mismatch = sorted(p for p, h in listed.items() if (pkg / p).is_file() and _sha(pkg / p) != h)
    missing = sorted(p for p in listed if not (pkg / p).is_file())
    extra = sorted(p.relative_to(pkg).as_posix() for p in pkg.rglob("*")
                   if p.is_file() and p.name != INDEX
                   and p.relative_to(pkg).as_posix() not in listed)
    segredos = {p: _text_secrets(pkg / p) for p in listed if (pkg / p).is_file()
                and _text_secrets(pkg / p)}
    ok = not (mismatch or missing or extra or segredos)
    return {"ok": ok, "revision": index.get("revision"), "mismatch": mismatch,
            "missing": missing, "extra": extra, "secrets": segredos,
            "index_sha256": _sha(pkg / INDEX)}


def acceptance_block(eng, revision: int, validated_by: str, scope: str, conditions: str,
                     simulated: bool = False, timestamp: str | None = None) -> str:
    """O bloco de aceitação do destinatário (Q6), com o `sha256` do índice do release. Um
    agente nunca aceita pelo destinatário; um release que não verifica não se aceita."""
    eng = Path(eng)
    W, F = _mod("workflow"), _mod("functional")
    prob = F["validator_problem"](validated_by)
    if prob:
        raise ReleaseError("aceitação recusada: " + prob, W["AUTHORIZATION_REQUIRED"])
    pkg = eng / RELEASE_DIR / "r{:04d}".format(int(revision))
    v = verify(pkg)
    if not v["ok"]:
        raise ReleaseError("o release r{:04d} não verifica — não se aceita".format(
            int(revision)), W["INTEGRITY_FAILURE"], v)
    ts = timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    did = "D-{:03d}".format(max([int(d[2:]) for d in W["_decision_ids"](eng)] or [0]) + 1)
    return ("\n## {} — {} (release r{:04d})\n\n- **Release sha256**: {}\n- **Scope**: {}\n"
            "- **Conditions**: {}\n- **Simulated**: {}\n- **Validated by**: {}\n"
            "- **Timestamp**: {}\n").format(did, ACC_TITLE, int(revision), v["index_sha256"],
                                           scope, conditions or "nenhuma",
                                           "yes" if simulated else "no", validated_by, ts)


def status(eng, revision: int) -> dict:
    """O nível do release agora: o do build, subido a `accepted_by_receiver` só por um bloco
    de aceitação não simulado com o `sha256` do índice que verifica."""
    eng = Path(eng)
    pkg = eng / RELEASE_DIR / "r{:04d}".format(int(revision))
    v = verify(pkg)
    index = json.loads((pkg / INDEX).read_text(encoding="utf-8")) if (pkg / INDEX).is_file() \
        else {}
    level = index.get("delivery_level", "preliminary") if v["ok"] else "preliminary"
    try:
        md = (eng / "decisions.md").read_text(encoding="utf-8")
    except OSError:
        md = ""
    aceite = None
    for m in ACC_HEAD_RE.finditer(md):
        if int(m.group(2)) != int(revision):
            continue
        corpo = md[m.end():].split("\n## ", 1)[0]
        sha = re.search(r"\*\*Release sha256\*\*\s*:\s*([0-9a-f]{64})", corpo)
        sim = re.search(r"\*\*Simulated\*\*\s*:\s*(\w+)", corpo)
        aceite = {"block": m.group(1), "simulated": bool(sim and sim.group(1) == "yes"),
                  "matches": bool(sha and v["ok"] and sha.group(1) == v["index_sha256"])}
    if aceite and aceite["matches"] and not aceite["simulated"] \
            and level == "ready_for_receiver_review":
        level = "accepted_by_receiver"
    return {"revision": int(revision), "verify": v, "delivery_level": level,
            "acceptance": aceite}


def main(argv=None) -> int:
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:                                                   # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="release do handoff (build/verify/status)")
    ap.add_argument("command", choices=["build", "verify", "status", "acceptance-block"])
    ap.add_argument("--engagement", default="")
    ap.add_argument("--package", default="")
    ap.add_argument("--revision", type=int, default=0)
    ap.add_argument("--validated-by", default="")
    ap.add_argument("--scope", default="")
    ap.add_argument("--conditions", default="")
    ap.add_argument("--simulated", action="store_true")
    a = ap.parse_args(argv)
    eng = Path(a.engagement)
    if a.engagement and not eng.is_dir():
        eng = Path("projects") / a.engagement
    W = _mod("workflow")
    try:
        if a.command == "build":
            out, rc = build(eng), 0
        elif a.command == "verify":
            out = verify(a.package or eng / RELEASE_DIR / "r{:04d}".format(a.revision))
            rc = 0 if out["ok"] else 1
        elif a.command == "status":
            out, rc = status(eng, a.revision), 0
        else:
            print(acceptance_block(eng, a.revision, a.validated_by, a.scope, a.conditions,
                                   a.simulated))
            return 0
    except ReleaseError as exc:
        print(json.dumps(W["response"](False, exc.code if exc.code in W["CODES"]
                                       else W["INTEGRITY_FAILURE"],
                                       [W["_reason"](str(exc), "release", exc.code)]),
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return rc


if __name__ == "__main__":
    sys.exit(main())
