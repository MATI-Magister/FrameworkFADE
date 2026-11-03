"""Registro del cierre confirmado: agrega el proyecto al registro de proyectos y actualiza el catálogo de activos.

    registro_nuevo, catalogo_nuevo, errores = registrar(cierre, preparacion, linea_base, detalle, registro, catalogo, datos)

Desde la terminal (desde la carpeta agentes):
    python registro/registrar_cierre.py cierre_confirmado.json preparacion_cierre.json linea_base.json detalle.json \\
        --registro datos/registro_proyectos.json --catalogo datos/catalogo_activos.json \\
        --nombre "Nombre del proyecto" --cliente "Cliente" --duracion 5 --equipo "Tech lead" "2 desarrolladores" \\
        --salida-registro registro_v2.json --salida-catalogo catalogo_v2.json

Solo registra un cierre que el líder del proyecto ya confirmó: ningún reúso sin confirmar ni causa por confirmar. El
arquetipo principal del proyecto se registra con las horas reales, porque así lo comparará A5 en las próximas cotizaciones.
Escribe versiones nuevas de los archivos; no modifica los originales. Con el proyecto en el registro, queda disponible
como comparable para A5 y para la recalibración.
"""
import copy, datetime, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "calculo"))
import faed_calculos as fc


def _siguiente(prefijo, ids):
    n = max([int(i.split("-")[1]) for i in ids if i.startswith(prefijo + "-")] or [0]) + 1
    return f"{prefijo}-{n:02d}"


def registrar(c, prep, base, det, registro, catalogo, datos):
    errores = []
    for r in c["reuso_real"]:
        if r["reutilizado"] is None:
            errores.append(f"Falta confirmar si {r['activo']} se reutilizó en {r['componente']}.")
    for x in c["causas"]:
        if x["causa"] == "por_confirmar":
            errores.append(f"Falta confirmar la causa de la desviación de {x['componente']}.")
    if prep["epicas_sin_asignar"] or prep["componentes_sin_horas"]:
        errores.append("Hay épicas sin asignar o componentes sin horas: corrija la exportación de Jira y prepare el cierre de nuevo.")
    if errores:
        return None, None, errores

    nombres = {x["id"]: x["nombre"] for x in det["componentes"]}
    causas = {x["componente"]: x["causa"] for x in c["causas"]}
    dev = {x["id"]: x for x in prep["desviacion"]["componentes"]}
    fecha = datos.get("fecha") or datetime.date.today().isoformat()

    reales = [{"arquetipo": x["arquetipo"], "horas": dev[x["id"]]["horas_reales"],
               "procesos": len(next(c for c in det["componentes"] if c["id"] == x["id"])["procesos"])} for x in base["componentes"]]
    principal_real = fc.participacion_arquetipos(reales, {"umbral_arquetipo_secundario": 0.15})[1]
    reg = copy.deepcopy(registro)
    pid = _siguiente("PRY", [p["id"] for p in reg["proyectos"]])
    reg["proyectos"].append({
        "id": pid, "nombre": datos["nombre"], "cliente": datos["cliente"], "descripcion": c["descripcion_proyecto"],
        "arquetipo_principal": principal_real, "arquetipo_principal_estimado": base["arquetipos"]["principal"],
        "componentes": [{"nombre": x["nombre"], "arquetipo": x["arquetipo"], "horas_esperadas": dev[x["id"]]["linea_base_ajustada"],
                         "horas_reales": dev[x["id"]]["horas_reales"], "desviacion": dev[x["id"]]["desviacion"],
                         "causa": causas.get(x["id"])} for x in base["componentes"]],
        "procesos": sum(len(x["procesos"]) for x in det["componentes"]), "talla": None,
        "horas_reales": prep["desviacion"]["horas_reales"], "desviacion": prep["desviacion"]["proyecto"],
        "dentro_del_rango": not prep["fuera_de_rango"], "horas_fuera_de_la_estimacion": round(sum(prep.get("horas_fuera_de_la_estimacion", {}).values()), 1),
        "duracion_meses": datos["duracion_meses"], "equipo": datos.get("equipo") or None,
        "origen": "cierre", "fecha_cierre": fecha, "id_solicitud": c["id_solicitud"], "version_valores": prep["version_valores"],
    })

    cat = copy.deepcopy(catalogo)
    activos = {a["id"]: a for a in cat["activos"]}
    for r in c["reuso_real"]:
        if r["activo"] in activos:
            activos[r["activo"]].setdefault("usos", []).append({
                "proyecto": datos["nombre"], "componente": nombres[r["componente"]], "reutilizacion_confirmada": r["reutilizado"],
                "procesos_estimados": r["procesos_estimados"], "procesos_cubiertos": r["procesos_cubiertos"]})
    for a in c["activos_nuevos"]:
        cat["activos"].append({
            "id": _siguiente("ACT", [x["id"] for x in cat["activos"]]), "nombre": a["nombre"], "descripcion": a["descripcion"],
            "procesos_que_cubre": a["procesos_que_cubre"], "tecnologias": a["tecnologias"], "estado": "vigente",
            "origen": {"proyecto": datos["nombre"], "componente": nombres[a["componente_origen"]]}, "usos": []})
    return reg, cat, []


if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser(description="Registra un cierre confirmado en el registro de proyectos y en el catálogo de activos.")
    a.add_argument("cierre"); a.add_argument("preparacion"); a.add_argument("linea_base"); a.add_argument("detalle")
    a.add_argument("--registro", required=True); a.add_argument("--catalogo", required=True)
    a.add_argument("--nombre", required=True); a.add_argument("--cliente", required=True)
    a.add_argument("--duracion", required=True, type=float, help="Duración real, en meses")
    a.add_argument("--equipo", nargs="*"); a.add_argument("--fecha")
    a.add_argument("--salida-registro", required=True); a.add_argument("--salida-catalogo", required=True)
    x = a.parse_args()
    leer = lambda r: json.loads(pathlib.Path(r).read_text(encoding="utf-8"))
    reg, cat, errores = registrar(leer(x.cierre), leer(x.preparacion), leer(x.linea_base), leer(x.detalle), leer(x.registro),
                                  leer(x.catalogo), {"nombre": x.nombre, "cliente": x.cliente, "duracion_meses": x.duracion,
                                                     "equipo": x.equipo, "fecha": x.fecha})
    if errores:
        for t in errores: print("ERROR ", t)
        sys.exit(1)
    pathlib.Path(x.salida_registro).write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pathlib.Path(x.salida_catalogo).write_text(json.dumps(cat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Registro: {reg['proyectos'][-1]['id']} agregado en {x.salida_registro}")
    print(f"Catálogo: {len(cat['activos']) - len(leer(x.catalogo)['activos'])} activos nuevos y usos actualizados en {x.salida_catalogo}")
