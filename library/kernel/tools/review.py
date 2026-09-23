"""review.py — candidatos publicados e a sua revisão independente (handoff-v1 F5).

`_design/candidates.json` (`handoff-candidates/1`) é o conjunto de candidatos de Options, com
revisão; só este motor o publica, pelo coordenador (`operation.run`, base e read-set), com a
cópia imutável de cada revisão em `_design/history/candidates.r<NNNN>.json`. Um parecer é
preso à revisão que leu: publicar candidatos antes de disparar revisores é o que torna isso
possível (plano 03 → *Sequência de Options*).

    draft-candidates    abre um rascunho em `_drafts/CANDDRAFT-…/`
    check-candidates    valida sem escrever
    publish-candidates  publica a revisão nova e a sua cópia imutável
    show-candidates     o estado do conjunto

Regras por rota (plano 02 §5, T27): `platform-constrained` — todos os candidatos na
plataforma imposta, com a autoridade da rota; nada de shortlist artificial de plataformas;
um candidato viável basta, com motivo. `solution-choice` — menos de três candidatos só com
o motivo escrito. `change-impact` — cada candidato descreve o delta e o raio de impacto sobre
uma baseline declarada.

Desenho: `docs/handoff-v1/F5/DESENHO.md` (Q2, §1).
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

CAND_PATH = "_design/candidates.json"
HISTORY_DIR = "_design/history"
DRAFTS_DIR = "_drafts"
CAND_PREFIX = "CANDDRAFT-"
CAND_FILE = "candidates.json"
DRAFT_MANIFEST = "_canddraft.json"
DRAFT_SCHEMA = "aisa-candidates-draft/1"
SCHEMA = "handoff-candidates/1"
SU_ID_RE = re.compile(r"^[CAUXRMD]-\d+$")


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


class ReviewError(Exception):
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
        raise ReviewError("{} ilegível — nada se escreve por cima".format(what),
                          _W()["INTEGRITY_FAILURE"], {"path": str(p), "detail": str(exc)})


def _workflow(eng: Path) -> dict:
    who = _W()["profile_of"](eng)
    if who["kind"] != _W()["HANDOFF"]:
        raise ReviewError("candidatos só num engagement handoff-v1",
                          _W()["UNSUPPORTED_PROFILE"], {"kind": who["kind"]})
    return who["workflow"] or {}


def _su_ids(eng: Path) -> set:
    try:
        md = (eng / "shared-understanding.md").read_text(encoding="utf-8")
    except OSError:
        return set()
    _h, rows, _s, _d = _D()["parse_su"](md)
    return {r["id"] for r in rows}


# ------------------------------------------------------------------ candidatos

def skeleton(eng: Path, route: str) -> dict:
    return {"schema_version": SCHEMA, "engagement_id": Path(eng).name, "revision": 0,
            "route": route, "based_on": [], "retired_ids": [], "criteria": [],
            "exclusions": [], "items": []}


def read_candidates(eng) -> dict:
    eng = Path(eng)
    p = eng / CAND_PATH
    dg = _digest(p)
    if not dg:
        return {"data": skeleton(eng, _workflow(eng).get("route")), "digest": ""}
    data = _load(p, CAND_PATH)
    if isinstance(data, dict) and data.get("schema_version") != SCHEMA:
        raise ReviewError("candidatos com schema `{}`; esta versão lê {}".format(
            data.get("schema_version"), SCHEMA), _W()["SCHEMA_UNSUPPORTED"], {"path": CAND_PATH})
    return {"data": data, "digest": dg}


def _problem(code: str, cid: str, detail: str) -> dict:
    return {"code": code, "candidate": cid, "detail": detail}


def _same(a, b) -> bool:
    return str(a or "").strip().casefold() == str(b or "").strip().casefold()


def candidate_integrity(eng, data: dict, prev: dict) -> list:
    """O que recusa a publicação (fail-closed)."""
    eng = Path(eng)
    W = _W()
    wf = _workflow(eng)
    out = []
    errors, _u = W["validate"](data, W["load_schema"]("handoff-candidates"))
    for e in errors:
        out.append(_problem("SCHEMA", "", str(e)))
    if errors:
        return out
    if data.get("engagement_id") != eng.name:
        out.append(_problem("ENGAGEMENT", "", "engagement_id `{}` não é `{}`".format(
            data.get("engagement_id"), eng.name)))
    if int(data["revision"]) != int(prev.get("revision") or 0) + 1:
        out.append(_problem("REVISION", "", "revisão {} — esperava {}".format(
            data["revision"], int(prev.get("revision") or 0) + 1)))
    if data["route"] != wf.get("route"):
        out.append(_problem("ROUTE", "", "os candidatos dizem rota `{}`; o engagement está em "
                            "`{}`".format(data["route"], wf.get("route"))))
    ids = [c["id"] for c in data["items"]]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        out.append(_problem("DUPLICATE_ID", dup, "id repetido"))
    retired = set(data.get("retired_ids") or [])
    for i in sorted(set(prev.get("retired_ids") or []) - retired):
        out.append(_problem("RETIRED_DROPPED", i, "id retirado deixou de constar em retired_ids"))
    for i in sorted(set(ids) & retired):
        out.append(_problem("REUSED_ID", i, "id retirado reutilizado"))
    for i in sorted({c["id"] for c in prev.get("items") or []} - set(ids) - retired):
        out.append(_problem("SILENT_REMOVAL", i, "candidato desapareceu sem entrar em "
                            "retired_ids"))
    su = _su_ids(eng)
    for c in data["items"]:
        for r in list(c.get("premise_refs") or []):
            rid = r.split("#")[-1]
            if not (SU_ID_RE.match(rid) and rid in su):
                out.append(_problem("DEAD_REF", c["id"], "premissa `{}` não é linha da SU"
                                    .format(r)))
    # -- regras por rota (T27)
    route = data["route"]
    if route == "platform-constrained":
        imposta = str(data.get("imposed_platform") or "").strip()
        autoridade = (wf.get("route_basis") or {}).get("authority_ref")
        if not imposta:
            out.append(_problem("NO_IMPOSED_PLATFORM", "", "rota com plataforma imposta sem "
                                "`imposed_platform`"))
        if not autoridade or not _same(data.get("imposition_ref"), autoridade):
            out.append(_problem("IMPOSITION_REF", "", "`imposition_ref` não é a autoridade da "
                                "rota (`{}`)".format(autoridade)))
        for c in data["items"]:
            if imposta and not _same(c.get("platform"), imposta):
                out.append(_problem("OUTSIDE_IMPOSED_PLATFORM", c["id"],
                                    "`{}` fora da plataforma imposta `{}` — com a tecnologia "
                                    "imposta, as opções geram-se dentro dela".format(
                                        c.get("platform"), imposta)))
    elif route == "solution-choice":
        if 0 < len(data["items"]) < 3 and not str(data.get("reduction_reason") or "").strip():
            out.append(_problem("SHORTLIST_WITHOUT_REASON", "",
                                "{} candidato(s) sem `reduction_reason` — a lista nunca se "
                                "reduz sem motivo".format(len(data["items"]))))
    elif route == "change-impact":
        if not str(data.get("baseline_ref") or "").strip():
            out.append(_problem("NO_BASELINE", "", "rota de mudança sem `baseline_ref`"))
        for c in data["items"]:
            if not str(c.get("delta") or "").strip() or not c.get("impact_refs"):
                out.append(_problem("NO_DELTA", c["id"], "candidato de mudança sem `delta` e "
                                    "`impact_refs`"))
    if not data["items"]:
        out.append(_problem("EMPTY", "", "nenhum candidato"))
    return out


def candidate_gaps(data: dict) -> list:
    """O que falta dizer num candidato; não recusa (fica visível)."""
    out = []
    for c in data.get("items") or []:
        om = c.get("order_of_magnitude") or {}
        if not (str(om.get("value") or "").strip() and str(om.get("source") or "").strip()) \
                and not str(om.get("unavailable") or "").strip():
            out.append(_problem("NO_ORDER_OF_MAGNITUDE", c["id"],
                                "ordem de grandeza sem fonte, nem declarada indisponível com o "
                                "que falta"))
        for campo in ("architecture", "reversibility"):
            if not str(c.get(campo) or "").strip():
                out.append(_problem("MISSING_" + campo.upper(), c["id"],
                                    "`{}` em falta".format(campo)))
    return out


def _reads(eng: Path) -> dict:
    rels = ["shared-understanding.md", "decisions.md", "frame.md", "_state.json"]
    return {r: _digest(eng / r) for r in rels}


def draft_candidates(eng) -> dict:
    eng = Path(eng)
    _workflow(eng)
    cur = read_candidates(eng)
    semente = "{}|{}".format(time.time_ns(), os.getpid())
    did = CAND_PREFIX + hashlib.sha256(semente.encode("utf-8")).hexdigest()[:12]
    d = eng / DRAFTS_DIR / did
    d.mkdir(parents=True)
    corpo = dict(cur["data"], revision=int(cur["data"].get("revision") or 0) + 1)
    (d / CAND_FILE).write_text(json.dumps(corpo, ensure_ascii=False, indent=1) + "\n",
                               encoding="utf-8", newline="\n")
    man = {"schema_version": DRAFT_SCHEMA, "id": did, "base": cur["digest"],
           "reads": _reads(eng), "published": None,
           "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    _O()["_atomic_write"](d / DRAFT_MANIFEST, json.dumps(man, ensure_ascii=False, indent=2))
    return {"draft": did, "path": str(d / CAND_FILE), "revision": corpo["revision"]}


def open_candidate_drafts(eng) -> list:
    """Rascunhos de candidatos ainda por publicar, abertos sobre a revisão corrente."""
    eng = Path(eng)
    cur = read_candidates(eng)["digest"]
    out = []
    for m in sorted((eng / DRAFTS_DIR).glob(CAND_PREFIX + "*/" + DRAFT_MANIFEST)):
        try:
            man = json.loads(m.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not man.get("published") and man.get("base") == cur:
            out.append(man["id"])
    return out


def _read_draft(eng: Path, did: str) -> tuple:
    d = eng / DRAFTS_DIR / did
    if not did.startswith(CAND_PREFIX) or not (d / DRAFT_MANIFEST).is_file():
        raise ReviewError("rascunho inexistente: {}".format(did), "DRAFT_MISSING", {"draft": did})
    return _load(d / DRAFT_MANIFEST, DRAFT_MANIFEST), _load(d / CAND_FILE, CAND_FILE)


def check_candidates(eng, data: dict | None = None) -> dict:
    eng = Path(eng)
    W = _W()
    cur = read_candidates(eng)
    prev = cur["data"]
    alvo = prev if data is None else data
    prova = dict(prev, revision=int(prev.get("revision") or 0) - 1) if data is None else prev
    inte = candidate_integrity(eng, alvo, prova)
    gaps = [] if inte else candidate_gaps(alvo)
    if inte:
        resp = W["response"](False, W["INTEGRITY_FAILURE"],
                             [W["_reason"](p["detail"], "review", p["code"]) for p in inte],
                             affected_ids=sorted({p["candidate"] for p in inte if p["candidate"]}),
                             input_revision=cur["digest"] or None)
    elif gaps:
        resp = W["response"](False, W["BLOCKING_GAP"],
                             [W["_reason"](p["detail"], "review", p["code"]) for p in gaps],
                             affected_ids=sorted({p["candidate"] for p in gaps}),
                             input_revision=cur["digest"] or None)
    else:
        resp = W["response"](True, input_revision=cur["digest"] or None)
    return dict(resp, integrity=inte, gaps=gaps)


def publish_candidates(eng, draft_id: str) -> dict:
    eng = Path(eng)
    W, O = _W(), _O()
    _workflow(eng)
    man, data = _read_draft(eng, draft_id)
    if man.get("published"):
        prior = O["read_receipt"](eng, man["published"])
        if prior:
            return {"operation_id": man["published"], "revision": data["revision"],
                    "receipt": prior, "replayed": True, "gaps": candidate_gaps(data)}
    cur = read_candidates(eng)
    if man["base"] != cur["digest"]:
        raise ReviewError("os candidatos mudaram depois do rascunho — abrir um rascunho novo",
                          W["STALE_INPUT"], {"draft": draft_id})
    mudou = sorted(r for r, dg in (man.get("reads") or {}).items() if _digest(eng / r) != dg)
    if mudou:
        raise ReviewError("inputs mudaram depois do rascunho: {}".format(", ".join(mudou)),
                          W["STALE_INPUT"], {"draft": draft_id, "paths": mudou})
    res = check_candidates(eng, data)
    if res["integrity"]:
        raise ReviewError("o rascunho viola a integridade dos candidatos: " + "; ".join(
            "{} {}".format(p["candidate"], p["detail"]).strip() for p in res["integrity"]),
            W["INTEGRITY_FAILURE"], {"draft": draft_id, "problems": res["integrity"]})
    texto = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    hist = "{}/candidates.r{:04d}.json".format(HISTORY_DIR, int(data["revision"]))
    op_id = "candidates-{}".format(hashlib.sha256(
        (cur["digest"] + texto).encode("utf-8")).hexdigest()[:16])
    recibo = O["run"](eng, op_id, {CAND_PATH: texto, hist: texto},
                      expected={CAND_PATH: cur["digest"], hist: ""},
                      read_set=man.get("reads") or {})
    man["published"] = op_id
    O["_atomic_write"](eng / DRAFTS_DIR / draft_id / DRAFT_MANIFEST,
                       json.dumps(man, ensure_ascii=False, indent=2))
    return {"operation_id": op_id, "revision": data["revision"], "history": hist,
            "receipt": recibo, "gaps": res["gaps"]}


def show_candidates(eng) -> dict:
    eng = Path(eng)
    cur = read_candidates(eng)
    data = cur["data"]
    return {"revision": data.get("revision"), "digest": cur["digest"],
            "route": data.get("route"), "items": [c["id"] for c in data.get("items") or []],
            "gaps": candidate_gaps(data), "open_drafts": open_candidate_drafts(eng)}


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:                                                   # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="candidatos e revisão independente (coordenador)")
    ap.add_argument("command", choices=["draft-candidates", "check-candidates",
                                        "publish-candidates", "show-candidates"])
    ap.add_argument("--engagement", required=True)
    ap.add_argument("--draft", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    eng = Path(a.engagement)
    if not eng.is_dir():
        eng = Path("projects") / a.engagement
    W, O = _W(), _O()
    try:
        if a.command == "draft-candidates":
            out, rc = draft_candidates(eng), 0
        elif a.command == "check-candidates":
            data = _read_draft(eng, a.draft)[1] if a.draft else None
            out = check_candidates(eng, data)
            rc = 0 if out["ok"] else (4 if out["code"] == W["BLOCKING_GAP"] else 1)
        elif a.command == "publish-candidates":
            out = publish_candidates(eng, a.draft)
            out = {k: v for k, v in out.items() if k != "receipt"} if not a.json else out
            rc = 0
        else:
            out, rc = show_candidates(eng), 0
    except ReviewError as exc:
        print(json.dumps(W["response"](False, exc.code if exc.code in W["CODES"]
                                       else W["INTEGRITY_FAILURE"],
                                       [W["_reason"](str(exc), "review", exc.code)]),
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
