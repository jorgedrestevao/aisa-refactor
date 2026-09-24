"""impact.py — o raio de impacto de uma mudança e o que ficou desactualizado (handoff-v1 F7).
Só leitura.

Lê as dependências que os artefactos publicados JÁ registam — nenhum grafo novo, nenhum
registo, nenhum booleano escrito (DESENHO F7, Q1: o `stale` deriva-se em cada leitura, como o
coverage §10, e por isso não diverge das fontes):

    linha da SU → FC          `requirement_refs`, `open_refs`, `proof_refs` (ou qualquer
                              referência exacta a uma linha dentro do item)
    linha da SU → âmbito      `includes` / `excludes`
    linha da SU → WP          `realizes` (requisito realizado directamente)
    linha da SU → candidato   `premise_refs`, `source_refs`, `impact_refs`
    linha da SU → desenho     `su_refs` de um nó do desenho
    FC → WP                   `realizes`
    candidato → parecer       o parecer sobre a revisão corrente dos candidatos
    unidade do pack → parecer `knowledge_refs` do mandato, com `sha256`

Mudança semântica de uma linha (Q2): `state`, `criticidade`, `resolved`, retirada — os
campos que já movem o gate no grafo (`graph.GATE_FIELDS`) e o marcador da P-21. Texto
editado no sítio é editorial: não abre nada; a revisão de bytes (`based_on.sha256`) continua
exacta e reporta-se à parte. `verificado_em` renovado não é mudança.

Para ver uma mudança de `state`/`criticidade` feita no sítio, o dependente precisa de saber o
que citou: `functional.py`, `inventory.py` e `review.py` juntam a `based_on`, ao publicar,
`shared-understanding.md#<id>` com a impressão (`row_basis`) de cada linha citada. Um
artefacto publicado antes disso só vê resolvida, retirada e inexistente — e di-lo
(`unverified`).

Achados de `stale`:

    ROW_RESOLVED      a linha citada foi resolvida (→ as sucessoras)
    ROW_WITHDRAWN     a linha citada foi retirada (P-21)
    ROW_MISSING       a linha citada não existe na SU
    ROW_CHANGED       `state`/`criticidade` diferentes do que o dependente registou
    VIA_CONTRACT      WP que realiza um FC desactualizado (transitivo)
    VIA_CANDIDATE     parecer sobre um candidato desactualizado (transitivo)
    KNOWLEDGE_CHANGED unidade do pack ou da memória que o mandato consumiu mudou

Desenho: `docs/handoff-v1/F7/DESENHO.md` §1.
"""
from __future__ import annotations

import hashlib
import json
import re
import runpy
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CACHE: dict = {}
SU_FILE = "shared-understanding.md"
SU_ID_RE = re.compile(r"^[CAUXRM]-\d+$")
FC_RE = re.compile(r"^FC-\d{4}$")
FC_PATH = "_design/functional-contracts.json"
SCOPE_PATH = "_design/scope.json"
WP_PATH = "_design/work-packages.json"
CAND_PATH = "_design/candidates.json"
REVIEWS_DIR = "_design/reviews"
ROW_FIELDS = ("state", "criticidade", "resolved", "retired")
SEMANTIC = ("ROW_RESOLVED", "ROW_WITHDRAWN", "ROW_MISSING", "ROW_CHANGED")
BP_SECTIONS_KEYS = ("id", "name", "key", "component")


