"""functional.py — os contratos funcionais do engagement (handoff-v1 F4).

`_design/functional-contracts.json` (`handoff-functional/1`) é a autoridade do comportamento
TO-BE detalhado (`library/kernel/handoff-contract.md` → *Functional contract*). Só este motor
o publica, pelo coordenador (`operation.run`, com base e read-set), como o checkpoint da F2:
`_design/` é guardado pelo `pre-authority-guard` e não é rascunhável pelo `resolve.py`.

    draft    abre um rascunho em `_drafts/FCDRAFT-…/` (cópia da revisão corrente ou esqueleto)
    check    valida sem escrever: integridade (recusa) e completude (`BLOCKING_GAP`)
    publish  publica numa operação a revisão nova e a sua cópia imutável em `_design/history/`
    show     o estado por FC

Integridade falha fechada (`INTEGRITY_FAILURE`, nada se publica): schema, ids nunca
reutilizados, revisão +1, referências que resolvem, nenhum FC a redefinir um campo.
Completude não recusa: um FC incompleto é publicado com `BLOCKING_GAP` no seu âmbito e não
é autorizável (T20). O motor nunca preenche um campo.

Desenho: `docs/handoff-v1/F4/DESENHO.md` (Q2, §1).
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

FC_PATH = "_design/functional-contracts.json"
HISTORY_DIR = "_design/history"
DRAFTS_DIR = "_drafts"
DRAFT_PREFIX = "FCDRAFT-"
DRAFT_FILE = "functional-contracts.json"
DRAFT_MANIFEST = "_fcdraft.json"
DRAFT_SCHEMA = "aisa-fc-draft/1"
SCHEMA = "handoff-functional/1"
FC_RE = re.compile(r"^FC-\d{4}$")
SU_ID_RE = re.compile(r"^[CAUXRMD]-\d+$")
BLUEPRINT_RE = re.compile(r"^_blueprint/ux-blueprint_v(\d+)\.yaml$")

# O que um FC tem de dizer, ou declarar como não aplicável com motivo (02 §7).
ESSENTIAL = ("rule", "acceptance_examples", "actors", "trigger", "postconditions",
             "exceptions")
EXAMPLE_KINDS = ("positive", "negative", "boundary")
BLOCKING = ("blocks_all", "blocks_scope")

# Autorização (F4.2, DESENHO §2). O bloco que o dono aprova, em `decisions.md`.
AUTH_TITLE = "Contratos funcionais autorizados"
AUTH_HEAD_RE = re.compile(r"^##\s+(D-\d+)\s+—\s+" + AUTH_TITLE + r"\b[^\n]*$", re.M)
AUTH_ITEM_RE = re.compile(r"(FC-\d{4})\s*\(sha256\s+([0-9a-f]{64})\)")
VALIDATED_RE = re.compile(r"\*\*Validated by\*\*\s*:\s*(.+)")
OWNER_RE = re.compile(r"^owner\s*\((?P<quem>[^)]+)\)")
# Quem nunca autoriza pelo cliente (plano 05 F4 item 6): o executor, um agente, uma
# persona do conselho, um revisor. Lista fechada, lida por palavra, nunca por semelhança.
NOT_HUMAN = ("executor", "agente", "agent", "claude", "chairman", "persona", "revisor",
             "reviewer", "business-analyst", "operations-lead", "user-advocate",
             "data-steward", "compliance-officer", "cfo-lens", "solution-architect",
             "frame-reviewer", "fc-reviewer", "lens-coverage-reviewer", "[âmbito autorizado]")


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


class FunctionalError(Exception):
    def __init__(self, message: str, code: str, detail: dict | None = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or {}


# ------------------------------------------------------------------ leitura

def _digest(p: Path) -> str:
    return _O()["digest"](p)


def _load(p: Path, what: str):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise FunctionalError("{} ilegível — nada se escreve por cima".format(what),
                              _W()["INTEGRITY_FAILURE"], {"path": str(p), "detail": str(exc)})


def skeleton(eng: Path) -> dict:
    return {"schema_version": SCHEMA, "engagement_id": Path(eng).name, "revision": 0,
            "based_on": [], "retired_ids": [], "items": []}


def read_current(eng) -> dict:
    """`{data, digest}` — `data` é o esqueleto (revisão 0) quando ainda não há ficheiro."""
    eng = Path(eng)
    p = eng / FC_PATH
    dg = _digest(p)
    if not dg:
        return {"data": skeleton(eng), "digest": ""}
    data = _load(p, FC_PATH)
    if isinstance(data, dict) and data.get("schema_version") != SCHEMA:
        raise FunctionalError("contratos funcionais com schema `{}`; esta versão lê {}".format(
            data.get("schema_version"), SCHEMA), _W()["SCHEMA_UNSUPPORTED"], {"path": FC_PATH})
    return {"data": data, "digest": dg}


def _su_rows(eng: Path) -> dict:
    try:
        md = (eng / "shared-understanding.md").read_text(encoding="utf-8")
    except OSError:
        return {}
    _h, rows, _s, _d = _D()["parse_su"](md)
    return {r["id"]: r for r in rows}


def blueprint_index(eng: Path, rel: str) -> dict:
    """O que um FC pode apontar num desenho: domínios, campos `<domínio>.<campo>`
    (com as facetas), entidades, ecrãs, componentes e personas."""
    try:
        text = (eng / rel).read_text(encoding="utf-8")
    except OSError:
        return {}
    obj, _iss = _D()["yl_parse"](text)
    obj = obj if isinstance(obj, dict) else {}
    arch = obj.get("architecture") if isinstance(obj.get("architecture"), dict) else {}
    refs, fields = set(), {}
    for dom in arch.get("record_authority") or []:
        if not isinstance(dom, dict) or not dom.get("key"):
            continue
        refs.add(str(dom["key"]))
        for f in dom.get("fields") or []:
            if isinstance(f, dict) and f.get("name"):
                ref = "{}.{}".format(dom["key"], f["name"])
                refs.add(ref)
                fields[ref] = f
    for key, attr in (("entities", "name"), ("screens", "name"), ("personas", "name")):
        for n in obj.get(key) or []:
            if isinstance(n, dict) and n.get(attr):
                refs.add(str(n[attr]))
    for c in arch.get("compositions") or []:
        if isinstance(c, dict) and c.get("component"):
            refs.add(str(c["component"]))
    return {"refs": refs, "fields": fields, "draft": bool(obj.get("draft"))}


def _blueprint_of(data: dict) -> str:
    for b in data.get("based_on") or []:
        if isinstance(b, dict) and BLUEPRINT_RE.match(str(b.get("ref", ""))):
            return str(b["ref"])
    return ""


def item_sha256(item: dict) -> str:
    """A impressão digital de um FC: o item normalizado, sem o que a autorização escreve
    sobre ele (`authorization_ref`, `authorization`, `publication_status`). É ela que um
    bloco de autorização lista (F4.2)."""
    corpo = {k: v for k, v in item.items()
             if k not in ("authorization_ref", "authorization", "publication_status")}
    return hashlib.sha256(json.dumps(corpo, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ autorização (F4.2)

def validator_problem(validated_by: str) -> str:
    """"" quando o validador é um papel humano do lado do cliente; senão, porquê não."""
    v = (validated_by or "").strip()
    m = OWNER_RE.match(v)
    if not m:
        return "o validador não é `owner (<papel>, …)`"
    baixo = v.lower()
    for t in NOT_HUMAN:
        if re.search(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])", baixo):
            return "`{}` não autoriza pelo cliente".format(t)
    if "via askuserquestion" not in baixo and "dados de teste" not in baixo:
        return "a autorização não diz como foi pedida (via AskUserQuestion)"
    return ""


def authorization_blocks(eng) -> list:
    """Os blocos de autorização de FC em `decisions.md`, pela ordem do ficheiro."""
    try:
        md = (Path(eng) / "decisions.md").read_text(encoding="utf-8")
    except OSError:
        return []
    out = []
    heads = list(AUTH_HEAD_RE.finditer(md))
    for i, m in enumerate(heads):
        fim = md.find("\n## ", m.end())
        corpo = md[m.end(): fim if fim != -1 else len(md)]
        vm = VALIDATED_RE.search(corpo)
        rm = re.search(r"\*\*Revision\*\*\s*:\s*r?(\d+)", corpo)
        validado = vm.group(1).strip() if vm else ""
        out.append({"id": m.group(1),
                    "items": {fc: sha for fc, sha in AUTH_ITEM_RE.findall(corpo)},
                    "revision": int(rm.group(1)) if rm else None,
                    "validated_by": validado,
                    "problem": validator_problem(validado)})
    return out


def authorization_state(eng, item: dict, blocks: list | None = None) -> dict:
    """`current` — o bloco mais recente que lista este FC tem o `sha256` do item de agora e
    um validador humano; `stale` — lista-o com outra impressão (a revisão antiga não cobre
    a nova, T24); `invalid` — o validador não é humano; `missing` — nenhum bloco o lista."""
    blocks = authorization_blocks(eng) if blocks is None else blocks
    sha = item_sha256(item)
    for b in reversed(blocks):
        if item["id"] not in b["items"]:
            continue
        if b["problem"]:
            return {"state": "invalid", "block": b["id"], "reason": b["problem"]}
        if b["items"][item["id"]] == sha:
            return {"state": "current", "block": b["id"], "revision": b["revision"]}
        return {"state": "stale", "block": b["id"], "revision": b["revision"],
                "reason": "o FC mudou depois da autorização {} (r{})".format(
                    b["id"], b["revision"])}
    return {"state": "missing", "block": None}


def assumed_premises(eng, item: dict, su: dict | None = None) -> list:
    """As linhas `Assumed` em que o FC se apoia. Uma autorização não as confirma (T22):
    ficam listadas, e o motor nunca muda o estado de uma linha da SU."""
    su = _su_rows(Path(eng)) if su is None else su
    out = []
    for r in item.get("requirement_refs") or []:
        rid = r.split("#")[-1]
        if su.get(rid, {}).get("state") == "Assumed":
            out.append(rid)
    return out


def authorization_block(eng, fc_ids, validated_by: str, scope: str,
                        timestamp: str | None = None) -> str:
    """O texto do bloco, com as impressões calculadas pelo motor (nunca à mão). Recusa um
    validador que não é humano e um FC que não é autorizável — com lacunas ou inexistente."""
    eng = Path(eng)
    cur = read_current(eng)["data"]
    por_id = {it["id"]: it for it in cur.get("items") or []}
    prob = validator_problem(validated_by)
    if prob:
        raise FunctionalError("autorização recusada: " + prob, _W()["AUTHORIZATION_REQUIRED"],
                              {"validated_by": validated_by})
    gaps = completeness(eng, cur)
    linhas = []
    for fc in fc_ids:
        if fc not in por_id:
            raise FunctionalError("{} não existe na revisão corrente".format(fc),
                                  _W()["INTEGRITY_FAILURE"], {"fc": fc})
        if any(g["fc"] == fc for g in gaps):
            raise FunctionalError("{} tem lacunas — não é autorizável".format(fc),
                                  _W()["BLOCKING_GAP"], {"fc": fc})
        linhas.append("{} (sha256 {})".format(fc, item_sha256(por_id[fc])))
    did = "D-{:03d}".format(max([int(d[2:]) for d in _W()["_decision_ids"](eng)] or [0]) + 1)
    ts = timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return ("\n## {} — {} (functional-contracts r{:04d})\n\n"
            "- **Authorizes**: {}\n- **Revision**: r{:04d}\n- **Scope**: {}\n"
            "- **Validated by**: {}\n- **Timestamp**: {}\n").format(
                did, AUTH_TITLE, int(cur["revision"]), " · ".join(linhas),
                int(cur["revision"]), scope, validated_by, ts)


# ------------------------------------------------------------------ verificação

def _problem(code: str, fc: str, detail: str) -> dict:
    return {"code": code, "fc": fc, "detail": detail}


def integrity(eng, data: dict, prev: dict) -> list:
    """O que recusa a publicação. Lista vazia = íntegro."""
    eng = Path(eng)
    W = _W()
    out = []
    errors, _unknown = W["validate"](data, W["load_schema"]("handoff-functional"))
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
    ids = [it["id"] for it in data["items"]]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        out.append(_problem("DUPLICATE_ID", dup, "id repetido"))
    retired = set(data.get("retired_ids") or [])
    for i in sorted(set(prev.get("retired_ids") or []) - retired):
        out.append(_problem("RETIRED_DROPPED", i, "id retirado deixou de constar em retired_ids"))
    for i in sorted(set(ids) & retired):
        out.append(_problem("REUSED_ID", i, "id retirado reutilizado"))
    antes = {it["id"] for it in prev.get("items") or []}
    for i in sorted(antes - set(ids) - retired):
        out.append(_problem("SILENT_REMOVAL", i,
                            "FC desapareceu sem entrar em retired_ids"))
    su = _su_rows(eng)
    decisoes = set(W["_decision_ids"](eng))
    bp = _blueprint_of(data)
    index = {}
    if bp:
        if not (eng / bp).is_file():
            out.append(_problem("BLUEPRINT_MISSING", "", "{} não existe".format(bp)))
        else:
            sha = next((b.get("sha256") for b in data["based_on"] if b.get("ref") == bp), None)
            if sha and sha != _digest(eng / bp).split(":")[-1]:
                out.append(_problem("BLUEPRINT_CHANGED", "",
                                    "{} não é o que based_on regista".format(bp)))
            index = blueprint_index(eng, bp)
            if index.get("draft"):
                out.append(_problem("BLUEPRINT_DRAFT", "",
                                    "{} é um rascunho de opção (draft: true)".format(bp)))
    for it in data["items"]:
        fc = it["id"]
        for r in it.get("requirement_refs") or []:
            base = r.split("#")[-1] if "#" in r else r
            if not (SU_ID_RE.match(base) and base in su):
                out.append(_problem("DEAD_REF", fc, "requisito `{}` não é linha da SU".format(r)))
        ref = it.get("authorization_ref")
        if ref and ref.split("#")[-1] not in decisoes:
            out.append(_problem("DEAD_REF", fc, "autorização `{}` não existe em "
                                "decisions.md".format(ref)))
        precisa = list(it.get("architecture_refs") or []) + [
            i["field_ref"] for i in it.get("inputs") or []]
        if precisa and not bp:
            out.append(_problem("NO_BLUEPRINT", fc, "aponta o desenho sem o declarar em "
                                "based_on"))
        elif bp:
            for r in precisa:
                if r not in index.get("refs", set()):
                    out.append(_problem("DEAD_REF", fc, "`{}` não existe em {}".format(r, bp)))
    return out


def _open_blocking(su: dict) -> dict:
    return {rid: r for rid, r in su.items() if r.get("state") in ("Unknown", "Conflicted")
            and not r.get("resolved") and not r.get("parked") and not r.get("retired")
            and (r.get("bloqueio") or "").strip() in BLOCKING}


def completeness(eng, data: dict) -> list:
    """`BLOCKING_GAP` por FC: o que falta dizer. Não recusa a publicação."""
    su = _su_rows(Path(eng))
    abertas = _open_blocking(su)
    out = []
    for it in data.get("items") or []:
        fc, na = it["id"], it.get("not_applicable") or {}
        for campo in ESSENTIAL:
            v = it.get(campo)
            vazio = v is None or (isinstance(v, (str, list, dict)) and not v)
            if vazio and campo not in na:
                out.append(_problem("MISSING_" + campo.upper(), fc,
                                    "`{}` em falta e sem motivo em not_applicable".format(campo)))
        calc = it.get("calculation")
        if calc is not None:
            if not (isinstance(calc, dict) and str(calc.get("units") or "").strip()):
                out.append(_problem("MISSING_UNITS", fc, "cálculo sem unidades"))
            if not (isinstance(calc, dict) and str(calc.get("rounding") or "").strip()):
                out.append(_problem("MISSING_ROUNDING", fc,
                                    "cálculo sem regra de arredondamento — lacuna, nunca "
                                    "um valor escolhido"))
            kinds = {e.get("kind") for e in it.get("acceptance_examples") or []}
            for k in EXAMPLE_KINDS:
                if k not in kinds:
                    out.append(_problem("MISSING_EXAMPLE_" + k.upper(), fc,
                                        "cálculo sem exemplo `{}`".format(k)))
        for d in it.get("delegated_choices") or []:
            if not (isinstance(d, dict) and all(str(d.get(k) or "").strip()
                                                for k in ("envelope", "owner", "acceptance"))):
                out.append(_problem("DELEGATION_INCOMPLETE", fc,
                                    "escolha delegada sem envelope, dono ou aceitação"))
        for r in it.get("open_refs") or []:
            rid = r.split("#")[-1]
            if rid in abertas:
                out.append(_problem("OPEN_BLOCKER", fc, "{} está em aberto e bloqueia "
                                    "({})".format(rid, abertas[rid].get("bloqueio"))))
    return out


def check(eng, data: dict | None = None, prev: dict | None = None) -> dict:
    """Resposta estruturada (`handoff-response/1`) + o detalhe: `integrity` e `gaps`."""
    eng = Path(eng)
    W = _W()
    cur = read_current(eng)
    prev = cur["data"] if prev is None else prev
    data = prev if data is None else data
    prova = dict(prev, revision=int(prev.get("revision") or 0) - 1) if data is prev else prev
    inte = integrity(eng, data, prova)
    gaps = [] if inte else completeness(eng, data)
    if inte:
        resp = W["response"](False, W["INTEGRITY_FAILURE"],
                             [W["_reason"](p["detail"], "functional", p["code"]) for p in inte],
                             affected_ids=sorted({p["fc"] for p in inte if p["fc"]}),
                             input_revision=cur["digest"] or None)
    elif gaps:
        resp = W["response"](False, W["BLOCKING_GAP"],
                             [W["_reason"](p["detail"], "functional", p["code"]) for p in gaps],
                             affected_ids=sorted({p["fc"] for p in gaps}),
                             input_revision=cur["digest"] or None,
                             next_actions=[{"action": "completar os FC no rascunho",
                                            "reason": "o FC fica publicado mas não "
                                                      "autorizável"}])
    else:
        resp = W["response"](True, input_revision=cur["digest"] or None)
    return dict(resp, integrity=inte, gaps=gaps)


# ------------------------------------------------------------------ rascunho e publicação

def _profile_or_refuse(eng: Path) -> None:
    who = _W()["profile_of"](eng)
    if who["kind"] != _W()["HANDOFF"]:
        raise FunctionalError("contratos funcionais só num engagement handoff-v1",
                              _W()["UNSUPPORTED_PROFILE"], {"kind": who["kind"]})


def _reads(eng: Path) -> dict:
    rels = ["shared-understanding.md", "decisions.md"] + sorted(
        str(p.relative_to(eng)).replace(os.sep, "/")
        for p in (eng / "_blueprint").glob("ux-blueprint_v*.yaml"))
    return {r: _digest(eng / r) for r in rels}


def draft(eng) -> dict:
    eng = Path(eng)
    _profile_or_refuse(eng)
    cur = read_current(eng)
    semente = "{}|{}".format(time.time_ns(), os.getpid())
    did = DRAFT_PREFIX + hashlib.sha256(semente.encode("utf-8")).hexdigest()[:12]
    d = eng / DRAFTS_DIR / did
    d.mkdir(parents=True)
    corpo = dict(cur["data"], revision=int(cur["data"].get("revision") or 0) + 1)
    (d / DRAFT_FILE).write_text(json.dumps(corpo, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8", newline="\n")
    man = {"schema_version": DRAFT_SCHEMA, "id": did, "base": cur["digest"],
           "reads": _reads(eng), "published": None,
           "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    _O()["_atomic_write"](d / DRAFT_MANIFEST, json.dumps(man, ensure_ascii=False, indent=2))
    return {"draft": did, "path": str(d / DRAFT_FILE), "revision": corpo["revision"]}


def _read_draft(eng: Path, did: str) -> tuple:
    d = eng / DRAFTS_DIR / did
    if not did.startswith(DRAFT_PREFIX) or not (d / DRAFT_MANIFEST).is_file():
        raise FunctionalError("rascunho inexistente: {}".format(did), "DRAFT_MISSING",
                              {"draft": did})
    return _load(d / DRAFT_MANIFEST, DRAFT_MANIFEST), _load(d / DRAFT_FILE, DRAFT_FILE)


def publish(eng, draft_id: str) -> dict:
    """Uma operação: a revisão nova e a sua cópia imutável. A frescura vem antes da
    integridade — um rascunho sobre uma base velha é `STALE_INPUT`, não um erro dele."""
    eng = Path(eng)
    W, O = _W(), _O()
    _profile_or_refuse(eng)
    man, data = _read_draft(eng, draft_id)
    if man.get("published"):
        # Repetir depois de um sucesso sem resposta devolve o mesmo recibo, sem efeitos
        # (F2, T13) — nunca um `STALE_INPUT` contra a base que ele próprio mudou.
        prior = O["read_receipt"](eng, man["published"])
        if prior:
            gaps = completeness(eng, data)
            return {"operation_id": man["published"], "revision": data["revision"],
                    "history": "{}/functional-contracts.r{:04d}.json".format(
                        HISTORY_DIR, int(data["revision"])),
                    "receipt": prior, "replayed": True, "gaps": gaps,
                    "code": _W()["BLOCKING_GAP"] if gaps else None}
    cur = read_current(eng)
    if man["base"] != cur["digest"]:
        raise FunctionalError("os contratos funcionais mudaram depois do rascunho — abrir "
                              "um rascunho novo", W["STALE_INPUT"], {"draft": draft_id})
    mudou = sorted(r for r, dg in (man.get("reads") or {}).items() if _digest(eng / r) != dg)
    if mudou:
        raise FunctionalError("inputs mudaram depois do rascunho: {}".format(", ".join(mudou)),
                              W["STALE_INPUT"], {"draft": draft_id, "paths": mudou})
    res = check(eng, data, cur["data"])
    if res["integrity"]:
        raise FunctionalError("o rascunho viola a integridade dos contratos funcionais: " +
                              "; ".join("{} {}".format(p["fc"], p["detail"]).strip()
                                        for p in res["integrity"]),
                              W["INTEGRITY_FAILURE"], {"draft": draft_id,
                                                       "problems": res["integrity"]})
    texto = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    hist = "{}/functional-contracts.r{:04d}.json".format(HISTORY_DIR, int(data["revision"]))
    op_id = "functional-{}".format(hashlib.sha256(
        (cur["digest"] + texto).encode("utf-8")).hexdigest()[:16])
    recibo = O["run"](eng, op_id, {FC_PATH: texto, hist: texto},
                      expected={FC_PATH: cur["digest"], hist: ""},
                      read_set=man.get("reads") or {})
    man["published"] = op_id
    O["_atomic_write"](eng / DRAFTS_DIR / draft_id / DRAFT_MANIFEST,
                       json.dumps(man, ensure_ascii=False, indent=2))
    return {"operation_id": op_id, "revision": data["revision"], "history": hist,
            "receipt": recibo, "gaps": res["gaps"], "code": res["code"]}


def show(eng) -> dict:
    eng = Path(eng)
    cur = read_current(eng)
    data = cur["data"]
    gaps = completeness(eng, data)
    blocks = authorization_blocks(eng)
    su = _su_rows(eng)
    por_fc = {}
    for it in data.get("items") or []:
        auth = authorization_state(eng, it, blocks)
        por_fc[it["id"]] = {
            "purpose": it.get("purpose"), "scope_id": it.get("scope_id"),
            "semantic_origin": it.get("semantic_origin"),
            "publication_status": it.get("publication_status"),
            "sha256": item_sha256(it),
            "gaps": [g for g in gaps if g["fc"] == it["id"]],
            "authorization": auth,
            "assumed_premises": assumed_premises(eng, it, su),
            "authorizable": not any(g["fc"] == it["id"] for g in gaps)}
    return {"revision": data.get("revision"), "digest": cur["digest"],
            "blueprint": _blueprint_of(data), "items": por_fc,
            "retired_ids": data.get("retired_ids") or []}


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:                                                   # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="contratos funcionais (publica pelo coordenador)")
    ap.add_argument("command", choices=["draft", "check", "publish", "show",
                                        "authorization-block"])
    ap.add_argument("--fc", action="append", default=[])
    ap.add_argument("--validated-by", default="")
    ap.add_argument("--scope", default="")
    ap.add_argument("--engagement", required=True)
    ap.add_argument("--draft", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    eng = Path(a.engagement)
    if not eng.is_dir():
        eng = Path("projects") / a.engagement
    W, O = _W(), _O()
    try:
        if a.command == "draft":
            out, rc = draft(eng), 0
        elif a.command == "check":
            data = _read_draft(eng, a.draft)[1] if a.draft else None
            out = check(eng, data)
            rc = 0 if out["ok"] else (4 if out["code"] == W["BLOCKING_GAP"] else 1)
        elif a.command == "publish":
            out = publish(eng, a.draft)
            out = {k: v for k, v in out.items() if k != "receipt"} if not a.json else out
            rc = 0
        elif a.command == "authorization-block":
            print(authorization_block(eng, a.fc, a.validated_by, a.scope))
            return 0
        else:
            out, rc = show(eng), 0
    except FunctionalError as exc:
        print(json.dumps(W["response"](False, exc.code if exc.code in W["CODES"]
                                       else W["INTEGRITY_FAILURE"],
                                       [W["_reason"](str(exc), "functional", exc.code)]),
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
