# A3 · Clasificación de componentes · propuesta para revisión

## Procedimiento

1. Leer A1 aceptado, A2, fuentes, respuestas PRE/PEN y decisiones vigentes.
2. Conservar ID, propósito y límites de cada componente. Un cambio de alcance
   requiere revisar A2, no redefinirlo silenciosamente al clasificar.
3. Registrar D1–D11 con valor/clase, explicación, fuente/versión, origen local o
   global heredado y estado. Verificar si una condición global aplica al componente.
4. Estados: **sustentado** (evidencia disponible), **supuesto** (hipótesis explícita
   pendiente de confirmar) y **por confirmar** (sin base para asignar valor).
   Sustentado no significa aprobación humana de la entrega.
5. Aplicar las escalas del modelo. No interpretar un dato desconocido como cero
   ni como complejidad baja. Mantener lo parcial visible sin forzar una clase.
6. Conservar preguntas de A2; agregar solo asuntos nuevos con códigos estables y
   responsable/impacto en el registro maestro. Una misma pregunta puede afectar
   varias dimensiones; referenciar su código sin duplicarla.
7. Explicar qué queda dimensionado, qué falta, si se requiere cierre y qué método
   podría usarse después, condicionado a sus entradas. No calcular esfuerzo todavía.

## Cómo aplicar las dimensiones

| Dimensión | Aplicación al componente |
| --- | --- |
| D1 · Tipo de desarrollo | Cuantificar composición nuevo/evolutivo/modernización/mantenimiento sobre una base identificada y justificar predominio. Sin inventar porcentajes. Ver discrepancia >50 % en modelo-madurez.md. |
| D2 · Arquetipo | Aplicaciones, integración, datos/IA, plataforma, seguridad o modernización; justificar principal y secundarios. Consumir autenticación no convierte toda funcionalidad en arquetipo Seguridad. |
| D3 · Tamaño funcional | Identificar frontera, procesos y criterio de conteo: XS 1–5, S 6–15, M 16–30, L 31–60, XL >60. Mostrar cantidad, unidad y medido/aproximado. Una pantalla/campo/archivo no es automáticamente un proceso. Cero o desconocido no es XS; clase XS no equivale a puntos funcionales. |
| D4 · Complejidad | Evaluar reglas, arquitectura, seguridad, procesamiento y dependencias, cada uno 0–2. Sumar solo con los cinco determinados: 0–2 baja, 3–5 media, 6–8 alta, 9–10 muy alta. Nube/directorio no fijan automáticamente sus factores. |
| D5 · Integración | Inventario y dificultad: I0 ninguna; I1 1–2 simples; I2 3–5 o alguna compleja; I3 >5 o condiciones de criticidad/protocolos no conocidos/múltiples terceros. Si falta el conteo, dejar pendiente salvo que otra condición ya determine I3. Referenciar integraciones compartidas sin duplicar su construcción. |
| D6 · Reutilización | Inventariar activos, porcentaje, procesos cubiertos y adaptación. INC-016 resuelto: escala ZIP R1 <10 %, R2 10–<30 %, R3 30–50 %, R4 >50 %. Conservar porcentaje, base de conteo y evidencia; no trasladar etiquetas del Excel. Consumir un servicio no prueba reuso del 100 %. |
| D7 · Entorno tecnológico | Stack, plataforma, restricciones y experiencia del equipo: T1 conocido, T2 parcialmente conocido, T3 nuevo, T4 experimental. Tecnología definida no prueba familiaridad; nube por sí sola no fija T1/T3. |
| D8 · Definición del componente | Escala elegida en INC-008: Validado si todos sus procesos/datos están confirmados directamente por el cliente; Definido si proceden de información escrita del cliente con validación pendiente; Supuesto ante inferidos, evidencia verbal no confirmada, interna no confirmada, faltantes o conflictos abiertos. Manda el proceso más débil; registrar su ID y fuentes. No cambia baja/media/alta global ni exige historias. |
| D9 · Contexto de ejecución | Revisar equipo, experiencia, dedicación, forma de trabajo, cliente y dependencias. Estable/parcialmente conocido/incierto con explicación; no inventar umbrales numéricos que el libro no define. Referenciar condiciones globales. |
| D10 · Sector | Gobierno, financiero, salud, comercio, telecomunicaciones u otros y sus restricciones. Normalmente heredado del proyecto, con excepciones justificadas. |
| D11 · Evidencia histórica | Comparables relevantes: E1 0–1, E2 2–3, E3 4–7, E4 ≥8. Revisar además similitud, calidad y vigencia. Cantidad desconocida no es cero; cero confirmado es E1 con fuente, no pregunta sin responder. |

## Resultado y control

Entregar `03-entregables/a3.md` con resumen, ficha D1–D11 por componente,
justificaciones, conteos/factores, asuntos PRE/PEN y conclusión de cierre.
Usar `plantillas/clasificacion-componentes.md`. No convertir clases o pesos en horas,
madurez en complejidad, ni etiquetas en drivers COCOMO. Registrar riesgos aparte
sin añadir D12 al cálculo. Conservar historial cuando cambien respuestas.

Si hay dudas materiales de alcance/equipo/entorno, el cierre es obligatorio. Solo
omitirlo con evidencia de completitud; llenar todas las filas no prueba confirmación.
El diseño detallado de A3 conserva puntos en revisión; la escala local de D8
ya fue elegida en INC-008 y sustituye M1–M4. Ejemplo ilustrativo: `docs/ejemplo-a3-clasificacion.md`; no es fuente
del requerimiento del piloto y no tiene respuestas reales del usuario.
