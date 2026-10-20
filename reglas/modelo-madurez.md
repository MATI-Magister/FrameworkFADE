# Modelo de madurez y caracterización · base del Excel

Original: `fuentes/Modelo_Madurez_Estimacion.xlsx`. Extracción portable:
`modelo-madurez.json`, con 11 dimensiones y 109 criterios, descriptores completos,
preguntas, evidencias esperadas y referencias de celda. El modelo no calcula
esfuerzo o costo. D12 (riesgo e incertidumbre) está fuera de la calificación del
libro; registrar riesgos aparte.

## Dos usos del catálogo

**A1:** evaluar si el requerimiento permite determinar cada dimensión. Asignar
0–3 por criterio según su rúbrica, citar evidencia y generar las preguntas faltantes.
No se exige haber ejecutado A2 para calificar; si solo hay módulos, señalar qué
detalle falta. Entregar resumen y evaluación comprensibles para personas.

**A3:** después de dividir, caracterizar cada componente con las mismas D1–D11.
Registrar valor/clase, evidencia y pendiente. Referenciar datos globales heredados
(sector, equipo o comparables) sin inventar diferencias locales. No promediar
etiquetas de componentes para obtener madurez; A1 se recalcula con criterios.

| Dimensión | Tipo | Peso | Qué se caracteriza |
| --- | --- | --- | --- |
| D1 · Tipo de desarrollo | Núcleo | 12 % | Nuevo, evolutivo, modernización o mantenimiento y composición |
| D2 · Tipo de solución / arquetipo | Núcleo | 11 % | Aplicaciones, integración, datos/IA, plataforma, seguridad o modernización |
| D3 · Tamaño funcional | Núcleo | 18 % | Procesos, fronteras, movimientos de datos y unidad de tamaño |
| D4 · Complejidad | Núcleo | 15 % | Reglas, arquitectura, seguridad, procesamiento y dependencias |
| D5 · Integración / interdependencia | Núcleo | 14 % | Interfaces, dificultad y terceros |
| D6 · Novedad y reutilización | Complementaria | 5 % | Activos reutilizables y adaptación |
| D7 · Entorno tecnológico | Complementaria | 5 % | Tecnología y familiaridad |
| D8 · Madurez del alcance | Complementaria | 7 % | Elementos definidos y validados |
| D9 · Contexto de ejecución | Complementaria | 5 % | Equipo, disponibilidad y condiciones |
| D10 · Sector / contexto de negocio | Complementaria | 3 % | Dominio, regulación y restricciones |
| D11 · Evidencia histórica disponible | Complementaria | 5 % | Comparables: cantidad, similitud, calidad y vigencia |

## Calificación y cálculo

- 0: sin información; 1: parcial/supuesto; 2: definido con vacíos; 3: completo y
  validado. Los descriptores específicos de Rubricas prevalecen sobre esta síntesis.
- Puntaje 3 requiere validación real por responsable, no inferencia de IA.
- N/A solo donde el criterio lo admite y con explicación; excluirlo del máximo.
- Dimensión = suma(puntaje × peso interno) / suma(3 × peso interno aplicable).
- Núcleo sin puntaje cuenta como 0. Complementaria sin puntaje numérico se excluye
  del promedio. Al empezar una complementaria, sus pendientes siguen en el máximo
  como 0. Informar siempre exclusiones y cobertura.
- General = promedio ponderado de dimensiones incluidas. Núcleo suma 70 % de los
  pesos originales; el denominador se normaliza cuando se excluyen complementarias.
- N1 <20 %, N2 20–<40 %, N3 40–<60 %, N4 60–<80 %, N5 ≥80 %.
- Si alguna núcleo está <40 %, limitar **el nivel** a N3 y conservar el porcentaje.
  Sin calificaciones numéricas, el estado es «Sin evaluar».

## Preguntas para mejorar la madurez

Prioridad = (3 − puntaje) × peso interno × peso de dimensión. Un criterio sin
calificar usa 0 para ordenar preguntas; N/A justificado se excluye. Mostrar diez
brechas principales y preguntar hasta cinco por ronda, agrupando evidencias comunes
sin perder IDs. Para 0–1 pedir información faltante; para 2 completar o validar;
para 3 no repetir preguntas respondidas.

Separar condiciones conocidas desfavorables de preguntas de información: «no hay
históricos» es una respuesta, no una pregunta pendiente. Puede limitar la técnica
sin faltar averiguar la cantidad. Tras cada ronda conservar versión, fuente,
fecha y responsable; cambiar solo puntajes sustentados por nueva evidencia y
recalcular el resultado completo. No premiar la cantidad de respuestas.

## Calculador local

```sh
python scripts/madurez.py --project piloto template
python scripts/madurez.py --project piloto evaluate
```

El agente completa score, evidence, validated_by y tipo de brecha en la plantilla
técnica; el cliente lee el informe Markdown. Los resultados van a `02-trabajo/`.
No cambia etapas ni aprueba A1. Al recalcular conserva la ronda previa en
`02-trabajo/madurez-rondas/`; el resultado técnico incluye sus evidencias de entrada.
Integrar el resultado en A1 junto con revisión de los 15 cruces de
consistencia de `Ficha!A61:G75`; el script no ejecuta fórmulas de Excel.

## Decisiones pendientes del modelo

1. **Paso A1→A2, acordado por el usuario:** primero generar preguntas para elevar
   N3 a N4 y presentarlas al experto. Con su instrucción explícita se puede pasar
   a componentes; si pide aclaraciones, iterar y recalcular. El objetivo N4 no es
   un pase automático ni impide una autorización experta con pendientes visibles.
   Guardar preguntas en `03-entregables/preguntas-a1.md`; el motor exige ese
   documento antes de aceptar A1 y comprueba que no cambió durante la aprobación.
2. **Tipo predominante:** `Dimensiones!G4` pide >50 %; `Ficha!G14` elige el mayor
   aunque no lo supere. Hasta acordarlo, describir composición mixta sin forzar
   predominio y mostrar la advertencia.
3. **Reuso:** el texto solapa 40 % entre R2/R3; `Ficha!G32` usa R2 desde 40 %
   inclusive, R3 desde 10 % hasta <40 %, R1 >70 %, R4 <10 %. Referencia provisional:
   esa fórmula, con límites pendientes de confirmación.
4. **Conocimiento frente a condición real:** D9.02 y D11.01 puntúan experiencia o
   comparables incluso si sabemos que no existen. Conservar puntuación del libro
   y marcar «condición conocida», sin inventar una brecha de documentación.
   Cambiar esa rúbrica exige nueva versión acordada.
5. **Tamaño:** los 8 puntos por proceso de `Parametros!B49` son un supuesto inicial
   no calibrado. No declararlo medición detallada COSMIC ni convertirlo
   automáticamente a líneas de código. Criterios de aceptación faltantes reducen
   D8, pero no obligan a escribir historias.

La fuente original se conserva sin reparar fórmulas ni sobrescribir datos.
