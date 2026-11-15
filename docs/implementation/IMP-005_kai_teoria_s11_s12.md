# IMP 005 Recorrido teórico de Kai G05

**Fecha:** 13 de noviembre de 2026, Lima. **Grupo:** G05 Santa Elena. **Estado:** VALIDATED técnicamente; aceptación conversacional pendiente.
**Responsable de la instrucción:** DD. **Implementación asistida:** Kai.
**Rama:** `codex/kai-g05-teoria-s11-s12`. **Base Git:** `7825c2110a111193eb8e069c6358baa0dca0eb3e`.

## Problema y objetivo

La ruta histórica de siete pasos interpreta el modelo existente. El contenido aprobado requiere ocho competencias del proceso de exploración al modelo preliminar, teoría de estimación, propiedades S11 y escenarios conceptuales S12. Sustituir números de paso reinterpretaría evidencias existentes y el esquema histórico no admite un octavo paso.

Se incorpora la base corregida R5.3.1 y se desarrolla un recorrido teórico versionado, con continuidad local separada, materiales visuales y criterios formativos. No se calculan nuevos resultados geológicos ni económicos del grupo. La comprensión de teoría se mantiene separada de la existencia de un producto técnico validado.

## Entradas y salidas previstas

Entradas: propuesta pedagógica y revisión HTML de DD del 13 de noviembre; guía visual recibida; base factual G05; ruta y registro R5.3.1; referencias y supuestos PT-01. Las unidades son m, %, g/t, t/m³, t, t/d, min y USD según cada contenido. Los números del ejercicio son supuestos académicos identificados.

Salidas: contenido E1/S11/S12, perfil del agente, guía visual local, registro SQLite y vista Excel V2 por alias. El registro no autentica personas ni evalúa semántica automáticamente; el tutor debe valorar el razonamiento. La ejecución de un test sintético no acredita comprensión humana.

## Decisiones de diseño

- DECISION-01: conservar `kai/registro.py`, `kai/ruta_g05.json` y `kai/config_g05.json` como V1, sin reinterpretarlos.
- DECISION-02: usar `kai/registro_v2.py` y `teoria_v2.sqlite` separados dentro del directorio individual. El historial V1 se consulta en modo solo lectura si está presente. No se copian historiales personales al worktree ni al paquete.
- DECISION-03: registrar conceptos y checkpoints de las etapas por identificadores textuales y versión de ruta. La habilitación de S12 teórica no afirma que exista un producto S11 grupal; se identifica como recorrido conceptual sin resultados de G05.
- DECISION-04: reutilizar la guía recibida y completar sus temas; conservar decisiones de compositación y bloques G05 y supuestos PT-01. No se desarrolla un estimador minero nuevo.

## Etapas reales de implementación

1. Se comprobaron repositorio, instrucciones protegidas y HEAD remoto G05. La rama fuente sigue en el commit indicado.
2. Se creó un worktree y una rama nueva, manteniendo las copias piloto originales. Se registraron hashes antes del cambio en un expediente externo.
3. Se incorporaron los archivos de ejecución y visualización del piloto R5.3.1, sin `.kai_local` ni carpetas QA. Se preservaron las reglas de gobernanza del repositorio G05 y se guardó el perfil anterior como referencia histórica.
4. Se documentaron problema, entradas, salidas, alcance y decisiones antes de desarrollar el registro V2 y el contenido.
5. Se incorporaron las ocho competencias iniciales, dieciséis unidades S11 y seis S12 desde la propuesta revisada, con preguntas, criterios, pistas y recursos. Se conservaron los parámetros PT-01 en una referencia separada, sin ejecutarlos sobre el modelo.
6. Se implementó continuidad V2 por alias con identidad y versión de ruta, etapas, evidencia, checkpoints, memoria social consentida, idempotencia y Excel separado. Se corrigió el cierre explícito de conexiones SQLite observado durante las pruebas Windows.
7. Se actualizó el perfil activo y se completó la guía visual: bloques, continuidad, propiedades, vacíos, escenarios y elección antes de revelar el método. Se encuadraron los logos mediante CSS sin editar los PNG.
8. La regresión aislada requirió incorporar el helper de bloqueo que usaban los tests V1 y unificar UTF-8 entre procesos. Se preservaron motor y tests históricos. Con el entorno completo pasaron 50 pruebas.
9. Se verificó el transporte JSON independiente de la consola y el rechazo de tipos de solicitud incorrectos. Las 16 pruebas V2 volvieron a pasar tras ese ajuste.
10. Chrome pasó los diez controles de la guía sin red y se revisaron las seis capturas. Se prepararon documentación de uso y protocolo de aceptación humana.

