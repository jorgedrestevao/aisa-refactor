# -*- coding: utf-8 -*-
"""Perfil de workflow `handoff-v1` — identificacao, capacidades do pack e respostas (F1).

    python library/kernel/tools/workflow.py check --engagement <slug> [--json]
    python library/kernel/tools/workflow.py check --pack <id> --profile handoff-v1 --route <rota> [--json]

Stdlib apenas (ADR-001). Nao escreve nada.

O QUE E
    O ponto unico onde se responde a tres perguntas antes de escrever num engagement:
    que perfil tem, se o pack o suporta, e se o bloco `workflow` de `_state.json` e valido.
    Hooks, skills e o coordenador perguntam aqui, e so aqui (desenho F1, I-06).

O QUE NAO E
    Nao e um motor novo de estado: nao publica, nao reconstroi, nao decide conteudo. A
    publicacao continua em `operation.py`, a reconstrucao em `bootstrap.py`, o espelho em
    `graph.py`/`resolve.py` e a frescura semantica em `coverage.py`.

LEGADO NAO E `LEGACY_MODE`
    Um engagement sem bloco `workflow` e legado do plano handoff-v1: foi criado pela versao
    historica (`jorgedrestevao/aisa@85baf10`) e nesta versao so se le (decisao classic A).
    `LEGACY_MODE`, no bootstrap, quer dizer outra coisa — engagement sem `_graph/` — e nao
    se reutiliza.

CAMPOS DESCONHECIDOS
    O validador de schema reporta campos que o schema nao declara e nunca os apaga. Quem le
    um bloco com campos a mais preserva-os; quem os deita fora esta a perder dados.
"""
from __future__ import annotations

import json
import re
import runpy
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
# O leitor de YAML do kernel vive no dashboard (subconjunto Y1-Y7). Carrega-se so quando
# um `pack.yaml` e lido: o coordenador pergunta o perfil em cada publicacao e nao deve
# pagar o dashboard inteiro por isso.
_CACHE: dict = {}


def _dash() -> dict:
    if "D" not in _CACHE:
        _CACHE["D"] = runpy.run_path(str(_HERE / "dashboard.py"))
    return _CACHE["D"]

PROFILE = "handoff-v1"
STATE_SCHEMA = "handoff-state/1"
ROUTES = ("solution-choice", "platform-constrained", "change-impact")
# `change-impact` entra por reabertura sobre baseline aprovada, nunca no nascimento.
BIRTH_ROUTES = ("solution-choice", "platform-constrained")
HISTORICAL_VERSION = "jorgedrestevao/aisa@85baf10"

UNSUPPORTED_PROFILE = "UNSUPPORTED_PROFILE"
STALE_INPUT = "STALE_INPUT"
INCOMPLETE_READ_SET = "INCOMPLETE_READ_SET"
AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
INTEGRITY_FAILURE = "INTEGRITY_FAILURE"
SCHEMA_UNSUPPORTED = "SCHEMA_UNSUPPORTED"
BLOCKING_GAP = "BLOCKING_GAP"
RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
CODES = (UNSUPPORTED_PROFILE, STALE_INPUT, INCOMPLETE_READ_SET, AUTHORIZATION_REQUIRED,
         INTEGRITY_FAILURE, SCHEMA_UNSUPPORTED, BLOCKING_GAP, RECOVERY_REQUIRED)

# O que `profile_of` devolve em `kind`.
HANDOFF = "handoff"
LEGACY = "legacy"
UNBORN = "unborn"
UNREADABLE = "unreadable"

SCHEMAS_DIR = _HERE.parent / "schemas"
PACKS_DIR = _HERE.parent.parent / "packs"


# ------------------------------------------------------------------ resposta

def response(ok, code=None, reasons=(), affected_ids=(), input_revision=None,
             next_actions=()) -> dict:
    """O envelope de 02 §9. `ok=True` nunca traz codigo; `ok=False` traz sempre um estavel."""
    if ok and code is not None:
        raise ValueError("resposta ok nao traz codigo")
    if not ok and code not in CODES:
        raise ValueError("codigo nao estavel: {!r}".format(code))
    return {"ok": bool(ok), "code": code,
            "reasons": [dict(r) for r in reasons],
            "affected_ids": list(affected_ids),
            "input_revision": input_revision,
            "next_actions": [dict(a) for a in next_actions]}


def _reason(detail, source="workflow", source_code=None):
    r = {"detail": detail, "source": source}
    if source_code:
        r["source_code"] = source_code
    return r


# ------------------------------------------------------------------ schemas

def load_schema(name: str) -> dict:
    """`handoff-state` -> o schema versionado em `library/kernel/schemas/`."""
    return json.loads((SCHEMAS_DIR / (name + ".schema.json")).read_text(encoding="utf-8"))


