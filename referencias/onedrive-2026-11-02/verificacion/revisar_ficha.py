"""Verificación de una ficha producida por el agente estructurador (uso interno, para revisar salidas).

    errores, avisos = revisar(ficha_nueva, textos_de_fuentes_nuevas, ficha_vigente)

Desde la terminal:
    python revisar_ficha.py ficha_v2.json --vigente ficha_v1.json --fuente F2=transcripcion.txt

Comprueba: esquema; citas literales y en su ubicación; que ningún dato ni contradicción de la versión vigente
haya desaparecido o cambiado de identificador; numeración de identificadores nuevos; versión; descartes y
resoluciones respaldados por una nota interna; y lista de cambios coherente con lo que cambió.
No comprueba la fidelidad del enunciado frente a la cita: eso es revisión humana.
"""
import json, pathlib, re
import jsonschema

ESQUEMA = json.loads((pathlib.Path(__file__).resolve().parent.parent / "a1_estructurador" / "faed_ficha.schema.json").read_text(encoding="utf-8"))


def _norm(t):
    return re.sub(r"\s+", " ", t).strip()


def _tramos(texto):
    tramos = {}
    for linea in texto.splitlines():
        m = re.match(r"\s*\[([^\]]+)\]\s*(.*)", linea)
        if m:
            tramos.setdefault(m.group(1).strip(), []).append(m.group(2))
    return {k: _norm(" ".join(v)) for k, v in tramos.items()}


def _datos(f):
    for g, campos in f.items():
        if isinstance(campos, dict):
            for c, lista in campos.items():
                for d in lista:
                    yield g, c, d


