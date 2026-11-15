# Kai Planeamiento · primera sesión G05

> Referencia histórica del recorrido R4/V1 de siete pasos. La tutoría activa R6 usa la ruta V2 y la [guía de inicio](INICIO_KAI_R6.md). Las exigencias administrativas de esta tabla no son criterios de la ruta activa.

**Objetivo de la sesión:** reconocer Santa Elena, seguir la procedencia de los datos y explicar el alcance del modelo preliminar que el grupo ya construyó. Esta ruta prepara contenido y referencias visuales; **no programa ni modifica el agente**. Se apoya en [`BASE_CONOCIMIENTO.md`](BASE_CONOCIMIENTO.md) y en las siete pantallas de [`index.html`](index.html).

**Antecedente académico de Fase 01:** adapta la recuperación P0 del modelo T2 y el núcleo conceptual S11.1 («¿Qué sabemos realmente de cada bloque?»). Sirve como puente previo de comprensión. Su producto formal, puntuación y relación con el plan semanal de S11/S12 quedan para decisión de DD; esta ruta no cambia el contrato PT-01.

**Secuencia por actividad:** refuerzo teórico breve → observación visual → una pregunta sencilla → interpretación del alumno → comprobación con la fuente visible → avance. Kai espera la respuesta antes de continuar. Un error recibe una pista y un nuevo ejemplo; no se marca comprensión por abrir una pantalla.

| Paso | Refuerzo y observación | Pregunta principal de Kai | Comprensión que se comprueba |
|---|---|---|---|
| **1. Reconoce tu proyecto** · [Nuestro proyecto](index.html#proyecto) | «Trabajamos G05, Santa Elena, DS05/EXP03. El modelo es preliminar.» Señalar los cuatro indicadores y la cadena de construcción. | «¿Qué hemos construido hasta ahora: un modelo preliminar de bloques o un plan de extracción?» | Identifica grupo, dataset y release; distingue modelo preliminar de plan minero. |
| **2. Sigue las observaciones** · [Nuestro proyecto](index.html#proyecto) y [Nuestros datos](index.html#datos) | Observar las 44 trayectorias 3D en la portada y distinguir las tres campañas por color; explicar en pocas frases collar, survey, ensaye y medición de densidad. | «¿La densidad mostrada aquí ya es densidad de cada bloque?» | Responde que son **459 observaciones de muestra**, sin estimación de bloque; los trazos 3D representan sondajes, no sólidos geológicos. |
| **3. Comprende el posicionamiento** · [Nuestros datos](index.html#datos) | Seguir la cadena collar → survey → desurvey → intervalo XYZ. | «¿Por qué necesitamos la trayectoria antes de dibujar un intervalo litológico en 3D?» | Relaciona profundidad medida con posición espacial calculada, sin afirmar continuidad geológica. |
| **4. Lee el compositado** · [Compositado](index.html#compositado) | Mostrar el caso real SE-C01-001 entre 8 y 13 m, contacto a 9 m y compósito residual 8–9 m. | «Si el objetivo es 2 m, ¿por qué conservamos el compósito 8–9 m de solo 1 m?» | Explica que el contacto separa códigos observados; no se mezclan para completar longitud. |
| **5. Interpreta la malla** · [Modelo de bloques](index.html#bloques) | Señalar 50 × 50 × 10 m, forma 15 × 14 × 55 y estados ROCK/AIR/PARTIAL. | «¿PARTIAL nos dice cuántos metros cúbicos de roca contiene ese bloque?» | Responde que identifica cruce de topografía, sin fracción volumétrica calculada. |
| **6. Lee la asignación y el 3D** · [Modelo de bloques](index.html#bloques) y [Vista 3D](index.html#tresd) | Comparar 978 asignados con 10 572 sin asignación. En el 3D, alternar capas y señalar un bloque por hover. | «Si un bloque queda UNKNOWN/UNASSIGNED, ¿podemos llamarlo ley cero?» | Distingue ausencia/conflicto de soporte litológico de una ley estimada. Comprende que el HTML incluye 11 550 bloques, aunque las capas visibles cambien. |
| **7. Explica el estado real** · [Decisiones](index.html#decisiones) y [Estado actual](index.html#estado) | Resumir una decisión documentada, un supuesto y dos límites. | «¿Qué dato o validación falta antes de afirmar que el modelo describe recursos o un plan de minado?» | Menciona al menos la falta de estimación y soporte/validación; conserva la cautela sobre Topopl, CRS/datum y códigos sin definición. |

## Evidencia esperada y condición de avance

La evidencia inicial es **oral/conversacional**: el alumno debe explicar con sus palabras (a) proyecto y release, (b) diferencia entre dato observado y resultado derivado, (c) por qué C2 conserva un residuo, (d) qué significan dimensiones y clases de bloque, y (e) una limitación técnica real. Kai puede formular **una sola pregunta por turno** y pedir una interpretación breve de la pantalla. Si falta una idea crítica, permanece en el paso y cambia el ejemplo.

El registro automático de respuestas en Excel y la continuidad entre sesiones pertenecen a una etapa posterior de implementación y validación; **este paquete no afirma que ya ocurran**. La aprobación formal de PT-01 y las calificaciones corresponden al contrato académico y a DD. Comprender un paso aquí no altera la nota ni equivale a aprobación docente.

## Pistas de corrección breve

- Si el alumno confunde compósito con bloque: «El compósito representa un tramo de sondaje. Mira el contacto a 9 m: ¿qué pasaría si mezcláramos OVB y VOL para completar 2 m?»
- Si confunde `UNKNOWN/UNASSIGNED` con cero: «El visor no tiene una columna de ley de bloque. ¿Qué información falta para escribir Cu en esa celda?»
- Si toma el 3D como validación total: «La figura muestra posiciones y códigos. ¿Qué límite conserva el panel de decisiones sobre continuidad geológica?»

## Fuentes internas que Kai deberá consultar al implementarse

1. [`BASE_CONOCIMIENTO.md`](BASE_CONOCIMIENTO.md) para los conceptos y límites.
2. [`datos/resumen_verificado.json`](datos/resumen_verificado.json) para indicadores y ejemplo.
3. [`procedencia/FUENTES_G05.json`](procedencia/FUENTES_G05.json) para identidad, commit y hashes.
4. [`VALIDACION.md`](VALIDACION.md) para saber qué funcionamiento se observó en Chrome.

Al alumno se le presentan **pantallas y explicaciones**, no rutas técnicas, JSON, comandos ni tareas de completar archivos.

## Apoyo visual R4

Antes de preguntar, mostrar la portada con trayectorias 3D del propio grupo. En decisiones, pedir al estudiante que distinga su elección documentada del procedimiento profesional general; no atribuirle una defensa pendiente. Esperar su respuesta antes de avanzar.
