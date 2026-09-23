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
SPECIALISTS = _HERE.parent / "specialists.md"
REVIEWS_DIR = "_design/reviews"
REV_RE = re.compile(r"^(REV-\d{4})\.mandate\.json$")
PACKS_DIR = _HERE.parent.parent / "packs"
REPO = PACKS_DIR.parent.parent
MEMORY_DIR = ".claude/agent-memory/_universal"
OUTPUT_CONTRACT = ["task_id", "input_revision", "coverage", "findings", "assumptions",
                   "unanswered", "recommended_actions", "sources_used"]
PROHIBITED = ["escrever numa autoridade", "autorizar pelo cliente", "confirmar um facto por "
              "constar de outra resposta", "ler o parecer de outro revisor",
              "rever um candidato ainda em construção"]


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


# ------------------------------------------------------------------ router (F5.2)

def router_rules() -> list:
    """As regras do bloco ```router-rules``` de `library/kernel/specialists.md` (dono único)."""
    text = SPECIALISTS.read_text(encoding="utf-8")
    m = re.search(r"```router-rules\n(.*?)```", text, re.S)
    if not m:
        raise ReviewError("specialists.md sem bloco router-rules", _W()["INTEGRITY_FAILURE"])
    return json.loads(m.group(1))


def _latest_blueprint(eng: Path) -> dict:
    vs = sorted(eng.glob("_blueprint/ux-blueprint_v*.yaml"),
                key=lambda p: int(re.search(r"v(\d+)", p.name).group(1)))
    for p in reversed(vs):
        obj, _i = _D()["yl_parse"](p.read_text(encoding="utf-8"))
        if isinstance(obj, dict) and not obj.get("draft"):
            return {"rel": "_blueprint/" + p.name, "obj": obj}
    return {}


def _blueprint_flags(bp: dict) -> dict:
    """`{flag: [evidência]}` dos sinais estruturados de um desenho."""
    obj = bp.get("obj") or {}
    arch = obj.get("architecture") if isinstance(obj.get("architecture"), dict) else {}
    out = {"outside-platform": [], "external-access": [], "human-surface": [],
           "headless": []}
    for c in arch.get("compositions") or []:
        if isinstance(c, dict) and str(c.get("boundary", "")).strip() == "outside-platform":
            out["outside-platform"].append("{}#{}".format(bp["rel"], c.get("component")))
    for d in arch.get("record_authority") or []:
        if isinstance(d, dict) and str(d.get("access_mode", "owned")).strip() != "owned":
            out["external-access"].append("{}#{}".format(bp["rel"], d.get("key")))
    mode = str((arch.get("experience") or {}).get("mode") or "").strip() \
        if isinstance(arch.get("experience"), dict) else ""
    if obj.get("screens") or (mode and mode != "none"):
        out["human-surface"].append("{}#screens".format(bp["rel"]))
    if bp and mode == "none" and not obj.get("screens"):
        out["headless"].append("{}#experience.mode=none".format(bp["rel"]))
    return out


def route(eng, phase: str = "options") -> dict:
    """Os especialistas que o risco pede, com a razão, e os não chamados, com o que se
    verificou (plano 03 → *Seleção de especialistas*). Determinístico: as mesmas entradas dão
    sempre a mesma selecção."""
    eng = Path(eng)
    _workflow(eng)
    try:
        md = (eng / "shared-understanding.md").read_text(encoding="utf-8")
    except OSError:
        md = ""
    _h, rows, _s, _d = _D()["parse_su"](md)
    rows = [r for r in rows if not (r.get("retired") or r.get("parked") or r.get("resolved"))]
    bp = _latest_blueprint(eng)
    flags = _blueprint_flags(bp)
    cands = read_candidates(eng)["data"]
    cflags = {"om-unavailable": [c["id"] for c in cands.get("items") or []
                                 if not (c.get("order_of_magnitude") or {}).get("source")]}
    selected, not_called = [], []
    for rule in router_rules():
        role, ev = rule["role"], []
        if phase in (rule.get("always_in") or []):
            ev.append("always_in:{} — {}".format(phase, rule.get("reason", "")))
        terms = [t.casefold() for t in rule.get("su_terms") or []]
        for r in rows:
            if r.get("lens") in (rule.get("su_lens") or []) and \
                    (not terms or any(t in (r.get("claim") or "").casefold()
                                      for t in terms)):
                ev.append("{} ({})".format(r["id"], r.get("lens")))
        for f in rule.get("blueprint") or []:
            ev += ["{}: {}".format(f, e) for e in flags.get(f, [])]
        for f in rule.get("candidates") or []:
            ev += ["{}: {}".format(f, e) for e in cflags.get(f, [])]
        na = [w for w in rule.get("not_applicable_when") or [] if flags.get(w)]
        checked = "lentes {} por {} · desenho {} · candidatos {}".format(
            rule.get("su_lens") or "-", rule.get("su_terms") or "-",
            rule.get("blueprint") or "-", rule.get("candidates") or "-")
        if na:
            not_called.append({"role": role, "justification": "não aplicável: {} ({})".format(
                ", ".join(na), ", ".join(flags[na[0]]))})
        elif ev:
            selected.append({"role": role, "evidence": ev})
        else:
            not_called.append({"role": role, "justification": "nenhum sinal — verificado: "
                               + checked})
    return {"phase": phase, "candidate_revision": cands.get("revision"),
            "blueprint": bp.get("rel", ""), "selected": selected, "not_called": not_called}


