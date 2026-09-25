"""process-map M3 — o processo liga-se à SU, ao desenho e à entrega; uma funcionalidade
material identificada no mapa não desaparece em silêncio.

Casos (docs/process-map/PLANO.md §15):
  MAP-17  funcionalidade no mapa e ausente do blueprint: lacuna com a origem no mapa; o
          desenho e a entrega não se anunciam completos
  MAP-18  corrigida (v03) ou excluída com autoridade: passa; excluída sem autoridade: recusa
  MAP-19  (estrutural) elemento material lido sem destino na reconciliação: COV-MAP-UNPLACED
  MAP-20  requisito TO-BE novo sem origem no Excel: admitido e coberto
  MAP-21  cobertura ausente / desactualizada / inválida, com o resto do pacote válido: não
          pronto, cada variante com a sua razão
  MAP-13  uma linha em dois passos, GLOBAL, SU antiga: lidas certas; a transição herda
  MAP-12  elemento retirado ainda citado: sinalizado com os sucessores, nunca reapontado
  MAP-14  início sem linha: sinal, não bloqueio
  MAP-08  exclusão material sem autoridade: recusada
  MAP-22  mudança material do mapa: a reconciliação fica desactualizada
  MAP-27  o pacote leva o mapa consumido, a vista e os registos de cobertura lidos
  e: uma obrigação partilhada por dois elementos é UM item (não duplica esforço).

Fixture: cópia de `fixtures/coverage/fx-coverage-f06` (o F06: a v01 do desenho perde C-007)
com um mapa publicado por cima; e o cenário «pronto» dos testes do release.

    python .claude/tests/test_process_map_coverage.py
"""
import json
import runpy
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
P = runpy.run_path(str(TOOLS / "process_map.py"))
C = runpy.run_path(str(TOOLS / "coverage.py"))
D = runpy.run_path(str(TOOLS / "dashboard.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
F = runpy.run_path(str(TOOLS / "functional.py"))
REL = runpy.run_path(str(TOOLS / "release.py"))
TR = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_release.py"), run_name="helpers")
L = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_handoff_legacy.py"), run_name="helpers")
FIX = ROOT / ".claude" / "tests" / "fixtures" / "coverage"
F06 = FIX / "fx-coverage-f06"
RECORDS = FIX / "records"
OWNER = "owner (Responsável de Qualidade — fixture, via AskUserQuestion)"
PM = "_capture/process-model.md#"
MAPU = "_map/map.json#"


def ev(*refs):
    return [{"ref": r} for r in refs]


def f06_map() -> dict:
    """O processo da F06: registar → calcular → escrever o estado → libertar (outro
    técnico) → três saídas. A saída «Resumo Aditivos» (C-007) é a que a v01 perde."""
    return {
        "schema_version": "process-map/1", "engagement_id": "fx-coverage-f06",
        "perspective": "as_is",
        "lanes": [{"id": "MAPL-001", "label": "Responsável de qualidade", "kind": "actor"},
                  {"id": "MAPL-002", "label": "Workbook de lotes", "kind": "tool"},
                  {"id": "MAPL-003", "label": "Segundo técnico", "kind": "actor"},
                  {"id": "MAPL-004", "label": "Equipas de produção", "kind": "consumer"},
                  {"id": "MAPL-005", "label": "Sistema de lotes", "kind": "downstream"}],
        "nodes": [
            {"id": "MAPN-001", "kind": "trigger", "label": "Chegam as análises do dia",
             "lane": "MAPL-001", "order": 0, "marker": "OBSERVED",
             "evidence": ev("enquadramento.md#T2")},
            {"id": "MAPN-002", "kind": "step", "label": "Regista as entradas",
             "lane": "MAPL-001", "order": 1, "marker": "OBSERVED", "evidence": ev(PM + "PM-003")},
            {"id": "MAPN-003", "kind": "step", "label": "Calcula resultado e % de aditivo",
             "lane": "MAPL-002", "order": 2, "marker": "OBSERVED",
             "evidence": ev(PM + "PM-001", PM + "PM-002")},
            {"id": "MAPN-004", "kind": "step", "label": "Escreve o estado do lote",
             "lane": "MAPL-001", "order": 3, "marker": "OBSERVED", "evidence": ev(PM + "PM-004")},
            {"id": "MAPN-005", "kind": "step", "label": "Liberta o lote",
             "lane": "MAPL-003", "order": 4, "marker": "OBSERVED",
             "evidence": ev("enquadramento.md#M-2")},
            {"id": "MAPN-006", "kind": "output", "label": "Resumo de Lotes",
             "lane": "MAPL-004", "order": 5, "marker": "OBSERVED", "evidence": ev(PM + "PM-001")},
            {"id": "MAPN-007", "kind": "output", "label": "Resumo Aditivos",
             "lane": "MAPL-002", "order": 5, "marker": "OBSERVED", "evidence": ev(PM + "PM-002")},
            {"id": "MAPN-008", "kind": "output", "label": "Ficheiro de integração",
             "lane": "MAPL-005", "order": 5, "marker": "OBSERVED",
             "evidence": ev("enquadramento.md#T4")}],
        "edges": [
            {"id": "MAPE-001", "src": "MAPN-001", "dst": "MAPN-002", "kind": "normal",
             "marker": "OBSERVED", "evidence": ev("enquadramento.md#T2")},
            {"id": "MAPE-002", "src": "MAPN-002", "dst": "MAPN-003", "kind": "normal",
             "marker": "OBSERVED", "evidence": ev(PM + "PM-003")},
            {"id": "MAPE-003", "src": "MAPN-003", "dst": "MAPN-004", "kind": "normal",
             "marker": "OBSERVED", "evidence": ev(PM + "PM-004")},
            {"id": "MAPE-004", "src": "MAPN-004", "dst": "MAPN-005", "kind": "normal",
             "marker": "OBSERVED", "evidence": ev("enquadramento.md#M-2")},
            {"id": "MAPE-005", "src": "MAPN-005", "dst": "MAPN-006", "kind": "normal",
             "marker": "OBSERVED", "evidence": ev(PM + "PM-001")},
            {"id": "MAPE-006", "src": "MAPN-003", "dst": "MAPN-007", "kind": "normal",
             "marker": "OBSERVED", "evidence": ev(PM + "PM-002")},
            {"id": "MAPE-007", "src": "MAPN-005", "dst": "MAPN-008", "kind": "normal",
             "marker": "OBSERVED", "evidence": ev("enquadramento.md#T4")}],
        "details": [{"id": "MAPD-001", "attaches_to": ["MAPN-003"], "kind": "rule",
                     "label": "limite de alerta sem fórmula que o use", "marker": "INFERRED",
                     "ref": {"ref": PM + "PM-005"}}],
        "gaps": [{"id": "MAPG-001", "attaches_to": ["MAPN-007"],
                  "question": "O Resumo Aditivos tem consumidor a jusante?", "pm_u_ref": "PM-U-001"},
                 {"id": "MAPG-002", "attaches_to": ["MAPD-001"],
                  "question": "O limite de alerta ainda governa alguma decisão?",
                  "pm_u_ref": "PM-U-002"},
                 {"id": "MAPG-003", "attaches_to": ["MAPN-002"],
                  "question": "As colunas Custo_Posto_* alimentam algum cálculo?",
                  "pm_u_ref": "PM-U-003"}],
        "orphans": [{"ref": PM + "PM-006", "reason": "out_of_scope", "materiality": "not-material",
                     "note": "o workbook do ano anterior só se consulta"}],
        "retired_ids": []}


# as unidades do mapa que a reconciliação lê como materiais, e a obrigação que as trata
MATERIAL = {"MAPN-005": ["C-002", "C-005"], "MAPN-006": ["C-006"], "MAPN-007": ["C-007"],
            "MAPN-008": ["C-008"], "MAPG-001": ["C-007"]}


def publish_map(eng, draft):
    d, _ = P["stamp"](eng, draft)
    p = Path(eng).parent / "map-draft.json"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    r = P["publish"](eng, d, p)
    assert r["published"], r
    return r


def rebase(eng, rec):
    """Recalcula a base inteira (o mapa acrescentou fontes e unidades à F06)."""
    inv = C["build_inventory"](eng)
    tgt = rec.get("target")
    basis = C["compute_basis"](eng, inv, rec["stage"], tgt,
                               authorities=(rec.get("basis") or {}).get("authorities", ()))
    basis.pop("diagnostics", None)
    rec["basis"] = basis
    return rec


def map_units(eng):
    return sorted(u["unit_key"] for u in C["build_inventory"](eng)["units"]
                  if u["class"] in C["MAP_UNIT_CLASSES"])


def recon(eng, place=True, skip=(), edit=None):
    rec = json.loads((RECORDS / "rec-v01-reconciliation-complete.json").read_text("utf-8"))
    for u in map_units(eng):
        eid = u.split("#", 1)[1]
        mat = "material" if eid in MATERIAL else "not-material"
        rec["source_review"].append({
            "id": "sr-map-" + eid, "unit_refs": [u], "assessment": "reviewed",
            "materiality": mat, "rationale": "elemento do mapa lido contra a SU",
            "links": {"su_refs": [], "coverage_items": [], "obligations": []}})
    by_req = {tuple(sorted(c["requirement_refs"])): c for c in rec["coverage"]}
    if place:
        for eid, reqs in MATERIAL.items():
            if eid in skip:
                continue
            by_req[tuple(sorted(reqs))]["source_unit_refs"].append(MAPU + eid)
    if edit:
        edit(rec)
    return rebase(eng, rec)


def install(eng, *recs):
    (eng / "_coverage").mkdir(exist_ok=True)
    for rec in recs:
        (eng / "_coverage" / ("coverage_%s.json" % rec["version"])).write_text(
            json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")


def blueprint_record(eng, name):
    return rebase(eng, json.loads((RECORDS / (name + ".json")).read_text("utf-8")))


def approve(eng, version, ts):
    text = F["blueprint_approval_block"](eng, version, OWNER, ts)
    p = eng / "decisions.md"
    p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")


class F06Base(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.eng = Path(self.tmp.name) / "fx-coverage-f06"
        shutil.copytree(F06, self.eng)
        publish_map(self.eng, f06_map())

    def state(self, stage="reconciliation", target=None):
        return C["coverage_state"](self.eng, stage, target)

    def codes(self, st):
        return {d["code"] for d in st["diagnostics"] if d["severity"] == "error"}


class Inventario(F06Base):

    def test_the_map_brings_its_elements_to_the_denominator(self):
        units = map_units(self.eng)
        self.assertIn(MAPU + "MAPN-007", units)
        self.assertIn(MAPU + "MAPG-001", units)
        self.assertNotIn(MAPU + "MAPL-001", units, "uma faixa é agrupamento, não unidade")
        inv = C["build_inventory"](self.eng)
        self.assertTrue(inv["complete"], inv["diagnostics"])

    def test_the_view_and_the_history_are_not_sources(self):
        P["render"](self.eng)
        rels = [s["path"] for s in C["compute_basis"](
            self.eng, C["build_inventory"](self.eng), "reconciliation", None)["sources"]]
        self.assertIn("_map/map.json", rels)
        self.assertNotIn("process-map.html", rels)
        self.assertFalse([r for r in rels if r.startswith("_map/history/")])


class MAP19_ElementoSemDestino(F06Base):

    def test_a_material_element_without_an_item_blocks_the_reconciliation(self):
        install(self.eng, recon(self.eng, skip=("MAPN-007", "MAPG-001")))
        st = self.state()
        self.assertEqual(st["coverage"], "gaps")
        unplaced = [d for d in st["diagnostics"] if d["code"] == "COV-MAP-UNPLACED"]
        self.assertEqual(sorted(d["locator"] for d in unplaced),
                         [MAPU + "MAPG-001", MAPU + "MAPN-007"])
        self.assertFalse(st["eligible"])

    def test_with_every_material_element_placed_the_reconciliation_is_complete(self):
        install(self.eng, recon(self.eng))
        st = self.state()
        self.assertEqual((st["contract_validity"], st["freshness"], st["coverage"]),
                         ("valid", "current", "complete"), st["diagnostics"][:3])

    def test_not_material_with_a_reason_needs_no_item(self):
        install(self.eng, recon(self.eng))
        self.assertNotIn("COV-MAP-UNPLACED", self.codes(self.state()))


class MAP17_OmissaoNoDesenho(F06Base):

    def setUp(self):
        super().setUp()
        install(self.eng, recon(self.eng), blueprint_record(self.eng, "rec-v02-blueprint-missing"))
        approve(self.eng, "01", "2026-03-11T09:00:00+01:00")

    def test_the_gap_reaches_the_release_with_its_origin_in_the_map(self):
        pc = REL["process_coverage"](self.eng)
        self.assertEqual(pc["reconciliation"]["state"], "complete", pc["reconciliation"])
        self.assertEqual(pc["blueprint"]["state"], "gaps")
        gap = next(g for g in pc["blueprint"]["gaps"] if g["requirement_refs"] == ["C-007"])
        self.assertEqual(gap["status"], "missing")
        self.assertIn({"unit": MAPU + "MAPN-007", "label": "Resumo Aditivos"}, gap["origin"])
        self.assertIn("cobertura do processo: revisão do desenho aprovado com lacunas",
                      pc["reasons"])
        rd = REL["readiness"](self.eng)
        self.assertFalse(rd["ready"])
        self.assertIn("cobertura do processo: revisão do desenho aprovado com lacunas",
                      rd["reasons"])

    def test_the_structurally_valid_v01_is_still_not_approvable(self):
        t = {"file": "_blueprint/ux-blueprint_v01.yaml",
             "identity": C["target_identity"](self.eng, "blueprint",
                                              "_blueprint/ux-blueprint_v01.yaml")}
        st = self.state("blueprint", t)
        self.assertEqual(st["structural"]["blocking"], 0)
        self.assertFalse(st["eligible"])


class MAP18_CorrigidaOuExcluida(F06Base):

    def test_the_corrected_design_closes_the_finding(self):
        install(self.eng, recon(self.eng),
                blueprint_record(self.eng, "rec-v02-blueprint-missing"),
                blueprint_record(self.eng, "rec-v03-blueprint-partial"),
                blueprint_record(self.eng, "rec-v04-blueprint-complete"))
        approve(self.eng, "03", "2026-03-12T09:00:00+01:00")
        pc = REL["process_coverage"](self.eng)
        self.assertEqual(pc["blueprint"]["state"], "complete", pc["blueprint"])
        self.assertEqual(pc["reasons"], [])

    def test_an_authorised_exclusion_is_accepted_and_one_without_authority_is_not(self):
        def exclude(scope):
            def edit(rec):
                it = next(c for c in rec["coverage"] if c["requirement_refs"] == ["C-007"])
                it.update(disposition="retire", scope_basis_refs=scope,
                          assessment={"status": "excluded",
                                      "rationale": "o Resumo Aditivos sai do âmbito da entrega",
                                      "acceptance_basis_refs": []},
                          required_action="nenhuma — exclusão", responsible_role="dono")
                rec["semantic_review"]["findings"].append(it["id"])
            return edit
        install(self.eng, recon(self.eng, edit=exclude(["D-002"])))
        st = self.state()
        self.assertNotIn("COV-EXCLUSION-NO-DECISION", self.codes(st))
        self.assertEqual(st["coverage"], "complete", self.codes(st))
        install(self.eng, recon(self.eng, edit=exclude([])))
        (self.eng / "_coverage" / "coverage_v01.json").unlink()
        rec = recon(self.eng, edit=exclude([]))
        rec["version"] = "v01"
        install(self.eng, rec)
        self.assertIn("COV-EXCLUSION-NO-DECISION", self.codes(self.state()))


class MAP20_RequisitoNovo(F06Base):

    def test_a_new_to_be_need_without_origin_in_the_files_is_admitted(self):
        def new_need(rec):
            rec["coverage"].append({
                "id": "item-007", "requirement_refs": ["A-001"], "source_unit_refs": [],
                "disposition": "preserve", "scope_basis_refs": [], "targets": [],
                "assessment": {"status": "covered", "rationale": "novo requisito do dono",
                               "acceptance_basis_refs": []}, "unresolved_refs": []})
        install(self.eng, recon(self.eng, edit=new_need))
        st = self.state()
        self.assertEqual(st["coverage"], "complete", [d for d in st["diagnostics"]
                                                     if d["severity"] == "error"][:3])


class ObrigacaoPartilhada(F06Base):

    def test_one_requirement_served_by_two_elements_is_one_item(self):
        rec = recon(self.eng)
        items = [c for c in rec["coverage"] if c["requirement_refs"] == ["C-007"]]
        self.assertEqual(len(items), 1)
        self.assertTrue({MAPU + "MAPN-007", MAPU + "MAPG-001"}
                        <= set(items[0]["source_unit_refs"]))


class MAP22_MudancaDoMapa(F06Base):

    def test_a_material_change_of_the_map_makes_the_reconciliation_stale(self):
        install(self.eng, recon(self.eng))
        self.assertEqual(self.state()["freshness"], "current")
        d = f06_map()
        d["base"] = P["load"](self.eng)["digest"]
        d["nodes"][6]["label"] = "Resumo Aditivos (publicado)"
        publish_map(self.eng, d)
        self.assertEqual(self.state()["freshness"], "stale")
        self.assertEqual(REL["process_coverage"](self.eng)["reconciliation"]["state"], "stale")

    def test_rendering_the_view_changes_nothing(self):
        install(self.eng, recon(self.eng))
        P["render"](self.eng)
        self.assertEqual(self.state()["freshness"], "current")


class MAP21_Variantes(unittest.TestCase):
    """O cenário «pronto» do release, com um mapa: só a cobertura do processo falha, e
    cada variante diz a sua razão."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.eng = Path(TR["pronto"](self.tmp.name))
        self.assertTrue(REL["readiness"](self.eng)["ready"], "o cenário base tem de estar pronto")
        self.assertFalse(REL["process_coverage"](self.eng)["evaluated"],
                         "sem mapa a capacidade é não avaliada")
        publish_map(self.eng, {
            "schema_version": "process-map/1", "engagement_id": "fx-hv1-02",
            "perspective": "as_is",
            "lanes": [{"id": "MAPL-001", "label": "Equipa", "kind": "actor"}],
            "nodes": [{"id": "MAPN-001", "kind": "trigger", "label": "Pedido",
                       "lane": "MAPL-001", "order": 0, "marker": "OBSERVED",
                       "evidence": ev("inputs/pedido.md")}],
            "edges": [], "details": [], "gaps": [], "orphans": [], "retired_ids": []})

    def reasons(self):
        rd = REL["readiness"](self.eng)
        self.assertFalse(rd["ready"])
        others = [r for r in rd["reasons"] if not r.startswith("cobertura do processo")]
        self.assertEqual(others, [], "a variante tem de ser a única razão")
        return rd["reasons"]

    def test_absent_coverage_keeps_the_release_preliminary(self):
        self.assertIn("cobertura do processo: reconciliação ausente", self.reasons())
        self.assertEqual(REL["build"](self.eng)["delivery_level"], "preliminary")

    def test_invalid_coverage_is_named(self):
        (self.eng / "_coverage").mkdir()
        (self.eng / "_coverage" / "coverage_v01.json").write_text(json.dumps(
            {"schema_version": 1, "version": "v01", "stage": "reconciliation"}),
            encoding="utf-8")
        self.assertIn("cobertura do processo: reconciliação inválida", self.reasons())

    def test_stale_coverage_is_named(self):
        inv = C["build_inventory"](self.eng)
        sr = []
        for i, u in enumerate(inv["units"]):
            lim = u["unit_key"] in {x["unit_key"] for x in inv["limitations"]}
            e = {"id": "sr-%03d" % i, "unit_refs": [u["unit_key"]],
                 "assessment": "unverifiable" if lim else "reviewed",
                 "materiality": "not-material", "rationale": "lido no teste",
                 "links": {"su_refs": [], "coverage_items": [], "obligations": []}}
            if lim:
                e["limitation"] = {"reason": "sem extractor", "impact": "nenhum",
                                   "action": "nenhuma"}
            sr.append(e)
        basis = C["compute_basis"](self.eng, inv, "reconciliation", None)
        basis.pop("diagnostics", None)
        rec = {"schema_version": 1, "version": "v01", "engagement": "fx-hv1-02",
               "stage": "reconciliation", "generated_at": "2026-03-10T10:00:00+01:00",
               "based_on": [], "target": None, "basis": basis, "source_review": sr,
               "coverage": [],
               "semantic_review": {"status": "completed",
                                   "performed_by": {"kind": "agent", "name": "teste"},
                                   "method": "source-to-target and target-to-source",
                                   "passes": {"source_to_target": True,
                                              "target_to_source": True},
                                   "limitations": [], "findings": [],
                                   "completed_at": "2026-03-10T10:00:00+01:00"}}
        install(self.eng, rec)
        self.assertEqual(REL["process_coverage"](self.eng)["reconciliation"]["state"],
                         "complete")
        p = self.eng / "inputs" / "pedido.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nnota nova\n", encoding="utf-8")
        self.assertIn("cobertura do processo: reconciliação desactualizada", self.reasons())

    def test_MAP27_the_package_carries_the_map_and_the_records(self):
        P["render"](self.eng)
        b = REL["build"](self.eng)
        idx = json.loads((Path(b["path"]) / "handoff-index.json").read_text("utf-8")) \
            if "path" in b else b
        files = json.dumps(idx)
        for rel in ("_map/map.json", "_map/history/mp-v01.json", "process-map.html"):
            self.assertIn(rel, files)


class MAP13_ElementosNaSU(unittest.TestCase):

    SU = """# SU

## Confirmed

| id | lens | claim | evidência | verificado_em | validade | elementos | ronda |
|---|---|---|---|---|---|---|---|
| C-001 | data | regra em dois passos | PM-001 | 2026-01-01 | organizacional | MAPN-003, MAPN-004 | R-01 |
| C-002 | chair | capacidade global | fonte | 2026-01-01 | organizacional | GLOBAL | R-01 |
| C-003 | data | sobre a organização | fonte | 2026-01-01 | organizacional | N/A — não é do processo | R-01 |
| C-004 | data | escrita por um escritor antigo | fonte | 2026-01-01 | organizacional | R-01 |

## Assumed

| id | lens | claim | base da assumption | verificado_em | validade | elementos | ronda |
|---|---|---|---|---|---|---|---|
| A-001 | data | volume estável | extrapolação | 2026-01-01 | organizacional | GLOBAL | R-01 |

## Unknown

| id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | elementos | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-001 | data | Quem consome? | fact_gap | funcional: consumidor | saída | role: dono | resposta | — | Med | email | dimensionante | PM-U-001 | MAPN-007 | R-01 |
"""

    def rows(self, md=None):
        return {r["id"]: r for r in D["parse_su"](md or self.SU)[1]}

    def test_multiple_global_na_and_the_old_writer(self):
        r = self.rows()
        self.assertEqual(r["C-001"]["elementos"], ["MAPN-003", "MAPN-004"])
        self.assertEqual(r["C-002"]["elementos_forma"], "global")
        self.assertEqual(r["C-003"]["elementos_forma"], "na")
        self.assertEqual((r["C-004"]["elementos_forma"], r["C-004"]["ronda"]), ("vazia", "R-01"))
        self.assertFalse(r["C-004"]["malformed"])

    def test_a_su_without_the_column_invents_no_association(self):
        old = self.SU.replace(" | elementos | ronda |", " | ronda |").replace(
            "|---|---|---|---|---|---|---|---|", "|---|---|---|---|---|---|---|")
        old = "\n".join(l for l in old.splitlines() if not l.startswith("| C-00") or "C-004" in l)
        r = self.rows(old)
        self.assertEqual(r["C-004"]["elementos_forma"], "ausente")

    def test_a_transition_inherits_the_elements_of_the_old_row(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        eng = L["novo"](Path(tmp.name))
        (eng / "shared-understanding.md").write_text(self.SU, encoding="utf-8")
        out = R["plan"](eng, "U-001", "Só a equipa interna consome.",
                        {"role": "dono do processo"}, today="2026-09-25")
        su = out["write_set"]["shared-understanding.md"] if "write_set" in out else out["su"]
        new = [r for r in D["parse_su"](su)[1] if "U-001" in r["support"]
               and r["id"] != "U-001"]
        self.assertEqual(len(new), 1)
        self.assertEqual(new[0]["elementos"], ["MAPN-007"])
        self.assertEqual(new[0]["ronda"], "R-01")


class ProjeccaoSUMapa(F06Base):

    SU_ROWS = [
        "| C-901 | data | o resumo aditivos fica | PM-002 | 2026-01-01 | organizacional | MAPN-007 | R-02 |",
        "| C-902 | data | aponta para um passo retirado | PM-003 | 2026-01-01 | organizacional | MAPN-002 | R-02 |",
        "| C-903 | data | aponta para o que não existe | PM-003 | 2026-01-01 | organizacional | MAPN-099 | R-02 |",
    ]

    def setUp(self):
        super().setUp()
        su = self.eng / "shared-understanding.md"
        text = su.read_text(encoding="utf-8")
        head = "| id | lens | claim | evidência | verificado_em | validade | ronda |"
        text = text.replace(head, "| id | lens | claim | evidência | verificado_em | validade | "
                                  "elementos | ronda |", 1)
        text = text.replace("|----|------|-------|-----------|---------------|----------|-------|",
                            "|----|------|-------|-----------|---------------|----------|-----------|-------|", 1)
        lines = text.splitlines()
        last = max(i for i, l in enumerate(lines) if l.startswith("| C-0"))
        lines[last + 1:last + 1] = self.SU_ROWS
        su.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_MAP14_a_trigger_without_rows_is_not_dark_a_step_is(self):
        pr = P["project"](self.eng)
        self.assertNotIn("MAPN-001", pr["dark"])
        self.assertIn("MAPN-004", pr["dark"])
        self.assertEqual(pr["elements"]["MAPN-007"]["rows"], ["C-901"])

    def test_MAP12_a_retired_element_still_cited_names_its_successors(self):
        d = f06_map()
        d["base"] = P["load"](self.eng)["digest"]
        step = d["nodes"][1]
        d["nodes"][1] = dict(step, id="MAPN-009", label="Regista entradas (formulário)",
                             was=["MAPN-002"])
        d["nodes"].append(dict(step, id="MAPN-010", label="Valida entradas", order=1,
                               lane="MAPL-003", was=["MAPN-002"]))
        d["retired_ids"] = [{"id": "MAPN-002", "reason": "dividido em registar e validar"}]
        for e in d["edges"]:
            e["src"] = "MAPN-009" if e["src"] == "MAPN-002" else e["src"]
            e["dst"] = "MAPN-009" if e["dst"] == "MAPN-002" else e["dst"]
        d["gaps"][2]["attaches_to"] = ["MAPN-009"]
        publish_map(self.eng, d)
        pr = P["project"](self.eng)
        self.assertIn({"row": "C-902", "element": "MAPN-002",
                       "successors": ["MAPN-009", "MAPN-010"]}, pr["retired"])
        self.assertIn({"row": "C-903", "element": "MAPN-099"}, pr["dead"])
        su = (self.eng / "shared-understanding.md").read_text(encoding="utf-8")
        self.assertIn("| MAPN-002 |", su, "o reapontamento nunca é automático")

    def test_rows_citing_map_ids_must_declare_the_map_as_read(self):
        cited = R["cited_sources"](self.eng, "\n".join(self.SU_ROWS))
        self.assertIn("_map/map.json", cited)
        self.assertNotIn("decisions.md", cited, "MAPN não é lido como decisão")


if __name__ == "__main__":
    unittest.main()
