"""M3 — demonstração obrigatória (PLANO.md, M3 → Demonstração obrigatória).

    python docs/process-map/M3/demo.py

Sobre CÓPIAS temporárias da fixture F06 com um mapa publicado (os mesmos passos que
`.claude/tests/test_process_map_coverage.py` fixa):

  1. a reconciliação dá destino a cada elemento material do mapa — e sem o destino de um
     deles fica incompleta (COV-MAP-UNPLACED);
  2. o desenho v01 (YAML válido, 0 bloqueios estruturais) omite a saída «Resumo Aditivos»:
     o gate da entrega bloqueia, com a fonte no mapa e o destino em falta;
  3. corrigido (v03) e revisto: passa;
  4. ramo separado — excluída com decisão: aceite; sem autoridade: recusada.

Os registos semânticos vêm das fixtures (escritos pelo revisor, não pelo motor): prova-se
o que o motor faz com eles, não que o agente descobriu a omissão sozinho (isso é o M5).
Escreve `demo-output.txt` ao lado.
"""
import json
import runpy
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
T = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_process_map_coverage.py"),
                   run_name="demo")
C, P, REL = T["C"], T["P"], T["REL"]
lines = []


def say(msg=""):
    lines.append(msg)


def fresh(tmp, name):
    eng = Path(tmp) / name / "fx-coverage-f06"
    shutil.copytree(T["F06"], eng)
    T["publish_map"](eng, T["f06_map"]())
    return eng


def errors(st):
    return sorted({d["code"] for d in st["diagnostics"] if d["severity"] == "error"})


with tempfile.TemporaryDirectory() as tmp:
    eng = fresh(tmp, "a")
    units = T["map_units"](eng)
    say("mapa mp-v01 publicado sobre a F06: {} unidades do mapa entram no denominador "
        "(passos, ligações, detalhes, dúvidas)".format(len(units)))

    T["install"](eng, T["recon"](eng, skip=("MAPN-007", "MAPG-001")))
    st = C["coverage_state"](eng, "reconciliation", None)
    say("1a. reconciliação sem destino para «Resumo Aditivos»: cobertura={} · {}".format(
        st["coverage"], ", ".join(d["locator"] for d in st["diagnostics"]
                                  if d["code"] == "COV-MAP-UNPLACED")))
    shutil.rmtree(eng / "_coverage")
    T["install"](eng, T["recon"](eng))
    st = C["coverage_state"](eng, "reconciliation", None)
    say("1b. com destino (item C-007 ← MAPN-007, MAPG-001): cobertura={} · actual={}".format(
        st["coverage"], st["freshness"]))

    T["install"](eng, T["blueprint_record"](eng, "rec-v02-blueprint-missing"))
    T["approve"](eng, "01", "2026-03-11T09:00:00+01:00")
    tgt = {"file": "_blueprint/ux-blueprint_v01.yaml",
           "identity": C["target_identity"](eng, "blueprint", "_blueprint/ux-blueprint_v01.yaml")}
    bst = C["coverage_state"](eng, "blueprint", tgt)
    say("2. desenho v01: estrutura {} bloqueio(s) — válido; cobertura={} · elegível={}".format(
        bst["structural"]["blocking"], bst["coverage"], bst["eligible"]))
    pc = REL["process_coverage"](eng)
    for g in pc["blueprint"]["gaps"]:
        say("   lacuna {} ({}): {} — origem: {}".format(
            ",".join(g["requirement_refs"]), g["status"], g.get("required_action", ""),
            "; ".join("{} «{}»".format(o["unit"], o["label"]) for o in g["origin"]
                      if o["unit"].startswith("_map/")) or "—"))
    rd = REL["readiness"](eng)
    say("   entrega pronta={} — {}".format(rd["ready"], next(r for r in rd["reasons"]
                                                          if "processo" in r)))

    for name in ("rec-v02-blueprint-missing", "rec-v03-blueprint-partial",
                 "rec-v04-blueprint-complete"):
        T["install"](eng, T["blueprint_record"](eng, name))
    T["approve"](eng, "03", "2026-03-12T09:00:00+01:00")
    pc = REL["process_coverage"](eng)
    say("3. desenho v03 (publica e consulta o Resumo Aditivos) revisto: cobertura do processo "
        "{} · razões: {}".format(pc["blueprint"]["state"], pc["reasons"] or "nenhuma"))

    for label, scope in (("com a decisão D-002", ["D-002"]), ("sem autoridade", [])):
        e2 = fresh(tmp, "b-" + ("ok" if scope else "ko"))

        def edit(rec, scope=scope):
            it = next(c for c in rec["coverage"] if c["requirement_refs"] == ["C-007"])
            it.update(disposition="retire", scope_basis_refs=scope,
                      assessment={"status": "excluded",
                                  "rationale": "o Resumo Aditivos sai do âmbito da entrega",
                                  "acceptance_basis_refs": []},
                      required_action="nenhuma — exclusão", responsible_role="dono")
            rec["semantic_review"]["findings"].append(it["id"])
        T["install"](e2, T["recon"](e2, edit=edit))
        st = C["coverage_state"](e2, "reconciliation", None)
        say("4. excluir «Resumo Aditivos» {}: cobertura={} · {}".format(
            label, st["coverage"],
            ", ".join(c for c in errors(st) if c.startswith("COV-EXCL")) or "aceite"))

out = "\n".join(lines) + "\n"
Path(__file__).with_name("demo-output.txt").write_text(out, encoding="utf-8")
sys.stdout.write(out)
