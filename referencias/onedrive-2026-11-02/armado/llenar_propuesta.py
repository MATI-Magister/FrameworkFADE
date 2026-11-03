"""Armado de la propuesta: pone en la plantilla los textos de A6 y las cifras del escenario validado.

    pendientes = llenar(plantilla, salida, propuesta, escenario, juicio, detalle, datos)

Desde la terminal (desde la carpeta agentes):
    python armado/llenar_propuesta.py propuesta.json escenario.json juicio.json detalle.json \\
        --cliente "Nombre del cliente" -o propuesta.docx [--contacto ...] [--preparado-por ...] \\
        [--modalidades bolsa_de_horas sprints bloque precio_fijo] [--vigencia 30] [--pago 30] [--sin-aceptacion]

Las cifras salen solo del escenario (salida de `faed_calculos.py escenario`); los textos, solo de A6 y de la funcionalidad
del bloque que propuso A5. Con confianza alta presenta una cifra única; con confianza media, el rango; con información
baja, un rango preliminar sin modalidades, sin bloque y sin aceptación. Quita las instrucciones de la plantilla y lista lo
que queda entre corchetes para que la Gerencia de Proyectos lo complete antes de enviar.
Requiere el paquete python-docx (pip install python-docx).
"""
import copy, datetime, json, math, pathlib, re, sys
import docx
from docx.oxml.ns import qn

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "calculo"))
import faed_calculos as fc

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
NOMBRES = {"bolsa_de_horas": "Bolsa de horas", "sprints": "Sprints", "bloque": "Primer bloque", "precio_fijo": "Precio fijo"}
FACTURACION = {"bolsa_de_horas": "mensual por consumo real", "sprints": "por sprint completado",
               "bloque": "por hitos definidos", "precio_fijo": "por hitos definidos"}
ESTANDAR_INCLUYE = ["Análisis, diseño, construcción, pruebas y despliegue de cada componente.",
                    "Gestión del proyecto y acompañamiento en la salida a producción."]


# ---------------------------------------------------------------- formato
def millones(x):
    return "$" + f"{x / 1e6:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") + " millones"


def entero(x):
    return f"{round(x):,}".replace(",", ".")


