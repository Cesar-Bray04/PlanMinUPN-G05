# Plan de integración controlada · Kai G05 · Etapa 1 → S11 → S12

**Fecha:** 13 de noviembre de 2026  
**Estado:** plan de implementación; no aplicado al repositorio estudiantil ni a PyCharm.  
**Base revisada:** corte aislado `QA_KAI_G05_R5_3_1_CORRECCION_CIERRE_WINSTON_AUDITORIA_20261112.zip`, ruta pedagógica G05 actualizada, guía visual HTML, PT-01 y misiones S11/S12.

## 1. Contrato y restricción comprobada

La etapa 1 termina tras ocho competencias: exploración, logueo, collar, survey, assay, compositación, geometría y modelo preliminar. El cierre habilita una etapa nueva, **S11 no iniciada**. S11 enseña y compara métodos de estimación antes de la corrida IDW² fijada en PT-01, y produce el modelo didáctico de recursos. S12 usa su resultado sustentado para seleccionar material candidato y comparar escenarios; el producto docente se llama modelo preliminar didáctico de reservas. El agente explica, pide una decisión razonada, ayuda si hace falta, muestra la decisión ya acordada, contrasta evidencia y avanza. No altera parámetros por la elección del alumno.

En el corte R5.3.1, `kai/registro.py` lee únicamente `kai/ruta_g05.json`, define `paso BETWEEN 1 AND 7` en las tres tablas académicas, exporta `Progreso_Kai_G05.xlsx` sin versión de ruta y devuelve `PREPARAR_T3` al cerrar los siete pasos. El perfil `.github/agents/kai-planeamiento.agent.md` nombra expresamente los siete pasos anteriores y el salto a T3. **Reemplazar `ruta_g05.json` por ocho pasos reinterpretaría los eventos de Luis y Winston, bloquearía el paso 8 en SQLite y produciría un Excel equívoco.**

El ZIP revisado es un corte **solo QA**, no la fuente vigente de distribución. Antes de programar se debe obtener el checkout actual del repositorio G05, fijar sus hashes y respaldar el registro local. No se debe copiar `.kai_local` de alumnos al repositorio.

## 2. Archivos y responsabilidades

| Pieza propuesta | Uso |
| --- | --- |
| `kai/ruta_g05.json` | Conservar la ruta histórica de siete pasos como V1, sin modificarla. |
| `kai/ruta_g05_v2.json` | Ocho pasos de la nueva etapa 1, con `route_id` y `route_version` explícitos y criterios de evidencia. |
| `kai/misiones_g05_v2.json` | S11.0, S11.1–S11.6 y S12.1–S12.6; decisiones fijadas en PT-01, ayudas y barreras técnicas. No duplicar cifras divergentes en el perfil. |
| `kai/registro.py` | Conservar la interfaz V1 para lectura histórica; agregar API V2 o un módulo separado con tablas/eventos versionados y selección explícita de etapa. Nunca convertir filas V1 en V2 por equivalencia numérica. |
| `.github/agents/kai-planeamiento.agent.md` | Sustituir instrucciones de «siete pasos → T3» por enrutamiento V1/V2, cierre de etapa 1, enseñanza S11–S12 y referencias al HTML. Mantener el trato cercano y la regla antirrepetición. |
| `docs/guia_visual_estimacion.html` | Copia exacta de la guía visual autocontenida; enlazarla en la guía estudiantil y abrir `#compositacion`, `#metodos`, `#decision` o `#limites` según el momento. |
| `INICIO_ESTUDIANTE_*.md` y guía docente | Explicar cómo retomar progreso, que la primera etapa cierra antes de S11 y que el HTML no califica ni guarda datos. |
| `index.html`, datos, procedencia, visores | Mantener sin cambios de ingeniería; son evidencia y apoyo visual. Un enlace discreto al HTML es opcional tras validar rutas relativas. |

## 3. Contrato de progreso propuesto

