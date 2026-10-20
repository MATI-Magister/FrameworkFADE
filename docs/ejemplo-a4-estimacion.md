# Ejemplo A4 · Portal de soporte

**Demostración ficticia para revisar el formato y el método. No corresponde al piloto, no es una cotización y no activa A4.** Continúa el ejemplo de componentes con aclaraciones técnicas adicionales supuestas, sin registrar respuestas reales.

## Resultado en palabras

Con las hipótesis del ejemplo, el escenario base requiere **995.7 horas-persona**, un calendario de **32.5 semanas** y **95.542.363 COP de mano de obra**. La programación depende de la capacidad parcial y la secuencia declaradas; no es una fecha comprometida.

## Dos escenarios del mismo alcance

| Escenario | Horas-persona | Semanas del plan | Mano de obra (COP) |
| --- | --- | --- | --- |
| Base | 995.7 | 32.5 | 95.542.363 |
| Conservador | 1284.1 | 42.3 | 123.486.460 |

Base: tamaño técnico supuesto de 2,0 KSLOC y actividades de configuración ponderadas. Conservador: mismo alcance, tamaño técnico superior de 2,5 KSLOC y valores altos de configuración. El aumento de tamaño es incertidumbre de implementación, no nuevas funciones. No es un percentil ni recargo universal. En un caso real estos rangos necesitan evidencia.

## Esfuerzo y costo por componente

| Componente | Método y cobertura | Horas base | Horas conservadoras | Costo base (COP) | Costo conservador (COP) |
| --- | --- | --- | --- | --- | --- |
| C-001 · Registro de solicitudes | COCOMO II (grupo) | 239.4 | 306.0 | 22.745.591 | 29.071.615 |
| C-002 · Gestión de solicitudes | COCOMO II (grupo) | 335.2 | 428.4 | 31.843.827 | 40.700.261 |
| C-003 · Consulta de solicitudes | COCOMO II (grupo) | 239.4 | 306.0 | 22.745.591 | 29.071.615 |
| C-004 · Avisos por correo | COCOMO II (grupo) | 143.7 | 183.6 | 13.647.354 | 17.442.969 |
| C-005 · Configuración del acceso corporativo | Actividades externas | 38.0 | 60.0 | 4.560.000 | 7.200.000 |
| **Total** | Sin coberturas duplicadas | **995.7** | **1284.1** | **95.542.363** | **123.486.460** |

COCOMO cubre el software nuevo C-001…C-004, incluidos diseño, código, pruebas y gestión técnica. C-005 es solo configuración de un conector soportado existente; su consumo por la aplicación ya está en el grupo de software. Si exige código propio o sus actividades ya estaban cubiertas, hay que revisar la matriz antes de sumar.

## Equipo y tarifas ficticias

| Rol agrupado | Personas | Horas efectivas/semana | Tarifa COP/hora |
| --- | --- | --- | --- |
| Ingenieria | 1 | 30 | 100.000 |
| Calidad | 1 | 30 | 80.000 |
| Plataforma | 1 | 15 | 120.000 |

El reparto de esfuerzo software es 75 % Ingeniería (diseño, código y gestión técnica) y 25 % Calidad. Es una regla ficticia expresamente elegida para el ejemplo; no sale de COCOMO ni es un estándar aprobado. C-005 usa Plataforma. No se añade una segunda partida de pruebas/gestión.

## Calendario por componente

Semanas continuas desde el inicio, con la disponibilidad efectiva declarada, sin vacaciones adicionales ni esperas externas. C-005 precede el acceso; C-002 espera C-001 probado; C-003/C-004 esperan C-002. Ingeniería trabaja C-003 antes de C-004 y puede solaparse con Calidad.

| Componente | Inicio base | Fin base | Duración base (semanas) | Duración conservadora (semanas) |
| --- | --- | --- | --- | --- |
| C-001 | 2.5 | 10.5 | 8.0 | 10.2 |
| C-002 | 10.5 | 21.7 | 11.2 | 14.3 |
| C-003 | 21.7 | 29.7 | 8.0 | 10.2 |
| C-004 | 27.7 | 32.5 | 4.8 | 6.1 |
| C-005 | 0.0 | 2.5 | 2.5 | 4.0 |