## Lógica minera y arquitectura

El recorrido separa observación, modelo preliminar, estimación didáctica y escenario conceptual. Mantiene compositado G05 de 2 m y bloques de 50 × 50 × 10 m; IDW² es el método previsto de la misión PT-01. El registro de comprensión no genera leyes, densidad, toneladas, candidatos o reservas. Los productos grupales permanecen no verificados y S12 conceptual se identifica como ejemplo PT-01.

`config_g05_v2.json` selecciona contenido e identidad. `ruta_g05_v2.json` y `misiones_g05_v2.json` definen las unidades. `registro_v2.py` valida solicitudes, conserva eventos y checkpoints anexados, obtiene la actividad pendiente y exporta Excel. Reutiliza únicamente la función de escritura XLSX del motor V1, sin operar sus tablas o exportar su historial. `parametros_pt01_v2.json` documenta supuestos y no configura un nuevo estimador.

## Archivos de la integración

Perfil `.github/agents/kai-planeamiento.agent.md`; `kai/*_v2.json` y `kai/registro_v2.py`; guía `docs/guia_visual_estimacion.html`; teoría, referencia de plan y perfil histórico en `docs/learning/`; inicio y documentación R6; prueba `tests/test_teoria_v2.py`, helper de bloqueo histórico y scripts de validación. El README y `.gitignore` del checkout fuente se ajustaron para entrada al recorrido y exclusión de registros locales. El visor del piloto recibió únicamente un enlace a la guía. El expediente final contiene la lista completa y hashes.

## Pruebas y validación

`python scripts/validar_kai_teoria.py`: **50/50 PASS** en copia temporal, incluyendo 34 pruebas V1 y 16 V2. `python -m unittest discover -s tests -p test_teoria_v2.py -v`: **16/16 PASS** después del ajuste final de transporte. `node scripts/qa_guia_teoria.cjs ...`: **10/10 controles PASS** en Chrome, sin solicitudes de red, con seis capturas inspeccionadas.

Validación minera de alcance: se contrastan los parámetros con las fuentes PT-01 y se conserva la distinción entre las geometrías G05 y DS00, falta de soporte y cero, centro de celda y volumen de bloque, candidatos y reservas. Los ejemplos de flota y costos mantienen sus unidades y sus limitaciones. No se presenta esto como validación cuantitativa de un modelo G05.

Prueba humana conversacional: **NOT RUN**, protocolo preparado en `docs/PROTOCOLO_HUMANO_KAI_R6.md`. Esta limitación mantiene separado el dictamen técnico de la aceptación pedagógica. El módulo no se declara CLOSED ni se publica.

## Límites

No hay leyes, densidades o tonelajes de bloque G05 verificados en esta implementación. El recorrido teórico y sus ejemplos no los sustituyen. La aceptación conversacional en Copilot/PyCharm requiere observación humana y se reportará aparte. No se modifican fuentes raw, algoritmos geológicos, visores originales ni gobernanza. No se ha realizado commit, push ni despliegue.

## Uso de IA

Kai asiste en contenido pedagógico, integración de continuidad, pruebas, revisión de unidades, documentación y paquete de auditoría.
