"""process_map.py — o mapa de conhecimento do processo (process-map M1).

O mapa organiza o processo compreendido — faixas, nós, arestas, detalhes, dúvidas e
órfãos — com referências verificáveis à evidência. Não é autoridade de factos: a Shared
Understanding é. Escreve-o só este motor, pelo coordenador (`operation.run`); a guarda
`pre-authority-guard.py` recusa Write/Edit em `_map/`. Plano: `docs/process-map/PLANO.md`.

    check   --engagement <slug|caminho> --draft <f> [--json]
            schema, integridade, evidência, referências (resolúveis e actuais), base,
            fontes consumidas, transferência de PM / PM-U / CALC / etiquetas de §4, órfãos
            e linhagem face à versão publicada. Não escreve nada.
            exit 0 válido · 4 válido com lacunas explícitas · 2 erro · 5 falha interna
    stamp   --engagement <slug|caminho> --draft <f>
            preenche, NO RASCUNHO, só o que falta: `base` ausente, o `sha256` de referências
            resolúveis sem digest, e as fontes consumidas em falta em `based_on`. Nunca
            substitui um valor existente — actualizar um digest não é reavaliar.
    publish --engagement <slug|caminho> --draft <f> [--json]
            `check` e depois UMA operação do coordenador: `_map/map.json` + o snapshot
            imutável `_map/history/mp-vNN.json`. `expected` = a base do rascunho (o mapa
            mudou → `BASE_CHANGED`); `read_set` = `based_on` (uma fonte mudou →
            `STALE_INPUT`). A versão sai da base, sob o lock; um conflito nunca se resolve
            incrementando a versão. Repetir o mesmo rascunho devolve o mesmo recibo.
    status  --engagement <slug|caminho> [--json]
            o mapa publicado: ausente · ok · inválido · versão não suportada.

Referências (`evidence[].ref`, `details[].ref`, `orphans[].ref`): `<caminho>[#<âncora>]`,
relativo ao engagement.
  - `_capture/<wb>.calc-chain.json#CALC-NNN`   bloco de cálculo desse workbook
  - `_capture/<f>.extraction.json#sheets[name=<folha>]`
  - `_capture/process-model.md#PM-NNN` · `#PM-U-NNN` · `#§4:<etiqueta>` · `#CALC-NNN`
    (este último só quando um único calc-chain tem esse id: senão é ambíguo)
  - `.md`: âncora que é um título → a secção inteira; senão as linhas que a contêm
  - outro ficheiro (ex. `inputs/<wb>.xlsx#Folha!B2`): o ficheiro inteiro, âncora não
    verificada (a extracção é o sítio onde a célula se verifica)
Sem âncora: o ficheiro inteiro. Nunca `_map/` nem o estado coordenado.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import runpy
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
SCHEMA = "process-map/1"
SCHEMA_FILE = _HERE.parent / "schemas" / "process-map.schema.json"
MAP_REL = "_map/map.json"
HISTORY_DIR = "_map/history"
PM_REL = "_capture/process-model.md"
ENQ_REL = "enquadramento.md"
MARKERS = ("OBSERVED", "INFERRED", "HYPOTHESIS", "UNKNOWN")
COLLECTIONS = ("lanes", "nodes", "edges", "details", "gaps")
FORBIDDEN_REF_DIRS = ("_map/", "_ops/", "_graph/", "_migration/", "_work/", "_drafts/")

# códigos do check (docs/process-map/M0/RELATORIO.md §4)
MAP_SCHEMA = "MAP-SCHEMA"
MAP_ID_DUPLICATE = "MAP-ID-DUPLICATE"
MAP_DANGLING = "MAP-DANGLING"
MAP_NO_EVIDENCE = "MAP-NO-EVIDENCE"
MAP_UNKNOWN_WITHOUT_GAP = "MAP-UNKNOWN-WITHOUT-GAP"
MAP_REF_UNRESOLVED = "MAP-REF-UNRESOLVED"
MAP_REF_AMBIGUOUS = "MAP-REF-AMBIGUOUS"
MAP_REF_UNSTAMPED = "MAP-REF-UNSTAMPED"
MAP_REF_STALE = "MAP-REF-STALE"
MAP_BASED_ON_INCOMPLETE = "MAP-BASED-ON-INCOMPLETE"
MAP_SOURCE_STALE = "MAP-SOURCE-STALE"
MAP_P0_NOT_CONSUMED = "MAP-P0-NOT-CONSUMED"
MAP_BASE_STALE = "MAP-BASE-STALE"
MAP_TRANSFER_MISSING = "MAP-TRANSFER-MISSING"
MAP_ORPHAN_UNJUSTIFIED = "MAP-ORPHAN-UNJUSTIFIED"
MAP_ORPHAN_NO_AUTHORITY = "MAP-ORPHAN-NO-AUTHORITY"
MAP_ID_DROPPED = "MAP-ID-DROPPED"
MAP_ID_REUSED = "MAP-ID-REUSED"
MAP_WAS_UNKNOWN = "MAP-WAS-UNKNOWN"
MAP_PUBLISHED_INVALID = "MAP-PUBLISHED-INVALID"
MAP_DRAFT_INSIDE = "MAP-DRAFT-INSIDE"

EXIT_OK, EXIT_ERROR, EXIT_GAPS, EXIT_INTERNAL = 0, 2, 4, 5

PM_RULE_RE = re.compile(r"\bPM-\d{3}\b")
PM_Q_RE = re.compile(r"\bPM-U-\d{3}\b")
CALC_RE = re.compile(r"\bCALC-\d{3,}\b")
SYN_LINE_RE = re.compile(r"^- (OBSERVED|INFERRED|HYPOTHESIS|UNKNOWN)\b(.*)$")
SYN_LABEL_RE = re.compile(r"^\s*(?:\([^)]*\)\s*)?—\s*`([^`]+)`")
SHEET_SEL_RE = re.compile(r"^sheets\[name=(?P<name>[^\]]+)\]$")
HEADING_RE = re.compile(r"^(#{1,6})\s")


def _repo_tools() -> Path:
    """Os motores irmãos: ao lado deste ficheiro, ou `library/kernel/tools` do repositório."""
    if (_HERE / "operation.py").is_file():
        return _HERE
    for parent in _HERE.parents:
        cand = parent / "library" / "kernel" / "tools"
        if (cand / "operation.py").is_file():
            return cand
    raise RuntimeError("library/kernel/tools não encontrado a partir de {}".format(_HERE))


_CACHE: dict = {}


def _mod(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = runpy.run_path(str(_repo_tools() / (name + ".py")))
    return _CACHE[name]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_text(text: str) -> str:
    return _sha(text.encode("utf-8"))


def canonical(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1) + "\n"


def _diag(code, message, where="", level="error"):
    return {"code": code, "level": level, "message": message, "where": where}


# ============================================================= engagement e rascunho

def find_engagement(spec: str) -> Path:
    return Path(_mod("coverage")["find_engagement"](spec))


def load_schema() -> dict:
    return json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))


def read_draft(path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("o rascunho não é um objecto JSON")
    return data


def _inside(eng: Path, path: Path) -> bool:
    try:
        Path(path).resolve().relative_to(eng.resolve())
        return True
    except ValueError:
        return False


def load(eng) -> dict:
    """O mapa publicado: `{status, map, digest, detail}`. Nada se escreve."""
    eng = Path(eng)
    p = eng / MAP_REL
    if not p.is_file():
        return {"status": "absent", "map": None, "digest": "", "detail": ""}
    raw = p.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        return {"status": "invalid", "map": None, "digest": _sha(raw),
                "detail": "{}: {}".format(type(exc).__name__, exc)}
    if not isinstance(data, dict):
        return {"status": "invalid", "map": None, "digest": _sha(raw),
                "detail": "o conteúdo não é um objecto JSON"}
    if data.get("schema_version") != SCHEMA:
        return {"status": "unsupported", "map": data, "digest": _sha(raw),
                "detail": "`{}` tem schema `{}`; esta versão lê `{}` — nada se lê nem "
                          "escreve por cima".format(MAP_REL, data.get("schema_version"),
                                                    SCHEMA)}
    errors, _unknown = _mod("workflow")["validate"](data, load_schema())
    if errors:
        return {"status": "invalid", "map": data, "digest": _sha(raw),
                "detail": "; ".join(errors[:5])}
    return {"status": "ok", "map": data, "digest": _sha(raw), "detail": ""}


def _version_number(version) -> int:
    m = re.match(r"^mp-v(\d+)$", str(version or ""))
    return int(m.group(1)) if m else 0


# ============================================================= resolução de referências

def split_ref(ref: str):
    path, _sep, anchor = str(ref).partition("#")
    return path.strip(), anchor.strip()


def _safe_rel(eng: Path, rel: str):
    if not rel or rel.startswith("/") or "\\" in rel or re.match(r"^[A-Za-z]:", rel):
        return None
    parts = rel.split("/")
    if any(p in ("", ".", "..") for p in parts):
        return None
    target = (eng / rel).resolve()
    if not _inside(eng, target):
        return None
    return target


def calc_chain_files(eng: Path) -> list:
    cap = eng / "_capture"
    if not cap.is_dir():
        return []
    return sorted("_capture/" + p.name for p in cap.glob("*.calc-chain.json") if p.is_file())


def _calc_block(eng: Path, rel: str, calc_id: str):
    try:
        data = json.loads((eng / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    for b in data.get("blocks") or []:
        if isinstance(b, dict) and b.get("id") == calc_id:
            return b
    return None


def _md_section(lines: list, idx: int) -> list:
    level = len(HEADING_RE.match(lines[idx]).group(1))
    out = [lines[idx]]
    for line in lines[idx + 1:]:
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) <= level:
            break
        out.append(line)
    return out


def _token_re(anchor: str):
    return re.compile(r"(?<![\w-]){}(?![\w])".format(re.escape(anchor)))


def synopsis_section(text: str) -> list:
    """As linhas da §4 (síntese) do process-model, até à §4bis ou à secção seguinte."""
    lines = text.splitlines()
    out, inside = [], False
    for line in lines:
        if re.match(r"^##\s+4\.\s", line):
            inside = True
            continue
        if inside and re.match(r"^##\s", line):
            break
        if inside:
            out.append(line)
    return out


def synopsis_labels(text: str) -> dict:
    """{etiqueta: [linhas]} das linhas materiais da §4 (etiqueta em crase logo a seguir
    ao marcador — a mesma forma que `aisa-round` e os testes step-8c lêem)."""
    labels: dict = {}
    for line in synopsis_section(text):
        m = SYN_LINE_RE.match(line.strip())
        if not m:
            continue
        lab = SYN_LABEL_RE.match(m.group(2))
        if lab:
            labels.setdefault(lab.group(1), []).append(line)
    return labels


def resolve_ref(eng, ref: str) -> dict:
    """`{status: ok|unresolved|ambiguous, path, anchor, digest, verified_anchor, detail,
    unit}` — `unit` é a chave qualificada da unidade de transferência que a referência
    cobre (ou vazio)."""
    eng = Path(eng)
    rel, anchor = split_ref(ref)
    out = {"status": "unresolved", "path": rel, "anchor": anchor, "digest": "",
           "verified_anchor": False, "detail": "", "unit": ""}
    if any(rel.startswith(d) for d in FORBIDDEN_REF_DIRS):
        out["detail"] = "fonte não admitida: `{}` é estado coordenado".format(rel)
        return out
    target = _safe_rel(eng, rel)
    if target is None:
        out["detail"] = "caminho fora do engagement ou mal formado: `{}`".format(rel)
        return out
    if not target.is_file():
        out["detail"] = "ficheiro inexistente: `{}`".format(rel)
        return out
    raw = target.read_bytes()
    if not anchor:
        out.update(status="ok", digest=_sha(raw), verified_anchor=True)
        return out
    if rel.endswith(".calc-chain.json"):
        if not CALC_RE.fullmatch(anchor):
            out["detail"] = "âncora `{}` não é um CALC-NNN".format(anchor)
            return out
        block = _calc_block(eng, rel, anchor)
        if block is None:
            out["detail"] = "`{}` não existe em `{}`".format(anchor, rel)
            return out
        out.update(status="ok", digest=_sha_text(canonical(block)), verified_anchor=True,
                   unit="{}#{}".format(rel, anchor))
        return out
    if rel.endswith(".json"):
        m = SHEET_SEL_RE.match(anchor)
        if not m:
            out["detail"] = "selector JSON não suportado: `{}`".format(anchor)
            return out
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            out["detail"] = "`{}` não é JSON legível".format(rel)
            return out
        hits = [s for s in data.get("sheets") or []
                if isinstance(s, dict) and s.get("name") == m.group("name")]
        if len(hits) != 1:
            out["detail"] = "folha `{}` encontrada {} vez(es) em `{}`".format(
                m.group("name"), len(hits), rel)
            out["status"] = "ambiguous" if hits else "unresolved"
            return out
        out.update(status="ok", digest=_sha_text(canonical(hits[0])), verified_anchor=True)
        return out
    if rel.endswith(".md"):
        text = raw.decode("utf-8", errors="replace")
        lines = text.splitlines()
        if rel == PM_REL and anchor.startswith("§4:"):
            label = anchor[3:].strip()
            hit = synopsis_labels(text).get(label)
            if not hit:
                out["detail"] = "etiqueta `{}` não existe na §4 de `{}`".format(label, rel)
                return out
            out.update(status="ok", digest=_sha_text("\n".join(hit)), verified_anchor=True,
                       unit="{}#§4:{}".format(PM_REL, label))
            return out
        if rel == PM_REL and CALC_RE.fullmatch(anchor):
            owners = [c for c in calc_chain_files(eng) if _calc_block(eng, c, anchor)]
            if len(owners) > 1:
                out["status"] = "ambiguous"
                out["detail"] = "`{}` existe em {} cadeias de cálculo ({}): qualificar " \
                                "pelo ficheiro".format(anchor, len(owners), ", ".join(owners))
                return out
            if owners:
                out["unit"] = "{}#{}".format(owners[0], anchor)
        tok = _token_re(anchor)
        for i, line in enumerate(lines):
            if HEADING_RE.match(line) and tok.search(line):
                sec = _md_section(lines, i)
                out.update(status="ok", digest=_sha_text("\n".join(sec)), verified_anchor=True)
                break
        else:
            hit = [line for line in lines if tok.search(line)]
            if not hit:
                out["detail"] = "âncora `{}` não encontrada em `{}`".format(anchor, rel)
                out["unit"] = ""
                return out
            out.update(status="ok", digest=_sha_text("\n".join(hit)), verified_anchor=True)
        if rel == PM_REL and (PM_RULE_RE.fullmatch(anchor) or PM_Q_RE.fullmatch(anchor)):
            out["unit"] = "{}#{}".format(PM_REL, anchor)
        return out
    out.update(status="ok", digest=_sha(raw), verified_anchor=False,
               detail="âncora `{}` não verificada neste formato: vale o ficheiro "
                      "inteiro".format(anchor))
    return out


# ============================================================= unidades de transferência

def transfer_units(eng) -> dict:
    """{chave qualificada: classe} — o que a L2 produziu e o mapa tem de colocar: regras
    `PM-NNN`, perguntas `PM-U-NNN`, etiquetas materiais da §4 e, por cadeia de cálculo,
    cada `CALC-NNN` qualificado pelo ficheiro."""
    eng = Path(eng)
    units: dict = {}
    pm = eng / PM_REL
    if pm.is_file():
        text = pm.read_text(encoding="utf-8", errors="replace")
        for pid in sorted(set(PM_Q_RE.findall(text))):
            units["{}#{}".format(PM_REL, pid)] = "process-question"
        rest = PM_Q_RE.sub(" ", text)
        for pid in sorted(set(PM_RULE_RE.findall(rest))):
            units["{}#{}".format(PM_REL, pid)] = "process-rule"
        for label in sorted(synopsis_labels(text)):
            units["{}#§4:{}".format(PM_REL, label)] = "synopsis-label"
    for rel in calc_chain_files(eng):
        try:
            data = json.loads((eng / rel).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for b in data.get("blocks") or []:
            if isinstance(b, dict) and CALC_RE.fullmatch(str(b.get("id", ""))):
                units["{}#{}".format(rel, b["id"])] = "calculation"
    return units


# ============================================================= check

def _all_refs(draft: dict):
    """(onde, objecto de evidência) de cada referência verificável do rascunho."""
    for coll in ("nodes", "edges"):
        for el in draft.get(coll) or []:
            if isinstance(el, dict):
                for i, ev in enumerate(el.get("evidence") or []):
                    if isinstance(ev, dict):
                        yield "{}/{}/evidence[{}]".format(coll, el.get("id"), i), ev
    for el in draft.get("details") or []:
        if isinstance(el, dict) and isinstance(el.get("ref"), dict):
            yield "details/{}/ref".format(el.get("id")), el["ref"]


def _decision_ids(eng: Path) -> set:
    p = eng / "decisions.md"
    if not p.is_file():
        return set()
    return set(re.findall(r"^##\s+(D-\d{3,})\b", p.read_text(encoding="utf-8",
                                                               errors="replace"), re.M))


def check(eng, draft: dict, draft_path=None) -> dict:
    """O veredicto sobre um rascunho. Nunca escreve. `errors` impede a publicação;
    `gaps` são lacunas explícitas que o mapa pode carregar publicado."""
    eng = Path(eng)
    errors, gaps, warnings = [], [], []
    if draft_path is not None and _inside(eng, Path(draft_path)):
        errors.append(_diag(MAP_DRAFT_INSIDE, "o rascunho tem de ficar fora do engagement "
                                              "(a publicação é do coordenador)",
                            str(draft_path)))
    schema_errors, unknown = _mod("workflow")["validate"](draft, load_schema())
    for e in schema_errors:
        errors.append(_diag(MAP_SCHEMA, e))
    for u in unknown:
        warnings.append(_diag("MAP-UNKNOWN-FIELD", "campo não declarado, preservado: " + u,
                              u, "warning"))
    if schema_errors:
        return _verdict(errors, gaps, warnings, {}, [])

    # ---- identidade e integridade referencial
    ids: dict = {}
    for coll in COLLECTIONS:
        for el in draft[coll]:
            if el["id"] in ids:
                errors.append(_diag(MAP_ID_DUPLICATE, "id repetido: {}".format(el["id"]),
                                    "{}/{}".format(coll, el["id"])))
            ids[el["id"]] = coll
    lanes = {el["id"] for el in draft["lanes"]}
    nodes = {el["id"] for el in draft["nodes"]}
    edges = {el["id"] for el in draft["edges"]}
    details = {el["id"] for el in draft["details"]}
    for el in draft["nodes"]:
        if el["lane"] not in lanes:
            errors.append(_diag(MAP_DANGLING, "faixa inexistente: {}".format(el["lane"]),
                                "nodes/{}/lane".format(el["id"])))
    for el in draft["edges"]:
        for end in ("src", "dst"):
            if el[end] not in nodes:
                errors.append(_diag(MAP_DANGLING, "nó inexistente: {}".format(el[end]),
                                    "edges/{}/{}".format(el["id"], end)))
    for el in draft["details"]:
        for a in el["attaches_to"]:
            if a not in nodes | edges:
                errors.append(_diag(MAP_DANGLING, "elemento inexistente: {}".format(a),
                                    "details/{}/attaches_to".format(el["id"])))
    gap_targets: set = set()
    for el in draft["gaps"]:
        for a in el["attaches_to"]:
            if a != "GLOBAL" and a not in nodes | edges | details:
                errors.append(_diag(MAP_DANGLING, "elemento inexistente: {}".format(a),
                                    "gaps/{}/attaches_to".format(el["id"])))
            gap_targets.add(a)
        gaps.append(_diag("MAP-GAP", el["question"], el["id"], "gap"))

    # ---- evidência: afirmação sem prova, ou UNKNOWN sem dúvida associada
    for coll in ("nodes", "edges"):
        for el in draft[coll]:
            where = "{}/{}".format(coll, el["id"])
            if el["marker"] == "UNKNOWN":
                if el["id"] not in gap_targets:
                    errors.append(_diag(MAP_UNKNOWN_WITHOUT_GAP, "UNKNOWN sem dúvida (MAPG) "
                                        "associada", where))
            elif not el["evidence"]:
                errors.append(_diag(MAP_NO_EVIDENCE, "{} sem evidência".format(el["marker"]),
                                    where))
    for el in draft["details"]:
        if el["marker"] == "UNKNOWN" and el["id"] not in gap_targets:
            errors.append(_diag(MAP_UNKNOWN_WITHOUT_GAP, "UNKNOWN sem dúvida (MAPG) associada",
                                "details/{}".format(el["id"])))

    # ---- referências: resolúveis, não ambíguas, com digest, actuais
    resolved: list = []
    referenced_files: set = set()
    covered_units: set = set()
    for where, ev in _all_refs(draft):
        r = resolve_ref(eng, ev["ref"])
        resolved.append((where, ev, r))
        if r["status"] == "ambiguous":
            errors.append(_diag(MAP_REF_AMBIGUOUS, r["detail"], where))
            continue
        if r["status"] != "ok":
            errors.append(_diag(MAP_REF_UNRESOLVED, r["detail"], where))
            continue
        referenced_files.add(r["path"])
        if r["unit"]:
            covered_units.add(r["unit"])
        if "sha256" not in ev:
            errors.append(_diag(MAP_REF_UNSTAMPED, "referência sem digest: `stamp` preenche "
                                                   "o que falta", where))
        elif ev["sha256"] != r["digest"]:
            errors.append(_diag(MAP_REF_STALE, "o conteúdo de `{}` mudou desde que foi "
                                               "citado: reavaliar o elemento".format(ev["ref"]),
                                where))
        if not r["verified_anchor"] and r["detail"]:
            warnings.append(_diag("MAP-ANCHOR-UNVERIFIED", r["detail"], where, "warning"))

    # ---- órfãos: resolvem, cobrem a unidade, e só `out_of_scope` justificado sai do âmbito
    decisions = _decision_ids(eng)
    for i, o in enumerate(draft["orphans"]):
        where = "orphans[{}]".format(i)
        r = resolve_ref(eng, o["ref"])
        if r["status"] != "ok":
            code = MAP_REF_AMBIGUOUS if r["status"] == "ambiguous" else MAP_REF_UNRESOLVED
            errors.append(_diag(code, r["detail"], where))
        else:
            referenced_files.add(r["path"])
            if r["unit"]:
                covered_units.add(r["unit"])
        if o["reason"] == "out_of_scope":
            if not o["note"].strip():
                errors.append(_diag(MAP_ORPHAN_UNJUSTIFIED, "fora de âmbito sem justificação",
                                    where))
            if o["materiality"] == "material":
                if not o.get("decision_ref"):
                    errors.append(_diag(MAP_ORPHAN_NO_AUTHORITY, "exclusão material sem "
                                        "decisão (D-NNN) que a autorize", where))
                elif o["decision_ref"] not in decisions:
                    errors.append(_diag(MAP_ORPHAN_NO_AUTHORITY, "decisão {} inexistente em "
                                        "decisions.md".format(o["decision_ref"]), where))
        else:
            gaps.append(_diag("MAP-ORPHAN-OPEN", "{} ({}): {}".format(
                o["ref"], o["reason"], o["note"]), where, "gap"))
    for el in draft["gaps"]:
        if el.get("pm_u_ref"):
            covered_units.add("{}#{}".format(PM_REL, el["pm_u_ref"]))

    # ---- fontes consumidas: completas e actuais; o P-0 e o modelo entram quando existem
    based = {}
    for s in draft["based_on"]:
        based[s["path"]] = s["sha256"]
    required_files = set(referenced_files)
    for rel in (ENQ_REL, PM_REL):
        if (eng / rel).is_file():
            required_files.add(rel)
    if (eng / ENQ_REL).is_file() and ENQ_REL not in based:
        errors.append(_diag(MAP_P0_NOT_CONSUMED, "`enquadramento.md` existe e não consta de "
                                                 "`based_on`: o P-0 não foi consumido",
                            "based_on"))
    for rel in sorted(required_files - {ENQ_REL}):
        if rel not in based:
            errors.append(_diag(MAP_BASED_ON_INCOMPLETE, "`{}` é citado mas não consta de "
                                                         "`based_on`".format(rel), "based_on"))
    for rel, sha in sorted(based.items()):
        target = _safe_rel(eng, rel)
        cur = _sha(target.read_bytes()) if target is not None and target.is_file() else ""
        if any(rel.startswith(d) for d in FORBIDDEN_REF_DIRS):
            errors.append(_diag(MAP_SCHEMA, "`based_on` não admite estado coordenado: "
                                            "`{}`".format(rel), "based_on"))
        elif cur != sha:
            errors.append(_diag(MAP_SOURCE_STALE, "a fonte `{}` mudou (ou desapareceu) desde "
                                                  "o rascunho".format(rel), "based_on"))

    # ---- transferência: nada do que a L2 produziu desaparece em silêncio
    units = transfer_units(eng)
    missing = sorted(u for u in units if u not in covered_units)
    for u in missing:
        errors.append(_diag(MAP_TRANSFER_MISSING, "{} ({}) sem destino no mapa: colocar num "
                                                  "elemento ou em `orphans`".format(u, units[u]),
                            u))

    # ---- base e linhagem face à versão publicada
    cur = load(eng)
    if cur["status"] in ("invalid", "unsupported"):
        errors.append(_diag(MAP_PUBLISHED_INVALID, cur["detail"], MAP_REL))
    if draft["base"] != cur["digest"]:
        errors.append(_diag(MAP_BASE_STALE, "o mapa publicado não é a base do rascunho: "
                                            "reabrir sobre a versão actual e reconciliar",
                            "base"))
    live = set(ids)
    retired = {r["id"] for r in draft["retired_ids"]}
    for rid in sorted(live & retired):
        errors.append(_diag(MAP_ID_REUSED, "{} está vivo e retirado".format(rid), rid))
    prev_live, prev_retired = set(), set()
    if cur["status"] == "ok":
        pm = cur["map"]
        prev_live = {el["id"] for c in COLLECTIONS for el in pm.get(c) or []}
        prev_retired = {r["id"] for r in pm.get("retired_ids") or []}
    for rid in sorted(prev_live - live - retired):
        errors.append(_diag(MAP_ID_DROPPED, "{} desapareceu sem ficar em `retired_ids`"
                            .format(rid), rid))
    for rid in sorted(prev_retired - retired):
        errors.append(_diag(MAP_ID_REUSED, "{} estava retirado e saiu de `retired_ids`"
                            .format(rid), rid))
    for rid in sorted(prev_retired & live):
        errors.append(_diag(MAP_ID_REUSED, "{} foi retirado e não pode voltar a ser usado"
                            .format(rid), rid))
    known_before = prev_live | prev_retired
    for coll in COLLECTIONS:
        for el in draft[coll]:
            for w in el.get("was") or []:
                if w not in known_before:
                    errors.append(_diag(MAP_WAS_UNKNOWN, "`was` aponta para {}, que não existia "
                                        "na versão publicada".format(w),
                                        "{}/{}".format(coll, el["id"])))
    for coll in ("nodes", "edges", "details"):
        for el in draft[coll]:
            if el["marker"] == "UNKNOWN":
                gaps.append(_diag("MAP-UNKNOWN", el["label"], el["id"], "gap"))
    return _verdict(errors, gaps, warnings, units, missing)


def _verdict(errors, gaps, warnings, units, missing) -> dict:
    return {"valid": not errors, "errors": errors, "gaps": gaps, "warnings": warnings,
            "transfer": {"units": len(units), "missing": missing}}


# ============================================================= stamp

def stamp(eng, draft: dict) -> tuple:
    """(rascunho com o que faltava, [o que se preencheu]). Nunca substitui."""
    eng = Path(eng)
    out = copy.deepcopy(draft)
    filled = []
    if "base" not in out:
        out["base"] = load(eng)["digest"]
        filled.append("base")
    files = set()
    for where, ev in _all_refs(out):
        r = resolve_ref(eng, ev.get("ref", ""))
        if r["status"] != "ok":
            continue
        files.add(r["path"])
        if "sha256" not in ev:
            ev["sha256"] = r["digest"]
            filled.append(where)
    for o in out.get("orphans") or []:
        r = resolve_ref(eng, o.get("ref", ""))
        if r["status"] == "ok":
            files.add(r["path"])
    for rel in (ENQ_REL, PM_REL):
        if (eng / rel).is_file():
            files.add(rel)
    based = out.setdefault("based_on", [])
    have = {s.get("path") for s in based if isinstance(s, dict)}
    for rel in sorted(files - have):
        target = _safe_rel(eng, rel)
        if target is not None and target.is_file():
            based.append({"path": rel, "sha256": _sha(target.read_bytes())})
            filled.append("based_on/" + rel)
    return out, filled


# ============================================================= publish

def operation_id(draft: dict) -> str:
    body = {k: v for k, v in draft.items() if k != "version"}
    return "process-map-" + _sha_text(canonical(body))[:16]


def publish(eng, draft: dict, draft_path=None) -> dict:
    """UMA operação do coordenador. Devolve `{published, ...}`; nunca levanta por recusa."""
    eng = Path(eng)
    O = _mod("operation")
    op_id = operation_id(draft)
    existing = O["read_receipt"](eng, op_id)
    if existing:
        return {"published": True, "replayed": True, "operation_id": op_id,
                "version": existing.get("map_version") or _receipt_version(eng, existing),
                "receipt": existing}
    verdict = check(eng, draft, draft_path)
    if not verdict["valid"]:
        return {"published": False, "code": "MAP-CHECK-FAILED", "verdict": verdict,
                "message": "o rascunho não passa no check: nada ficou publicado"}
    cur = load(eng)
    version = "mp-v{:02d}".format(_version_number((cur["map"] or {}).get("version")) + 1
                                  if cur["status"] == "ok" else 1)
    content = canonical(dict(draft, version=version))
    hist_rel = "{}/{}.json".format(HISTORY_DIR, version)
    read_set = {s["path"]: s["sha256"] for s in draft["based_on"]}
    try:
        receipt = O["run"](eng, op_id, {MAP_REL: content, hist_rel: content},
                           expected={MAP_REL: draft["base"], hist_rel: ""},
                           read_set=read_set)
    except O["OperationError"] as exc:
        resp = O["response_from_error"](exc)
        return {"published": False, "code": resp["code"], "source_code": exc.code,
                "response": resp, "message": str(exc)}
    return {"published": True, "replayed": bool(receipt.get("replayed")),
            "operation_id": op_id, "version": version, "map": MAP_REL, "history": hist_rel,
            "receipt": receipt}


def _receipt_version(eng: Path, receipt: dict) -> str:
    for rel in (receipt.get("after") or receipt.get("revision") or {}):
        m = re.match(r"^_map/history/(mp-v\d+)\.json$", str(rel))
        if m:
            return m.group(1)
    return ""


# ============================================================= CLI

def utf8_console() -> None:
    """A consola do Windows não é UTF-8 por omissão: sem isto, um acento rebenta o print."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _print(obj, as_json: bool, lines):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for line in lines:
            print(line)