# ------------------------------------------------------------------ mandato (F5.2)

def _pack_version(pack: str) -> str:
    try:
        text = (PACKS_DIR / pack / "pack.yaml").read_text(encoding="utf-8")
    except OSError:
        return ""
    m = re.search(r"(?m)^pack_version:\s*(\S+)", text)
    return m.group(1) if m else ""


def _next_rev(eng: Path) -> str:
    n = [int(REV_RE.match(p.name).group(1)[4:]) for p in (eng / REVIEWS_DIR).glob("REV-*")
         if REV_RE.match(p.name)]
    return "REV-{:04d}".format(max(n or [0]) + 1)


def mandate(eng, role: str, questions, knowledge=(), objective: str = "",
            scope_ids=(), budget: str = "uma leitura; sem rondas próprias") -> dict:
    """Publica o mandato ANTES de o revisor correr. Recusado sem candidatos publicados ou
    com um rascunho de candidatos aberto sobre a revisão corrente (T25); as unidades do pack
    ficam com caminho, `sha256` e versão (T29)."""
    eng = Path(eng)
    W, O = _W(), _O()
    wf = _workflow(eng)
    cur = read_candidates(eng)
    if not cur["digest"] or not cur["data"].get("items"):
        raise ReviewError("nenhum candidato publicado — um revisor só corre sobre uma revisão "
                          "publicada", W["BLOCKING_GAP"], {"role": role})
    abertos = open_candidate_drafts(eng)
    if abertos:
        raise ReviewError("candidatos em construção ({}) — publicar antes de rever".format(
            ", ".join(abertos)), W["BLOCKING_GAP"], {"drafts": abertos})
    roles = {r["role"] for r in router_rules()}
    if role not in roles:
        raise ReviewError("papel `{}` não existe em specialists.md".format(role),
                          W["INTEGRITY_FAILURE"], {"role": role})
    if not [q for q in questions if str(q).strip()]:
        raise ReviewError("mandato sem perguntas", W["INTEGRITY_FAILURE"], {"role": role})
    pack = json.loads((eng / "_state.json").read_text(encoding="utf-8")).get("pack", "")
    kref = []
    for k in knowledge:
        path = (REPO / k).resolve()
        base = (PACKS_DIR / pack).resolve()
        memoria = (REPO / MEMORY_DIR / role).resolve()
        if base in path.parents and path.is_file():
            kref.append({"ref": k, "sha256": _digest(path), "kind": "pack", "pack": pack,
                         "pack_version": _pack_version(pack)})
        elif memoria in path.parents and path.is_file():
            kref.append({"ref": k, "sha256": _digest(path), "kind": "memory", "role": role})
        else:
            raise ReviewError("fonte fora do pack activo e da memória do papel, ou inexistente: "
                              "{}".format(k), W["INTEGRITY_FAILURE"], {"ref": k})
    inputs = [CAND_PATH, "shared-understanding.md", "frame.md", "decisions.md",
              "_design/functional-contracts.json"]
    irefs = [{"ref": r, "sha256": _digest(eng / r)} for r in inputs if _digest(eng / r)]
    rid = _next_rev(eng)
    corpo = {"schema_version": "aisa-review-mandate/1", "task_id": rid, "role": role,
             "objective": objective or "rever a revisão publicada dos candidatos",
             "route": wf.get("route"), "scope_ids": list(scope_ids),
             "questions": [str(q) for q in questions], "input_refs": irefs,
             "candidate_revision": int(cur["data"]["revision"]), "knowledge_refs": kref,
             "output_contract": OUTPUT_CONTRACT,
             "stop_conditions": ["todas as perguntas com cobertura ou em `unanswered`"],
             "budget": budget, "prohibited_actions": PROHIBITED,
             "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    texto = json.dumps(corpo, ensure_ascii=False, indent=1) + "\n"
    rel = "{}/{}.mandate.json".format(REVIEWS_DIR, rid)
    recibo = O["run"](eng, "mandate-{}".format(hashlib.sha256(texto.encode("utf-8"))
                                               .hexdigest()[:16]),
                      {rel: texto}, expected={rel: ""},
                      read_set={r["ref"]: r["sha256"] for r in irefs})
    return {"task_id": rid, "mandate": rel, "receipt": recibo, "data": corpo}


def read_mandate(eng, rid: str) -> dict:
    return _load(Path(eng) / REVIEWS_DIR / "{}.mandate.json".format(rid), rid + ".mandate")


# ------------------------------------------------------------------ pareceres (F5.3)

REVIEW_SCHEMA = "handoff-review/1"
LEDGER_PATH = REVIEWS_DIR + "/ledger.json"
LEDGER_SCHEMA = "aisa-review-ledger/1"
DISPOSITIONS = ("accepted", "rejected", "delegated", "escalated", "deferred")
CLOSING = ("accepted", "rejected", "delegated")
MAX_DIVERGENCES, MAX_CALLS = 3, 2
O_ID_RE = re.compile(r"\bO-\d{3,}\b")


def _review_rel(rid: str) -> str:
    return "{}/{}.json".format(REVIEWS_DIR, rid)


def read_review(eng, rid: str) -> dict:
    p = Path(eng) / _review_rel(rid)
    return _load(p, rid) if p.is_file() else {}


def _source_digest(eng: Path, ref: str) -> str:
    base = REPO if ref.startswith(("library/", ".claude/")) else eng
    return _digest(base / ref)


def review_integrity(eng, mand: dict, rev: dict) -> list:
    """O que recusa um parecer (T29 e o contrato de saída)."""
    W = _W()
    out = [_problem("SCHEMA", "", str(e))
           for e in W["validate"](rev, W["load_schema"]("handoff-review"))[0]]
    if out:
        return out
    if rev["task_id"] != mand["task_id"] or rev["role"] != mand["role"]:
        out.append(_problem("TASK", rev["task_id"], "o parecer não é deste mandato"))
    if rev["input_revision"] != mand["candidate_revision"]:
        out.append(_problem("INPUT_REVISION", rev["task_id"], "leu a revisão {} — o mandato é "
                            "da {}".format(rev["input_revision"], mand["candidate_revision"])))
    feitas = {c["question"] for c in rev["coverage"]} | {u["question"] for u in rev["unanswered"]}
    for q in mand["questions"]:
        if q not in feitas:
            out.append(_problem("UNCOVERED_QUESTION", rev["task_id"], "pergunta do mandato sem "
                                "cobertura nem motivo: {}".format(q)))
    permitidas = {r["ref"]: r["sha256"] for r in mand["input_refs"] + mand["knowledge_refs"]}
    for s in rev["sources_used"]:
        if s["ref"] not in permitidas:
            out.append(_problem("SOURCE_NOT_IN_MANDATE", s["ref"], "fonte fora do mandato"))
        elif s["sha256"] != permitidas[s["ref"]]:
            out.append(_problem("SOURCE_DIGEST", s["ref"], "sha256 diferente do mandato"))
    ids = [f["id"] for f in rev["findings"]]
    for f in rev["findings"]:
        if not f["id"].startswith(rev["task_id"] + ".") or ids.count(f["id"]) > 1:
            out.append(_problem("FINDING_ID", f["id"], "id do achado fora do parecer ou repetido"))
    return out


def receive(eng, rid: str, payload: dict) -> dict:
    """Valida e publica o parecer de um mandato pelo coordenador. Uma fonte usada que mudou
    depois do mandato é `STALE_INPUT`: o parecer refaz-se, não se publica sobre outra base."""
    eng = Path(eng)
    W, O = _W(), _O()
    _workflow(eng)
    mand = read_mandate(eng, rid)
    mrel = "{}/{}.mandate.json".format(REVIEWS_DIR, rid)
    rev = dict(json.loads(json.dumps(payload)), schema_version=REVIEW_SCHEMA,
               task_id=payload.get("task_id", rid),
               candidate_revision=mand["candidate_revision"],
               mandate_sha256=_digest(eng / mrel))
    for i, f in enumerate(rev.get("findings") or [], 1):
        if isinstance(f, dict) and not f.get("id"):
            f["id"] = "{}.F{:02d}".format(rid, i)
    rev.pop("received_at", None)
    texto = json.dumps(rev, ensure_ascii=False, indent=1) + "\n"
    rel = _review_rel(rid)
    if (eng / rel).is_file():
        prior = dict(read_review(eng, rid))
        prior.pop("received_at", None)
        if json.dumps(prior, ensure_ascii=False, indent=1) + "\n" == texto:
            return {"task_id": rid, "review": rel, "replayed": True}
        raise ReviewError("{} já tem parecer publicado — um parecer nunca se reescreve"
                          .format(rid), W["INTEGRITY_FAILURE"], {"task_id": rid})
    probs = review_integrity(eng, mand, rev)
    if probs:
        raise ReviewError("o parecer viola o contrato de saída: " + "; ".join(
            "{} {}".format(p["candidate"], p["detail"]).strip() for p in probs),
            W["INTEGRITY_FAILURE"], {"task_id": rid, "problems": probs})
    mudou = sorted(s["ref"] for s in rev["sources_used"]
                   if _source_digest(eng, s["ref"]) != s["sha256"])
    if mudou:
        raise ReviewError("fontes mudaram depois do mandato: {}".format(", ".join(mudou)),
                          W["STALE_INPUT"], {"task_id": rid, "paths": mudou})
    rev["received_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    texto = json.dumps(rev, ensure_ascii=False, indent=1) + "\n"
    rs = {s["ref"]: s["sha256"] for s in rev["sources_used"]
          if not s["ref"].startswith(("library/", ".claude/"))}
    rs[mrel] = rev["mandate_sha256"]
    recibo = O["run"](eng, "review-{}".format(hashlib.sha256(texto.encode("utf-8"))
                                              .hexdigest()[:16]),
                      {rel: texto}, expected={rel: ""}, read_set=rs)
    return {"task_id": rid, "review": rel, "receipt": recibo,
            "findings": [f["id"] for f in rev["findings"]]}


def _changed_candidates(eng: Path, since: int) -> set:
    """Ids cujo candidato mudou (ou saiu) entre a revisão `since` e a corrente."""
    old = eng / "{}/candidates.r{:04d}.json".format(HISTORY_DIR, since)
    antes = {c["id"]: c for c in (_load(old, old.name).get("items") or [])} if old.is_file() else {}
    agora = {c["id"]: c for c in read_candidates(eng)["data"].get("items") or []}
    return {i for i, c in antes.items() if agora.get(i) != c} | (set(agora) - set(antes))


def read_ledger(eng) -> dict:
    eng = Path(eng)
    p = eng / LEDGER_PATH
    dg = _digest(p)
    if not dg:
        return {"data": {"schema_version": LEDGER_SCHEMA, "revision": 0, "dispositions": [],
                         "divergences": []}, "digest": ""}
    return {"data": _load(p, LEDGER_PATH), "digest": dg}


def _publish_ledger(eng: Path, cur: dict, data: dict, read_set: dict, tag: str) -> dict:
    data = dict(data, revision=int(cur["data"]["revision"]) + 1)
    texto = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    hist = "{}/review-ledger.r{:04d}.json".format(HISTORY_DIR, data["revision"])
    op = "{}-{}".format(tag, hashlib.sha256((cur["digest"] + texto).encode("utf-8"))
                        .hexdigest()[:16])
    recibo = _O()["run"](eng, op, {LEDGER_PATH: texto, hist: texto},
                         expected={LEDGER_PATH: cur["digest"], hist: ""}, read_set=read_set)
    return {"operation_id": op, "revision": data["revision"], "receipt": recibo, "data": data}


def _reviews(eng: Path) -> list:
    out = []
    for p in sorted((eng / REVIEWS_DIR).glob("REV-*.mandate.json")):
        rid = REV_RE.match(p.name).group(1)
        out.append((rid, _load(p, p.name), read_review(eng, rid)))
    return out


def _finding(eng: Path, fid: str) -> tuple:
    rid = fid.split(".")[0]
    rev = read_review(eng, rid)
    f = next((x for x in rev.get("findings") or [] if x["id"] == fid), None)
    if not f:
        raise ReviewError("achado inexistente: {}".format(fid), _W()["INTEGRITY_FAILURE"],
                          {"finding": fid})
    return rid, rev, f


def _resolves(eng: Path, ref: str) -> bool:
    """Uma referência de correcção que existe agora: `FC-NNNN` na revisão corrente dos
    contratos, `D-NNN` em `decisions.md`, uma linha da SU, ou um ficheiro do engagement."""
    ref = str(ref).strip()
    if re.fullmatch(r"FC-\d{4}", ref):
        try:
            fcs = json.loads((eng / "_design/functional-contracts.json").read_text(
                encoding="utf-8"))
        except (OSError, ValueError):
            return False
        return ref in {i.get("id") for i in fcs.get("items") or []}
    if re.fullmatch(r"D-\d{3,}", ref):
        return ref in set(_W()["_decision_ids"](eng))
    if SU_ID_RE.match(ref):
        return ref in _su_ids(eng)
    return bool(ref) and not ref.startswith(("/", "..")) and (eng / ref).is_file()


def dispose(eng, finding_id: str, disposition: str, rationale: str, evidence: str = "",
            envelope: str = "", owner: str = "", impact: str = "", to: str = "",
            corrected_by=()) -> dict:
    """Regista a disposição de um achado (plano 03 passo 4). Append-only: a disposição
    anterior e o parecer ficam; um achado de um parecer `stale` não se fecha (T26).
    `accepted` diz o que o corrigiu, e o motor verifica que existe (T43 S3): uma correcção
    ainda por fazer é `delegated` (envelope e dono) ou `deferred` (impacto)."""
    eng = Path(eng)
    W = _W()
    _workflow(eng)
    rid, rev, f = _finding(eng, finding_id)
    cur_rev = int(read_candidates(eng)["data"].get("revision") or 0)
    if rev["candidate_revision"] != cur_rev:
        raise ReviewError("{} leu a revisão {} dos candidatos; a corrente é a {} — revalidar, "
                          "não dispor".format(rid, rev["candidate_revision"], cur_rev),
                          W["STALE_INPUT"], {"finding": finding_id})
    falta = {"accepted": [], "rejected": [("evidence", evidence)],
             "delegated": [("envelope", envelope), ("owner", owner)],
             "escalated": [("to", to)], "deferred": [("impact", impact)]}
    if disposition not in falta:
        raise ReviewError("disposição `{}` fora de {}".format(disposition, DISPOSITIONS),
                          W["INTEGRITY_FAILURE"], {"finding": finding_id})
    em_falta = [k for k, v in [("rationale", rationale)] + falta[disposition]
                if not str(v).strip()]
    corr = [str(c).strip() for c in ([corrected_by] if isinstance(corrected_by, str)
                                     else corrected_by) if str(c).strip()]
    if disposition == "accepted" and not corr:
        em_falta.append("corrected_by")
    if em_falta:
        raise ReviewError("disposição `{}` sem {}".format(disposition, ", ".join(em_falta)),
                          W["INTEGRITY_FAILURE"], {"finding": finding_id, "missing": em_falta})
    orfas = [c for c in corr if not _resolves(eng, c)]
    if orfas:
        raise ReviewError("a correcção não existe: {} — `accepted` só com o que já corrige; "
                          "senão `delegated` ou `deferred`".format(", ".join(orfas)),
                          W["INTEGRITY_FAILURE"], {"finding": finding_id, "missing": orfas})
    cur = read_ledger(eng)
    d = cur["data"]
    ent = {"seq": len(d["dispositions"]) + 1, "finding": finding_id,
           "disposition": disposition, "rationale": rationale, "candidate_revision": cur_rev,
           "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    ent.update({k: v for k, v in (("evidence", evidence), ("envelope", envelope),
                                  ("owner", owner), ("impact", impact), ("to", to),
                                  ("corrected_by", corr)) if v})
    novo = dict(d, dispositions=d["dispositions"] + [ent])
    return _publish_ledger(eng, cur, novo, {_review_rel(rid): _digest(eng / _review_rel(rid)),
                                            CAND_PATH: _digest(eng / CAND_PATH)}, "dispose")


