"""inventory.py — o âmbito autorizado e o inventário de trabalho (handoff-v1 F6).

Dois artefactos, cada um com revisão e histórico imutável, publicados só por este motor pelo
coordenador (`operation.run`, com base e read-set), como os FC da F4:

    `_design/scope.json` (`handoff-scope/1`) — cada `SCOPE-NNNN`: o que inclui (linhas da
        SU, jornadas) e o que exclui, cada exclusão autorizada
    `_design/work-packages.json` (`handoff-work-packages/1`) — cada `WP-NNNN`: o que realiza
        (FC, nós do desenho, linhas), o que prova, de que depende, a aceitação e a definição
        de feito

    draft    abre um rascunho em `_drafts/<KIND>DRAFT-…/` (revisão corrente ou esqueleto)
    check    valida sem escrever: integridade (recusa) e lacunas (visíveis)
    publish  publica numa operação a revisão nova e a sua cópia em `_design/history/`
    show     o estado corrente

Integridade falha fechada (`INTEGRITY_FAILURE`): schema, ids nunca reutilizados, revisão +1,
referências que resolvem (nós do desenho pelo resolvedor de selectores do `coverage.py`: um
nó exacto, nunca um fallback), `depends_on` sem ciclo, exclusão sem autorização, e esforço
dentro do inventário (o esforço é só da estimativa — DESENHO Q2).

Desenho: `docs/handoff-v1/F6/DESENHO.md` (Q1, Q3, §1).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import runpy
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CACHE: dict = {}

HISTORY_DIR = "_design/history"
DRAFTS_DIR = "_drafts"
DRAFT_MANIFEST = "_invdraft.json"
DRAFT_SCHEMA = "aisa-inventory-draft/1"
FC_PATH = "_design/functional-contracts.json"
KINDS = {
    "scope": {"path": "_design/scope.json", "schema": "handoff-scope/1",
              "schema_file": "handoff-scope", "prefix": "SCOPEDRAFT-", "file": "scope.json",
              "id": re.compile(r"^SCOPE-\d{4}$")},
    "work-packages": {"path": "_design/work-packages.json",
                      "schema": "handoff-work-packages/1",
                      "schema_file": "handoff-work-packages", "prefix": "WPDRAFT-",
                      "file": "work-packages.json", "id": re.compile(r"^WP-\d{4}$")},
}
SU_ID_RE = re.compile(r"^[CAUXRM]-\d+$")
D_RE = re.compile(r"^D-\d{3,}$")
FC_RE = re.compile(r"^FC-\d{4}$")
J_RE = re.compile(r"^J-\d{4}$")
# Um inventário que carrega esforço compete com a estimativa (Q2): recusado.
EFFORT_KEYS = {"effort", "esforco", "esforço", "duration", "duracao", "duração", "days",
               "dias", "hours", "horas", "estimate", "estimativa", "person_days"}


def _mod(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = runpy.run_path(str(_HERE / (name + ".py")))
    return _CACHE[name]


def _W() -> dict:
    return _mod("workflow")


def _O() -> dict:
    return _mod("operation")


def _D() -> dict:
    return _mod("dashboard")


def _C() -> dict:
    return _mod("coverage")


class InventoryError(Exception):
    def __init__(self, message: str, code: str, detail: dict | None = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or {}


def _digest(p: Path) -> str:
    return _O()["digest"](p)


def _load(p: Path, what: str):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise InventoryError("{} ilegível — nada se escreve por cima".format(what),
                             _W()["INTEGRITY_FAILURE"], {"path": str(p), "detail": str(exc)})


def _kind(kind: str) -> dict:
    if kind not in KINDS:
        raise InventoryError("tipo `{}` desconhecido (scope · work-packages)".format(kind),
                             _W()["INTEGRITY_FAILURE"], {"kind": kind})
    return KINDS[kind]


def _profile_or_refuse(eng: Path) -> None:
    who = _W()["profile_of"](eng)
    if who["kind"] != _W()["HANDOFF"]:
        raise InventoryError("âmbito e inventário só num engagement handoff-v1",
                             _W()["UNSUPPORTED_PROFILE"], {"kind": who["kind"]})


def skeleton(eng: Path, kind: str) -> dict:
    return {"schema_version": _kind(kind)["schema"], "engagement_id": Path(eng).name,
            "revision": 0, "based_on": [], "retired_ids": [], "items": []}


def read_current(eng, kind: str) -> dict:
    eng = Path(eng)
    k = _kind(kind)
    p = eng / k["path"]
    dg = _digest(p)
    if not dg:
        return {"data": skeleton(eng, kind), "digest": ""}
    data = _load(p, k["path"])
    if isinstance(data, dict) and data.get("schema_version") != k["schema"]:
        raise InventoryError("{} com schema `{}`; esta versão lê {}".format(
            k["path"], data.get("schema_version"), k["schema"]), _W()["SCHEMA_UNSUPPORTED"],
            {"path": k["path"]})
    return {"data": data, "digest": dg}


def _su_ids(eng: Path) -> set:
    try:
        md = (eng / "shared-understanding.md").read_text(encoding="utf-8")
    except OSError:
        return set()
    _h, rows, _s, _d = _D()["parse_su"](md)
    return {r["id"] for r in rows}


def _fcs(eng: Path) -> dict:
    try:
        data = json.loads((eng / FC_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {i["id"]: i for i in data.get("items") or [] if isinstance(i, dict) and "id" in i}


def _problem(code: str, item: str, detail: str) -> dict:
    return {"code": code, "item": item, "detail": detail}


def _effort_keys(obj, path="") -> list:
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).casefold() in EFFORT_KEYS:
                out.append(path + "." + str(k) if path else str(k))
            out += _effort_keys(v, (path + "." if path else "") + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += _effort_keys(v, "{}[{}]".format(path, i))
    return out


def _cycle(items: list) -> list:
    graph = {w["id"]: list(w.get("depends_on") or []) for w in items}
    state, stack = {}, []

    def visit(n):
        state[n] = 1
        stack.append(n)
        for m in graph.get(n, []):
            if state.get(m) == 1:
                return stack[stack.index(m):] + [m]
            if m in graph and not state.get(m):
                c = visit(m)
                if c:
                    return c
        state[n] = 2
        stack.pop()
        return []

    for n in graph:
        if not state.get(n):
            c = visit(n)
            if c:
                return c
    return []


def integrity(eng, kind: str, data: dict, prev: dict) -> list:
    """O que recusa a publicação (fail-closed)."""
    eng = Path(eng)
    W, k = _W(), _kind(kind)
    out = [_problem("SCHEMA", "", str(e))
           for e in W["validate"](data, W["load_schema"](k["schema_file"]))[0]]
    if out:
        return out
    if data.get("engagement_id") != eng.name:
        out.append(_problem("ENGAGEMENT", "", "engagement_id `{}` não é `{}`".format(
            data.get("engagement_id"), eng.name)))
    if int(data["revision"]) != int(prev.get("revision") or 0) + 1:
        out.append(_problem("REVISION", "", "revisão {} — esperava {}".format(
            data["revision"], int(prev.get("revision") or 0) + 1)))
    ids = [i["id"] for i in data["items"]]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        out.append(_problem("DUPLICATE_ID", dup, "id repetido"))
    retired = set(data.get("retired_ids") or [])
    for i in sorted(set(prev.get("retired_ids") or []) - retired):
        out.append(_problem("RETIRED_DROPPED", i, "id retirado deixou de constar em retired_ids"))
    for i in sorted(set(ids) & retired):
        out.append(_problem("REUSED_ID", i, "id retirado reutilizado"))
    for i in sorted({x["id"] for x in prev.get("items") or []} - set(ids) - retired):
        out.append(_problem("SILENT_REMOVAL", i, "item desapareceu sem entrar em retired_ids"))
    for p in _effort_keys(data):
        out.append(_problem("EFFORT_IN_INVENTORY", "", "`{}` — o esforço é só da estimativa"
                            .format(p)))
    su = _su_ids(eng)
    decisions = set(W["_decision_ids"](eng))
    fcs = _fcs(eng)
    journeys = {f.get("journey_id") for f in fcs.values() if f.get("journey_id")}
    if kind == "scope":
        for s in data["items"]:
            for inc in s.get("includes") or []:
                r = inc["ref"]
                if not ((SU_ID_RE.match(r) and r in su) or (J_RE.match(r) and r in journeys)):
                    out.append(_problem("DEAD_REF", s["id"], "incluído `{}` não é linha da SU "
                                        "nem jornada de um FC".format(r)))
            for exc in s.get("excludes") or []:
                a = str(exc.get("authorization_ref") or "").split("#")[-1]
                if not (D_RE.match(a) and a in decisions):
                    out.append(_problem("UNAUTHORIZED_EXCLUSION", s["id"], "exclusão `{}` sem "
                                        "autorização em decisions.md".format(exc["ref"])))
            a = str(s.get("authorized_by") or "").split("#")[-1]
            if a and not (D_RE.match(a) and a in decisions):
                out.append(_problem("DEAD_REF", s["id"], "`authorized_by` {} não existe"
                                    .format(a)))
    else:
        scopes = {x["id"] for x in read_current(eng, "scope")["data"].get("items") or []}
        wps = set(ids)
        C = _C()
        for w in data["items"]:
            if w["scope_id"] not in scopes:
                out.append(_problem("DEAD_REF", w["id"], "`scope_id` {} não existe em "
                                    "_design/scope.json".format(w["scope_id"])))
            for r in list(w.get("realizes") or []) + list(w.get("proves") or []):
                if FC_RE.match(r):
                    ok = r in fcs
                elif SU_ID_RE.match(r) or D_RE.match(r):
                    ok = r in su or r in decisions
                else:
                    ok = C["resolve_unit"](eng, r)["ok"]
                if not ok:
                    out.append(_problem("DEAD_REF", w["id"], "`{}` não resolve para um nó"
                                        .format(r)))
            for r in w.get("proves") or []:
                if "proof_obligations" not in r:
                    out.append(_problem("NOT_A_PROOF", w["id"], "`proves` aponta `{}`, que não é "
                                        "uma obrigação de prova do desenho".format(r)))
            for d in w.get("depends_on") or []:
                if d not in wps:
                    out.append(_problem("DEAD_REF", w["id"], "depende de `{}`, que não existe"
                                        .format(d)))
            for a in w.get("acceptance") or []:
                if a.get("fc") and a["fc"] not in fcs:
                    out.append(_problem("DEAD_REF", w["id"], "aceitação cita `{}`, que não "
                                        "existe".format(a["fc"])))
        ciclo = _cycle(data["items"])
        if ciclo:
            out.append(_problem("DEPENDENCY_CYCLE", ciclo[0], " → ".join(ciclo)))
    return out


def gaps(kind: str, data: dict) -> list:
    """O que falta dizer; não recusa (fica visível)."""
    out = []
    if kind == "scope":
        for s in data.get("items") or []:
            if not s.get("includes"):
                out.append(_problem("EMPTY_SCOPE", s["id"], "âmbito sem itens incluídos"))
            if not s.get("authorized_by"):
                out.append(_problem("SCOPE_NOT_AUTHORIZED", s["id"], "âmbito sem bloco que o "
                                    "autorize"))
        return out
    for w in data.get("items") or []:
        na = w.get("not_applicable") or {}
        for campo in ("realizes", "acceptance", "definition_of_done"):
            if not w.get(campo) and not str(na.get(campo) or "").strip():
                out.append(_problem("MISSING_" + campo.upper(), w["id"],
                                    "`{}` em falta, sem motivo em not_applicable".format(campo)))
    return out


def check(eng, kind: str, data: dict | None = None) -> dict:
    eng = Path(eng)
    W = _W()
    cur = read_current(eng, kind)
    prev = cur["data"]
    alvo = prev if data is None else data
    prova = dict(prev, revision=int(prev.get("revision") or 0) - 1) if data is None else prev
    inte = integrity(eng, kind, alvo, prova)
    gp = [] if inte else gaps(kind, alvo)
    if inte:
        resp = W["response"](False, W["INTEGRITY_FAILURE"],
                             [W["_reason"](p["detail"], "inventory", p["code"]) for p in inte],
                             affected_ids=sorted({p["item"] for p in inte if p["item"]}),
                             input_revision=cur["digest"] or None)
    elif gp:
        resp = W["response"](False, W["BLOCKING_GAP"],
                             [W["_reason"](p["detail"], "inventory", p["code"]) for p in gp],
                             affected_ids=sorted({p["item"] for p in gp}),
                             input_revision=cur["digest"] or None)
    else:
        resp = W["response"](True, input_revision=cur["digest"] or None)
    return dict(resp, integrity=inte, gaps=gp)


def _reads(eng: Path, kind: str) -> dict:
    rels = ["shared-understanding.md", "decisions.md", FC_PATH]
    if kind == "work-packages":
        rels.append(KINDS["scope"]["path"])
        rels += sorted("_blueprint/" + p.name for p in (eng / "_blueprint").glob("*.yaml"))
    return {r: _digest(eng / r) for r in rels if _digest(eng / r)}


def draft(eng, kind: str) -> dict:
    eng = Path(eng)
    k = _kind(kind)
    _profile_or_refuse(eng)
    cur = read_current(eng, kind)
    semente = "{}|{}|{}".format(kind, time.time_ns(), os.getpid())
    did = k["prefix"] + hashlib.sha256(semente.encode("utf-8")).hexdigest()[:12]
    d = eng / DRAFTS_DIR / did
    d.mkdir(parents=True)
    corpo = dict(cur["data"], revision=int(cur["data"].get("revision") or 0) + 1)
    (d / k["file"]).write_text(json.dumps(corpo, ensure_ascii=False, indent=1) + "\n",
                               encoding="utf-8", newline="\n")
    man = {"schema_version": DRAFT_SCHEMA, "id": did, "kind": kind, "base": cur["digest"],
           "reads": _reads(eng, kind), "published": None,
           "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    _O()["_atomic_write"](d / DRAFT_MANIFEST, json.dumps(man, ensure_ascii=False, indent=2))
    return {"draft": did, "path": str(d / k["file"]), "revision": corpo["revision"],
            "kind": kind}


def _read_draft(eng: Path, did: str) -> tuple:
    d = eng / DRAFTS_DIR / did
    kind = next((n for n, k in KINDS.items() if did.startswith(k["prefix"])), "")
    if not kind or not (d / DRAFT_MANIFEST).is_file():
        raise InventoryError("rascunho inexistente: {}".format(did), "DRAFT_MISSING",
                             {"draft": did})
    return kind, _load(d / DRAFT_MANIFEST, DRAFT_MANIFEST), _load(d / KINDS[kind]["file"],
                                                                  KINDS[kind]["file"])


def publish(eng, draft_id: str) -> dict:
    eng = Path(eng)
    W, O = _W(), _O()
    _profile_or_refuse(eng)
    kind, man, data = _read_draft(eng, draft_id)
    k = KINDS[kind]
    if man.get("published"):
        prior = O["read_receipt"](eng, man["published"])
        if prior:
            return {"operation_id": man["published"], "revision": data["revision"],
                    "kind": kind, "receipt": prior, "replayed": True,
                    "gaps": gaps(kind, data)}
    cur = read_current(eng, kind)
    if man["base"] != cur["digest"]:
        raise InventoryError("{} mudou depois do rascunho — abrir um rascunho novo".format(
            k["path"]), W["STALE_INPUT"], {"draft": draft_id})
    mudou = sorted(r for r, dg in (man.get("reads") or {}).items() if _digest(eng / r) != dg)
    if mudou:
        raise InventoryError("inputs mudaram depois do rascunho: {}".format(", ".join(mudou)),
                             W["STALE_INPUT"], {"draft": draft_id, "paths": mudou})
    res = check(eng, kind, data)
    if res["integrity"]:
        raise InventoryError("o rascunho viola a integridade: " + "; ".join(
            "{} {}".format(p["item"], p["detail"]).strip() for p in res["integrity"]),
            W["INTEGRITY_FAILURE"], {"draft": draft_id, "problems": res["integrity"]})
    texto = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    stem = k["file"].rsplit(".", 1)[0]
    hist = "{}/{}.r{:04d}.json".format(HISTORY_DIR, stem, int(data["revision"]))
    op_id = "{}-{}".format(stem, hashlib.sha256(
        (cur["digest"] + texto).encode("utf-8")).hexdigest()[:16])
    recibo = O["run"](eng, op_id, {k["path"]: texto, hist: texto},
                      expected={k["path"]: cur["digest"], hist: ""},
                      read_set=man.get("reads") or {})
    man["published"] = op_id
    O["_atomic_write"](eng / DRAFTS_DIR / draft_id / DRAFT_MANIFEST,
                       json.dumps(man, ensure_ascii=False, indent=2))
    return {"operation_id": op_id, "revision": data["revision"], "kind": kind, "history": hist,
            "receipt": recibo, "gaps": res["gaps"]}


def show(eng, kind: str) -> dict:
    eng = Path(eng)
    cur = read_current(eng, kind)
    data = cur["data"]
    return {"kind": kind, "revision": data.get("revision"), "digest": cur["digest"],
            "items": [i["id"] for i in data.get("items") or []], "gaps": gaps(kind, data)}


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:                                                   # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="âmbito e inventário de trabalho (coordenador)")
    ap.add_argument("command", choices=["draft", "check", "publish", "show"])
    ap.add_argument("--engagement", required=True)
    ap.add_argument("--kind", choices=sorted(KINDS), default="work-packages")
    ap.add_argument("--draft", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    eng = Path(a.engagement)
    if not eng.is_dir():
        eng = Path("projects") / a.engagement
    W, O = _W(), _O()
    try:
        if a.command == "draft":
            out, rc = draft(eng, a.kind), 0
        elif a.command == "check":
            if a.draft:
                kind, _m, data = _read_draft(eng, a.draft)
                out = check(eng, kind, data)
            else:
                out = check(eng, a.kind)
            rc = 0 if out["ok"] else (4 if out["code"] == W["BLOCKING_GAP"] else 1)
        elif a.command == "publish":
            out = publish(eng, a.draft)
            out = {k: v for k, v in out.items() if k != "receipt"} if not a.json else out
            rc = 0
        else:
            out, rc = show(eng, a.kind), 0
    except InventoryError as exc:
        print(json.dumps(W["response"](False, exc.code if exc.code in W["CODES"]
                                       else W["INTEGRITY_FAILURE"],
                                       [W["_reason"](str(exc), "inventory", exc.code)]),
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    except O["OperationError"] as exc:
        print(json.dumps(O["response_from_error"](exc), ensure_ascii=False, indent=2),
              file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return rc


if __name__ == "__main__":
    sys.exit(main())
