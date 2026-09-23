# -*- coding: utf-8 -*-
"""handoff-v1 F4.2 — a autorização do dono a contratos funcionais.

Desenho: `docs/handoff-v1/F4/DESENHO.md` §2 (Q3). O bloco `D-NNN — Contratos funcionais
autorizados` lista cada FC com o `sha256` do item; o motor calcula-o, nunca à mão.

    T22  TO-BE aprovado com premissa AS-IS assumida → a autorização não confirma a premissa
    T24  FC muda após a aprovação → a aprovação da revisão antiga não autoriza a nova
    item 6 (plano 05 F4) → só um papel humano autoriza; um agente nunca autoriza pelo cliente
"""
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
FC = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_functional_contracts.py"))
E2E = FC["E2E"]
F = FC["F"]
R = runpy.run_path(str(TOOLS / "resolve.py"))

OWNER = "owner (responsável de compras, dados de teste — via AskUserQuestion)"
PREMISSA = ("| A-001 | operations | A chefia valida os urgentes no próprio dia útil | "
            "entrevista-processo.md#¶6 (inferido: «no mesmo dia») | 2026-09-23 | "
            "organizacional | R-01 |")


def fc_idempotencia(**over):
    return FC["fc_submissao"](**over)


def fc_urgente(**over):
    it = FC["fc_submissao"](
        id="FC-0003", journey_id="J-0002", purpose="Encaminhar um pedido urgente",
        requirement_refs=["C-003", "A-001"],
        rule="um pedido urgente segue para compras e a chefia valida depois",
        acceptance_examples=[{"kind": "positive", "given": "pedido urgente", "when": "submete",
                              "then": "compras recebe-o antes da validação"}])
    it.update(over)
    return it


def engagement(tmp):
    eng = FC["engagement"](tmp)
    E2E["publish_analysis"](eng, {"Assumed": [PREMISSA]})
    return eng


def publish(eng, items, revision):
    return F["publish"](eng, FC["write_draft"](eng, FC["contracts"](eng, items, revision)))


def authorize(eng, fcs, validated_by=OWNER):
    bloco = F["authorization_block"](eng, fcs, validated_by, "SCOPE-0001",
                                     timestamp="2026-09-23T23:30:00Z")
    d = R["draft"](eng, ["decisions.md"], reads=["_design/functional-contracts.json"])
    p = eng / "_drafts" / d["draft"] / "decisions.md"
    p.write_text(p.read_text(encoding="utf-8") + bloco, encoding="utf-8", newline="\n")
    R["publish"](eng, d["draft"])
    return bloco


class Autorizacao(unittest.TestCase):

    def test_only_complete_contracts_are_authorizable(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publish(eng, [fc_idempotencia(rule="")], 1)
            with self.assertRaises(F["FunctionalError"]) as err:
                F["authorization_block"](eng, ["FC-0001"], OWNER, "SCOPE-0001")
            self.assertEqual(err.exception.code, "BLOCKING_GAP")
            self.assertFalse(F["show"](eng)["items"]["FC-0001"]["authorizable"])

    def test_the_block_carries_the_motor_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publish(eng, [fc_idempotencia()], 1)
            bloco = authorize(eng, ["FC-0001"])
            sha = F["item_sha256"](F["read_current"](eng)["data"]["items"][0])
            self.assertIn("FC-0001 (sha256 {})".format(sha), bloco)
            st = F["show"](eng)["items"]["FC-0001"]["authorization"]
            self.assertEqual(st["state"], "current", st)


class T24_RevisaoNova(unittest.TestCase):

    def test_a_changed_contract_loses_its_authorization_the_others_keep_theirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publish(eng, [fc_idempotencia(), fc_urgente()], 1)
            authorize(eng, ["FC-0001", "FC-0003"])
            publish(eng, [fc_idempotencia(rule="a mesma chave devolve o pedido e avisa"),
                          fc_urgente()], 2)
            items = F["show"](eng)["items"]
            self.assertEqual(items["FC-0001"]["authorization"]["state"], "stale")
            self.assertIn("mudou depois da autorização", items["FC-0001"]["authorization"]["reason"])
            self.assertEqual(items["FC-0003"]["authorization"]["state"], "current",
                             "um FC que não mudou perdeu a autorização")

    def test_a_new_authorization_covers_the_new_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publish(eng, [fc_idempotencia()], 1)
            authorize(eng, ["FC-0001"])
            publish(eng, [fc_idempotencia(rule="outra regra")], 2)
            authorize(eng, ["FC-0001"])
            self.assertEqual(F["show"](eng)["items"]["FC-0001"]["authorization"]["state"],
                             "current")


class T22_PremissaAssumida(unittest.TestCase):

    def test_authorizing_the_to_be_does_not_confirm_the_as_is_premise(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publish(eng, [fc_urgente(semantic_origin="authorized_to_be")], 1)
            antes = FC["E2E"]["rows"](eng)["A-001"]
            authorize(eng, ["FC-0003"])
            depois = FC["E2E"]["rows"](eng)["A-001"]
            self.assertEqual(depois["state"], "Assumed")
            self.assertEqual(antes["claim"], depois["claim"])
            item = F["show"](eng)["items"]["FC-0003"]
            self.assertEqual(item["authorization"]["state"], "current")
            self.assertEqual(item["assumed_premises"], ["A-001"])


class SoPapelHumano(unittest.TestCase):

    def test_an_agent_never_authorizes_for_the_client(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publish(eng, [fc_idempotencia()], 1)
            for quem in ("executor [ÂMBITO AUTORIZADO]",
                         "owner (fc-reviewer, via AskUserQuestion)",
                         "owner (solution-architect, via AskUserQuestion)",
                         "owner (responsável de compras)",
                         "o analista"):
                with self.subTest(quem=quem):
                    with self.assertRaises(F["FunctionalError"]) as err:
                        F["authorization_block"](eng, ["FC-0001"], quem, "SCOPE-0001")
                    self.assertEqual(err.exception.code, "AUTHORIZATION_REQUIRED")

    def test_a_block_written_by_hand_with_an_agent_does_not_authorize(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            publish(eng, [fc_idempotencia()], 1)
            bloco = authorize(eng, ["FC-0001"])
            falso = bloco.replace("D-001", "D-002").replace(
                OWNER, "owner (claude, via AskUserQuestion)")
            d = R["draft"](eng, ["decisions.md"])
            p = eng / "_drafts" / d["draft"] / "decisions.md"
            p.write_text(p.read_text(encoding="utf-8") + falso, encoding="utf-8",
                         newline="\n")
            R["publish"](eng, d["draft"])
            st = F["show"](eng)["items"]["FC-0001"]["authorization"]
            self.assertEqual(st["state"], "invalid")
            self.assertIn("não autoriza pelo cliente", st["reason"])


if __name__ == "__main__":
    unittest.main()
