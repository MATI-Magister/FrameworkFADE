# Estimación preliminar · <nombre del proyecto>

Estado: <borrador / para revisión / aprobado por responsable> · Fecha: <fecha>
Reglas utilizadas: <versión> · Moneda: <moneda / por confirmar>

## Resultado en palabras
Explicar qué solución se estimó, sus principales factores de esfuerzo y el nivel de
incertidumbre. Indicar si faltan datos que impidan calcular costos o duración.

## Comparación de escenarios
| Escenario | Esfuerzo (horas-persona) | Duración aproximada (semanas) | Costo de ejecución (<moneda>) |
| --- | --- | --- | --- |
| Base | <valor> | <valor/rango o por confirmar> | <valor o por confirmar> |
| Conservador | <valor> | <valor/rango o por confirmar> | <valor o por confirmar> |

Explicar en palabras qué cambia entre escenarios y qué condiciones mantienen.
No presentar el conservador como garantía o probabilidad estadística.

## Qué estamos estimando
Alcance incluido y exclusiones; identificar las versiones de los componentes.

| Componente | Trabajo considerado | Horas base | Horas conservadoras | Costo base (<moneda>) | Costo conservador (<moneda>) |
| --- | --- | --- | --- | --- | --- |
| <C-001 · nombre> | <descripción breve> | <valor> | <valor> | <valor/por confirmar> | <valor/por confirmar> |
| Total | <sin duplicar transversales> | <total> | <total> | <total/por confirmar> | <total/por confirmar> |

## Equipo y calendario considerado
Roles, disponibilidad efectiva, dependencias, paralelismo y esperas. Explicar cómo
se obtuvo la duración. Indicar si solo existe un límite inferior, sin prometer fechas.

| Componente | Inicio base | Fin base | Duración base (semanas) | Duración conservadora (semanas) | Dependencias / esperas |
| --- | --- | --- | --- | --- | --- |
| <C-...> | <semana/fecha> | <semana/fecha> | <valor/por confirmar> | <valor/por confirmar> | <referencias> |

El fin del proyecto corresponde a la última actividad. Las duraciones de componentes
que se solapan no se suman. Verificar capacidad por persona y dependencias en ambos
escenarios; contrastar con referencia de duración COCOMO cuando corresponda.

| Componente | Rol | Horas base | Horas conservadoras | Tarifa (<moneda>/hora) | Costo base (<moneda>) | Costo conservador (<moneda>) |
| --- | --- | --- | --- | --- | --- | --- |
| <C-...> | <rol> | <valor> | <valor> | <valor/por confirmar> | <valor/por confirmar> | <valor/por confirmar> |

Fundamentar el reparto por roles y reconciliar con los totales de componente.

## Supuestos, riesgos y decisiones pendientes
| Código PRE/PEN si aplica | Condición | Efecto en el resultado | Tratamiento o decisión requerida |
| --- | --- | --- | --- |
| <ID existente o nuevo según registro> | <condición> | <impacto> | <responsable, estado y acción> |

## Costos adicionales y condiciones económicas
Licencias, servicios, impuestos y margen, según lo acordado. Distinguir costo de
precio comercial. «Por confirmar» no equivale a cero ni a incluido.

## Anexo · Cómo calculamos
Primero explicar el método principal y su cobertura por componente/actividad.
Para COCOMO II declarar variante, tamaño y conversión, factores, calibración,
personas-mes, paso a horas, fases y reparto reconciliado. No usar el porcentaje
de madurez como multiplicador ni sumar estimaciones alternativas del mismo trabajo.

| Componente / partida | Método principal | Fases o actividades cubiertas | Qué queda fuera | Fuente de las entradas |
| --- | --- | --- | --- | --- |
| <ID y partida> | <COCOMO / actividades / analogía> | <cobertura explícita> | <partidas separadas o exclusiones> | <referencias> |

Si falta estimar una parte, identificar el total como parcial sin reemplazarla por cero.
Si se aprueba juicio experto para trabajo fuera de cobertura, explicar O (bajo),
M (probable), P (alto); base = (O + 4 × M + P) / 6 y conservador = P solo para esas filas.

| Componente | Actividad | Rol | O (horas) | M (horas) | P (horas) | Fundamento del rango |
| --- | --- | --- | --- | --- | --- | --- |
| <código> | <actividad> | <rol> | <valor> | <valor> | <valor> | <tareas, referencia o juicio experto> |

Referenciar tarifas, capacidad, operaciones verificadas y archivo reproducible.
Explicar redondeos, versión/huella de reglas y fuentes sin saturar el resumen.

## Revisión y aprobación
Responsable, observaciones y decisión explícita; pendiente hasta su aceptación.