def diverge(eng, finding_ids, subject: str) -> dict:
    """Abre uma divergência material (dialéctica limitada). A quarta na mesma revisão já nasce
    `escalated`: o limite escala, nunca aceita (T30)."""
    eng = Path(eng)
    W = _W()
    _workflow(eng)
    if len(finding_ids) < 1 or not str(subject).strip():
        raise ReviewError("divergência sem achados ou sem assunto", W["INTEGRITY_FAILURE"], {})
    cur_rev = int(read_candidates(eng)["data"].get("revision") or 0)
    kinds, rs = set(), {}
    for fid in finding_ids:
        rid, rev, f = _finding(eng, fid)
        if rev["candidate_revision"] != cur_rev:
            raise ReviewError("{} é de um parecer stale".format(fid), W["STALE_INPUT"],
                              {"finding": fid})
        kinds.add(f["kind"])
        rs[_review_rel(rid)] = _digest(eng / _review_rel(rid))
    cur = read_ledger(eng)
    d = cur["data"]
    desta = [x for x in d["divergences"] if x["candidate_revision"] == cur_rev]
    div = {"id": "DIV-{:02d}".format(len(d["divergences"]) + 1), "findings": list(finding_ids),
           "subject": subject, "kind": "fact" if "fact" in kinds else "recommendation",
           "candidate_revision": cur_rev, "calls": 0, "status": "open", "history": []}
    if len(desta) >= MAX_DIVERGENCES:
        div.update(status="escalated", reason="limite de {} divergências por revisão".format(
            MAX_DIVERGENCES))
    novo = dict(d, divergences=d["divergences"] + [div])
    rs[CAND_PATH] = _digest(eng / CAND_PATH)
    return _publish_ledger(eng, cur, novo, rs, "diverge")


