"""M4 — demonstração: retoma fria (PLANO.md, M4 → Demonstração).

    python docs/process-map/M4/demo.py

1. Prepara um engagement temporário (a fixture de `test_process_map_core.py`): mapa
   publicado e validado pelo dono (dados de teste).
2. «Fecha a sessão»: a retoma corre num PROCESSO NOVO — `workflow.py resume --json` —, sem
   nada desta execução em memória; tudo o que diz sai dos ficheiros.
3. Altera uma fonte (uma nota editorial no modelo do processo) e retoma outra vez: o
   estado aparece por revalidar, com o que mudou e o que fazer.
4. Revalida (registo explícito) e retoma: actual, e a validação do dono transportada.
Escreve `demo-output.txt` ao lado.
"""
import json
import os
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORE = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_process_map_core.py"), run_name="demo")
P = CORE["P"]
WF = ROOT / "library" / "kernel" / "tools" / "workflow.py"
lines = []


def say(msg=""):
    lines.append(msg)


def cold_resume(eng: Path) -> dict:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-B", str(WF), "resume", "--engagement", str(eng),
                        "--json"], capture_output=True, text=True, encoding="utf-8", env=env)
    return json.loads(r.stdout)


def tell(r: dict):
    pm = r["process_map"]
    val = pm["validation"]
    say("   processo: {} passos — {}".format(len(pm["blocks"]), " → ".join(
        "{}. {} ({})".format(b["n"], b["label"], b["lane"]) for b in pm["blocks"])))
    say("   mapa {} · validação {}{} · fontes {}".format(
        pm["version"], val["status"], " ({})".format(val["decision"]) if val["decision"] else "",
        pm["freshness"]["state"]))
    for b in pm["blockers"]:
        say("   bloqueio [{}] {}".format(b["kind"], b["detail"]))
    say("   a seguir: {} — {}".format(r["next_action"]["action"], r["next_action"]["reason"]))


with tempfile.TemporaryDirectory() as t:
    base = Path(t)
    eng = CORE["engagement"](base)
    d, _ = P["stamp"](eng, CORE["draft_v1"]())
    p = base / "d.json"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    P["publish"](eng, d, p)
    dec = eng / "decisions.md"
    dec.write_text(dec.read_text(encoding="utf-8") + P["approval_block"](
        eng, "processo diário de preço", "MAPG-001 por esclarecer",
        "owner (Responsável de Pricing — dados de teste)", "2026-09-25T10:00:00Z"),
        encoding="utf-8")
    say("preparado: mapa mp-v01 publicado e validado (dono de teste); sessão fechada.")

    say("1. retoma fria num processo novo:")
    tell(cold_resume(eng))

    pm = eng / "_capture" / "process-model.md"
    pm.write_text(pm.read_text(encoding="utf-8") + "\nnota da reunião de hoje\n",
                  encoding="utf-8")
    say("2. uma fonte mudou entre sessões (nota editorial no modelo do processo); retoma:")
    tell(cold_resume(eng))

    r = P["revalidate"](eng, ["_capture/process-model.md"],
                        "nota no fim do ficheiro; nenhuma regra citada mudou", "analista")
    p.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    pub = P["publish"](eng, r, p)
    say("3. revalidação registada → {}; retoma:".format(pub["version"]))
    tell(cold_resume(eng))

out = "\n".join(lines) + "\n"
Path(__file__).with_name("demo-output.txt").write_text(out, encoding="utf-8")
sys.stdout.write(out)
