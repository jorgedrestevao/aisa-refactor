# -*- coding: utf-8 -*-
"""handoff-v1 F4.1 — o motor dos contratos funcionais (`functional.py`).

Desenho: `docs/handoff-v1/F4/DESENHO.md` §1 (Q2). Contrato: `library/kernel/handoff-contract.md`
→ *Functional contract*.

    T20  FC sem regra essencial ou aceitação → `BLOCKING_GAP` no âmbito afectado
    integridade: schema, ids nunca reutilizados, revisão +1, referências que resolvem → recusa
    frescura: base ou inputs mudados depois do rascunho → `STALE_INPUT`
    publicação: uma operação do coordenador, revisão corrente + cópia imutável no histórico

Engagement sintético sobre a fixture `fx-hv1-02` (o de `test_hv1_02_discovery`), com um
desenho mínimo em `_blueprint/`.
"""
import json
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
E2E = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_hv1_02_discovery.py"))
F = runpy.run_path(str(TOOLS / "functional.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))

BLUEPRINT = """version: v01
blueprint_id: bp-fx-hv1-02-v01
engagement: fx-hv1-02
concretizes_decision: D-001
draft: false

architecture:
  scope: "pedido de equipamento, aprovação e passagem a compras"
  authorization: authorized
  record_authority:
    - domain: "Pedidos"
      access_mode: owned
      key: pedidos
      su_refs: [C-001]
      fields:
        - {name: id_pedido, type: identifier, required: true, state: Assumed, source: "shared-understanding.md#C-002"}
        - {name: chave_submissao, type: identifier, required: true, state: Assumed, source: "shared-understanding.md#C-002"}
        - {name: valor_total, type: number, required: true, computed: true, state: Confirmed, source: "shared-understanding.md#C-002"}
        - {name: estado, type: choice, required: true, values: [submetido, aprovado, rejeitado], state: Assumed, source: "shared-understanding.md#C-003"}
  compositions:
    - component: submissao-idempotente
      pattern: direct
entities:
  - name: Pedido
    su_refs: [C-002]
screens:
  - name: PedidoFormScreen
    su_refs: [C-005]
personas:
  - name: Requerente
    su_refs: [C-005]
"""


def engagement(tmp):
    eng = E2E["engagement"](tmp)
    E2E["publish_analysis"](eng)
    (eng / "_blueprint").mkdir()
    (eng / "_blueprint" / "ux-blueprint_v01.yaml").write_text(BLUEPRINT, encoding="utf-8",
                                                              newline="\n")
    return eng


def fc_submissao(**over):
    it = {
        "id": "FC-0001", "journey_id": "J-0001",
        "purpose": "Submeter um pedido de equipamento sem o duplicar",
        "scope_id": "SCOPE-0001", "semantic_origin": "proposed_to_be",
        "owner_role": "responsável de compras",
        "requirement_refs": ["C-002", "C-003"],
        "architecture_refs": ["pedidos", "submissao-idempotente"],
        "authorization_ref": None,
        "actors": ["Requerente"],
        "trigger": "o requerente submete o formulário",
        "inputs": [{"field_ref": "pedidos.chave_submissao", "required": True},
                   {"field_ref": "pedidos.estado", "required": True,
                    "values": ["submetido", "aprovado", "rejeitado"]}],
        "rule": "uma segunda submissão com a mesma chave devolve o pedido existente",
        "postconditions": ["existe um só pedido por chave de submissão"],
        "exceptions": [{"condition": "falha de rede depois da gravação",
                        "behavior": "a repetição devolve o mesmo pedido"}],
        "acceptance_examples": [
            {"kind": "positive", "given": "um pedido novo", "when": "submete",
             "then": "fica um pedido submetido"},
            {"kind": "negative", "given": "o mesmo pedido já submetido", "when": "submete "
             "de novo", "then": "não nasce um segundo pedido"}],
        "publication_status": "draft",
    }
    it.update(over)
    return it


def contracts(eng, items, revision=1, retired=()):
    sha = O["digest"](eng / "_blueprint" / "ux-blueprint_v01.yaml")
    return {"schema_version": "handoff-functional/1", "engagement_id": eng.name,
            "revision": revision,
            "based_on": [{"ref": "_blueprint/ux-blueprint_v01.yaml", "sha256": sha},
                         {"ref": "shared-understanding.md"}],
            "retired_ids": list(retired), "items": items}


def write_draft(eng, data):
    d = F["draft"](eng)
    Path(d["path"]).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return d["draft"]


class Publicacao(unittest.TestCase):

    def test_one_coordinator_operation_with_immutable_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            r1 = F["publish"](eng, write_draft(eng, contracts(eng, [fc_submissao()])))
            self.assertTrue(r1["receipt"])
            self.assertTrue(r1["operation_id"].startswith("functional-"))
            h1 = (eng / "_design/history/functional-contracts.r0001.json").read_bytes()
            self.assertEqual(h1, (eng / F["FC_PATH"]).read_bytes())
            dados = contracts(eng, [fc_submissao(purpose="Submeter sem duplicar")], 2)
            F["publish"](eng, write_draft(eng, dados))
            self.assertEqual(
                (eng / "_design/history/functional-contracts.r0001.json").read_bytes(), h1,
                "a revisão publicada mudou")
            self.assertTrue((eng / "_design/history/functional-contracts.r0002.json").is_file())
            self.assertEqual(F["show"](eng)["revision"], 2)

    def test_publishing_the_same_draft_twice_replays_the_receipt(self):
        """F2 T13: repetir depois de um sucesso sem resposta não duplica nem recusa."""
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            did = write_draft(eng, contracts(eng, [fc_submissao()]))
            r1 = F["publish"](eng, did)
            r2 = F["publish"](eng, did)
            self.assertTrue(r2["replayed"])
            self.assertEqual(r1["operation_id"], r2["operation_id"])
            self.assertEqual(F["show"](eng)["revision"], 1)

    def test_a_draft_starts_from_the_current_revision_plus_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = F["draft"](eng)
            self.assertEqual(json.loads(Path(d["path"]).read_text(encoding="utf-8"))["revision"], 1)

    def test_a_legacy_engagement_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp) / "velho"
            eng.mkdir()
            (eng / "_state.json").write_text(json.dumps({"phase": "decision"}), encoding="utf-8")
            with self.assertRaises(F["FunctionalError"]) as err:
                F["draft"](eng)
            self.assertEqual(err.exception.code, "UNSUPPORTED_PROFILE")


class T20_Completude(unittest.TestCase):

    def publish(self, item):
        self.tmp = tempfile.TemporaryDirectory()
        eng = engagement(self.tmp.name)
        return eng, F["publish"](eng, write_draft(eng, contracts(eng, [item])))

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_complete_contract_has_no_gap(self):
        _e, r = self.publish(fc_submissao())
        self.assertEqual(r["gaps"], [])
        self.assertIsNone(r["code"])

    def test_missing_acceptance_is_a_blocking_gap_not_a_refusal(self):
        eng, r = self.publish(fc_submissao(acceptance_examples=[]))
        self.assertEqual(r["code"], "BLOCKING_GAP")
        self.assertIn("MISSING_ACCEPTANCE_EXAMPLES", [g["code"] for g in r["gaps"]])
        self.assertTrue((eng / F["FC_PATH"]).is_file(), "o FC incompleto não foi publicado")
        self.assertTrue(F["show"](eng)["items"]["FC-0001"]["gaps"])

    def test_not_applicable_with_a_reason_closes_the_field(self):
        it = fc_submissao()
        del it["exceptions"]
        it["not_applicable"] = {"exceptions": "sem excepção além da repetição, já na regra"}
        _e, r = self.publish(it)
        self.assertEqual(r["gaps"], [])

    def test_a_calculation_without_rounding_is_a_gap_never_a_value(self):
        it = fc_submissao(id="FC-0002", purpose="Calcular o valor do pedido",
                          calculation={"units": "EUR", "rounding": ""},
                          acceptance_examples=[{"kind": "positive", "given": "g", "when": "w",
                                                "then": "t"}])
        _e, r = self.publish(it)
        codes = [g["code"] for g in r["gaps"]]
        for c in ("MISSING_ROUNDING", "MISSING_EXAMPLE_NEGATIVE", "MISSING_EXAMPLE_BOUNDARY"):
            self.assertIn(c, codes)

    def test_an_open_blocking_question_blocks_the_scope(self):
        _e, r = self.publish(fc_submissao(open_refs=["U-001"]))
        self.assertIn("OPEN_BLOCKER", [g["code"] for g in r["gaps"]])

    def test_a_delegated_choice_needs_envelope_owner_and_acceptance(self):
        _e, r = self.publish(fc_submissao(delegated_choices=[{"envelope": "até 3 tentativas"}]))
        self.assertIn("DELEGATION_INCOMPLETE", [g["code"] for g in r["gaps"]])


class Integridade(unittest.TestCase):

    def refused(self, eng, data):
        antes = O["digest"](eng / F["FC_PATH"])
        with self.assertRaises(F["FunctionalError"]) as err:
            F["publish"](eng, write_draft(eng, data))
        self.assertEqual(err.exception.code, "INTEGRITY_FAILURE")
        self.assertEqual(O["digest"](eng / F["FC_PATH"]), antes, "publicou apesar da recusa")
        return err.exception

    def test_dead_references_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            for over in ({"requirement_refs": ["C-999"]},
                         {"inputs": [{"field_ref": "pedidos.inexistente", "required": True}]},
                         {"architecture_refs": ["componente-fantasma"]},
                         {"authorization_ref": "decisions.md#D-404"}):
                with self.subTest(over=over):
                    self.refused(eng, contracts(eng, [fc_submissao(**over)]))

    def test_an_empty_not_applicable_reason_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            self.refused(eng, contracts(eng, [fc_submissao(not_applicable={"trigger": ""})]))

    def test_ids_are_never_reused_nor_silently_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            F["publish"](eng, write_draft(eng, contracts(eng, [fc_submissao()])))
            e = self.refused(eng, contracts(eng, [], 2))
            self.assertIn("SILENT_REMOVAL", [p["code"] for p in e.detail["problems"]])
            F["publish"](eng, write_draft(eng, contracts(eng, [], 2, retired=["FC-0001"])))
            e = self.refused(eng, contracts(eng, [fc_submissao()], 3, retired=["FC-0001"]))
            self.assertIn("REUSED_ID", [p["code"] for p in e.detail["problems"]])

    def test_the_revision_moves_by_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            e = self.refused(eng, contracts(eng, [fc_submissao()], revision=3))
            self.assertIn("REVISION", [p["code"] for p in e.detail["problems"]])

    def test_a_field_is_referenced_never_redefined(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            dados = contracts(eng, [fc_submissao()])
            dados["based_on"] = [{"ref": "shared-understanding.md"}]
            e = self.refused(eng, dados)
            self.assertIn("NO_BLUEPRINT", [p["code"] for p in e.detail["problems"]])


class Frescura(unittest.TestCase):

    def test_an_su_change_after_the_draft_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            did = write_draft(eng, contracts(eng, [fc_submissao()]))
            su = eng / "shared-understanding.md"
            su.write_text(su.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaises(F["FunctionalError"]) as err:
                F["publish"](eng, did)
            self.assertEqual(err.exception.code, "STALE_INPUT")

    def test_another_publication_in_between_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            a = write_draft(eng, contracts(eng, [fc_submissao()]))
            b = write_draft(eng, contracts(eng, [fc_submissao(purpose="outra")]))
            F["publish"](eng, a)
            with self.assertRaises(F["FunctionalError"]) as err:
                F["publish"](eng, b)
            self.assertEqual(err.exception.code, "STALE_INPUT")


class Impressao(unittest.TestCase):

    def test_the_fingerprint_ignores_what_authorization_writes(self):
        a = fc_submissao()
        b = dict(a, authorization_ref="decisions.md#D-002", publication_status="integrated",
                 authorization={"ref": "D-002", "revision": 1, "sha256": "0" * 64})
        self.assertEqual(F["item_sha256"](a), F["item_sha256"](b))
        self.assertNotEqual(F["item_sha256"](a), F["item_sha256"](dict(a, rule="outra")))


class CLI(unittest.TestCase):

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(TOOLS / "functional.py")] + list(args),
                              capture_output=True, text=True, timeout=300,
                              env=dict(os.environ, PYTHONIOENCODING="utf-8"))

    def test_check_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            ok = write_draft(eng, contracts(eng, [fc_submissao()]))
            gap = write_draft(eng, contracts(eng, [fc_submissao(rule="")]))
            bad = write_draft(eng, contracts(eng, [fc_submissao(requirement_refs=["C-999"])]))
            for did, rc in ((ok, 0), (gap, 4), (bad, 1)):
                p = self.run_cli("check", "--engagement", str(eng), "--draft", did)
                self.assertEqual(p.returncode, rc, p.stdout + p.stderr)
            p = self.run_cli("publish", "--engagement", str(eng), "--draft", ok)
            self.assertEqual(p.returncode, 0, p.stderr)
            p = self.run_cli("show", "--engagement", str(eng))
            self.assertIn("FC-0001", json.loads(p.stdout)["items"])


if __name__ == "__main__":
    unittest.main()
