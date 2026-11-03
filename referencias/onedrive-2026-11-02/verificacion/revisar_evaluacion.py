"""Verificación de una evaluación del nivel de información (uso interno, para revisar salidas del agente).

    errores, avisos = revisar(evaluacion, ficha, sesiones_realizadas, maximo_sesiones_adicionales)

Desde la terminal:
    python revisar_evaluacion.py evaluacion.json ficha.json --sesiones 1 --maximo 1

Recalcula toda la aritmética, revisa el orden y la prioridad de las preguntas, los supuestos, las contradicciones
pendientes y el siguiente paso, y comprueba que ningún puntaje supere el techo que permite su evidencia.
No juzga si el descriptor elegido es el correcto: eso es revisión humana.
"""
import json, pathlib, re
import jsonschema

DIR = pathlib.Path(__file__).resolve().parent
ESQUEMA = json.loads((DIR.parent / "a2_evaluador" / "faed_evaluacion.schema.json").read_text(encoding="utf-8"))
RUBRICA = {c["id"]: c for c in json.loads((DIR / "rubrica_b1.json").read_text(encoding="utf-8"))}
PESOS = {"D1": 12, "D2": 11, "D3": 18, "D4": 15, "D5": 14, "D6": 5, "D7": 5, "D8": 7, "D10": 3}
NUCLEO = ["D1", "D2", "D3", "D4", "D5"]
ESCRITAS_CLIENTE = {"documento_cliente", "historias_usuario", "correo", "otro"}


def _nivel(p):
    return "baja" if p < 40 else "media" if p < 67 else "alta"


def _techo(dato, tipos_fuente):
    # Cota: no se sabe cuál cita es la de la validación; basta con que alguna no sea de una nota interna.
    if dato["confirmado_por_cliente"] and any(tipos_fuente.get(c["fuente"]) != "notas_internas" for c in dato["citas"]):
        return 3
    if dato["afirmado_por"] != "cliente":
        return 1
    return 2 if any(tipos_fuente.get(c["fuente"]) in ESCRITAS_CLIENTE for c in dato["citas"]) else 1


