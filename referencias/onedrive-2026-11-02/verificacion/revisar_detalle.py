"""Verificación de la salida de A4 · Detallar.

    errores, avisos = revisar(detalle, ficha, componentes, catalogo, mapa)

Desde la terminal:
    python revisar_detalle.py detalle.json ficha.json componentes.json --catalogo catalogo.json --mapa mapa.json

Comprueba el esquema, que las fichas correspondan a los componentes de A3, que cada reúso se apoye en un activo vigente del
catálogo, que cada factor sin evidencia tenga puntaje 1, que las tecnologías tengan el nivel del mapa (o T3 si no están),
que las interfaces coincidan con la ficha y que la madurez no sea mayor que la que permite la evidencia. Al final calcula
cada componente con las funciones de cálculo y lista las confirmaciones que requiere del Tech lead.
No juzga si cada puntaje es el mejor: eso es revisión humana.
"""
import json, pathlib, re, sys
import jsonschema

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "calculo"))
import faed_calculos as fc

ESQUEMA = json.loads((RAIZ / "a4_detallador" / "faed_detalle_componentes.schema.json").read_text(encoding="utf-8"))
ESCRITAS_CLIENTE = {"documento_cliente", "historias_usuario", "correo", "otro"}
MADUREZ = {3: "validado", 2: "definido", 1: "supuesto", 0: "supuesto"}
ORDEN = ["supuesto", "definido", "validado"]
PROTOCOLOS = {"REST", "SOAP", "MQTT", "ODATA", "GRAPHQL", "GRPC", "SFTP", "FTP", "HTTP", "HTTPS", "AMQP", "JMS", "EDI"}


def _evidencia(dato, tipos, en_contradiccion):
    """3 confirmado por el cliente · 2 escrito por el cliente · 1 dicho, del equipo o en contradicción abierta."""
    if dato["id"] in en_contradiccion:
        return 1
    if dato["confirmado_por_cliente"] and any(tipos.get(c["fuente"]) != "notas_internas" for c in dato["citas"]):
        return 3
    if dato["afirmado_por"] == "cliente" and any(tipos.get(c["fuente"]) in ESCRITAS_CLIENTE for c in dato["citas"]):
        return 2
    return 1


