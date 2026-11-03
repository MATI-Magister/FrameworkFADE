"""Verificación de la salida de A7 · Cerrar y aprender.

    errores, avisos = revisar(cierre, preparacion, detalle, catalogo, notas, propuesta)

Desde la terminal:
    python revisar_cierre.py cierre.json preparacion_cierre.json detalle.json --propuesta propuesta.json --catalogo catalogo.json --notas F3=notas.txt

Comprueba el esquema, que haya un elemento de reúso por cada activo que se usó como evidencia y una causa por cada
componente que la requiere, que cada cita aparezca literal en su línea de las notas, que todo lo confirmado tenga cita y
todo lo no sustentado quede en null o por confirmar con su pregunta, que los activos nuevos no estén ya en el catálogo y
que la revisión de cierre se llene solo cuando el proyecto la requiere, con supuestos copiados tal como están en la
propuesta o en las fichas de los componentes. No juzga si cada causa es la correcta: eso lo
confirma el líder del proyecto.
"""
import json, pathlib, re, sys
import jsonschema

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ESQUEMA = json.loads((RAIZ / "a7_cierre" / "faed_cierre.schema.json").read_text(encoding="utf-8"))


def _norm(t):
    return re.sub(r"\s+", " ", t).strip()


def _lineas(texto):
    out = {}
    for linea in texto.splitlines():
        m = re.match(r"\s*\[([^\]]+)\]\s*(.*)", linea)
        if m:
            out[m.group(1).strip()] = _norm(out.get(m.group(1).strip(), "") + " " + m.group(2))
    return out