def revisar(ev, ficha, sesiones_realizadas, maximo_sesiones_adicionales):
    errores, avisos = [], []
    try:
        jsonschema.validate(ev, ESQUEMA)
    except jsonschema.ValidationError as e:
        return [f"Formato: {e.message} en {'/'.join(map(str, e.absolute_path))}"], []

    datos = {d["id"]: d for g in ficha.values() if isinstance(g, dict) for l in g.values() for d in l}
    tipos = {f["id"]: f["tipo"] for f in ficha["fuentes"]}
    if [c["id"] for c in ev["criterios"]] != list(RUBRICA):
        errores.append("Los criterios no son los 20 del anexo B.1 en su orden.")
    if [d["id"] for d in ev["dimensiones"]] != list(PESOS):
        errores.append("Las dimensiones no son las 9 evaluadas en su orden.")
    dims = {d["id"]: d for d in ev["dimensiones"]}
    crit = {c["id"]: c for c in ev["criterios"]}

    # Evidencia y techo
    for c in ev["criterios"]:
        d = c["id"].split(".")[0]
        if not dims[d]["aplica"]:
            continue
        for i in c["evidencia"]:
            if i not in datos:
                errores.append(f"{c['id']}: la evidencia {i} no existe en la ficha.")
            elif datos[i]["estado"] != "vigente":
                errores.append(f"{c['id']}: se apoya en {i}, que está descartado.")
        validos = [datos[i] for i in c["evidencia"] if i in datos and datos[i]["estado"] == "vigente"]
        if c["puntaje"] > 0 and not validos:
            errores.append(f"{c['id']}: tiene puntaje {c['puntaje']} sin evidencia en la ficha.")
        techo = 3 if c["id"] == "D6.1" and validos else max((_techo(x, tipos) for x in validos), default=0)
        if c["puntaje"] > techo:
            errores.append(f"{c['id']}: puntaje {c['puntaje']} por encima del techo que permite su evidencia ({techo}).")
        if c["puntaje"] == 3 and c["para_subir"] is not None:
            avisos.append(f"{c['id']}: tiene 3 y aun así indica qué falta.")
        if c["puntaje"] < 3 and not c["para_subir"]:
            errores.append(f"{c['id']}: está por debajo de 3 y no indica qué falta para subir.")

    # Aritmética
    suma_pond, suma_pesos = 0.0, 0
    for d, peso in PESOS.items():
        if d not in dims:
            continue
        if d in NUCLEO and not dims[d]["aplica"]:
            errores.append(f"{d}: es núcleo y no puede excluirse.")
        cs = [c for c in ev["criterios"] if c["id"].split(".")[0] == d]
        obt = sum(c["puntaje"] * RUBRICA[c["id"]]["P"] for c in cs)
        pos = sum(3 * RUBRICA[c["id"]]["P"] for c in cs)
        pct = round(obt / pos * 100, 1)
        x = dims[d]
        if (x["puntos_obtenidos"], x["puntos_posibles"]) != (obt, pos) or abs(x["porcentaje"] - pct) > 0.05:
            errores.append(f"{d}: debía dar {obt}/{pos} = {pct} %, y la evaluación dice {x['puntos_obtenidos']}/{x['puntos_posibles']} = {x['porcentaje']} %.")
        if x["aplica"]:
            suma_pond += peso * (obt / pos * 100)
            suma_pesos += peso
    general = round(suma_pond / suma_pesos, 1)
    calc = ev["calculo"]
    bajos = [d for d in NUCLEO if dims[d]["porcentaje"] < 40]
    nivel_pct = _nivel(general)
    nivel = "media" if nivel_pct == "alta" and bajos else nivel_pct
    if abs(calc["porcentaje_general"] - general) > 0.1:
        errores.append(f"Porcentaje general: debía dar {general} % y dice {calc['porcentaje_general']} %.")
    if calc["suma_pesos"] != suma_pesos:
        errores.append(f"Suma de pesos: debía ser {suma_pesos} y dice {calc['suma_pesos']}.")
    if calc["nivel_por_porcentaje"] != nivel_pct or calc["nivel"] != nivel:
        errores.append(f"Nivel: debía ser {nivel_pct} por porcentaje y {nivel} final; dice {calc['nivel_por_porcentaje']} y {calc['nivel']}.")
    if sorted(calc["nucleo_bajo_40"]) != sorted(bajos) or calc["tope_aplicado"] != (nivel_pct == "alta" and bool(bajos)):
        errores.append("Tope: las dimensiones núcleo bajo 40 % o la aplicación del tope no coinciden con el cálculo.")

    # Dimensiones excluidas
    for d, x in dims.items():
        if not x["aplica"]:
            if not x["motivo_no_aplica"]:
                errores.append(f"{d}: se excluyó sin motivo.")
            else:
                avisos.append(f"{d}: se excluyó por «{x['motivo_no_aplica']}»; confirmar que no aplica y no que falta información.")
            if any(c["puntaje"] for c in ev["criterios"] if c["id"].split(".")[0] == d):
                errores.append(f"{d}: no aplica y tiene criterios con puntaje.")

    # Momento y siguiente paso, a partir de los parámetros
    transcripciones = sum(1 for f in ficha["fuentes"] if f["tipo"] == "transcripcion_sesion")
    if transcripciones and not sesiones_realizadas:
        avisos.append(f"La ficha tiene {transcripciones} transcripciones de sesión y el parámetro dice 0 sesiones realizadas; revisar el parámetro.")
    if ev["version_ficha"] != ficha["version"] or ev["id_solicitud"] != ficha["id_solicitud"]:
        errores.append("La evaluación no corresponde a la solicitud o a la versión de la ficha recibida.")
    momento = "preparacion" if sesiones_realizadas == 0 else "despues_de_sesion"
    if ev["momento"] != momento:
        errores.append(f"Momento: con {sesiones_realizadas} sesiones realizadas debía ser {momento} y dice {ev['momento']}.")
    if momento == "preparacion":
        esperado = "realizar_sesion"
    elif nivel != "baja":
        esperado = "clasificar_componentes"
    else:
        esperado = "sesion_adicional" if sesiones_realizadas - 1 < maximo_sesiones_adicionales else "rango_preliminar_y_fase_de_definicion"
    if ev["siguiente_paso"]["accion"] != esperado:
        errores.append(f"Siguiente paso: debía ser {esperado} y dice {ev['siguiente_paso']['accion']}.")

    # Preguntas: prioridad = puntos que subiría el porcentaje general; orden con desempate núcleo y tope
    posibles = {d: dims[d]["puntos_posibles"] for d in dims}
    tope = calc["tope_aplicado"]
    def clave(cid, prioridad):
        d = cid.split(".")[0]
        return (0 if tope and d in bajos else 1, -round(prioridad, 2), 0 if d in NUCLEO else 1)
    previa = None
    for q in ev["preguntas"]:
        c = crit[q["criterio"]]
        d = c["id"].split(".")[0]
        if not dims[d]["aplica"]:
            errores.append(f"Pregunta {q['orden']}: mejora un criterio de una dimensión que no aplica.")
            continue
        esperada = round((3 - c["puntaje"]) * RUBRICA[c["id"]]["P"] / posibles[d] * PESOS[d] / suma_pesos * 100, 2)
        if c["puntaje"] == 3:
            errores.append(f"Pregunta {q['orden']}: mejora un criterio que ya tiene 3.")
        if abs(q["prioridad"] - esperada) > 0.011:
            errores.append(f"Pregunta {q['orden']}: prioridad {q['prioridad']}; debía ser {esperada}.")
        actual = clave(c["id"], esperada)
        if previa is not None and actual < previa:
            errores.append(f"Pregunta {q['orden']}: no respeta el orden de prioridad.")
        previa = actual
        if re.search(r"\bD\d+\.\d+\b", q["pregunta"]):
            errores.append(f"Pregunta {q['orden']}: incluye un código de FAED en el texto.")
    if sum(1 for q in ev["preguntas"] if q["destinatario"] == "cliente") > 10:
        errores.append("Hay más de diez preguntas para el cliente.")

    # Supuestos y contradicciones
    requeridos = {c["id"] for c in ev["criterios"] if c["puntaje"] <= 1 and dims[c["id"].split(".")[0]]["aplica"]}
    dados = {s["criterio"] for s in ev["supuestos"]}
    if requeridos - dados:
        errores.append(f"Faltan supuestos para: {', '.join(sorted(requeridos - dados))}.")
    abiertas = {k["id"] for k in ficha["contradicciones"] if k["estado"] == "abierta"}
    if abiertas != {k["contradiccion"] for k in ev["contradicciones_pendientes"]}:
        errores.append("Las contradicciones pendientes no coinciden con las abiertas en la ficha.")
    return errores, avisos


if __name__ == "__main__":
    import argparse, sys
    a = argparse.ArgumentParser(description="Verifica una evaluación producida por A2 · Evaluar la información.")
    a.add_argument("evaluacion", help="Evaluación (JSON) que entregó el agente")
    a.add_argument("ficha", help="Ficha (JSON) que recibió el agente")
    a.add_argument("--sesiones", type=int, required=True, help="Sesiones realizadas que recibió el agente")
    a.add_argument("--maximo", type=int, required=True, help="Máximo de sesiones adicionales que recibió el agente")
    x = a.parse_args()
    ev = json.loads(pathlib.Path(x.evaluacion).read_text(encoding="utf-8"))
    ficha = json.loads(pathlib.Path(x.ficha).read_text(encoding="utf-8"))
    errores, avisos = revisar(ev, ficha, x.sesiones, x.maximo)
    for t in errores: print("ERROR ", t)
    for t in avisos: print("AVISO ", t)
    print(f"{len(errores)} errores · {len(avisos)} avisos")
    sys.exit(1 if errores else 0)
