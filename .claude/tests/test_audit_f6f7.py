# -*- coding: utf-8 -*-
"""A1–A5 e a revalidação explícita — a auditoria externa dos gates da F6 e da F7.

Evidência e correcção: `docs/handoff-v1/F7/CORRECAO-AUDITORIA.md`. A auditoria (commit
`1dcdb61`) reproduziu quatro falhas nos gates de entrega; a reprodução nesta sessão
confirmou-as e encontrou a quinta (A5). O mantenedor fixou o princípio da correcção
(2026-09-24): a actualidade das dependências verifica-se ao consumir, ao renderizar e ao
construir o release, não só ao publicar; um sha diferente prova uma alteração de conteúdo,
mas não a classifica — mover uma dependência exige uma avaliação registada, e trocar o hash
não pode, por si só, equivaler a revalidar o conteúdo.

    A1  aceitação do destinatário sem pessoa, âmbito, condições ou `Simulated` explícito
    A2  âmbito sem autorização e WP sem aceitação/DoD: o motor do inventário vê, o gate não
    A3  FC mudado, republicado e reautorizado: trabalho, spec e estimativa antigos prontos
    A4  edição entre a readiness e a cópia: o pacote verifica, mas não é o que passou
    A5  desenho mudado no mesmo caminho, aprovação renovada: FC no sha antigo prontos
    RV  a revalidação: registada, completa, coerente com o conteúdo, só-acrescenta, e
        verificada também na leitura (histórico e adulteração)

Estes casos nasceram vermelhos.
"""
import hashlib
import json
import runpy
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
TR = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_release.py"))
TI = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_impact.py"))
REL, F, R, IT, AU = TR["REL"], TR["F"], TR["R"], TR["IT"], TR["AU"]
I = runpy.run_path(str(TOOLS / "impact.py"))
TRC = runpy.run_path(str(TOOLS / "trace.py"))
INV = runpy.run_path(str(TOOLS / "inventory.py"))
W = runpy.run_path(str(TOOLS / "workflow.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))
BP = IT["BP"]
FCP = "_design/functional-contracts.json"
WPP = "_design/work-packages.json"
AVALIADOR = "autor funcional (dados de teste)"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def decisao(eng, bloco):
    TR["_decisao"](eng, bloco)


def proximo_d(eng):
    return "D-{:03d}".format(max(int(d[2:]) for d in W["_decision_ids"](eng)) + 1)


def republica_fc(eng, muda=None, revalidacao=None, pin_actual=True):
    """Rascunho dos FC → (sha do desenho de agora) → mudança → revalidação → publicação."""
    dr = F["draft"](eng)
    p = Path(dr["path"])
    data = json.loads(p.read_text(encoding="utf-8"))
    if pin_actual:
        for b in data["based_on"]:
            if b.get("ref") == BP:
                b["sha256"] = sha(eng / BP)
    if muda:
        muda(data)
    if revalidacao is not None:
        data["revalidation"] = revalidacao
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return F["publish"](eng, dr["draft"])


def republica_inv(eng, kind="work-packages", muda=None, revalidacao=None):
    dr = INV["draft"](eng, kind)
    p = Path(dr["path"])
    data = json.loads(p.read_text(encoding="utf-8"))
    if muda:
        muda(data)
    if revalidacao is not None:
        data["revalidation"] = revalidacao
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return INV["publish"](eng, dr["draft"])


def reautoriza(eng, fcs, ts="2026-09-24T12:00:00Z"):
    decisao(eng, F["authorization_block"](eng, fcs, AU["OWNER"], "SCOPE-0001", timestamp=ts))


def todos_os_fc(eng):
    return [it["id"] for it in json.loads((eng / FCP).read_text(encoding="utf-8"))["items"]]


def still_valid(eng, porque="o desenho mudou numa nota sem efeito nos contratos"):
    return {"items": {f: "still_valid" for f in todos_os_fc(eng)}, "assessment": porque,
            "assessed_by": AVALIADOR}


def pronto_revalidado(tmp):
    """O cenário «pronto» dos testes do release. Mudava o desenho depois de publicar os FC e
    deixava-os no sha anterior — era o A5 dentro da fixture; agora revalida-os
    (`test_release.pronto`, `revalidar=True`)."""
    return TR["pronto"](tmp)


def codigos(lista, campo="code"):
    return sorted({f[campo] for f in lista})


def gate_codes(eng):
    return codigos(TRC["scope_gate"](eng)["blockers"])


# =============================================================================
# A1 — a aceitação do destinatário lê o bloco inteiro
# =============================================================================

class A1_AceitacaoCompleta(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.eng = pronto_revalidado(self.tmp)
        b = REL["build"](self.eng)
        self.assertEqual(b["delivery_level"], "ready_for_receiver_review", b["reasons"])
        self.sha = REL["verify"](Path(b["path"]))["index_sha256"]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def bloco(self, **campos):
        base = {"Release sha256": self.sha, "Scope": "SCOPE-0001",
                "Conditions": "provas V2 antes do go-live", "Simulated": "no",
                "Validated by": AU["OWNER"], "Timestamp": "2099-01-01T10:00:00Z"}
        base.update(campos)
        linhas = "".join("- **{}**: {}\n".format(k, v) for k, v in base.items() if v is not None)
        return "\n## {} — Aceitação do destinatário (release r0001)\n\n{}".format(
            proximo_d(self.eng), linhas)

    def nivel(self):
        return REL["status"](self.eng, 1)["delivery_level"]

    def test_a_bare_block_does_not_promote(self):
        decisao(self.eng, "\n## {} — Aceitação do destinatário (release r0001)\n\n"
                          "- **Release sha256**: {}\n".format(proximo_d(self.eng), self.sha))
        s = REL["status"](self.eng, 1)
        self.assertEqual(s["delivery_level"], "ready_for_receiver_review")
        self.assertFalse(s["acceptance"]["valid"])

    def test_the_absence_of_simulated_is_not_a_no(self):
        decisao(self.eng, self.bloco(Simulated=None))
        self.assertEqual(self.nivel(), "ready_for_receiver_review")
        # o gate já o recusava pelo campo em falta; a leitura também não o pode dar por real
        # (mutante sobrevivente: `simulated = sim == "yes"`)
        self.assertTrue(REL["status"](self.eng, 1)["acceptance"]["simulated"])

    def test_an_agent_never_accepts(self):
        decisao(self.eng, self.bloco(**{"Validated by": "claude"}))
        self.assertEqual(self.nivel(), "ready_for_receiver_review")

    def test_the_scope_must_be_the_release_scope(self):
        decisao(self.eng, self.bloco(Scope="SCOPE-0099"))
        self.assertEqual(self.nivel(), "ready_for_receiver_review")

    def test_conditions_are_required(self):
        decisao(self.eng, self.bloco(Conditions=None))
        self.assertEqual(self.nivel(), "ready_for_receiver_review")

    def test_an_acceptance_dated_before_the_build_is_refused(self):
        decisao(self.eng, self.bloco(Timestamp="2020-01-01T00:00:00Z"))
        self.assertEqual(self.nivel(), "ready_for_receiver_review")

    def test_the_block_the_motor_generates_still_promotes(self):
        decisao(self.eng, REL["acceptance_block"](self.eng, 1, AU["OWNER"], "SCOPE-0001",
                                                  "provas V2 antes do go-live"))
        self.assertEqual(self.nivel(), "accepted_by_receiver")


# =============================================================================
# A2 — as lacunas do âmbito e do inventário chegam ao gate final
# =============================================================================

class A2_LacunasNoGate(unittest.TestCase):

    def test_an_unauthorised_scope_blocks_the_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto_revalidado(tmp)
            self.assertTrue(REL["readiness"](eng)["ready"])
            republica_inv(eng, "scope", muda=lambda d: d["items"][0].update(authorized_by=None))
            self.assertIn("SCOPE_NOT_AUTHORIZED", gate_codes(eng))
            rd = REL["readiness"](eng)
            self.assertFalse(rd["ready"])
            self.assertTrue(any("SCOPE_NOT_AUTHORIZED" in m for m in rd["reasons"]), rd["reasons"])
            self.assertEqual(REL["build"](eng)["delivery_level"], "preliminary")

    def test_work_without_acceptance_or_done_blocks_the_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto_revalidado(tmp)

            def sem_aceitacao(d):
                for w in d["items"]:
                    if w["id"] == "WP-0002":
                        w["acceptance"], w["definition_of_done"] = [], ""
            republica_inv(eng, muda=sem_aceitacao)
            c = gate_codes(eng)
            self.assertIn("MISSING_ACCEPTANCE", c)
            self.assertIn("MISSING_DEFINITION_OF_DONE", c)
            self.assertFalse(REL["readiness"](eng)["ready"])


# =============================================================================
# A3 — um FC mudado deixa por revalidar o trabalho e os derivados que o consomem
# =============================================================================

def sms(d):
    for it in d["items"]:
        if it["id"] == "FC-0001":
            it["postconditions"] = list(it.get("postconditions") or []) + [
                "é enviado um SMS ao fornecedor com o número do pedido"]


class A3_FCMudadoDerivadosPorRevalidar(unittest.TestCase):

    def mudado(self, tmp):
        eng = pronto_revalidado(tmp)
        republica_fc(eng, muda=sms)
        self.assertEqual(F["show"](eng)["items"]["FC-0001"]["authorization"]["state"], "stale")
        reautoriza(eng, ["FC-0001"])
        self.assertEqual(F["show"](eng)["items"]["FC-0001"]["authorization"]["state"], "current")
        return eng

    def test_the_work_that_realises_a_changed_contract_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.mudado(tmp)
            achados = [f for f in I["blocking"](eng) if f["ref"] == "WP-0001"]
            self.assertIn("CONTRACT_CHANGED", codigos(achados))
            self.assertNotIn("WP-0002", [f["ref"] for f in I["blocking"](eng)])  # T41
            self.assertFalse(REL["readiness"](eng)["ready"])

    def test_the_hash_alone_does_not_revalidate_the_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.mudado(tmp)
            with self.assertRaises(INV["InventoryError"]) as cm:
                republica_inv(eng)
            self.assertEqual(cm.exception.code, "REVALIDATION_REQUIRED")

    def test_revalidated_work_then_stales_the_spec_and_the_estimate_until_rerendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.mudado(tmp)
            republica_inv(eng, revalidacao={
                "items": {"WP-0001": "still_valid"}, "assessed_by": "autor do inventário",
                "assessment": "o SMS é um efeito do mesmo passo de submissão; o WP cobre-o"})
            self.assertEqual([f for f in I["blocking"](eng) if f["ref"] == "WP-0001"], [])
            rd = REL["readiness"](eng)
            self.assertFalse(rd["ready"])
            self.assertTrue(any("inventário" in m for m in rd["reasons"]), rd["reasons"])
            for nome in ("fx_implementation-spec_v01.md", "fx_estimate_v01.md"):
                p = eng / "_render" / nome
                p.write_text(p.read_text(encoding="utf-8").replace("r1", "r2"),
                             encoding="utf-8")
            self.assertTrue(REL["readiness"](eng)["ready"], REL["readiness"](eng)["reasons"])


# =============================================================================
# A4 — o pacote é o estado que passou a validação, ou não se publica
# =============================================================================

class A4_SnapshotConsistente(unittest.TestCase):

    def test_an_edit_during_the_build_is_refused_and_leaves_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto_revalidado(tmp)
            g = REL["build"].__globals__
            real = g["readiness"]

            def readiness_e_edicao(e):
                out = real(e)
                (Path(e) / out["estimate"]).write_text("# Estimativa\n\nsem inventário\n",
                                                       encoding="utf-8")
                return out
            g["readiness"] = readiness_e_edicao
            try:
                with self.assertRaises(REL["ReleaseError"]) as cm:
                    REL["build"](eng)
            finally:
                g["readiness"] = real
            self.assertEqual(cm.exception.code, "STALE_INPUT")
            self.assertFalse((eng / "_release" / "r0001").exists())

    def test_a_pending_operation_refuses_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto_revalidado(tmp)
            O["_atomic_write"](O["pending_path"](eng), json.dumps(
                {"intent_version": 1, "operation_id": "op-x", "request_hash": "h", "owner": {},
                 "before": {}, "after": {"shared-understanding.md": "f" * 64},
                 "staging": "_ops/staging/op-x"}))
            with self.assertRaises(REL["ReleaseError"]) as cm:
                REL["build"](eng)
            self.assertEqual(cm.exception.code, "RECOVERY_REQUIRED")
            self.assertFalse((eng / "_release" / "r0001").exists())

    def test_a_stable_engagement_still_builds(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto_revalidado(tmp)
            b = REL["build"](eng)
            self.assertEqual(b["delivery_level"], "ready_for_receiver_review")
            self.assertTrue(REL["verify"](Path(b["path"]))["ok"])


# =============================================================================
# A5 — o desenho muda no mesmo caminho; os FC no sha anterior não passam
# =============================================================================

class A5_DesenhoMudadoFCNoShaAntigo(unittest.TestCase):

    def test_the_old_ready_fixture_was_the_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TR["pronto"](tmp, revalidar=False)    # desenho mudado, aprovação renovada
            self.assertEqual(F["blueprint_approval_state"](eng)["state"], "current")
            self.assertIn("BASIS_CHANGED", codigos(I["blocking"](eng)))
            self.assertFalse(REL["readiness"](eng)["ready"])

    def test_a_design_changed_in_place_with_renewed_approval_blocks_the_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto_revalidado(tmp)
            p = eng / BP
            p.write_text(p.read_text(encoding="utf-8").replace(
                "name: estado, type: choice", "name: estado_pedido, type: choice"),
                encoding="utf-8")
            decisao(eng, F["blueprint_approval_block"](eng, "01", AU["OWNER"],
                                                       timestamp="2026-09-24T13:00:00Z"))
            self.assertEqual(F["blueprint_approval_state"](eng)["state"], "current")
            refs = {f["ref"] for f in I["blocking"](eng) if f["code"] == "BASIS_CHANGED"}
            self.assertTrue({"FC-0001", "FC-0003"} <= refs, refs)
            self.assertNotIn("FC-0002", refs)                 # excluído: informa, não bloqueia
            self.assertFalse(REL["readiness"](eng)["ready"])
            g = F["render_gate"](eng, ["FC-0001"])
            self.assertFalse(g["final_allowed"], g)


# =============================================================================
# RV — mover uma dependência exige uma avaliação registada
# =============================================================================

class RV_RevalidacaoExplicita(unittest.TestCase):

    def test_swapping_the_hash_alone_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TR["pronto"](tmp, revalidar=False)
            with self.assertRaises(F["FunctionalError"]) as cm:
                republica_fc(eng)
            self.assertEqual(cm.exception.code, "REVALIDATION_REQUIRED")

    def test_an_editorial_change_is_revalidated_without_reopening_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TR["pronto"](tmp, revalidar=False)
            antes = (eng / "decisions.md").read_text(encoding="utf-8")
            estados = {k: v["authorization"]["state"]
                       for k, v in F["show"](eng)["items"].items()}
            republica_fc(eng, revalidacao=still_valid(eng))
            self.assertEqual(I["blocking"](eng), [])
            self.assertEqual({k: v["authorization"]["state"]
                              for k, v in F["show"](eng)["items"].items()}, estados)
            self.assertEqual((eng / "decisions.md").read_text(encoding="utf-8"), antes)
            doc = json.loads((eng / FCP).read_text(encoding="utf-8"))
            rv = doc["revalidations"][-1]
            self.assertEqual([m["ref"] for m in rv["moved"]], [BP])
            self.assertEqual(rv["assessed_by"], AVALIADOR)
            self.assertTrue(REL["readiness"](eng)["ready"], REL["readiness"](eng)["reasons"])

    def test_a_material_change_blocks_the_dependents_until_they_are_updated(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TR["pronto"](tmp, revalidar=False)
            rv = still_valid(eng, "valor_total passou a opcional; FC-0001 deixa de o garantir")
            rv["items"]["FC-0001"] = "updated"
            republica_fc(eng, muda=sms, revalidacao=rv)
            self.assertIn("FC_NOT_AUTHORIZED", gate_codes(eng))   # o dono volta a autorizar
            reautoriza(eng, ["FC-0001"])
            self.assertIn("CONTRACT_CHANGED", codigos(
                [f for f in I["blocking"](eng) if f["ref"] == "WP-0001"]))

    def test_a_verdict_must_match_the_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TR["pronto"](tmp, revalidar=False)
            with self.assertRaises(F["FunctionalError"]) as cm:
                republica_fc(eng, muda=sms, revalidacao=still_valid(eng))
            self.assertIn("VERDICT_MISMATCH", json.dumps(cm.exception.detail))
            rv = still_valid(eng)
            rv["items"]["FC-0003"] = "updated"
            with self.assertRaises(F["FunctionalError"]) as cm:
                republica_fc(eng, revalidacao=rv)
            self.assertIn("VERDICT_MISMATCH", json.dumps(cm.exception.detail))

    def test_every_dependent_is_assessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TR["pronto"](tmp, revalidar=False)
            rv = still_valid(eng)
            del rv["items"]["FC-0003"]
            with self.assertRaises(F["FunctionalError"]) as cm:
                republica_fc(eng, revalidacao=rv)
            self.assertIn("REVALIDATION_INCOMPLETE", json.dumps(cm.exception.detail))

    def test_an_assessment_and_an_assessor_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TR["pronto"](tmp, revalidar=False)
            for campo, code in (("assessment", "ASSESSMENT_MISSING"),
                                ("assessed_by", "ASSESSOR_MISSING")):
                rv = still_valid(eng)
                rv[campo] = "  "
                with self.assertRaises(F["FunctionalError"]) as cm:
                    republica_fc(eng, revalidacao=rv)
                self.assertIn(code, json.dumps(cm.exception.detail))

    def test_earlier_assessments_are_never_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TR["pronto"](tmp, revalidar=False)
            republica_fc(eng, revalidacao=still_valid(eng))
            with self.assertRaises(F["FunctionalError"]) as cm:
                republica_fc(eng, muda=lambda d: d.update(revalidations=[]))
            self.assertIn("REVALIDATION_DROPPED", json.dumps(cm.exception.detail))

    def test_a_hand_edited_pin_is_caught_when_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TR["pronto"](tmp, revalidar=False)
            doc = json.loads((eng / FCP).read_text(encoding="utf-8"))
            for b in doc["based_on"]:
                if b.get("ref") == BP:
                    b["sha256"] = sha(eng / BP)             # por fora do motor
            (eng / FCP).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")
            self.assertIn("HISTORY_MISMATCH", codigos(I["blocking"](eng)))
            self.assertFalse(REL["readiness"](eng)["ready"])

    def test_a_row_changed_in_place_needs_a_recorded_assessment(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto_revalidado(tmp)
            TI["_linha"](eng, "U-001", "| Critical |", "| Med |")
            self.assertIn(("ROW_CHANGED", "FC-0002"),
                          {(f["code"], f["ref"]) for f in I["stale"](eng)["findings"]})
            with self.assertRaises(F["FunctionalError"]) as cm:
                republica_fc(eng)
            self.assertEqual(cm.exception.code, "REVALIDATION_REQUIRED")
            republica_fc(eng, revalidacao={"items": {"FC-0002": "still_valid"},
                                           "assessment": "a criticidade baixou; o contrato do "
                                           "cálculo continua bloqueado pela mesma pergunta",
                                           "assessed_by": AVALIADOR})
            self.assertNotIn(("ROW_CHANGED", "FC-0002"),
                             {(f["code"], f["ref"]) for f in I["stale"](eng)["findings"]})

    def test_an_unpinned_inventory_blocks_the_final_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = pronto_revalidado(tmp)
            doc = json.loads((eng / WPP).read_text(encoding="utf-8"))
            doc["based_on"] = [b for b in doc["based_on"]
                               if not str(b.get("ref", "")).startswith(FCP + "#")]
            texto = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
            (eng / WPP).write_text(texto, encoding="utf-8")   # como um inventário anterior
            (eng / "_design/history/work-packages.r{:04d}.json".format(
                doc["revision"])).write_text(texto, encoding="utf-8")
            self.assertIn("DEPENDENCY_UNPINNED", codigos(I["blocking"](eng)))
            self.assertFalse(REL["readiness"](eng)["ready"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
