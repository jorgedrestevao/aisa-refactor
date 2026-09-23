"""trace.py — a rastreabilidade vertical do âmbito entregue (handoff-v1 F6). Só leitura.

Constrói a cadeia `âmbito → requisito/regra → FC → nó do desenho → WP → aceitação/prova`
a partir das autoridades publicadas (`_design/scope.json`,
`_design/functional-contracts.json`,
`_design/work-packages.json`, o desenho aprovado, a SU) e reporta nos dois sentidos
(`docs/handoff-v1/plan/08_HANDOFF.md` → *Rastreabilidade vertical*):

    NO_CONTRACT            item incluído sem FC nem WP que o realize directamente
    NO_WORK                FC do âmbito, ou item incluído, sem WP
    NO_TEST                o trabalho que realiza um item não tem aceitação
    NO_DESIGN_REASON       WP que não realiza nada e não diz porquê
    PROOF_WITHOUT_WORK     obrigação de prova do desenho sem WP que a prove (T31)
    PROOF_WITHOUT_ACCEPTANCE  o WP que a prova não tem condição de aceitação (T31)
    VIABILITY_PROOF_OPEN   pergunta em aberto `proof_obligation` — pode invalidar a viabilidade
                           e por isso bloqueia o compromisso do âmbito (T34; `states.md`)
    UI_IN_HEADLESS         WP que realiza um ecrã num desenho headless (T37)

Exclusões autorizadas do âmbito não geram achado. O motor não escreve nada e não decide:
um achado é um facto de estrutura; se o requisito é material é juízo do dono.

Desenho: `docs/handoff-v1/F6/DESENHO.md` §2.
"""
from __future__ import annotations

import json
import re
import runpy
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CACHE: dict = {}
FC_RE = re.compile(r"^FC-\d{4}$")
J_RE = re.compile(r"^J-\d{4}$")
SU_ID_RE = re.compile(r"^[CAUXRM]-\d+$")
PO_SEL_RE = re.compile(r"proof_obligations\[([^\]]+)\]")


