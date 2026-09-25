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
            o mapa publicado (ausente · ok · inválido · versão não suportada) e a validação
            aplicável: validado · validação de outra versão · inválida · por validar.
    render  --engagement <slug|caminho>
            `<engagement>/process-map.html`, vista derivada e determinista (fluxograma por
            faixas em SVG + passos, ligações, dúvidas, fora do mapa, fontes).
    questions --engagement <slug|caminho> [--json]
            as dúvidas do mapa agrupadas por tema, estrutura primeiro — a validação pelo
            dono pergunta por grupo, nunca por célula.
    project --engagement <slug|caminho> [--json]
            as linhas da SU organizadas pelo mapa: por elemento, sem associação avaliada,
            GLOBAL, N/A, elementos sem linhas (sinal, não lacuna), ids desconhecidos e
            retirados (com sucessores). Nunca escreve.
    summary --engagement <slug|caminho> [--task resume|framing|options|blueprint|handoff]
            [--budget N] [--json]
            o mapa em contexto compacto (retoma): versão, validação, actualidade, bloqueios
            (nunca truncados), estado por bloco; detalhe só para o que a tarefa pede;
            acima do orçamento declara-se parcial e diz como expandir.
    revalidate --engagement --source <rel> [--source …] --assessment "<o que se viu>"
            --by "<papel>" [--reviewed MAPN-…] --out <rascunho fora do engagement>
            regista a reavaliação de fontes que mudaram: actualiza `based_on` e só as
            referências dos elementos revistos; os afectados por rever continuam stale.
    approval-block --engagement --scope --conditions --validated-by [--timestamp]
            o texto do bloco `D-NNN — Mapa do processo mp-vNN validado` com o digest da
            versão publicada; quem o escreve em decisions.md é `resolve.py draft/publish`.

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
MAP_PASSAGE_UNPLACED = "MAP-PASSAGE-UNPLACED"

EXIT_OK, EXIT_ERROR, EXIT_GAPS, EXIT_INTERNAL = 0, 2, 4, 5

PM_RULE_RE = re.compile(r"\bPM-\d{3}\b")
PM_Q_RE = re.compile(r"\bPM-U-\d{3}\b")
CALC_RE = re.compile(r"\bCALC-\d{3,}\b")
SYN_LINE_RE = re.compile(r"^- (OBSERVED|INFERRED|HYPOTHESIS|UNKNOWN)\b(.*)$")
SYN_LABEL_RE = re.compile(r"^\s*(?:\([^)]*\)\s*)?—\s*`([^`]+)`")
SHEET_SEL_RE = re.compile(r"^sheets\[name=(?P<name>[^\]]+)\]$")
HEADING_RE = re.compile(r"^(#{1,6})\s")
# parágrafos das fontes de texto (extracção LT): `[¶N] texto` e a âncora `¶N` ou `¶N–M`
PARA_LINE_RE = re.compile(r"^\[¶(\d+)\]\s?(.*)$")
PARA_ANCHOR_RE = re.compile(r"^¶(\d+)(?:[–-](\d+))?$")
# fonte curta = até este número de parágrafos; transcrições com tempo (.vtt/.srt) ficam
# de fora — são falas, não parágrafos, e o mapa cita-as por intervalo de tempo
PASSAGE_LIMIT = 60
TIMED_FORMATS = (".vtt", ".srt")


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
           "verified_anchor": False, "detail": "", "unit": "", "units": []}
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
        para = PARA_ANCHOR_RE.match(anchor) if rel.endswith(".text.md") else None
        if para and para.group(2):
            lo, hi = int(para.group(1)), int(para.group(2))
            by_n = {}
            for line in lines:
                pm = PARA_LINE_RE.match(line)
                if pm:
                    by_n[int(pm.group(1))] = line
            want = list(range(lo, hi + 1))
            if hi < lo or any(k not in by_n for k in want):
                out["detail"] = "parágrafos `{}` não existem todos em `{}`".format(anchor, rel)
                return out
            out.update(status="ok", digest=_sha_text("\n".join(by_n[k] for k in want)),
                       verified_anchor=True,
                       units=["{}#¶{}".format(rel, k) for k in want])
            return out
        if para:
            out["units"] = ["{}#¶{}".format(rel, para.group(1))]
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
                out["unit"], out["units"] = "", []
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