def revisar(det, ficha, comp, catalogo, mapa, valores=None):
    errores, avisos = [], []
    try:
        jsonschema.validate(det, ESQUEMA)
    except jsonschema.ValidationError as e:
        return [f"Formato: {e.message} en {'/'.join(map(str, e.absolute_path))}"], []

    datos = {d["id"]: d for g in ficha.values() if isinstance(g, dict) for l in g.values() for d in l}
    vigentes = {i for i, d in datos.items() if d["estado"] == "vigente"}
    tipos = {f["id"]: f["tipo"] for f in ficha["fuentes"]}
    en_contradiccion = {i for k in ficha["contradicciones"] if k["estado"] == "abierta" for i in k["elementos_relacionados"]}
    activos = {a["id"]: a for a in catalogo["activos"]}
    tecnologias, alias = {}, {}
    for t in mapa["tecnologias"]:
        tecnologias[t["nombre"].lower()] = t["nivel"]
        for x in t.get("alias", []):
            alias[x.lower()] = t["nombre"]
    if not mapa["tecnologias"]:
        avisos.append("El mapa de tecnologías está vacío: toda tecnología quedará en T3 y, sin tecnologías exigidas, el entorno se asume T1.")
    fuera_mapa = {}

    if det["id_solicitud"] != ficha["id_solicitud"] or det["version_ficha"] != ficha["version"]:
        errores.append("La salida no corresponde a la solicitud o a la versión de la ficha recibida.")
    a3 = {c["id"]: c for c in comp["componentes"]}
    if [c["id"] for c in det["componentes"]] != list(a3):
        errores.append("Las fichas no corresponden a los componentes de A3, en el mismo orden.")

    for c in det["componentes"]:
        cid, base = c["id"], a3.get(c["id"])
        if not base:
            continue
        if (c["nombre"], c["arquetipo"]) != (base["nombre"], base["arquetipo"]):
            errores.append(f"{cid}: cambió el nombre o el arquetipo que entregó A3.")
        if [(p["id"], p["nombre"], p["origen"]) for p in c["procesos"]] != [(p["id"], p["nombre"], p["origen"]) for p in base["procesos"]]:
            errores.append(f"{cid}: los procesos no son los que entregó A3.")
            continue

        # Reúso
        for p in c["procesos"]:
            a = p["activo_reutilizado"]
            if a is None:
                if p["justificacion_reuso"] is not None:
                    avisos.append(f"{p['id']}: tiene justificación de reúso sin activo.")
                continue
            if a not in activos:
                errores.append(f"{p['id']}: el activo {a} no existe en el catálogo.")
            elif activos[a]["estado"] != "vigente":
                errores.append(f"{p['id']}: el activo {a} está en estado {activos[a]['estado']} y no cuenta como reúso.")
            if not (p["justificacion_reuso"] or "").strip():
                errores.append(f"{p['id']}: el reúso no tiene justificación.")

        # Complejidad
        sin_evidencia = 0
        for f, x in c["complejidad"].items():
            for i in x["evidencia"]:
                if i not in vigentes:
                    errores.append(f"{cid} · {f}: la evidencia {i} no existe o no está vigente en la ficha.")
            if not x["evidencia"]:
                sin_evidencia += 1
                if x["puntaje"] != 1:
                    errores.append(f"{cid} · {f}: no tiene evidencia y su puntaje es {x['puntaje']}; sin evidencia corresponde 1.")
        if sin_evidencia and len(c["supuestos"]) < sin_evidencia:
            avisos.append(f"{cid}: tiene {sin_evidencia} factores sin evidencia y solo {len(c['supuestos'])} supuestos.")

        # Interfaces
        for i in c["interfaces"]:
            d = datos.get(i["interfaz"])
            if i["interfaz"] not in vigentes or not i["interfaz"].startswith("INT-"):
                errores.append(f"{cid}: la interfaz {i['interfaz']} no existe o no está vigente en la ficha.")
                continue
            if d.get("falla_detiene_operacion") is not None and i["critica"] != d["falla_detiene_operacion"]:
                errores.append(f"{cid}: {i['interfaz']} contradice lo que dice la ficha sobre si su falla detiene la operación.")
            if i["protocolo_conocido"] and not d.get("protocolo"):
                avisos.append(f"{cid}: {i['interfaz']} marca el protocolo como conocido, pero la ficha no lo registra.")

        # Interfaces que A3 asignó al componente de integración
        for i in base.get("interfaces", []):
            if i not in {x["interfaz"] for x in c["interfaces"]}:
                errores.append(f"{cid}: no registra {i}, la interfaz que construye según A3.")

        # Tecnologías
        for t in c["tecnologias"]:
            nivel = tecnologias.get(t["nombre"].lower())
            if t["nombre"].upper() in PROTOCOLOS:
                avisos.append(f"{cid}: {t['nombre']} es un protocolo de intercambio; va en las interfaces, no en las tecnologías.")
            if nivel is None and t["nombre"].lower() in alias:
                errores.append(f"{cid}: {t['nombre']} está en el mapa como {alias[t['nombre'].lower()]}; use ese nombre.")
                continue
            if not t["en_mapa"]:
                fuera_mapa.setdefault(t["nombre"], []).append(cid)
            if t["en_mapa"] and nivel is None:
                errores.append(f"{cid}: {t['nombre']} dice estar en el mapa de tecnologías y no está.")
            elif t["en_mapa"] and t["nivel"] != nivel:
                errores.append(f"{cid}: {t['nombre']} tiene nivel {t['nivel']} y el mapa dice {nivel}.")
            elif not t["en_mapa"] and nivel is not None:
                errores.append(f"{cid}: {t['nombre']} está en el mapa con nivel {nivel}.")
            elif not t["en_mapa"] and t["nivel"] != "T3":
                errores.append(f"{cid}: {t['nombre']} no está en el mapa; corresponde T3 y dice {t['nivel']}.")

        # Madurez: el proceso más débil
        niveles = []
        for p in base["procesos"]:
            if p["origen"] == "inferido":
                niveles.append(1)
            else:
                ev = [_evidencia(datos[i], tipos, en_contradiccion) for i in p["datos_ficha"] if i in datos]
                niveles.append(min(ev) if ev else 1)
        esperada = MADUREZ[min(niveles)]
        if ORDEN.index(c["madurez"]) > ORDEN.index(esperada):
            errores.append(f"{cid}: madurez {c['madurez']}; la evidencia permite como máximo {esperada}.")
        elif c["madurez"] != esperada:
            avisos.append(f"{cid}: madurez {c['madurez']}, más conservadora que la que permite la evidencia ({esperada}).")

        # Vacíos
        for v in c["vacios"]:
            if re.search(r"\b(D\d+\.\d+|C\d{2}(-P\d{2})?|PF-\d+|INT-\d+|ACT-\d+|REU-\d+)\b", v["pregunta"]):
                errores.append(f"{cid}: una pregunta incluye códigos internos: «{v['pregunta'][:60]}».")

    # Cálculo y confirmaciones, agrupadas
    if not errores:
        v = valores or fc.cargar_valores()
        for r in (fc.calcular_componente(x, v) for x in fc.componentes_desde_detalle(det)):
            for k in r["confirmaciones"]:
                if not k.startswith("tecnologías fuera del mapa"):
                    avisos.append(f"{r['id']}: requiere confirmación del Tech lead por {k}.")
        for nombre, cs in fuera_mapa.items():
            avisos.append(f"{nombre} no está en el mapa de tecnologías (lo usan {', '.join(cs)}): el Tech lead confirma su nivel una sola vez.")
    return errores, avisos


if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser(description="Verifica la salida de A4 · Detallar.")
    a.add_argument("detalle"); a.add_argument("ficha"); a.add_argument("componentes")
    a.add_argument("--catalogo", required=True); a.add_argument("--mapa", required=True)
    x = a.parse_args()
    leer = lambda r: json.loads(pathlib.Path(r).read_text(encoding="utf-8"))
    errores, avisos = revisar(leer(x.detalle), leer(x.ficha), leer(x.componentes), leer(x.catalogo), leer(x.mapa))
    for t in errores: print("ERROR ", t)
    for t in avisos: print("AVISO ", t)
    print(f"{len(errores)} errores · {len(avisos)} avisos")
    sys.exit(1 if errores else 0)
