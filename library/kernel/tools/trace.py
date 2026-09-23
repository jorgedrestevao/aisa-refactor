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


# ------------------------------------------------------------------ derivados (T32)

WP_RE = re.compile(r"\bWP-\d{4}\b")
INV_REV_RE = re.compile(r"(?:invent[aá]rio|inventory|work-packages)\s*r(\d+)", re.I)
EFFORT_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:dias?|days?|horas?|hours?|semanas?|weeks?|"
                       r"person[- ]days?|pessoa[- ]dias?|pd)\b", re.I)


def derived_check(eng, text: str, kind: str = "estimate") -> dict:
    """A estimativa (`estimate`), a spec (`spec`) ou o backlog (`backlog`) contra o inventário:
    cada linha de tabela que cita `WP-NNNN` é uma unidade; a revisão do inventário citada tem
    de ser a corrente (DESENHO Q2). Estimativa: cada WP exactamente uma vez. Spec e backlog:
    cada WP pelo menos uma vez. Um WP citado que não existe é sempre achado. Nunca compara esforços."""
    eng = Path(eng)
    inv = _load(eng / "_design/work-packages.json")
    rev = inv.get("revision")
    ids = {w["id"] for w in inv.get("items") or [] if isinstance(w, dict)}
    linhas = [l for l in (text or "").splitlines() if l.lstrip().startswith("|")]
    contagem: dict = {}
    for l in linhas:
        for w in set(WP_RE.findall(l)):
            contagem[w] = contagem.get(w, 0) + 1
    out = []
    revs = {int(r) for r in INV_REV_RE.findall(text or "")}
    if not revs:
        out.append(_f("NO_INVENTORY_REVISION", kind, "não cita a revisão do inventário que leu"))
    elif revs != {rev}:
        out.append(_f("STALE_INVENTORY", kind, "cita inventário r{}; o corrente é r{}".format(
            "/r".join(str(r) for r in sorted(revs)), rev)))
    for w in sorted(set(contagem) - ids):
        out.append(_f("UNKNOWN_WP", w, "{} cita um WP que não existe no inventário".format(kind)))
    for w in sorted(ids - set(contagem)):
        out.append(_f({"estimate": "UNESTIMATED_WP", "spec": "MISSING_IN_SPEC"}.get(
            kind, "MISSING_IN_BACKLOG"), w,
                      "WP do inventário sem unidade em {}".format(kind)))
    if kind == "estimate":
        for w, n in sorted(contagem.items()):
            if n > 1 and w in ids:
                out.append(_f("DUPLICATE_ESTIMATE", w, "estimado {} vezes — esforço concorrente"
                              .format(n)))
    return {"kind": kind, "inventory_revision": rev, "units": contagem, "findings": out,
            "ok": not out}


def spec_effort_check(text: str) -> list:
    """Duração ou esforço numa linha de tabela da spec que cita `WP-NNNN`: o esforço é só da
    estimativa (Q2). Só as linhas do inventário — uma regra de negócio com «dias» não conta."""
    out = []
    for l in (text or "").splitlines():
        if l.lstrip().startswith("|") and WP_RE.search(l) and EFFORT_RE.search(l):
            out.append(_f("EFFORT_IN_SPEC", WP_RE.search(l).group(0),
                          "a linha do inventário na spec leva duração: «{}»".format(
                              EFFORT_RE.search(l).group(0))))
    return out


# ------------------------------------------------------------------ gate de âmbito (T33, N4)

