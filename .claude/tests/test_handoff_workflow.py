# -*- coding: utf-8 -*-
"""handoff-v1 F1.4 — perfil, capacidades do pack, schemas e resposta estruturada.

`library/kernel/tools/workflow.py` e o ponto unico onde se pergunta que perfil tem um
engagement e se o pack o suporta (docs/handoff-v1/F1/DESENHO-CONTRATOS.md 2.1). Aqui:

- T04  pack sem capacidade handoff -> UNSUPPORTED_PROFILE, sem fallback;
- T03  (identificacao) engagement sem perfil persistido e legado, recusado para escrita,
       com o caminho de leitura e a versao historica nomeados;
- T36  (leitor novo, schema futuro) falha clara, sem tocar no ficheiro;
- schemas: subconjunto declarado, exemplos do plano validos, campos desconhecidos
       reportados e nunca apagados.
"""
import copy
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "workflow.py"))
EXAMPLES = ROOT / "docs" / "handoff-v1" / "plan" / "examples"
SCHEMAS = ("handoff-state", "handoff-pack", "handoff-response", "handoff-work",
           "handoff-functional", "handoff-index")


def bloco(route="solution-choice", authority=None, **extra):
    b = {"profile": "handoff-v1", "schema_version": "handoff-state/1", "route": route,
         "route_revision": 1,
         "route_basis": {"justification": "plataforma em aberto (sintetico)",
                         "source_refs": [], "authority_ref": authority},
         "route_history": []}
    b.update(extra)
    return b


