# A4 · Esfuerzo, duración y costo · propuesta para revisión

## Entradas y salida

Leer A1 aceptado, componentes A2, clasificación A3, respuestas y adendas del cierre,
reglas aprobadas y su snapshot. Un ejemplo de formación no habilita A4 del piloto.
Entregar informe legible por componente y rol con dos escenarios, alcance, fuentes,
supuestos, pendientes PRE/PEN y cálculo reproducible en `02-trabajo/`.

## 1. Decidir cobertura y método

Crear una matriz componente/actividad → método → fases cubiertas. Para software
con tamaño y parámetros defendibles, considerar COCOMO II. Para configuración,
aprovisionamiento, adopción u otro trabajo fuera de esa cobertura, usar actividades
o analogía con fundamento. No imponer COCOMO a un arquetipo por su nombre.

Un componente puede tener partidas de ambos métodos si sus coberturas son distintas.
Si descomposición y COCOMO estiman lo mismo, mostrar una como contraste, no sumarlas.
Verificar si análisis, gestión, pruebas e integración ya están cubiertos antes de
agregarlos. Reutilizar un directorio no elimina el trabajo de conectar/configurar/probar.

## 2. Calcular esfuerzo

**COCOMO II:** acordar Early Design o Post-Architecture; tamaño en KSLOC y su base,
factores de escala, multiplicadores, calibración, adaptación/reuso y fases cubiertas.
No convertir COSMIC ni XS/S/M a líneas automáticamente. No usar N3/N4 como driver.
Ver `cocomo-ii.md`. Calcular esfuerzo del conjunto de software según las reglas
de agregación y reconciliar su reparto por componente. No sumar modelos pequeños
independientes ignorando la escala del conjunto. Personas-mes se convierten a
horas con una convención identificada, nunca se presentan como meses calendario.

**Actividades fuera de cobertura:** por componente–actividad–rol identificar
fundamento y O/M/P, si este método se aprueba. Base = (O + 4M + P) / 6;
conservador = P, con 0 ≤ O ≤ M ≤ P. Alternativamente usar una analogía calibrada
declarada. No inventar horas por una etiqueta de complejidad.

Reparto por rol requiere una regla/evidencia propia y aprobada; no viene del
nombre del componente ni se deriva automáticamente de COCOMO. Cada reparto suma
100 % y reconcilia con el total. Conservar los cálculos sin redondeos intermedios.

## 3. Construir duración y calendario

Definir recursos concretos, capacidad efectiva por semana, dedicación, dependencias,
esperas externas y calendario. Dividir trabajo por capacidad asignada y programar
actividades sin sobreasignar personas. El fin del proyecto es el fin de la última
actividad, no la suma de duraciones de componentes que se solapan.

Por componente mostrar inicio, fin y duración transcurrida, incluyendo sus esperas
si existen; identificar la unidad de calendario. Para COCOMO, contrastar el plan
con la referencia de duración de la variante si hay datos: discrepancias requieren
revisión, no ajustar silenciosamente coeficientes o asumir aceleración gratis.
Un plan de recursos es una decisión distinta del esfuerzo del modelo. No prometer
fechas sin capacidad y dependencias confirmadas.

## 4. Calcular costo

Costo de mano de obra por componente = suma(horas por rol × tarifa por hora).
Declarar moneda, vigencia y qué cubre la tarifa. Separar licencias, consumo de nube,
servicios de terceros, impuestos, margen y otros costos directos. No confundir costo
de ejecución con precio de venta. Lo que no tiene dato queda «por confirmar».

## 5. Construir escenarios

Base y conservador mantienen alcance y declaran entradas que cambian. En COCOMO
pueden representar rangos defendibles de tamaño o drivers, sin asignar un recargo
porcentual universal. En actividades puede usarse el rango O/M/P acordado. Recalcular
esfuerzo, costo y calendario para cada escenario; no inflar solo el total.
Conservador no es garantía ni percentil. No duplicar contingencia sobre riesgos ya cubiertos.

## 6. Revisar antes de entregar

Verificar sumas, unidades, roles, cobertura única, capacidad sin solapes indebidos,
dependencias, inputs sustentados y escenarios comparables. Un total con componentes
sin estimar debe decir **parcial** e identificar lo excluido; no presentar su suma
como total completo. Si faltan tarifas o equipo, no reemplazarlos por cero/defaults.
Preguntas nuevas mantienen PRE/PEN por componente o G para asuntos compartidos.

El motor A4 completo sigue exigiendo reglas y datos operativos aprobados. El script
`scripts/ejemplo_a4.py` es una demostración limitada con datos ficticios, no un
calculador productivo completo de COCOMO ni un modelo calibrado para la organización.
Ejemplo legible: `docs/ejemplo-a4-estimacion.md`.