def revisar(c, prep, det, catalogo, notas, propuesta=None):
    """notas: {id_fuente: texto con marcas de línea}."""
    errores, avisos = [], []
    try:
        jsonschema.validate(c, ESQUEMA)
    except jsonschema.ValidationError as e:
        return [f"Formato: {e.message} en {'/'.join(map(str, e.absolute_path))}"], []
    lineas = {f: _lineas(t) for f, t in notas.items()}

    def citas_ok(donde, citas):
        for x in citas:
            if x["fuente"] not in lineas:
                errores.append(f"{donde}: cita una fuente desconocida ({x['fuente']}).")
            elif _norm(x["texto"]) not in lineas[x["fuente"]].get(x["ubicacion"], ""):
                errores.append(f"{donde}: la cita no aparece literal en {x['fuente']}, {x['ubicacion']}: «{x['texto'][:60]}».")

    if c["id_solicitud"] != det["id_solicitud"]:
        errores.append("La salida no corresponde a la solicitud.")

    # Reúso real
    esperado = {}
    for comp in det["componentes"]:
        for p in comp["procesos"]:
            if p["activo_reutilizado"]:
                k = (p["activo_reutilizado"], comp["id"])
                esperado[k] = esperado.get(k, 0) + 1
    vistos = {(r["activo"], r["componente"]): r for r in c["reuso_real"]}
    if set(vistos) != set(esperado) or len(vistos) != len(c["reuso_real"]):
        errores.append("Debe haber un elemento de reúso por cada par de activo y componente que se usó como evidencia al estimar.")
    procesos = {comp["id"]: len(comp["procesos"]) for comp in det["componentes"]}
    for k, r in vistos.items():
        donde = f"Reúso de {k[0]} en {k[1]}"
        if k in esperado and r["procesos_estimados"] != esperado[k]:
            errores.append(f"{donde}: la estimación marcó {esperado[k]} procesos y dice {r['procesos_estimados']}.")
        citas_ok(donde, r["citas"])
        if r["reutilizado"] is None:
            if r["procesos_cubiertos"] is not None or r["citas"]:
                errores.append(f"{donde}: sin confirmación, los procesos cubiertos van en null y sin citas.")
            if not c["preguntas_para_el_lider"]:
                errores.append(f"{donde}: no está confirmado y no hay preguntas para el líder del proyecto.")
        else:
            if not r["citas"]:
                errores.append(f"{donde}: se confirma o se descarta sin cita.")
            if r["reutilizado"] and r["procesos_cubiertos"] is None:
                errores.append(f"{donde}: se reutilizó y no dice cuántos procesos cubrió.")
            if r["reutilizado"] is False and r["procesos_cubiertos"] not in (None, 0):
                errores.append(f"{donde}: no se reutilizó y dice que cubrió procesos.")
            if r["procesos_cubiertos"] and r["procesos_cubiertos"] > procesos.get(k[1], 0):
                errores.append(f"{donde}: cubre más procesos de los que tiene el componente.")

    # Causas
    requieren = prep["desviacion"]["requieren_causa"]
    if [x["componente"] for x in c["causas"]] != requieren:
        errores.append("Debe haber una causa por cada componente que la requiere, en el orden de la preparación: " + ", ".join(requieren) + ".")
    for x in c["causas"]:
        donde = f"Causa de {x['componente']}"
        citas_ok(donde, x["citas"])
        if x["causa"] == "por_confirmar":
            if x["citas"]:
                avisos.append(f"{donde}: está por confirmar, pero tiene citas.")
            if not c["preguntas_para_el_lider"]:
                errores.append(f"{donde}: está por confirmar y no hay preguntas para el líder del proyecto.")
        elif not x["citas"]:
            errores.append(f"{donde}: la causa {x['causa']} no tiene cita.")

    # Activos nuevos
    en_catalogo = {a["nombre"].lower() for a in catalogo["activos"]}
    for a in c["activos_nuevos"]:
        donde = f"Activo nuevo «{a['nombre']}»"
        if a["componente_origen"] not in procesos:
            errores.append(f"{donde}: el componente {a['componente_origen']} no existe.")
        if a["nombre"].lower() in en_catalogo:
            errores.append(f"{donde}: ya está en el catálogo.")
        if not a["procesos_que_cubre"]:
            errores.append(f"{donde}: no dice qué procesos cubre.")
        if not a["citas"]:
            errores.append(f"{donde}: no tiene cita que diga que se puede volver a usar.")
        citas_ok(donde, a["citas"])

    # Revisión de cierre
    rv = c["revision_de_cierre"]
    if prep["requiere_revision_de_cierre"]:
        if not rv["supuestos_no_cumplidos"] and not rv["temas"]:
            errores.append("El proyecto cerró fuera del rango y la revisión de cierre está vacía.")
        conocidos = {_norm(x) for x in (propuesta or {}).get("supuestos", [])} | {_norm(x) for comp in det["componentes"] for x in comp["supuestos"]}
        for s in rv["supuestos_no_cumplidos"]:
            citas_ok("Supuesto no cumplido", s["citas"])
            if propuesta is not None and _norm(s["supuesto"]) not in conocidos:
                errores.append(f"Supuesto no cumplido que no está en la propuesta ni en las fichas de los componentes: «{s['supuesto'][:60]}».")
            if not s["citas"]:
                errores.append(f"Supuesto no cumplido sin cita: «{s['supuesto'][:60]}».")
    elif rv["supuestos_no_cumplidos"] or rv["temas"]:
        errores.append("El proyecto cerró dentro del rango; la revisión de cierre no aplica y debe ir vacía.")

    if prep.get("horas_fuera_de_la_estimacion") and not c["advertencias"]:
        avisos.append("Hay horas de trabajos fuera de la estimación y la salida no lo advierte.")
    if prep["epicas_sin_asignar"] or prep["componentes_sin_horas"]:
        if not c["advertencias"]:
            avisos.append("Hay épicas sin asignar o componentes sin horas y la salida no lo advierte.")
    return errores, avisos


if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser(description="Verifica la salida de A7 · Cerrar y aprender.")
    a.add_argument("cierre"); a.add_argument("preparacion"); a.add_argument("detalle")
    a.add_argument("--propuesta", required=True, help="Textos de A6 que se enviaron al cliente")
    a.add_argument("--catalogo", required=True)
    a.add_argument("--notas", required=True, nargs="+", help="Fuentes de las notas: ID=RUTA")
    x = a.parse_args()
    leer = lambda r: json.loads(pathlib.Path(r).read_text(encoding="utf-8"))
    notas = {k: pathlib.Path(v).read_text(encoding="utf-8") for k, v in (n.split("=", 1) for n in x.notas)}
    errores, avisos = revisar(leer(x.cierre), leer(x.preparacion), leer(x.detalle), leer(x.catalogo), notas, leer(x.propuesta))
    for t in errores: print("ERROR ", t)
    for t in avisos: print("AVISO ", t)
    print(f"{len(errores)} errores · {len(avisos)} avisos")
    sys.exit(1 if errores else 0)