def _mod(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = runpy.run_path(str(_HERE / (name + ".py")))
    return _CACHE[name]


def _load(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _digest(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return ""


def su_rows(eng: Path, md: str | None = None) -> dict:
    if md is None:
        try:
            md = (Path(eng) / SU_FILE).read_text(encoding="utf-8")
        except OSError:
            return {}
    return {r["id"]: r for r in _mod("dashboard")["parse_su"](md)[1] if r.get("id")}


# ------------------------------------------------------------ impressão por linha

def row_basis(row: dict) -> dict:
    """O que de uma linha move o gate (Q2) — nunca o texto."""
    return {"state": row.get("state") or "", "criticidade": row.get("criticidade") or "",
            "resolved": bool(row.get("resolved")), "retired": bool(row.get("retired"))}


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True)
                          .encode("utf-8")).hexdigest()


def _su_id(s) -> str:
    """O id da linha se `s` é uma referência exacta a uma linha (`C-003`,
    `shared-understanding.md#C-003`, `#C-003`); senão vazio. Prosa nunca casa."""
    if not isinstance(s, str):
        return ""
    s = s.strip()
    if "#" in s:
        head, tail = s.rsplit("#", 1)
        return tail if head in ("", SU_FILE) and SU_ID_RE.match(tail) else ""
    return s if SU_ID_RE.match(s) else ""


def cited_rows(obj) -> list:
    """As linhas que um item (ou artefacto) cita por referência exacta, em qualquer campo."""
    out = set()

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        else:
            rid = _su_id(x)
            if rid:
                out.add(rid)
    walk(obj)
    return sorted(out)


def with_row_basis(data: dict, rows: dict) -> dict:
    """`data` com a impressão de cada linha citada em `based_on` — chamado por quem publica,
    sobre a SU que o rascunho leu (o read-set garante que é a mesma). As entradas
    `shared-understanding.md#<id>` anteriores saem; as outras ficam como estavam."""
    corpo = {k: v for k, v in data.items() if k != "based_on"}
    fora = [b for b in data.get("based_on") or []
            if not (isinstance(b, dict) and str(b.get("ref", "")).startswith(SU_FILE + "#"))]
    for rid in cited_rows(corpo):
        if rid in rows:
            b = row_basis(rows[rid])
            fora.append({"ref": "{}#{}".format(SU_FILE, rid), "sha256": _sha(b), "row": b})
    return dict(data, based_on=fora)


def _recorded(data: dict) -> dict:
    fora = {}
    for b in data.get("based_on") or []:
        if isinstance(b, dict) and str(b.get("ref", "")).startswith(SU_FILE + "#"):
            fora[str(b["ref"]).split("#", 1)[1]] = b.get("row") or {}
    return fora


# ------------------------------------------------------------ dependências

def _bp_nodes(eng: Path) -> tuple:
    """(versão, [(chave do nó, [linhas])]) do desenho que o `trace` considera."""
    bp = _mod("trace")["_blueprint"](eng)
    nodes = []

    def walk(x, path):
        if isinstance(x, dict):
            refs = x.get("su_refs")
            if isinstance(refs, list):
                ids = [r for r in (_su_id(str(i)) for i in refs) if r]
                if ids:
                    nodes.append((path, ids))
            for k, v in x.items():
                if k != "su_refs":
                    walk(v, "{}/{}".format(path, k) if path else k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                chave = next((k for k in BP_SECTIONS_KEYS
                              if isinstance(v, dict) and isinstance(v.get(k), str)), None)
                walk(v, "{}[{}={}]".format(path, chave, v[chave]) if chave
                     else "{}[{}]".format(path, i))
    walk(bp["obj"], "")
    return bp["rel"], nodes


def edges(eng) -> list:
    """Cada dependência registada: `{src, dst, via, artefact}`. `src` é uma linha, um FC,
    um candidato ou uma unidade de conhecimento; `dst` é quem depende."""
    eng = Path(eng)
    out = []

    def add(src, dst, via, art):
        out.append({"src": src, "dst": dst, "via": via, "artefact": art})
    for path, kind in ((FC_PATH, "FC"), (SCOPE_PATH, "SCOPE"), (WP_PATH, "WP"),
                       (CAND_PATH, "O")):
        for it in _load(eng / path).get("items") or []:
            if not isinstance(it, dict) or not it.get("id"):
                continue
            for rid in cited_rows(it):
                add(rid, it["id"], "row", path)
            if kind == "WP":
                for r in it.get("realizes") or []:
                    if FC_RE.match(str(r)):
                        add(r, it["id"], "realizes", path)
    rel, nodes = _bp_nodes(eng)
    for chave, ids in nodes:
        for rid in ids:
            add(rid, "{}#{}".format(rel, chave), "su_refs", rel)
    cand_rev = int(_load(eng / CAND_PATH).get("revision") or 0)
    for p in sorted((eng / REVIEWS_DIR).glob("REV-*.mandate.json")):
        mand = _load(p)
        rid = mand.get("task_id") or p.name.split(".", 1)[0]
        if int(mand.get("candidate_revision") or -1) == cand_rev:
            for it in _load(eng / CAND_PATH).get("items") or []:
                if isinstance(it, dict) and it.get("id"):
                    add(it["id"], rid, "candidate_revision", str(p.relative_to(eng)))
        for k in mand.get("knowledge_refs") or []:
            if isinstance(k, dict) and k.get("ref"):
                add("knowledge:" + str(k["ref"]), rid, "knowledge_refs",
                    str(p.relative_to(eng)))
    return out


# ------------------------------------------------------------ stale

def _excluded(eng: Path) -> set:
    return {e.get("ref") for s in _load(eng / SCOPE_PATH).get("items") or []
            for e in s.get("excludes") or [] if isinstance(e, dict)}


def _f(code, ref, cause, chain, detail, artefact, **extra):
    d = {"code": code, "ref": ref, "cause": cause, "chain": chain, "detail": detail,
         "artefact": artefact}
    d.update(extra)
    return d


def _row_finding(rid, row, recorded):
    """(código, detalhe) de uma linha citada, ou None se nada mudou no que move o gate."""
    if row is None:
        return "ROW_MISSING", "`{}` não existe na SU".format(rid)
    if row.get("retired"):                      # antes de `resolved`: a retirada também o põe
        return "ROW_WITHDRAWN", "`{}` foi retirada (P-21)".format(rid)
    if row.get("resolved"):
        suc = ", ".join(row.get("resolved_to") or []) or "sem sucessora nomeada"
        return "ROW_RESOLVED", "`{}` foi resolvida → {}".format(rid, suc)
    if recorded:
        agora = row_basis(row)
        mud = ["{} {} → {}".format(k, recorded.get(k) or "—", agora[k] or "—")
               for k in ("state", "criticidade") if recorded.get(k, "") != agora[k]]
        if mud:
            return "ROW_CHANGED", "`{}`: {}".format(rid, "; ".join(mud))
    return None


def stale(eng) -> dict:
    """O que depende, hoje, de uma premissa que mudou — com a cadeia. Nada se escreve."""
    eng = Path(eng)
    rows = su_rows(eng)
    excl = _excluded(eng)
    findings, unverified = [], []
    por_dep = {}
    for path in (FC_PATH, SCOPE_PATH, WP_PATH, CAND_PATH):
        data = _load(eng / path)
        rec = _recorded(data)
        for it in data.get("items") or []:
            if not isinstance(it, dict) or not it.get("id"):
                continue
            for rid in cited_rows(it):
                achado = _row_finding(rid, rows.get(rid), rec.get(rid))
                if rid in rows and rid not in rec and not achado:
                    unverified.append({"ref": it["id"], "row": rid, "artefact": path})
                if achado:
                    f = _f(achado[0], it["id"], rid, [rid, it["id"]], achado[1], path,
                           excluded=it["id"] in excl)
                    findings.append(f)
                    por_dep.setdefault(it["id"], []).append(f)
    rel, nodes = _bp_nodes(eng)
    for chave, ids in nodes:
        dep = "{}#{}".format(rel, chave)
        for rid in ids:
            achado = _row_finding(rid, rows.get(rid), None)
            if achado:
                findings.append(_f(achado[0], dep, rid, [rid, dep], achado[1], rel))
    # transitivo: FC → WP; candidato → parecer. `depends_on` é sequência, não premissa: um WP
    # que só depende de outro não fica desactualizado por isso (T41: preservar o não afectado).
    for w in _load(eng / WP_PATH).get("items") or []:
        for fc in w.get("realizes") or []:
            for base in por_dep.get(fc, []):
                findings.append(_f("VIA_CONTRACT", w["id"], fc, base["chain"] + [w["id"]],
                                   "realiza {} ({})".format(fc, base["detail"]), WP_PATH,
                                   excluded=fc in excl))
    cand = _load(eng / CAND_PATH)
    cand_rev = int(cand.get("revision") or 0)
    for p in sorted((eng / REVIEWS_DIR).glob("REV-*.mandate.json")):
        mand = _load(p)
        rid = mand.get("task_id") or p.name.split(".", 1)[0]
        art = str(p.relative_to(eng))
        if int(mand.get("candidate_revision") or -1) == cand_rev:
            for it in cand.get("items") or []:
                for base in por_dep.get(it.get("id"), []):
                    findings.append(_f("VIA_CANDIDATE", rid, it["id"],
                                       base["chain"] + [rid], "revê {} ({})".format(
                                           it["id"], base["detail"]), art))
        repo = Path(_mod("review")["REPO"])
        for k in mand.get("knowledge_refs") or []:
            if isinstance(k, dict) and k.get("ref") and k.get("sha256") and \
                    _digest(repo / k["ref"]) != str(k["sha256"]).split(":")[-1]:
                findings.append(_f("KNOWLEDGE_CHANGED", rid, k["ref"], [k["ref"], rid],
                                   "`{}` mudou depois do mandato".format(k["ref"]), art))
    return {"stale": bool(findings), "findings": findings, "unverified": unverified,
            "affected": sorted({f["ref"] for f in findings}), "bytes": byte_revisions(eng)}


def blocking(eng, refs=None) -> list:
    """Os achados que bloqueiam a versão final (Q3): FC, âmbito e WP fora das exclusões
    autorizadas. `refs` restringe a esses dependentes (o render só olha para os FC que cita).
    Candidatos, pareceres e nós do desenho informam — o `/status` mostra-os, não bloqueiam."""
    alvo = set(refs) if refs is not None else None
    return [f for f in stale(eng)["findings"]
            if f["artefact"] in (FC_PATH, SCOPE_PATH, WP_PATH) and not f.get("excluded")
            and (alvo is None or f["ref"] in alvo)]


def byte_revisions(eng) -> list:
    """A revisão de bytes, exacta, de cada ficheiro que um artefacto registou em `based_on`
    com `sha256`. Informa; nunca abre nada (T42): um byte mudado sem mudança nas linhas
    citadas é editorial."""
    eng = Path(eng)
    out = []
    for path in (FC_PATH, SCOPE_PATH, WP_PATH, CAND_PATH):
        for b in _load(eng / path).get("based_on") or []:
            if not isinstance(b, dict) or "#" in str(b.get("ref", "")) or not b.get("sha256"):
                continue
            agora = _digest(eng / b["ref"])
            gravado = str(b["sha256"]).split(":")[-1]
            out.append({"artefact": path, "ref": b["ref"], "recorded": gravado, "now": agora,
                        "changed": agora != gravado})
    return out


def impact(eng, changed) -> dict:
    """O raio de uma mudança ANTES de a publicar: quem depende, directa e transitivamente,
    das linhas `changed`. Estrutura: dependências registadas. Texto livre (frame, options,
    síntese): as citações por texto do `resolve.cited_by` — candidatos, não veredicto."""
    eng = Path(eng)
    alvo = sorted({c for c in changed or [] if c})
    es = edges(eng)
    directos = [e for e in es if e["src"] in alvo and e["via"] in ("row", "su_refs")]
    vistos = {e["dst"] for e in directos}
    trans, fila = [], list(vistos)
    while fila:
        n = fila.pop()
        for e in es:
            if e["src"] == n and e["via"] in ("realizes", "candidate_revision") \
                    and e["dst"] not in vistos:
                vistos.add(e["dst"])
                trans.append(e)
                fila.append(e["dst"])
    texto = _mod("resolve")["cited_by"](eng, alvo)
    todos = {e["dst"] for e in es if e["via"] in ("row", "su_refs", "realizes",
                                                   "candidate_revision")}
    return {"changed": alvo, "direct": directos, "transitive": trans,
            "affected": sorted(vistos), "unaffected": sorted(todos - vistos),
            "text_citations": {k: v for k, v in texto.items() if v},
            "verdict": "estrutura: dependências registadas; texto: candidatos — o julgamento "
                       "por dependente de texto livre é de quem lê"}


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:                                                   # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="raio de impacto e stale derivado (só leitura)")
    ap.add_argument("command", choices=["stale", "impact", "edges"])
    ap.add_argument("--engagement", required=True)
    ap.add_argument("--changed", nargs="*", default=[], help="impact: as linhas que mudam")
    a = ap.parse_args(argv)
    eng = Path(a.engagement)
    if not eng.is_dir():
        eng = _HERE.parents[2] / "projects" / a.engagement
    if a.command == "stale":
        r = stale(eng)
    elif a.command == "impact":
        r = impact(eng, a.changed)
    else:
        r = {"edges": edges(eng)}
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 1 if a.command == "stale" and r["stale"] else 0


if __name__ == "__main__":
    sys.exit(main())
