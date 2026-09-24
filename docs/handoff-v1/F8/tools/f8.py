#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F8 — ferramentas das execuções-piloto do handoff-v1. Só biblioteca padrão.

Desenho: `docs/handoff-v1/F8/DESENHO.md`. Não fazem parte do runtime do aisa: servem a
orquestração e a medição dos pilotos. Nunca escrevem num engagement. Escrevem só em
`docs/handoff-v1/F8/execucoes/` (run-log e snapshots) e, no `restore`, numa pasta de
engagement que ainda não exista.

    runlog add        acrescenta um evento ao run-log de uma execução (JSONL, append-only)
    snapshot save     copia o engagement inteiro para um snapshot imutável, com manifesto
    snapshot verify   confere um snapshot contra o seu manifesto
    snapshot restore  repõe um snapshot numa pasta de engagement que não exista
    truth             congela o que o engagement diz agora (fronteira de segmento)
    check-resume      compara a declaração de retoma do executor com a verdade congelada
    canary            procura no engagement texto que só existe no `expected`
    verify-eval       confere a tabela do avaliador: todos os E-items, veredictos, locators
    summary           agrega as execuções contra os critérios de 06; nunca emite GO

O que isto não faz: julgar qualidade. `check-resume` e `verify-eval` emitem achados; o
veredicto de qualidade é do avaliador e do mantenedor (DESENHO Q4). `summary` sem execuções
diz `SEM EXECUÇÃO`, nunca verde.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import runpy
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
F8 = ROOT / "docs" / "handoff-v1" / "F8"
EXEC = F8 / "execucoes"
FIXTURES = ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1"
TOOLS = ROOT / "library" / "kernel" / "tools"

CRITICO = "critical"
AVISO = "warning"

EVENTOS = {"segment_start", "segment_end", "relay_request", "relay_response", "pause",
           "interruption", "change_injected", "resume_report", "resume_check", "truth",
           "release", "recipient", "correction", "evaluation", "usage", "note"}
PAPEIS = {"executor", "cliente", "revisor", "destinatario", "avaliador", "sonda"}
VEREDICTOS = {"cumprido", "violado", "ausente", "nao_aplicavel"}
CLASSES_LACUNA = ("blocks_all", "blocks_scope", "delegated_choice", "implementation_proof")
ABERTOS = ("Unknown", "Conflicted", "Risky")

# O corpus que o executor lê legitimamente. Uma frase do `expected` que também exista aqui
# não serve de canário: aparecer no engagement não prova que o executor leu o `expected`.
CORPUS_RUNTIME = ("library", ".claude/skills", ".claude/agents", ".claude/commands",
                  ".claude/rules", "CLAUDE.md")
TEXTO = {".md", ".json", ".yaml", ".yml", ".txt", ".csv", ".jsonl"}
# O que no engagement é cópia das fontes: fica fora da procura do canário.
FORA_DO_CANARIO = ("inputs", "_capture")

_CACHE: dict = {}


class F8Error(Exception):
    def __init__(self, code: str, detail: str):
        super().__init__("{}: {}".format(code, detail))
        self.code = code
        self.detail = detail


def _mod(nome: str) -> dict:
    if nome not in _CACHE:
        _CACHE[nome] = runpy.run_path(str(TOOLS / (nome + ".py")))
    return _CACHE[nome]


def _eng(ref, engagements: Path | None = None) -> Path:
    p = Path(ref)
    if p.is_dir():
        return p
    return (engagements or ROOT / "projects") / str(ref)


def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _achado(code, sev, detail, **extra) -> dict:
    return dict({"code": code, "severity": sev, "detail": detail}, **extra)


# ------------------------------------------------------------------------- run-log

def _run_dir(exec_dir: Path, run: str) -> Path:
    if not re.fullmatch(r"R\d+", run or ""):
        raise F8Error("BAD_RUN", "id de execução `{}` — esperado `R<n>`".format(run))
    return Path(exec_dir) / run


def runlog_read(exec_dir: Path, run: str) -> list:
    """Os eventos, por ordem. Uma linha ilegível é erro, nunca se salta em silêncio."""
    p = _run_dir(exec_dir, run) / "run-log.jsonl"
    if not p.is_file():
        return []
    fora = []
    for n, linha in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if not linha.strip():
            continue
        try:
            fora.append(json.loads(linha))
        except ValueError as exc:
            raise F8Error("RUNLOG_UNREADABLE", "{} linha {}: {}".format(p, n, exc))
    return fora