Las duraciones por componente no se suman: C-003 y C-004 se solapan parcialmente. El script verifica precedencias y ausencia de sobreasignación por persona/rol.

Como contraste, la referencia nominal de duración COCOMO del grupo software es 28.6 semanas base y 30.9 conservadoras (convención 52/12 semanas/mes). El calendario de recursos incluye además C-005 y sus restricciones; no se suman las dos duraciones del mismo software. Su coherencia debe revisarse con el experto.

## Anexo de cálculo reproducible

Early Design COCOMO II.2000 de referencia, sin calibración local: A=2,94; B=0,91. Los cinco factores nominales son PREC=3,72; FLEX=3,04; RESL=4,24; TEAM=3,29; PMAT=4,68. PERS, RCPX, PDIF, PREX, FCIL, RUSE y SCED se eligen explícitamente nominales (=1) solo para la demostración. Ninguno se tomó del porcentaje de madurez.

E = 0,91 + 0,01 × 18,97 = 1.0997. Base: 2,94 × 2^1.0997 = 6.300718 personas-mes; ×152 = 957.709079 horas-persona de software.

Se estima el grupo completo y luego se reparte por tamaño porque todos sus drivers son homogéneos en este caso simplificado. No se suman cuatro modelos independientes. Los tamaños base son 0,5 / 0,7 / 0,5 / 0,3 KSLOC para C-001…C-004; son hipótesis técnicas de ejemplo, no conversiones de XS o COSMIC. Conservador: 0,625 / 0,875 / 0,625 / 0,375 KSLOC. Sin adaptación, código autogenerado ni modelo de reuso.

Para C-005 se separan actividades de servicio fuera de la cobertura software:

| Actividad de configuración | O (h) | M (h) | P (h) |
| --- | --- | --- | --- |
| Configuración del conector y permisos del servicio | 12 | 18 | 30 |
| Configuración de roles en el proveedor existente | 8 | 12 | 20 |
| Verificación del servicio configurado y evidencia de acceso | 4 | 6 | 10 |

Base C-005 = suma((O+4M+P)/6) = 38 h; conservador = suma(P) = 60 h. Costo = suma(horas de cada rol × tarifa). Ejemplo C-005 base: 38 × 120.000 = 4.560.000 COP. Los totales se calculan sin redondeos intermedios.

## Exclusiones y pendientes antes de usarlo en un proyecto real

| Código ilustrativo | Pregunta o entrega requerida |
| --- | --- |
| G-PRE-002 | ¿Qué método y evidencia de tamaño se aprobarán para el software real? |
| G-PRE-003 | ¿Qué parámetros/calibración y cobertura COCOMO se aprobarán? |
| G-PRE-004 | ¿Qué tarifas, reparto por roles y capacidad efectiva se aprobarán? |
| G-PRE-005 | ¿Qué costos directos, impuestos y margen incluirá el entregable comercial? |
| C-005-PRE-006 | ¿La solución de acceso puede resolverse solo configurando el conector existente? |

Códigos nuevos ilustrativos, posteriores a los del ejemplo A3; no son asuntos reales del piloto. G-PRE-001 sobre dedicación sigue siendo el mismo asunto del ejemplo previo: el conjunto de capacidades de esta demostración es una hipótesis, no su cierre real. Costos de nube/licencias y condiciones comerciales están por confirmar: el total mostrado solo es mano de obra.

## Fuentes y reproducción

Datos ficticios: `ejemplos/a4/entradas.json`. Ejecutar `python scripts/ejemplo_a4.py` reproduce este informe y verifica reconciliación, precedencias y recursos. No modifica el estado del piloto ni habilita COCOMO en el motor.

Referencia: USC, *COCOMO II Model Definition Manual* v2.1, secciones 1.2, 3.3, 4 y 8. [Texto del manual reproducido](https://studylib.net/doc/11638144/cocomo-ii-model-definition-manual-version-2.1). Las hipótesis de este ejemplo no son recomendaciones de esa fuente.

**Aprobación:** pendiente. Este documento explica una propuesta metodológica, no autoriza una ejecución real.