- Clave estable de cada evidencia: `(alias, route_id, route_version, etapa, actividad_id)`; `actividad_id` es texto (`E1.01`–`E1.08`, `S11.0`–`S11.6`, `S12.1`–`S12.6`). El entero `paso` V1 no identifica competencias V2.
- Guardar en tablas V2 separadas del esquema V1 (en el mismo SQLite del alias si es viable), con clave foránea lógica de etapa y huella que incluya la identidad de ruta. Mantener append-only para eventos y revisiones; las correcciones se anexan con procedencia.
- Estado inicial V2 de un alumno antiguo: `E1_NO_INICIADA`; su V1 se muestra como **historial previo**, nunca como aprobación automática de E1. Si DD reconoce un aprendizaje anterior, registrar una equivalencia docente individual con referencia, sin editar eventos V1.
- `E1_COMPLETADA` requiere las ocho evidencias suficientes y revisiones obligatorias resueltas. Después: `S11_NO_INICIADA`, sin formular una novena pregunta. `S11_COMPLETADA` requiere archivos y barreras PT-01 validados; solo entonces se habilita S12 con datos del grupo. Si faltan, usar microcaso sintético identificado expresamente.
- Exportar un Excel V2 con columnas de ruta, versión, etapa y actividad, separado del Excel histórico V1. SQLite sigue siendo canónico; no convertir la vista Excel en fuente de verdad.
- El HTML no escribe estado ni registra respuestas: Kai registra la evidencia conversacional y el contraste con archivos mediante el motor V2.

## 4. Secuencia de integración

1. **Preflight del G05 vigente.** Copia aislada del checkout actual, manifiesto de archivos y hashes, respaldo de SQLite/Excel, `PRAGMA integrity_check`, registro de la versión de PT-01 y comprobación de que existen las herramientas S11/S12 adaptadas a DS05. Los archivos documentados para DS00 no prueban ejecución grupal.
2. **Corte E1.** Incorporar la ruta V2, perfil y registro versionado. Ejercitar los ocho pasos con alias ficticio nuevo. Al cerrar, devolver solo `S11_NO_INICIADA` y un mensaje de transición. Comprobar que V1 de Luis y Winston devuelve exactamente sus estados anteriores.
3. **Puente S11.0.** Copiar el HTML al repositorio. Kai explica visualmente 2 m frente a 10 m y, sin fórmulas, vecino más cercano, IDW/IDW², kriging ordinario, simple, con tendencia y de indicadores, cokriging y simulación condicional. Una pregunta de aplicación por familia, sin exigir definiciones repetidas. Reconoce la elección razonada del alumno y comunica después IDW² como decisión de PT-01 para G05.
4. **S11.1–S11.6.** Verificar fuentes, ejecutar la estimación con dominio y soporte, densidad, tonelaje, sensibilidad 75/50 m y contraste CSV/3D. Usar parámetros propios del grupo y no la malla DS00. Conservar `null` cuando falte soporte. Cerrar el producto académico de S11 con sus cinco archivos y explicación del alumno.
5. **S12.1–S12.6.** Clasificar candidatos con 0,50 % Cu y tonelaje válido; contrastar 5 000 t/d de mina, 3 000 t/d de planta y 22 días; comparar ciclos de 30/40 min (6/8 camiones bajo supuestos PT-01), CAPEX específico, OPEX y restricciones. El producto final enlaza archivos e identidad S11. Los campos técnicos siguen siendo `ORE_CANDIDATE` y `WASTE_CANDIDATE`, no `RESERVE`.
6. **Aceptación y distribución.** Tests de esquema, secuencia, exportación y continuidad; comparación byte a byte de los eventos históricos; ensayo visual del HTML sin conexión; conversación humana desde cero, con error, «no sé», respuesta copiada, cierre E1, arranque S11 y transición S12. Emitir dictamen técnico y pedagógico por separado. Solo después preparar un paquete estudiantil; no mezclar carpetas `SOLO_QA` ni perfiles ficticios.

## 5. Criterios de cierre y límite conceptual

| Cierre | Kai puede decir | Kai no debe inferir |
| --- | --- | --- |
| E1 | «Llegaste al modelo preliminar; esa primera etapa terminó. S11 empieza después». | Que S11 o T3 están aprobadas. |
| S11 | «Construiste el modelo didáctico de recursos donde hubo soporte». | Que existe una declaración profesional de recursos. |
| S12 | «Construiste el modelo preliminar didáctico de reservas y comparaste escenarios». | Que los candidatos son reservas declaradas, hay pit, secuencia factible o rentabilidad demostrada. |

La distinción es parte del aprendizaje: S11 aún carece de clasificación y justificación profesional de perspectivas razonables de extracción; S12 aún carece de recurso apto para conversión, factores modificadores completos y prefactibilidad/factibilidad. PT-01 conserva sus nombres técnicos originales («modelo cuantitativo didáctico» y «escenario operativo conceptual»); los nombres de DD identifican la progresión **académica**.

**Para discutir con Kai principal:** el nuevo itinerario evalúa la comprensión del proceso que creó el modelo, no solo la lectura del modelo existente. El progreso histórico conserva valor, pero no prueba automáticamente las competencias nuevas. También conviene fijar institucionalmente la convención «modelo preliminar didáctico de reservas» para impedir que se confunda con una reserva reportable.