def runlog_add(exec_dir: Path, run: str, tipo: str, data: dict, segment: str | None = None,
               ts: str | None = None) -> dict:
    if tipo not in EVENTOS:
        raise F8Error("BAD_EVENT", "tipo `{}` fora de {}".format(tipo, sorted(EVENTOS)))
    if not isinstance(data, dict):
        raise F8Error("BAD_EVENT", "`data` tem de ser um objecto JSON")
    if tipo == "usage" and data.get("role") not in PAPEIS:
        raise F8Error("BAD_EVENT", "usage sem papel conhecido ({})".format(sorted(PAPEIS)))
    anteriores = runlog_read(exec_dir, run)
    ev = {"seq": len(anteriores) + 1, "ts": ts or _agora(), "run": run, "segment": segment,
          "type": tipo, "data": data}
    d = _run_dir(exec_dir, run)
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "run-log.jsonl", "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return ev


# ------------------------------------------------------------------------ snapshots

def _ficheiros(base: Path) -> dict:
    fora = {}
    for p in sorted(base.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            fora[p.relative_to(base).as_posix()] = _sha(p)
    return fora


def snapshot_save(eng: Path, exec_dir: Path, run: str, label: str) -> dict:
    eng = Path(eng)
    if not eng.is_dir():
        raise F8Error("NO_ENGAGEMENT", "{} não existe".format(eng))
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", label or ""):
        raise F8Error("BAD_LABEL", "etiqueta `{}`".format(label))
    dest = _run_dir(exec_dir, run) / "snapshots" / label
    if dest.exists():
        raise F8Error("SNAPSHOT_EXISTS", "{} já existe — um snapshot é imutável".format(dest))
    shutil.copytree(eng, dest / "engagement",
                    ignore=shutil.ignore_patterns("__pycache__"))
    manifesto = {"schema": "f8-snapshot/1", "run": run, "label": label,
                 "engagement": eng.name, "saved_at": _agora(),
                 "files": _ficheiros(dest / "engagement")}
    (dest / "manifest.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1)
                                        + "\n", encoding="utf-8", newline="\n")
    return {"snapshot": str(dest), "files": len(manifesto["files"])}


def snapshot_verify(exec_dir: Path, run: str, label: str) -> list:
    dest = _run_dir(exec_dir, run) / "snapshots" / label
    try:
        manifesto = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [_achado("MANIFEST_UNREADABLE", CRITICO, str(exc))]
    agora = _ficheiros(dest / "engagement") if (dest / "engagement").is_dir() else {}
    fora = []
    for rel, sha in manifesto.get("files", {}).items():
        if rel not in agora:
            fora.append(_achado("MISSING", CRITICO, rel))
        elif agora[rel] != sha:
            fora.append(_achado("CHANGED", CRITICO, rel))
    for rel in sorted(set(agora) - set(manifesto.get("files", {}))):
        fora.append(_achado("EXTRA", CRITICO, rel))
    return fora


def snapshot_restore(exec_dir: Path, run: str, label: str, target: Path) -> dict:
    target = Path(target)
    if target.exists():
        raise F8Error("RESTORE_TARGET_EXISTS", "{} já existe — nunca se repõe por cima de um "
                                               "engagement".format(target))
    problemas = snapshot_verify(exec_dir, run, label)
    if problemas:
        raise F8Error("SNAPSHOT_INVALID", "; ".join(p["code"] + " " + p["detail"]
                                                    for p in problemas))
    shutil.copytree(_run_dir(exec_dir, run) / "snapshots" / label / "engagement", target)
    return {"restored": str(target)}


# ---------------------------------------------------------------------------- verdade

def _material(r: dict) -> bool:
    if r.get("state") not in ABERTOS or r.get("resolved") or r.get("retired") \
            or r.get("parked"):
        return False
    if r.get("state") == "Risky":
        return True          # a tabela Risky não tem criticidade: um risco aberto conta
    return (r.get("criticidade") in ("Critical", "High")
            or r.get("bloqueio") in ("blocks_all", "blocks_scope"))


def truth(eng: Path) -> dict:
    """O que os ficheiros do engagement dizem AGORA, para comparar mais tarde.

    Só lê. A SU é a autoridade: copiam-se ids, estados e colunas de bloqueio, sem os
    interpretar. A retoma do kernel (`workflow.resume`) entra tal como sai."""
    eng = Path(eng)
    W, B, D = _mod("workflow"), _mod("bootstrap"), _mod("dashboard")
    try:
        estado = json.loads((eng / "_state.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        estado = {}
    boot = B["bootstrap"](eng)
    linhas = []
    if boot.get("ready"):
        modelo = D["build_model"](eng, date.today())
        for r in (modelo.get("su") or {}).get("rows") or []:
            linhas.append({"id": r.get("id"), "state": r.get("state"),
                           "criticidade": r.get("criticidade") or "",
                           "bloqueio": r.get("bloqueio") or "", "tipo": r.get("tipo") or "",
                           "parked": bool(r.get("parked")),
                           "resolved": str(r.get("resolved")) == "True"
                           or r.get("resolved") is True,
                           "retired": str(r.get("retired")) == "True"
                           or r.get("retired") is True})
    retoma = W["resume"](eng)
    return {
        "engagement": eng.name,
        "captured_at": _agora(),
        "phase": estado.get("phase", ""),
        "route": (estado.get("workflow") or {}).get("route", ""),
        "ready": bool(boot.get("ready")),
        "limitations": [l.get("code") for l in boot.get("limitations", [])],
        "rows": linhas,
        "all_ids": sorted({r["id"] for r in linhas if r["id"]}),
        "open_ids": sorted(r["id"] for r in linhas if r["state"] in ABERTOS
                           and not r["resolved"] and not r["retired"]),
        "material_open": sorted(r["id"] for r in linhas if _material(r)),
        "decisions": sorted(d["id"] for d in W["_decision_titles"](eng)),
        "resume": {k: retoma.get(k) for k in ("ok", "code", "next_action", "tasks",
                                              "results_pending", "reconcile_proposal")},
    }


CAMPOS_RETOMA = ("engagement", "phase", "route", "decisions", "open_questions", "next_step")


def _comandos(texto) -> set:
    return set(re.findall(r"(?<![\w/])/[a-z][a-z-]+", str(texto or "")))


def check_resume(t: dict, report: dict) -> dict:
    """A declaração do executor depois de `/resume` contra a verdade congelada antes.

    Críticos: perder uma decisão ou uma pergunta material, inventar uma, trocar fase, rota
    ou engagement, ignorar uma recuperação pendente. O resto avisa."""
    achados = []
    falta = [c for c in CAMPOS_RETOMA if c not in report]
    if falta:
        achados.append(_achado("REPORT_INCOMPLETE", CRITICO, "faltam {}".format(falta)))
    if report.get("engagement") not in (None, t["engagement"]):
        achados.append(_achado("WRONG_ENGAGEMENT", CRITICO, "{} ≠ {}".format(
            report.get("engagement"), t["engagement"])))
    for campo, code in (("phase", "PHASE_MISMATCH"), ("route", "ROUTE_MISMATCH")):
        if campo in report and report[campo] != t[campo]:
            achados.append(_achado(code, CRITICO, "{} ≠ {}".format(report[campo], t[campo])))
    dec = set(report.get("decisions") or [])
    for i in sorted(set(t["decisions"]) - dec):
        achados.append(_achado("LOST_DECISION", CRITICO, i))
    for i in sorted(dec - set(t["decisions"])):
        achados.append(_achado("INVENTED_DECISION", CRITICO, i))
    perg = set(report.get("open_questions") or [])
    for i in sorted(set(t["material_open"]) - perg):
        achados.append(_achado("LOST_QUESTION", CRITICO, i))
    for i in sorted(perg - set(t["open_ids"])):
        if i in t["all_ids"]:
            achados.append(_achado("STALE_QUESTION", AVISO, "{} já não está aberta".format(i)))
        else:
            achados.append(_achado("INVENTED_QUESTION", CRITICO, i))
    if (t.get("resume") or {}).get("code") == "RECOVERY_REQUIRED" \
            and report.get("recovery_required") is not True:
        achados.append(_achado("RECOVERY_IGNORED", CRITICO,
                               "o kernel pede recuperação e a declaração não a nomeia"))
    esperado = _comandos(((t.get("resume") or {}).get("next_action") or {}).get("action"))
    if esperado and not (esperado & _comandos(report.get("next_step"))):
        achados.append(_achado("NEXT_STEP_DIFFERS", AVISO, "kernel: {} · declarado: {}".format(
            sorted(esperado), report.get("next_step"))))
    return {"engagement": t["engagement"], "findings": achados,
            "verdict": "fail" if any(a["severity"] == CRITICO for a in achados) else "pass"}


# ---------------------------------------------------------------------------- canário

def _palavras(texto: str) -> list:
    return re.findall(r"\w+", texto.lower())


def _grams(texto: str, n: int) -> set:
    w = _palavras(texto)
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def _textos(base: Path, fora=()):
    base = Path(base)
    if base.is_file():
        yield base, base.read_text(encoding="utf-8", errors="replace")
        return
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in TEXTO or "__pycache__" in p.parts:
            continue
        if fora and p.relative_to(base).parts[0] in fora:
            continue
        yield p, p.read_text(encoding="utf-8", errors="replace")


def _retira_presentes(alvos: set, base: Path, n: int, fora=()) -> None:
    for _, texto in _textos(base, fora):
        if not alvos:
            return
        w = _palavras(texto)
        for i in range(len(w) - n + 1):
            alvos.discard(tuple(w[i:i + n]))


def expected_texts(scenario: dict) -> list:
    """O texto que só o `expected` tem: afirmações, `must_not`, fechos e variantes."""
    fora = []
    for e in scenario.get("expected", []):
        fora.append(e.get("statement", ""))
        fora.extend(e.get("must_not", []))
        fecho = (e.get("classification") or {}).get("closure")
        if fecho:
            fora.append(fecho)
    for v in scenario.get("variants", []):
        fora.extend([v.get("change", ""), v.get("expected", "")])
    return [t for t in fora if t]


def canary(eng: Path, expected: list, allowed: list, n: int = 6) -> dict:
    """Frases de `n` palavras que só existem no `expected` e aparecem no engagement.

    `allowed` são ficheiros ou pastas que o executor lê legitimamente (fontes, ficha do
    cliente, fontes de mudança); o corpus do runtime entra sempre. Um acerto não prova
    batota — prova que é preciso olhar."""
    alvos = set()
    for t in expected:
        alvos |= _grams(t, n)
    for base in list(allowed) + [ROOT / c for c in CORPUS_RUNTIME]:
        if Path(base).exists():
            _retira_presentes(alvos, Path(base), n)
    acertos = []
    for p, texto in _textos(eng, FORA_DO_CANARIO):
        w = _palavras(texto)
        vistos = set()
        for i in range(len(w) - n + 1):
            g = tuple(w[i:i + n])
            if g in alvos and g not in vistos:
                vistos.add(g)
                acertos.append({"file": p.relative_to(eng).as_posix(), "gram": " ".join(g)})
    return {"engagement": Path(eng).name, "n": n, "distinctive_grams": len(alvos),
            "hits": acertos, "verdict": "contaminated" if acertos else "clean"}


# ---------------------------------------------------------------------- avaliação

def _locator(base: Path, loc: str) -> str | None:
    """None se resolve; senão a razão."""
    m = re.fullmatch(r"(?P<path>[^#:]+?)(?::(?P<line>\d+)|#(?P<tok>.+))?", loc.strip())
    if not m:
        return "forma inválida"
    p = base / m.group("path")
    if not p.is_file():
        return "ficheiro inexistente"
    texto = p.read_text(encoding="utf-8", errors="replace")
    if m.group("line"):
        if not 1 <= int(m.group("line")) <= len(texto.splitlines()):
            return "linha fora do ficheiro"
    elif m.group("tok"):
        if not re.search(r"(?<![\w-])" + re.escape(m.group("tok")) + r"(?![\w-])", texto):
            return "âncora ausente no ficheiro"
    return None


def verify_eval(base: Path, evaluation: dict, expected_ids: list) -> dict:
    """A tabela do avaliador contra o engagement avaliado: todos os E-items, veredicto
    válido e cada locator a resolver. Não julga o veredicto — confere a evidência."""
    base = Path(base)
    itens = {i.get("id"): i for i in evaluation.get("items", [])}
    achados = []
    for e in expected_ids:
        if e not in itens:
            achados.append(_achado("MISSING_ITEM", CRITICO, e))
    for iid, item in itens.items():
        if iid not in expected_ids:
            achados.append(_achado("UNKNOWN_ITEM", AVISO, str(iid)))
        if item.get("verdict") not in VEREDICTOS:
            achados.append(_achado("BAD_VERDICT", CRITICO, "{}: {}".format(
                iid, item.get("verdict"))))
        bons = 0
        for loc in item.get("locators") or []:
            razao = _locator(base, str(loc))
            if razao:
                achados.append(_achado("LOCATOR_UNRESOLVED", CRITICO, "{}: {} ({})".format(
                    iid, loc, razao)))
            else:
                bons += 1
        if item.get("verdict") in ("cumprido", "violado") and not bons:
            achados.append(_achado("NO_EVIDENCE", CRITICO, str(iid)))
        if not str(item.get("rationale") or "").strip():
            achados.append(_achado("EMPTY_RATIONALE", AVISO, str(iid)))
    contagem = {v: sum(1 for i in itens.values() if i.get("verdict") == v)
                for v in sorted(VEREDICTOS)}
    return {"findings": achados, "counts": contagem,
            "verdict": "fail" if any(a["severity"] == CRITICO for a in achados) else "pass"}


# ------------------------------------------------------------------------- agregado

def _run_summary(eventos: list) -> dict:
    uso: dict = {}
    for ev in eventos:
        if ev["type"] != "usage":
            continue
        d = ev["data"]
        u = uso.setdefault(d["role"], {"calls": 0, "tokens": 0, "tool_uses": 0,
                                       "duration_ms": 0})
        u["calls"] += 1
        for k in ("tokens", "tool_uses", "duration_ms"):
            u[k] += int(d.get(k) or 0)
    retomas = [ev["data"].get("verdict") for ev in eventos if ev["type"] == "resume_check"]
    leituras = [ev["data"] for ev in eventos if ev["type"] == "recipient"]
    avaliacoes = [ev["data"] for ev in eventos if ev["type"] == "evaluation"]
    return {
        "segments_done": sum(1 for ev in eventos if ev["type"] == "segment_end"),
        "relay": {k: sum(1 for ev in eventos if ev["type"] == "relay_request"
                         and ev["data"].get("kind") == k) for k in ("pergunta", "subagente")},
        "interruptions": sum(1 for ev in eventos if ev["type"] == "interruption"),
        "change_injected": any(ev["type"] == "change_injected" for ev in eventos),
        "usage": uso,
        "resume_checks": {"total": len(retomas),
                          "pass": sum(1 for v in retomas if v == "pass")},
        "recipient_readings": len(leituras),
        "essential_unanswered_final": (leituras[-1].get("essential_unanswered")
                                       if leituras else None),
        "evaluation": (avaliacoes[-1].get("counts") if avaliacoes else None),
    }


def summary(exec_dir: Path) -> dict:
    exec_dir = Path(exec_dir)
    runs = sorted(d.name for d in exec_dir.iterdir()
                  if d.is_dir() and (d / "run-log.jsonl").is_file()) \
        if exec_dir.is_dir() else []
    if not runs:
        return {"verdict": "SEM EXECUÇÃO", "runs": {}, "criteria": {}}
    por = {r: _run_summary(runlog_read(exec_dir, r)) for r in runs}
    total_ret = sum(s["resume_checks"]["total"] for s in por.values())
    ok_ret = sum(s["resume_checks"]["pass"] for s in por.values())
    finais = [s["essential_unanswered_final"] for s in por.values()]
    aval = [s["evaluation"] for s in por.values() if s["evaluation"]]
    criteria = {
        "resumes_preserved": {"pass": ok_ret, "total": total_ret,
                              "met": total_ret > 0 and ok_ret == total_ret},
        "recipient_essential_unanswered": {
            "values": finais,
            "met": bool(finais) and all(v == 0 for v in finais if v is not None)
            and None not in finais},
        "must_not_violations": {"total": sum(a.get("violado", 0) for a in aval),
                                "met": bool(aval) and all(a.get("violado", 0) == 0
                                                          for a in aval)},
        "material_items_absent": {"total": sum(a.get("ausente", 0) for a in aval),
                                  "met": bool(aval) and all(a.get("ausente", 0) == 0
                                                            for a in aval)},
    }
    return {"verdict": "EXPLORATÓRIO — {} execução(ões); o gate é do mantenedor".format(
        len(runs)), "runs": por, "criteria": criteria}


# ------------------------------------------------------------------------------ CLI

def _json_arg(texto: str | None, ficheiro: str | None) -> dict:
    if ficheiro:
        return json.loads(Path(ficheiro).read_text(encoding="utf-8"))
    return json.loads(texto or "{}")


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            pass
    ap = argparse.ArgumentParser(description="ferramentas dos pilotos F8 (só leitura dos "
                                             "engagements)")
    ap.add_argument("--exec-dir", default=str(EXEC))
    sub = ap.add_subparsers(dest="cmd", required=True)

    rl = sub.add_parser("runlog")
    rl.add_argument("action", choices=["add", "show"])
    rl.add_argument("--run", required=True)
    rl.add_argument("--type")
    rl.add_argument("--segment")
    rl.add_argument("--data")
    rl.add_argument("--data-file")

    sn = sub.add_parser("snapshot")
    sn.add_argument("action", choices=["save", "verify", "restore"])
    sn.add_argument("--run", required=True)
    sn.add_argument("--label", required=True)
    sn.add_argument("--engagement")

    tr = sub.add_parser("truth")
    tr.add_argument("--engagement", required=True)
    tr.add_argument("--out")

    cr = sub.add_parser("check-resume")
    cr.add_argument("--truth", required=True)
    cr.add_argument("--report", required=True)

    ca = sub.add_parser("canary")
    ca.add_argument("--engagement", required=True)
    ca.add_argument("--fixture", required=True, help="id da pasta em fixtures/handoff-v1/")
    ca.add_argument("--expected-extra", action="append", default=[],
                    help="JSON com uma lista `expected` (p.ex. a da mudança)")
    ca.add_argument("--allowed", action="append", default=[],
                    help="ficheiro ou pasta que o executor lê legitimamente")
    ca.add_argument("-n", type=int, default=6)

    ve = sub.add_parser("verify-eval")
    ve.add_argument("--engagement", required=True, help="pasta avaliada (ou snapshot)")
    ve.add_argument("--eval", required=True)
    ve.add_argument("--fixture", required=True)
    ve.add_argument("--expected-extra", action="append", default=[])

    sub.add_parser("summary")

    a = ap.parse_args(argv)
    exec_dir = Path(a.exec_dir)
    try:
        if a.cmd == "runlog":
            if a.action == "add":
                out = runlog_add(exec_dir, a.run, a.type, _json_arg(a.data, a.data_file),
                                 a.segment)
            else:
                out = runlog_read(exec_dir, a.run)
        elif a.cmd == "snapshot":
            if a.action == "save":
                out = snapshot_save(_eng(a.engagement), exec_dir, a.run, a.label)
            elif a.action == "verify":
                achados = snapshot_verify(exec_dir, a.run, a.label)
                out = {"findings": achados, "verdict": "fail" if achados else "pass"}
            else:
                out = snapshot_restore(exec_dir, a.run, a.label, _eng(a.engagement))
        elif a.cmd == "truth":
            out = truth(_eng(a.engagement))
            if a.out:
                Path(a.out).parent.mkdir(parents=True, exist_ok=True)
                Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8", newline="\n")
        elif a.cmd == "check-resume":
            out = check_resume(_json_arg(None, a.truth), _json_arg(None, a.report))
        elif a.cmd in ("canary", "verify-eval"):
            cen = json.loads((FIXTURES / a.fixture / "scenario.json").read_text(
                encoding="utf-8"))
            extra = [json.loads(Path(f).read_text(encoding="utf-8")) for f in a.expected_extra]
            if a.cmd == "canary":
                textos = expected_texts(cen)
                for x in extra:
                    textos += expected_texts(x)
                out = canary(_eng(a.engagement), textos,
                             [FIXTURES / a.fixture / "sources"] + [Path(p) for p in a.allowed],
                             a.n)
            else:
                ids = [e["id"] for e in cen["expected"]]
                for x in extra:
                    ids += [e["id"] for e in x.get("expected", [])]
                out = verify_eval(_eng(a.engagement), _json_arg(None, a.eval), ids)
        else:
            out = summary(exec_dir)
    except F8Error as exc:
        print(json.dumps({"ok": False, "code": exc.code, "detail": exc.detail},
                         ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if isinstance(out, dict) and out.get("verdict") in ("fail", "contaminated"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