def passage_units(eng) -> dict:
    """`{units: {chave: texto}, unitemized: [caminho]}` — os parágrafos com conteúdo das
    fontes de texto curtas (extracção LT com estado `ok`, até `PASSAGE_LIMIT` parágrafos,
    sem as transcrições com tempo). Cada um tem de ter destino no mapa: citado num elemento
    ou disposto em `orphans`. Uma fonte mais longa não se verifica parágrafo a parágrafo, e o
    `check` di-lo (lacuna explícita)."""
    eng = Path(eng)
    out = {"units": {}, "unitemized": []}
    cap = eng / "_capture"
    if not cap.is_dir():
        return out
    for p in sorted(cap.glob("*.extraction.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict) or data.get("artefact") != "aisa.capture.text-extraction":
            continue
        if data.get("status") != "ok":
            continue
        ident = data.get("identity") or {}
        if str(ident.get("format", "")).lower() in TIMED_FORMATS:
            continue
        name = (data.get("output") or {}).get("text_md") or ""
        text_p = cap / name
        if not name or not text_p.is_file():
            continue
        rel = "_capture/" + name
        paras = {}
        for line in text_p.read_text(encoding="utf-8", errors="replace").splitlines():
            pm = PARA_LINE_RE.match(line)
            if pm:
                body = pm.group(2).lstrip("> ").strip()
                if re.search(r"\w", body):
                    paras[int(pm.group(1))] = body
        if len(paras) > PASSAGE_LIMIT:
            out["unitemized"].append(rel)
            continue
        for n, body in sorted(paras.items()):
            out["units"]["{}#¶{}".format(rel, n)] = body
    return out


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
        covered_units.update(r["units"])
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
            covered_units.update(r["units"])
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
    for s in incomplete_sources(eng):
        gaps.append(_diag("MAP-SOURCE-INCOMPLETE", "extracção `{}`: {}{}".format(
            s["path"], s["status"], " — " + s["reason"] if s["reason"] else ""),
            s["path"], "gap"))

    # ---- fontes curtas: cada parágrafo com conteúdo tem destino no mapa ou disposição
    pas = passage_units(eng)
    open_pas: dict = {}
    for key in pas["units"]:
        if key not in covered_units:
            rel, n = key.rsplit("#¶", 1)
            open_pas.setdefault(rel, []).append(int(n))
    for rel in sorted(open_pas):
        errors.append(_diag(MAP_PASSAGE_UNPLACED, "`{}`: {} sem destino no mapa — citar num "
                            "elemento ou dispor em `orphans` (âncora `¶N` ou `¶N–M`)".format(
                                rel, _para_ranges(open_pas[rel])), rel))
    for rel in pas["unitemized"]:
        gaps.append(_diag("MAP-SOURCE-UNITEMIZED", "`{}` tem mais de {} parágrafos: não se "
                          "verifica parágrafo a parágrafo".format(rel, PASSAGE_LIMIT),
                          rel, "gap"))
    return _verdict(errors, gaps, warnings, units, missing,
                    {"units": len(pas["units"]),
                     "missing": sorted("{}#¶{}".format(r, n) for r, ns in open_pas.items()
                                       for n in ns)})


def _verdict(errors, gaps, warnings, units, missing, passages=None) -> dict:
    return {"valid": not errors, "errors": errors, "gaps": gaps, "warnings": warnings,
            "transfer": {"units": len(units), "missing": missing},
            "passages": passages or {"units": 0, "missing": []}}


def _para_ranges(ns) -> str:
    """[1,2,3,5] → «¶1–3, ¶5»."""
    ns, out = sorted(set(ns)), []
    for n in ns:
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return ", ".join("¶{}".format(a) if a == b else "¶{}–{}".format(a, b) for a, b in out)


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


# ============================================================= fontes com leitura incompleta

def incomplete_sources(eng) -> list:
    """As extracções da captura com estado diferente de `ok` — a incompletude fica à vista,
    referenciada ou não pelo mapa (`[{path, status, reason}]`)."""
    eng = Path(eng)
    out = []
    cap = eng / "_capture"
    if not cap.is_dir():
        return out
    for p in sorted(cap.glob("*.extraction.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            out.append({"path": "_capture/" + p.name, "status": "unreadable", "reason": ""})
            continue
        st = str(data.get("status", "")) if isinstance(data, dict) else "unreadable"
        if st != "ok":
            out.append({"path": "_capture/" + p.name, "status": st or "unknown",
                        "reason": str((data or {}).get("reason") or "")})
    return out


# ============================================================= validação pelo dono

VALIDATION_HEAD_RE = re.compile(r"^##\s+(D-\d{3,})\s+—\s+Mapa do processo\s+(mp-v\d{2,})\s+"
                                r"validado\s*$")
FIELD_RE = re.compile(r"^-\s+\*\*(?P<k>[^*]+)\*\*\s*:\s*(?P<v>.*)$")
VALIDATION_FIELDS = ("Map sha256", "Scope", "Conditions", "Validated by", "Timestamp")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})$")


def validation_blocks(eng) -> list:
    """Os blocos `## D-NNN — Mapa do processo mp-vNN validado` de decisions.md, pela ordem
    do ficheiro, com os campos lidos e os problemas de cada um."""
    eng = Path(eng)
    try:
        lines = (eng / "decisions.md").read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    blocks, cur = [], None
    for line in lines:
        if line.startswith("## "):
            m = VALIDATION_HEAD_RE.match(line.strip())
            cur = {"decision": m.group(1), "version": m.group(2), "fields": {}} if m else None
            if cur:
                blocks.append(cur)
            continue
        if cur:
            f = FIELD_RE.match(line.strip())
            if f:
                cur["fields"][f.group("k").strip()] = f.group("v").strip()
    validator_problem = _mod("functional")["validator_problem"]
    for b in blocks:
        probs = []
        for k in VALIDATION_FIELDS:
            if not b["fields"].get(k):
                probs.append("falta `{}`".format(k))
        sha = b["fields"].get("Map sha256", "")
        if sha and not re.fullmatch(r"[0-9a-f]{64}", sha):
            probs.append("`Map sha256` não é um digest")
        vp = validator_problem(b["fields"].get("Validated by", ""))
        if b["fields"].get("Validated by") and vp:
            probs.append(vp)
        ts = b["fields"].get("Timestamp", "")
        if ts and not ISO_RE.match(ts):
            probs.append("`Timestamp` não é ISO-8601")
        hist = eng / HISTORY_DIR / (b["version"] + ".json")
        if not hist.is_file():
            probs.append("a versão {} não existe no histórico".format(b["version"]))
        elif sha and _sha(hist.read_bytes()) != sha:
            probs.append("o digest não é o de {} (bloco não corresponde à versão que "
                         "diz validar)".format(b["version"]))
        b["problems"] = probs
    return blocks


def validation(eng) -> dict:
    """A validação aplicável ao mapa publicado AGORA:
    `validated` (bloco válido para esta versão e estes bytes) · `stale` (a validação válida
    mais recente é de outra versão: a mudança pede avaliação — nunca transita sozinha) ·
    `invalid` (há bloco para esta versão, mas incompleto ou forjado) · `not_validated` ·
    `no_map`. O mapa nunca é alterado para levar a sua aprovação."""
    eng = Path(eng)
    cur = load(eng)
    blocks = validation_blocks(eng)
    base = {"blocks": [{k: b[k] for k in ("decision", "version", "problems")} for b in blocks]}
    if cur["status"] != "ok":
        return dict(base, status="no_map", decision="", version="", scope="", conditions="",
                    detail="sem mapa publicado legível ({})".format(cur["status"]))
    version = cur["map"].get("version", "")
    good = [b for b in blocks if not b["problems"]]
    here = [b for b in good if b["version"] == version and
            b["fields"]["Map sha256"] == cur["digest"]]
    if here:
        b = here[-1]
        return dict(base, status="validated", decision=b["decision"], version=version,
                    scope=b["fields"]["Scope"], conditions=b["fields"]["Conditions"],
                    validated_by=b["fields"]["Validated by"],
                    timestamp=b["fields"]["Timestamp"], detail="")
    # process-map M4: uma revisão que só revalidou fontes (mesma representação) mantém a
    # validação — desde que cada fonte que mudou desde a versão validada tenha a sua
    # entrada em `revalidations`. Trocar digests sem esse registo nunca a transporta.
    for b in reversed(good):
        hist = eng / HISTORY_DIR / (b["version"] + ".json")
        try:
            old_map = json.loads(hist.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if structural_digest(old_map) != structural_digest(cur["map"]):
            continue
        before = {s["path"]: s["sha256"] for s in old_map.get("based_on") or []}
        now = {s["path"]: s["sha256"] for s in cur["map"].get("based_on") or []}
        moved = {p for p in set(before) | set(now) if before.get(p) != now.get(p)}
        logged = {s for r in cur["map"].get("revalidations") or []
                  if _version_number(r.get("from_version")) >= _version_number(b["version"])
                  for s in r.get("sources") or []}
        if moved and moved <= logged:
            return dict(base, status="validated", decision=b["decision"], version=version,
                        scope=b["fields"]["Scope"], conditions=b["fields"]["Conditions"],
                        validated_by=b["fields"]["Validated by"],
                        timestamp=b["fields"]["Timestamp"], carried_from=b["version"],
                        detail="validação de {} transportada: a representação é a mesma e "
                               "as fontes que mudaram foram revalidadas ({})".format(
                                   b["version"], ", ".join(sorted(moved))))
    bad_here = [b for b in blocks if b["version"] == version and b["problems"]]
    if bad_here:
        b = bad_here[-1]
        return dict(base, status="invalid", decision=b["decision"], version=version,
                    scope="", conditions="",
                    detail="{}: {}".format(b["decision"], "; ".join(b["problems"])))
    if good:
        b = good[-1]
        return dict(base, status="stale", decision=b["decision"], version=version,
                    scope=b["fields"]["Scope"], conditions=b["fields"]["Conditions"],
                    detail="{} validou {}; o mapa publicado é {} — avaliar a mudança e "
                           "validar de novo".format(b["decision"], b["version"], version))
    return dict(base, status="not_validated", decision="", version=version, scope="",
                conditions="", detail="nenhuma validação do dono registada")


def approval_block(eng, scope: str, conditions: str, validated_by: str,
                   timestamp: str | None = None) -> str:
    """O texto do bloco de validação da versão publicada, com o digest calculado pelo
    motor. O escritor de decisions.md continua a ser `resolve.py draft/publish`."""
    import time
    eng = Path(eng)
    cur = load(eng)
    if cur["status"] != "ok":
        raise ValueError("sem mapa publicado legível ({})".format(cur["status"]))
    prob = _mod("functional")["validator_problem"](validated_by)
    if prob:
        raise ValueError("validação recusada: " + prob)
    if not str(scope).strip():
        raise ValueError("validação recusada: falta o âmbito validado")
    if not str(conditions).strip():
        raise ValueError("validação recusada: `Conditions` diz as dúvidas mantidas, ou "
                         "`nenhuma`")
    ts = timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        md = (eng / "decisions.md").read_text(encoding="utf-8")
    except OSError:
        md = ""
    later = sorted(t for t in re.findall(r"\*\*Timestamp\*\*\s*:\s*(\S+)", md) if t > ts)
    if later:
        raise ValueError("o bloco teria data {} anterior a uma decisão já registada ({})"
                         .format(ts, later[-1]))
    ids = _mod("workflow")["_decision_ids"](eng)
    did = "D-{:03d}".format(max([int(d[2:]) for d in ids] or [0]) + 1)
    return ("\n## {} — Mapa do processo {} validado\n\n- **Map sha256**: {}\n"
            "- **Scope**: {}\n- **Conditions**: {}\n- **Validated by**: {}\n"
            "- **Timestamp**: {}\n").format(did, cur["map"]["version"], cur["digest"],
                                            scope.strip(), conditions.strip(),
                                            validated_by.strip(), ts)


# ============================================================= perguntas agrupadas

GROUPS = (("estrutura", "Passos e ligações"),
          ("saidas", "Saídas e quem as recebe"),
          ("excecoes", "Exceções e desvios"),
          ("ambito", "Âmbito e temas transversais"))
FIXED_QUESTIONS = {
    "estrutura": "Os passos e a ordem estão certos, e nenhum falta?",
    "saidas": "As saídas e quem as recebe estão completas?",
    "ambito": "O que está fora do mapa está bem fora do âmbito?",
}


def questions(eng) -> list:
    """As dúvidas do mapa publicado agrupadas por tema, estrutura primeiro — o material da
    validação pelo dono (perguntas agrupadas, nunca uma por célula). Cada grupo abre com a
    pergunta fixa que valida a representação; as dúvidas vêm a seguir."""
    cur = load(eng)
    if cur["status"] != "ok":
        return []
    m = cur["map"]
    kinds = {n["id"]: n["kind"] for n in m["nodes"]}
    lane_kind = {la["id"]: la["kind"] for la in m["lanes"]}
    node_lane = {n["id"]: n["lane"] for n in m["nodes"]}
    edge_kind = {e["id"]: e["kind"] for e in m["edges"]}
    detail_on = {d["id"]: d["attaches_to"] for d in m["details"]}

    def group_of(targets):
        flat = []
        for t in targets:
            flat += detail_on.get(t, [t])
        if "GLOBAL" in flat:
            return "ambito"
        if any(kinds.get(t) == "exception" or edge_kind.get(t) == "exception" for t in flat):
            return "excecoes"
        if any(kinds.get(t) == "output" or
               lane_kind.get(node_lane.get(t, "")) in ("consumer", "downstream") for t in flat):
            return "saidas"
        return "estrutura"

    items = {g: [] for g, _t in GROUPS}
    for g in m["gaps"]:
        items[group_of(g["attaches_to"])].append(
            {"id": g["id"], "question": g["question"], "about": g["attaches_to"],
             "respondent": g.get("respondent", ""), "pm_u_ref": g.get("pm_u_ref", "")})
    for o in m["orphans"]:
        if o["reason"] == "out_of_scope":
            continue
        items["estrutura" if o["reason"] == "gap_in_map" else "ambito"].append(
            {"id": o["ref"], "question": o["note"], "about": [], "respondent": "",
             "pm_u_ref": ""})
    out = []
    for g, title in GROUPS:
        fixed = FIXED_QUESTIONS.get(g)
        if not items[g] and not fixed:
            continue
        out.append({"group": g, "title": title, "validates": fixed or "",
                    "items": items[g]})
    return out


# ============================================================= projecção SU ↔ mapa

SU_FILE = "shared-understanding.md"
KNOWLEDGE = ("Confirmed", "Assumed")


def successors(m: dict) -> dict:
    """{id retirado: [ids que o dizem em `was`]} — a linhagem, para reapontar."""
    out: dict = {}
    for c in COLLECTIONS:
        for el in m.get(c) or []:
            for w in el.get("was") or []:
                out.setdefault(w, []).append(el["id"])
    return {k: sorted(v) for k, v in out.items()}


def project(eng) -> dict:
    """As linhas da SU organizadas pelo mapa publicado. Nunca escreve e nunca julga
    completude: `dark` (elemento sem linha) é sinal para investigar, não lacuna — um início
    ou uma ligação visual podem não precisar de linha própria.

    `elements`: por elemento, as linhas abertas que o citam e a contagem por estado.
    `unevaluated`: linhas sem associação avaliada (vazia, ausente, N/A sem razão, inválida).
    `global` / `na`: as linhas transversais e as que não têm lugar no processo — listadas
    para revisão, nunca destino por defeito.
    `dead`: ids citados que o mapa não conhece. `retired`: ids retirados ainda citados, com
    os sucessores — reapontar é do escritor, nunca automático."""
    eng = Path(eng)
    cur = load(eng)
    D = _mod("dashboard")
    try:
        md = (eng / SU_FILE).read_text(encoding="utf-8")
    except OSError:
        md = ""
    _h, rows, _s, _d = D["parse_su"](md)
    live_rows = [r for r in rows if not r["resolved"]]
    out = {"map_status": cur["status"], "map_version": "", "elements": {}, "dark": [],
           "unevaluated": [], "global": [], "na": [], "dead": [], "retired": [],
           "rows": len(live_rows)}
    if cur["status"] != "ok":
        out["unevaluated"] = sorted(r["id"] for r in live_rows)
        return out
    m = cur["map"]
    out["map_version"] = m.get("version", "")
    kinds = {}
    for c in COLLECTIONS:
        for el in m[c]:
            kinds[el["id"]] = (c, el.get("kind", ""), el.get("label") or el.get("question", ""))
    retired = {r["id"] for r in m["retired_ids"]}
    succ = successors(m)
    for eid, (c, kind, label) in sorted(kinds.items()):
        if c == "gaps":
            continue
        out["elements"][eid] = {"collection": c, "kind": kind, "label": label, "rows": [],
                                "by_state": {}}
    for r in live_rows:
        forma = r.get("elementos_forma", "ausente")
        if forma == "global":
            out["global"].append(r["id"])
            continue
        if forma == "na":
            out["na"].append(r["id"])
            continue
        if forma != "ids":
            out["unevaluated"].append(r["id"])
            continue
        for eid in r["elementos"]:
            if eid in out["elements"]:
                e = out["elements"][eid]
                e["rows"].append(r["id"])
                e["by_state"][r["state"]] = e["by_state"].get(r["state"], 0) + 1
            elif eid in retired:
                out["retired"].append({"row": r["id"], "element": eid,
                                       "successors": succ.get(eid, [])})
            elif eid in kinds:
                continue                      # uma dúvida (MAPG) citada: é dela, não conta
            else:
                out["dead"].append({"row": r["id"], "element": eid})
    for eid, e in out["elements"].items():
        if not e["rows"] and not (e["collection"] == "nodes" and e["kind"] == "trigger") \
                and e["collection"] != "lanes":
            out["dark"].append(eid)
    for k in ("unevaluated", "global", "na", "dark"):
        out[k] = sorted(set(out[k]))
    return out


# ============================================================= actualidade e revalidação (M4)

STRUCTURAL_EXCLUDE = ("version", "base", "based_on", "revalidations")


def structural_digest(m: dict) -> str:
    """O digest do que o dono valida — a representação —, sem a base, as fontes consumidas
    nem o registo de revalidações. Duas versões com o mesmo digest estrutural dizem o
    mesmo processo; só mudou a evidência sobre a qual o disseram."""
    return _sha_text(canonical({k: v for k, v in m.items() if k not in STRUCTURAL_EXCLUDE}))


def freshness(eng, m: dict) -> dict:
    """A actualidade do mapa publicado face às fontes que consumiu (`based_on`).

    Por fonte que mudou: `anchors: unchanged` (as âncoras citadas resolvem com o mesmo
    digest — mudança fora do que o mapa diz, p. ex. o carimbo de uma recaptura) ou
    `changed`, com os elementos afectados. Uma mudança editorial continua a pedir registo
    (`revalidate`); nunca volta a «actual» por troca de hash."""
    eng = Path(eng)
    refs_by_file: dict = {}
    for where, ev in _all_refs(m):
        refs_by_file.setdefault(split_ref(ev["ref"])[0], []).append((where, ev))
    changed = []
    for s in m.get("based_on") or []:
        target = _safe_rel(eng, s["path"])
        cur = _sha(target.read_bytes()) if target is not None and target.is_file() else ""
        if cur == s["sha256"]:
            continue
        affected = []
        for where, ev in refs_by_file.get(s["path"], []):
            r = resolve_ref(eng, ev["ref"])
            if r["status"] != "ok" or r["digest"] != ev.get("sha256"):
                el = where.split("/")[1]
                if el not in affected:
                    affected.append(el)
        changed.append({"source": s["path"], "missing": not cur,
                        "anchors": "changed" if (affected or not cur) else "unchanged",
                        "affected": sorted(affected)})
    return {"state": "stale" if changed else "current", "changed": changed}


def revalidate(eng, sources, assessment: str, assessed_by: str, reviewed=(),
               date: str | None = None) -> dict:
    """O rascunho que regista a reavaliação das fontes que mudaram (não publica).

    Actualiza o digest em `based_on` das fontes nomeadas e, **só** nos elementos listados
    em `reviewed`, o digest das referências para essas fontes. Um elemento afectado que
    ninguém reviu fica com o digest antigo: o `check` recusa (`MAP-REF-STALE`) até ele ser
    visto. A entrada em `revalidations` diz o quê, porquê, quem e sobre que versão."""
    import datetime
    eng = Path(eng)
    cur = load(eng)
    if cur["status"] != "ok":
        raise ValueError("sem mapa publicado legível ({})".format(cur["status"]))
    if not str(assessment).strip() or not str(assessed_by).strip():
        raise ValueError("a revalidação diz o que se avaliou e quem avaliou")
    m = copy.deepcopy(cur["map"])
    fr = freshness(eng, m)
    moved = {c["source"]: c for c in fr["changed"]}
    sources = list(sources)
    unknown = [s for s in sources if s not in moved]
    if unknown:
        raise ValueError("fonte(s) sem mudança face ao mapa publicado: {}".format(
            ", ".join(unknown)))
    reviewed = set(reviewed)
    previous = {}
    for s in m["based_on"]:
        if s["path"] in sources:
            target = _safe_rel(eng, s["path"])
            previous[s["path"]] = s["sha256"]
            s["sha256"] = _sha(target.read_bytes()) if target is not None and \
                target.is_file() else s["sha256"]
    affected = sorted({e for s in sources for e in moved[s]["affected"]})
    for where, ev in _all_refs(m):
        el = where.split("/")[1]
        if split_ref(ev["ref"])[0] in sources and el in reviewed:
            r = resolve_ref(eng, ev["ref"])
            if r["status"] == "ok":
                ev["sha256"] = r["digest"]
    m.pop("version", None)
    m["base"] = cur["digest"]
    m.setdefault("revalidations", []).append({
        "sources": sorted(sources), "previous": previous, "affected": affected,
        "reviewed": sorted(reviewed), "assessment": str(assessment).strip(),
        "assessed_by": str(assessed_by).strip(),
        "date": date or datetime.date.today().isoformat(),
        "from_version": cur["map"].get("version", "mp-v01")})
    return m


# ============================================================= resumo para a retoma (M4)

TASK_DETAIL = {
    "resume": (),
    "framing": ("output",),
    "options": ("output", "exception", "decision"),
    "blueprint": ("trigger", "step", "decision", "exception", "output"),
    "handoff": ("output", "exception"),
}
SUMMARY_BUDGET = 40


def summary(eng, task: str = "resume", raw: bytes | None = None,
            budget: int = SUMMARY_BUDGET) -> dict:
    """O mapa em contexto compacto, para uma sessão nova ou uma tarefa.

    `raw`: os bytes de `_map/map.json` que o snapshot da retoma leu — o resumo sai desses
    bytes e de mais nenhuns (leitura consistente). Nível 0 sempre: versão, validação,
    actualidade, bloqueios e o estado de cada bloco. O detalhe (nível 1) só para os tipos
    de bloco que a tarefa pede (`TASK_DETAIL`). Acima do orçamento: `partial`, com o que
    ficou de fora e como expandir. Os bloqueios nunca se truncam."""
    eng = Path(eng)
    if raw is not None:
        try:
            m = json.loads(raw.decode("utf-8"))
            digest = _sha(raw)
            status = "ok" if isinstance(m, dict) and m.get("schema_version") == SCHEMA \
                else "unsupported"
        except (UnicodeDecodeError, ValueError):
            m, digest, status = None, _sha(raw), "invalid"
    else:
        cur = load(eng)
        m, digest, status = cur["map"], cur["digest"], cur["status"]
    out = {"status": status, "task": task, "version": "", "digest": digest,
           "validation": {}, "freshness": {}, "blockers": [], "blocks": [],
           "partial": False, "omitted": [], "expand": ""}
    if status != "ok":
        if status != "absent":
            out["blockers"].append({"kind": "map", "detail": "mapa {}".format(status)})
        return out
    out["version"] = m.get("version", "")
    val = validation(eng)
    out["validation"] = {k: val.get(k, "") for k in ("status", "decision", "version",
                                                     "detail")}
    fr = freshness(eng, m)
    out["freshness"] = fr
    pr = project(eng)
    if val["status"] != "validated":
        out["blockers"].append({"kind": "validation",
                                "detail": "mapa {} {}".format(out["version"], val["status"])})
    for c in fr["changed"]:
        out["blockers"].append({"kind": "source", "detail": "{} mudou ({}){}".format(
            c["source"], "âncoras iguais — revalidar" if c["anchors"] == "unchanged"
            else "elementos afectados", ": " + ", ".join(c["affected"]) if c["affected"]
            else "")})
    for o in m["orphans"]:
        if o["reason"] != "out_of_scope" and o["materiality"] != "not-material":
            out["blockers"].append({"kind": "orphan",
                                    "detail": "{} ({}): {}".format(o["ref"], o["reason"],
                                                                   o["note"])})
    for c in ("nodes", "edges", "details"):
        for el in m[c]:
            if el["marker"] == "UNKNOWN":
                out["blockers"].append({"kind": "unknown", "detail": "{} «{}» por saber"
                                        .format(el["id"], el["label"])})
    for d in pr["dead"]:
        out["blockers"].append({"kind": "dead", "detail": "{} cita {}, que o mapa não tem"
                                .format(d["row"], d["element"])})
    for d in pr["retired"]:
        out["blockers"].append({"kind": "retired", "detail": "{} cita {} (retirado → {})"
                                .format(d["row"], d["element"],
                                        ", ".join(d["successors"]) or "sem sucessor")})
    lay = layout(m)
    gaps_on: dict = {}
    for g in m["gaps"]:
        for a in g["attaches_to"]:
            gaps_on.setdefault(a, []).append(g["id"])
    details_on: dict = {}
    for d in m["details"]:
        for a in d["attaches_to"]:
            details_on.setdefault(a, []).append(d)
    lanes = {la["id"]: la["label"] for la in m["lanes"]}
    detail_kinds = TASK_DETAIL.get(task, ())
    blocks = []
    for n in sorted(m["nodes"], key=lambda n: lay["number"][n["id"]]):
        e = pr["elements"].get(n["id"], {})
        b = {"n": lay["number"][n["id"]], "id": n["id"], "kind": n["kind"],
             "label": n["label"], "lane": lanes.get(n["lane"], n["lane"]),
             "marker": n["marker"], "rows": e.get("by_state", {}),
             "gaps": gaps_on.get(n["id"], []),
             "dark": n["id"] in pr["dark"]}
        if n["kind"] in detail_kinds:
            b["detail"] = [{"id": d["id"], "kind": d["kind"], "label": d["label"],
                            "ref": d["ref"]["ref"]} for d in details_on.get(n["id"], [])]
            b["evidence"] = [ev["ref"] for ev in n["evidence"]]
        blocks.append(b)
    if len(blocks) > budget:
        out["partial"] = True
        out["omitted"] = [b["id"] for b in blocks[budget:]]
        blocks = blocks[:budget]
        out["expand"] = ("python library/kernel/tools/process_map.py summary --engagement {} "
                         "--task {} --budget {} --json".format(eng.name, task,
                                                             budget + len(out["omitted"])))
    out["blocks"] = blocks
    return out


# ============================================================= render (vista derivada)

KIND_LABEL = {"trigger": "início", "step": "passo", "decision": "decisão",
              "exception": "exceção", "output": "saída"}
LANE_LABEL = {"actor": "quem faz", "tool": "ferramenta", "channel": "canal",
              "consumer": "quem recebe", "downstream": "sistema a jusante"}
MARK_LABEL = {"OBSERVED": "observado", "INFERRED": "inferido", "HYPOTHESIS": "hipótese",
              "UNKNOWN": "por saber"}
ORPHAN_LABEL = {"gap_in_map": "falta representar", "out_of_scope": "fora do âmbito",
                "undetermined": "por avaliar"}
VALIDATION_LABEL = {"validated": "validado pelo dono", "stale": "validação de outra versão",
                    "invalid": "validação inválida", "not_validated": "por validar",
                    "no_map": "sem mapa"}
RENDER_REL = "process-map.html"

CSS = """
:root{--bg:#EDE9DF;--panel:#FFFFFF;--surface:#F5F2EC;--line:#D7CEC5;--ink:#39383A;
--ink2:#6B635B;--accent:#FF5A00;--a-tint:#FFE7D8;--brand:#7A1400;--warn:#8F3200;
--f-ui:'Segoe UI',system-ui,-apple-system,Arial,sans-serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#191A1C;
--panel:#232427;--surface:#2B2C30;--line:#3B3C42;--ink:#EDE9DF;--ink2:#B5AEA4;
--a-tint:#431800;--brand:#FFB183;--warn:#E0A33A}}
:root[data-theme="dark"]{--bg:#191A1C;--panel:#232427;--surface:#2B2C30;--line:#3B3C42;
--ink:#EDE9DF;--ink2:#B5AEA4;--a-tint:#431800;--brand:#FFB183;--warn:#E0A33A}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 var(--f-ui)}
main{max-width:1200px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:28px 0 8px}
.sub{color:var(--ink2);margin:0 0 12px}
.badge{display:inline-block;padding:2px 10px;border-radius:999px;background:var(--a-tint);
color:var(--brand);font-weight:600;font-size:12px}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 12px}
.stat b{font-size:16px;margin-right:4px}
.legend{display:flex;flex-wrap:wrap;gap:16px;color:var(--ink2);font-size:12px;margin:8px 0}
.flow{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:8px}
svg{display:block}
svg .lane-bg{fill:var(--surface)}svg .lane-sep{stroke:var(--line)}
svg .lane-t{fill:var(--ink);font:600 12px var(--f-ui)}
svg .lane-k{fill:var(--ink2);font:11px var(--f-ui)}
svg .node{fill:var(--panel);stroke:var(--ink2);stroke-width:1.2}
svg .node.exception{stroke:var(--warn);stroke-dasharray:5 3}
svg .node.unknown{stroke-dasharray:2 3}
svg .node.output{stroke:var(--brand);stroke-width:2}
svg .node.decision{fill:var(--a-tint)}
svg .nt{fill:var(--ink);font:12px var(--f-ui)}
svg .nm{fill:var(--warn);font:italic 11px var(--f-ui)}
svg .ns{fill:var(--ink2);font:11px var(--f-ui)}
svg .num{fill:var(--accent)}svg .numt{fill:#FFFFFF;font:600 11px var(--f-ui)}
svg .edge{fill:none;stroke:var(--ink2);stroke-width:1.3}
svg .edge.exception{stroke:var(--warn);stroke-dasharray:6 4}
svg .el{fill:var(--ink2);font:11px var(--f-ui)}
svg .q{fill:var(--warn);font:700 13px var(--f-ui)}
table{width:100%;border-collapse:collapse;background:var(--panel);
border:1px solid var(--line);border-radius:8px;font-size:13px}
th,td{text-align:left;vertical-align:top;padding:6px 10px;border-bottom:1px solid var(--line)}
th{background:var(--surface);font-weight:600}
td code{font-size:12px;overflow-wrap:anywhere}
.tbl{overflow-x:auto}
ul.q{margin:4px 0 12px;padding-left:20px}
.empty{color:var(--ink2)}
"""

COL_W, NODE_W, NODE_H, LANE_LBL, PAD_Y, GAP_Y = 200, 164, 66, 170, 18, 26

# As faixas desenham-se agrupadas pelo tipo (`lane.kind`), por esta ordem e com estes nomes;
# o subtítulo diz quem ou o quê. O mapa guarda as faixas como estão: agrupar é só da vista.
BAND_ORDER = ("actor", "tool", "channel", "consumer", "downstream")
BAND_TITLE = {"actor": "Humano", "tool": "Ferramenta", "channel": "Publicação",
              "consumer": "Quem recebe", "downstream": "Sistema a jusante"}


def _e(text) -> str:
    import html
    return html.escape(str(text), quote=True)


def _wrap(label: str, width: int = 24, lines: int = 3) -> list:
    words, out, cur = str(label).split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= width:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][:max(0, width - 1)] + "…"
    return out or [""]


def _ranks(m: dict) -> dict:
    """Coluna de cada nó = a sua posição no fluxo: 0 para quem não tem antecessor, senão
    um a mais do que o antecessor mais adiantado. Só contam ligações para a frente (pela
    `order`, empate pelo id) — um retorno nunca empurra a coluna. Uma exceção alcançada só
    por ligação de exceção fica na coluna de onde sai, junto do passo que a origina."""
    key = {n["id"]: (n["order"], n["id"]) for n in m["nodes"]}
    fwd = [e for e in m["edges"] if e["src"] in key and e["dst"] in key
           and key[e["src"]] < key[e["dst"]]]
    rank: dict = {}
    for nid in sorted(key, key=lambda n: key[n]):
        into = [e for e in fwd if e["dst"] == nid]
        flow = [rank[e["src"]] + 1 for e in into if e["kind"] != "exception"]
        side = [rank[e["src"]] for e in into if e["kind"] == "exception"]
        rank[nid] = max(flow) if flow else (max(side) if side else 0)
    return rank


def layout(m: dict) -> dict:
    """Posições deterministas. Faixas agrupadas pelo tipo (`BAND_ORDER`), só as que têm nós;
    coluna pela posição no fluxo (`_ranks`); na mesma faixa e coluna, empilhados por `order`
    e id, as exceções por baixo. A numeração segue o caminho principal e depois as exceções.
    Mesmos inputs, mesmas posições."""
    used = {n["lane"] for n in m["nodes"]}
    kinds = [k for k in BAND_ORDER if any(la["kind"] == k and la["id"] in used
                                          for la in m["lanes"])]
    band_of = {la["id"]: la["kind"] for la in m["lanes"]}
    count = {}
    for n in m["nodes"]:
        count[n["lane"]] = count.get(n["lane"], 0) + 1
    # membros por frequência (empate pela ordem das faixas): o primeiro é o de omissão —
    # os passos dele não repetem o nome; os dos outros dizem quem os faz
    order = {la["id"]: i for i, la in enumerate(m["lanes"])}
    member_ids = {k: sorted((la["id"] for la in m["lanes"] if la["kind"] == k and la["id"] in used),
                            key=lambda lid: (-count[lid], order[lid])) for k in kinds}
    label_of = {la["id"]: la["label"] for la in m["lanes"]}
    members = {k: [label_of[lid] for lid in member_ids[k]] for k in kinds}
    rank = _ranks(m)
    stacks: dict = {}
    for n in sorted(m["nodes"], key=lambda n: (n["kind"] == "exception", n["order"], n["id"])):
        stacks.setdefault((band_of[n["lane"]], rank[n["id"]]), []).append(n["id"])
    depth = {k: max([len(v) for (b, _r), v in stacks.items() if b == k] or [1]) for k in kinds}
    y, band_y = 0, {}
    for k in kinds:
        h = PAD_Y * 2 + depth[k] * NODE_H + (depth[k] - 1) * GAP_Y
        band_y[k] = (y, h)
        y += h
    pos = {}
    for (k, r), ids in stacks.items():
        top = band_y[k][0] + PAD_Y
        for i, nid in enumerate(ids):
            pos[nid] = (LANE_LBL + 20 + r * COL_W, top + i * (NODE_H + GAP_Y))
    reached = {e["dst"] for e in m["edges"] if e["kind"] != "exception"}
    exc = {n["id"] for n in m["nodes"] if n["kind"] == "exception" and n["id"] not in reached}
    number = {nid: i + 1 for i, nid in enumerate(sorted(
        pos, key=lambda n: (n in exc, rank[n], pos[n][1], n)))}
    cols = max(rank.values(), default=0) + 1
    width = LANE_LBL + 40 + cols * COL_W - (COL_W - NODE_W)
    back = any(e["src"] in pos and e["dst"] in pos and pos[e["dst"]][0] < pos[e["src"]][0]
               for e in m["edges"])
    return {"pos": pos, "band_y": band_y, "bands": kinds, "members": members,
            "named": {lid for k in kinds for lid in member_ids[k][1:]}, "band_of": band_of,
            "width": width, "height": max(y, 1) + (30 if back else 0), "number": number}


def _edge_path(sx, sy, dx, dy, height):
    """Ligação em ângulo recto entre dois nós; `(d, lx, ly, anchor)`."""
    if sx == dx:
        if dy > sy:     # mesma coluna, por baixo: desce a direito
            x = sx + NODE_W / 2
            return ("M{:.0f},{:.0f} V{:.0f}".format(x, sy + NODE_H, dy),
                    x + 6, (sy + NODE_H + dy) / 2 + 4, "start")
        gx = sx + NODE_W + (COL_W - NODE_W) / 2   # por cima: contorna pela direita
        return ("M{:.0f},{:.0f} H{:.0f} V{:.0f} H{:.0f}".format(
            sx + NODE_W, sy + NODE_H / 2, gx, dy + NODE_H / 2, sx + NODE_W),
            gx + 4, (sy + dy) / 2 + NODE_H / 2, "start")
    if dx > sx:
        x1, y1, x2, y2 = sx + NODE_W, sy + NODE_H / 2, dx, dy + NODE_H / 2
        mx = x2 - (COL_W - NODE_W) / 2
        if abs(y1 - y2) < 1:
            return ("M{:.0f},{:.0f} H{:.0f}".format(x1, y1, x2),
                    (x1 + x2) / 2, y1 - 6, "middle")
        return ("M{:.0f},{:.0f} H{:.0f} V{:.0f} H{:.0f}".format(x1, y1, mx, y2, x2),
                mx + 4, (y1 + y2) / 2, "start")
    # para trás: por baixo do diagrama, sem atravessar os nós
    x1, x2 = sx + NODE_W / 2, dx + NODE_W / 2
    low = height - 12
    return ("M{:.0f},{:.0f} V{:.0f} H{:.0f} V{:.0f}".format(x1, sy + NODE_H, low, x2,
                                                         dy + NODE_H),
            (x1 + x2) / 2, low - 4, "middle")


def render_svg(m: dict) -> str:
    """O fluxograma por faixas, em SVG inline. Sem limite de nós: o diagrama cresce e a
    moldura desliza; a tabela de passos é a vista completa."""
    lay = layout(m)
    pos, W, H = lay["pos"], lay["width"], lay["height"]
    gap_on = set()
    for g in m["gaps"]:
        gap_on.update(g["attaches_to"])
    for d in m["details"]:
        if d["id"] in gap_on:
            gap_on.update(d["attaches_to"])
    lane_label = {la["id"]: la["label"] for la in m["lanes"]}
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}" viewBox="0 0 {} {}" '
         'role="img" aria-label="Fluxograma do processo por faixas">'.format(W, H, W, H),
         '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
         'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
         'fill="currentColor"/></marker></defs>']
    for i, k in enumerate(lay["bands"]):
        y, h = lay["band_y"][k]
        if i % 2 == 0:
            o.append('<rect class="lane-bg" x="0" y="{}" width="{}" height="{}"/>'.format(y, W, h))
        o.append('<line class="lane-sep" x1="0" y1="{0}" x2="{1}" y2="{0}"/>'.format(y + h, W))
        o.append('<text class="lane-t" x="12" y="{}">{}</text>'.format(y + 26, _e(BAND_TITLE[k])))
        for j, line in enumerate(_wrap(" · ".join(lay["members"][k]), 24, 3)):
            o.append('<text class="lane-k" x="12" y="{}">{}</text>'.format(y + 43 + j * 14,
                                                                          _e(line)))
    for e in sorted(m["edges"], key=lambda e: e["id"]):
        if e["src"] not in pos or e["dst"] not in pos:
            continue
        (sx, sy), (dx, dy) = pos[e["src"]], pos[e["dst"]]
        d, lx, ly, anchor = _edge_path(sx, sy, dx, dy, H)
        cls = "edge exception" if e["kind"] == "exception" else "edge"
        o.append('<path class="{}" d="{}" marker-end="url(#arr)" style="color:var(--ink2)">'
                 '<title>{}</title></path>'.format(cls, d, _e(e.get("label") or e["id"])))
        if e.get("label"):
            o.append('<text class="el" x="{:.0f}" y="{:.0f}" text-anchor="{}">{}</text>'
                     .format(lx, ly, anchor, _e(e["label"])))
    for n in sorted(m["nodes"], key=lambda n: n["id"]):
        x, y = pos[n["id"]]
        cls = "node " + n["kind"] + (" unknown" if n["marker"] == "UNKNOWN" else "")
        o.append('<g><title>{} — {} ({})</title>'.format(_e(n["label"]),
                                                        _e(KIND_LABEL[n["kind"]]), _e(n["id"])))
        if n["kind"] == "decision":
            cx, cy = x + NODE_W / 2, y + NODE_H / 2
            o.append('<polygon class="{}" points="{:.0f},{:.0f} {:.0f},{:.0f} {:.0f},{:.0f} '
                     '{:.0f},{:.0f}"/>'.format(cls, cx, y - 10, x + NODE_W + 10, cy, cx,
                                                y + NODE_H + 10, x - 10, cy))
        else:
            rx = 28 if n["kind"] == "trigger" else 6
            o.append('<rect class="{}" x="{}" y="{}" width="{}" height="{}" rx="{}"/>'.format(
                cls, x, y, NODE_W, NODE_H, rx))
        sub = []
        if n["marker"] != "OBSERVED":
            sub.append(MARK_LABEL[n["marker"]])
        if n["lane"] in lay["named"]:
            sub.append(lane_label[n["lane"]])
        dec = n["kind"] == "decision"
        sub_line = _wrap(" · ".join(sub), 20 if dec else 27, 1)[0] if sub else ""
        lines = _wrap(n["label"], 18 if dec else 24, 2 if sub_line else 3)
        top = y + NODE_H / 2 - (len(lines) - 1) * 7 - (7 if sub_line else 0)
        for i, line in enumerate(lines):
            o.append('<text class="nt" x="{:.0f}" y="{:.0f}" text-anchor="middle">{}</text>'
                     .format(x + NODE_W / 2, top + i * 14 + 4, _e(line)))
        if sub_line:
            cls_s = "nm" if n["marker"] != "OBSERVED" else "ns"
            o.append('<text class="{}" x="{:.0f}" y="{:.0f}" text-anchor="middle">{}</text>'
                     .format(cls_s, x + NODE_W / 2, y + NODE_H - (4 if dec else 9),
                             _e(sub_line)))
        num = lay["number"][n["id"]]
        o.append('<circle class="num" cx="{}" cy="{}" r="10"/><text class="numt" x="{}" y="{}" '
                 'text-anchor="middle">{}</text>'.format(x, y, x, y + 4, num))
        if n["id"] in gap_on:
            o.append('<text class="q" x="{}" y="{}">?</text>'.format(x + NODE_W - 12, y + 16))
        o.append('</g>')
    o.append('</svg>')
    return "".join(o)


