# Expedientes locales

Cada subcarpeta representa un proyecto independiente. Crear uno con `!nuevo <id>`
o `python scripts/framework.py init <id>`. La instalación crea `piloto` si no existe.

El portal descubre todas las carpetas directamente bajo `proyectos/`. Muestra
estado del flujo, próxima etapa y rutas de evidencia. Las carpetas sin estado se
identifican como «Sin inicializar»; los estados dañados quedan visibles como error.
Consultar el portal no crea, repara ni aprueba expedientes.

```text
01-entradas/requerimientos/   Originales del cliente
01-entradas/contexto/         Arquitectura, equipo y restricciones
01-entradas/respuestas/       Respuestas del experto con sus códigos
02-trabajo/                  Evaluaciones, cálculos y rondas
03-entregables/              Registro, A1–A4, cierre, revisión e informe cliente
04-estado/                   Estado, snapshots de reglas e historial
```

Git ignora íntegramente los expedientes; este README sí se versiona. El repositorio
distribuye el framework, no los datos de clientes. Respaldar los expedientes por
el mecanismo acordado; no quitar la exclusión para subir documentos reales.
