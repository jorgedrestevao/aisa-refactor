# -*- coding: utf-8 -*-
"""handoff-v1 F3.5 — fx-hv1-02 de ponta a ponta na Discovery nova.

Fixture: `.claude/tests/fixtures/handoff-v1/fx-hv1-02-pp-constrained` (sintética). Gate de
F3 (`docs/handoff-v1/F3/DESENHO.md` §6): a regra de arredondamento e o valor factual
ausente ficam **visíveis e bem classificados** depois de uma passagem.

A cadeia corre nos motores reais:

    fontes em inputs/ -> rascunho da SU (resolve.draft) -> publicação (resolve.publish, com
    a integridade) -> árbitro (dashboard.arbiter_declarations) -> registo `lens`
    (coverage.lens_skeleton / finalize) -> fecho (coverage.lens_round_state) -> aviso
    Discovery -> Framing (dashboard.gate_state) e o que o dono vê (dashboard.build_model)

Limite declarado: as linhas da análise integrada são escritas por este teste a partir do
`expected` da fixture — o que uma sessão produziria. O teste prova que, escritas assim,
atravessam a cadeia sem se perderem nem mudarem de classe; não prova que uma sessão as
escreve. Isso mede-se nos pilotos.

    T05  regra de arredondamento: material funcional, admitida, com o exemplo de limite
    T06  facto em falta: `fact_gap` sem alternativas inventadas
    T07  pergunta sem impacto: estacionada com motivo; N/A sem motivo não fecha a cobertura
    T08  concordância sem evidência: não promove a `Confirmed`
"""
import json
import runpy
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
FIX = ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1" / "fx-hv1-02-pp-constrained"
SCEN = json.loads((FIX / "scenario.json").read_text(encoding="utf-8"))
ESTADO = runpy.run_path(str(ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1"
                            / "estado.py"))["estado"]