def _refs_html(evs) -> str:
    return "<br>".join("<code>{}</code>".format(_e(ev["ref"])) for ev in evs) or \
        '<span class="empty">—</span>'


def render_html(eng) -> str:
    """A página completa do mapa publicado, em linguagem de negócio. Mesmos inputs, mesmos
    bytes: nenhum relógio, nenhum id aleatório. Mostra a incompletude com ou sem
    validação — a aprovação nunca esconde uma dúvida."""
    eng = Path(eng)
    cur = load(eng)
    if cur["status"] != "ok":
        raise ValueError("sem mapa publicado legível ({}): {}".format(cur["status"],
                                                                    cur["detail"]))
    m = cur["map"]
    val = validation(eng)
    incomplete = incomplete_sources(eng)
    lay = layout(m)
    lanes = {la["id"]: la for la in m["lanes"]}
    by_num = sorted(m["nodes"], key=lambda n: lay["number"][n["id"]])
    details_on: dict = {}
    for d in m["details"]:
        for a in d["attaches_to"]:
            details_on.setdefault(a, []).append(d)
    count = {k: sum(1 for n in m["nodes"] if n["kind"] == k) for k in KIND_LABEL}
    unknown = sum(1 for c in ("nodes", "edges", "details") for el in m[c]
                  if el["marker"] == "UNKNOWN")
    open_orphans = [o for o in m["orphans"] if o["reason"] != "out_of_scope"]
    build = _sha_text(canonical({"map": cur["digest"], "validation": val["status"],
                                 "decision": val.get("decision", ""),
                                 "incomplete": incomplete}))[:12]
    o = ['<!DOCTYPE html>\n<html lang="pt">\n<head>\n<meta charset="utf-8">\n'
         '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
         '<title>Mapa do processo</title>\n<!-- process-map {} · {} · build {} -->\n'
         '<style>{}</style>\n</head>\n<body>\n<main>\n'.format(
             _e(m["version"]), _e(cur["digest"][:12]), build, CSS)]
    o.append('<h1>Mapa do processo — {}</h1>'.format(_e(m["engagement_id"])))
    o.append('<p class="sub">Processo actual, versão {} · <span class="badge">{}</span>{}</p>'
             .format(_e(m["version"][4:]), _e(VALIDATION_LABEL[val["status"]]),
                     " — {}".format(_e(val["detail"])) if val["detail"] else
                     " ({}{})".format(_e(val.get("decision", "")),
                                      ", âmbito: " + _e(val["scope"]) if val.get("scope")
                                      else "")))
    o.append('<div class="stats">')
    for k in ("step", "decision", "exception", "output"):
        o.append('<span class="stat"><b>{}</b>{}</span>'.format(
            count[k], {"step": "passos", "decision": "decisões", "exception": "exceções",
                       "output": "saídas"}[k]))
    o.append('<span class="stat"><b>{}</b>dúvidas por esclarecer</span>'.format(
        len(m["gaps"]) + len(open_orphans)))
    o.append('<span class="stat"><b>{}</b>por saber</span></div>'.format(unknown))
    o.append('<div class="legend"><span>① … = passo da tabela</span><span>contorno '
             'tracejado = exceção ou desvio</span><span>? = há dúvida por esclarecer</span>'
             '<span>inferido / hipótese / por saber (INFERRED / HYPOTHESIS / UNKNOWN) = '
             'o que a evidência ainda não mostra directamente</span></div>')
    o.append('<div class="flow">{}</div>'.format(render_svg(m)))

    o.append('<h2>Passos</h2><div class="tbl"><table><thead><tr><th>Nº</th><th>O que '
             'acontece</th><th>Quem / onde</th><th>Tipo</th><th>Como se sabe</th>'
             '<th>Fontes</th><th>Detalhe</th></tr></thead><tbody>')
    for n in by_num:
        mine = details_on.get(n["id"], [])
        det = "".join("<div>{}: {} <code>{}</code>{}</div>".format(
            _e(d["kind"]), _e(d["label"]), _e(d["ref"]["ref"]),
            " (×{})".format(d["count"]) if d.get("count") else "")
            for d in mine) or '<span class="empty">—</span>'
        if len(mine) > 3:
            det = "<details><summary>{} detalhes</summary>{}</details>".format(len(mine), det)
        o.append('<tr><td>{}</td><td>{} <span class="empty">({})</span>{}</td><td>{}</td>'
                 '<td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                     lay["number"][n["id"]], _e(n["label"]), _e(n["id"]),
                     "<br>prazo: " + _e(n["sla"]) if n.get("sla") else "",
                     _e(lanes[n["lane"]]["label"]), _e(KIND_LABEL[n["kind"]]),
                     _e(MARK_LABEL[n["marker"]]), _refs_html(n["evidence"]), det))
    o.append('</tbody></table></div>')

    o.append('<h2>Ligações</h2><div class="tbl"><table><thead><tr><th>De</th><th>Para</th>'
             '<th>O que passa</th><th>Tipo</th><th>Como se sabe</th><th>Fontes</th></tr>'
             '</thead><tbody>')
    for e in sorted(m["edges"], key=lambda e: e["id"]):
        carries = ", ".join(e.get("carries") or []) or e.get("label", "") or "—"
        o.append('<tr><td>{}</td><td>{}</td><td>{} <span class="empty">({})</span></td>'
                 '<td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                     lay["number"].get(e["src"], "?"), lay["number"].get(e["dst"], "?"),
                     _e(carries), _e(e["id"]),
                     {"normal": "caminho normal", "exception": "exceção",
                      "branch": "ramo de decisão"}[e["kind"]],
                     _e(MARK_LABEL[e["marker"]]), _refs_html(e["evidence"])))
    o.append('</tbody></table></div>')

    o.append('<h2>A confirmar</h2>')
    groups = questions(eng)
    if not any(g["items"] for g in groups):
        o.append('<p class="empty">Sem dúvidas registadas no mapa.</p>')
    for g in groups:
        if not g["items"]:
            continue
        o.append('<h3>{}</h3><ul class="q">'.format(_e(g["title"])))
        for it in g["items"]:
            about = ", ".join(str(lay["number"].get(a, a)) for a in it["about"])
            o.append('<li>{}{}{} <span class="empty">({})</span></li>'.format(
                _e(it["question"]), " — sobre " + _e(about) if about else "",
                " — responde: " + _e(it["respondent"]) if it["respondent"] else "",
                _e(it["id"])))
        o.append('</ul>')

    o.append('<h2>Fora do mapa</h2>')
    if not m["orphans"]:
        o.append('<p class="empty">Tudo o que a captura produziu tem lugar no mapa.</p>')
    else:
        o.append('<div class="tbl"><table><thead><tr><th>O quê</th><th>Situação</th>'
                 '<th>Importância</th><th>Porquê</th></tr></thead><tbody>')
        for orp in m["orphans"]:
            o.append('<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}{}</td></tr>'
                     .format(_e(orp["ref"]), _e(ORPHAN_LABEL[orp["reason"]]),
                             _e({"material": "material", "not-material": "não material",
                                 "undetermined": "por avaliar"}[orp["materiality"]]),
                             _e(orp["note"]),
                             " (decisão {})".format(_e(orp["decision_ref"]))
                             if orp.get("decision_ref") else ""))
        o.append('</tbody></table></div>')

    o.append('<h2>Fontes</h2>')
    if incomplete:
        o.append('<p><b>Leitura incompleta:</b></p><ul class="q">')
        for s in incomplete:
            o.append('<li><code>{}</code> — {}{}</li>'.format(
                _e(s["path"]), _e(s["status"]), " — " + _e(s["reason"]) if s["reason"] else ""))
        o.append('</ul>')
    o.append('<div class="tbl"><table><thead><tr><th>Fonte consumida</th><th>Impressão '
             'digital</th></tr></thead><tbody>')
    for s in sorted(m["based_on"], key=lambda s: s["path"]):
        o.append('<tr><td><code>{}</code></td><td><code>{}</code></td></tr>'.format(
            _e(s["path"]), _e(s["sha256"][:12])))
    o.append('</tbody></table></div>\n</main>\n</body>\n</html>\n')
    return "".join(o)


