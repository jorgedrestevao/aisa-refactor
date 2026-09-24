# -*- coding: utf-8 -*-
"""handoff-v1 F6.6 — percursos de ponta a ponta até ao release, em três fixtures.

Desenho: `docs/handoff-v1/F6/DESENHO.md` §6 (Q8).

`fx-hv1-02` (plataforma imposta): o percurso da F5 + âmbito autorizado, inventário,
    pré-visualizações da spec e da estimativa projectadas do inventário, e o release. O nível
    sai `preliminary` e diz porquê. A passagem a compras (C-001) está no âmbito sem contrato
    (N1). Excluir o cálculo do valor deixa um campo obrigatório sem produtor (N4). O pacote não
    esconde nenhum dos dois.
`fx-hv1-05` (migração de legado) — T38: reconciliação, cutover, coexistência, rollback,
    normalização e retenção, cada um ligado a trabalho e a aceitação; tirar um deles é achado.
`fx-hv1-04` (headless) — T37 no pacote: a interface é «não aplicável», e nenhum motivo de
    prontidão pede ecrãs.

Limite declarado: âmbito, inventário e pré-visualizações são escritos pelo teste a partir do
`expected` das fixtures (o que `/blueprint` e `/render` produziriam); as pré-visualizações só
projectam o inventário — nenhuma secção do template foi renderizada e nenhum esforço foi
calculado, e dizem-no. O ensaio T43 sobre o pacote é assistido e fica no relatório.

    python .claude/tests/test_hv1_release_paths.py                 # testes
    python .claude/tests/test_hv1_release_paths.py --write <pasta> # congela o pacote fx-hv1-02
"""
import json
import runpy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
TESTS = ROOT / ".claude" / "tests"
VT = runpy.run_path(str(TESTS / "test_hv1_vertical.py"))
IT = runpy.run_path(str(TESTS / "test_inventory.py"))
TT = runpy.run_path(str(TESTS / "test_trace.py"))
E2E = runpy.run_path(str(TESTS / "test_hv1_02_discovery.py"))
M = runpy.run_path(str(TOOLS / "migrate.py"))
REL = runpy.run_path(str(TOOLS / "release.py"))
TR = runpy.run_path(str(TOOLS / "trace.py"))
FIX05 = TESTS / "fixtures" / "handoff-v1" / "fx-hv1-05-migration"
DONO = ("\n- **Validated by**: owner (responsável de compras, dados de teste — via "
        "AskUserQuestion)\n- **Timestamp**: {}\n")


def previews(eng, label):
    """Só o inventário projectado — sem secção do template renderizada, sem esforço."""
    inv = json.loads((eng / "_design/work-packages.json").read_text(encoding="utf-8"))
    linhas = ["| {} | {} | {} | {} | {} | {} | {} |".format(
        w["id"], w["purpose"], ", ".join(w["realizes"]), ", ".join(w["proves"]) or "—",
        ", ".join(w["depends_on"]) or "—",
        "; ".join(a["condition"] for a in w["acceptance"]) or "—",
        w.get("definition_of_done") or "—") for w in inv["items"]]
    (eng / "_render").mkdir(exist_ok=True)
    (eng / "_render" / "{}_implementation-spec_v01.md".format(label)).write_text(
        "# Implementation Specification — {} (PRÉ-VISUALIZAÇÃO)\n\n> Pré-visualização do ensaio "
        "F6.6: só o inventário projectado de `_design/work-packages.json`. As restantes secções "
        "do template não foram renderizadas.\n\n### Inventário de trabalho (inventário r{})\n\n"
        "| WP | Propósito | Realiza | Prova | Depende de | Aceitação | Definição de feito |\n"
        "|---|---|---|---|---|---|---|\n{}\n".format(label, inv["revision"], "\n".join(linhas)),
        encoding="utf-8")
    (eng / "_render" / "{}_estimate_v01.md".format(label)).write_text(
        "# Estimativa — {} (PRÉ-VISUALIZAÇÃO, sem esforço calculado)\n\n> Nenhuma banda de "
        "esforço foi calculada: o método da estimativa não correu neste ensaio.\n\n"
        "| Unidade (WP) | Esforço |\n|---|---|\n{}\n\nInventário r{}.\n".format(
            label, "\n".join("| {} | por calcular |".format(w["id"]) for w in inv["items"]),
            inv["revision"]), encoding="utf-8")