class Base(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def eng(self, state=None, raw=None, name="eng-x"):
        e = self.root / name
        e.mkdir()
        if raw is not None:
            (e / "_state.json").write_text(raw, encoding="utf-8")
        elif state is not None:
            (e / "_state.json").write_text(json.dumps(state), encoding="utf-8")
        return e

    def pack(self, name, body):
        d = self.root / "packs" / name
        d.mkdir(parents=True)
        (d / "pack.yaml").write_text("pack_id: {}\n{}".format(name, body), encoding="utf-8")
        return self.root / "packs"


class T04_PackSemCapacidade(Base):

    def test_the_pp_pack_declares_the_profile_and_the_three_routes(self):
        caps = W["pack_capabilities"]("pp")
        self.assertTrue(caps["declared"], caps["errors"])
        self.assertEqual(caps["capabilities"]["supported_workflow_profiles"], ["handoff-v1"])
        self.assertEqual(set(caps["capabilities"]["supported_routes"]), set(W["ROUTES"]))

    def test_skeleton_packs_are_refused_without_fallback(self):
        for pack in ("generic", "mendix", "outsystems"):
            r = W["validate_profile"](pack=pack, profile="handoff-v1",
                                      route="solution-choice", birth=True)
            self.assertFalse(r["ok"], pack)
            self.assertEqual(r["code"], "UNSUPPORTED_PROFILE", pack)

    def test_a_declared_profile_without_the_route_is_refused(self):
        packs = self.pack("so-escolha", "supported_workflow_profiles: [handoff-v1]\n"
                                        "supported_routes: [solution-choice]\n"
                                        "design_contract_version: 1\n")
        ok = W["validate_profile"](pack="so-escolha", profile="handoff-v1",
                                   route="solution-choice", birth=True, packs_dir=packs)
        self.assertTrue(ok["ok"], ok)
        no = W["validate_profile"](pack="so-escolha", profile="handoff-v1",
                                   route="platform-constrained", birth=True, packs_dir=packs)
        self.assertEqual(no["code"], "UNSUPPORTED_PROFILE")

    def test_a_malformed_declaration_is_not_read_as_support(self):
        packs = self.pack("torto", "supported_workflow_profiles: handoff-v1\n"
                                   "supported_routes: [solution-choice]\n"
                                   "design_contract_version: 1\n")
        caps = W["pack_capabilities"]("torto", packs)
        self.assertFalse(caps["declared"])
        r = W["validate_profile"](pack="torto", profile="handoff-v1", route="solution-choice",
                                  birth=True, packs_dir=packs)
        self.assertEqual(r["code"], "UNSUPPORTED_PROFILE")

    def test_a_missing_pack_is_refused(self):
        r = W["validate_profile"](pack="nao-existe", profile="handoff-v1",
                                  route="solution-choice", birth=True)
        self.assertEqual(r["code"], "UNSUPPORTED_PROFILE")

    def test_an_unknown_profile_is_refused(self):
        r = W["validate_profile"](pack="pp", profile="classic", route="solution-choice",
                                  birth=True)
        self.assertEqual(r["code"], "UNSUPPORTED_PROFILE")

    def test_change_impact_is_not_a_birth_route(self):
        r = W["validate_profile"](pack="pp", profile="handoff-v1", route="change-impact",
                                  birth=True)
        self.assertEqual(r["code"], "UNSUPPORTED_PROFILE")


class T03_LegadoIdentificado(Base):

    def test_state_without_workflow_is_legacy(self):
        e = self.eng({"engagement": "eng-x", "pack": "pp", "phase": "discovery"})
        self.assertEqual(W["profile_of"](e)["kind"], "legacy")

    def test_legacy_is_refused_with_the_read_path_and_the_historical_version(self):
        e = self.eng({"engagement": "eng-x", "pack": "pp", "phase": "discovery"})
        antes = (e / "_state.json").read_bytes()
        r = W["validate_profile"](e)
        self.assertFalse(r["ok"])
        self.assertEqual(r["code"], "UNSUPPORTED_PROFILE")
        self.assertEqual(r["reasons"][0]["source_code"], "legacy_profile_absent")
        accoes = " ".join(a["action"] for a in r["next_actions"])
        self.assertIn("/status", accoes)
        self.assertIn(W["HISTORICAL_VERSION"], accoes)
        self.assertEqual((e / "_state.json").read_bytes(), antes, "a identificacao escreveu")

    def test_legacy_is_not_the_bootstrap_legacy_mode(self):
        """`LEGACY_MODE` quer dizer sem `_graph/`; o legado do plano quer dizer sem perfil."""
        self.assertNotIn("LEGACY_MODE", W["CODES"])

    def test_an_unreadable_state_is_never_taken_for_legacy(self):
        e = self.eng(raw="{ isto nao e json")
        self.assertEqual(W["profile_of"](e)["kind"], "unreadable")
        self.assertEqual(W["validate_profile"](e)["code"], "INTEGRITY_FAILURE")

    def test_no_state_is_an_engagement_being_born(self):
        e = self.eng()
        self.assertEqual(W["profile_of"](e)["kind"], "unborn")

    def test_a_valid_handoff_engagement_passes(self):
        e = self.eng({"engagement": "eng-x", "pack": "pp", "phase": "discovery",
                      "workflow": bloco()})
        r = W["validate_profile"](e)
        self.assertTrue(r["ok"], r)
        self.assertIsNone(r["code"])

    def test_platform_constrained_needs_the_authority_row(self):
        e = self.eng({"pack": "pp", "workflow": bloco("platform-constrained")})
        self.assertEqual(W["validate_profile"](e)["code"], "INTEGRITY_FAILURE")
        e2 = self.eng({"pack": "pp", "workflow": bloco("platform-constrained", "C-001")},
                      name="eng-y")
        self.assertTrue(W["validate_profile"](e2)["ok"])

    def test_a_malformed_block_is_an_integrity_failure(self):
        e = self.eng({"pack": "pp", "workflow": {"profile": "handoff-v1",
                                                 "schema_version": "handoff-state/1"}})
        self.assertEqual(W["validate_profile"](e)["code"], "INTEGRITY_FAILURE")

    def test_a_handoff_engagement_on_a_pack_without_capability_is_refused(self):
        e = self.eng({"pack": "generic", "workflow": bloco()})
        self.assertEqual(W["validate_profile"](e)["code"], "UNSUPPORTED_PROFILE")


class T36_SchemaFuturo(Base):

    def test_a_future_state_schema_fails_clearly_and_leaves_the_file_alone(self):
        e = self.eng({"pack": "pp", "workflow": bloco(schema_version="handoff-state/2",
                                                      campo_futuro={"a": 1})})
        antes = (e / "_state.json").read_bytes()
        r = W["validate_profile"](e)
        self.assertEqual(r["code"], "SCHEMA_UNSUPPORTED")
        self.assertTrue(r["next_actions"])
        self.assertEqual((e / "_state.json").read_bytes(), antes)


class Schemas(unittest.TestCase):

    def test_every_schema_uses_only_the_declared_subset(self):
        for name in SCHEMAS:
            sch = W["load_schema"](name)
            errors, _ = W["validate"]({}, sch)
            self.assertFalse([e for e in errors if "subconjunto" in e or "$ref" in e], name)

    def test_the_plan_examples_validate(self):
        for name, ex in (("handoff-work", "work-checkpoint.json"),
                         ("handoff-functional", "functional-contract.json")):
            data = json.loads((EXAMPLES / ex).read_text(encoding="utf-8"))
            errors, unknown = W["validate"](data, W["load_schema"](name))
            self.assertEqual(errors, [], name)
            self.assertIn("$.example_only", unknown)

    def test_unknown_fields_are_reported_and_never_dropped(self):
        b = bloco(campo_novo={"x": [1, 2]})
        antes = copy.deepcopy(b)
        errors, unknown = W["validate"](b, W["load_schema"]("handoff-state"))
        self.assertEqual(errors, [])
        self.assertEqual(unknown, ["$.campo_novo"])
        self.assertEqual(b, antes)

    def test_a_keyword_outside_the_subset_is_an_error_not_silence(self):
        errors, _ = W["validate"]({}, {"type": "object", "additionalProperties": False})
        self.assertTrue(errors)

    def test_responses_follow_the_response_schema(self):
        sch = W["load_schema"]("handoff-response")
        for r in (W["response"](True),
                  W["response"](False, "BLOCKING_GAP", [{"detail": "x"}], ["U-001"], "r1",
                                [{"action": "a", "reason": "b"}])):
            self.assertEqual(W["validate"](r, sch)[0], [], r)

    def test_the_eight_stable_codes(self):
        self.assertEqual(set(W["CODES"]), {
            "UNSUPPORTED_PROFILE", "STALE_INPUT", "INCOMPLETE_READ_SET",
            "AUTHORIZATION_REQUIRED", "INTEGRITY_FAILURE", "SCHEMA_UNSUPPORTED",
            "BLOCKING_GAP", "RECOVERY_REQUIRED"})
        self.assertEqual(W["load_schema"]("handoff-response")["properties"]["code"]["enum"][:-1],
                         list(W["CODES"]))

    def test_t07_a_not_applicable_field_without_a_reason_is_invalid(self):
        """T07 (metade N/A): no contrato funcional, N/A sem motivo nao passa."""
        sch = W["load_schema"]("handoff-functional")
        base = json.loads((EXAMPLES / "functional-contract.json").read_text(encoding="utf-8"))
        ok = copy.deepcopy(base)
        ok["items"][0]["not_applicable"] = {"concurrency": "um so utilizador por pedido"}
        self.assertEqual(W["validate"](ok, sch)[0], [])
        vazio = copy.deepcopy(base)
        vazio["items"][0]["not_applicable"] = {"concurrency": ""}
        self.assertTrue(W["validate"](vazio, sch)[0])
        errors, unknown = W["validate"](ok, sch)
        self.assertNotIn("$.items[0].not_applicable.concurrency", unknown,
                         "a chave de um mapa nao e campo desconhecido")

    def test_ok_never_carries_a_code_and_a_refusal_always_does(self):
        with self.assertRaises(ValueError):
            W["response"](True, "BLOCKING_GAP")
        with self.assertRaises(ValueError):
            W["response"](False, "QUALQUER_COISA")


if __name__ == "__main__":
    unittest.main(verbosity=1)
