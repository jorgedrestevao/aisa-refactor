"""M2 — demonstração: captura de fixture → mapa legível → dúvida agrupada → resposta → nova
revisão → validação aplicável (PLANO.md, M2 → Demonstração).

    python docs/process-map/M2/demo.py [<pasta de saída>]

Sobre uma CÓPIA temporária da fixture `fixtures/calc-capture/fx-calc-bancas`:
  - captura determinista REAL (L1 extracção + L3 replay + cadeia de cálculo + índice);
  - process-model e rascunho do mapa escritos por este script — o papel da L2 e do passo 5d,
    aqui sintético e declarado como tal (não prova compreensão semântica: isso é o M5);
  - o dono é SIMULADO (dados de teste): as respostas e a aprovação estão rotuladas;
  - answers.md e decisions.md são escritos pelo escritor real (`resolve.py draft/publish`).
Escreve `demo-output.txt` ao lado e, na pasta de saída, o HTML das duas versões.
"""
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "library" / "kernel" / "tools"
P = runpy.run_path(str(TOOLS / "process_map.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
L = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_handoff_legacy.py"), run_name="demo")
FIX = ROOT / ".claude" / "tests" / "fixtures" / "calc-capture" / "fx-calc-bancas" / "inputs"
WB = "precos-bancas-reduzido.xlsx"
OWNER = "owner (Responsável de Pricing — dono simulado, dados de teste)"
lines = []


def say(msg=""):
    lines.append(msg)


def run(*args):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True,
                       encoding="utf-8")
    if r.returncode not in (0,):
        raise SystemExit("falhou: {}\n{}".format(args, r.stderr))
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""


ENQ = """# Enquadramento — bancas (demonstração)

## T1 · actors
O fixador de preço e a assistente; os comerciais recebem.

## T2 · trigger
Todos os dias úteis, de manhã.

## T3 · activities
Recolher cotações, actualizar o mercado, calcular os preços por porto e produto.

## T4 · outcomes
O preço mínimo por porto e produto chega aos comerciais; um preço de referência BIOS.
"""

PM = """# Process Model — bancas (demonstração: autoria sintética da L2)

> P-0: consumed (T1–T7)

## 3. Business rules (PM-NNN)

| id | rule | state | evidence | verificado_em | validade |
|---|---|---|---|---|---|
| PM-001 | O preço mínimo por porto × produto sai da folha Outputs | Assumed | Outputs!X21 | 2026-01-01 | financeiro |
| PM-002 | O preço de referência BIOS sai da folha Outputs BIOS | Assumed | Outputs BIOS!D6 | 2026-01-01 | financeiro |

## 4. Process synopsis (cross-source)

- OBSERVED — `Outputs`: o preço mínimo até / após por porto e produto — `PM-001`.
- OBSERVED — `Outputs BIOS`: a família de preços de biocombustível — `PM-002`.
- INFERRED — `Simulador`: cópia editável da saída para projectar a segunda e a terça — `Simulador!A1`.

## 4bis. Cadeia de cálculo (por saída)

(fragmento do motor)

## 6. Interrogation list (PM-U-NNN)

| id | question | why it matters |
|---|---|---|
| PM-U-001 | Quem recebe o preço BIOS e com que cadência? | muda o consumidor |
"""


def draft_v1(eng):
    chain = json.loads((eng / "_capture" / (WB + ".calc-chain.json")).read_text("utf-8"))
    cref = "_capture/{}.calc-chain.json#".format(WB)
    blocks = chain["blocks"]
    bios = [b for b in blocks if b["sheet"] == "Outputs BIOS"]
    rest = [b for b in blocks if b["sheet"] != "Outputs BIOS"]
    details = []
    for i, b in enumerate(rest + bios, start=1):
        details.append({"id": "MAPD-{:03d}".format(i),
                        "attaches_to": ["MAPN-006" if b in bios else "MAPN-004"],
                        "kind": "calculation", "label": str(b.get("label") or b["anchor"]),
                        "marker": "OBSERVED", "ref": {"ref": cref + b["id"]}})
    pm = "_capture/process-model.md#"
    return {
        "schema_version": "process-map/1", "engagement_id": "bancas", "perspective": "as_is",
        "lanes": [{"id": "MAPL-001", "label": "Fixador", "kind": "actor"},
                  {"id": "MAPL-002", "label": "Excel de preços", "kind": "tool"},
                  {"id": "MAPL-003", "label": "Comerciais", "kind": "consumer"}],
        "nodes": [
            {"id": "MAPN-001", "kind": "trigger", "label": "Dia útil", "lane": "MAPL-001",
             "order": 0, "marker": "OBSERVED", "evidence": [{"ref": "enquadramento.md#T2"}]},
            {"id": "MAPN-002", "kind": "step", "label": "Recolhe cotações e actualiza o mercado",
             "lane": "MAPL-001", "order": 1, "marker": "OBSERVED",
             "evidence": [{"ref": "enquadramento.md#T3"},
                          {"ref": "_capture/{}.extraction.json#sheets[name=Market View]"
                           .format(WB)}]},
            {"id": "MAPN-003", "kind": "decision", "label": "Cotações suficientes?",
             "lane": "MAPL-001", "order": 2, "marker": "HYPOTHESIS",
             "evidence": [{"ref": pm + "§4:Simulador"}]},
            {"id": "MAPN-004", "kind": "step", "label": "Calcula preços por porto e produto",
             "lane": "MAPL-002", "order": 3, "marker": "OBSERVED",
             "evidence": [{"ref": pm + "PM-001"}]},
            {"id": "MAPN-005", "kind": "output", "label": "Preço mínimo até / após",
             "lane": "MAPL-003", "order": 4, "marker": "OBSERVED",
             "evidence": [{"ref": pm + "§4:Outputs"}]},
            {"id": "MAPN-006", "kind": "output", "label": "Preço de referência BIOS",
             "lane": "MAPL-002", "order": 4, "marker": "OBSERVED",
             "evidence": [{"ref": pm + "PM-002"}, {"ref": pm + "§4:Outputs BIOS"}]}],
        "edges": [
            {"id": "MAPE-001", "src": "MAPN-001", "dst": "MAPN-002", "kind": "normal",
             "marker": "OBSERVED", "evidence": [{"ref": "enquadramento.md#T2"}]},
            {"id": "MAPE-002", "src": "MAPN-002", "dst": "MAPN-003", "kind": "normal",
             "marker": "INFERRED", "evidence": [{"ref": pm + "§4:Simulador"}]},
            {"id": "MAPE-003", "src": "MAPN-003", "dst": "MAPN-004", "kind": "branch",
             "label": "sim", "marker": "INFERRED", "evidence": [{"ref": pm + "PM-001"}]},
            {"id": "MAPE-004", "src": "MAPN-004", "dst": "MAPN-005", "kind": "normal",
             "marker": "OBSERVED", "evidence": [{"ref": pm + "PM-001"}],
             "carries": ["preço mínimo por porto × produto"]},
            {"id": "MAPE-005", "src": "MAPN-004", "dst": "MAPN-006", "kind": "normal",
             "marker": "OBSERVED", "evidence": [{"ref": pm + "PM-002"}]}],
        "details": details,
        "gaps": [{"id": "MAPG-001", "attaches_to": ["MAPN-006"],
                  "question": "Quem recebe o preço BIOS e com que cadência?",
                  "respondent": "dono", "pm_u_ref": "PM-U-001"},
                 {"id": "MAPG-002", "attaches_to": ["MAPN-003"],
                  "question": "O que se faz quando não há cotações suficientes?",
                  "respondent": "dono"}],
        "orphans": [], "retired_ids": []}


def publish(eng, draft, out):
    draft, _ = P["stamp"](eng, draft)
    path = out / "draft.json"
    path.write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
    v = P["check"](eng, draft)
    r = P["publish"](eng, draft, path)
    if not r["published"]:
        raise SystemExit(json.dumps(r, ensure_ascii=False, indent=1))
    P["render"](eng)
    return v, r


def write_authority(eng, rel, text):
    d = R["draft"](eng, [rel], reads=["_map/map.json"])
    p = Path(d["path"]) / rel
    p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")
    return R["publish"](eng, d["draft"])


def main(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        base = Path(t)
        eng = L["novo"](base, "bancas")
        (eng / "inputs").mkdir()
        shutil.copy(FIX / WB, eng / "inputs" / WB)
        cap = eng / "_capture"
        cap.mkdir()
        ext = cap / (WB + ".extraction.json")
        run(TOOLS / "xlsx_extract.py", eng / "inputs" / WB, ext)
        run(TOOLS / "xlsx_extract.py", "--replay", eng / "inputs" / WB, ext, cap / (WB + ".replay.md"))
        run(TOOLS / "text_extract.py", "--index", eng)
        (eng / "enquadramento.md").write_text(ENQ, encoding="utf-8")
        (cap / "process-model.md").write_text(PM, encoding="utf-8")
        units = P["transfer_units"](eng)
        say("captura real: {} folhas extraídas, {} blocos de cálculo; unidades a colocar no "
            "mapa: {}".format(len(json.loads(ext.read_text("utf-8"))["sheets"]),
                              sum(1 for c in units.values() if c == "calculation"), len(units)))

        v, r = publish(eng, draft_v1(eng), base)
        say("1. mapa {}: válido={} · sem destino {} · lacunas {} → {}".format(
            r["version"], v["valid"], len(v["transfer"]["missing"]), len(v["gaps"]),
            P["RENDER_REL"]))
        shutil.copy(eng / P["RENDER_REL"], out_dir / "process-map-v01.html")
        say("   validação: {}".format(P["validation"](eng)["status"]))

        say("2. perguntas ao dono, por grupo (uma chamada, não uma por célula):")
        for g in P["questions"](eng):
            say("   [{}] {}".format(g["title"], g["validates"] or "—"))
            for it in g["items"]:
                say("      · {} ({})".format(it["question"], it["id"]))

        answer = ("[dono simulado — dados de teste] Falta o passo em que o preço mínimo é "
                  "carregado no sistema de vendas pela outra equipa.")
        write_authority(eng, "answers.md",
                        "\n## MAPA-mp-v01 — Falta algum passo, saída ou quem a recebe?\n\n{}\n"
                        .format(answer))
        say("3. resposta verbatim em answers.md (escritor real): «{}»".format(answer))

        d2 = draft_v1(eng)
        d2["base"] = P["load"](eng)["digest"]
        d2["lanes"].append({"id": "MAPL-004", "label": "Sistema de vendas",
                            "kind": "downstream"})
        d2["nodes"].append({"id": "MAPN-007", "kind": "step",
                            "label": "Carrega o preço mínimo no sistema de vendas",
                            "lane": "MAPL-004", "order": 5, "marker": "OBSERVED",
                            "evidence": [{"ref": "answers.md#MAPA-mp-v01"}]})
        d2["edges"].append({"id": "MAPE-006", "src": "MAPN-005", "dst": "MAPN-007",
                            "kind": "normal", "marker": "OBSERVED",
                            "evidence": [{"ref": "answers.md#MAPA-mp-v01"}]})
        v2, r2 = publish(eng, d2, base)
        say("4. correcção do dono → nova versão {} (histórico: {}); validação: {}".format(
            r2["version"], sorted(p.name for p in (eng / "_map" / "history").iterdir()),
            P["validation"](eng)["status"]))

        block = P["approval_block"](eng, "processo diário de preço de bancas (Portugal)",
                                    "MAPG-001 e MAPG-002 ficam por esclarecer; a decisão "
                                    "«Cotações suficientes?» é hipótese", OWNER)
        write_authority(eng, "decisions.md", block)
        val = P["validation"](eng)
        say("5. validação registada em decisions.md (escritor real): {} {} {} — condições: {}"
            .format(val["status"], val["decision"], val["version"], val["conditions"]))
        say("   a hipótese continua hipótese: {}".format(
            next(n["marker"] for n in P["load"](eng)["map"]["nodes"] if n["id"] == "MAPN-003")))
        P["render"](eng)
        shutil.copy(eng / P["RENDER_REL"], out_dir / "process-map-v02.html")
        say("   HTML: process-map-v01.html · process-map-v02.html")
    out = "\n".join(lines) + "\n"
    Path(__file__).with_name("demo-output.txt").write_text(out, encoding="utf-8")
    sys.stdout.write(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent)