def fx02(tmp):
    eng, _c, _r = VT["percurso"](tmp)
    VT["_append_decision"](eng, "\n## D-005 — Âmbito de entrega SCOPE-0001\n\n- **Inclui**: "
                           "submissão (J-0001), aprovação com segregação (J-0003), o âmbito "
                           "declarado (C-001)\n- **Exclui**: o cálculo do valor (FC-0002) até à "
                           "regra de arredondamento (U-001)" + DONO.format("2026-09-24T09:00:00Z"),
                           reads=["shared-understanding.md", "_design/functional-contracts.json"])
    IT["publish"](eng, "scope", IT["escopo"](
        eng, includes=[{"ref": "J-0001", "reason": "submissão"},
                       {"ref": "J-0003", "reason": "aprovação com segregação"},
                       {"ref": "C-001", "reason": "o âmbito declarado: inclui a passagem a "
                        "compras"}],
        excludes=[{"ref": "FC-0002", "reason": "arredondamento por escolher (U-001)",
                   "authorization_ref": "decisions.md#D-005"}], authorized_by="D-005"))
    IT["publish"](eng, "work-packages", IT["inventario"](eng, [
        IT["wp"](), IT["wp"]("WP-0002", purpose="Aprovação com segregação no servidor",
                             realizes=["FC-0003", "C-004"], depends_on=["WP-0001"],
                             acceptance=[{"fc": "FC-0003", "condition": "exemplo negativo do "
                                          "FC-0003 pela interface e pela API"}],
                             definition_of_done="exemplos do FC-0003 a passar")]))
    previews(eng, "fx-hv1-02")
    return eng


# ------------------------------------------------------------------ fx-hv1-05 (T38)

ROWS05 = {
    "Confirmed": [
        "| C-002 | operations | O rollback volta ao legado sem perder o que se registou depois "
        "da passagem | entrevista-inventario.md#¶1 | 2026-09-24 | organizacional | R-01 |",
        "| C-003 | data | A reconciliação conta, por tipo e por estado, antes e depois da "
        "passagem | entrevista-inventario.md#¶3 | 2026-09-24 | organizacional | R-01 |",
        "| C-004 | data | O estado em texto livre precisa de uma tabela de correspondência | "
        "nota-legado.md#¶4 | 2026-09-24 | organizacional | R-01 |",
        "| C-005 | governance | O histórico de atribuições conserva-se 10 anos | "
        "nota-legado.md#¶5 | 2026-09-24 | regulatorio | R-01 |",
        "| C-006 | operations | O legado fica consultável só de leitura duas semanas depois da "
        "passagem | nota-legado.md#¶6 | 2026-09-24 | organizacional | R-01 |",
        "| C-007 | operations | A passagem não coincide com o inventário anual de Dezembro | "
        "entrevista-inventario.md#¶4 | 2026-09-24 | organizacional | R-01 |"],
    "Assumed": [
        "| A-001 | data | Cerca de 12 000 registos, ~3% de números de série repetidos | "
        "nota-legado.md#¶1 (estimativa do entrevistado, sem perfil de dados) | 2026-09-24 | "
        "organizacional | R-01 |"],
}
MIGRACAO = {
    "WP-0001": ("Mapeamento e normalização do estado", ["C-004"],
                "a tabela aplicada à amostra dá um só valor para «em uso», «Em Uso» e «EM USO»"),
    "WP-0002": ("Reconciliação por tipo e estado", ["C-003"],
                "amostra: 10 de origem (4 portáteis, 4 monitores, 2 acessórios) contam igual "
                "depois"),
    "WP-0003": ("Cutover e coexistência só de leitura", ["C-006", "C-007"],
                "legado só de leitura durante duas semanas; data fora de Dezembro"),
    "WP-0004": ("Rollback sem perda", ["C-002"],
                "um registo feito depois da passagem sobrevive ao regresso ao legado"),
    "WP-0005": ("Retenção do histórico", ["C-005"],
                "o histórico de atribuições de 2016 continua consultável"),
}


