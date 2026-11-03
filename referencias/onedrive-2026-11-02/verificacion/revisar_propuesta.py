"""Verificación de la salida de A6 · Redactar propuesta.

    errores, avisos = revisar(propuesta, detalle, juicio, evaluacion, primer_bloque, tipo_estimacion)

Desde la terminal:
    python revisar_propuesta.py propuesta.json detalle.json juicio.json evaluacion.json --primer-bloque si --tipo formal

Comprueba el esquema, que haya una descripción por cada componente, que ningún texto tenga cifras de la estimación,
códigos ni términos internos del método, que el objetivo del bloque y el primer entregable sigan los parámetros, que la
propuesta tenga supuestos e información por pedir cuando la evaluación los trae, y que las exclusiones de las fronteras
aparezcan en lo que no incluye. No juzga si los textos son fieles a la ficha ni si están bien redactados: eso es
revisión humana.
"""
import json, pathlib, re, sys
import jsonschema

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ESQUEMA = json.loads((RAIZ / "a6_redactor" / "faed_propuesta.schema.json").read_text(encoding="utf-8"))
CODIGOS = r"\b(D\d+\.\d+|C\d{2}(-P\d{2})?|PF-\d+|INT-\d+|PRY-\d+|ACT-\d+|SOL-\d{4}-\d+|[A-Z]{3}-\d{2})\b"
CIFRAS = r"\$|\bmillones\b|\bCOP\b|\d[\d.,]*\s*(horas|h)\b|\bsprints?\b"
PLAZOS = r"\d[\d.,]*\s*(semanas|meses)\b"
TERMINOS = ["arquetipo", "madurez", "talla", "nivel de información", "nivel de experiencia", "confianza", "comparable",
            "ruta compleja", "ruta estándar", "reúso", "factor de", "FAED", "framework", "escenario optimista", "escenario pesimista"]


def _textos(pr):
    yield "nombre del proyecto", pr["nombre_proyecto"]
    for i, t in enumerate(pr["contexto"], 1): yield f"contexto, párrafo {i}", t
    yield "descripción de la solución", pr["solucion"]["descripcion"]
    for c in pr["solucion"]["componentes"]: yield f"descripción de {c['id']}", c["descripcion"]
    for i, t in enumerate(pr["solucion"]["incluye_adicional"], 1): yield f"incluye {i}", t
    for i, t in enumerate(pr["solucion"]["no_incluye"], 1): yield f"no incluye {i}", t
    for i, t in enumerate(pr["supuestos"], 1): yield f"supuesto {i}", t
    for i, t in enumerate(pr["informacion_que_mejora"], 1): yield f"información {i}", t
    if pr["objetivo_bloque"]: yield "objetivo del bloque", pr["objetivo_bloque"]
    if pr["primer_entregable"]: yield "primer entregable", pr["primer_entregable"]


def revisar(pr, det, juicio, ev, primer_bloque, tipo_estimacion="formal"):
    errores, avisos = [], []
    try:
        jsonschema.validate(pr, ESQUEMA)
    except jsonschema.ValidationError as e:
        return [f"Formato: {e.message} en {'/'.join(map(str, e.absolute_path))}"], []

    if pr["id_solicitud"] != det["id_solicitud"] or pr["version_ficha"] != det["version_ficha"]:
        errores.append("La salida no corresponde a la solicitud o a la versión de la ficha de los componentes.")
    if [c["id"] for c in pr["solucion"]["componentes"]] != [c["id"] for c in det["componentes"]]:
        errores.append("Debe haber una descripción por cada componente, en el mismo orden de las fichas de los componentes.")

    for donde, t in _textos(pr):
        if not t.strip():
            errores.append(f"{donde}: está vacío.")
        if re.search(CIFRAS, t, re.I):
            errores.append(f"{donde}: tiene cifras de la estimación o del precio: «{t[:70]}».")
        if re.search(CODIGOS, t):
            errores.append(f"{donde}: tiene códigos internos: «{t[:70]}».")
        for k in TERMINOS:
            if re.search(r"\b" + re.escape(k), t, re.I):
                errores.append(f"{donde}: usa el término interno «{k}».")
        if re.search(PLAZOS, t):
            avisos.append(f"{donde}: menciona un plazo; confirme que es una cifra del cliente: «{t[:70]}».")
        if "—" in t:
            avisos.append(f"{donde}: usa guiones largos.")

    if not 2 <= len(pr["contexto"]) <= 3:
        avisos.append(f"El contexto tiene {len(pr['contexto'])} párrafos; la plantilla pide de dos a tres.")

    hay = primer_bloque == "si"
    if hay and tipo_estimacion == "preliminar":
        errores.append("Una estimación preliminar no lleva primer bloque: revise el parámetro.")
    if hay and not juicio["primer_bloque"]["procesos"]:
        errores.append("El parámetro dice que hay primer bloque, pero A5 no lo propuso.")
    if tipo_estimacion == "preliminar":
        if pr["objetivo_bloque"] is not None or pr["primer_entregable"] is not None:
            errores.append("En una estimación preliminar, el objetivo del bloque y el primer entregable van en null.")
    elif hay and (pr["objetivo_bloque"] is None or pr["primer_entregable"] is not None):
        errores.append("Con primer bloque, va el objetivo del bloque y el primer entregable en null.")
    elif not hay and (pr["objetivo_bloque"] is not None or pr["primer_entregable"] is None):
        errores.append("Sin primer bloque, va el primer entregable y el objetivo del bloque en null.")

    if ev["supuestos"] and not pr["supuestos"]:
        errores.append("La evaluación trae supuestos y la propuesta no tiene ninguno.")
    al_cliente = [q for q in ev["preguntas"] if q["destinatario"] == "cliente"]
    if al_cliente and not pr["informacion_que_mejora"]:
        errores.append("La evaluación trae preguntas para el cliente y la propuesta no pide ninguna información.")
    excluye = [x for c in det["componentes"] for x in c["frontera"]["excluye"]]
    if excluye and len(pr["solucion"]["no_incluye"]) < 1:
        errores.append("Las fronteras de los componentes tienen exclusiones y la propuesta no incluye ninguna.")
    if len(set(map(str.lower, pr["supuestos"]))) != len(pr["supuestos"]):
        avisos.append("Hay supuestos repetidos.")
    return errores, avisos


if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser(description="Verifica la salida de A6 · Redactar propuesta.")
    a.add_argument("propuesta"); a.add_argument("detalle"); a.add_argument("juicio"); a.add_argument("evaluacion")
    a.add_argument("--primer-bloque", required=True, choices=["si", "no"])
    a.add_argument("--tipo", required=True, choices=["formal", "preliminar"])
    x = a.parse_args()
    leer = lambda r: json.loads(pathlib.Path(r).read_text(encoding="utf-8"))
    errores, avisos = revisar(leer(x.propuesta), leer(x.detalle), leer(x.juicio), leer(x.evaluacion), x.primer_bloque, x.tipo)
    for t in errores: print("ERROR ", t)
    for t in avisos: print("AVISO ", t)
    print(f"{len(errores)} errores · {len(avisos)} avisos")
    sys.exit(1 if errores else 0)
