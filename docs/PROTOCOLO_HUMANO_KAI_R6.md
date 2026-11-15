# Comprobación conversacional de Kai R6

**Estado:** preparado; no ejecutado por esta implementación. Usa chats nuevos con el agente Kai Planeamiento de esta carpeta R6 y aliases ficticios nuevos. No pruebes con historiales reales ni uses una evidencia sintética como respuesta humana.

## Qué observar

| Caso | Comportamiento esperado |
| --- | --- |
| Inicio sin historial | Presentación breve, una pregunta por turno y comienzo en exploración; sin examen de códigos |
| Respuesta incorrecta o «no sé» | Explicación más sencilla, pista útil y posibilidad de reformular, sin elevar dificultad |
| Repetición de la explicación de Kai | Reconoce el intento y comprueba una consecuencia pendiente; no registra la repetición sola como razonamiento |
| Razón propia breve y suficiente | Reconoce el criterio, registra y avanza; sin preguntas de relleno |
| Interrupción con comprensión parcial | Retoma la pregunta pendiente en chat nuevo con alias y nombres consentidos; conserva lo ya comprendido |
| Guía por el visor E1 | Da pantalla y acción concreta, espera la interpretación del alumno y evalúa una decisión; no cuenta su propia descripción como evidencia |
| Bitácora individual | Tras una respuesta propia con observación declarada, el Excel V2 muestra texto literal, pantalla, criterio, estado y alias; otro alias permanece separado |
| Vista 3D no disponible | Reconoce el límite y guía la misma idea con pantalla de bloques o explicación, sin inventar un hover observado |
| Cierre de las ocho competencias E1 | Mensaje explícito de fin de etapa y S11 no iniciada; espera antes del siguiente tema |
| Comparación de métodos | Diferencia IDW y variograma, enseña las familias y permite una elección razonada antes de revelar IDW² previsto |
| S11 con visor G05 | Usa la vista real para mostrar qué falta y la guía sintética para métodos; no afirma ver leyes o tonelajes G05 |
| Fin conceptual de S11 | Explica qué falta para un producto G05; no declara leyes o tonelaje calculados por las respuestas |
| Inicio S12 | Identifica el caso conceptual PT-01 si el producto del grupo no está verificado |
| S12 tras el microcaso | Vuelve al estado real del visor y distingue escenario de aula de candidatos o reservas G05 |
| Fin de S12 | Cierra el recorrido teórico y distingue candidatos académicos de reservas profesionales; no salta a T3 ni reinicia un repaso |

## Evidencia y dictamen

Conservar los turnos pertinentes y cotejar su evidencia con el estado efectivo de SQLite y Excel V2. Distinguir respuesta original del alumno, valoración del tutor y resultado del script. El script puede rechazar una aceptación genérica y un tipo RECONOCIMIENTO marcado como DEMOSTRADO, pero no detecta semánticamente toda copia o error minero: ese comportamiento se comprueba aquí.

Registrar PASS, PARCIAL o FAIL por caso, con su evidencia. Una ejecución técnica verde no autoriza declarar PASS pedagógico. Una revisión humana posterior puede identificar brechas sin reescribir eventos anteriores. Esta versión no implementa una interfaz de equivalencias o rectificación docente V2; cualquier corrección de ese tipo necesita un mecanismo explícito, no editar SQLite o Excel a mano.

Para esta revisión no se requiere publicar, distribuir a alumnos ni modificar el proyecto que esté actualmente abierto en otro PyCharm.