def dialectic_call(eng, div_id: str, outcome: str, synthesis: str = "",
                   locator: str = "") -> dict:
    """Regista uma chamada da ronda dialéctica. `synthesis_accepted` fecha como `synthesized`
    (um facto só com localizador); a segunda chamada sem síntese aceite → `escalated` (T30)."""
    eng = Path(eng)
    W = _W()
    _workflow(eng)
    cur = read_ledger(eng)
    d = cur["data"]
    div = next((x for x in d["divergences"] if x["id"] == div_id), None)
    if not div or div["status"] != "open":
        raise ReviewError("divergência {} não está aberta".format(div_id),
                          W["INTEGRITY_FAILURE"], {"divergence": div_id})
    if outcome not in ("synthesis_accepted", "contested"):
        raise ReviewError("resultado `{}` fora de synthesis_accepted|contested".format(outcome),
                          W["INTEGRITY_FAILURE"], {"divergence": div_id})
    if outcome == "synthesis_accepted" and not str(synthesis).strip():
        raise ReviewError("síntese aceite sem texto", W["INTEGRITY_FAILURE"],
                          {"divergence": div_id})
    if outcome == "synthesis_accepted" and div["kind"] == "fact" and not str(locator).strip():
        raise ReviewError("uma divergência de facto não se resolve por síntese sem "
                          "localizador — fica Conflicted ou escala", W["INTEGRITY_FAILURE"],
                          {"divergence": div_id, "code": "NO_LOCATOR"})
    nova = dict(div, calls=div["calls"] + 1,
                history=div["history"] + [{"call": div["calls"] + 1, "outcome": outcome}])
    if outcome == "synthesis_accepted":
        nova.update(status="synthesized", synthesis=synthesis)
        if locator:
            nova["locator"] = locator
    elif nova["calls"] >= MAX_CALLS:
        nova.update(status="escalated", reason="{} chamadas sem síntese aceite".format(
            MAX_CALLS))
    novo = dict(d, divergences=[nova if x["id"] == div_id else x for x in d["divergences"]])
    return _publish_ledger(eng, cur, novo, {CAND_PATH: _digest(eng / CAND_PATH)}, "dialectic")