def scope_gate(eng) -> dict:
    """`complete` · `partial` · `blocked`. Um bloqueio num item incluído bloqueia a entrega;
    um parcial só passa com exclusões autorizadas (garantido pelo `inventory.py`) e coerente:
    nenhum WP trabalha para o excluído nem depende de quem trabalha, e nenhum campo
    obrigatório do desenho fica sem quem o produza (N4)."""
    eng = Path(eng)
    F = _mod("functional")
    t = trace(eng)
    scope = _load(eng / "_design/scope.json")
    fcdata = _load(eng / "_design/functional-contracts.json")
    fcs = {i["id"]: i for i in fcdata.get("items") or [] if isinstance(i, dict)}
    wps = [w for w in _load(eng / "_design/work-packages.json").get("items") or []]
    show = F["show"](eng)["items"] if fcs else {}
    excluded = {e["ref"] for s in scope.get("items") or [] for e in s.get("excludes") or []}
    blockers = list(t["findings"])
    for f, v in show.items():
        if f in excluded:
            continue
        if not v["authorizable"]:
            blockers.append(_f("FC_NOT_AUTHORIZABLE", f, "lacunas ou conflitos: {}".format(
                ", ".join(sorted({g["code"] for g in v["gaps"] + v["conflicts"]})))))
        elif v["authorization"]["state"] != "current":
            blockers.append(_f("FC_NOT_AUTHORIZED", f, "autorização {}".format(
                v["authorization"]["state"])))
    try:
        md = (eng / "shared-understanding.md").read_text(encoding="utf-8")
    except OSError:
        md = ""
    for r in _mod("dashboard")["parse_su"](md)[1]:
        if r.get("state") == "Unknown" and r.get("bloqueio") == "blocks_all" and not (
                r.get("resolved") or r.get("parked") or r.get("retired")):
            blockers.append(_f("BLOCKS_ALL_OPEN", r["id"], "pergunta em aberto bloqueia tudo"))
    incoerente = []
    trabalha_excl = {w["id"] for w in wps if set(w.get("realizes") or []) & excluded}
    for w in sorted(trabalha_excl):
        incoerente.append(_f("WORK_FOR_EXCLUDED", w, "realiza um item excluído"))
    for w in wps:
        if w["id"] not in trabalha_excl and set(w.get("depends_on") or []) & trabalha_excl:
            incoerente.append(_f("DEPENDS_ON_EXCLUDED", w["id"], "depende de trabalho do "
                                 "excluído: {}".format(", ".join(sorted(
                                     set(w["depends_on"]) & trabalha_excl)))))
    bp = _blueprint(eng)
    campos = F["blueprint_index"](eng, bp["rel"]).get("fields", {}) if bp["rel"] else {}

    def produz(it):
        txt = " ".join(str(x) for x in it.get("postconditions") or [])
        return {"{}.{}".format(*m) for m in F["DOTTED_RE"].findall(txt)}
    incluidos = [it for f, it in fcs.items() if f not in excluded]
    for f in sorted(excluded & set(fcs)):
        for ref in sorted(produz(fcs[f])):
            campo = campos.get(ref) or {}
            if campo.get("required") in (True, "true", "yes") and not any(
                    ref in produz(i) for i in incluidos):
                incoerente.append(_f("REQUIRED_FIELD_WITHOUT_PRODUCER", ref, "obrigatório em "
                                     "{} e só {} (excluído) o produz".format(bp["rel"], f)))
    if blockers:
        estado = "blocked"
    elif excluded:
        estado = "partial" if not incoerente else "blocked"
    else:
        estado = "complete"
    return {"delivery": estado, "blockers": blockers, "incoherent": incoerente,
            "excluded": sorted(excluded)}


def main(argv=None) -> int:
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:                                                   # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="rastreabilidade vertical (só leitura)")
    ap.add_argument("command", choices=["show", "estimate-check", "backlog-check", "scope-gate"])
    ap.add_argument("--engagement", required=True)
    ap.add_argument("--file", default="", help="estimate-check/backlog-check: o deliverable")
    ap.add_argument("--spec", default="", help="estimate-check: a implementation-spec")
    a = ap.parse_args(argv)
    eng = Path(a.engagement)
    if not eng.is_dir():
        eng = Path("projects") / a.engagement
    if a.command in ("estimate-check", "backlog-check"):
        texto = (eng / a.file).read_text(encoding="utf-8") if a.file else ""
        out = derived_check(eng, texto, "estimate" if a.command == "estimate-check"
                            else "backlog")
        if a.spec:
            out["findings"] += spec_effort_check((eng / a.spec).read_text(encoding="utf-8"))
            out["ok"] = not out["findings"]
        ok = out["ok"]
    elif a.command == "scope-gate":
        out = scope_gate(eng)
        ok = out["delivery"] != "blocked"
    else:
        out = trace(eng)
        ok = out["ok"]
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
