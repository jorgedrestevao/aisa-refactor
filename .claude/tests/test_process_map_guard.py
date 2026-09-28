"""process-map M1 — `_map/` é estado coordenado (MAP-25).

O mapa de conhecimento do processo (`_map/map.json` + `_map/history/mp-vNN.json`) só é
escrito por `process_map.py`, pelo coordenador. Uma escrita por ferramenta (Write/Edit)
nestes caminhos é edição à mão de estado coordenado e é recusada sempre, com o engagement
reconstruído ou não. A vista `process-map.html` à raiz é derivada e fica fora da guarda.

Limite documentado (HOOKS.md): o hook vê Write/Edit; uma escrita por Bash não passa por ele.
Contra essa via valem as regras do repositório, não este teste.

    python .claude/tests/test_process_map_guard.py
"""
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
L = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_handoff_legacy.py"), run_name="helpers")
B = L["B"]


def edit(path):
    return {"tool_name": "Edit", "tool_input": {"file_path": str(path), "old_string": "a",
                                                "new_string": "b"}}


class MAP25_MapaCoordenado(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.eng = L["novo"](self.base)

    def test_write_and_edit_into_the_map_are_refused_even_when_ready(self):
        self.assertTrue(B["bootstrap"](self.eng)["ready"])
        for rel in ("_map/map.json", "_map/history/mp-v01.json"):
            for payload in (L["write"](self.eng / rel, "{}"), edit(self.eng / rel)):
                p = L["hook"]("pre-authority-guard.py", payload, self.base)
                self.assertTrue(L["negou"](p), "{} {} passou".format(payload["tool_name"], rel))

    def test_the_derived_view_is_not_guarded(self):
        p = L["hook"]("pre-authority-guard.py",
                      L["write"](self.eng / "process-map.html", "<html></html>"), self.base)
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_a_similarly_named_folder_is_not_the_map(self):
        p = L["hook"]("pre-authority-guard.py",
                      L["write"](self.eng / "_mapas" / "nota.md", "x"), self.base)
        self.assertEqual(p.returncode, 0, p.stderr)


if __name__ == "__main__":
    unittest.main()