def _mod(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = runpy.run_path(str(_HERE / (name + ".py")))
    return _CACHE[name]


def _load(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _blueprint(eng: Path) -> dict:
    """O desenho aprovado; sem aprovação, a versão não-rascunho mais recente (dito)."""
    F, D = _mod("functional"), _mod("dashboard")
    rel = F["approved_blueprint"](eng)
    fonte = "aprovado"
    if not rel or not (eng / rel).is_file():
        vs = sorted(eng.glob("_blueprint/ux-blueprint_v*.yaml"),
                    key=lambda p: int(re.search(r"v(\d+)", p.name).group(1)))
        rel, fonte = "", "nenhum"
        for p in reversed(vs):
            obj, _i = D["yl_parse"](p.read_text(encoding="utf-8"))
            if isinstance(obj, dict) and not obj.get("draft"):
                rel, fonte = "_blueprint/" + p.name, "não aprovado — o mais recente"
                break
    if not rel:
        return {"rel": "", "fonte": fonte, "obj": {}}
    obj, _i = D["yl_parse"]((eng / rel).read_text(encoding="utf-8"))
    return {"rel": rel, "fonte": fonte, "obj": obj if isinstance(obj, dict) else {}}


def _headless(obj: dict) -> bool:
    arch = obj.get("architecture") if isinstance(obj.get("architecture"), dict) else {}
    exp = arch.get("experience") if isinstance(arch.get("experience"), dict) else {}
    return str(exp.get("mode") or "").strip() == "none" and not obj.get("screens")


def _po_index(sel: str, obligations: list):
    """O índice da obrigação que um selector `…proof_obligations[<i>|chave=valor]` aponta."""
    m = PO_SEL_RE.search(sel or "")
    if not m:
        return None
    disc = m.group(1)
    if disc.isdigit():
        i = int(disc)
        return i if 0 <= i < len(obligations) else None
    k, _, v = disc.partition("=")
    hits = [i for i, o in enumerate(obligations) if isinstance(o, dict) and str(o.get(k)) == v]
    return hits[0] if len(hits) == 1 else None


def _f(code: str, ref: str, detail: str, scope: str = "") -> dict:
    return {"code": code, "ref": ref, "scope": scope, "detail": detail}


def trace(eng) -> dict:
    eng = Path(eng)
    D = _mod("dashboard")
    scope = _load(eng / "_design/scope.json")
    fcdata = _load(eng / "_design/functional-contracts.json")
    inv = _load(eng / "_design/work-packages.json")
    fcs = {i["id"]: i for i in fcdata.get("items") or [] if isinstance(i, dict)}
    wps = [w for w in inv.get("items") or [] if isinstance(w, dict)]
    try:
        md = (eng / "shared-understanding.md").read_text(encoding="utf-8")
    except OSError:
        md = ""
    _h, rows, _s, _d = D["parse_su"](md)
    bp = _blueprint(eng)
    arch = bp["obj"].get("architecture") if isinstance(bp["obj"].get("architecture"), dict) else {}
    obligations = [o for o in arch.get("proof_obligations") or []]
    headless = _headless(bp["obj"])

    realized_by: dict = {}
    for w in wps:
        for r in w.get("realizes") or []:
            realized_by.setdefault(r, []).append(w)
    findings, chains = [], []

    for s in scope.get("items") or []:
        sid = s["id"]
        excluded = {e["ref"] for e in s.get("excludes") or []}
        in_scope_fcs = set()
        for inc in s.get("includes") or []:
            ref = inc["ref"]
            if ref in excluded:
                continue
            if J_RE.match(ref):
                via = [f for f, it in fcs.items() if it.get("journey_id") == ref]
            else:
                via = [f for f, it in fcs.items() if ref in (it.get("requirement_refs") or [])]
            via = [f for f in via if f not in excluded]
            in_scope_fcs.update(via)
            work = list(realized_by.get(ref, []))
            for f in via:
                work += [w for w in realized_by.get(f, []) if w not in work]
            chains.append({"scope": sid, "ref": ref, "fc": sorted(via),
                           "wp": sorted({w["id"] for w in work})})
            if not via and not realized_by.get(ref):
                findings.append(_f("NO_CONTRACT", ref, "incluído no âmbito sem FC e sem WP que o "
                                   "realize — nem excluído com autorização", sid))
            elif not work:
                findings.append(_f("NO_WORK", ref, "incluído no âmbito sem trabalho", sid))
            elif not any(w.get("acceptance") for w in work):
                findings.append(_f("NO_TEST", ref, "o trabalho que o realiza não tem aceitação",
                                   sid))
        for f, it in fcs.items():
            if it.get("scope_id") == sid and f not in excluded:
                in_scope_fcs.add(f)
        for f in sorted(in_scope_fcs):
            work = realized_by.get(f, [])
            if not work:
                findings.append(_f("NO_WORK", f, "FC do âmbito sem WP que o realize", sid))
            elif not any(any(a.get("fc") == f for a in w.get("acceptance") or [])
                         for w in work):
                findings.append(_f("NO_TEST", f, "nenhum WP tem aceitação sobre este FC", sid))

    for w in wps:
        na = w.get("not_applicable") or {}
        if not w.get("realizes") and not str(na.get("realizes") or "").strip():
            findings.append(_f("NO_DESIGN_REASON", w["id"], "WP sem motivo de desenho",
                               w.get("scope_id", "")))
        if headless and any("screens" in r for r in w.get("realizes") or []):
            findings.append(_f("UI_IN_HEADLESS", w["id"], "realiza um ecrã num desenho "
                               "headless", w.get("scope_id", "")))

    proofs = []
    for i, o in enumerate(obligations):
        claim = o.get("claim") if isinstance(o, dict) else str(o)
        by = [w for w in wps if any(_po_index(p, obligations) == i
                                    for p in w.get("proves") or [])]
        proofs.append({"index": i, "claim": claim, "level": (o or {}).get("level")
                       if isinstance(o, dict) else None,
                       "wp": [w["id"] for w in by],
                       "accepted": any(w.get("acceptance") for w in by)})
        if not by:
            findings.append(_f("PROOF_WITHOUT_WORK", "{}#architecture/proof_obligations[{}]"
                               .format(bp["rel"], i), "obrigação de prova sem WP: «{}»"
                               .format(claim)))
        elif not proofs[-1]["accepted"]:
            findings.append(_f("PROOF_WITHOUT_ACCEPTANCE", "{}#architecture/proof_obligations[{}]"
                               .format(bp["rel"], i), "o WP que a prova não tem aceitação"))

    viability = []
    for r in rows:
        if r.get("state") == "Unknown" and r.get("tipo") == "proof_obligation" and not (
                r.get("resolved") or r.get("parked") or r.get("retired")):
            viability.append({"id": r["id"], "claim": r.get("claim"),
                              "bloqueio": r.get("bloqueio")})
            findings.append(_f("VIABILITY_PROOF_OPEN", r["id"], "prova futura que pode invalidar "
                               "a viabilidade: bloqueia o compromisso, não é item de checklist"))

    return {"scope_revision": scope.get("revision"), "fc_revision": fcdata.get("revision"),
            "inventory_revision": inv.get("revision"),
            "blueprint": {"ref": bp["rel"], "source": bp["fonte"]},
            "applicability": {"ui": "not_applicable (headless)" if headless else "applicable"},
            "chains": chains, "proofs": proofs, "viability_blockers": viability,
            "findings": findings, "ok": not findings}


def main(argv=None) -> int:
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:                                                   # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="rastreabilidade vertical (só leitura)")
    ap.add_argument("command", choices=["show"])
    ap.add_argument("--engagement", required=True)
    a = ap.parse_args(argv)
    eng = Path(a.engagement)
    if not eng.is_dir():
        eng = Path("projects") / a.engagement
    out = trace(eng)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["ok"] else 4


if __name__ == "__main__":
    sys.exit(main())