_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _is_type(value, name):
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[name])


def validate(instance, schema: dict, root: dict | None = None, path: str = "$"):
    """`(erros, desconhecidos)` — o subconjunto de JSON Schema que os schemas usam.

    Palavras-chave: `type`, `const`, `enum`, `required`, `properties`, `items`,
    `minItems`, `minLength`, `minimum`, `pattern`, `$ref` local e `additionalProperties`
    como schema (os valores de um mapa: cada chave vale contra ele e nao e desconhecida).
    Qualquer outra num schema
    e erro de schema, nao silencio. `desconhecidos` lista os campos que o schema nao
    declara: sao reportados e preservados, nunca apagados."""
    root = root or schema
    errors, unknown = [], []
    known = {"$schema", "$id", "title", "description", "$defs", "type", "const", "enum",
             "required", "properties", "items", "minItems", "minLength", "minimum",
             "pattern", "$ref", "additionalProperties"}
    extra = set(schema) - known
    if extra:
        return ["{}: palavra-chave de schema fora do subconjunto: {}".format(
            path, ", ".join(sorted(extra)))], unknown
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            return ["{}: $ref nao local: {}".format(path, ref)], unknown
        return validate(instance, root["$defs"][ref.split("/")[-1]], root, path)
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(instance, n) for n in names):
            return ["{}: tipo {} esperado".format(path, "|".join(names))], unknown
    if "const" in schema and instance != schema["const"]:
        errors.append("{}: valor {!r} != {!r}".format(path, instance, schema["const"]))
    if "enum" in schema and instance not in schema["enum"]:
        errors.append("{}: valor {!r} fora de {}".format(path, instance, schema["enum"]))
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append("{}: texto vazio".format(path))
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append("{}: {!r} nao segue {}".format(path, instance, schema["pattern"]))
    if _is_type(instance, "number") and "minimum" in schema and instance < schema["minimum"]:
        errors.append("{}: {} < {}".format(path, instance, schema["minimum"]))
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append("{}: menos de {} item(ns)".format(path, schema["minItems"]))
        if "items" in schema:
            for i, item in enumerate(instance):
                e, u = validate(item, schema["items"], root, "{}[{}]".format(path, i))
                errors += e
                unknown += u
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append("{}: falta `{}`".format(path, key))
        props = schema.get("properties")
        extra = schema.get("additionalProperties")
        if extra is not None and not isinstance(extra, dict):
            return errors + ["{}: additionalProperties so como schema".format(path)], unknown
        if props is not None or extra is not None:
            for key, value in instance.items():
                sub = "{}.{}".format(path, key)
                if props is not None and key in props:
                    e, u = validate(value, props[key], root, sub)
                elif extra is not None:
                    e, u = validate(value, extra, root, sub)
                else:
                    e, u = [], [sub]
                errors += e
                unknown += u
    return errors, unknown


# ------------------------------------------------------------------ perfil

def _read_state(eng: Path):
    p = Path(eng) / "_state.json"
    if not p.is_file():
        return None, None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, "{}: {}".format(type(exc).__name__, exc)
    if not isinstance(data, dict):
        return None, "o conteudo nao e um objecto JSON"
    return data, None


def profile_of(eng) -> dict:
    """Que perfil tem o engagement. Le `_state.json` e nada mais.

    `kind`:
      `unborn`     sem `_state.json` — o `/start` esta a cria-lo;
      `unreadable` `_state.json` existe e nao se le — nunca se trata como legado;
      `legacy`     `_state.json` sem bloco `workflow` — versao historica, so leitura aqui;
      `handoff`    bloco `workflow` presente (a validade verifica-se em `validate_profile`).
    """
    state, err = _read_state(eng)
    if err:
        return {"kind": UNREADABLE, "workflow": None, "state": None, "detail": err}
    if state is None:
        return {"kind": UNBORN, "workflow": None, "state": None, "detail": ""}
    if "workflow" not in state:
        return {"kind": LEGACY, "workflow": None, "state": state,
                "detail": "sem bloco `workflow`: engagement da versao historica"}
    return {"kind": HANDOFF, "workflow": state["workflow"], "state": state, "detail": ""}


# ------------------------------------------------------------ escrita de autoridades

