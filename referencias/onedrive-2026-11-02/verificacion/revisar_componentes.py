"""Verificación de la salida de A3 · Dividir.

    errores, avisos = revisar(componentes, ficha, tipo_estimacion, evaluacion=None, carril_rapido=False)

Desde la terminal:
    python revisar_componentes.py componentes.json ficha.json --tipo formal [--evaluacion evaluacion.json] [--carril-rapido]

Comprueba el esquema, que cada proceso funcional vigente de la ficha quede en un componente una sola vez o con su motivo,
que los datos citados existan y estén vigentes, que cada proceso inferido tenga justificación y supuesto, que las
interfaces y migraciones de la ficha tengan componente o motivo y que ningún componente sea de talla XL. Si recibe la
evaluación, comprueba además que cada separación por riesgo, regulación u homogeneidad tenga evidencia de 2 o más y que
la profundidad (talla probable, familias de criterios) corresponda al nivel de información.
No juzga si la agrupación o el arquetipo son los mejores: eso es revisión humana.
"""
import json, pathlib, re
import jsonschema

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ESQUEMA = json.loads((RAIZ / "a3_divisor" / "faed_componentes.schema.json").read_text(encoding="utf-8"))

# Criterio de la evaluación (anexo B.1) que debe tener 2 o más para hacer cada separación
EVIDENCIA = {"CR-01": ("D7.1", "D4.4", "D5.3"), "CR-02": ("D1.2",), "CR-03": ("D10.1",), "CH-01": ("D7.1",),
             "CH-02": ("D6.1",), "CH-03": ("D4.4",), "CH-04": ("D2.2",)}
TALLAS = ["XS", "S", "M", "L", "XL"]


def _datos(ficha):
    return {d["id"]: d for g in ficha.values() if isinstance(g, dict) for l in g.values() for d in l}


