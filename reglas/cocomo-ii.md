# COCOMO II en A4 · propuesta sin aprobar

## Aplicación propuesta

Usar un método híbrido según cobertura. Para software con tamaño defendible y
parámetros disponibles, evaluar COCOMO II. Para configuración, infraestructura,
investigación de IA, adopción u otro trabajo no cubierto, usar descomposición o
analogía con fundamento. Elegir por entradas reales, no solo por arquetipo.
La madurez informa si podemos parametrizar el método; no es un multiplicador.

El manual USC distingue Early Design (alternativas tempranas) y Post-Architecture
(arquitectura y drivers detallados). Propongo revisar primero Early Design por el
momento del requerimiento, sin activarlo automáticamente por alcanzar N4/N5.

## Entradas pendientes

Tamaño en miles de líneas fuente (KSLOC), o conversión funcional documentada y
adecuada; cinco factores de escala; multiplicadores de la variante (siete en Early
Design, diecisiete en Post-Architecture); tratamiento de nuevo/adaptado/reuso;
calibración y cobertura de fases. No asignar nominales silenciosamente.

El Excel usa conceptos COSMIC; el manual COCOMO II documenta puntos de función
no ajustados IFPUG y conversión a líneas. No sustituir una unidad por otra ni
inventar conversión universal. Declarar método de tamaño, lenguaje/tecnología y
procedencia de conversión, o dejar la ruta COCOMO pendiente.

## Cálculo y consolidación

Caso básico: esfuerzo personas-mes = A × Size^E × producto(EM), con
E = B + 0.01 × suma(SF). A/B y tablas deben pertenecer a una calibración identificada.
Adaptación/reuso/traducción requieren sus reglas, no un descuento lineal de esfuerzo.
Antes de estimar múltiples componentes aplicar la agregación del manual: la escala
no lineal impide sumar sin más modelos independientes. Explicar el reparto por
componente y reconciliarlo con el total. Tampoco inventar un reparto por roles.

Personas-mes no son meses calendario. Declarar conversión a horas, fases incluidas
y calendario; si se utiliza la ecuación de duración, acordar sus parámetros.

Registrar componente/actividad, método principal, fases cubiertas y partidas extra.
Una descomposición del mismo trabajo sirve de contraste: **no se suma** a COCOMO.
Solo añadir trabajo fuera de cobertura una vez. Comprobar antes si gestión, pruebas,
análisis o despliegue ya están incluidos. Los escenarios declaran qué entradas
cambian manteniendo alcance. O/M/P queda como propuesta para trabajo por juicio
experto; no agregarlo automáticamente encima de COCOMO ni duplicar contingencia.

## Estado

La ruta está documentada en agentes y protocolo. El calculador local de madurez
sí está implementado; **no hay aún calculador COCOMO II habilitado**. Faltan variante,
tamaño/conversión, tablas, calibración, cobertura de fases y datos operativos.
A4 sigue bloqueado hasta aprobar reglas y completar sus entradas.

Existe una demostración separada: `scripts/ejemplo_a4.py`, con entradas ficticias
en `ejemplos/a4/entradas.json`. Enseña un grupo homogéneo de software nuevo, reparto
por tamaño con drivers comunes y actividades externas sin doble conteo. No habilita
una implementación productiva ni cubre modelos de adaptación/reuso o casos heterogéneos.
El procedimiento A4 para revisión está en `a4-estimacion.md`.

## Fuentes

USC Center for Software Engineering, *COCOMO II Model Definition Manual*, v2.1,
secciones 1–3 y 8: [manual en copia académica](https://llavoie.espaceweb.usherbrooke.ca/llavoie/enseignement/References/CocomoII_Model_Manual.pdf).
Índice web consultado el 17 de octubre de 2026; descarga directa no disponible
en esta sesión. Antes de incorporar tablas numéricas verificar la edición completa.
[Manual de implementación USC](https://llavoie.espaceweb.usherbrooke.ca/llavoie/enseignement/References/CocomoII_Reference_Manual.pdf)
para variantes y multiplicadores.

Se pudo consultar después el [texto reproducido del manual USC v2.1](https://studylib.net/doc/11638144/cocomo-ii-model-definition-manual-version-2.1),
secciones 1.2, 3.3, 4 y 8, para ecuaciones, agregación y conversión de unidades del
ejemplo didáctico. Los tamaños, reparto por rol, capacidades y tarifas son hipótesis
propias de demostración, no valores de ese manual ni decisiones aprobadas.
