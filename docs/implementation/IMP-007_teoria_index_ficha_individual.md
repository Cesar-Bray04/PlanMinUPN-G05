# IMP-007 · Teoría visible en el índice y ficha de datos individual

## Problema y corrección

El `index.html` recibido de R6 abría el recorrido del modelo G05; la teoría de ocho métodos geoestadísticos estaba en `docs/guia_visual_estimacion.html`, enlazada debajo de la navegación. El ajuste IMP-006 dejó `index.html` idéntico. La guía no desapareció, pero el alumno podía recorrer el índice sin encontrar la comparación central de S11.

Ahora `index.html#teoria` es una pantalla visible en la navegación y en la portada. Integra la guía existente mediante un `iframe` local y ofrece abrirla en pantalla completa. No se editó la guía ni el HTML de la vista 3D original. Kai lleva primero al alumno a esta pantalla al comenzar S11 y vuelve al visor G05 para reconocer la ausencia de leyes de bloque.

## Entregable individual

`kai/ficha_individual_g05.json` define 21 campos visibles en las pantallas del índice, con pregunta, pantalla, tipo, unidad y referencia al resumen verificado. El resumen se fija por SHA-256 y commit fuente. `kai/ficha_individual.py` guarda cada intento en un SQLite local por alias, compara el valor propuesto con el resumen y escribe en `Ficha_Individual_G05.xlsx` **solo valores correctos**. Una respuesta incorrecta conserva el campo pendiente y devuelve una pista. El alumno no tiene que abrir ni editar el Excel. El archivo está listo para entregar únicamente tras los 21 valores aprobados.

La ficha y el SQLite se guardan en `.kai_local/<alias>/`; no deben incorporarse al repositorio del grupo. La plantilla `kai/PLANTILLA_Ficha_Individual_G05.xlsx` se distribuye vacía. Esta ficha es independiente del Excel V2 de bitácora teórica. Los 459 datos de densidad corresponden a muestras; no se inventan leyes, densidades o tonelajes por bloque.

La solicitud temporal `.kai_solicitud_ficha_g05.json` se excluye mediante `.gitignore`, igual que los archivos locales por alias.

## Comprobaciones y límites

- 24 pruebas específicas de ficha y ruta teórica pasan en este entorno, incluyendo respuesta errónea, respuesta correcta, separación de alias, 21 campos completos, bloqueo por resumen alterado y presencia de la guía en el índice.
- La prueba ampliada de 72 casos no cerró aquí: faltan `pytest` y `plotly` en el intérprete del entorno, y dos pruebas de bloqueo de Excel dependen de Windows. No se atribuye a esta entrega una validación de esas pruebas.
- Se examinó la plantilla renderizada y la tabla muestra los valores vacíos hasta su aprobación.
- La navegación y carga del `iframe` no pudieron comprobarse visualmente en un navegador de este entorno. Falta esa inspección en el Chrome local del docente, así como una conversación real en Copilot/PyCharm con una respuesta correcta y otra incorrecta.
- El paquete de aplicación verifica el hash del índice y de los archivos R6 previos. Si el checkout del docente contiene otro índice aprobado, se detiene sin sobrescribirlo; requiere comparación manual con esa versión.

No se modifican los datos mineros, el visualizador 3D, los historiales V1/V2 ni las decisiones PT-01. No hay commit ni push en esta entrega aislada.