def state_problems(actual_text: str, new_text: str) -> list:
    """Razoes para recusar `new_text` como `_state.json` sobre `actual_text` (F1 I-07).

    Nenhuma chave existente desaparece em silencio, e o bloco `workflow` nao muda por
    esta via: muda-o o `workflow.py` pelo coordenador. Um `_state.json` actual que nao se
    le nao tem nada a comparar — quem decide e o bootstrap. Uma regra, dois consumidores:
    o guarda (escrita por ferramenta) e `resolve.publish` (escrita pelo coordenador)."""
    try:
        actual = json.loads(actual_text)
    except (TypeError, ValueError):
        return []
    if not isinstance(actual, dict):
        return []
    try:
        novo = json.loads(new_text)
    except ValueError as exc:
        return [_reason("o `_state.json` novo não é JSON ({})".format(exc),
                        source_code="STATE_NOT_JSON")]
    if not isinstance(novo, dict):
        return [_reason("o `_state.json` novo não é um objecto JSON",
                        source_code="STATE_NOT_JSON")]
    fora = []
    perdidas = sorted(set(actual) - set(novo))
    if perdidas:
        fora.append(_reason(
            "o `_state.json` novo deixa cair {} — campos existentes não se descartam em "
            "silêncio".format(", ".join("`{}`".format(k) for k in perdidas)),
            source_code="STATE_KEYS_DROPPED"))
    if "workflow" in actual and novo.get("workflow") != actual.get("workflow"):
        fora.append(_reason(
            "o bloco `workflow` (perfil e rota) não muda por esta via: muda-o o "
            "`workflow.py` pelo coordenador", source_code="WORKFLOW_CHANGED"))
    return fora


def su_problems(eng, old_text: str, new_text: str) -> list:
    """Razoes para recusar `new_text` como SU de um engagement `handoff-v1` (T08, F0 D19).

    1. Nenhuma linha desaparece: a SU e append-only; uma transicao acrescenta a sucessora e
       as edicoes sancionadas mudam celulas, nunca apagam a linha.
    2. Uma linha `Confirmed` nova, ou existente que a escrita muda (promocao no lugar com o
       mesmo id incluida), traz um localizador das classes de `states.md` → *Confirmed
       threshold*, com o alvo presente. Verificador do motor (`audit_confirmed_locators`),
       o mesmo que o `/status` le: presenca e existencia do alvo, nunca a verdade."""
    D = _dash()
    velhas = {r["id"]: (r["state"], r["raw"]) for r in D["parse_su"](old_text or "")[1]}
    linhas = D["parse_su"](new_text)[1]
    fora = []
    sumidas = sorted(set(velhas) - {r["id"] for r in linhas})
    if sumidas:
        fora.append(_reason(
            "linha(s) apagada(s) da SU: {} — a SU é append-only; uma transição acrescenta a "
            "sucessora (`was <id>`)".format(", ".join(sumidas)),
            source_code="SU_ROW_REMOVED"))
    tocadas = {r["id"] for r in linhas
               if r["state"] == "Confirmed" and not r["resolved"]
               and velhas.get(r["id"]) != (r["state"], r["raw"])}
    if tocadas:
        audit = D["audit_confirmed_locators"](linhas, Path(eng), only_ids=tocadas)
        falhas = ["{} ({})".format(x["id"], x["motivo"])
                  for x in audit["sem_locator"] + audit["alvo_ausente"]]
        if falhas:
            fora.append(_reason(
                "linha(s) `Confirmed` sem prova localizável: {} — concordância entre "
                "personas não é evidência (`library/kernel/states.md` → *Confirmed "
                "threshold*); escrever como `Assumed` com a base, ou `Unknown`".format(
                    "; ".join(falhas)), source_code="CONFIRMED_WITHOUT_LOCATOR"))
    return fora


def pack_capabilities(pack: str, packs_dir: Path | None = None) -> dict:
    """As capacidades que `pack.yaml` DECLARA. O que nao esta declarado nao e suportado."""
    p = Path(packs_dir or PACKS_DIR) / (pack or "") / "pack.yaml"
    if not pack or not p.is_file():
        return {"pack": pack, "found": False, "declared": False, "capabilities": {},
                "errors": ["pack.yaml de `{}` nao existe".format(pack)], "unknown": []}
    text = p.read_text(encoding="utf-8")
    caps = {}
    for key in ("supported_workflow_profiles", "supported_routes", "design_contract_version"):
        val = _dash()["yl_scalar_at"](text, key)
        if val is not None:
            caps[key] = val
    if not caps:
        return {"pack": pack, "found": True, "declared": False, "capabilities": {},
                "errors": [], "unknown": []}
    errors, unknown = validate(caps, load_schema("handoff-pack"))
    return {"pack": pack, "found": True, "declared": not errors, "capabilities": caps,
            "errors": errors, "unknown": unknown}


def _legacy_refusal() -> dict:
    return response(False, UNSUPPORTED_PROFILE,
                    [_reason("engagement sem perfil persistido (legado): esta versao so o le",
                             source_code="legacy_profile_absent")],
                    next_actions=[
                        {"action": "ler o engagement aqui (/status, /dashboard, /resume)",
                         "reason": "a leitura nao altera nada"},
                        {"action": "continuar o trabalho em {}".format(HISTORICAL_VERSION),
                         "reason": "a versao nova nao tem runtime classic (decisao A)"}])


