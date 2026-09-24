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

Dependências fixadas e revalidação explícita (auditoria externa de 2026-09-24, A3/A5;
`docs/handoff-v1/F7/CORRECAO-AUDITORIA.md`). Um sha diferente prova que o conteúdo mudou; não
diz se a mudança é editorial. Por isso cada artefacto do desenho fixa em `based_on` o que
consome — o sha do desenho (FC e WP), a impressão de cada FC que um WP realiza, a impressão de
cada linha citada — e a leitura confere-o, além da publicação:

    BASIS_CHANGED       o ficheiro do desenho fixado mudou (o mesmo caminho, outro conteúdo)
    CONTRACT_CHANGED    o FC que um WP realiza já não tem a impressão que o WP fixou
    DEPENDENCY_UNPINNED o artefacto consome algo que não fixou: não se prova que está actual
    HISTORY_MISMATCH    o artefacto não é a revisão que o coordenador publicou no histórico
    PIN_UNREVALIDATED   no histórico, uma dependência mudou de impressão sem avaliação registada

Mover uma dependência exige uma avaliação registada no próprio artefacto (`revalidations`):
por item, `still_valid` (conteúdo igual) ou `updated` (conteúdo mudou), o texto da avaliação e
o papel de quem avaliou; o motor preenche de/para e data, e os registos só se acrescentam.
Trocar o hash, sozinho, não revalida nada: o publicador recusa (`REVALIDATION_REQUIRED`) e a
leitura apanha a troca feita por fora do motor. `updated` num FC continua a pedir nova
autorização do dono (a impressão do item mudou); `still_valid` não reabre decisões.

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
DESIGN_RE = re.compile(r"^_blueprint/ux-blueprint_v\d+\.yaml$")
# Os artefactos cujas dependências só se movem com uma avaliação registada. Os candidatos
# ficam de fora: uma revisão nova dos candidatos já obriga a pareceres novos (T26).
PINNED = (FC_PATH, SCOPE_PATH, WP_PATH)
HISTORY_STEM = {FC_PATH: "_design/history/functional-contracts",
                SCOPE_PATH: "_design/history/scope",
                WP_PATH: "_design/history/work-packages"}
VERDICTS = ("still_valid", "updated")
PIN_CODES = ("BASIS_CHANGED", "CONTRACT_CHANGED", "DEPENDENCY_UNPINNED", "HISTORY_MISMATCH",
             "PIN_UNREVALIDATED")


