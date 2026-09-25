"""M0 — reprodução das observações de base do mapa de conhecimento do processo.

Corre sobre CÓPIAS temporárias de fixtures; não escreve em nenhum engagement nem em
`library/`. Escreve apenas `observations.json` ao lado deste script.

    python docs/process-map/M0/reproduce.py

Provas:
  inventory   um modelo com PM-901, CALC-901 (em dois workbooks) e uma etiqueta material
              de §4: quais entram como unidades do denominador de cobertura
  ids         o leitor de citações perante os prefixos candidatos do mapa
  f06         blueprint v01 estruturalmente limpo e funcionalmente incompleto
  capture     ordem índice de evidência / L2 e leitura do P-0 na skill de captura
  delivery    se release/trace consultam a cobertura
"""
from __future__ import annotations

import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "library" / "kernel" / "tools"
FIX = ROOT / ".claude" / "tests" / "fixtures" / "coverage"
ENG = FIX / "fx-coverage-f06"
RECORDS = FIX / "records"
PLACEHOLDER = "b31c2af5507500ef2272d791693f3335b4be63f86ff8a781a8436d1cc253fb81"
BP01 = "_blueprint/ux-blueprint_v01.yaml"

C = runpy.run_path(str(TOOLS / "coverage.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
D = runpy.run_path(str(TOOLS / "dashboard.py"))


def copy_engagement(tmp: Path) -> Path:
    eng = tmp / ENG.name
    shutil.copytree(ENG, eng)
    return eng


# ------------------------------------------------------------------ inventory

PM_APPEND = """

<!-- M0 probe -->
| PM-901 | Regra sonda M0: o preço de referência soma o prémio ao spread | Assumed | registo-de-lotes.xlsx!Calc!B2 | 2026-01-01 | financeiro |

- `OUT-M0` Saída sonda: preço de referência enviado aos comerciais — OBSERVED (registo-de-lotes.xlsx!Calc!B9)

### CALC-901 — preço de referência (sonda M0)
| output | pseudo-código | locators | por confirmar |
|---|---|---|---|
| Calc!B9 | B9 = B2 + B3 | registo-de-lotes.xlsx!Calc!B2:B9 | — |
"""


def calc_chain(wb: str) -> dict:
    return {"tool": {"name": "xlsx_extract", "pass": "calc-chain"},
            "blocks": [{"id": "CALC-003", "sheet": "Calc", "anchor": "B9",
                        "label": "sonda M0 " + wb, "steps": []}]}


def probe_inventory(tmp: Path) -> dict:
    eng = copy_engagement(tmp)
    pm = eng / "_capture" / "process-model.md"
    pm.write_text(pm.read_text(encoding="utf-8") + PM_APPEND, encoding="utf-8")
    for wb in ("registo-de-lotes.xlsx", "registo-de-lotes-2024.xlsx"):
        (eng / "_capture" / (wb + ".calc-chain.json")).write_text(
            json.dumps(calc_chain(wb)), encoding="utf-8")
    inv = C["build_inventory"](eng)
    keys = sorted(u["unit_key"] for u in inv["units"])
    pm_units = [k for k in keys if k.startswith("_capture/process-model.md")]
    calc_units = [k for k in keys if "calc-chain" in k or "CALC-" in k]
    return {
        "probe": "PM-901 + CALC-901 (§4bis) + CALC-003 em dois calc-chain.json + etiqueta OUT-M0 (§4)",
        "pm_901_is_unit": "_capture/process-model.md#PM-901" in keys,
        "calc_901_is_unit": any("CALC-901" in k for k in keys),
        "calc_chain_units": calc_units,
        "out_m0_label_is_unit": any("OUT-M0" in k for k in keys),
        "process_model_unit_kinds": sorted({u["class"] for u in inv["units"]
                                            if u["unit_key"].startswith("_capture/process-model.md")}),
        "process_model_units": len(pm_units),
    }


# ------------------------------------------------------------------ ids

def probe_ids(tmp: Path) -> dict:
    eng = copy_engagement(tmp)
    samples = ["MAP-D-001", "MAPL-001", "MAPN-001", "MAPE-001", "MAPD-001", "MAPG-001",
               "_map/map.json#MAPN-004", "_capture/registo-de-lotes.xlsx.calc-chain.json#CALC-003"]
    return {s: R["cited_sources"](eng, "ver " + s) for s in samples}


# ------------------------------------------------------------------ f06

def hydrate(eng: Path, rec: dict) -> dict:
    basis = rec.get("basis")
    if not isinstance(basis, dict):
        return rec
    inv = C["build_inventory"](eng)
    synth = tuple(sorted(s for s in ((rec.get("deliverable") or {}).get("authority_sources")
                                     or []) if str(s).startswith("_synthesis/")))
    now = C["compute_basis"](eng, inv, rec["stage"], rec.get("target"),
                             authorities=basis.get("authorities", ()),
                             synthesis_authorities=synth)
    for field in ("inventory_sha256", "su_fingerprint", "decision_fingerprint"):
        if basis.get(field) == PLACEHOLDER:
            basis[field] = now[field]
    return rec


def probe_f06(tmp: Path) -> dict:
    eng = copy_engagement(tmp)
    text = (eng / BP01).read_text(encoding="utf-8")
    rows = D["parse_su"]((eng / "shared-understanding.md").read_text(encoding="utf-8"))[1]
    issues = D["bp_validate"](text, Path(BP01).name, D["bp_pack_cfg"]("pp"),
                              {r["id"] for r in rows}, D["bp_loader"](eng))
    (eng / "_coverage").mkdir(exist_ok=True)
    for name in ("rec-v01-reconciliation-complete", "rec-v02-blueprint-missing"):
        rec = hydrate(eng, json.loads((RECORDS / (name + ".json")).read_text(encoding="utf-8")))
        (eng / "_coverage" / ("coverage_%s.json" % rec["version"])).write_text(
            json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-B", str(TOOLS / "coverage.py"), "check",
                        "--engagement", str(eng), "--stage", "blueprint", "--target", BP01,
                        "--json"], cwd=str(ROOT), env=env, text=True, capture_output=True,
                       encoding="utf-8", errors="replace")
    out = json.loads(r.stdout)
    rec = json.loads((RECORDS / "rec-v02-blueprint-missing.json").read_text(encoding="utf-8"))
    return {
        "structural_blocks_v01": len([i for i in issues if i["severity"] == "block"]),
        "structural_issues_v01": len(issues),
        "coverage_check_exit": r.returncode,
        "coverage": out.get("coverage"),
        "eligible": out.get("eligible"),
        "missing_in_record": sorted(",".join(c["requirement_refs"]) for c in rec["coverage"]
                                    if c["assessment"]["status"] == "missing"),
        "note": "o registo semântico já vem escrito na fixture: prova o bloqueio de uma "
                "omissão CONHECIDA, não a descoberta autónoma pelo agente",
    }


# ------------------------------------------------------------------ capture

def probe_capture() -> dict:
    skill = (ROOT / ".claude" / "skills" / "aisa-capture" / "SKILL.md").read_text(encoding="utf-8")
    lines = skill.splitlines()

    def first(pattern):
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                return i
        return None

    return {
        "l2_reads_index_line": first(r"^\s*a2\..*evidence-index"),
        "index_rebuilt_line": first(r"text_extract\.py --index"),
        "index_rebuilt_after_l2": (first(r"text_extract\.py --index") or 0)
        > (first(r"^\s*a2\..*evidence-index") or 10 ** 9),
        "mentions_enquadramento": "enquadramento" in skill,
        "template_mentions_enquadramento": "enquadramento" in (
            ROOT / "library" / "kernel" / "capture-templates" / "process-model.template.md"
        ).read_text(encoding="utf-8"),
    }


def probe_delivery() -> dict:
    def refers(name):
        return bool(re.search(r"\bcoverage\b", (TOOLS / name).read_text(encoding="utf-8")))
    return {"release_py_refers_coverage": refers("release.py"),
            "trace_py_refers_coverage": refers("trace.py"),
            "functional_py_refers_coverage": refers("functional.py")}


def main() -> int:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True,
                          capture_output=True).stdout.strip()
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        obs = {"base_sha": head,
               "inventory": probe_inventory(tmp / "inv"),
               "ids": probe_ids(tmp / "ids"),
               "f06": probe_f06(tmp / "f06"),
               "capture": probe_capture(),
               "delivery": probe_delivery()}
    out = Path(__file__).with_name("observations.json")
    out.write_text(json.dumps(obs, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps(obs, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
