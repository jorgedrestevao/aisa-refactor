"""M1 — demonstração pedida no plano (PLANO.md, M1 → Demonstração).

    python docs/process-map/M1/demo.py

Sobre um engagement temporário (a fixture de `.claude/tests/test_process_map_core.py`):
  1. publicar um mapa;
  2. alterar uma fonte e mostrar a recusa do rascunho antigo;
  3. repetir a operação original sem criar nova versão;
  4. mostrar que dois CALC-001 de ficheiros diferentes resolvem cada um para o seu bloco.
Não toca em nenhum engagement real. Escreve `demo-output.txt` ao lado.
"""
import json
import runpy
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
T = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_process_map_core.py"), run_name="demo")
P = T["P"]
lines = ["motor: {}".format(Path(T["MOTOR"]).relative_to(ROOT))]


def say(msg):
    lines.append(msg)


with tempfile.TemporaryDirectory() as t:
    base = Path(t)
    eng = T["engagement"](base)
    outside = base / "drafts"
    outside.mkdir()
    draft, filled = P["stamp"](eng, T["draft_v1"]())
    path = outside / "draft.json"
    path.write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
    say("rascunho carimbado: {} campos preenchidos (base, digests, fontes consumidas)"
        .format(len(filled)))

    v = P["check"](eng, draft)
    say("1. check: válido={} · unidades {} · sem destino {} · lacunas {}".format(
        v["valid"], v["transfer"]["units"], len(v["transfer"]["missing"]), len(v["gaps"])))
    r = P["publish"](eng, draft, path)
    say("   publish: publicado={} versão={} operação={}".format(
        r["published"], r["version"], r["operation_id"]))
    say("   ficheiros: {}".format(sorted(p.relative_to(eng).as_posix()
                                         for p in (eng / "_map").rglob("*.json"))))

    stale, _ = P["stamp"](eng, dict(T["draft_v1"](), base=P["load"](eng)["digest"]))
    stale["nodes"][1]["label"] = "Calcula o preço (revisto)"
    pm = eng / "_capture" / "process-model.md"
    pm.write_text(pm.read_text(encoding="utf-8") + "\nregra nova vinda da reunião\n",
                  encoding="utf-8")
    r2 = P["publish"](eng, stale, path)
    codes = sorted({e["code"] for e in r2["verdict"]["errors"]})
    say("2. fonte alterada depois do rascunho: publicado={} · {} · {}".format(
        r2["published"], r2["code"], ", ".join(codes)))
    say("   mapa publicado continua {}".format(P["load"](eng)["map"]["version"]))

    r3 = P["publish"](eng, draft, path)
    say("3. repetir a operação original: publicado={} repetição={} versão={} · histórico {}"
        .format(r3["published"], r3["replayed"], r3["version"],
                sorted(p.name for p in (eng / "_map" / "history").iterdir())))

    a = P["resolve_ref"](eng, "_capture/precos.xlsx.calc-chain.json#CALC-001")
    b = P["resolve_ref"](eng, "_capture/precos-2024.xlsx.calc-chain.json#CALC-001")
    c = P["resolve_ref"](eng, "_capture/process-model.md#CALC-001")
    say("4. CALC-001 em dois workbooks: {} → {}… · {} → {}…".format(
        a["unit"], a["digest"][:12], b["unit"], b["digest"][:12]))
    say("   sem qualificar pelo ficheiro: {} — {}".format(c["status"], c["detail"]))

out = "\n".join(lines) + "\n"
(Path(__file__).with_name("demo-output.txt")).write_text(out, encoding="utf-8")
sys.stdout.write(out)