def revisar(comp, ficha, tipo_estimacion, evaluacion=None, carril_rapido=False):
    errores, avisos = [], []
    try:
        jsonschema.validate(comp, ESQUEMA)
    except jsonschema.ValidationError as e:
        return [f"Formato: {e.message} en {'/'.join(map(str, e.absolute_path))}"], []

    datos = _datos(ficha)
    vigentes = {i for i, d in datos.items() if d["estado"] == "vigente"}
    if comp["id_solicitud"] != ficha["id_solicitud"] or comp["version_ficha"] != ficha["version"]:
        errores.append("La salida no corresponde a la solicitud o a la versión de la ficha recibida.")
    if comp["tipo_estimacion"] != tipo_estimacion:
        errores.append(f"Tipo de estimación: se recibió {tipo_estimacion} y la salida dice {comp['tipo_estimacion']}.")
    if tipo_estimacion == "preliminar" and not comp["advertencias"]:
        avisos.append("La estimación es preliminar y no hay ninguna advertencia sobre la información incompleta.")

    asignados = {}
    supuestos_por_comp = {s["componente"] for s in comp["supuestos"]}
    for n, c in enumerate(comp["componentes"], 1):
        cid = c["id"]
        if cid != f"C{n:02d}":
            errores.append(f"{cid}: los componentes se numeran en orden (se esperaba C{n:02d}).")
        if not c["procesos"]:
            errores.append(f"{cid}: componente sin procesos.")
        if len(c["procesos"]) > 60:
            errores.append(f"{cid}: tiene {len(c['procesos'])} procesos (talla XL); debe dividirse.")
        for k, p in enumerate(c["procesos"], 1):
            if p["id"] != f"{cid}-P{k:02d}":
                errores.append(f"{p['id']}: los procesos se numeran en orden dentro del componente (se esperaba {cid}-P{k:02d}).")
            for i in p["datos_ficha"]:
                if i not in datos:
                    errores.append(f"{p['id']}: cita {i}, que no existe en la ficha.")
                elif i not in vigentes:
                    errores.append(f"{p['id']}: se apoya en {i}, que está descartado.")
            if p["origen"] == "ficha":
                if not p["datos_ficha"]:
                    errores.append(f"{p['id']}: dice salir de la ficha y no cita ningún dato.")
                if p["justificacion"] is not None:
                    avisos.append(f"{p['id']}: tiene justificación aunque su origen es la ficha.")
                for i in p["datos_ficha"]:
                    if i.startswith("PF-"):
                        asignados.setdefault(i, []).append(p["id"])
            else:
                if not (p["justificacion"] or "").strip():
                    errores.append(f"{p['id']}: es inferido y no explica por qué la solución lo necesita.")
                if cid not in supuestos_por_comp:
                    errores.append(f"{p['id']}: es inferido y su componente no tiene ningún supuesto.")
                avisos.append(f"{p['id']}: proceso inferido «{p['nombre']}»; confirmar que la solución lo necesita.")
        for i in c["interfaces"]:
            if i not in vigentes or not i.startswith("INT-"):
                errores.append(f"{cid}: la interfaz {i} no existe o no está vigente en la ficha.")
        if c["arquetipo"] == "integracion" and not c["interfaces"]:
            avisos.append(f"{cid}: es de integración y no cubre ninguna interfaz de la ficha.")
        if c["arquetipo"] == "integracion" and len(c["interfaces"]) > 1:
            errores.append(f"{cid}: agrupa {len(c['interfaces'])} interfaces; cada interfaz que requiere un conector es un componente de integración aparte.")

    # Cada proceso funcional vigente, en un solo lugar
    sin_asignar = {x["dato"]: x["motivo"] for x in comp["procesos_sin_asignar"]}
    for i in sin_asignar:
        if i not in vigentes or not i.startswith("PF-"):
            errores.append(f"Sin asignar: {i} no es un proceso funcional vigente de la ficha.")
    for pf in sorted(i for i in vigentes if i.startswith("PF-")):
        lugares = asignados.get(pf, [])
        if len(lugares) > 1:
            errores.append(f"{pf}: está en más de un proceso ({', '.join(lugares)}); se contaría dos veces.")
        if lugares and pf in sin_asignar:
            errores.append(f"{pf}: está asignado y también aparece sin asignar.")
        if not lugares and pf not in sin_asignar:
            errores.append(f"{pf}: no quedó en ningún componente ni en los procesos sin asignar.")

    # Interfaces y migraciones de la ficha con su componente
    cubiertas = {i for c in comp["componentes"] for i in c["interfaces"]}
    dependencias = {}
    for x in comp["dependencias_sin_componente"]:
        i = x["interfaz"]
        if i not in vigentes or not i.startswith("INT-"):
            errores.append(f"Dependencia sin componente: {i} no es una interfaz vigente de la ficha.")
        elif i in cubiertas:
            errores.append(f"{i}: tiene componente de integración y también aparece como dependencia sin componente.")
        elif not x["motivo"].strip():
            errores.append(f"{i}: está como dependencia sin componente y no dice por qué.")
        dependencias[i] = x["motivo"]
    for i in sorted(v for v in vigentes if v.startswith("INT-")):
        if i not in cubiertas and i not in dependencias:
            avisos.append(f"{i}: la interfaz no tiene componente de integración; confirmar que no requiere conector.")
    citados = {i for c in comp["componentes"] if c["arquetipo"] == "modernizacion" for p in c["procesos"] for i in p["datos_ficha"]}
    for i in sorted(v for v in vigentes if v.startswith("MIG-")):
        if i not in citados:
            avisos.append(f"{i}: la migración de datos no tiene componente de modernización.")

    # Profundidad y evidencia de las separaciones, según la evaluación (o el carril rápido)
    nivel = "baja" if carril_rapido else (evaluacion or {}).get("calculo", {}).get("nivel")
    puntajes = {c["id"]: c["puntaje"] for c in (evaluacion or {}).get("criterios", [])}
    for c in comp["componentes"]:
        cid, criterios = c["id"], c["criterios_aplicados"]
        if not criterios:
            avisos.append(f"{cid}: no registra los criterios de división que lo originaron.")
        if evaluacion is not None:
            for k in criterios:
                if k in EVIDENCIA and not any(puntajes.get(d, 0) >= 2 for d in EVIDENCIA[k]):
                    errores.append(f"{cid}: aplica {k} sin evidencia; {' o '.join(EVIDENCIA[k])} debe tener 2 o más en la evaluación.")
        if nivel == "baja":
            otros = [k for k in criterios if k in EVIDENCIA and k != "CR-01"]
            if otros:
                avisos.append(f"{cid}: con información baja solo se aplican los criterios estructurales y CR-01; aplica {', '.join(otros)}.")
            if c["talla_probable"] is None:
                avisos.append(f"{cid}: con información baja o en carril rápido, el candidato debe indicar su talla probable.")
        elif nivel in ("media", "alta") and c["talla_probable"] is not None:
            avisos.append(f"{cid}: indica talla probable aunque la información es {nivel}; debería ser null.")
        if c["talla_probable"] is not None:
            n = len(c["procesos"])
            por_conteo = "XS" if n <= 5 else "S" if n <= 15 else "M" if n <= 30 else "L" if n <= 60 else "XL"
            if TALLAS.index(c["talla_probable"]) > TALLAS.index(por_conteo):
                avisos.append(f"{cid}: su talla probable es {c['talla_probable']}, pero sus {n} procesos listados dan {por_conteo}; "
                              "las horas saldrán de lo listado y pueden quedar cortas.")
    return errores, avisos


if __name__ == "__main__":
    import argparse, sys
    a = argparse.ArgumentParser(description="Verifica la salida de A3 · Dividir.")
    a.add_argument("componentes"); a.add_argument("ficha")
    a.add_argument("--tipo", choices=["formal", "preliminar"], required=True, help="Tipo de estimación que recibió el agente")
    a.add_argument("--evaluacion", help="Evaluación de A2 que recibió el agente; con ella se revisa la evidencia de las separaciones")
    a.add_argument("--carril-rapido", action="store_true", help="La solicitud fue por el carril rápido")
    x = a.parse_args()
    leer = lambda r: json.loads(pathlib.Path(r).read_text(encoding="utf-8"))
    errores, avisos = revisar(leer(x.componentes), leer(x.ficha), x.tipo,
                              leer(x.evaluacion) if x.evaluacion else None, x.carril_rapido)
    for t in errores: print("ERROR ", t)
    for t in avisos: print("AVISO ", t)
    print(f"{len(errores)} errores · {len(avisos)} avisos")
    sys.exit(1 if errores else 0)
