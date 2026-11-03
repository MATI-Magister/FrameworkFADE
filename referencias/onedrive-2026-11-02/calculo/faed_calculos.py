"""Funciones de cálculo de FAED: código, sin inteligencia artificial.

Los agentes entregan juicios (procesos, factores, niveles); estas funciones calculan los números con los valores del
método vigentes, para que cada resultado sea reproducible y auditable. Las reglas siguen el documento del framework:
sección 4 (talla, complejidad, reúso), sección 6 (esfuerzo, precio y modalidades), sección 7 (ruta) y anexo B.2
(experiencia).

Uso desde la terminal (opcional antes de la acción: --valores otra_version.json):
    python faed_calculos.py componentes detalle.json                       # horas de cada componente (salida de A4)
    python faed_calculos.py preparar detalle.json --registro registro.json     # lo que recibe A5
    python faed_calculos.py escenario detalle.json juicio_a5.json --registro registro.json --nivel-informacion media --experiencia-equipo 2
    python faed_calculos.py estimar entrada.json                           # desde componentes ya clasificados
    python faed_calculos.py cierre linea_base.json --jira horas.csv [--cambios cambios.json]   # lo que recibe A7
    python faed_calculos.py desviacion cierre.json                         # desviación desde horas ya consolidadas
    python faed_calculos.py indicadores registro.json --catalogo catalogo.json   # indicadores y disparador de recalibración
"""
import json, math, pathlib, sys

DIR = pathlib.Path(__file__).resolve().parent
NIVELES = ["baja", "media", "alta"]
FACTORES = ["reglas", "arquitectura", "seguridad", "procesamiento", "dependencias"]


