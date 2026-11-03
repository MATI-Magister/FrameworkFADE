"""Verificación de la salida de A5 · Generar escenario.

    errores, avisos = revisar(juicio, detalle, preparacion, tipo_estimacion, modalidad_solicitada)

Desde la terminal:
    python revisar_escenario.py juicio.json detalle.json preparacion.json --tipo formal --modalidad ninguna

Comprueba el esquema, que haya un juicio con justificación por cada candidato de la preparación y ningún proyecto de más,
que el bloque se proponga solo cuando corresponde, que sus procesos existan y que sus horas queden dentro del tamaño del
bloque, y que la funcionalidad no tenga códigos internos. Avisa cuando el bloque incluye procesos de componentes Supuestos.
No juzga si cada candidato es de verdad comparable ni si el bloque es la mejor funcionalidad: eso es revisión humana.
"""
import json, pathlib, re, sys
import jsonschema

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "calculo"))
import faed_calculos as fc

ESQUEMA = json.loads((RAIZ / "a5_generador" / "faed_juicio_escenario.schema.json").read_text(encoding="utf-8"))
MODALIDADES = ["ninguna", "bolsa_de_horas", "sprints", "bloque", "precio_fijo"]
CODIGOS = r"\b(D\d+\.\d+|C\d{2}(-P\d{2})?|PF-\d+|INT-\d+|PRY-\d+|ACT-\d+|REU-\d+)\b"


def revisar(juicio, det, prep, tipo_estimacion, modalidad_solicitada, valores=None):
    errores, avisos = [], []
    try:
        jsonschema.validate(juicio, ESQUEMA)
    except jsonschema.ValidationError as e:
        return [f"Formato: {e.message} en {'/'.join(map(str, e.absolute_path))}"], []
    v = valores or fc.cargar_valores()

    if juicio["id_solicitud"] != det["id_solicitud"] or juicio["version_ficha"] != det["version_ficha"]:
        errores.append("La salida no corresponde a la solicitud o a la versión de la ficha de los componentes.")

    # Comparables
    candidatos = [c["id"] for c in prep["candidatos"]]
    juzgados = [x["proyecto"] for x in juicio["comparables"]]
    if juzgados != candidatos:
        extra = [i for i in juzgados if i not in candidatos]
        if extra:
            errores.append("Proyectos que no están entre los candidatos: " + ", ".join(extra) + ".")
        errores.append("Debe haber un juicio por cada candidato de la preparación, en el mismo orden.")
    for x in juicio["comparables"]:
        if not x["justificacion"].strip():
            errores.append(f"{x['proyecto']}: el juicio no tiene justificación.")
    if not candidatos and not juicio["advertencias"]:
        avisos.append("No hay candidatos a comparables y la salida no lo advierte.")
    n = sum(1 for x in juicio["comparables"] if x["es_comparable"])
    if n <= 1:
        avisos.append(f"{n} proyectos comparables: la experiencia será baja" + ("." if tipo_estimacion == "preliminar" else " y la cotización seguirá la ruta compleja."))

    # Primer bloque
    bloque = juicio["primer_bloque"]
    ids = bloque["procesos"]
    total = sum(prep["proyecto"]["horas_componentes"].values()) * (1 + v["gestion_y_acompanamiento"])
    tam = v["bloque_de_trabajo_horas"]
    no_corresponde = (tipo_estimacion == "preliminar" and "la estimación es preliminar") or \
                     (modalidad_solicitada in ("bolsa_de_horas", "sprints", "precio_fijo") and f"el cliente pidió {modalidad_solicitada}") or \
                     (total <= tam["maximo"] and "el proyecto completo cabe en un bloque")
    if no_corresponde and ids:
        errores.append(f"No corresponde proponer bloque: {no_corresponde}.")
    elif not no_corresponde and not ids:
        errores.append("Corresponde proponer un primer bloque y la lista de procesos está vacía.")
    if ids:
        existentes = {p["id"] for p in prep["procesos"]}
        faltan = [i for i in ids if i not in existentes]
        if faltan:
            errores.append("Procesos del bloque que no existen: " + ", ".join(faltan) + ".")
        if len(set(ids)) != len(ids):
            errores.append("El bloque repite procesos.")
        if not (bloque["funcionalidad"] or "").strip():
            errores.append("El bloque no describe la funcionalidad que el cliente puede usar.")
        elif re.search(CODIGOS, bloque["funcionalidad"]):
            errores.append("La funcionalidad del bloque incluye códigos internos.")
        if not faltan:
            comps = [fc.calcular_componente(c, v) for c in fc.componentes_desde_detalle(det)]
            h = fc.horas_bloque(ids, det, comps, v)
            if not tam["minimo"] <= h <= tam["maximo"]:
                errores.append(f"El bloque suma {h} horas; el tamaño del bloque es de {tam['minimo']} a {tam['maximo']} horas.")
            supuestos = {c["id"] for c in det["componentes"] if c["madurez"] == "supuesto"}
            con_supuesto = sorted({i.split("-")[0] for i in ids} & supuestos)
            if con_supuesto and not juicio["advertencias"]:
                avisos.append("El bloque incluye procesos de componentes Supuestos (" + ", ".join(con_supuesto) + ") y la salida no lo advierte.")
    elif bloque["funcionalidad"] is not None:
        avisos.append("No hay procesos en el bloque, pero sí una funcionalidad.")
    return errores, avisos


if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser(description="Verifica la salida de A5 · Generar escenario.")
    a.add_argument("juicio"); a.add_argument("detalle"); a.add_argument("preparacion")
    a.add_argument("--tipo", required=True, choices=["formal", "preliminar"])
    a.add_argument("--modalidad", required=True, choices=MODALIDADES)
    x = a.parse_args()
    leer = lambda r: json.loads(pathlib.Path(r).read_text(encoding="utf-8"))
    errores, avisos = revisar(leer(x.juicio), leer(x.detalle), leer(x.preparacion), x.tipo, x.modalidad)
    for t in errores: print("ERROR ", t)
    for t in avisos: print("AVISO ", t)
    print(f"{len(errores)} errores · {len(avisos)} avisos")
    sys.exit(1 if errores else 0)
