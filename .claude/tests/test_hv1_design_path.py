# -*- coding: utf-8 -*-
"""handoff-v1 F4.6 — o percurso de desenho funcional de ponta a ponta, em duas fixtures.

Desenho: `docs/handoff-v1/F4/DESENHO.md` §6. Plano 05 F4 item 5: um percurso pequeno com
jornada, dados, automação, recuperação e teste; sem obrigação de interface quando headless.

`fx-hv1-02` (pedido de equipamento):
    FC-0001 submeter sem duplicar — jornada, dados, automação, recuperação, aceitação;
            autorizado pelo dono (sintético, dados de teste) e publicável no render
    FC-0002 calcular o valor — bloqueado enquanto a regra de arredondamento (U-001) não for
            escolhida: lacuna visível, não autorizável, e o render devolve-a ao autor
`fx-hv1-04` (sincronização headless):
    FC-0010 enviar pedidos aprovados ao ERP-X sem duplicar e com reprocessamento; nenhuma
            superfície, e nada no motor a exige

Limite declarado: os FC são escritos pelo teste a partir do `expected` das fixtures — o que o
passo 13c do `/blueprint` produziria; o teste prova a cadeia dos motores (publicação,
completude, coerência, autorização, render), não que uma sessão os escreve assim.
"""
import json
import runpy
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
AU = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_functional_authorization.py"))
RG = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_functional_render.py"))
FC, F, R, E2E = AU["FC"], AU["F"], AU["R"], AU["E2E"]
M = runpy.run_path(str(TOOLS / "migrate.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))
FIX04 = ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1" / "fx-hv1-04-headless"
OWNER = AU["OWNER"]


def fc_valor(**over):
    it = FC["fc_submissao"](
        id="FC-0002", journey_id="J-0001", purpose="Calcular o valor do pedido",
        requirement_refs=["C-002"], architecture_refs=["pedidos"],
        inputs=[{"field_ref": "pedidos.chave_submissao", "required": True}],
        rule="soma de quantidade × preço unitário por linha, mais IVA à taxa normal",
        postconditions=["pedidos.valor_total fica gravado em EUR"],
        exceptions=[{"condition": "linha sem preço", "behavior": "o pedido não é submetido"}],
        calculation={"units": "EUR", "rounding": ""},
        acceptance_examples=[
            {"kind": "positive", "given": "duas linhas de 10,00 € sem IVA", "when": "calcula",
             "then": "24,60 € com IVA a 23%"},
            {"kind": "negative", "given": "uma linha sem preço", "when": "calcula",
             "then": "não há valor e o pedido não segue"}],
        open_refs=["U-001"])
    it.update(over)
    return it


class Fx02Percurso(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        eng = AU["engagement"](cls.tmp.name)
        RG["approve_blueprint"](eng)
        AU["publish"](eng, [AU["fc_idempotencia"](), fc_valor()], 1)
        cls.bloco = AU["authorize"](eng, ["FC-0001"])
        cls.eng = eng
        cls.show = F["show"](eng)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_journey_carries_data_automation_recovery_and_acceptance(self):
        it = next(i for i in F["read_current"](self.eng)["data"]["items"] if i["id"] == "FC-0001")
        self.assertEqual(it["journey_id"], "J-0001")
        self.assertTrue(all(i["field_ref"].startswith("pedidos.") for i in it["inputs"]))
        self.assertIn("submissao-idempotente", it["architecture_refs"])
        self.assertIn("repetição", it["exceptions"][0]["behavior"])
        self.assertEqual({e["kind"] for e in it["acceptance_examples"]}, {"positive", "negative"})
        self.assertEqual(self.show["items"]["FC-0001"]["gaps"], [])

    def test_the_authorisation_is_synthetic_and_says_so(self):
        self.assertIn("dados de teste", self.bloco)
        self.assertEqual(self.show["items"]["FC-0001"]["authorization"]["state"], "current")

    def test_the_rounding_rule_blocks_the_calculation(self):
        v = self.show["items"]["FC-0002"]
        codes = [g["code"] for g in v["gaps"]]
        for c in ("MISSING_ROUNDING", "MISSING_EXAMPLE_BOUNDARY", "OPEN_BLOCKER"):
            self.assertIn(c, codes)
        self.assertFalse(v["authorizable"])
        with self.assertRaises(F["FunctionalError"]):
            F["authorization_block"](self.eng, ["FC-0002"], OWNER, "SCOPE-0001")

    def test_the_render_publishes_what_is_authorised_and_returns_the_rest(self):
        so_1 = F["render_gate"](self.eng, text="Submissão: FC-0001.")
        self.assertTrue(so_1["final_allowed"], so_1)
        ambos = F["render_gate"](self.eng, text="Submissão: FC-0001. Valor: FC-0002.")
        self.assertFalse(ambos["final_allowed"])
        self.assertEqual({g["fc"] for g in ambos["gaps"]}, {"FC-0002"})
        self.assertEqual({g["owner"] for g in ambos["gaps"]}, {"functional"})

    def test_requirement_to_contract_to_design_is_traceable(self):
        dados = F["read_current"](self.eng)["data"]
        self.assertTrue(dados["based_on"][0]["ref"].startswith("_blueprint/"))
        for it in dados["items"]:
            self.assertTrue(it["requirement_refs"])
            self.assertTrue(it["architecture_refs"])
        self.assertEqual(F["integrity"](self.eng, dados, dict(dados, revision=0)), [])


HEADLESS_BP = """version: v01
blueprint_id: bp-fx-hv1-04-v01
engagement: fx-hv1-04
concretizes_decision: D-001
draft: false

architecture:
  scope: "envio nocturno de pedidos aprovados ao ERP-X, com alerta e reprocessamento"
  authorization: authorized
  experience:
    mode: none
  record_authority:
    - domain: "Envios ao ERP-X"
      access_mode: owned
      key: envios
      su_refs: [C-001]
      fields:
        - {name: id_pedido, type: identifier, required: true, state: Assumed, source: "shared-understanding.md#C-001"}
        - {name: estado_envio, type: choice, required: true, values: [pendente, enviado, falhado], state: Assumed, source: "shared-understanding.md#C-001"}
  compositions:
    - component: sincronizacao-nocturna
      pattern: direct
      boundary: outside-platform
"""

HEADLESS_ROWS = {
    "Confirmed": [
        "| C-002 | operations | O ERP-X recusa pedidos entre as 02:00 e as 03:00 | "
        "nota-integracao.md#¶3 | 2026-09-23 | organizacional | R-01 |"],
    "Unknown": [
        "| U-001 | data | Qual é o limite de pedidos por minuto do ERP-X? | fact_gap | "
        "operação: muda o ritmo de envio | envio ao ERP-X (observed_as_is) | fonte: fornecedor "
        "do ERP-X | limite documentado | delegated_choice | Med | documento | dimensionante: "
        "define o ritmo | nota-integracao.md#¶4 | R-01 |"],
}


def headless(tmp):
    eng = Path(tmp) / "projects" / "fx-hv1-04"
    (eng / "inputs").mkdir(parents=True)
    for src in (FIX04 / "sources").iterdir():
        shutil.copy(src, eng / "inputs" / src.name)
    su = E2E["SU_BIRTH"].replace("fx-hv1-02", "fx-hv1-04").replace(
        "| C-001 | enquadramento | Âmbito: pedido, aprovação e passagem a compras | pedido.md#¶4 |",
        "| C-001 | enquadramento | Âmbito: envio de pedidos aprovados ao ERP-X, sem ecrãs | "
        "pedido.md#¶2 |")
    (eng / "shared-understanding.md").write_text(su, encoding="utf-8", newline="\n")
    (eng / "answers.md").write_text("# Respostas\n", encoding="utf-8", newline="\n")
    (eng / "decisions.md").write_text("# Decisions\n", encoding="utf-8", newline="\n")
    (eng / "_state.json").write_text(E2E["ESTADO"](phase="decision", round="D-01"),
                                     encoding="utf-8", newline="\n")
    M["apply"](eng)
    E2E["publish_analysis"](eng, HEADLESS_ROWS)
    (eng / "_blueprint").mkdir()
    (eng / "_blueprint" / "ux-blueprint_v01.yaml").write_text(HEADLESS_BP, encoding="utf-8",
                                                              newline="\n")
    return eng


def fc_sync():
    return {
        "id": "FC-0010", "journey_id": "J-0010",
        "purpose": "Enviar os pedidos aprovados ao ERP-X sem duplicar a encomenda",
        "scope_id": "SCOPE-0010", "semantic_origin": "proposed_to_be",
        "owner_role": "responsável de compras", "requirement_refs": ["C-001", "C-002"],
        "architecture_refs": ["envios", "sincronizacao-nocturna"], "authorization_ref": None,
        "actors": ["agendamento nocturno"], "trigger": "agendamento diário, fora da janela "
        "02:00–03:00",
        "inputs": [{"field_ref": "envios.id_pedido", "required": True},
                   {"field_ref": "envios.estado_envio", "required": True,
                    "values": ["pendente", "enviado", "falhado"]}],
        "rule": "cada pedido aprovado e pendente é enviado uma vez, com a identidade do pedido "
                "como chave de correlação",
        "postconditions": ["o pedido fica enviado ou falhado, nunca duas vezes enviado"],
        "exceptions": [{"condition": "o ERP-X recusa durante a manutenção",
                        "behavior": "o envio é reagendado e repetido sem duplicar"},
                       {"condition": "falha persistente", "behavior": "alerta e o pedido fica "
                        "falhado, reprocessável selectivamente"}],
        "acceptance_examples": [
            {"kind": "positive", "given": "um pedido aprovado pendente", "when": "o envio corre",
             "then": "fica uma encomenda no ERP-X"},
            {"kind": "negative", "given": "o mesmo pedido já enviado", "when": "o envio "
             "repete", "then": "não nasce segunda encomenda"}],
        "delegated_choices": [{"envelope": "ritmo até ao limite do fornecedor (U-001)",
                               "owner": "equipa de integração",
                               "acceptance": "nenhum pedido recusado por excesso de ritmo"}],
        "proof_refs": ["prova: o ERP-X aceita chave de idempotência (fx-hv1-04 E03)"],
        "publication_status": "draft"}


class Fx04Headless(unittest.TestCase):

    def test_a_headless_scope_owes_no_screen(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = headless(tmp)
            sha = O["digest"](eng / "_blueprint" / "ux-blueprint_v01.yaml")
            dados = {"schema_version": "handoff-functional/1", "engagement_id": eng.name,
                     "revision": 1,
                     "based_on": [{"ref": "_blueprint/ux-blueprint_v01.yaml", "sha256": sha}],
                     "retired_ids": [], "items": [fc_sync()]}
            r = F["publish"](eng, FC["write_draft"](eng, dados))
            self.assertEqual(r["gaps"], [], r["gaps"])
            v = F["show"](eng)["items"]["FC-0010"]
            self.assertTrue(v["authorizable"])
            self.assertEqual(v["conflicts"], [])
            self.assertFalse([g for g in v["gaps"] if "screen" in g["detail"].lower()
                              or "ecrã" in g["detail"].lower()])
            texto = json.dumps(F["read_current"](eng)["data"], ensure_ascii=False)
            self.assertNotIn("Screen", texto, "um FC headless apontou um ecrã")


if __name__ == "__main__":
    unittest.main()