def fx05(tmp, sem=None, sem_aceitacao=None):
    eng = Path(tmp) / "projects" / "fx-hv1-05"
    (eng / "inputs").mkdir(parents=True)
    for src in (FIX05 / "sources").iterdir():
        shutil.copy(src, eng / "inputs" / src.name)
    su = E2E["SU_BIRTH"].replace("fx-hv1-02", "fx-hv1-05").replace(
        "| C-001 | enquadramento | Âmbito: pedido, aprovação e passagem a compras | pedido.md#¶4 |",
        "| C-001 | enquadramento | Âmbito: passagem do registo legado para o novo, com regresso "
        "possível | entrevista-inventario.md#¶1 |")
    (eng / "shared-understanding.md").write_text(su, encoding="utf-8", newline="\n")
    (eng / "answers.md").write_text("# Respostas\n", encoding="utf-8", newline="\n")
    (eng / "decisions.md").write_text("# Decisions\n", encoding="utf-8", newline="\n")
    (eng / "_state.json").write_text(E2E["ESTADO"](phase="decision", round="D-01"),
                                     encoding="utf-8", newline="\n")
    M["apply"](eng)
    E2E["publish_analysis"](eng, ROWS05)
    VT["_append_decision"](eng, "\n## D-001 — Âmbito de entrega SCOPE-0005\n\n- **Inclui**: "
                           "migração do registo e do histórico\n- **Exclui**: amortizações"
                           + DONO.format("2026-09-24T09:00:00Z"))
    IT["publish"](eng, "scope", {
        "schema_version": "handoff-scope/1", "engagement_id": eng.name, "revision": 1,
        "based_on": [], "retired_ids": [], "items": [{
            "id": "SCOPE-0005", "name": "Migração do registo de equipamentos",
            "includes": [{"ref": r, "reason": "obrigação de migração"}
                         for r in ("C-002", "C-003", "C-004", "C-005", "C-006", "C-007")],
            "excludes": [{"ref": "amortizações", "reason": "fora do âmbito",
                          "authorization_ref": "D-001"}],
            "authorized_by": "D-001"}]})
    items = []
    for wid, (purpose, refs, cond) in MIGRACAO.items():
        if wid == sem:
            continue
        items.append(IT["wp"](wid, scope_id="SCOPE-0005", purpose=purpose, realizes=refs,
                              acceptance=[] if wid == sem_aceitacao else [{"condition": cond}],
                              definition_of_done=cond))
    IT["publish"](eng, "work-packages", IT["inventario"](eng, items))
    return eng


