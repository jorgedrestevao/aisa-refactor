# -*- coding: utf-8 -*-
"""handoff-v1 F5.5 — o primeiro percurso vertical, pelos motores, e o pacote experimental.

Desenho: `docs/handoff-v1/F5/DESENHO.md` §5 (Q6, Q9).

`fx-hv1-02` (plataforma imposta), de ponta a ponta:
    análise publicada (F3) → decisão de imposição D-001 → candidatos dentro da plataforma
    (T27) → router com evidência (T28) → mandatos (T25, T29) → pareceres recebidos e
    dispostos (T26, T29) → decisão D-002 → desenho aprovado D-003 → FC-0001 autorizado D-004,
    FC-0002 bloqueado pela regra de arredondamento (U-001) → `render_gate` →
    pacote experimental: ficheiros com `sha256` e índice `handoff-index/1`,
    `delivery_level: preliminary`, com `implementation-spec` e estimativa em `exclusions` (Q9).

Limite declarado: os candidatos, os pareceres e os FC são escritos pelo teste a partir do
`expected` da fixture — o que o autor, os revisores e o `/blueprint` produziriam. O teste
prova a cadeia dos motores e a integridade do pacote, não que uma sessão os escreve assim;
o ensaio T43 (destinatário em contexto novo) é assistido e fica no relatório.

    python .claude/tests/test_hv1_vertical.py                 # testes
    python .claude/tests/test_hv1_vertical.py --write <pasta> # congela o pacote
"""
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
TESTS = ROOT / ".claude" / "tests"
E2E = runpy.run_path(str(TESTS / "test_hv1_02_discovery.py"))
FC = runpy.run_path(str(TESTS / "test_functional_contracts.py"))
AU = runpy.run_path(str(TESTS / "test_functional_authorization.py"))
RG = runpy.run_path(str(TESTS / "test_functional_render.py"))
DP = runpy.run_path(str(TESTS / "test_hv1_design_path.py"))
RV = runpy.run_path(str(TOOLS / "review.py"))
F = runpy.run_path(str(TOOLS / "functional.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))
W = runpy.run_path(str(TOOLS / "workflow.py"))
PLATAFORMA = "Plataforma X"
AUTORIDADE = "decisions.md#D-001"
UNIDADE = "library/packs/pp/architecture-templates/architecture-core.md"


def _append_decision(eng, bloco, reads=()):
    d = R["draft"](eng, ["decisions.md"], reads=list(reads))
    p = eng / "_drafts" / d["draft"] / "decisions.md"
    p.write_text(p.read_text(encoding="utf-8") + bloco, encoding="utf-8", newline="\n")
    R["publish"](eng, d["draft"])


def analysis(tmp):
    """F3: análise publicada; a rota com a autoridade que a impõe (D-001)."""
    eng = E2E["engagement"](tmp)
    rows = dict(E2E["ANALISE"])
    rows["Assumed"] = [AU["PREMISSA"]]
    E2E["publish_analysis"](eng, rows)
    _append_decision(eng, "\n## D-001 — Plataforma imposta\n\n- **Decisão**: a solução "
                     "constrói-se na {} (imposta pela direcção de SI, sintético)\n"
                     "- **Evidência**: pedido.md#¶2\n- **Validated by**: owner (dados de "
                     "teste)\n- **Timestamp**: 2026-09-23T20:00:00Z\n".format(PLATAFORMA))
    p = eng / "_state.json"
    st = json.loads(p.read_text(encoding="utf-8"))
    st["phase"] = "options"
    st["workflow"]["route"] = "platform-constrained"
    st["workflow"]["route_basis"] = {"justification": "plataforma imposta pela direcção de SI "
                                     "(sintético)", "source_refs": ["pedido.md#¶2"],
                                     "authority_ref": AUTORIDADE}
    p.write_text(json.dumps(st, ensure_ascii=False) + "\n", encoding="utf-8")
    return eng


def candidates(eng):
    """F5.1: duas formas dentro da plataforma imposta, nenhuma fora (T27)."""
    base = {"option_class": "aplicação na plataforma", "platform": PLATAFORMA,
            "order_of_magnitude": {"value": "4–6 semanas", "source": "ANALOGY (sintético)"},
            "risks": ["regra de arredondamento por escolher (U-001)"],
            "premise_refs": ["C-002", "C-004"]}
    items = [dict(base, id="O-001", name="Aplicação de formulário com fluxo de aprovação",
                  technology=PLATAFORMA + " — formulário + fluxo, dados na plataforma",
                  architecture="pedido com chave de submissão; aprovação por papel; passagem "
                               "a compras por fluxo", reversibility="média"),
             dict(base, id="O-002", name="Aplicação orientada a registos",
                  technology=PLATAFORMA + " — aplicação de registos, dados na plataforma",
                  architecture="registo de pedidos com estados e regras de negócio no "
                               "armazenamento", reversibility="baixa",
                  order_of_magnitude={"value": "6–8 semanas", "source": "ANALOGY (sintético)"})]
    dr = RV["draft_candidates"](eng)
    data = {"schema_version": "handoff-candidates/1", "engagement_id": eng.name, "revision": 1,
            "route": "platform-constrained", "based_on": [{"ref": "shared-understanding.md"}],
            "retired_ids": [], "criteria": ["cumprir a segregação (C-004)",
                                            "calcular o valor sem ambiguidade (U-001)"],
            "exclusions": [{"what": "outras plataformas", "reason": "imposta (D-001)"}],
            "imposed_platform": PLATAFORMA, "imposition_ref": AUTORIDADE,
            "reduction_reason": "duas formas viáveis dentro da imposta", "items": items}
    Path(dr["path"]).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return RV["publish_candidates"](eng, dr["draft"])


QUESTOES = {
    "architecture-review": "A forma O-001 aguenta a submissão sem duplicar e a aprovação por papel?",
    "security-operation": "A segregação (C-004) é aplicada no servidor e não só no ecrã?",
    "ux-process": "O requerente (C-005) consegue criar e consultar sem passos inúteis?",
}


def review(eng, m, findings):
    fontes = [r for r in m["input_refs"] if r["ref"] in ("_design/candidates.json",
                                                         "shared-understanding.md")]
    fontes += m["knowledge_refs"]
    payload = {"task_id": m["task_id"], "role": m["role"],
               "input_revision": m["candidate_revision"],
               "coverage": [{"question": q, "checked": "candidatos r1 e linhas citadas"}
                            for q in m["questions"]],
               "findings": findings, "assumptions": [], "unanswered": [],
               "recommended_actions": [],
               "sources_used": [{"ref": r["ref"], "sha256": r["sha256"]} for r in fontes]}
    return RV["receive"](eng, m["task_id"], payload)


def reviews(eng):
    """F5.2–F5.3: router → mandatos → pareceres → disposições."""
    rota = RV["route"](eng)
    mandatos = {}
    for s in rota["selected"]:
        k = [UNIDADE] if s["role"] == "architecture-review" else []
        mandatos[s["role"]] = RV["mandate"](eng, s["role"], [QUESTOES[s["role"]]],
                                            knowledge=k, scope_ids=["O-001"])["data"]
    review(eng, mandatos["architecture-review"], [{
        "target": "O-001", "severity": "material", "kind": "recommendation",
        "evidence": "entrevista-processo.md#¶3 (valor por linha)",
        "failure_scenario": "o valor muda conforme a regra de arredondamento escolhida",
        "closing_condition": "regra escolhida pelo dono e fixada no FC do valor"}])
    review(eng, mandatos["security-operation"], [{
        "target": "O-001", "severity": "blocking", "kind": "recommendation",
        "evidence": "matriz-papeis.md#¶3 (C-004)",
        "failure_scenario": "um chefe aprova o próprio pedido se a regra só esconder o botão",
        "closing_condition": "a regra aplicada no servidor e um teste negativo no FC"}])
    review(eng, mandatos["ux-process"], [])
    RV["dispose"](eng, "REV-0001.F01", "deferred", "fica para o FC do valor",
                  impact="FC-0002 não é autorizável enquanto U-001 estiver aberta")
    RV["dispose"](eng, "REV-0002.F01", "accepted", "entra no desenho como regra do servidor "
                  "e no FC como exemplo negativo")
    return rota


def decide_and_design(eng):
    """Decisão D-002, desenho aprovado D-003, FC publicado e FC-0001 autorizado D-004."""
    _append_decision(eng, "\n## D-002 — Solução escolhida: O-001\n\n- **Escolhida**: O-001 "
                     "(candidatos r1)\n- **Descartada**: O-002 — reversibilidade baixa\n"
                     "- **Validated by**: owner (dados de teste)\n- **Timestamp**: "
                     "2026-09-23T21:00:00Z\n", reads=["_design/candidates.json"])
    (eng / "_blueprint").mkdir()
    (eng / "_blueprint" / "ux-blueprint_v01.yaml").write_text(
        FC["BLUEPRINT"].replace("concretizes_decision: D-001", "concretizes_decision: D-002"),
        encoding="utf-8", newline="\n")
    RG["approve_blueprint"](eng)
    AU["publish"](eng, [AU["fc_idempotencia"](), DP["fc_valor"]()], 1)
    AU["authorize"](eng, ["FC-0001"])


PACOTE = ["shared-understanding.md", "decisions.md", "answers.md", "_state.json",
          "_design/candidates.json", "_design/functional-contracts.json",
          "_blueprint/ux-blueprint_v01.yaml"]


def package(eng, out):
    """O pacote experimental: cópia dos ficheiros, `sha256` e índice `handoff-index/1`."""
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    rels = PACOTE + sorted(p.relative_to(eng).as_posix()
                           for p in (eng / "_design" / "reviews").glob("*.json"))
    rels += sorted("inputs/" + p.name for p in (eng / "inputs").iterdir())
    for rel in rels:
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(eng / rel, out / rel)
    gate = F["render_gate"](eng, text="Submissão: FC-0001. Valor: FC-0002.")
    (out / "render-gate.json").write_text(json.dumps(gate, ensure_ascii=False, indent=1) + "\n",
                                          encoding="utf-8", newline="\n")
    rels.append("render-gate.json")
    show = F["show"](eng)
    rv = RV["show_reviews"](eng)
    try:
        code = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                       text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        code = "desconhecida"
    pack = (ROOT / "library/packs/pp/pack.yaml").read_text(encoding="utf-8")
    pv = next(l.split(":", 1)[1].strip() for l in pack.splitlines()
              if l.startswith("pack_version:"))
    cand = RV["read_candidates"](eng)["data"]
    fcs = F["read_current"](eng)["data"]
    index = {
        "schema_version": "handoff-index/1", "engagement_id": eng.name, "revision": 1,
        "based_on": [
            {"ref": "_design/candidates.json", "revision": cand["revision"],
             "sha256": O["digest"](eng / "_design/candidates.json")},
            {"ref": "_design/functional-contracts.json", "revision": fcs["revision"],
             "sha256": O["digest"](eng / "_design/functional-contracts.json")},
            {"ref": "_blueprint/ux-blueprint_v01.yaml",
             "sha256": O["digest"](eng / "_blueprint/ux-blueprint_v01.yaml")}],
        "scope_refs": ["SCOPE-0001"],
        "exclusions": [
            {"ref": "implementation-spec", "reason": "não renderizada no ensaio F5.5 — texto da "
             "skill de render, sem motor (DESENHO Q9); trabalho e testes por projectar"},
            {"ref": "estimate", "reason": "não renderizada no ensaio F5.5 (DESENHO Q9); só a "
             "ordem de grandeza dos candidatos, por analogia"},
            {"ref": "FC-0002", "reason": "bloqueado: a regra de arredondamento (U-001) não foi "
             "escolhida pelo dono; não autorizável"},
            {"ref": "gestão de stock", "reason": "fora do âmbito (fixture fx-hv1-02)"},
            {"ref": "recepção física", "reason": "fora do âmbito (fixture fx-hv1-02)"}],
        "code_version": code, "pack_version": pv,
        "files": [{"path": r, "sha256": O["digest"](out / r)} for r in rels],
        "authorization_refs": ["decisions.md#D-001", "decisions.md#D-002",
                               "decisions.md#D-003", "decisions.md#D-004"],
        "readiness": {
            "render_final_allowed": gate["final_allowed"],
            "fc": {k: {"authorizable": v["authorizable"],
                       "authorization": v["authorization"]["state"],
                       "gaps": [g["code"] for g in v["gaps"]]}
                   for k, v in show["items"].items()},
            "open_findings": rv["open_findings"],
            "reviews": {r["task_id"]: r["state"] for r in rv["reviews"]}},
        "proofs": {"performed": [],
                   "pending": ["prova: submissão repetida não duplica (FC-0001, exemplo "
                               "negativo)", "prova: a segregação C-004 recusa no servidor"]},
        "receiver_acceptance": None, "delivery_level": "preliminary",
        "label": "preliminary · incompleto — ensaio F5.5, dados sintéticos; não é pronto para "
                 "construção"}
    (out / "handoff-index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1)
                                            + "\n", encoding="utf-8", newline="\n")
    return index


def percurso(tmp):
    eng = analysis(tmp)
    cand = candidates(eng)
    rota = reviews(eng)
    decide_and_design(eng)
    return eng, cand, rota


class Percurso(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.eng, cls.cand, cls.rota = percurso(cls.tmp.name)
        cls.out = Path(cls.tmp.name) / "pacote"
        cls.index = package(cls.eng, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_t27_candidates_stay_inside_the_imposed_platform(self):
        dados = RV["read_candidates"](self.eng)["data"]
        self.assertEqual({c["platform"] for c in dados["items"]}, {PLATAFORMA})
        self.assertEqual(self.cand["gaps"], [])

    def test_t28_the_router_names_why_each_role_was_or_was_not_called(self):
        sel = {s["role"] for s in self.rota["selected"]}
        self.assertEqual(sel, {"architecture-review", "security-operation", "ux-process"})
        self.assertEqual({n["role"] for n in self.rota["not_called"]},
                         {"data-integration", "cost-estimate"})

    def test_reviews_are_current_and_every_finding_is_disposed(self):
        s = RV["show_reviews"](self.eng)
        self.assertEqual({r["state"] for r in s["reviews"]}, {"current"})
        self.assertEqual(s["open_findings"], ["REV-0001.F01"], "o adiado fica visível")

    def test_the_design_carries_one_authorised_contract_and_one_blocked(self):
        v = F["show"](self.eng)["items"]
        self.assertEqual(v["FC-0001"]["authorization"]["state"], "current")
        self.assertFalse(v["FC-0002"]["authorizable"])
        g = json.loads((self.out / "render-gate.json").read_text(encoding="utf-8"))
        self.assertFalse(g["final_allowed"])
        self.assertEqual({x["fc"] for x in g["gaps"]}, {"FC-0002"})

    def test_the_index_is_valid_preliminary_and_names_what_is_missing(self):
        errors, _u = W["validate"](self.index, W["load_schema"]("handoff-index"))
        self.assertEqual(errors, [])
        self.assertEqual(self.index["delivery_level"], "preliminary")
        self.assertIsNone(self.index["receiver_acceptance"])
        refs = {e["ref"] for e in self.index["exclusions"]}
        self.assertTrue({"implementation-spec", "estimate", "FC-0002"} <= refs)
        self.assertEqual(self.index["proofs"]["performed"], [])

    def test_every_file_in_the_index_matches_its_hash(self):
        for f in self.index["files"]:
            self.assertEqual(O["digest"](self.out / f["path"]), f["sha256"], f["path"])
        listed = {f["path"] for f in self.index["files"]}
        on_disk = {p.relative_to(self.out).as_posix() for p in self.out.rglob("*")
                   if p.is_file() and p.name != "handoff-index.json"}
        self.assertEqual(listed, on_disk, "ficheiro no pacote fora do índice, ou o inverso")

    def test_citing_a_candidate_needs_its_authority_or_its_projection(self):
        novo = {"decisions.md": "## D-009 — escolhida O-001\n"}
        base = {"files": {"decisions.md": ""}}
        self.assertEqual(R["read_set_gaps"](self.eng, dict(base, reads={}), novo),
                         {"options.md": ["O-001"]})
        for lido in ("_design/candidates.json", "options.md"):
            self.assertEqual(R["read_set_gaps"](self.eng, dict(base, reads={lido: ""}), novo),
                             {}, lido)

    def test_the_package_carries_no_operational_state(self):
        for f in self.index["files"]:
            self.assertFalse(f["path"].startswith(("_ops/", "_graph/", "_drafts/")), f["path"])


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--write":
        with tempfile.TemporaryDirectory() as t:
            e, _c, _r = percurso(t)
            idx = package(e, sys.argv[2])
            print(json.dumps({"files": len(idx["files"]), "code_version": idx["code_version"],
                              "delivery_level": idx["delivery_level"]}, ensure_ascii=False))
    else:
        unittest.main()