M = runpy.run_path(str(TOOLS / "migrate.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
C = runpy.run_path(str(TOOLS / "coverage.py"))
D = runpy.run_path(str(TOOLS / "dashboard.py"))
SIX = ["business", "operations", "user", "data", "governance", "financial"]
EXP = {e["id"]: e for e in SCEN["expected"]}

SU_BIRTH = """# Shared Understanding — fx-hv1-02

> Fase actual: Discovery
> Última actualização: 2026-09-23

## Confirmed

| id | lens | claim | evidência | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|
| C-001 | enquadramento | Âmbito: pedido, aprovação e passagem a compras | pedido.md#¶4 | 2026-09-23 | organizacional | R-00 |

## Assumed

| id | lens | claim | base da assumption | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|

## Unknown

| id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Conflicted

| id | lens | conflito | partes | impacto | âmbito | quem decide | fecho | bloqueio | criticidade | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Risky

| id | lens | risco | impacto | mitigação proposta | ronda |
|---|---|---|---|---|---|
"""

# A análise integrada da passagem R-01, escrita a partir do `expected` da fixture.
E01 = EXP["E01"]["classification"]
ANALISE = {
    "Confirmed": [
        "| C-002 | business | O valor do pedido é a soma de quantidade × preço unitário por "
        "linha, mais IVA | entrevista-processo.md#¶2 | 2026-09-23 | organizacional | R-01 |",
        "| C-003 | operations | Pedidos urgentes seguem para compras e a chefia valida no mesmo "
        "dia | entrevista-processo.md#¶5 | 2026-09-23 | organizacional | R-01 |",
        "| C-004 | governance | A chefia nunca aprova um pedido feito por si própria | "
        "matriz-papeis.md#¶2 | 2026-09-23 | organizacional | R-01 |",
        "| C-005 | user | Requerente cria e consulta os seus pedidos | matriz-papeis.md#¶1 "
        "| 2026-09-23 | organizacional | R-01 |",
    ],
    "Unknown": [
        # E01 — T05: design_choice, funcional + aceitação, blocks_scope, com o limite.
        "| U-001 | financial | Arredonda-se cada linha ao cêntimo ou só o total? | design_choice "
        "| funcional, aceitação: três linhas de 0,335 € dão 1,02 € por linha e 1,01 € no total "
        "| {} (proposed_to_be) | role: {} | regra escolhida pelo dono, com o exemplo de limite "
        "como teste de aceitação | {} | Critical | reuniao | dimensionante: (a) {} (b) {} | "
        "entrevista-processo.md#¶2; entrevista-processo.md#¶3 | R-01 |".format(
            E01["affected_scope"], E01["owner_role"], E01["blocking"],
            E01["alternatives"][0], E01["alternatives"][1]),
        # E02 — T06: fact_gap, sem alternativas.
        "| U-002 | data | Qual é o limiar que exige a direcção financeira? | fact_gap | "
        "funcional, aceitação: muda o roteamento da aprovação | roteamento da aprovação "
        "(observed_as_is) | fonte: despacho da direcção financeira | valor do despacho, com data "
        "| blocks_scope | Critical | documento | dimensionante: o valor define quem aprova | "
        "entrevista-processo.md#¶4; matriz-papeis.md#¶4 | R-01 |",
        # E03 — T07: sem impacto demonstrável, estacionada com motivo.
        "| U-003 | user | O botão de submeter deve ser verde? | design_choice | — | ecrã de "
        "submissão | role: requerente | — | none | Low | email | cosmético: (a) verde (b) outra "
        "cor | entrevista-processo.md#¶7 | R-01 — estacionada (R-01: sem impacto "
        "demonstrável) |",
    ],
}


def add_rows(md, section, rows):
    lines = md.split("\n")
    i = lines.index("## " + section)
    j = i + 1
    while j < len(lines) and not lines[j].startswith("|"):
        j += 1
    while j < len(lines) and lines[j].startswith("|"):
        j += 1
    return "\n".join(lines[:j] + rows + lines[j:])


def engagement(tmp):
    eng = Path(tmp) / "projects" / "fx-hv1-02"
    (eng / "inputs").mkdir(parents=True)
    for src in (FIX / "sources").iterdir():
        shutil.copy(src, eng / "inputs" / src.name)
    (eng / "shared-understanding.md").write_text(SU_BIRTH, encoding="utf-8", newline="\n")
    (eng / "answers.md").write_text("# Respostas\n", encoding="utf-8", newline="\n")
    (eng / "decisions.md").write_text("# Decisions\n", encoding="utf-8", newline="\n")
    (eng / "_state.json").write_text(ESTADO(phase="discovery", round="R-01"),
                                     encoding="utf-8", newline="\n")
    M["apply"](eng)
    return eng


def publish_analysis(eng, extra=None):
    d = R["draft"](eng, ["shared-understanding.md"], reads=["inputs/**/*"])
    p = eng / "_drafts" / d["draft"] / "shared-understanding.md"
    md = p.read_text(encoding="utf-8")
    for section, rows in (extra or ANALISE).items():
        md = add_rows(md, section, rows)
    p.write_text(md, encoding="utf-8", newline="\n")
    return R["publish"](eng, d["draft"])


def rows(eng):
    _h, parsed, _s, _d = D["parse_su"]((eng / "shared-understanding.md").read_text(
        encoding="utf-8"))
    return {r["id"]: r for r in parsed}


class Passagem(unittest.TestCase):
    """Uma passagem R-01 sobre a fixture, do rascunho ao aviso de fase."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.eng = engagement(cls.tmp.name)
        cls.pub = publish_analysis(cls.eng)
        cls.rows = rows(cls.eng)
        cls.arb = D["arbiter_declarations"](list(cls.rows.values()))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_analysis_is_published_by_the_coordinator(self):
        self.assertTrue(self.pub["receipt"], self.pub)
        self.assertTrue({"C-002", "U-001", "U-002", "U-003"} <= set(self.rows))

    # ---------------------------------------------------------------- T05
    def test_t05_the_rounding_rule_is_material_and_admitted(self):
        u = self.rows["U-001"]
        self.assertEqual(u["state"], "Unknown")
        self.assertEqual(u.get("tipo"), E01["question_type"])
        self.assertEqual(u.get("bloqueio"), E01["blocking"])
        self.assertEqual(u["impacto_aspectos"], ["funcional", "aceitacao"])
        self.assertIn("1,02 €", u["impacto_texto"], "o exemplo de limite perdeu-se")
        self.assertNotIn("U-001", [e["id"] for e in self.arb["sem_declaracao"]])
        self.assertNotIn("U-001", [e["id"] for e in self.arb["sem_impacto"]])
        self.assertEqual(u["swing_class"], "dimensionante",
                         "classificada como cosmética por não mudar a tecnologia")

    # ---------------------------------------------------------------- T06
    def test_t06_the_missing_fact_owes_no_alternatives(self):
        u = self.rows["U-002"]
        self.assertEqual(u.get("tipo"), "fact_gap")
        self.assertNotIn("U-002", [e["id"] for e in self.arb["sem_declaracao"]])
        self.assertNotIn("U-002", [e["id"] for e in self.arb["alternativas_nao_avaliadas"]])

    # ---------------------------------------------------------------- T07
    def test_t07_the_colour_question_is_parked_with_its_reason(self):
        u = self.rows["U-003"]
        self.assertTrue(u["parked"], u)
        self.assertIn("sem impacto demonstrável", u["parked_reason"])
        crit = [r["id"] for r in D["_critical"](list(self.rows.values()), "Unknown")]
        self.assertEqual(sorted(crit), ["U-001", "U-002"])

    def test_t07_na_without_reason_does_not_close_the_coverage(self):
        sk = C["lens_skeleton"](self.eng, "R-01")
        sk["generated_at"] = "2026-09-23T20:00:00Z"
        for d in SIX:
            sk["lens_coverage"]["dimensions"][d] = {
                "status": "assessed", "refs": ["C-002"], "justification": "x"}
        sk["lens_coverage"]["dimensions"]["user"] = {
            "status": "not_applicable", "refs": [], "justification": ""}
        sk["lens_coverage"]["conflict_scan"] = {"refs": [], "note": "nenhum"}
        p = Path(self.tmp.name) / "na.json"
        p.write_text(json.dumps(sk), encoding="utf-8")
        self.assertFalse(C["finalize"](self.eng, p)["published"])

    # ---------------------------------------------------------------- T08
    def test_t08_agreement_does_not_promote_to_confirmed(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            consenso = {"Confirmed": [
                "| C-010 | financial | O limiar da direcção financeira é 5 000 € | o analista e "
                "o revisor concordam | 2026-09-23 | organizacional | R-01 |"]}
            with self.assertRaises(R["ResolveError"]) as err:
                publish_analysis(eng, consenso)
            self.assertEqual(getattr(err.exception, "code", ""), "INTEGRITY_FAILURE")
            self.assertNotIn("C-010", rows(eng))

    # ---------------------------------------------------------------- fecho e aviso
    def test_the_passagem_closes_and_both_questions_stay_visible(self):
        sk = C["lens_skeleton"](self.eng, "R-01")
        sk["generated_at"] = "2026-09-23T20:30:00Z"
        cov = {
            "business": ("assessed", ["C-002", "C-001"], "resultado e regra de cálculo"),
            "operations": ("assessed", ["C-003"], "excepção urgente e quem valida"),
            "user": ("assessed", ["C-005"], "requerente e o seu percurso"),
            "data": ("gap", ["U-002"], "o limiar vive num despacho não fornecido"),
            "governance": ("assessed", ["C-004"], "separação de funções na aprovação"),
            "financial": ("gap", ["U-001"], "a regra de arredondamento muda o valor"),
        }
        for d, (st, refs, j) in cov.items():
            sk["lens_coverage"]["dimensions"][d] = {"status": st, "refs": refs,
                                                    "justification": j}
        sk["lens_coverage"]["conflict_scan"] = {"refs": [], "note": "nenhum conflito entre "
                                                                    "as fontes"}
        p = Path(self.tmp.name) / "lens.json"
        p.write_text(json.dumps(sk), encoding="utf-8")
        self.assertTrue(C["finalize"](self.eng, p)["published"])
        st = C["lens_round_state"](self.eng, "R-01")
        self.assertTrue(st["closes"], st["reasons"])
        self.assertEqual(st["coverage"], "gaps")
        gaps = {g["item"] for g in st["state"]["gaps"]}
        self.assertEqual(gaps, {"LENS:data", "LENS:financial"})
        # o dono vê as duas perguntas em aberto, com a classificação certa
        model = D["build_model"](self.eng, date(2026, 9, 23))
        abertas = {r["id"]: r for r in D["_open_rows"](list(rows(self.eng).values()),
                                                         "Unknown")}
        self.assertEqual(set(abertas), {"U-001", "U-002"})
        self.assertEqual(abertas["U-001"]["tipo"], "design_choice")
        self.assertEqual(abertas["U-002"]["tipo"], "fact_gap")
        self.assertEqual(model["su"]["sections"]["Unknown"]["open"], 2)
        # e o aviso Discovery -> Framing lê o registo desta passagem
        g = D["gate_state"](self.eng, "discovery→framing")
        c = next(c for c in g["criteria"] if "registo lens" in c["criterion"])
        self.assertTrue(c["ok"], c)
        crit = next(c for c in g["criteria"] if c["criterion"] == "Unknown Critical = 0")
        self.assertFalse(crit["ok"], "as duas perguntas graves deixaram de pesar no aviso")
        self.assertIn("U-001", crit["value"])
        self.assertIn("U-002", crit["value"])


class StatusLeORegisto(unittest.TestCase):

    def test_the_passagem_line_reads_the_lens_record(self):
        s = (ROOT / ".claude" / "skills" / "aisa-status" / "SKILL.md").read_text(
            encoding="utf-8")
        self.assertIn("engagement.lentes_ronda_aberta: corridas, fecha, revista, motivos", s)
        self.assertNotIn("`/round <perspectiva em falta>`", s)


class CapturaAdmitePorTipo(unittest.TestCase):
    """A captura escreve PM-U pela mesma regra de admissão (DESENHO §5)."""

    def test_the_template_carries_type_and_impact_at_the_end(self):
        t = (ROOT / "library" / "kernel" / "capture-templates" /
             "process-model.template.md").read_text(encoding="utf-8")
        head = next(l for l in t.splitlines() if l.startswith("| id | question |"))
        cols = [c.strip() for c in head.strip("|").split("|")]
        self.assertEqual(cols[-2:], ["tipo", "impacto"])
        self.assertEqual(cols[4], "criticidade", "os leitores posicionais partiam")
        self.assertIn("*Admission of a\nquestion*", t)

    def test_the_capture_skill_applies_admission(self):
        s = " ".join((ROOT / ".claude" / "skills" / "aisa-capture" / "SKILL.md").read_text(
            encoding="utf-8").split())
        self.assertIn("Every PM-U row passes the admission rule", s)
        self.assertIn("a candidate that moves none of the five aspects is not written", s)


if __name__ == "__main__":
    unittest.main()