def cargar_valores(ruta=None):
    return json.loads(pathlib.Path(ruta or DIR / "valores_metodo.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- escalas (sección 4 y anexo A)
def talla(procesos):
    if procesos < 1:
        raise ValueError("Un componente tiene al menos un proceso funcional.")
    return "XS" if procesos <= 5 else "S" if procesos <= 15 else "M" if procesos <= 30 else "L" if procesos <= 60 else "XL"


def nivel_reuso(porcentaje):
    """R1 menos de 10 % · R2 de 10 % a menos de 30 % · R3 de 30 % a 50 % · R4 más de 50 %."""
    return "R1" if porcentaje < 10 else "R2" if porcentaje < 30 else "R3" if porcentaje <= 50 else "R4"


def nivel_complejidad(puntos):
    """Suma de cinco factores de 0 a 2: 0 a 2 baja · 3 a 5 media · 6 a 8 alta · 9 a 10 muy alta."""
    return "baja" if puntos <= 2 else "media" if puntos <= 5 else "alta" if puntos <= 8 else "muy_alta"


def nivel_integracion(interfaces):
    """I0 sin interfaces · I1 1 a 2 simples · I2 3 a 5 o alguna compleja ·
    I3 más de 5, alguna crítica (su falla detiene la operación principal del cliente) o con protocolo desconocido."""
    n = len(interfaces)
    if n == 0:
        return "I0"
    if n > 5 or any(i.get("critica") is True for i in interfaces) or any(not i.get("protocolo_conocido", True) for i in interfaces):
        return "I3"
    if n >= 3 or any(i.get("compleja") for i in interfaces):
        return "I2"
    return "I1"


def nivel_entorno(tecnologias):
    """El entorno del componente es el de su tecnología menos conocida. Si el cliente no exige ninguna tecnología,
    la empresa usa las que conoce: T1."""
    return max((t["nivel"] for t in tecnologias), default="T1", key=["T1", "T2", "T3", "T4"].index)


# ---------------------------------------------------------------- componente (sección 6, esfuerzo)
def calcular_componente(c, v):
    """c: {id, nombre, arquetipo, procesos, entorno, integracion,
           factores_complejidad {reglas..dependencias: 0-2}  o  complejidad (nivel),
           procesos_reutilizados (número)  o  reuso (nivel)}"""
    if c["arquetipo"] not in v["horas_por_proceso"]:
        raise ValueError(f"{c.get('id')}: arquetipo desconocido '{c['arquetipo']}'.")
    procesos = int(c["procesos"])
    r = {k: c[k] for k in ("id", "nombre", "arquetipo") if k in c}
    r["procesos"] = procesos
    r["talla"] = talla(procesos)
    r["debe_dividirse"] = r["talla"] == "XL"

    if "factores_complejidad" in c:
        f = c["factores_complejidad"]
        faltan = [k for k in FACTORES if k not in f]
        if faltan or any(f[k] not in (0, 1, 2) for k in FACTORES):
            raise ValueError(f"{c.get('id')}: los cinco factores de complejidad van de 0 a 2 (faltan o sobran: {faltan}).")
        r["complejidad_puntos"] = sum(f[k] for k in FACTORES)
        r["complejidad"] = nivel_complejidad(r["complejidad_puntos"])
    else:
        r["complejidad"] = c["complejidad"]

    if "procesos_reutilizados" in c:
        reus = int(c["procesos_reutilizados"])
        if not 0 <= reus <= procesos:
            raise ValueError(f"{c.get('id')}: los procesos reutilizados van de 0 al total de procesos.")
        r["reuso_porcentaje"] = round(reus / procesos * 100, 1)
        r["reuso"] = nivel_reuso(reus / procesos * 100)
    else:
        r["reuso"] = c.get("reuso", "R1")

    r["entorno"] = nivel_entorno(c["tecnologias"]) if "tecnologias" in c else c["entorno"]
    r["integracion"] = nivel_integracion(c["interfaces"]) if "interfaces" in c else c.get("integracion")
    r["confirmaciones"] = []
    if r.get("reuso_porcentaje", 0) >= 30 or r["reuso"] in ("R3", "R4"):
        r["confirmaciones"].append("reúso de 30 % o más")
    fuera = [t["nombre"] for t in c.get("tecnologias", []) if not t.get("en_mapa", True)]
    if fuera:
        r["confirmaciones"].append("tecnologías fuera del mapa: " + ", ".join(fuera))
    r["horas_base"] = procesos * v["horas_por_proceso"][c["arquetipo"]]
    r["factores"] = {"complejidad": v["factor_complejidad"][r["complejidad"]],
                     "entorno": v["factor_entorno"][r["entorno"]],
                     "reuso": v["factor_reuso"][r["reuso"]]}
    r["horas"] = round(r["horas_base"] * r["factores"]["complejidad"] * r["factores"]["entorno"] * r["factores"]["reuso"], 1)
    r["version_valores"] = v["version"]
    return r


def componentes_desde_detalle(detalle):
    """Convierte la salida de A4 · Detallar en la entrada de calcular_componente."""
    salida = []
    for c in detalle["componentes"]:
        salida.append({
            "id": c["id"], "nombre": c["nombre"], "arquetipo": c["arquetipo"],
            "procesos": len(c["procesos"]),
            "procesos_reutilizados": sum(1 for p in c["procesos"] if p["activo_reutilizado"]),
            "factores_complejidad": {k: c["complejidad"][k]["puntaje"] for k in FACTORES},
            "tecnologias": c["tecnologias"], "interfaces": c["interfaces"],
        })
    return salida


ARQUETIPOS = ["aplicaciones", "integracion", "datos_ia", "plataforma", "seguridad", "modernizacion"]


def participacion_arquetipos(componentes, v, campo="horas"):
    """Participación de cada arquetipo en las horas. El principal es el de más horas; ante un empate exacto, el de más
    procesos y, si persiste, el primero en el orden del catálogo de arquetipos."""
    total = sum(c[campo] for c in componentes)
    horas, procesos = {}, {}
    for c in componentes:
        horas[c["arquetipo"]] = horas.get(c["arquetipo"], 0) + c[campo]
        procesos[c["arquetipo"]] = procesos.get(c["arquetipo"], 0) + c.get("procesos", 0)
    orden = sorted(horas, key=lambda a: (-horas[a], -procesos[a], ARQUETIPOS.index(a)))
    part = {k: round(horas[k] / total, 3) for k in orden}
    principal = orden[0]
    secundarios = [k for k in orden[1:] if part[k] >= v["umbral_arquetipo_secundario"]]
    return part, principal, secundarios


def casi_empate(part, principal, v):
    """Arquetipos cuya participación queda a menos del margen de casi empate del principal."""
    margen = v.get("margen_casi_empate_arquetipo", 0.05)
    return [k for k, p in part.items() if k != principal and part[principal] - p < margen]


# ---------------------------------------------------------------- experiencia y confianza (anexo B.2, sección 5)
def calcular_experiencia(e):
    """e: {comparables, datos_comparables (0-3), experiencia_equipo (0-3), entorno_principal (T1-T4),
           proyectos_con_secundarios: {arquetipo: número}}"""
    n = int(e["comparables"])
    p_comp = 0 if n <= 1 else 1 if n <= 3 else 2 if n <= 7 else 3
    p_ent = {"T4": 0, "T3": 1, "T2": 2, "T1": 3}[e["entorno_principal"]]
    puntos = [p_comp, int(e["datos_comparables"]), int(e["experiencia_equipo"]), p_ent]
    pct = round(sum(puntos) / 12 * 100, 1)
    nivel = "baja" if pct < 40 else "media" if pct < 70 else "alta"
    motivos = []
    if n <= 1:
        nivel = "baja"; motivos.append("cero o un proyecto comparable")
    limitantes = [a for a, k in (e.get("proyectos_con_secundarios") or {}).items() if k <= 1]
    if nivel == "alta" and limitantes:
        nivel = "media"; motivos.append("cero o un proyecto con componentes de: " + ", ".join(limitantes))
    return {"puntos": puntos, "porcentaje": pct, "nivel": nivel, "ajustes": motivos}


def confianza(nivel_informacion, nivel_experiencia):
    return min(nivel_informacion, nivel_experiencia, key=NIVELES.index)


# ---------------------------------------------------------------- escenario (sección 6)
def escenario(componentes, nivel_confianza, v):
    subtotal = round(sum(c["horas"] for c in componentes), 1)
    gestion = round(subtotal * v["gestion_y_acompanamiento"], 1)
    esperado = subtotal + gestion
    a = v["amplitud_rango"][nivel_confianza]
    sin_redondear = {"optimista": esperado * (1 + a["optimista"]), "esperado": esperado, "pesimista": esperado * (1 + a["pesimista"])}
    return {"subtotal_componentes": subtotal, "gestion": gestion, "confianza": nivel_confianza,
            "horas": {k: round(h) for k, h in sin_redondear.items()},
            "horas_sin_redondear": {k: round(h, 2) for k, h in sin_redondear.items()}}


# ---------------------------------------------------------------- precio (sección 6, presentación comercial)
def precios(esc, v, horas_bloque=None):
    if v.get("costo_por_hora") is None or v.get("margen_objetivo") is None:
        return {"nota": "Faltan el costo por hora o el margen objetivo en los valores del método."}
    ph = v["costo_por_hora"] / (1 - v["margen_objetivo"])
    h, hs = esc["horas"], esc["horas_sin_redondear"]
    sprints = math.ceil(hs["esperado"] / v["capacidad_sprint_horas"] * 2) / 2
    r = {"precio_por_hora": round(ph),
         "escenarios": {k: round(h[k] * ph) for k in h},
         "bolsa_de_horas": round(h["esperado"] * ph),
         "sprints": {"numero": sprints, "horas_cobradas": sprints * v["capacidad_sprint_horas"],
                     "precio_por_sprint": round(v["capacidad_sprint_horas"] * ph),
                     "precio": round(sprints * v["capacidad_sprint_horas"] * ph)}}
    if esc["confianza"] == "baja":
        r["precio_fijo"] = {"precio": None, "nota": "Con confianza baja, solo la dirección puede autorizar un precio fijo."}
    else:
        base = (hs["esperado"] + hs["pesimista"]) / 2
        r["precio_fijo"] = {"horas_base": round(base, 1), "precio": round(base * ph)}
    if horas_bloque is not None:
        b = v["bloque_de_trabajo_horas"]
        r["primer_bloque"] = {"horas": horas_bloque, "precio": round(horas_bloque * ph),
                              "dentro_del_tamano": b["minimo"] <= horas_bloque <= b["maximo"]}
    return r


# ---------------------------------------------------------------- ruta (sección 7)
def ruta(componentes, esc, prec, nivel_experiencia, v, modalidad=None, cliente_estrategico=False, infraestructura=0,
         nivel_informacion=None):
    """Ruta de validación (sección 7). Un rango preliminar (información baja) no es una propuesta formal: lo revisa el
    validador y las señales quedan como advertencias. Sin umbrales definidos, la ruta estándar es provisional."""
    tecnicos, comerciales, pendientes = [], [], []
    if nivel_experiencia == "baja":
        tecnicos.append("experiencia baja")
    for c in componentes:
        if c["entorno"] == "T4": tecnicos.append(f"{c.get('id')}: tecnología experimental (T4)")
        if c["complejidad"] == "muy_alta": tecnicos.append(f"{c.get('id')}: complejidad muy alta")
        if c.get("integracion") == "I3": tecnicos.append(f"{c.get('id')}: integración I3")
    ue = v.get("umbral_esfuerzo_ruta_compleja")
    if ue is None: pendientes.append("umbral de esfuerzo")
    elif esc["horas"]["esperado"] > ue: tecnicos.append("horas esperadas sobre el umbral de esfuerzo")
    uv = v.get("umbral_valor_ruta_compleja")
    if uv is None: pendientes.append("umbral de valor")
    elif "escenarios" in prec:
        valor = (prec["precio_fijo"]["precio"] if modalidad == "precio_fijo" and prec["precio_fijo"]["precio"] else prec["escenarios"]["esperado"]) + infraestructura
        if valor > uv: comerciales.append("precio sobre el umbral de valor")
    if cliente_estrategico:
        comerciales.append("cliente estratégico")
    if nivel_informacion == "baja":
        return {"ruta": "preliminar", "motivos": [], "senales": tecnicos + comerciales, "decide": "Validador",
                "provisional": False, "umbrales_sin_definir": pendientes,
                "nota": "Rango preliminar: no es una propuesta formal. Las señales se revisan al emitir la propuesta formal."}
    compleja = bool(tecnicos or comerciales)
    provisional = not compleja and bool(pendientes)
    if compleja:
        decide = "CEO, con la validación técnica del CIO" if comerciales else "CIO"
    else:
        decide = "Validador" + (", con confirmación de la dirección mientras no estén definidos los umbrales" if provisional else "")
    return {"ruta": "compleja" if compleja else "estandar", "motivos": tecnicos + comerciales, "senales": [], "decide": decide,
            "provisional": provisional, "umbrales_sin_definir": pendientes,
            "nota": ("Sin umbrales definidos no se puede descartar que el precio o las horas exijan la ruta compleja." if provisional else "")}


# ---------------------------------------------------------------- comparables y primer bloque (A5)
TALLAS = ["XS", "S", "M", "L", "XL"]


def talla_registrada(p):
    """Talla de un proyecto del registro: la de sus procesos medidos o, si no se midieron, la aproximada."""
    return talla(p["procesos"]) if p.get("procesos") else p.get("talla")


def puntaje_datos(p):
    """Anexo B.2, datos registrados de un comparable. 3: horas reales, duración, tamaño medido y equipo ·
    2: horas reales, duración y talla aproximada · 1: solo horas reales o solo duración · 0: incompletos."""
    h, d = p.get("horas_reales") is not None, p.get("duracion_meses") is not None
    if h and d and p.get("procesos") and p.get("equipo"):
        return 3
    if h and d and talla_registrada(p):
        return 2
    return 1 if (h or d) else 0


def procesos_con_horas(detalle, comps, v):
    """Horas de cada proceso, con su parte de gestión y acompañamiento: las horas del componente repartidas entre sus procesos."""
    horas = {c["id"]: c["horas"] / c["procesos"] for c in comps}
    return [{"id": p["id"], "componente": c["id"], "nombre": p["nombre"],
             "horas": round(horas[c["id"]] * (1 + v["gestion_y_acompanamiento"]), 1)}
            for c in detalle["componentes"] for p in c["procesos"]]


def preparar_a5(detalle, registro, v):
    """Lo que recibe A5: el proyecto ya calculado, los proyectos candidatos a comparables y las horas de cada proceso.
    Candidato: proyecto del registro del mismo arquetipo principal, de talla igual o adyacente y con horas reales. Si otro
    arquetipo queda a menos del margen de casi empate del principal, también son candidatos los proyectos de ese arquetipo."""
    comps = [calcular_componente(c, v) for c in componentes_desde_detalle(detalle)]
    part, principal, secundarios = participacion_arquetipos(comps, v)
    empate = casi_empate(part, principal, v)
    procesos = sum(c["procesos"] for c in comps)
    t = talla(procesos)
    k = TALLAS.index(t)
    adyacentes = TALLAS[max(k - 1, 0): k + 2]
    ejecutados = registro["proyectos"]
    cand = [{"id": p["id"], "nombre": p["nombre"], "descripcion": p.get("descripcion", ""), "arquetipo_principal": p["arquetipo_principal"],
             "talla": talla_registrada(p), "componentes": [c["nombre"] for c in p.get("componentes", [])], "horas_reales": p["horas_reales"],
             "puntaje_datos": puntaje_datos(p)}
            for p in ejecutados
            if p.get("arquetipo_principal") in [principal] + empate and talla_registrada(p) in adyacentes and p.get("horas_reales") is not None]
    con_sec = {a: sum(1 for p in ejecutados
                      if p.get("arquetipo_principal") == a or any(c["arquetipo"] == a for c in p.get("componentes", [])))
               for a in secundarios}
    return {"proyecto": {"procesos": procesos, "talla": t, "arquetipo_principal": principal, "arquetipos_secundarios": secundarios,
                         "arquetipos_en_casi_empate": empate,
                         "participacion": part, "horas_componentes": {c["id"]: c["horas"] for c in comps}},
            "candidatos": cand, "proyectos_con_secundarios": con_sec,
            "procesos": procesos_con_horas(detalle, comps, v),
            "bloque_de_trabajo_horas": v["bloque_de_trabajo_horas"], "version_valores": v["version"]}


def horas_bloque(ids_procesos, detalle, comps, v):
    """Horas del primer bloque: la suma de las horas de sus procesos, con su parte de gestión y acompañamiento."""
    horas = {c["id"]: c["horas"] / c["procesos"] for c in comps}
    por_id = {p["id"]: horas[c["id"]] for c in detalle["componentes"] for p in c["procesos"]}
    faltan = [i for i in ids_procesos if i not in por_id]
    if faltan:
        raise ValueError("Procesos del bloque que no existen: " + ", ".join(faltan))
    return round(sum(por_id[i] for i in set(ids_procesos)) * (1 + v["gestion_y_acompanamiento"]), 1)


def estimar_escenario(detalle, juicio, registro, nivel_informacion, experiencia_equipo, v,
                      modalidad=None, cliente_estrategico=False, infraestructura=0):
    """Escenario completo a partir de la salida de A4, los juicios de A5 y el registro de proyectos.
    experiencia_equipo (0-3) la responde el Tech lead."""
    comps = [calcular_componente(c, v) for c in componentes_desde_detalle(detalle)]
    prep = preparar_a5(detalle, registro, v)
    elegidos = {x["proyecto"] for x in juicio["comparables"] if x["es_comparable"]}
    puntajes = [c["puntaje_datos"] for c in prep["candidatos"] if c["id"] in elegidos]
    principal = prep["proyecto"]["arquetipo_principal"]
    exp = {"comparables": len(puntajes), "datos_comparables": min(puntajes) if puntajes else 0,
           "experiencia_equipo": experiencia_equipo,
           "entorno_principal": nivel_entorno([{"nivel": c["entorno"]} for c in comps if c["arquetipo"] == principal]),
           "proyectos_con_secundarios": prep["proyectos_con_secundarios"]}
    ids = juicio["primer_bloque"]["procesos"]
    r = estimar({"componentes": comps_a_entrada(comps), "nivel_informacion": nivel_informacion, "experiencia": exp,
                 "horas_primer_bloque": horas_bloque(ids, detalle, comps, v) if ids else None, "modalidad": modalidad,
                 "cliente_estrategico": cliente_estrategico, "infraestructura_y_licencias": infraestructura}, v)
    r["id_solicitud"], r["version_ficha"] = detalle["id_solicitud"], detalle["version_ficha"]
    r["experiencia"]["respuestas"] = exp
    r["comparables"] = sorted(elegidos)
    r["confirmaciones"] = [f"{c['id']}: {k}" for c in comps for k in c["confirmaciones"]]
    return r


def comps_a_entrada(comps):
    """Componentes ya calculados, en el formato de entrada de calcular_componente (con sus niveles)."""
    return [{"id": c["id"], "nombre": c.get("nombre"), "arquetipo": c["arquetipo"], "procesos": c["procesos"],
             "complejidad": c["complejidad"], "reuso": c["reuso"], "entorno": c["entorno"], "integracion": c["integracion"]}
            for c in comps]


# ---------------------------------------------------------------- estimación completa
def estimar(entrada, v):
    """entrada: {nivel_informacion, experiencia, componentes | detalle (salida de A4), horas_primer_bloque, modalidad,
    cliente_estrategico, infraestructura_y_licencias}"""
    base = componentes_desde_detalle(entrada["detalle"]) if "detalle" in entrada else entrada["componentes"]
    comps = [calcular_componente(c, v) for c in base]
    part, principal, secundarios = participacion_arquetipos(comps, v)
    exp = calcular_experiencia(entrada["experiencia"])
    conf = confianza(entrada["nivel_informacion"], exp["nivel"])
    esc = escenario(comps, conf, v)
    prec = precios(esc, v, entrada.get("horas_primer_bloque"))
    rt = ruta(comps, esc, prec, exp["nivel"], v, entrada.get("modalidad"), entrada.get("cliente_estrategico", False),
              entrada.get("infraestructura_y_licencias", 0), entrada["nivel_informacion"])
    return {"version_valores": v["version"], "componentes": comps,
            "arquetipos": {"participacion": part, "principal": principal, "secundarios": secundarios},
            "experiencia": exp, "nivel_informacion": entrada["nivel_informacion"], "confianza": conf,
            "escenario": esc, "precios": prec, "ruta": rt,
            "modalidad": entrada.get("modalidad"), "infraestructura_y_licencias": entrada.get("infraestructura_y_licencias", 0)}


# ---------------------------------------------------------------- desviación (sección 8, cierre y aprendizaje)
def desviacion(cierre):
    """cierre: {componentes: [{id, horas_esperadas, horas_reales, horas_cambios_alcance}], gestion: {...}, umbral_causa}"""
    def d(x):
        base = x["horas_esperadas"] + x.get("horas_cambios_alcance", 0)
        return {**x, "linea_base_ajustada": round(base, 1), "desviacion": round((x["horas_reales"] - base) / base, 3)}
    comps = [d(c) for c in cierre["componentes"]]
    partes = comps + ([d(cierre["gestion"])] if "gestion" in cierre else [])
    total_base = sum(p["linea_base_ajustada"] for p in partes)
    total_real = sum(p["horas_reales"] for p in partes)
    umbral = cierre.get("umbral_causa", 0.20)
    return {"componentes": comps, "gestion": partes[-1] if "gestion" in cierre else None,
            "linea_base_ajustada": round(total_base, 1), "horas_reales": round(total_real, 1),
            "proyecto": round((total_real - total_base) / total_base, 3),
            "requieren_causa": [c["id"] for c in comps if abs(c["desviacion"]) > umbral]}


def horas_jira(filas):
    """Suma las horas de la exportación de Jira. Cada épica de un componente empieza por su código (C01…); la de gestión
    contiene la palabra gestión; la de un trabajo que no se estimó (soporte, garantía) empieza por FUERA. Devuelve las horas
    por componente, las de gestión, las de trabajos fuera de la estimación y las épicas sin asignar."""
    import re
    comps, gestion, fuera, sin_asignar = {}, 0.0, {}, {}
    for f in filas:
        epica, horas = f["epica"].strip(), float(str(f["horas"]).replace(",", "."))
        m = re.match(r"(C\d{2})\b", epica)
        if m:
            comps[m.group(1)] = comps.get(m.group(1), 0) + horas
        elif epica.upper().startswith("FUERA"):
            fuera[epica] = fuera.get(epica, 0) + horas
        elif "gesti" in epica.lower():
            gestion += horas
        else:
            sin_asignar[epica] = sin_asignar.get(epica, 0) + horas
    return comps, gestion, fuera, sin_asignar


def preparar_cierre(linea_base, filas_jira, cambios, v):
    """Lo que recibe A7: horas reales contra la línea base ajustada por los cambios de alcance, desviaciones, componentes que
    requieren causa y si el proyecto cerró fuera del rango (lo que exige la revisión de cierre).
    linea_base: el escenario enviado (salida de la función escenario). cambios: [{componente | "gestion", horas, descripcion}]."""
    reales, gestion_real, fuera_estimacion, sin_asignar = horas_jira(filas_jira)
    ids = [c["id"] for c in linea_base["componentes"]]
    faltan = [i for i in ids if i not in reales]
    extra = [i for i in reales if i not in ids]
    cambio = lambda k: sum(c["horas"] for c in cambios if c["componente"] == k)
    d = desviacion({"componentes": [{"id": c["id"], "nombre": c.get("nombre"), "arquetipo": c["arquetipo"],
                                     "horas_esperadas": c["horas"], "horas_reales": round(reales.get(c["id"], 0), 1),
                                     "horas_cambios_alcance": cambio(c["id"])} for c in linea_base["componentes"]],
                    "gestion": {"id": "gestion", "horas_esperadas": linea_base["escenario"]["gestion"],
                                "horas_reales": round(gestion_real, 1), "horas_cambios_alcance": cambio("gestion")},
                    "umbral_causa": v["umbral_desviacion"]})
    total_cambios = sum(c["horas"] for c in cambios)
    hs = linea_base["escenario"]["horas_sin_redondear"]
    rango = {"optimista": round(hs["optimista"] + total_cambios, 1), "pesimista": round(hs["pesimista"] + total_cambios, 1)}
    fuera = not rango["optimista"] <= d["horas_reales"] <= rango["pesimista"]
    return {"id_solicitud": linea_base.get("id_solicitud"), "version_valores": linea_base["version_valores"],
            "confianza_estimada": linea_base["confianza"], "desviacion": d, "cambios_alcance": cambios,
            "rango_ajustado": rango, "fuera_de_rango": fuera, "requiere_revision_de_cierre": fuera,
            "horas_fuera_de_la_estimacion": fuera_estimacion,
            "epicas_sin_asignar": sin_asignar, "componentes_sin_horas": faltan, "componentes_no_estimados": extra}


# ---------------------------------------------------------------- indicadores y recalibración (sección 8)
def indicadores(registro, catalogo, v):
    """Indicadores del framework y disparador de recalibración, sobre los proyectos cerrados con FAED (origen cierre y con
    desviación registrada). Disparador: componentes de un mismo arquetipo que se desvían por encima del umbral en el mismo
    sentido en el número mínimo de proyectos de los valores del método."""
    cerrados = [p for p in registro["proyectos"] if p.get("origen") == "cierre" and p.get("desviacion") is not None]
    r = {"proyectos_cerrados": len(cerrados)}
    if cerrados:
        r["desviacion_promedio"] = round(sum(abs(p["desviacion"]) for p in cerrados) / len(cerrados), 3)
        dentro = [p for p in cerrados if p.get("dentro_del_rango") is not None]
        r["dentro_del_rango"] = round(sum(1 for p in dentro if p["dentro_del_rango"]) / len(dentro), 3) if dentro else None
    usos = [u for a in catalogo["activos"] for u in a.get("usos", []) if u.get("reutilizacion_confirmada") is not None]
    r["reuso_cumplido"] = round(sum(1 for u in usos if u["reutilizacion_confirmada"]) / len(usos), 3) if usos else None
    umbral, minimo = v["umbral_desviacion"], v["proyectos_disparador_recalibracion"]
    conteo = {}
    for p in cerrados:
        for c in p.get("componentes", []):
            d = c.get("desviacion")
            if d is not None and abs(d) > umbral:
                k = (c["arquetipo"], "arriba" if d > 0 else "abajo")
                conteo.setdefault(k, set()).add(p["id"])
    r["disparadores"] = [{"arquetipo": a, "sentido": s_, "proyectos": sorted(ps)} for (a, s_), ps in sorted(conteo.items()) if len(ps) >= minimo]
    r["en_observacion"] = [{"arquetipo": a, "sentido": s_, "proyectos": sorted(ps)} for (a, s_), ps in sorted(conteo.items()) if len(ps) < minimo]
    return r


if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser(description="Funciones de cálculo de FAED.")
    a.add_argument("--valores", help="Archivo de valores del método (por defecto, valores_metodo.json)")
    sub = a.add_subparsers(dest="accion", required=True)
    x1 = sub.add_parser("componentes", help="Horas de cada componente a partir de la salida de A4")
    x1.add_argument("detalle")
    x2 = sub.add_parser("preparar", help="Lo que recibe A5: proyecto calculado, candidatos a comparables y horas por proceso")
    x2.add_argument("detalle"); x2.add_argument("--registro", required=True)
    x3 = sub.add_parser("escenario", help="Escenario completo con los juicios de A5")
    x3.add_argument("detalle"); x3.add_argument("juicio"); x3.add_argument("--registro", required=True)
    x3.add_argument("--nivel-informacion", required=True, choices=NIVELES)
    x3.add_argument("--experiencia-equipo", required=True, type=int, choices=[0, 1, 2, 3])
    x3.add_argument("--modalidad", choices=["bolsa_de_horas", "sprints", "bloque", "precio_fijo"])
    x3.add_argument("--cliente-estrategico", action="store_true")
    x3.add_argument("--infraestructura", type=float, default=0)
    x4 = sub.add_parser("estimar", help="Estimación a partir de componentes ya clasificados (por ejemplo, el caso del anexo C)")
    x4.add_argument("entrada")
    x5 = sub.add_parser("desviacion", help="Desviación por componente y del proyecto, a partir de horas ya consolidadas")
    x5.add_argument("cierre")
    x6 = sub.add_parser("cierre", help="Lo que recibe A7: horas de Jira contra la línea base, desviaciones y revisión de cierre")
    x6.add_argument("linea_base"); x6.add_argument("--jira", required=True, help="Exportación de Jira en CSV, con las columnas epica y horas")
    x6.add_argument("--cambios", help="Cambios de alcance aprobados, en JSON")
    x7 = sub.add_parser("indicadores", help="Indicadores del framework y disparador de recalibración")
    x7.add_argument("registro"); x7.add_argument("--catalogo", required=True)
    x = a.parse_args()
    v = cargar_valores(x.valores)
    leer = lambda r: json.loads(pathlib.Path(r).read_text(encoding="utf-8"))
    if x.accion == "componentes":
        res = [calcular_componente(c, v) for c in componentes_desde_detalle(leer(x.detalle))]
    elif x.accion == "preparar":
        res = preparar_a5(leer(x.detalle), leer(x.registro), v)
    elif x.accion == "escenario":
        res = estimar_escenario(leer(x.detalle), leer(x.juicio), leer(x.registro), x.nivel_informacion, x.experiencia_equipo, v,
                                x.modalidad, x.cliente_estrategico, x.infraestructura)
    elif x.accion == "estimar":
        res = estimar(leer(x.entrada), v)
    elif x.accion == "cierre":
        import csv
        with open(x.jira, encoding="utf-8-sig", newline="") as f:
            filas = list(csv.DictReader(f))
        res = preparar_cierre(leer(x.linea_base), filas, leer(x.cambios) if x.cambios else [], v)
    elif x.accion == "indicadores":
        res = indicadores(leer(x.registro), leer(x.catalogo), v)
    else:
        res = desviacion(leer(x.cierre))
    json.dump(res, sys.stdout, ensure_ascii=False, indent=2)
    print()