class Fx02Pacote(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.eng = fx02(cls.tmp.name)
        cls.r = REL["build"](cls.eng)
        cls.pkg = Path(cls.r["path"])
        cls.index = json.loads((cls.pkg / "handoff-index.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_level_is_computed_and_says_why(self):
        self.assertEqual(self.r["delivery_level"], "preliminary")
        self.assertTrue(any("rastreabilidade" in m for m in self.r["reasons"]))
        self.assertTrue(any("gate de âmbito" in m for m in self.r["reasons"]))

    def test_n1_the_scope_item_without_contract_is_in_the_package(self):
        t = json.loads((self.pkg / "trace.json").read_text(encoding="utf-8"))
        self.assertIn(("NO_CONTRACT", "C-001"),
                      {(f["code"], f["ref"]) for f in t["trace_findings"]})

    def test_n4_the_incoherent_partial_is_in_the_package(self):
        g = json.loads((self.pkg / "scope-gate.json").read_text(encoding="utf-8"))
        self.assertIn(("REQUIRED_FIELD_WITHOUT_PRODUCER", "pedidos.valor_total"),
                      {(f["code"], f["ref"]) for f in g["incoherent"]})

    def test_the_package_verifies_and_carries_the_previews_labelled(self):
        self.assertTrue(REL["verify"](self.pkg)["ok"])
        spec = (self.pkg / "_render/fx-hv1-02_implementation-spec_v01.md").read_text(
            encoding="utf-8")
        self.assertIn("PRÉ-VISUALIZAÇÃO", spec)
        self.assertEqual(self.index["readiness"]["render_checks"],
                         {"implementation-spec": [], "estimate": []})
        self.assertIn("SCOPE-0001", self.index["scope_definition"])


class Fx05Migracao(unittest.TestCase):

    def test_t38_every_migration_obligation_has_work_and_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = TR["trace"](fx05(tmp))
            self.assertTrue(r["ok"], r["findings"])
            self.assertEqual(len(r["chains"]), 6)

    def test_t38_a_missing_rollback_or_its_acceptance_is_a_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            codes = {(f["code"], f["ref"])
                     for f in TR["trace"](fx05(tmp, sem="WP-0004"))["findings"]}
            self.assertIn(("NO_CONTRACT", "C-002"), codes)
        with tempfile.TemporaryDirectory() as tmp:
            codes = {(f["code"], f["ref"]) for f in TR["trace"](
                fx05(tmp, sem_aceitacao="WP-0004"))["findings"]}
            self.assertIn(("NO_TEST", "C-002"), codes)


class Fx04Headless(unittest.TestCase):

    def test_t37_the_package_owes_no_screen(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["DP"]["headless"](tmp)
            sha = runpy.run_path(str(TOOLS / "operation.py"))["digest"](
                eng / "_blueprint" / "ux-blueprint_v01.yaml")
            dados = {"schema_version": "handoff-functional/1", "engagement_id": eng.name,
                     "revision": 1,
                     "based_on": [{"ref": "_blueprint/ux-blueprint_v01.yaml", "sha256": sha}],
                     "retired_ids": [], "items": [TT["DP"]["fc_sync"]()]}
            TT["F"]["publish"](eng, TT["DP"]["FC"]["write_draft"](eng, dados))
            IT["publish"](eng, "scope", {
                "schema_version": "handoff-scope/1", "engagement_id": eng.name, "revision": 1,
                "based_on": [], "retired_ids": [], "items": [{
                    "id": "SCOPE-0010", "name": "Envio ao ERP-X", "authorized_by": None,
                    "includes": [{"ref": "J-0010", "reason": "o envio"}], "excludes": []}]})
            IT["publish"](eng, "work-packages", IT["inventario"](eng, [IT["wp"](
                "WP-0010", scope_id="SCOPE-0010", purpose="Envio nocturno",
                realizes=["FC-0010"],
                acceptance=[{"fc": "FC-0010", "condition": "não nasce segunda encomenda"}])]))
            pkg = Path(REL["build"](eng)["path"])
            t = json.loads((pkg / "trace.json").read_text(encoding="utf-8"))
            idx = json.loads((pkg / "handoff-index.json").read_text(encoding="utf-8"))
            self.assertFalse([f for f in t["trace_findings"] if f["code"] == "UI_IN_HEADLESS"])
            self.assertNotIn("ecrã", json.dumps(idx["readiness"], ensure_ascii=False).lower())
            self.assertNotIn("screen", json.dumps(idx["readiness"]).lower())


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--write":
        with tempfile.TemporaryDirectory() as t:
            e = fx02(t)
            r = REL["build"](e, out=sys.argv[2])
            print(json.dumps(r, ensure_ascii=False))
    else:
        unittest.main()