def revisar(nueva, textos, vigente=None):
    """textos: {id_fuente: texto con marcas} de las fuentes nuevas de esta versión."""
    errores, avisos = [], []
    try:
        jsonschema.validate(nueva, ESQUEMA)
    except jsonschema.ValidationError as e:
        return [f"Formato: {e.message} en {'/'.join(map(str, e.absolute_path))}"], []

    prefijos = {}
    for g, campos in ESQUEMA["properties"].items():
        if campos.get("type") == "object":
            for c, d in campos["properties"].items():
                prefijos[c] = re.search(r"Prefijo de identificador: (\w+)", d["description"]).group(1)

    previos = {d["id"]: (c, d) for _, c, d in _datos(vigente)} if vigente else {}
    actuales = {}
    for g, c, d in _datos(nueva):
        if d["id"] in actuales:
            errores.append(f"{d['id']}: identificador repetido.")
        actuales[d["id"]] = (c, d)
        if not d["id"].startswith(prefijos[c] + "-"):
            errores.append(f"{d['id']}: no usa el prefijo {prefijos[c]} de su sección {c}.")
        if not d["citas"]:
            errores.append(f"{d['id']}: dato sin cita.")
        for cita in d["citas"]:
            if cita["fuente"] in textos:
                frag, texto = _norm(cita["texto"]), textos[cita["fuente"]]
                tr = _tramos(texto)
                if frag not in _norm(texto):
                    errores.append(f"{d['id']}: la cita no aparece literal en {cita['fuente']}: «{frag[:70]}».")
                elif tr and frag not in tr.get(cita["ubicacion"], ""):
                    errores.append(f"{d['id']}: la cita no está en la ubicación «{cita['ubicacion']}».")
            elif cita["fuente"] not in {f["id"] for f in (vigente or {}).get("fuentes", [])}:
                errores.append(f"{d['id']}: cita una fuente desconocida ({cita['fuente']}).")

    # Nada de la versión vigente desaparece ni cambia de sección
    for i, (c, d) in previos.items():
        if i not in actuales:
            errores.append(f"{i}: estaba en la versión vigente y desapareció.")
        elif actuales[i][0] != c:
            errores.append(f"{i}: cambió de sección ({c} → {actuales[i][0]}).")
        elif len(actuales[i][1]["citas"]) < len(d["citas"]):
            errores.append(f"{i}: perdió citas que tenía en la versión vigente.")
    # Numeración de los datos nuevos
    for c in prefijos:
        usados = sorted(int(i.split("-")[1]) for i, (cc, _) in previos.items() if cc == c)
        nuevos = sorted(int(i.split("-")[1]) for i, (cc, _) in actuales.items() if cc == c and i not in previos)
        if nuevos and usados and nuevos[0] <= usados[-1]:
            errores.append(f"{c}: un dato nuevo reutiliza o retrocede la numeración ({prefijos[c]}-{nuevos[0]:02d}).")
    # Versión
    esperada = (vigente["version"] + 1) if vigente else 1
    if nueva["version"] != esperada:
        errores.append(f"Versión {nueva['version']}; se esperaba {esperada}.")
    # Contradicciones vigentes conservadas
    previas = {k["id"]: k for k in (vigente or {}).get("contradicciones", [])}
    actuales_con = {k["id"]: k for k in nueva["contradicciones"]}
    for i in previas:
        if i not in actuales_con:
            errores.append(f"{i}: contradicción de la versión vigente que desapareció.")
    for k in nueva["contradicciones"]:
        if len(set(k["elementos_relacionados"])) < 2:
            errores.append(f"{k['id']}: una contradicción necesita al menos dos datos.")
        for i in k["elementos_relacionados"]:
            if i not in actuales:
                errores.append(f"{k['id']}: nombra un dato inexistente ({i}).")
    # Descartes y resoluciones solo con decisión registrada en una nota interna
    notas = {f["id"] for f in nueva["fuentes"] if f["tipo"] == "notas_internas"}
    for i, (c, d) in actuales.items():
        antes = previos.get(i, (None, {"estado": "vigente"}))[1]
        if d["estado"] == "descartado" and antes["estado"] == "vigente" and not notas & set(textos):
            errores.append(f"{i}: se descartó sin una nota interna nueva que registre la decisión.")
    for k in nueva["contradicciones"]:
        r = k["resolucion"]
        if k["estado"] == "resuelta" and (r["fuente"] not in notas or not r["decision"] or not r["decidido_por"]):
            errores.append(f"{k['id']}: resuelta sin una nota interna que registre la decisión y quién la tomó.")
        if k["estado"] == "abierta" and any(v is not None for v in r.values()):
            errores.append(f"{k['id']}: está abierta, pero su resolución no está vacía.")
    # Datos para revisión humana obligatoria
    for i, (c, d) in actuales.items():
        if d["afirmado_por"] == "no_identificado" and i not in previos:
            avisos.append(f"{i}: afirmado por alguien no identificado; revisar antes de marcar la versión como revisada.")
        if d["confirmado_por_cliente"] and len(d["citas"]) < 1:
            errores.append(f"{i}: confirmado por el cliente sin cita de la validación.")
    # Cambios declarados frente a cambios reales
    declarados = {(x["elemento"], x["accion"]) for x in nueva["cambios"]}
    for i in actuales:
        if i not in previos and (i, "agregado") not in declarados:
            avisos.append(f"{i}: se agregó y no aparece en cambios.")
    for i in actuales:
        if i in previos and actuales[i][1] != previos[i][1] and not any(e == i for e, _ in declarados):
            avisos.append(f"{i}: cambió y no aparece en cambios.")
    return errores, avisos


if __name__ == "__main__":
    import argparse, sys
    a = argparse.ArgumentParser(description="Verifica una versión de la ficha producida por A1 · Estructurar.")
    a.add_argument("ficha", help="Ficha nueva (JSON) que entregó el agente")
    a.add_argument("--vigente", help="Ficha vigente (JSON) con la que trabajó el agente; omitir si es la primera versión")
    a.add_argument("--fuente", action="append", default=[], metavar="ID=RUTA",
                   help="Texto de cada fuente nueva, con sus marcas de ubicación; por ejemplo F2=transcripcion.txt")
    x = a.parse_args()
    nueva = json.loads(pathlib.Path(x.ficha).read_text(encoding="utf-8"))
    vigente = json.loads(pathlib.Path(x.vigente).read_text(encoding="utf-8")) if x.vigente else None
    textos = {k: pathlib.Path(r).read_text(encoding="utf-8") for k, r in (f.split("=", 1) for f in x.fuente)}
    errores, avisos = revisar(nueva, textos, vigente)
    for t in errores: print("ERROR ", t)
    for t in avisos: print("AVISO ", t)
    print(f"{len(errores)} errores · {len(avisos)} avisos")
    sys.exit(1 if errores else 0)
