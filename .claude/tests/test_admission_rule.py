"""Admissão de uma pergunta — handoff-v1 (library/kernel/states.md -> Admission of a question).

Substitui a conjunção P-26 (três declarações, oito eixos): uma pergunta entra quando a resposta
pode mudar pelo menos um de cinco aspectos (solução, funcional, aceitação, operação,
viabilidade) e a linha traz `tipo`, `impacto`, `âmbito`, quem responde, `fecho`, `bloqueio` e
`referências` (decisões Q3/Q4 do mantenedor, handoff-v1 F1.5; disposição F0: adaptar).

**A maior parte deste módulo é executável.** Cada cenário constrói uma Shared Understanding
sintética com as colunas novas, corre o parser e o árbitro do motor, e verifica o que sai.
Os invariantes do motor antigo mantêm-se: não edita linhas, conta à parte as SUs sem as
colunas, salta resolvidas, retiradas e estacionadas, e filtra pela passagem. A classe de
canais é anti-regressão textual: a regra antiga era uma instrução escrita em cada canal.

    python .claude/tests/test_admission_rule.py
"""

import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


def load_dashboard():
    path = os.path.join(ROOT, "library", "kernel", "tools", "dashboard.py")
    spec = importlib.util.spec_from_file_location("aisa_dashboard_admission", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


D = load_dashboard()

# As palavras do plano (02 §4) para cada um dos cinco aspectos, e o aspecto a que levam.
PALAVRAS = {"solução": "solucao", "arquitectura": "solucao", "tecnologia": "solucao",
            "funcional": "funcional", "cálculo": "funcional", "transição": "funcional",
            "excepção": "funcional", "resultado": "funcional",
            "aceitação": "aceitacao", "contratual": "aceitacao", "evidência": "aceitacao",
            "segurança": "operacao", "privacidade": "operacao", "operação": "operacao",
            "suporte": "operacao", "migração": "operacao", "recuperação": "operacao",
            "viabilidade": "viabilidade", "dependência": "viabilidade", "custo": "viabilidade",
            "esforço": "viabilidade"}

SU_HEAD = """# Shared Understanding — fixture

## Unknown

| id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""
SU_CONFLICTED = """
## Conflicted

| id | lens | conflito | partes | impacto | âmbito | quem decide | fecho | bloqueio | criticidade | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|
"""
# Uma SU anterior à handoff-v1: sem as colunas da admissão. Nenhuma linha é achado.
SU_HEAD_LEGACY = """# Shared Understanding — fixture legado

## Unknown

| id | lens | pergunta | quem responde | criticidade | custo | swing | ronda |
|---|---|---|---|---|---|---|---|
"""


def su(*rows, conflicted=(), legacy=False):
    head = SU_HEAD_LEGACY if legacy else SU_HEAD
    md = head + "".join(r.rstrip() + "\n" for r in rows)
    if conflicted:
        md += SU_CONFLICTED + "".join(r.rstrip() + "\n" for r in conflicted)
    _h, parsed, _s, _d = D.parse_su(md)
    return parsed


def unknown(uid, pergunta="?", tipo="fact_gap", impacto="funcional: muda o resultado",
            ambito="cálculo do pedido", quem="role: dono do processo", fecho="valor confirmado",
            bloqueio="blocks_scope", criticidade="Med", custo="email",
            swing="dimensionante: muda o cálculo", refs="sources/nota.md#N1", ronda="R-01"):
    return "| %s | data | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        uid, pergunta, tipo, impacto, ambito, quem, fecho, bloqueio, criticidade, custo,
        swing, refs, ronda)


def ids(entries):
    return [e["id"] for e in entries]


# T05 — fx-hv1-02 E01: a regra de arredondamento não muda tecnologia e é material funcional.
T05 = unknown("U-001", "Arredonda-se cada linha ao cêntimo ou só o total?", tipo="design_choice",
              impacto="funcional, aceitação: três linhas de 0,335 € dão 1,02 € por linha e "
                      "1,01 € no total",
              ambito="cálculo do valor do pedido (proposed_to_be)",
              quem="role: responsável de compras com contabilidade",
              fecho="regra escolhida pelo dono, com o exemplo de limite como teste de aceitação",
              bloqueio="blocks_scope", criticidade="Critical", custo="reuniao",
              swing="dimensionante: (a) arredondar cada linha ao cêntimo (b) arredondar só o total",
              refs="sources/entrevista-processo.md#C2; sources/entrevista-processo.md#C3")
# T06 — fx-hv1-02 E02: facto em falta, sem alternativas.
T06 = unknown("U-002", "Qual é o limiar que exige a direcção financeira?", tipo="fact_gap",
              impacto="funcional, aceitação: muda o roteamento da aprovação",
              ambito="roteamento da aprovação (observed_as_is)",
              quem="fonte: despacho da direcção financeira", fecho="valor do despacho, com data",
              swing="dimensionante: o valor define quem aprova",
              refs="sources/entrevista-processo.md#C4; sources/matriz-papeis.md#M4")


class AAdmissaoCorrida(unittest.TestCase):
    """O comportamento, corrido: SU sintética -> parser -> árbitro."""

    def test_t05_a_rounding_rule_that_changes_no_technology_is_admitted(self):
        out = D.arbiter_declarations(su(T05))
        self.assertEqual([], out["sem_declaracao"])
        self.assertEqual(1, out["avaliadas"])

    def test_t06_a_missing_fact_needs_no_fabricated_alternatives(self):
        out = D.arbiter_declarations(su(T06))
        self.assertEqual([], out["sem_declaracao"])
        self.assertEqual([], out["alternativas_nao_avaliadas"])

    def test_a_design_choice_without_two_alternatives_is_reported(self):
        out = D.arbiter_declarations(su(unknown("U-003", tipo="design_choice",
                                                swing="dimensionante: muda o cálculo")))
        self.assertEqual(["U-003"], ids(out["sem_declaracao"]))
        self.assertIn("alternativas", out["sem_declaracao"][0]["motivo"])

    def test_each_missing_field_is_named(self):
        casos = {"tipo": dict(tipo="—"), "sem ambito": dict(ambito=""),
                 "sem quem responde": dict(quem=""), "sem condicao de fecho": dict(fecho="—"),
                 "bloqueio": dict(bloqueio="talvez"), "sem referencias": dict(refs="")}
        for falta, kw in casos.items():
            out = D.arbiter_declarations(su(unknown("U-004", **kw)))
            self.assertEqual(["U-004"], ids(out["sem_declaracao"]), falta)
            self.assertIn(falta, out["sem_declaracao"][0]["motivo"], falta)

    def test_an_impact_without_an_aspect_is_listed_for_parking(self):
        out = D.arbiter_declarations(su(unknown("U-005", impacto="é importante")))
        self.assertEqual(["U-005"], ids(out["sem_impacto"]))
        self.assertEqual(["U-005"], ids(out["sem_declaracao"]))

    def test_every_plan_word_reaches_its_aspect(self):
        for palavra, aspecto in PALAVRAS.items():
            rows = su(unknown("U-006", impacto="%s: muda algo" % palavra))
            self.assertEqual([aspecto], rows[0]["impacto_aspectos"], palavra)
            self.assertEqual([], D.arbiter_declarations(rows)["sem_impacto"], palavra)

    def test_no_blocking_is_a_legitimate_value(self):
        out = D.arbiter_declarations(su(unknown("U-007", bloqueio="—")))
        self.assertEqual([], out["sem_declaracao"])

    def test_a_conflicted_row_owes_who_decides(self):
        x = ("| X-001 | ops | quem valida? | matriz ∧ entrevista | funcional: muda a transição | "
             "aprovação | %s | decisão do dono | blocks_scope | Critical | sources/m.md#M4 | R-01 |")
        self.assertEqual([], D.arbiter_declarations(su(conflicted=[x % "role: dono"]))["sem_declaracao"])
        out = D.arbiter_declarations(su(conflicted=[x % ""]))
        self.assertEqual(["X-001"], ids(out["sem_declaracao"]))
        self.assertIn("sem quem decide", out["sem_declaracao"][0]["motivo"])

    def test_a_decisivo_without_a_referent_is_named_apart(self):
        out = D.arbiter_declarations(su(unknown("U-008", swing="decisivo: muda muito")))
        self.assertEqual(["U-008"], ids(out["decisivo_sem_referente"]))
        out = D.arbiter_declarations(su(unknown("U-009", swing="decisivo: elimina O-002")))
        self.assertEqual([], out["decisivo_sem_referente"])


class BInvariantesDoMotor(unittest.TestCase):

    def test_a_su_without_the_columns_is_counted_apart_and_never_read_as_a_finding(self):
        rows = su("| U-010 | data | quem recebe o preço? | papel de dono | Critical | email | "
                  "dimensionante: muda | R-01 |", legacy=True)
        out = D.arbiter_declarations(rows)
        self.assertEqual(0, out["avaliadas"])
        self.assertEqual(1, out["sem_colunas_handoff"])
        self.assertEqual([], out["sem_declaracao"])

    def test_resolved_withdrawn_and_parked_rows_are_not_evaluated(self):
        rows = su(unknown("U-011", impacto="x", ronda="R-01 — resolved → C-010"),
                  unknown("U-012", impacto="x", ronda="R-01 — retirada P-21 (fora de âmbito)"),
                  unknown("U-013", impacto="x", ronda="R-01 — estacionada (sem impacto demonstrável)"),
                  unknown("U-014", impacto="x"))
        out = D.arbiter_declarations(rows)
        self.assertEqual(1, out["avaliadas"])
        self.assertEqual(["U-014"], ids(out["sem_declaracao"]))

    def test_the_round_filter_reads_only_the_round_just_run(self):
        rows = su(unknown("U-015", impacto="x", ronda="R-01"),
                  unknown("U-016", impacto="x", ronda="R-02"))
        out = D.arbiter_declarations(rows, ronda="R-02")
        self.assertEqual(1, out["avaliadas"])
        self.assertEqual(["U-016"], ids(out["sem_declaracao"]))

    def test_the_motor_never_edits_a_row(self):
        rows = su(unknown("U-017", impacto="x", criticidade="Critical"))
        antes = dict(rows[0])
        D.arbiter_declarations(rows)
        self.assertEqual(antes, rows[0])

    def test_the_motor_publishes_its_own_limits(self):
        out = D.arbiter_declarations(su())
        self.assertIn("PRESENCA dos campos", out["julgamento"])
        self.assertIn("ACEITES por desenho", out["falsos_negativos"])
        self.assertEqual(["aceitacao", "funcional", "operacao", "solucao", "viabilidade"],
                         out["aspectos"])
        for gone in ("sem_eixo", "sem_citacao_m", "conjuncao", "enquadramento_declarado"):
            self.assertNotIn(gone, out)


class CCanais(unittest.TestCase):
    """Anti-regressão textual: cada canal aponta para a regra do kernel e já não enuncia a
    conjunção P-26 (a regra vive num sítio só — plano 03)."""

    CHANNELS = {
        "kernel": ("library", "kernel", "states.md"),
        "CLAUDE.md": ("CLAUDE.md",),
        "aisa-round": (".claude", "skills", "aisa-round", "SKILL.md"),
        "chairman-synthesis": (".claude", "skills", "chairman-synthesis", "SKILL.md"),
        "aisa-answer": (".claude", "skills", "aisa-answer", "SKILL.md"),
        "aisa-capture": (".claude", "skills", "aisa-capture", "SKILL.md"),
        "lens-business": (".claude", "skills", "lens-business", "SKILL.md"),
        "lens-operations": (".claude", "skills", "lens-operations", "SKILL.md"),
        "lens-user": (".claude", "skills", "lens-user", "SKILL.md"),
        "lens-data": (".claude", "skills", "lens-data", "SKILL.md"),
        "lens-governance": (".claude", "skills", "lens-governance", "SKILL.md"),
        "lens-financial": (".claude", "skills", "lens-financial", "SKILL.md"),
    }

    def test_no_channel_restates_the_p26_conjunction(self):
        for name, parts in self.CHANNELS.items():
            text = read(*parts)
            for velho in ("TO-BE DIVERGENCE", "three declarations", "três declarações",
                          "An `M-n` **never** waives", "`M-n` **nunca** dispensa"):
                self.assertNotIn(velho, text, "%s: %s" % (name, velho))

    def test_every_channel_points_at_the_kernel_rule(self):
        for name, parts in self.CHANNELS.items():
            if name == "kernel":
                continue
            self.assertIn("Admission of a question", read(*parts), name)

    def test_every_writer_names_the_fields(self):
        """`aisa-capture` preça linhas PM-U do modelo de processo, nao linhas da SU: os
        campos aplicam-se quando uma lente a adopta; aponta para a regra (teste acima)."""
        for name, parts in self.CHANNELS.items():
            if name == "aisa-capture":
                continue
            flat = " ".join(read(*parts).split())
            for campo in ("tipo", "impacto", "fecho", "bloqueio"):
                self.assertIn(campo, flat, "%s não nomeia %s" % (name, campo))

    def test_the_two_writers_outside_the_round_are_covered(self):
        chair = " ".join(read(".claude", "skills", "chairman-synthesis", "SKILL.md").split())
        self.assertIn("the `F-` and `O-` rounds are checked here", chair)
        answer = " ".join(read(".claude", "skills", "aisa-answer", "SKILL.md").split())
        self.assertIn("passes the same admission rule", answer)

    def test_the_lenses_do_not_turn_the_organisation_gap_into_pending_work(self):
        for lens in ("business", "operations", "user", "data", "governance", "financial"):
            flat = " ".join(read(".claude", "skills", "lens-" + lens, "SKILL.md").split())
            self.assertIn("the organisation's ignorance is not pending work", flat, lens)
            self.assertIn("that is a **requirement** of the to-be", flat, lens)

    def test_the_lenses_stopped_restating_the_admission_rule_in_their_steps(self):
        for lens in ("business", "operations", "user", "data", "governance", "financial"):
            flat = " ".join(read(".claude", "skills", "lens-" + lens, "SKILL.md").split())
            self.assertNotIn("passes admission (Hard rule 7)", flat, lens)
            self.assertIn("passes admission, whole, as the Hard rules state it", flat, lens)

    def test_the_kernel_owns_the_rule_and_the_parking(self):
        states = " ".join(read("library", "kernel", "states.md").split())
        self.assertIn("The organisation's ignorance is not the project's work", states)
        self.assertIn("at least one of five aspects", states)
        self.assertIn("Priority is not blocking", states)
        self.assertIn("Sanctioned edits to existing rows are exactly six", states)
        self.assertIn("parking a question with no demonstrable impact", states)
        self.assertIn("A marker with no reason is **not** a parking", states)


class OrganisationalGapsProduceRequirementsNotExclusions(unittest.TestCase):
    """C7 — as três linhas do registo composto que contradiziam o `blocking-set`."""

    COMPOSED = read("library", "packs", "pp", "decision-model", "composed-disqualifiers.md")

    def row(self, row_id):
        found = [ln for ln in self.COMPOSED.splitlines() if ln.startswith("| **%s**" % row_id)]
        self.assertEqual(1, len(found), row_id)
        return found[0]

    def test_the_three_rows_no_longer_exclude(self):
        for row_id in ("CD-02", "CD-08", "CD-09"):
            ln = self.row(row_id)
            self.assertNotIn("Poor fit — excluded, whole scope", ln, row_id)
            self.assertIn("**Fit with constraints**", ln, row_id)
            self.assertIn("`Risky` row", ln, row_id)

    def test_each_row_points_at_the_blocking_set_entry_it_now_agrees_with(self):
        for row_id, entry in {"CD-02": "B-17", "CD-08": "B-02", "CD-09": "B-26"}.items():
            self.assertIn(entry, self.row(row_id), "%s não cita %s" % (row_id, entry))

    def test_a_name_is_not_a_participating_condition(self):
        self.assertNotIn("named operator", self.row("CD-02"))
        self.assertNotIn("reconciliation owner", self.row("CD-08"))

    def test_technical_blocking_is_untouched(self):
        flat = " ".join(self.COMPOSED.split())
        self.assertIn("seven technical axes", flat)
        self.assertIn("neither is touched here", flat)


if __name__ == "__main__":
    unittest.main(verbosity=2)