def show_reviews(eng) -> dict:
    """Estado da revisão sobre a revisão corrente dos candidatos: pareceres `mandated` ·
    `current` · `stale`, achados com a última disposição, o que revalidar, divergências."""
    eng = Path(eng)
    cur_rev = int(read_candidates(eng)["data"].get("revision") or 0)
    led = read_ledger(eng)["data"]
    ultima = {}
    for x in led["dispositions"]:
        ultima[x["finding"]] = x
    out, abertos = [], []
    for rid, mand, rev in _reviews(eng):
        if not rev:
            out.append({"task_id": rid, "role": mand["role"], "state": "mandated",
                        "candidate_revision": mand["candidate_revision"]})
            continue
        state = "current" if rev["candidate_revision"] == cur_rev else "stale"
        fs = []
        mudou = _changed_candidates(eng, rev["candidate_revision"]) if state == "stale" else set()
        for f in rev["findings"]:
            disp = ultima.get(f["id"], {}).get("disposition", "")
            item = {"id": f["id"], "severity": f["severity"], "kind": f["kind"],
                    "target": f["target"], "disposition": disp or "open"}
            if state == "stale":
                alvo = set(O_ID_RE.findall(f["target"]))
                item["revalidate"] = not alvo or bool(alvo & mudou)
            elif disp not in CLOSING:
                abertos.append(f["id"])
            fs.append(item)
        out.append({"task_id": rid, "role": rev["role"], "state": state,
                    "candidate_revision": rev["candidate_revision"], "findings": fs,
                    "unanswered": [u["question"] for u in rev["unanswered"]]})
    return {"candidate_revision": cur_rev, "reviews": out, "open_findings": abertos,
            "divergences": [{k: v for k, v in x.items() if k != "history"}
                            for x in led["divergences"]]}


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:                                                   # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="candidatos e revisão independente (coordenador)")
    ap.add_argument("command", choices=["draft-candidates", "check-candidates",
                                        "publish-candidates", "show-candidates", "route",
                                        "mandate", "receive", "show-reviews", "dispose",
                                        "diverge", "dialectic-call"])
    ap.add_argument("--task", default="")
    ap.add_argument("--file", default="")
    ap.add_argument("--finding", action="append", default=[])
    ap.add_argument("--disposition", default="")
    ap.add_argument("--rationale", default="")
    ap.add_argument("--evidence", default="")
    ap.add_argument("--envelope", default="")
    ap.add_argument("--owner", default="")
    ap.add_argument("--impact", default="")
    ap.add_argument("--to", default="")
    ap.add_argument("--subject", default="")
    ap.add_argument("--divergence", default="")
    ap.add_argument("--outcome", default="")
    ap.add_argument("--synthesis", default="")
    ap.add_argument("--locator", default="")
    ap.add_argument("--corrected-by", action="append", default=[])
    ap.add_argument("--phase", default="options")
    ap.add_argument("--role", default="")
    ap.add_argument("--question", action="append", default=[])
    ap.add_argument("--knowledge", action="append", default=[])
    ap.add_argument("--objective", default="")
    ap.add_argument("--scope", action="append", default=[])
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
        elif a.command == "route":
            out, rc = route(eng, a.phase), 0
        elif a.command == "mandate":
            out = mandate(eng, a.role, a.question, a.knowledge, a.objective, a.scope)
            out = {k: v for k, v in out.items() if k != "receipt"} if not a.json else out
            rc = 0
        elif a.command == "receive":
            out = receive(eng, a.task, _load(Path(a.file), a.file))
            out, rc = {k: v for k, v in out.items() if k != "receipt" or a.json}, 0
        elif a.command == "show-reviews":
            out, rc = show_reviews(eng), 0
        elif a.command == "dispose":
            out = dispose(eng, (a.finding or [""])[0], a.disposition, a.rationale, a.evidence,
                          a.envelope, a.owner, a.impact, a.to, a.corrected_by)
            out, rc = {k: v for k, v in out.items() if k not in ("receipt", "data")}, 0
        elif a.command == "diverge":
            out = diverge(eng, a.finding, a.subject)
            out, rc = {k: v for k, v in out.items() if k not in ("receipt", "data")}, 0
        elif a.command == "dialectic-call":
            out = dialectic_call(eng, a.divergence, a.outcome, a.synthesis, a.locator)
            out, rc = {k: v for k, v in out.items() if k not in ("receipt", "data")}, 0
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