def _mod(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = runpy.run_path(str(_HERE / (name + ".py")))
    return _CACHE[name]


def _load(p: Path) -> dict:
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    prob = _mod("workflow")["schema_problem"](p, data)       # F7: versão fora da tabela
    if prob:
        raise _mod("workflow")["SchemaError"](prob, str(p))
    return data


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
    findings += pin_findings(eng) + history_findings(eng)
    return {"stale": bool(findings), "findings": findings, "unverified": unverified,
            "affected": sorted({f["ref"] for f in findings}), "bytes": byte_revisions(eng)}


def blocking(eng, refs=None) -> list:
    """Os achados que bloqueiam a versão final (Q3): FC, âmbito e WP fora das exclusões
    autorizadas. `refs` restringe a esses dependentes (o render só olha para os FC que cita).
    Candidatos, pareceres e nós do desenho informam — o `/status` mostra-os, não bloqueiam."""
    alvo = set(refs) if refs is not None else None
    return [f for f in stale(eng)["findings"]
            if f["artefact"] in (FC_PATH, SCOPE_PATH, WP_PATH) and not f.get("excluded")
            and (alvo is None or f["ref"] in alvo
                 or (f.get("document_level") and f["artefact"] == FC_PATH))]


def byte_revisions(eng) -> list:
    """A revisão de bytes, exacta, de cada ficheiro que um artefacto registou em `based_on`
    com `sha256`. Informa. O que bloqueia é `pin_findings` (BASIS_CHANGED): um sha mudado
    prova a mudança mas não a classifica — editorial ou material decide-o uma avaliação
    registada, nunca este leitor (auditoria A5; T42 substituído)."""
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


# ------------------------------------------------------------ dependências fixadas

def item_fingerprint(path: str, item: dict) -> str:
    """A impressão de um item: a do FC (sem os campos que a autorização escreve), ou o item
    inteiro, canónico, para âmbito e WP."""
    if path == FC_PATH:
        return _mod("functional")["item_sha256"](item)
    return _sha(item)


def pins(data: dict) -> dict:
    """`ref → sha256` de cada entrada de `based_on` que fixa uma dependência."""
    out = {}
    for b in data.get("based_on") or []:
        if isinstance(b, dict) and b.get("ref") and b.get("sha256"):
            out[str(b["ref"])] = str(b["sha256"]).split(":")[-1]
    return out


def design_file(ref) -> str:
    """O ficheiro do desenho de `ref` (`<ficheiro>` ou `<ficheiro>#<selector>`); senão vazio."""
    head = str(ref or "").split("#", 1)[0]
    return head if DESIGN_RE.match(head) else ""


def _items(data: dict) -> list:
    return [it for it in data.get("items") or [] if isinstance(it, dict) and it.get("id")]


def _fc_refs(it: dict) -> set:
    out = {str(r) for r in it.get("realizes") or [] if FC_RE.match(str(r))}
    out |= {str(a["fc"]) for a in it.get("acceptance") or []
            if isinstance(a, dict) and FC_RE.match(str(a.get("fc") or ""))}
    return out


def _design_refs(it: dict) -> set:
    return {design_file(r) for r in list(it.get("realizes") or []) + list(it.get("proves") or [])
            if design_file(r)}


def needed_pins(path: str, data: dict) -> dict:
    """O que o artefacto consome e tem de fixar: `ref do pin → itens que dependem dele`.
    Os FC dependem do desenho que o documento nomeia; um WP, dos FC que realiza ou cuja
    aceitação usa e dos ficheiros do desenho cujos nós realiza ou prova; todos, das linhas que
    citam."""
    out: dict = {}
    items = _items(data)
    if path == FC_PATH:
        bp = _mod("functional")["_blueprint_of"](data)
        if bp:
            out[bp] = [it["id"] for it in items]
    elif path == WP_PATH:
        for it in items:
            for fc in sorted(_fc_refs(it)):
                out.setdefault("{}#{}".format(FC_PATH, fc), []).append(it["id"])
            for f in sorted(_design_refs(it)):
                out.setdefault(f, []).append(it["id"])
    for it in items:
        for rid in cited_rows(it):
            out.setdefault("{}#{}".format(SU_FILE, rid), []).append(it["id"])
    return {k: sorted(set(v)) for k, v in out.items()}


def with_dependency_pins(eng, data: dict) -> dict:
    """O inventário com a impressão de cada FC que realiza e o sha de cada ficheiro do desenho
    que referencia — calculados pelo motor, sobre o que o read-set do rascunho garante
    inalterado. As entradas desses tipos que o autor tenha escrito saem: o pin é do motor."""
    eng = Path(eng)
    fcs = {it["id"]: it for it in _items(_load(eng / FC_PATH))}

    def do_motor(b):
        ref = str(b.get("ref", "")) if isinstance(b, dict) else ""
        return ref.startswith(FC_PATH + "#") or (design_file(ref) == ref and ref)
    fora = [b for b in data.get("based_on") or [] if not do_motor(b)]
    for ref in sorted(needed_pins(WP_PATH, data)):
        if ref.startswith(FC_PATH + "#"):
            fc = ref.split("#", 1)[1]
            if fc in fcs:
                fora.append({"ref": ref, "sha256": item_fingerprint(FC_PATH, fcs[fc])})
        elif design_file(ref) == ref:
            d = _digest(eng / ref)
            if d:
                fora.append({"ref": ref, "sha256": d})
    return dict(data, based_on=fora)


def moved_pins(path: str, prev: dict, new: dict) -> list:
    """As dependências fixadas nas duas revisões com impressões diferentes. Uma dependência que
    aparece ou desaparece entra ou sai com o conteúdo do próprio item — não é movimento."""
    a, b = pins(prev), pins(new)
    dep = needed_pins(path, new)
    return [{"ref": ref, "from": a[ref], "to": b[ref], "dependents": dep.get(ref, [])}
            for ref in sorted(set(a) & set(b)) if a[ref] != b[ref]]


def _rp(code, item, detail) -> dict:
    return {"code": code, "item": item, "detail": detail}


def revalidation_record(path: str, prev: dict, new: dict, pending, revision, at: str) -> tuple:
    """`(problemas, registo)` — chamado por quem publica, com os pins novos já calculados.

    Mover uma dependência exige a avaliação de cada item que depende dela: `still_valid` só se
    o conteúdo do item não mudou, `updated` só se mudou; a avaliação por escrito e o papel de
    quem a fez. Os registos anteriores vão tal como estavam (só se acrescentam), e o registo
    novo é o motor que o escreve — um rascunho não traz registos feitos."""
    probs = []
    antes = list(prev.get("revalidations") or [])
    agora = list(new.get("revalidations") or [])
    if agora != antes:
        probs.append(_rp("REVALIDATION_DROPPED" if agora[:len(antes)] != antes
                         else "REVALIDATION_FORGED", "",
                         "os registos de revalidação só se acrescentam, e só pelo motor"))
    moved = moved_pins(path, prev, new)
    if not moved:
        if pending:
            probs.append(_rp("NOTHING_TO_REVALIDATE", "", "nenhuma dependência mudou desde a "
                             "revisão anterior — não há o que revalidar"))
        return probs, None
    if not isinstance(pending, dict):
        probs.append(_rp("REVALIDATION_REQUIRED", "", "mudaram dependências desde a revisão "
                         "anterior ({}) — cada item que depende delas precisa de uma avaliação "
                         "registada; trocar o sha não revalida".format(
                             ", ".join(m["ref"] for m in moved))))
        return probs, None
    itens = pending.get("items") if isinstance(pending.get("items"), dict) else {}
    precisa = sorted({d for m in moved for d in m["dependents"]})
    antes_it = {it["id"]: it for it in _items(prev)}
    agora_it = {it["id"]: it for it in _items(new)}
    for d in precisa:
        if d not in itens:
            probs.append(_rp("REVALIDATION_INCOMPLETE", d, "depende de uma dependência que "
                             "mudou e não foi avaliado"))
    for iid, v in sorted(itens.items()):
        if iid not in precisa:
            probs.append(_rp("REVALIDATION_NOT_DEPENDENT", iid, "não depende de nenhuma "
                             "dependência que mudou"))
            continue
        if v not in VERDICTS:
            probs.append(_rp("BAD_VERDICT", iid, "`{}` — esperado still_valid ou updated"
                             .format(v)))
            continue
        mudou = iid not in antes_it or iid not in agora_it or \
            item_fingerprint(path, antes_it[iid]) != item_fingerprint(path, agora_it[iid])
        if v == "still_valid" and mudou:
            probs.append(_rp("VERDICT_MISMATCH", iid, "still_valid, mas o conteúdo mudou"))
        elif v == "updated" and not mudou:
            probs.append(_rp("VERDICT_MISMATCH", iid, "updated, mas o conteúdo é o mesmo"))
    if not str(pending.get("assessment") or "").strip():
        probs.append(_rp("ASSESSMENT_MISSING", "", "a avaliação vai por escrito: o que mudou "
                         "e porque cada item se mantém ou mudou"))
    if not str(pending.get("assessed_by") or "").strip():
        probs.append(_rp("ASSESSOR_MISSING", "", "o papel de quem avaliou"))
    if probs:
        return probs, None
    return [], {"revision": int(revision),
                "moved": [{"ref": m["ref"], "from": m["from"], "to": m["to"]} for m in moved],
                "items": {k: itens[k] for k in sorted(itens)},
                "assessment": str(pending["assessment"]).strip(),
                "assessed_by": str(pending["assessed_by"]).strip(), "at": at}


def pin_findings(eng) -> list:
    """A leitura (auditoria A3/A5): cada dependência fixada contra o estado de agora. O estado
    das linhas citadas continua com os achados ROW_* de sempre; aqui, o que falta fixar."""
    eng = Path(eng)
    excl = _excluded(eng)
    fcs = {it["id"]: it for it in _items(_load(eng / FC_PATH))}
    rows = su_rows(eng)
    out = []
    for path in PINNED:
        data = _load(eng / path)
        if not data:
            continue
        p = pins(data)
        for ref, deps in sorted(needed_pins(path, data).items()):
            if ref.startswith(SU_FILE + "#"):
                rid = ref.split("#", 1)[1]
                if rid in rows and ref not in p:
                    for d in deps:
                        out.append(_f("DEPENDENCY_UNPINNED", d, ref, [ref, d],
                                      "cita `{}` sem impressão registada — não se prova que "
                                      "está actual".format(rid), path, excluded=d in excl))
                continue
            fc = ref.split("#", 1)[1] if ref.startswith(FC_PATH + "#") else ""
            if ref not in p:
                for d in deps:
                    out.append(_f("DEPENDENCY_UNPINNED", d, ref, [ref, d],
                                  "consome `{}` sem impressão registada — não se prova que "
                                  "está actual".format(ref), path,
                                  excluded=d in excl or fc in excl))
            elif fc:
                agora = item_fingerprint(FC_PATH, fcs[fc]) if fc in fcs else ""
                if agora != p[ref]:
                    for d in deps:
                        out.append(_f("CONTRACT_CHANGED", d, fc, [fc, d], "{} {} depois de {} "
                                      "o fixar — revalidar".format(
                                          fc, "mudou" if agora else "deixou de existir", d),
                                      path, excluded=fc in excl))
            elif _digest(eng / ref) != p[ref]:
                for d in deps:
                    out.append(_f("BASIS_CHANGED", d, ref, [ref, d], "`{}` mudou depois de {} "
                                  "o fixar — revalidar".format(ref, d), path,
                                  excluded=d in excl))
    return out


def history_findings(eng) -> list:
    """O artefacto é a revisão que o coordenador publicou, e cada mudança de impressão no seu
    histórico tem a avaliação registada — a troca do hash feita por fora do motor, ou por um
    motor anterior a esta regra, não passa por revalidação."""
    eng = Path(eng)
    out = []
    for path in PINNED:
        cur = eng / path
        if not cur.is_file():
            continue
        rev = int(_load(cur).get("revision") or 0)
        stem = HISTORY_STEM[path]
        h = eng / "{}.r{:04d}.json".format(stem, rev)
        if not h.is_file() or h.read_bytes() != cur.read_bytes():
            out.append(_f("HISTORY_MISMATCH", path, path, [path], "{} não é a revisão r{:04d} "
                          "que o coordenador publicou — editado por fora do motor".format(
                              path, rev), path, document_level=True))
            continue
        prev = None
        for k in range(1, rev + 1):
            hk = eng / "{}.r{:04d}.json".format(stem, k)
            try:
                dk = json.loads(hk.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                out.append(_f("HISTORY_MISMATCH", path, hk.relative_to(eng).as_posix(), [path],
                              "revisão r{:04d} em falta ou ilegível no histórico".format(k),
                              path, document_level=True))
                break
            if prev is not None:
                recs = [r for r in dk.get("revalidations") or []
                        if isinstance(r, dict) and r.get("revision") == k]
                refs = {m.get("ref") for r in recs for m in r.get("moved") or []}
                itens = {i for r in recs for i in (r.get("items") or {})}
                for m in moved_pins(path, prev, dk):
                    if m["ref"] not in refs or not set(m["dependents"]) <= itens:
                        out.append(_f("PIN_UNREVALIDATED", path, m["ref"], [m["ref"], path],
                                      "r{:04d}: `{}` mudou de impressão sem avaliação "
                                      "registada".format(k, m["ref"]), path,
                                      document_level=True))
            prev = dk
    return out


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
