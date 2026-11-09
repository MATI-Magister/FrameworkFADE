# Modelo activo de información B.1

Elegido por el usuario el 2026-11-02. Fuente: rúbrica e instrucciones de evaluación
del ZIP; extracción portable en modelo-informacion.json. La elección reemplaza A1
del Excel, no borra sus fuentes, resultados pasados ni catálogo de clasificación.

20 criterios de 0 a 3 en D1, D2, D3, D4, D5, D6, D7, D8 y D10. Pesos de dimensión:
12, 11, 18, 15, 14, 5, 5, 7 y 3 (suman 90 y se normalizan). Pesos por criterio 3,
salvo D4.4, D5.3 y D6.1 que pesan 2. Los descriptores se conservan completos en JSON.

Para cada dimensión: puntos obtenidos / puntos posibles. General: promedio de
porcentajes por sus pesos, redondeado a una decimal como el verificador del ZIP.
Baja <40 %; media 40–<67 %; alta ≥67 %. Si alguna núcleo D1–D5 está bajo 40 %,
un resultado alto pasa a medio. Un resultado ya bajo permanece bajo.

Las complementarias aplicables sin información cuentan como cero. Solo se excluyen
si realmente no aplican, con motivo; las núcleo no se excluyen. Una plantilla vacía
queda «Sin evaluar», aunque la aritmética provisional tenga cero. No es un análisis
terminado. D9/D11 se consideran en experiencia, fuera de este porcentaje.

## Evidencia y preguntas

Puntaje mayor que cero requiere evidencia. Techo por dato: equipo/no identificado
o declaración verbal sin confirmar = 1; documento escrito por cliente = 2;
confirmación explícita directa del cliente, con cita escrita o en sesión = 3.
Cada dato que sustenta el criterio se registra en evidence_items; aplica el mínimo
techo de esos datos. D6.1 permite conocimiento interno de activos según descriptor,
con fuente. Una nota «el cliente confirmó» no es la confirmación del cliente.

El validador comprueba estructura, origen y techo; no comprueba automáticamente que
una cita existe y significa lo afirmado. El estructurador y experto revisan los
originales. La cita de confirmación debe corresponder exactamente al dato evaluado.

Prioridad = (3−puntaje) × peso interno / máximo dimensión × peso dimensión /
pesos incluidos × 100. Si el tope impide alta, atender primero núcleos que lo causan;
después mayor prioridad y núcleo en empate. Incluir todas las preguntas necesarias, con
códigos separados del texto natural. Las demás brechas, preguntas internas y
contradicciones siguen en el soporte de la ronda. Generar supuestos ante 0/1 para
revisión humana; no convertir una falta de información en una decisión tomada.

## Uso

python scripts/madurez.py --project <id> template

Completar 01-entradas/respuestas/evaluacion-madurez.json con evidencia. Cada
evidence_item lleva source, location, quote, author y medium. Si confirmed=true,
confirmation lleva source, location, quote, author=cliente y medium. Si medium=sesion, tanto el dato verbal como su confirmación
requieren speaker con nombre o rol identificado del cliente; no se cuentan sesiones. Para 3,
identificar validated_by (salvo D6.1). Usar applicability para excluir dimensiones.

python scripts/madurez.py --project <id> evaluate

El cálculo conserva rondas e informe en 02-trabajo/. A1 debe presentar resumen y
preguntas antes de finish; !aprove a1 solo lo decide el experto. No hay equivalencia
automática N3→media o N4→alta ni paso automático por nivel.