def render(eng) -> Path:
    """Escreve `<engagement>/process-map.html` — vista derivada, nunca fonte de verdade;
    escrita atómica e só quando os bytes mudam."""
    eng = Path(eng)
    html_text = render_html(eng)
    out = eng / RENDER_REL
    if out.is_file() and out.read_text(encoding="utf-8") == html_text:
        return out
    _mod("operation")["_atomic_write"](out, html_text)
    return out


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
    for name in ("check", "stamp", "publish", "status", "render", "questions",
                 "approval-block", "project", "summary", "revalidate"):
        p = sub.add_parser(name)
        p.add_argument("--engagement", required=True)
        if name in ("check", "stamp", "publish"):
            p.add_argument("--draft", required=True)
        if name == "summary":
            p.add_argument("--task", default="resume", choices=sorted(TASK_DETAIL))
            p.add_argument("--budget", type=int, default=SUMMARY_BUDGET)
        if name == "revalidate":
            p.add_argument("--source", action="append", required=True)
            p.add_argument("--assessment", required=True)
            p.add_argument("--by", required=True)
            p.add_argument("--reviewed", action="append", default=[])
            p.add_argument("--out", required=True)
        if name == "approval-block":
            p.add_argument("--scope", required=True)
            p.add_argument("--conditions", required=True)
            p.add_argument("--validated-by", required=True)
            p.add_argument("--timestamp")
        p.add_argument("--json", action="store_true")
    utf8_console()
    args = ap.parse_args(argv)
    try:
        eng = find_engagement(args.engagement)
        if args.cmd == "status":
            st = load(eng)
            st = {k: v for k, v in st.items() if k != "map"} | {
                "version": (st["map"] or {}).get("version", "")}
            val = validation(eng) if st["status"] == "ok" else {"status": "no_map",
                                                                 "detail": ""}
            st["validation"] = {k: v for k, v in val.items() if k != "blocks"}
            _print(st, args.json, ["mapa publicado: {} {} {}".format(
                st["status"], st["version"], st["detail"]).rstrip(),
                "validação: {} {}".format(val["status"], val.get("detail", "")).rstrip()])
            return EXIT_OK if st["status"] in ("ok", "absent") else EXIT_ERROR
        if args.cmd == "render":
            out = render(eng)
            _print({"path": str(out)}, args.json, ["vista: {}".format(out)])
            return EXIT_OK
        if args.cmd == "summary":
            s = summary(eng, args.task, budget=args.budget)
            lines = ["mapa {} {} · validação {} · actualidade {} · {} bloco(s){}".format(
                s["status"], s["version"], (s["validation"] or {}).get("status", "—"),
                (s["freshness"] or {}).get("state", "—"), len(s["blocks"]),
                " (parcial: {} fora)".format(len(s["omitted"])) if s["partial"] else "")]
            lines += ["  bloqueio [{}] {}".format(b["kind"], b["detail"]) for b in s["blockers"]]
            _print(s, args.json, lines)
            return EXIT_OK
        if args.cmd == "revalidate":
            if _inside(eng, Path(args.out)):
                print("recusado: o rascunho tem de ficar fora do engagement", file=sys.stderr)
                return EXIT_ERROR
            try:
                d = revalidate(eng, args.source, args.assessment, args.by, args.reviewed)
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return EXIT_ERROR
            Path(args.out).write_text(canonical(d), encoding="utf-8")
            _print({"draft": args.out, "revalidation": d["revalidations"][-1]}, args.json,
                   ["rascunho de revalidação: {} (afectados {}, revistos {})".format(
                       args.out, d["revalidations"][-1]["affected"],
                       d["revalidations"][-1]["reviewed"])])
            return EXIT_OK
        if args.cmd == "project":
            pr = project(eng)
            _print(pr, args.json, [
                "mapa {} {}: {} linhas abertas · sem associação avaliada {} · GLOBAL {} · "
                "N/A {} · elementos sem linhas {} · ids desconhecidos {} · ids retirados {}"
                .format(pr["map_status"], pr["map_version"], pr["rows"],
                        len(pr["unevaluated"]), len(pr["global"]), len(pr["na"]),
                        len(pr["dark"]), len(pr["dead"]), len(pr["retired"]))])
            return EXIT_OK
        if args.cmd == "questions":
            qs = questions(eng)
            lines = []
            for g in qs:
                lines.append("{} — {}".format(g["title"], g["validates"] or ""))
                lines += ["  - {} ({})".format(i["question"], i["id"]) for i in g["items"]]
            _print(qs, args.json, lines or ["sem mapa publicado"])
            return EXIT_OK
        if args.cmd == "approval-block":
            try:
                text = approval_block(eng, args.scope, args.conditions, args.validated_by,
                                      args.timestamp)
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return EXIT_ERROR
            _print({"block": text}, args.json, [text])
            return EXIT_OK
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