def _verdict_lines(v: dict) -> list:
    out = ["mapa: {} · erros {} · lacunas {} · avisos {} · unidades {} (sem destino {})"
           .format("válido" if v["valid"] else "inválido", len(v["errors"]), len(v["gaps"]),
                   len(v["warnings"]), v["transfer"]["units"], len(v["transfer"]["missing"]))]
    for d in v["errors"]:
        out.append("  ERRO {} [{}] {}".format(d["code"], d["where"], d["message"]))
    for d in v["gaps"]:
        out.append("  lacuna {} [{}] {}".format(d["code"], d["where"], d["message"]))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="process_map.py",
                                 description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "stamp", "publish", "status"):
        p = sub.add_parser(name)
        p.add_argument("--engagement", required=True)
        if name != "status":
            p.add_argument("--draft", required=True)
        p.add_argument("--json", action="store_true")
    utf8_console()
    args = ap.parse_args(argv)
    try:
        eng = find_engagement(args.engagement)
        if args.cmd == "status":
            st = load(eng)
            st = {k: v for k, v in st.items() if k != "map"} | {
                "version": (st["map"] or {}).get("version", "")}
            _print(st, args.json, ["mapa publicado: {} {} {}".format(
                st["status"], st["version"], st["detail"]).rstrip()])
            return EXIT_OK if st["status"] in ("ok", "absent") else EXIT_ERROR
        draft = read_draft(args.draft)
        if args.cmd == "check":
            v = check(eng, draft, args.draft)
            _print(v, args.json, _verdict_lines(v))
            if not v["valid"]:
                return EXIT_ERROR
            return EXIT_GAPS if v["gaps"] else EXIT_OK
        if args.cmd == "stamp":
            if _inside(eng, Path(args.draft)):
                print("recusado: o rascunho tem de ficar fora do engagement", file=sys.stderr)
                return EXIT_ERROR
            out, filled = stamp(eng, draft)
            Path(args.draft).write_text(canonical(out), encoding="utf-8")
            _print({"filled": filled}, args.json,
                   ["preenchido: {}".format(", ".join(filled) or "nada")])
            return EXIT_OK
        res = publish(eng, draft, args.draft)
        _print(res, args.json, [
            "publicado {} ({}){}".format(res["version"], res["operation_id"],
                                        " — repetição, sem nova versão" if res.get("replayed")
                                        else "")
            if res["published"] else "não publicado: {} — {}".format(res["code"],
                                                                       res["message"])]
            + (_verdict_lines(res["verdict"]) if res.get("verdict") else []))
        return EXIT_OK if res["published"] else EXIT_ERROR
    except Exception as exc:  # noqa: BLE001 — resultado não verificado, nunca sucesso
        print("falha interna ({}): {} — resultado não verificado".format(
            type(exc).__name__, exc), file=sys.stderr)
        return EXIT_INTERNAL


if __name__ == "__main__":
    sys.exit(main())
