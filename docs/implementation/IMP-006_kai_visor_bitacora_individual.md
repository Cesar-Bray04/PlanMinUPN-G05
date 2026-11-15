# IMP-006 · Visor guiado y bitácora individual V2

## Motivo

En R6 Kai enlazaba el visor G05, pero la ruta no especificaba qué pantalla abrir ni qué hacer allí antes de responder. El Excel V2 contenía resumen, eventos y checkpoints, sin una hoja de trabajo individual que reuniera escena, evidencia y valoración por actividad. La plantilla existente de siete pasos pertenece a V1 y se conserva.

## Decisión aplicada

- Diecisiete actividades V2 tienen `visor` con enlace a una pantalla existente de `index.html`, acción concreta y pregunta vinculada con el criterio. E1 lo usa durante todo el recorrido; S11 y S12 vuelven al modelo real para comprobar su alcance. Las fichas geoestadísticas y escenarios de la guía HTML siguen explícitamente sintéticos.
- El perfil pide usar la acción visual antes de la decisión y escuchar la interpretación del alumno. Si el 3D no carga, Kai usa otra representación del mismo concepto sin afirmar que vio la escena. Una respuesta suficiente previa no se repite solo para abrir el visor.
- El Excel derivado V2 agrega `Bitacora individual` con una fila por cada una de las 30 actividades. Muestra recurso, acción, última evidencia literal, criterio o comprensión parcial, estado y pendiente. El alumno no edita este libro; SQLite sigue siendo canónico.
- `observacion_visor` es un dato opcional de `registrar`: se guarda únicamente si el alumno dijo qué observó en una actividad con visita al visor. No se extrae artificialmente de la respuesta ni de lo que Kai describió. Los registros V2 anteriores incorporan la columna vacía sin reescribir eventos. La respuesta literal original permanece en su columna.
- `kai/PLANTILLA_Individual_Kai_G05_V2.xlsx` es la referencia vacía y anónima. El archivo que Kai llena por alias sigue siendo `.kai_local/<alias>/Progreso_Kai_G05_Teoria_V2.xlsx`. La plantilla grupal se abordará en otro trabajo.

## Comprobación y límites

El test V2 comprueba enlaces a pantallas existentes, plantilla de 30 actividades, exportación literal y aislamiento de alias, rechazo de una observación atribuida a una actividad sin visor y migración de una base V2 anterior. Las pruebas técnicas no acreditan que Copilot/PyCharm conduzca bien la conversación; el protocolo humano ahora incluye escenas E1, ausencia de 3D, uso de G05 frente a ejemplos sintéticos y comprobación de la bitácora.

No se han calculado leyes, densidades, tonelajes ni candidatos G05. El visor sigue siendo el modelo preliminar. V1, los datos mineros y los visores originales no se modifican. La disponibilidad de enlaces locales dentro del chat de Copilot debe comprobarse en el IDE; si no son clicables, Kai indica el nombre de la pantalla del mismo `index.html`.
