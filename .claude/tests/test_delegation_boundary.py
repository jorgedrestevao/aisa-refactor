# -*- coding: utf-8 -*-
"""Regra central de delegação a subagentes e fronteira inline da L2 da captura.

Origem (mantenedor, 2026-09-24): numa sessão local, a autoria do process-model (L2 do
`/capture`) foi lançada num agente paralelo. A regra de delegação existia, mas fraca no que o
runtime carrega: o princípio 4 do `CLAUDE.md` e `orchestration.md` falavam de *definir* um
subagente, amarrados às fases; a formulação forte vivia só em `docs/handoff-v1/README.md`, que o
runtime não carrega; e o `aisa-capture` não dizia onde corre a L2. Nenhuma instrução mandava
delegar a L2 — faltava a fronteira. A regra geral passa a viver no `CLAUDE.md`; o
`orchestration.md`, o README e a §3.4 da arquitectura remetem para ela; o `aisa-capture` aplica-a
antes do passo 5.

Limite declarado: estrutural. Prova que a regra existe onde o runtime a lê e que nenhuma
instrução a contraria; não prova que uma sessão a segue.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def ler(*partes):
    return (ROOT.joinpath(*partes)).read_text(encoding="utf-8")


def flat(texto):
    return " ".join(texto.split())


def seccao(texto, titulo, fim="\n## "):
    assert titulo in texto, titulo
    return texto.split(titulo, 1)[1].split(fim, 1)[0]


CLAUDE = ler("CLAUDE.md")
CAPTURE = ler(".claude", "skills", "aisa-capture", "SKILL.md")
ORCH = ler("library", "kernel", "orchestration.md")
README = ler("docs", "handoff-v1", "README.md")
ARQ = ler("docs", "ARCHITECTURE.md")

REGRA = "`CLAUDE.md` → *Delegação a subagentes*"
FRONTEIRA = "**Execution boundary — process-model authoring.**"

# Uma instrução que delega a L2: fala do process-model (ou da L2) e de subagente/paralelo,
# e não diz que corre inline.
ALVO = re.compile(r"process[- ]model|modelo de processo|\bL2\b", re.I)
DELEGA = re.compile(r"subagent|sub-agent|Agent tool|Task tool|general-purpose|\bExplore\b"
                    r"|in the background|em background|in parallel|em paralelo|subagente", re.I)
INLINE = re.compile(r"\binline\b", re.I)


def delega_a_l2(paragrafo):
    return bool(ALVO.search(paragrafo) and DELEGA.search(paragrafo)
                and not INLINE.search(paragrafo))


def ficheiros_do_runtime():
    return sorted(list(ROOT.glob(".claude/skills/*/SKILL.md"))
                  + list(ROOT.glob(".claude/commands/*.md"))
                  + list(ROOT.glob(".claude/agents/*.md"))
                  + list(ROOT.glob("library/kernel/**/*.md"))
                  + [ROOT / "CLAUDE.md"])


class RegraCentral(unittest.TestCase):

    SEC = flat(seccao(CLAUDE, "## Delegação a subagentes (regra geral)")) \
        if "## Delegação a subagentes (regra geral)" in CLAUDE else ""

    def test_a_seccao_existe_entre_os_principios_e_os_caminhos(self):
        titulo = "## Delegação a subagentes (regra geral)"
        self.assertIn(titulo, CLAUDE)
        self.assertLess(CLAUDE.index("## Operating principles"), CLAUDE.index(titulo))
        self.assertLess(CLAUDE.index(titulo), CLAUDE.index("## Key paths"))

    def test_vale_para_qualquer_subagente_e_prevalece_sobre_o_harness(self):
        self.assertIn("definido em `.claude/agents/` ou lançado na hora", self.SEC)
        self.assertIn("em primeiro plano ou em background", self.SEC)
        self.assertIn("Prevalece sobre as sugestões por defeito do harness", self.SEC)

    def test_as_duas_condicoes(self):
        self.assertIn("a tarefa não precisa do contexto de quem a lança, **e** o seu detalhe "
                      "não tem de voltar — só o veredicto", self.SEC)

    def test_um_ficheiro_nao_torna_a_tarefa_elegivel(self):
        self.assertIn("**Escrever o resultado num ficheiro não torna uma tarefa elegível.**",
                      self.SEC)
        self.assertIn("corre na sessão (inline)", self.SEC)

    def test_na_duvida_na_sessao_e_revisor_depois(self):
        self.assertIn("**Na dúvida, na sessão.**", self.SEC)
        self.assertIn("Um revisor corre depois de o que revê estar escrito — nunca ao lado",
                      self.SEC)

    def test_o_principio_quatro_remete_para_a_seccao(self):
        p4 = next(l for l in CLAUDE.splitlines()
                  if l.startswith("4. **Orquestração por fase, subagente só com benefício**"))
        self.assertIn("*Delegação a subagentes* (abaixo)", p4)
        self.assertNotIn("Um subagente só se define quando", p4)


class FronteiraDaL2(unittest.TestCase):

    def test_a_fronteira_vem_entre_o_passo_4_e_o_passo_5(self):
        self.assertTrue(FRONTEIRA in CAPTURE, "falta a fronteira da L2 no aisa-capture")
        i4 = CAPTURE.index("4. **L3 — replay**")
        ib = CAPTURE.index(FRONTEIRA)
        i5 = CAPTURE.index("5. **L2 — process model**")
        self.assertLess(i4, ib)
        self.assertLess(ib, i5)

    def test_o_texto_da_fronteira(self):
        self.assertTrue(FRONTEIRA in CAPTURE, "falta a fronteira da L2 no aisa-capture")
        par = flat(CAPTURE.split(FRONTEIRA, 1)[1].split("5. **L2 — process model**", 1)[0])
        for frase in ("Create and update `_capture/process-model.md` inline in the main session",
                      "does not meet the subagent eligibility rule in `CLAUDE.md`",
                      "even when the result is written to a file",
                      "explicitly record unavailable inputs",
                      "Independent extraction jobs may run in parallel",
                      "only after the model version to be reviewed has been written"):
            self.assertIn(frase, par)


class Remissoes(unittest.TestCase):

    def test_orchestration_remete_para_a_regra_central(self):
        par = flat(ORCH.split("**When a subagent is justified**", 1)[1].split("\n\n", 1)[0])
        self.assertIn(REGRA, par)
        self.assertNotIn("README → *Regras de execução*", par)
        self.assertIn("writing the result to a file does not make a task eligible", par)
        self.assertIn("`aisa-capture` → *Execution boundary — process-model authoring*", par)

    def test_coordenar_nao_e_delegar(self):
        sec = flat(seccao(ORCH, "## Orchestrator boundaries"))
        self.assertIn("Coordinating execution is not delegating it", sec)
        self.assertIn(REGRA, sec)

    def test_o_readme_do_refactor_remete_para_o_claude_md(self):
        self.assertIn(REGRA, flat(seccao(README, "## Regras de execução")))

    def test_a_arquitectura_marca_o_council_como_historico(self):
        sec = flat(seccao(ARQ, "### 3.4 ", fim="\n### 3.5"))
        self.assertIn("é **histórico**", sec)
        self.assertIn(REGRA, sec)


class SemOrdensContraditorias(unittest.TestCase):

    def test_o_detector_distingue_delegar_de_correr_inline(self):
        self.assertTrue(delega_a_l2(
            "Launch a general-purpose subagent in parallel to write `_capture/process-model.md`."))
        self.assertFalse(delega_a_l2(
            "Create and update `_capture/process-model.md` inline in the main session. An "
            "independent review may use a subagent only after the model has been written."))

    def test_nenhuma_instrucao_manda_delegar_a_l2(self):
        ficheiros = ficheiros_do_runtime()
        nomes = {p.relative_to(ROOT).as_posix() for p in ficheiros}
        self.assertIn(".claude/skills/aisa-capture/SKILL.md", nomes)
        self.assertIn("library/kernel/orchestration.md", nomes)
        self.assertIn("CLAUDE.md", nomes)
        achados = []
        for p in ficheiros:
            for par in re.split(r"\n\s*\n", p.read_text(encoding="utf-8")):
                if delega_a_l2(par):
                    achados.append("%s: %s" % (p.relative_to(ROOT).as_posix(), flat(par)[:160]))
        self.assertEqual(achados, [], "\n".join(achados))


if __name__ == "__main__":
    unittest.main()