def _check_request(pack, profile, route, packs_dir=None) -> dict:
    if profile != PROFILE:
        return response(False, UNSUPPORTED_PROFILE,
                        [_reason("perfil `{}` nao existe nesta versao".format(profile))],
                        next_actions=[{"action": "usar o perfil {}".format(PROFILE),
                                       "reason": "unico perfil desta versao"}])
    caps = pack_capabilities(pack, packs_dir)
    if not caps["found"]:
        return response(False, UNSUPPORTED_PROFILE, [_reason(e) for e in caps["errors"]])
    if caps["errors"]:
        return response(False, UNSUPPORTED_PROFILE,
                        [_reason("declaracao de capacidades invalida: " + e) for e in caps["errors"]])
    declared = caps["capabilities"]
    if not caps["declared"] or profile not in declared.get("supported_workflow_profiles", []):
        return response(False, UNSUPPORTED_PROFILE,
                        [_reason("o pack `{}` nao declara o perfil {}".format(pack, profile))],
                        next_actions=[{"action": "escolher um pack que declare {}".format(profile),
                                       "reason": "sem declaracao nao ha fallback"}])
    if route not in declared.get("supported_routes", []):
        return response(False, UNSUPPORTED_PROFILE,
                        [_reason("o pack `{}` nao declara a rota `{}`".format(pack, route))])
    return response(True)


def validate_profile(eng=None, *, pack=None, profile=None, route=None,
                     birth=False, packs_dir=None) -> dict:
    """Pode este engagement (ou este pedido de criacao) seguir no perfil `handoff-v1`?

    Com `eng`: le `_state.json`, identifica o legado e valida o bloco `workflow` contra o
    schema e contra o que o pack declara. Com `pack`/`profile`/`route` e sem engagement:
    valida um pedido de criacao (`birth=True` admite so as rotas de nascimento)."""
    if eng is None:
        if birth and route not in BIRTH_ROUTES:
            return response(False, UNSUPPORTED_PROFILE,
                            [_reason("a rota `{}` nao se escolhe no nascimento".format(route))],
                            next_actions=[{"action": "escolher uma de: " + ", ".join(BIRTH_ROUTES),
                                           "reason": "change-impact exige baseline aprovada"}])
        return _check_request(pack, profile, route, packs_dir)

    eng = Path(eng)
    who = profile_of(eng)
    if who["kind"] == UNBORN:
        return response(False, INTEGRITY_FAILURE,
                        [_reason("`{}` nao tem `_state.json`".format(eng.name))])
    if who["kind"] == UNREADABLE:
        return response(False, INTEGRITY_FAILURE,
                        [_reason("`_state.json` ilegivel: " + who["detail"])])
    if who["kind"] == LEGACY:
        return _legacy_refusal()

    wf = who["workflow"]
    if isinstance(wf, dict) and wf.get("schema_version") not in (None, STATE_SCHEMA):
        return response(False, SCHEMA_UNSUPPORTED,
                        [_reason("bloco `workflow` com schema `{}`; esta versao le {}".format(
                            wf.get("schema_version"), STATE_SCHEMA))],
                        next_actions=[{"action": "abrir com uma versao que leia esse schema",
                                       "reason": "nao se interpreta um schema por aproximacao"}])
    errors, _unknown = validate(wf, load_schema("handoff-state"))
    if errors:
        return response(False, INTEGRITY_FAILURE, [_reason(e) for e in errors])
    if wf["route"] == "platform-constrained" and not wf["route_basis"]["authority_ref"]:
        return response(False, INTEGRITY_FAILURE,
                        [_reason("rota platform-constrained sem `authority_ref` para a imposicao")])
    return _check_request(who["state"].get("pack"), wf["profile"], wf["route"], packs_dir)


# ------------------------------------------------------------------ CLI

def utf8_console() -> None:
    _dash()["utf8_console"]()


def main(argv=None) -> int:
    utf8_console()
    import argparse
    ap = argparse.ArgumentParser(description="perfil de workflow handoff-v1 (so leitura)")
    ap.add_argument("command", choices=["check"])
    ap.add_argument("--engagement")
    ap.add_argument("--pack")
    ap.add_argument("--profile")
    ap.add_argument("--route")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.engagement:
        eng = Path(a.engagement)
        if not eng.is_dir():
            eng = Path("projects") / a.engagement
        out = validate_profile(eng)
    else:
        out = validate_profile(pack=a.pack, profile=a.profile, route=a.route, birth=True)
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("ok" if out["ok"] else out["code"])
        for r in out["reasons"]:
            print("  - " + r["detail"])
        for n in out["next_actions"]:
            print("  -> {} ({})".format(n["action"], n["reason"]))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