def decimal(x):
    return (f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")).removesuffix(",0")


def semanas(horas, v):
    """Duración en semanas: sprints redondeados al medio sprint por las semanas de cada sprint. None si no está definido."""
    if not v.get("semanas_por_sprint"):
        return None
    return math.ceil(horas / v["capacidad_sprint_horas"] * 2) / 2 * v["semanas_por_sprint"]


# ---------------------------------------------------------------- XML de la plantilla
def texto(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def poner_texto(p, t):
    """Deja el párrafo con un solo run, con el formato del primero, y el texto dado."""
    runs = p.findall(qn("w:r"))
    base = runs[0] if runs else None
    for r in runs:
        p.remove(r)
    r = copy.deepcopy(base) if base is not None else p.makeelement(qn("w:r"), {})
    for x in list(r):
        if x.tag != qn("w:rPr"):
            r.remove(x)
    w = r.makeelement(qn("w:t"), {qn("xml:space"): "preserve"})
    w.text = t
    r.append(w)
    p.append(r)
    return p


def poner_resto(p, t):
    """Conserva el primer run (la etiqueta en negrita) y deja el resto del párrafo con el formato del segundo run."""
    runs = p.findall(qn("w:r"))
    etiqueta, modelo = runs[0], copy.deepcopy(runs[1] if len(runs) > 1 else runs[0])
    for r in runs[1:]:
        p.remove(r)
    for x in list(modelo):
        if x.tag != qn("w:rPr"):
            modelo.remove(x)
    w = modelo.makeelement(qn("w:t"), {qn("xml:space"): "preserve"})
    w.text = t
    modelo.append(w)
    etiqueta.addnext(modelo)


def lista(parrafos, items):
    """Llena una lista de párrafos de ejemplo con los elementos dados: usa el primero como modelo y quita los demás."""
    modelo, ancla = parrafos[0], parrafos[-1]
    for t in items:
        n = poner_texto(copy.deepcopy(modelo), t)
        ancla.addnext(n)
        ancla = n
    for p in parrafos:
        p.getparent().remove(p)


def celda(fila, i, t):
    p = fila.findall(qn("w:tc"))[i].find(qn("w:p"))
    poner_texto(p, t)
    for extra in fila.findall(qn("w:tc"))[i].findall(qn("w:p"))[1:]:
        extra.getparent().remove(extra)


def quitar(el):
    sig = el.getnext()
    el.getparent().remove(el)
    return sig


def llenar(plantilla, salida, prop, esc, juicio, det, datos, v=None):
    v = v or fc.cargar_valores()
    d = docx.Document(plantilla)
    body = d.element.body
    pend = []

    def P(inicio):
        for el in body.iterchildren(qn("w:p")):
            if texto(el).startswith(inicio):
                return el
        raise ValueError(f"La plantilla no tiene el párrafo que empieza por «{inicio}».")

    def T(inicio):
        for el in body.iterchildren(qn("w:tbl")):
            if texto(el).startswith(inicio):
                return el
        raise ValueError(f"La plantilla no tiene la tabla que empieza por «{inicio}».")

    def siguientes(el, inicio):
        out, x = [], el
        while x is not None and x.tag == qn("w:p") and texto(x).startswith(inicio):
            out.append(x); x = x.getnext()
        return out

    instruccion = copy.deepcopy(P("Instrucción:"))
    pr, conf = esc["precios"], esc["confianza"]
    h = esc["escenario"]["horas"]
    preliminar = esc["nivel_informacion"] == "baja"
    bloque = juicio["primer_bloque"]["procesos"]
    if preliminar and bloque:
        bloque = []
        pend.append("El escenario trae un primer bloque, pero con información baja la estimación es preliminar; no se incluyó.")
    modalidades = datos.get("modalidades") or ["bolsa_de_horas", "sprints", "bloque", "precio_fijo"]
    if esc.get("modalidad") and esc["modalidad"] in modalidades:
        modalidades = [esc["modalidad"]] + [m for m in modalidades if m != esc["modalidad"]]
    if not bloque:
        modalidades = [m for m in modalidades if m != "bloque"]
    if pr["precio_fijo"]["precio"] is None and "precio_fijo" in modalidades:
        modalidades.remove("precio_fijo")
        pedido = esc.get("modalidad") == "precio_fijo" or "precio_fijo" in (datos.get("modalidades") or [])
        if pedido and esc["nivel_informacion"] != "baja":
            pend.append("Precio fijo: con confianza baja solo la dirección puede autorizarlo; no se incluyó.")
    if esc["ruta"].get("provisional"):
        pend.append("Ruta estándar provisional: sin umbrales de valor y esfuerzo definidos, la dirección confirma la ruta antes de enviar.")
    fijo = esc.get("modalidad") == "precio_fijo" and pr["precio_fijo"]["precio"] is not None

    # Portada
    hoy = datos.get("fecha") or datetime.date.today()
    portada = {"Código": datos.get("codigo") or prop["id_solicitud"].replace("SOL", "COT"),
               "Fecha": f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}",
               "Cliente": datos["cliente"], "Contacto": datos.get("contacto") or "[NOMBRE_CONTACTO]",
               "Proyecto": prop["nombre_proyecto"], "Preparado por": datos.get("preparado_por") or "[NOMBRE_RESPONSABLE_PROPUESTA]"}
    for fila in T("Código").findall(qn("w:tr")):
        k = texto(fila.findall(qn("w:tc"))[0])
        if k in portada:
            celda(fila, 1, portada[k])
    for sec in d.sections:
        for parte in (sec.header, sec.footer):
            for w in parte._element.iter(qn("w:t")):
                if w.text and "[NOMBRE_PROYECTO]" in w.text:
                    w.text = w.text.replace("[NOMBRE_PROYECTO]", prop["nombre_proyecto"])

    # 1. Contexto
    lista([P("[Descripción de la necesidad"), P("[Contexto relevante")], prop["contexto"])

    # 2. Solución y alcance
    poner_texto(P("[Descripción general de la solución"), prop["solucion"]["descripcion"])
    t = T("Componente")
    filas = t.findall(qn("w:tr"))
    nombres = {c["id"]: c["nombre"] for c in det["componentes"]}
    for c in prop["solucion"]["componentes"]:
        f = copy.deepcopy(filas[1]); celda(f, 0, nombres[c["id"]]); celda(f, 1, c["descripcion"]); t.append(f)
    for f in filas[1:]:
        t.remove(f)
    infra = esc.get("infraestructura_y_licencias") or 0
    no_incluye = prop["solucion"]["no_incluye"] + ([] if infra else ["Infraestructura y licencias, que se cotizan aparte si aplican."])
    lista(siguientes(P("[Elemento incluido 1"), "[Elemento incluido"), ESTANDAR_INCLUYE + prop["solucion"]["incluye_adicional"])
    lista(siguientes(P("[Elemento excluido 1"), "[Elemento excluido"), no_incluye)

    # 3. Estimación e inversión
    tabla = T("Horas estimadas")
    s_esp = semanas(esc["escenario"]["horas_sin_redondear"]["esperado"], v)
    s_opt = semanas(esc["escenario"]["horas_sin_redondear"]["optimista"], v)
    s_pes = semanas(esc["escenario"]["horas_sin_redondear"]["pesimista"], v)
    if s_esp is None:
        pend.append("Duración: falta definir las semanas por sprint en los valores del método.")
    if conf == "alta" or (fijo and not preliminar):
        # Cifra única: con confianza alta o cuando el cliente pidió precio fijo (sección 6 del framework)
        filas_t = tabla.findall(qn("w:tr"))
        valores_t = [entero(h["esperado"]), millones(pr["precio_fijo"]["precio"] if fijo else pr["escenarios"]["esperado"]),
                     f"{decimal(s_esp)} semanas" if s_esp else "[N semanas]"]
        for fila, val in zip(filas_t, valores_t):
            celda(fila, 1, val)
        if fijo:
            celda(filas_t[1], 0, "Inversión a precio fijo")
    else:
        dur = f", con una duración entre {decimal(s_opt)} y {decimal(s_pes)} semanas" if s_esp else ", con una duración entre [N] y [M] semanas"
        confirma = "el primer bloque" if bloque else "una fase de definición"
        rango = f"entre {millones(pr['escenarios']['optimista'])} y {millones(pr['escenarios']['pesimista'])}"
        if esc["nivel_informacion"] == "baja":
            t_rango = (f"Esta estimación es un rango preliminar: la inversión se encuentra {rango}{dur}. "
                       f"Para emitir una propuesta formal, Software Colombia necesita la información de la sección 5.")
        else:
            t_rango = (f"La inversión estimada se encuentra {rango}{dur}. Al completar {confirma}, "
                       f"Software Colombia confirma el valor dentro de ese rango.")
        p_rango = poner_texto(copy.deepcopy(P("La solución se compone")), t_rango)
        tabla.addprevious(p_rango)
        if conf == "baja" and esc["nivel_informacion"] != "baja":
            nota = poner_texto(copy.deepcopy(instruccion), "Nota interna: con confianza baja por falta de experiencia, la dirección define "
                               "cómo presentar la inversión. Elimine esta nota antes de enviar.")
            p_rango.addnext(nota)
            pend.append("Nota interna de la sección 3: la dirección define cómo presentar la inversión.")
        quitar(tabla)
    t_inf = T("Infraestructura")
    if infra:
        celda(t_inf.findall(qn("w:tr"))[0], 1, millones(infra))
    else:
        quitar(t_inf)

    t = T("Modalidad")
    if preliminar:
        modalidades = []
        quitar(P("Las modalidades de contratación"))
    filas = t.findall(qn("w:tr"))
    modelo = {texto(f.findall(qn("w:tc"))[0]): f for f in filas[1:]}
    for m in modalidades:
        f = copy.deepcopy(modelo[NOMBRES[m]])
        if m == "bolsa_de_horas":
            celda(f, 1, millones(pr["bolsa_de_horas"]))
        elif m == "sprints":
            celda(f, 1, millones(pr["sprints"]["precio"]))
            n = pr["sprints"]["numero"]
            celda(f, 2, (f"1 sprint del equipo, de {entero(v['capacidad_sprint_horas'])} horas." if n == 1 else
                         f"{decimal(n)} sprints del equipo, de {entero(v['capacidad_sprint_horas'])} horas cada uno."))
        elif m == "bloque":
            celda(f, 1, millones(pr["primer_bloque"]["precio"]))
            celda(f, 2, f"{juicio['primer_bloque']['funcionalidad']} Permite confirmar el alcance restante.")
        else:
            celda(f, 1, millones(pr["precio_fijo"]["precio"]))
        t.append(f)
    for f in filas[1:]:
        t.remove(f)
    if not modalidades:
        quitar(t)

    # 4 y 5
    lista(siguientes(P("[Supuesto 1"), "[Supuesto"), prop["supuestos"])
    lista(siguientes(P("[Información 1"), "[Información"), prop["informacion_que_mejora"])

    # 6. Plan de inicio
    titulo, t_bloque, cierre = P("Primer bloque recomendado"), T("Objetivo"), P("[Al cerrar el primer bloque")
    if bloque:
        por_comp = {}
        for i in bloque:
            por_comp.setdefault(i.split("-")[0], []).append(i)
        partes = [c["nombre"] + ("" if len(por_comp[c["id"]]) == len(c["procesos"]) else " (en parte)")
                  for c in det["componentes"] if c["id"] in por_comp]
        comps = [fc.calcular_componente(x, v) for x in fc.componentes_desde_detalle(det)]
        hb = fc.horas_bloque(bloque, det, comps, v)
        s_b = semanas(hb, v)
        valores = {"Objetivo": prop["objetivo_bloque"], "Componentes incluidos": "; ".join(partes) + ".",
                   "Duración estimada": f"{decimal(s_b)} semanas" if s_b else "[N semanas]",
                   "Resultado esperado": juicio["primer_bloque"]["funcionalidad"], "Inversión": millones(pr["primer_bloque"]["precio"])}
        for fila in t_bloque.findall(qn("w:tr")):
            celda(fila, 1, valores[texto(fila.findall(qn("w:tc"))[0])])
        poner_texto(cierre, texto(cierre).strip("[]"))
    elif preliminar:
        inicio = poner_texto(copy.deepcopy(cierre), "El siguiente paso es completar con el equipo del cliente la información de la "
                             "sección 5, en una sesión adicional o en una fase de definición. Con ella, Software Colombia emite la "
                             "propuesta formal con el valor y la modalidad de contratación.")
        titulo.addprevious(inicio)
        quitar(titulo); quitar(t_bloque); quitar(cierre)
    else:
        inicio = poner_texto(copy.deepcopy(cierre), "El proyecto inicia con una reunión de arranque en la semana del [FECHA]. El equipo "
                             f"asignado se compone de [ROLES]. El primer entregable es {prop['primer_entregable'].rstrip('.')}, "
                             "en la semana [N].")
        titulo.addprevious(inicio)
        quitar(titulo); quitar(t_bloque); quitar(cierre)

    # 7. Condiciones
    if preliminar:
        quitar(P("Facturación:"))
        quitar(P("Forma de pago:"))
        titulo_doc = P("Propuesta de servicios")
        poner_texto(titulo_doc, "Rango preliminar de inversión")
        for sec in d.sections:
            for w in sec.header._element.iter(qn("w:t")):
                if w.text and "Propuesta de servicios" in w.text:
                    w.text = w.text.replace("Propuesta de servicios", "Rango preliminar")
    poner_resto(P("Vigencia:"), f" esta propuesta es válida por {datos.get('vigencia', 30)} días calendario a partir de la fecha de emisión.")
    if not preliminar:
        fact = FACTURACION[modalidades[0]] if modalidades else "[mensual por avance / por sprint completado / por hitos definidos]"
        poner_resto(P("Facturación:"), f" {fact}.")
    if not preliminar:
        poner_resto(P("Forma de pago:"), f" {datos.get('pago', 30)} días después de la fecha de la factura.")

    # 8. Aceptación
    if datos.get("sin_aceptacion") or preliminar:
        x = P("8. Aceptación")
        while x is not None and x.tag != qn("w:sectPr"):
            x = quitar(x)

    # Instrucciones fuera y párrafos vacíos repetidos
    for el in list(body.iterchildren(qn("w:p"))):
        if texto(el).startswith("Instrucción:"):
            quitar(el)
    for el in list(body.iterchildren(qn("w:p"))):
        vacio = lambda e: e is not None and e.tag == qn("w:p") and not texto(e).strip() and e.find(".//" + qn("w:br")) is None
        if vacio(el) and vacio(el.getnext()):
            quitar(el)
        elif vacio(el) and el.getnext() is not None and el.getnext().tag == qn("w:p") and \
                el.getnext().find(".//" + qn("w:pStyle")) is not None and \
                el.getnext().find(".//" + qn("w:pStyle")).get(qn("w:val")) == "Heading1":
            quitar(el)

    d.save(salida)
    restantes = sorted(set(re.findall(r"\[[^\]]+\]", "\n".join(texto(p) for p in body.iter(qn("w:p"))))))
    if restantes:
        pend.append("Campos por completar: " + ", ".join(restantes))
    return pend


if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser(description="Arma la propuesta en la plantilla con los textos de A6 y el escenario validado.")
    a.add_argument("propuesta"); a.add_argument("escenario"); a.add_argument("juicio"); a.add_argument("detalle")
    a.add_argument("--cliente", required=True); a.add_argument("-o", "--salida", required=True)
    a.add_argument("--plantilla", default=str(RAIZ / "datos" / "plantilla_propuesta.docx"))
    a.add_argument("--contacto"); a.add_argument("--preparado-por"); a.add_argument("--codigo")
    a.add_argument("--modalidades", nargs="+", choices=list(NOMBRES))
    a.add_argument("--vigencia", type=int, default=30); a.add_argument("--pago", type=int, default=30)
    a.add_argument("--sin-aceptacion", action="store_true")
    a.add_argument("--valores")
    x = a.parse_args()
    leer = lambda r: json.loads(pathlib.Path(r).read_text(encoding="utf-8"))
    pend = llenar(x.plantilla, x.salida, leer(x.propuesta), leer(x.escenario), leer(x.juicio), leer(x.detalle),
                  {"cliente": x.cliente, "contacto": x.contacto, "preparado_por": x.preparado_por, "codigo": x.codigo,
                   "modalidades": x.modalidades, "vigencia": x.vigencia, "pago": x.pago, "sin_aceptacion": x.sin_aceptacion},
                  fc.cargar_valores(x.valores))
    print(f"Propuesta armada: {x.salida}")
    for t in pend: print("PENDIENTE ", t)
