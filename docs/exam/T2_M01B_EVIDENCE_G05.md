# Evidencia de sesión T2 M01B — G05

## ESTADO FINAL VIGENTE

Este estado técnico final prevalece sobre todos los checkpoints, respuestas,
estados Git y conclusiones históricas que siguen en este registro.

- **Rama:** `feature/m01b-block-model`.
- **HEAD actual/documental:** `207ba75`.
- **Commit técnico del modelo final:** `a70b546`.
- **Estado base:** `BASE_VERIFIED`.
- **Suite final técnica:** `41 passed`.
- **Git:** `git diff --check` limpio antes del commit técnico final; árbol de trabajo limpio después del commit.
- **P2:** decisión conceptual aprobada para el alcance preliminar; reproducibilidad y cobertura verificadas, optimización del tamaño/origen no demostrada. Para el modelo categórico preliminar del alcance T2 se adopta una malla reproducible de 50 × 50 × 10 m, con forma 15 × 14 × 55 (11,550 bloques) y origen local provisional (242225, 8196250, 2990) m. La dimensión horizontal de 50 m se eligió como escala conceptual comparable con las medianas observadas de distancia al collar vecino más cercano (55.90 m) y de espaciamiento por sección (54.90 m; mediana de las medianas por sección: 58.77 m); la cobertura es heterogénea y este análisis no constituye variografía ni demuestra un tamaño óptimo. La dimensión vertical de 10 m se conserva como discretización adoptada, pero no está justificada formalmente por el espaciamiento vertical observado. El origen se obtuvo por redondeo inferior respecto del cero numérico local con incrementos de 25/25/10 m para la candidata conceptual anterior y se retuvo al pasar a 50/50/10 m; no es una referencia oficial.
- **Cobertura y procedencia de Topopl:** 44/44 collars y 313/313 estaciones de trayectoria dentro del grid; 120 intervalos litológicos contabilizados dentro por `11,574.785091049 m` y 0 m fuera; los 210 centros XY tienen elevación TIN finita. De los 218.112 puntos raw, 69.266 están dentro del rectángulo XY del grid y 148.846 fuera. `Topopl.csv` está integrado técnicamente, pero no figura en el `release_manifest.json` original. La referencia histórica de compatibilidad espacial indicada por el docente no acredita procedencia oficial.
- **Referencia espacial:** CRS/EPSG de `Topopl.csv` y datum/referencia vertical de `Z` NO DOCUMENTADOS. El release documenta coordenadas/cartesianas locales en metros, pero no hay evidencia suficiente para asignar formalmente esa referencia a Topopl; no se infieren UTM, WGS84, PSAD56, zona ni transformación. `collar.csv.z` no permite inferir el datum topográfico.

### Estado vigente B00–B10

| ID | Estado | Evidencia y alcance |
|---|---|---|
| B00 | `VERIFIED` | Rama `feature/m01b-block-model`, HEAD actual/documental `207ba75`, commit técnico del modelo final `a70b546` y árbol de trabajo limpio tras ese commit técnico. |
| B01 | `VERIFIED` | Fuentes, manifiesto, integridad, campos y unidades verificados; topografía disponible y su cobertura se detalla en B09. |
| B02 | `VERIFIED` | Validador ejecutado con 4 hallazgos `INFO` y ningún `ERROR` o `WARNING`; pruebas de la suite final aprobadas. |
| B03 | `VERIFIED` | Trayectorias/posiciones XYZ utilizables; 44 sondajes, 313 estaciones y 120 intervalos litológicos posicionados. |
| B04 | `VERIFIED` | Capacidad histórica: `stash@{0}` y `stash@{1}` contienen `src/mod1/visualizer.py`, `tests/test_visualizer.py` y `outputs/figures/m01_drillholes_3d_DS05_EXP03.html`; `baseline_M01B.txt` registra 62 tests y 10 subtests aprobados históricamente. El visualizador heredado no está activo en HEAD; la visualización vigente del producto final es P6. No es evidencia de ejecución actual desde HEAD. |
| B05 | `VERIFIED` | Decisiones y resultados documentados en IMP-003/IMP-004 y reconciliados con el estado técnico final. |
| B06 | `VERIFIED` | Auditoría observacional reproducida: 5.803 assays, 120 intervalos litológicos y 44 sondajes; 0 gaps, 0 overlaps y 0 discrepancias `length_m != to_m - from_m`; 76 contactos contiguos con cambio de código; 48 assays cruzan al menos un contacto; cobertura assay desde MD 0 hasta profundidad final en 44/44 sondajes. Pasaron 16 pruebas focalizadas relacionadas. Alcance limitado a coherencia/trazabilidad de observaciones, no interpretación geológica externa. |
| B07 | `VERIFIED` | Regla de compositado documentada: longitud objetivo, ponderación por longitud y preservación de residuales; no implica interpretación de códigos. |
| B08 | `VERIFIED` | 5.830 composites regenerados byte por byte idénticos al CSV versionado; SHA-256 `7a00a557bf604eba8ac45d158ba2a01a6d03caa8fccd14b020c47df478b4193c`. Longitud total `11,574.785091049 m`; Cu ponderado conservado dentro del redondeo del CSV (diferencia `4.55e-12`, por precisión del formato, no un fallo). Los 5.803 IDs raw aparecen en 9.506 referencias de origen por división en contactos; 5.750 composites completos y 80 residuales. |
| B09 | `VERIFIED` | `data/raw/topography/Topopl.csv`: 218.112 puntos con campos `PID/X/Y/Z`; cobertura completa del grid en X/Y e intersección en Z. |
| B10 | `VERIFIED` | Suite final de 41 pruebas aprobadas, `git diff --check` limpio antes del commit, artefactos trazables y árbol limpio después del commit técnico final. |

### Gates y resultados técnicos vigentes

- **P3, P4, P5 y P6:** `VERIFIED` dentro del alcance computacional/documental registrado; P4/P5 representan coherencia y trazabilidad respecto de observaciones, no certificación profesional externa.
- **Grid:** bloques de `50 × 50 × 10 m`; dimensiones `15 × 14 × 55`, total `11.550` bloques. El origen es provisional.
- **Topografía por bloques:** `ROCK` 6.853; `AIR` 4.493; `PARTIAL` 204.
- **Validación geológica:** 120 intervalos posicionados; 76 contactos; `11,574.785091049 m` contabilizados dentro de la malla y `0 m` fuera; 978 bloques asignados con intersección positiva, 68 conflictos y 10.504 bloques sin soporte. Conflictos y bloques sin soporte permanecen `UNKNOWN/UNASSIGNED`.
- **P6:** HTML 3D integrado con topografía, bloques, sondajes, intervalos litológicos, contactos y sección X-Z.

### Limitaciones vigentes

- CRS/EPSG y datum vertical no están documentados.
- No está documentado el significado oficial de `OVB`, `BRX`, `POR`, `VOL` o `AIR`; se conservan como códigos literales.
- La validación geológica comprueba coherencia con intervalos y contactos observados del repositorio; no constituye certificación profesional externa.
- La clasificación topográfica es computacional y no estima fracción volumétrica de bloque.

## HISTÓRICO — checkpoints y respuestas originales

Todo el contenido que sigue conserva el registro cronológico original. Los estados
de recuperación, bloqueos, HEAD, conteos de pruebas y estados parciales/bloqueados
que aparecen allí describen únicamente el momento de cada checkpoint; no son el
estado vigente y quedan sustituidos por **ESTADO FINAL VIGENTE**.

## Protocolo, límites y fidelidad

- Protocolo aplicado durante esta sesión: `EXAM_T2_M01B v1.0`, perfil `TUTOR-EVALUADOR`; activación de sesión, no actualización del modelo.
- Modo de trabajo: `REPOSITORY_CHECK` inicial y después `ALIGNMENT_RECOVERY`; estado final `RECOVERY_BLOCKED`.
- No se aplicó stash; no se modificaron gobernanza, `data/raw/`, código fuente, tests, IMP-002 ni otros archivos. No hubo commit/push ni instalación.
- Esta evidencia registra las respuestas del estudiante copiadas literalmente de los mensajes disponibles en esta conversación. No reconstruye turnos no disponibles.
- Se leyeron las reglas del repo, documentos del examen, PROJECT/STATUS e IMP-002. Los documentos del examen están realmente en `docs/exam/T2_M01B/01_AGENT_EXAM_M01B.md` y `docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md`.
- El trabajo de documentación en este archivo y en `T2_M01B_PLAN_G05.md` fue autorizado expresamente por el estudiante el 2026-10-23. No se han actualizado todavía otros registros.

## Registro cronológico de decisiones y respuestas

### CHECKPOINT 01 — Priorizar reconciliación de M01

- Modo: `ALIGNMENT_RECOVERY`.
- Alternativas ofrecidas: A localizar y confirmar Topopl; B reconciliar M01/XYZ; C pedir al docente confirmación de versiones/rutas.
- Respuesta original:

> Elijo la alternativa B: reconciliar primero el estado de M01 y la generación de XYZ.
>
> Evidencia real: el repositorio actual está limpio en feature/m01b-block-model, pero existen respaldos en git stash list, incluido backup antes de integrar topografía y M01. Esto puede explicar por qué el checkout actual no muestra toda la implementación espacial previa.
>
> Ventaja: permite comprobar primero si desurvey, positioning y las coordenadas XYZ de M01 son reproducibles antes de construir decisiones espaciales de M01B.
>
> Limitación: aunque se recupere M01, la topografía todavía debe verificarse por separado antes de clasificar bloques como AIR/ROCK/PARTIAL.
>
> No implementes código todavía. Continúa en ALIGNMENT_RECOVERY y dime el siguiente paso de verificación en solo lectura.

- Evaluación explícita del agente: `CORRECTA`, H0.
- Aclaración verificada después: `git status -sb` mostró `?? docs/exam/`; por tanto, la frase “limpio” de la respuesta del estudiante fue corregida con evidencia: no había cambios rastreados reportados, pero el checkout no estaba completamente limpio.
- Gate: ninguno; sin edición.

### CHECKPOINT 02 — Inspeccionar stash más reciente

- Alternativas ofrecidas: A inspeccionar `stash@{0}` frente al checkout e IMP-002; B comparar stashes; C pedir confirmación docente.
- Respuesta original:

> Elijo la alternativa A: inspeccionar stash@{0} y compararlo con el checkout actual y con IMP-002.
>
> Evidencia: stash@{0} es el respaldo más reciente, creado el 16-10-2026 en feature/m01b-block-model, y contiene las implementaciones de desurvey, positioning, validator, visualizer, además de pruebas, topografía y salidas.
>
> Ventaja: permite verificar primero la versión más reciente y más cercana al estado actual del proyecto, evitando revisar respaldos antiguos sin necesidad.
>
> Limitación: inspeccionar los archivos no demuestra que las pruebas pasen ni que los resultados puedan reproducirse; eso tendrá que verificarse después mediante ejecución controlada.
>
> Continúa en modo solo lectura. No apliques el stash ni modifiques archivos.

- Resultado real: `stash@{0}` es del 2026-10-16 y contiene cambios de M01, pruebas, topografía y salidas; `stash@{1}` es anterior. Se inspeccionaron interfaces y existencia de implementaciones/tests; no se aplicó ninguno.
- Evaluación conversacional explícita: no se emitió veredicto `CORRECTA/PARCIAL` en ese turno; no se inventa uno.

### CHECKPOINT 03 — Procedencia oficial de Topopl

- Alternativas ofrecidas: A aportar confirmación docente; B comparar con copia/hash oficial; C mantener B09 `BLOCKED` y consultar.
- Respuesta original:

> Elijo la alternativa A: confirmar que Topopl.csv del stash@{0} corresponde a la fuente oficial de topografía.
>
> Evidencia: el archivo aparece en stash@{0} como data/raw/topography/Topopl.csv, con campos PID, X, Y, Z, y el IMP-002 registra 218,112 puntos; sin embargo, actualmente no está en el checkout ni en el manifiesto de datos.
>
> Ventaja: permite resolver primero la procedencia de la topografía antes de usarla para clasificar bloques respecto al terreno.
>
> Limitación: aun confirmando su procedencia, todavía será necesario verificar cobertura, compatibilidad espacial y ejecutar las validaciones correspondientes.
>
> Mantén ALIGNMENT_RECOVERY en solo lectura. No recuperes ni modifiques archivos todavía.

- Comprobación real del candidato del stash: 218.112 filas; columnas `PID,X,Y,Z`; X `242090.504105–243287.725586`, Y `8195892.194946–8197095.651855`, Z `3120.858516–3596`; SHA-256 `1724a97f1fa6f6a059def896d1ba566b1e23d6f78781034bf2e3f53d2d4b1887`.
- Resultado: los rangos/conteo concuerdan con IMP-002, pero el manifiesto no incluye la topografía/hash y no hay referencia independiente que vincule el archivo específico con aprobación docente. B09 continúa `BLOCKED`.
- Evaluación explícita: no se emitió etiqueta evaluativa en ese turno.

### CHECKPOINT 04 — Mantener B09 bloqueado

- Alternativas ofrecidas tras la verificación: A aportar referencia docente; B copia/hash oficial; C mantener bloqueo y consultar al docente.
- Respuesta original:

> Elijo la alternativa C: mantener B09 como BLOCKED y solicitar confirmación al docente sobre la procedencia oficial de Topopl.csv.
>
> Evidencia: el archivo del stash@{0} tiene 218,112 registros, campos PID,X,Y,Z, hash SHA-256 identificado y rangos coincidentes con IMP-002; sin embargo, no figura en release_manifest.json ni existe una referencia verificable que vincule ese archivo específico con una aprobación oficial.
>
> Ventaja: evita asumir como oficial una fuente cuya procedencia no está documentada y mantiene la trazabilidad del examen.
>
> Limitación: B09 seguirá bloqueado hasta recibir confirmación o una referencia oficial, por lo que no podremos validar completamente la clasificación topográfica.
>
> Mantén B09 como BLOCKED y continúa únicamente con las verificaciones conceptuales o técnicas que sí sean viables sin usar esa topografía como fuente oficial.

- Decisión operativa aplicada: mantener B09 `BLOCKED`; no usar Topopl para clasificar. No se emitió veredicto evaluativo explícito.

### CHECKPOINT 05 — Inspeccionar hallazgos del validador aislado

- Alternativas ofrecidas: A inspeccionar hallazgos concretos de `validate_data`; B generar figura M01 temporal; C pausar hasta resolver procedencia de topografía.
- Respuesta original:

> Elijo la alternativa A: inspeccionar los hallazgos concretos de validate_data sobre los datos raw actuales.
>
> Evidencia: el candidato M01 de stash@{0} pasó 71 pruebas y 10 subtests, y permitió regenerar 5,830 composites idénticos byte por byte al CSV actual. Esto demuestra que el candidato puede ejecutar la cadena necesaria sin usar topografía.
>
> Ventaja: permite identificar qué controles de integridad y consistencia minera se aplican realmente a los datos antes de avanzar con decisiones espaciales posteriores.
>
> Limitación: esta verificación sigue siendo sobre el candidato aislado y no restaura M01 en el checkout actual; además, B09 permanece BLOCKED por la procedencia de la topografía.
>
> Continúa en ALIGNMENT_RECOVERY, sin aplicar el stash ni modificar archivos.

- Ejecución aislada de `validate_data` contra los CSV raw del checkout: 4 hallazgos, todos `INFO`: dos `ASSAY-03` (5.803 ceros en `mo_pct` y 5.803 en `au_gt`), uno `DENS-03` (459 muestras distribuidas en 44 sondajes) y uno `REL-04` (alteration vacío); cero `ERROR`/`WARNING`.
- Evaluación explícita del agente sobre la selección de inspeccionar hallazgos: no se emitió etiqueta `CORRECTA/PARCIAL` en ese turno.

### CHECKPOINT 06 — Alcance de los hallazgos del validador

- Alternativas ofrecidas tras mostrar los hallazgos: A evidencia de reglas del candidato y B02 sigue parcial; B declarar M01/base verificados; C descartar controles hasta resolver B09.
- Respuesta original:

> Elijo la alternativa A.
>
> Evidencia: validate_data sobre los datos raw actuales reportó 4 hallazgos, todos de nivel INFO, sin ERROR ni WARNING: ASSAY-03 para los 5,803 valores cero en mo_pct y au_gt, DENS-03 para 459 muestras de densidad en 44 sondajes y REL-04 porque alteration.csv está vacío.
>
> Ventaja: demuestra que los datos no activaron errores en las reglas implementadas por el candidato y aporta evidencia concreta sobre la calidad y estructura de los inputs.
>
> Limitación: la validación se ejecutó con el candidato aislado, no desde el checkout actual; por eso B02 debe mantenerse PARTIAL. Además, esto no resuelve B09 ni demuestra que todo M01 esté completamente verificado.
>
> Mantén B02 como PARTIAL y continúa con el siguiente paso viable de ALIGNMENT_RECOVERY en solo lectura.

- Evaluación explícita del agente: `CORRECTA`, H0. B02 permanece `PARTIAL`.

### CHECKPOINT 07 — XYZ del candidato M01

- Alternativas: A mantener B03 parcial y candidato como diagnóstico; B considerar B03 verificado conceptualmente; C pausar evaluación conceptual hasta confirmar topografía.
- Respuesta original:

> Elijo la alternativa A: mantener B03 como PARTIAL y usar estos resultados solo como evidencia diagnóstica del candidato.
>
> Evidencia: el candidato generó trayectorias para 44 sondajes y 313 estaciones, posicionó 5,803 assays, 120 intervalos de litología y 459 muestras de densidad; todas las coordenadas fueron finitas y los 44 puntos en MD=0 coincidieron exactamente con sus collars.
>
> Ventaja: permite demostrar que el candidato puede producir posicionamientos consistentes sin confundir esa evidencia con una implementación activa en el checkout.
>
> Limitación: el checkout actual todavía contiene stubs en desurvey y positioning, por lo que el flujo no es reproducible directamente desde HEAD y B03 no puede declararse VERIFIED.
>
> Mantén B03 como PARTIAL y continúa con el siguiente paso viable de ALIGNMENT_RECOVERY sin usar topografía ni modificar archivos.

- Resultado real de ejecución aislada: 44 sondajes, 313 estaciones; 5.803 assays, 120 litologías, 0 alteraciones, 459 densidades posicionadas; XYZ finitos; coincidencia exacta collar/MD=0 en 44/44; validador con 0 errores y 4 INFO.
- Evaluación explícita: `CORRECTA`, H0. B03 queda `PARTIAL`.

### CHECKPOINT 08 — Auditoría directa assay/lithology

- Contexto: el estudiante había solicitado en el checkpoint anterior mantener B03 `PARTIAL` y continuar en solo lectura. No hubo un nuevo mensaje del estudiante entre esa solicitud y esta ejecución de auditoría; no se registra una respuesta adicional.
- Auditoría read-only ejecutada sobre raw: assays `5803`, 44 sondajes, sin IDs duplicados, gaps/overlaps internos, comienzan MD 0 y terminan en profundidad de collar 44/44; litología `120`, 44 sondajes, sin claves duplicadas, gaps/overlaps, comienzan MD 0 y terminan a profundidad de collar 44/44; códigos literales AIR 2, BRX 10, OVB 46, POR 35, VOL 27; 76 contactos de códigos diferentes; 48 assays cruzan al menos un límite; alteración 0 filas.
- No se atribuye al estudiante una decisión evaluativa para este comando diagnóstico.

### CHECKPOINT 09 — Pedir diccionario geológico

- Alternativas: A conservar códigos literales; B solicitar diccionario/confirmación; C proponer agrupaciones provisionales con evidencia adicional.
- Respuesta original:

> Elijo la alternativa B: solicitar un diccionario o confirmación geológica oficial antes de interpretar o agrupar los códigos litológicos.
>
> Evidencia: lithology.csv contiene los códigos OVB, BRX, POR, VOL y AIR, pero data_dictionary.csv solo define lith_code como código litológico observado y no documenta el significado de cada valor.
>
> Ventaja: evita asignar interpretaciones o dominios geológicos sin respaldo y mantiene trazabilidad con la información oficial.
>
> Limitación: mientras no exista ese diccionario o confirmación, la interpretación y agrupación de los códigos debe permanecer pendiente; por ahora se conservarán los códigos originales sin reinterpretarlos.
>
> Continúa en ALIGNMENT_RECOVERY con las verificaciones que puedan realizarse sin asumir el significado geológico de los códigos y sin usar la topografía bloqueada.

- Evaluación explícita del agente: `CORRECTA`, H0.

### CHECKPOINT 10 — Preservar contactos y conflictos

- Alternativas: A conservar segmentos; B marcar `MIXED/AMBIGUOUS`; C asignar solo con soporte único y usar `UNKNOWN/UNASSIGNED` ante conflicto.
- Respuesta original:

> Elijo la alternativa C: asignar una categoría solo cuando exista soporte de un único código observado; cuando exista conflicto entre códigos, dejar el estado como UNKNOWN/UNASSIGNED.
>
> Evidencia: composites.csv contiene 5,830 composites con lith_code y trazabilidad, y la auditoría identificó 76 contactos entre códigos distintos y 48 assays que cruzan al menos un contacto.
>
> Ventaja: preserva los límites observados y evita forzar una clasificación geológica cuando la evidencia es ambigua.
>
> Limitación: aumentará la cantidad de celdas sin asignación y, sin un diccionario geológico oficial, todavía no se pueden interpretar ni agrupar los códigos como dominios formales.
>
> Continúa en ALIGNMENT_RECOVERY, sin implementación ni cambios de archivos.

- Evaluación explícita del agente: `CORRECTA`, H0.

### CHECKPOINT 11 — Concordancia de soporte conceptual

- Alternativas: A punto medio de composite; B intervalo espacial del sondaje; C exigir concordancia entre observaciones y dejar desconocido el conflicto.
- Respuesta original:

> Elijo la alternativa C: exigir concordancia entre las observaciones que aportan soporte y dejar UNKNOWN/UNASSIGNED cuando existan códigos en conflicto.
>
> Evidencia: composites.csv contiene coordenadas de punto medio y códigos litológicos literales, y la auditoría identificó 76 contactos entre códigos distintos y 48 assays que cruzan contactos. Además, todavía no existe un grid definido ni trayectorias activas en el checkout actual.
>
> Ventaja: reduce el riesgo de asignar una categoría cuando la evidencia espacial es contradictoria y mantiene explícita la incertidumbre.
>
> Limitación: será necesario definir más adelante cómo medir la concordancia y qué umbral aceptar, lo que puede aumentar la cantidad de celdas UNKNOWN/UNASSIGNED.
>
> Mantén esta decisión como conceptual y continúa en ALIGNMENT_RECOVERY sin implementar código.

- Evaluación explícita del agente: `CORRECTA`, H0.

### CHECKPOINT 12 — Envolvente provisional

- Alternativas: A envolvente provisional de collars/composites; B solo reportar rangos; C aplazar evaluación espacial.
- Respuesta original:

> Elijo la alternativa A: estimar una envolvente espacial provisional a partir de collars y composites.
>
> Evidencia: composites.csv contiene coordenadas XYZ de punto medio y los datos del proyecto usan coordenadas cartesianas locales en metros. Además, ya se verificó que el candidato M01 puede generar posiciones para los 44 sondajes.
>
> Ventaja: permite cuantificar el soporte espacial realmente observado y comparar posteriormente alternativas de malla sin definir todavía el grid final.
>
> Limitación: esta envolvente será provisional porque no incorpora una topografía oficialmente verificada ni representa necesariamente la extensión final del modelo.
>
> Continúa en ALIGNMENT_RECOVERY y calcula únicamente la envolvente provisional en modo solo lectura, sin crear el grid ni modificar archivos.

- Resultado real: collars (44) + puntos medios composites (5830), rangos conjuntos X `242228.128434–242971.871566 m` (span `743.743133 m`), Y `8196266.798008–8196913.201992 m` (span `646.403984 m`), Z `2995.885049–3532.000000 m` (span `536.114951 m`). CRS formal no documentado.
- Evaluación explícita: no se emitió etiqueta evaluativa en ese turno.

### CHECKPOINT 13 — Tamaño candidato de bloque

- Alternativas calculadas para cubrir la envolvente mediante `ceil(extensión/dimensión)`: A `12,5×12,5×5 m`, 336.960 celdas; B `25×25×10 m`, 42.120; C `50×50×20 m`, 5.265.
- Respuesta original:

> Elijo la alternativa B: bloque de 25 × 25 × 10 m como candidata conceptual.
>
> Evidencia: la envolvente provisional observada es de aproximadamente 743.743 m en X, 646.404 m en Y y 536.115 m en Z. Con esta alternativa se obtienen aproximadamente 30 × 26 × 54 = 42,120 celdas, una carga mucho menor que la alternativa fina de 336,960 celdas y con mayor detalle que la alternativa gruesa de 5,265.
>
> Ventaja: ofrece un equilibrio razonable entre detalle espacial y costo computacional para una evaluación conceptual inicial.
>
> Limitación: todavía no está justificada con un análisis formal del espaciamiento entre sondajes ni con topografía validada, por lo que no debe considerarse tamaño de bloque definitivo.
>
> Mantén esta alternativa como candidata conceptual y continúa con la siguiente decisión de la pauta sin implementar código ni aprobar todavía P2_GRID.

- Evaluación explícita del agente: `CORRECTA`, H0. Tamaño no definitivo.

### CHECKPOINT 14 — Origen del grid

- Alternativas: A origen en mínimos observados; B referencia fija/alineación regular; C mantener origen pendiente.
- Respuesta original:

> Elijo la alternativa C: mantener el origen como parámetro pendiente hasta confirmar una referencia espacial oficial.
>
> Evidencia: el README solo documenta coordenadas cartesianas locales en metros; no existe un CRS/EPSG formal ni una referencia de grid aprobada. Además, la envolvente actual es provisional y se calculó solo con collars y puntos medios de composites.
>
> Ventaja: evita fijar una alineación arbitraria que luego pueda desplazar índices y centros de bloque cuando se confirme la referencia espacial definitiva.
>
> Limitación: mientras el origen siga pendiente, no se pueden definir de forma final los índices ni los centros del grid.
>
> Mantén 25 × 25 × 10 m como candidata conceptual y el origen como pendiente. Continúa con la siguiente decisión de P2 sin aprobar todavía P2_GRID.

- Evaluación explícita del agente: `CORRECTA`, H0.

### CHECKPOINT 15 — Margen de envolvente

- Alternativas: A usar rango observado sin margen; B añadir margen tras revisar extremos de trayectorias; C dejar margen pendiente.
- Respuesta original:

> Elijo la alternativa C: dejar el margen pendiente hasta confirmar las trayectorias y la topografía.
>
> Evidencia: la envolvente actual se calculó con collars y puntos medios de composites, pero no representa necesariamente los extremos completos de las trayectorias. Además, B03 sigue PARTIAL en el checkout y B09 continúa BLOCKED por la topografía.
>
> Ventaja: evita ampliar el grid con un margen arbitrario basado en evidencia incompleta.
>
> Limitación: mientras el margen siga pendiente, la extensión final del grid no puede considerarse cerrada ni lista para aprobar P2_GRID.
>
> Mantén el margen como pendiente y continúa con la siguiente decisión de P2 sin implementar código.

- Evaluación explícita del agente: `CORRECTA`, H0.

### CHECKPOINT 16 — Política de borde

- Alternativas: A bloques nominales completos y límites extendidos; B bloques irregulares de borde; C aplazar hasta definir origen/extensión.
- Respuesta original:

> Elijo la alternativa C: dejar la política de borde pendiente hasta definir el origen y la extensión final.
>
> Evidencia: la malla 25 × 25 × 10 m y sus 42,120 celdas son todavía una comparación conceptual basada en una envolvente provisional; el origen, el margen y la extensión final siguen pendientes y P2_GRID no está aprobado.
>
> Ventaja: evita fijar una geometría de borde sobre una malla que todavía no está definida de manera final.
>
> Limitación: los conteos actuales siguen siendo conceptuales y no pueden considerarse los conteos definitivos del grid.
>
> Con esta decisión, cierra P2 como PARCIAL/PENDIENTE con lo ya justificado, registra origen, margen, borde y extensión final como pendientes, y continúa con el siguiente punto viable de la pauta sin abrir más subdecisiones de P2.

- Evaluación explícita del agente: `CORRECTA`, H0. P2 `PARTIAL/PENDIENTE`.

### CHECKPOINT 17 — Regla topográfica conceptual

- Alternativas: A centro de celda; B evaluación de vértices; C fracción de ocupación.
- Respuesta original:

> Elijo la alternativa B: evaluar la relación entre la superficie topográfica y los vértices del bloque cuando se disponga de la topografía oficial.
>
> Evidencia: B09 continúa BLOCKED porque Topopl.csv no está confirmado como fuente oficial, por lo que esta elección es únicamente conceptual.
>
> Ventaja: permite identificar de forma explícita bloques completamente sobre la superficie, completamente bajo ella y posibles bloques parcialmente cortados, sin requerir inicialmente un cálculo volumétrico más complejo.
>
> Limitación: la evaluación por vértices no determina directamente qué fracción del bloque corresponde a roca, por lo que los casos parciales requerirán una regla adicional o validación posterior.
>
> Mantén esta decisión como conceptual, marca P3 como pendiente de B09 y continúa con el siguiente punto viable de la pauta sin abrir más subdecisiones innecesarias de P3.

- Evaluación explícita del agente: `CORRECTA`, H0. P3 pendiente de B09.

### CHECKPOINT 18 — Fuentes para asignación P4

- Alternativas: A puntos medios de composites; B intervalos litológicos posicionados; C ambas fuentes con concordancia.
- Respuesta original:

> Elijo la alternativa C: usar ambas fuentes —composites e intervalos litológicos posicionados— y asignar una categoría solo cuando exista concordancia según una regla que se definirá posteriormente.
>
> Evidencia: composites.csv contiene coordenadas XYZ de punto medio, lith_code y trazabilidad a assays; lithology.csv contiene 120 intervalos observados y 76 contactos entre códigos distintos.
>
> Ventaja: permite contrastar dos fuentes de soporte y hacer explícitos los conflictos, reduciendo el riesgo de asignar una categoría cuando la evidencia no es consistente.
>
> Limitación: todavía falta definir cómo medir la concordancia espacial y el posicionamiento M01 no está activo en el checkout, por lo que esta decisión sigue siendo conceptual y puede aumentar los bloques UNKNOWN/UNASSIGNED.
>
> Cierra P4 como decisión conceptual pendiente de implementación y continúa con el siguiente punto viable de la pauta, sin abrir subdecisiones innecesarias.

- Evaluación explícita del agente: `PARCIAL`, H0; motivo comunicado: el lith_code de composites se deriva de lithology al cortar/compositar, así que esas etiquetas no son fuentes independientes de corroboración.

### CHECKPOINT 19 — Evidencia de P5

- Alternativas: A priorizar tests; B priorizar revisión espacial; C registrar ambas evidencias parciales.
- Respuesta original:

> Elijo la alternativa C: registrar las pruebas computacionales y la validación minera como evidencias parciales y no aceptar P5 como completado hasta verificarlas desde una ruta reproducible.
>
> Evidencia: el candidato aislado pasó 71 pruebas y 10 subtests, y se verificó conservación de longitud y Cu ponderado en los composites. Sin embargo, todavía no existe revisión espacial completa contra topografía y el posicionamiento M01 no está activo en el checkout.
>
> Ventaja: evita confundir tests exitosos con validación minera y mantiene separados ambos tipos de evidencia.
>
> Limitación: P5 seguirá PARTIAL hasta reactivar una ruta reproducible y completar controles espaciales y mineros.
>
> Cierra P5 como PARTIAL y continúa con el siguiente punto viable de la pauta, sin abrir más subdecisiones innecesarias.

- Evaluación explícita del agente: `CORRECTA`, H0. P5 `PARTIAL`.

### CHECKPOINT 20 — P6 visualización diagnóstica

- Alternativas: A vista 3D de composites/sondajes; B posponer hasta grid/topografía; C secciones/vistas 2D diagnósticas.
- Respuesta original:

> Elijo la alternativa C: usar primero secciones o vistas 2D de los datos disponibles como diagnóstico, sin presentarlas como visualización del modelo de bloques.
>
> Evidencia: composites.csv ya contiene coordenadas XYZ y códigos observados, pero todavía no existe un grid aprobado ni una topografía oficial verificada; además, el checkout no contiene una visualización M01 activa.
>
> Ventaja: permite revisar distribución espacial, contactos y zonas con menor soporte usando la evidencia disponible, sin depender todavía de un grid ni de topografía.
>
> Limitación: no proporciona una representación volumétrica 3D del modelo de bloques ni permite validar la relación con la superficie topográfica.
>
> Cierra P6 como decisión conceptual/PARTIAL y continúa con el cierre de ALIGNMENT_RECOVERY, indicando qué falta para pasar a BASE_VERIFIED o RECOVERY_BLOCKED, sin abrir más subdecisiones.

- Estado registrado por el agente: P6 conceptual/`PARTIAL`; evaluación etiquetada no emitida explícitamente, no se inventa.

### CHECKPOINT 21 — Refinamiento conceptual de P4

- Alternativas presentadas:
  - A: usar el código del composite solo como control de consistencia, no como corroboración independiente.
  - B: tratar los intervalos litológicos como fuente categórica y usar composites solo para ubicar el soporte de assay.
  - C: mantener P4 pendiente hasta recibir una fuente geológica independiente o confirmación oficial.
- Respuesta original:

> Elijo la alternativa B: tratar los intervalos de litología como fuente categórica y usar los composites únicamente para ubicar el soporte de assay.
>
> Evidencia: lith_code en los composites fue heredado de los intervalos de litología, por lo que ambas etiquetas no constituyen observaciones geológicas independientes.
>
> Ventaja: separa correctamente la función de cada fuente y evita interpretar la trazabilidad de los composites como evidencia geológica adicional.
>
> Limitación: para usar los intervalos litológicos espacialmente todavía se necesita posicionamiento M01 reproducible desde el checkout, por lo que P4 sigue pendiente de implementación.
>
> Registra esta decisión en PLAN_G05 y EVIDENCE_G05, cierra P4 como PARTIAL y continúa con el siguiente punto pendiente de la pauta sin abrir nuevas subdecisiones de P4.

- Evaluación explícita del agente: `CORRECTA`, H0. La separación propuesta evita contar como corroboración independiente el código heredado en composites.
- Estado: P4 `PARTIAL`; el uso espacial de intervalos sigue dependiendo de posicionamiento M01 reproducible desde el checkout. No se implementó.

### CHECKPOINT 22 — Prioridad de pruebas y reproducibilidad P5

- Alternativas presentadas:
  - A: priorizar pruebas y reproducibilidad desde HEAD cuando se autorice recuperar M01.
  - B: priorizar controles espaciales contra topografía cuando B09 se desbloquee.
  - C: priorizar revisión geológica de secciones diagnósticas cuando haya posiciones disponibles.
- Respuesta original:

> Elijo la alternativa A: priorizar pruebas y reproducibilidad desde HEAD cuando se autorice recuperar M01.
>
> Evidencia: el candidato aislado pasó 71 pruebas y 10 subtests y regeneró los 5,830 composites de forma idéntica, pero el checkout actual todavía mantiene stubs en las capacidades M01 necesarias.
>
> Ventaja: permite verificar primero que la ruta activa del repositorio puede reproducir resultados antes de realizar validaciones mineras posteriores.
>
> Limitación: aunque las pruebas pasen desde HEAD, eso no demostrará por sí solo que la representación sea geológicamente válida ni resolverá B09.
>
> Registra esta decisión en PLAN_G05 y EVIDENCE_G05, mantén P5 como PARTIAL y continúa con el siguiente punto pendiente sin abrir más subdecisiones innecesarias.

- Evaluación explícita del agente: `CORRECTA`, H0. La respuesta distingue reproducibilidad computacional de validez geológica y reconoce que B09 sigue sin resolverse.
- Estado: P5 `PARTIAL`; esta prioridad es conceptual y no autoriza recuperar M01 ni ejecutar cambios. Validación minera/espacial pendiente.

### CHECKPOINT 23 — Evaluación tras recuperación selectiva M01

- Pregunta presentada: elegir entre mantener B02/B03 `PARTIAL`, declararlas `VERIFIED` por la ejecución en memoria, o tratar las pruebas del candidato aislado como prueba de la recuperación actual.
- Respuesta original:

> Elijo la alternativa A: mantener B02 y B03 como PARTIAL.
>
> Evidencia: tras la recuperación selectiva, la suite disponible terminó con 11 tests aprobados; además, la comprobación en memoria procesó 44 sondajes y 313 puntos de trayectoria, posicionó 5,803 assays, 120 intervalos litológicos y 459 muestras de densidad, con coordenadas finitas y coincidencia de los 44 puntos MD=0 con sus collars. El validador reportó 4 INFO, sin ERROR ni WARNING.
>
> Ventaja: reconoce que el flujo M01 funciona actualmente en el árbol de trabajo sin sobreafirmar un nivel de verificación que las pruebas disponibles no demuestran.
>
> Limitación: faltan pruebas específicas para validator, desurvey y positioning, y los tres módulos siguen modificados y sin commit; por tanto, todavía no puede afirmarse que HEAD limpio reproduzca estas capacidades.
>
> No uses los 71 tests y 10 subtests del candidato aislado como prueba directa de esta recuperación actual. Registra esta conclusión y continúa con el siguiente gate o verificación necesaria.

- Evaluación explícita del agente: `CORRECTA`, H0. La respuesta distingue resultados en el árbol de trabajo de pruebas específicas y de HEAD limpio; no usa los 71 tests/10 subtests del candidato aislado como evidencia directa de esta recuperación.
- Resultados actuales observados: `python -m pytest -q tests` terminó con `11 passed in 0.07s`. Comprobación en memoria con los CSV existentes: 44 holes, 313 puntos de trayectoria; 5.803 assays, 120 intervalos litológicos, 0 alteraciones, 459 muestras de densidad; XYZ posicionados finitos; coincidencia MD=0 con collars `44/44`; cuatro hallazgos `INFO`, cero `ERROR` y cero `WARNING`.
- Una primera versión de la comprobación inline terminó con `SyntaxError` en una f-string; se corrigió y la ejecución posterior produjo los resultados anteriores.
- `git diff --check` no informó problemas. Los únicos archivos rastreados modificados son los tres módulos autorizados; `docs/exam/` sigue apareciendo no rastreado, como ya constaba. Los stashes permanecen listados; no se aplicaron ni eliminaron.
- Estado: B02/B03 `PARTIAL`; los módulos están modificados en el árbol de trabajo, sin commit. No se afirma que HEAD limpio reproduzca estas capacidades. B09 sigue `BLOCKED`.

### CHECKPOINT 24 — Pruebas focalizadas y cierre T2 M01B

- Gate aprobado por el estudiante: crear pruebas focalizadas únicamente bajo `tests/` para validator, desurvey y positioning, con casos sintéticos en memoria, sin modificar módulos fuente. Ejecutar primero las pruebas focalizadas y luego la suite disponible. Sin cambios fuente adicionales, commit ni push.
- Archivo añadido: `tests/test_m01_spatial.py`. Contiene seis pruebas: dos del validador (hallazgos/reglas e inmutabilidad del input; intervalo fuera de profundidad y muestra de densidad duplicada), dos de desurvey (trayectoria recta desde collar y rechazo de MD duplicada) y dos de positioning (interpolación XYZ de límites/punto medio y rechazo de intervalo fuera de trayectoria).
- Comandos y resultados reales:

```text
C:\CN\.venv\Scripts\python.exe -m pytest -q tests/test_m01_spatial.py
6 passed in 0.03s

C:\CN\.venv\Scripts\python.exe -m pytest -q tests
17 passed in 0.08s

git -C C:\CN\PlanMinUPN-G05 diff --check
sin salida; sin problemas reportados
```

- Los resultados aplican a las versiones recuperadas en el árbol de trabajo; no equivalen a ejecución desde HEAD limpio ni a validación minera/geológica. No se usaron datos topográficos ni se generaron derivados.
- Estado final: B02 y B03 `PARTIAL`; B09 `BLOCKED`; B10 `PARTIAL`. Estado global `RECOVERY_BLOCKED`, no `BASE_VERIFIED`. P2 `PARTIAL/PENDIENTE`, P3 pendiente de B09, P4/P5/P6 `PARTIAL`.
- Cierre técnico: hay resultados computacionales reproducibles de pruebas focalizadas y suite disponible, además de la comprobación en memoria documentada en CHECKPOINT 23. No se demuestra validez geológica ni clasificación topográfica. Siguen pendientes procedencia oficial/verificación de topografía, reproducibilidad desde HEAD limpio, reconciliación de IMP-002, validación espacial/minera y visualización.
- Estado Git consultado al cierre:

```text
## feature/m01b-block-model
 M src/mod1/desurvey.py
 M src/mod1/positioning.py
 M src/mod1/validator.py
?? docs/exam/
?? tests/test_m01_spatial.py
```

- HEAD observado: `9771efbecf4fb9fb1763d2cb0e99fa3280137b4a`. `git diff --check` sin problemas. No se hizo commit ni push; stash no aplicado ni eliminado.

### CHECKPOINT 25 — Origen candidato alineado para P2

- Alternativas presentadas:
  - A: mantener como candidato conceptual el origen regular y conteo propuestos, sin cerrar `P2_GRID`.
  - B: revisar el origen con una referencia concreta del proyecto, como un collar documentado.
  - C: dejar el origen pendiente hasta tener referencia oficial.
- Respuesta original:

> Elijo la alternativa A: mantener este origen y conteo como candidato conceptual, sin cerrar todavía P2_GRID.
>
> Evidencia: con bloques de 25 × 25 × 10 m y la envolvente provisional, el origen alineado a múltiplos regulares sería X=242225, Y=8196250 y Z=2990, con una malla de 30 × 27 × 55 = 44,550 bloques.
>
> Ventaja: proporciona una alineación reproducible y un conteo explícito de bloques, facilitando comparar y auditar la geometría propuesta.
>
> Limitación: el origen depende del cero de las coordenadas locales como referencia numérica y todavía no existe una alineación oficial del proyecto; además, margen externo, bordes y espaciamiento formal siguen pendientes.
>
> Mantén esta geometría como candidata conceptual y continúa con el siguiente requisito mínimo para poder cerrar P2_GRID, sin implementar todavía.

- Evaluación explícita del agente: `CORRECTA`, H0. La elección mantiene el carácter provisional y reconoce que el origen no tiene respaldo oficial y que quedan pendientes de P2.
- Cálculo aritmético ejecutado en modo lectura sobre la envolvente ya registrada: origen `(242225, 8196250, 2990) m`; conteos `(30, 27, 55)`; total `44.550`; máximo de malla `(242975, 8196925, 3540) m`; margen inferior X/Y/Z `(3.128434, 16.798008, 5.885049) m`; margen superior `(3.128434, 11.798008, 8.000000) m`. No se usó topografía ni se modificaron archivos de datos o código para este cálculo.
- Estado P2: `PARTIAL/PENDIENTE`; `P2_GRID` no aprobado. La elección conceptual del origen no autoriza implementar.

### CHECKPOINT 26 — Análisis descriptivo de espaciamiento para P2

- Alternativas presentadas para el análisis:
  - A: collars en planta y distribución por secciones.
  - B: puntos medios de composites en 3D.
  - C: combinar espaciamiento entre collars con cobertura de composites por direcciones y secciones.
- Respuesta original:

> Elijo la alternativa C: combinar el espaciamiento entre collars con la cobertura de composites a lo largo de las trayectorias, resumiendo ambos por direcciones y secciones.
>
> Evidencia: el proyecto tiene 44 sondajes con posiciones disponibles en el árbol de trabajo, además de composites posicionados. El tamaño de bloque candidato es 25 × 25 × 10 m, pero todavía falta demostrar que esa resolución es coherente con la separación real entre sondajes y con el soporte downhole.
>
> Ventaja: permite distinguir la separación entre sondajes de la densidad de muestras dentro de cada sondaje, evitando sobreestimar la resolución espacial disponible.
>
> Limitación: requiere un análisis adicional por direcciones y secciones, y los datos posicionados todavía provienen de un árbol de trabajo modificado, no de un HEAD limpio confirmado.
>
> Realiza únicamente este análisis de espaciamiento, sin usar topografía ni modificar archivos fuera de PLAN_G05 y EVIDENCE_G05. Después indica si 25 × 25 × 10 m sigue siendo defendible como candidata o si requiere revisión.

- Evaluación explícita del agente: `CORRECTA`, H0. La elección diferencia correctamente separación entre sondajes de soporte downhole y reconoce la limitación del árbol modificado.
- Método ejecutado solo en memoria, sin topografía: distancias XY entre collars; orientación exploratoria de vecino más cercano por sectores X/Y/diagonal; cobertura de composites en celdas horizontales de 25×25 m y secciones de elevación de 10 m; soporte downhole por longitud y continuidad de intervalos.
- Comando de cálculo: script Python inline enviado desde PowerShell a `C:\CN\.venv\Scripts\python.exe -`; leyó `data/raw/collar.csv` y `data/processed/m01b/composites.csv`. El cálculo no escribió archivos.
- Resultados de collars: 44 vecinos más cercanos, distancias XY: min `10.17 m`, Q1 `22.81 m`, mediana `55.90 m`, Q3 `89.02 m`, max `180.00 m`. Conteos de vecino más cercano: `≤25 m: 12/44`, `≤50 m: 14/44`, `≤100 m: 37/44`, `>100 m: 7/44`. Orientación exploratoria: 16 principalmente X, 18 principalmente Y, 10 diagonales. En las 810 celdas XY de 25×25 m del candidato, 42 tienen collar; 40 celdas tienen uno y 2 tienen dos.
- Resultados downhole/secciones: 5.830 composites; 5.750 con longitud 2 m y 80 residuales; 5.786 pares consecutivos revisados, sin gaps positivos ni overlaps. De 55 secciones verticales de 10 m entre los límites del grid candidato, 52 contienen composites de al menos dos sondajes. Número de sondajes por sección: min 2, Q1 4, mediana 17, Q3 43, max 44. Para 1.138 observaciones de vecino más cercano por sondaje/sección: min `1.02 m`, Q1 `24.74 m`, mediana `54.90 m`, Q3 `106.16 m`, max `275.78 m`. Medianas de sección: min `36.23 m`, mediana `58.77 m`, max `179.66 m`. Ejemplos: Z `3010–3020 m`, 3 sondajes y mediana NN `151.38 m`; Z `3270–3280 m`, 36 sondajes y mediana `48.62 m`; Z `3520–3530 m`, 2 sondajes y mediana `179.66 m`.
- Interpretación acotada: el soporte downhole de 2 m es continuo en los composites, pero no equivale a espaciamiento vertical. Las distancias horizontales típicas entre sondajes son mayores que el ancho candidato de 25 m y varían ampliamente por sección; esto requiere revisión de la resolución horizontal, pero no basta por sí solo para rechazar el tamaño ni constituye variografía/validación minera.
- Conclusión solicitada: `25 × 25 × 10 m` continúa como candidata conceptual, pero **requiere revisión antes de poder considerarse defendible o cerrar P2_GRID**. El grid sigue no aprobado; no se hizo topografía ni se modificaron código/datos.

### CHECKPOINT 27 — Comparación conceptual de tamaño de bloque P2

- El estudiante pidió revisar `25 × 25 × 10 m` contra una única alternativa más gruesa coherente con el espaciamiento horizontal aproximado de 55 m, calcular sus conteos con la envolvente/origen registrados, y si era coherente cerrar P2 como decisión conceptual aprobada para avanzar. Indicó continuar hacia P3/P4 y flujo mínimo, sin nuevas subpreguntas de P2 y sin implementar.
- Comparación aritmética ejecutada en memoria con envolvente provisional y origen retenido `(242225, 8196250, 2990) m`:

```text
25 × 25 × 10 m: nx × ny × nz = 30 × 27 × 55 = 44.550; máximo de malla = (242975, 8196925, 3540) m
50 × 50 × 10 m: nx × ny × nz = 15 × 14 × 55 = 11.550; máximo de malla = (242975, 8196950, 3540) m
```

- Evaluación técnica: la alternativa horizontal de 50 m es más coherente conceptualmente con medianas de vecino horizontal de 55.90 m para collars y 54.90 m dentro de secciones; es más gruesa que 25 m y reduce los bloques en 33.000 (aprox. 74.1%). La heterogeneidad del espaciamiento impide afirmar soporte uniforme. La altura de 10 m no queda demostrada por composites de 2 m downhole, que no expresan espaciado vertical.
- Cierre autorizado por la solicitud del estudiante: P2 queda como **decisión conceptual aprobada para avanzar al siguiente gate técnico**, con `50 × 50 × 10 m` como candidata revisada. No equivale a un gate de implementación ni a cierre técnico definitivo de `P2_GRID`; quedan por verificar origen, envolvente, márgenes/borde y fundamento vertical. No se usó topografía ni se cambió código/datos.
- Transición sin nueva subdecisión de P2: P3 no puede ejecutarse hasta desbloquear B09 (confirmación oficial de topografía y controles de cobertura/unidades/alineación). P4 mantiene la regla conceptual: intervalos litológicos posicionados como fuente categórica, composites para ubicar soporte assay, códigos literales y `UNKNOWN/UNASSIGNED` ante soporte conflictivo/insuficiente; falta posicionamiento reproducible y definición de regla. Flujo mínimo restante: gate de implementación del grid → clasificación topográfica cuando B09 esté autorizado/verificado → asignación categórica → validación computacional y minera/espacial → visualización 3D diagnóstica con superficie, clases y estados de soporte.

### CHECKPOINT 28 — Gate P4, grid y asignación categórica preliminar

- Respuesta original del estudiante:

> Elijo la alternativa A.
>
> Apruebo el alcance y la regla propuestos para P4:
>
> * crear src/mod1/block_model.py;
> * crear tests/test_m01b_block_model.py;
> * generar data/processed/m01b/block_model_preliminary.csv;
> * actualizar únicamente PLAN_G05 y EVIDENCE_G05 con resultados reales.
>
> Mantén la malla provisional de 50 × 50 × 10 m, origen (242225, 8196250, 2990) y forma 15 × 14 × 55.
>
> Apruebo la regla conservadora:
>
> * asignar un lith_code solo cuando todo el soporte litológico de la celda concuerde;
> * dejar UNKNOWN/UNASSIGNED si no hay soporte, hay conflicto o código vacío;
> * no usar mayoría ni extrapolación;
> * los composites solo cuentan soporte de assay y no modifican la categoría litológica;
> * no usar topografía ni clasificar AIR/ROCK.
>
> Después de implementar, ejecuta las pruebas focalizadas y la suite disponible, registra resultados reales y no hagas commit ni push.

- Evaluación explícita del agente: `CORRECTA`, H0. El gate autorizado cubrió módulo, tests, derivado y actualización de ambos documentos; no autorizó topografía, AIR/ROCK, commit ni push.
- Archivos creados: `src/mod1/block_model.py`, `tests/test_m01b_block_model.py`, `data/processed/m01b/block_model_preliminary.csv`. Se mantuvieron los cambios previos de los tres módulos M01 autorizados; no se modificaron otros fuentes, raw, IMP-002 ni composites.
- Regla ejecutada: cada intervalo litológico posicionado aporta el punto medio; si todos los códigos no vacíos que caen en una celda son idénticos, se asigna ese código literal. Sin soporte, si hay código vacío o códigos distintos, se emite `UNKNOWN/UNASSIGNED`; no se aplica mayoría ni extrapolación. Punto medio de composite solo incrementa conteo de soporte assay. Fuera de malla se produce `ValueError`.
- Geometría: origen `(242225, 8196250, 2990) m`, bloque `(50, 50, 10) m`, forma `(15,14,55)`, 11.550 celdas; sin topografía.
- CSV verificado: 11.550 filas e índices únicos; estados `ASSIGNED=102`, `UNKNOWN/UNASSIGNED=11.448`; soporte litológico en 107 celdas, incluidos 5 conflictos; 11.443 celdas sin soporte; 5.830 composites contados como soporte assay. Códigos asignados literalmente: `OVB=39`, `POR=32`, `VOL=23`, `BRX=8`. No se clasificó topografía ni se convirtió `AIR` en clase aire/roca.
- SHA-256 de `block_model_preliminary.csv`: `d42b4c83f065d6f9256985a04749d8375e380fe37991af932d34a1bd4fb19cf9`.
- Pruebas ejecutadas sobre código final:

```text
C:\CN\.venv\Scripts\python.exe -m pytest -q tests/test_m01b_block_model.py
6 passed in 0.05s

C:\CN\.venv\Scripts\python.exe -m pytest -q tests
23 passed in 0.11s

git -C C:\CN\PlanMinUPN-G05 diff --check
sin salida; sin problemas reportados
```

- Estado técnico: P4 `PARTIAL`, con modelo categórico preliminar generado; limitación: punto medio de intervalos no es intersección volumétrica ni validación geológica. P2 conceptual aprobado y candidato generado, no validación final. P3/B09 continúa `BLOCKED`; topografía no usada.
- Flujo restante: desbloquear y validar topografía antes de P3; luego validación espacial/minera del grid/asignaciones y gate separado para visualizador 3D. No se ejecutó commit ni push.
- Estado Git verificado al terminar: `src/mod1/desurvey.py`, `src/mod1/positioning.py`, `src/mod1/validator.py` modificados; `data/processed/m01b/block_model_preliminary.csv`, `src/mod1/block_model.py`, `tests/test_m01_spatial.py`, `tests/test_m01b_block_model.py` y `docs/exam/` no rastreados. HEAD sigue `9771efbecf4fb9fb1763d2cb0e99fa3280137b4a`; no hubo commit ni push. `git diff --check` sin salida.

## Comandos, inspecciones y resultados reales

### Git y estado

Comandos ejecutados en modo lectura:

```text
git -C C:\CN\PlanMinUPN-G05 status -sb
git -C C:\CN\PlanMinUPN-G05 branch --show-current
git -C C:\CN\PlanMinUPN-G05 rev-parse HEAD
git -C C:\CN\PlanMinUPN-G05 stash list --date=iso
git -C C:\CN\PlanMinUPN-G05 stash show --stat --include-untracked 'stash@{0}'
git -C C:\CN\PlanMinUPN-G05 stash show --stat --include-untracked 'stash@{1}'
git -C C:\CN\PlanMinUPN-G05 stash show --name-status --include-untracked 'stash@{0}'
git -C C:\CN\PlanMinUPN-G05 stash show --name-status --include-untracked 'stash@{1}'
git -C C:\CN\PlanMinUPN-G05 show 'stash@{0}:<ruta>'
git -C C:\CN\PlanMinUPN-G05 ls-tree -r --name-only 'stash@{0}^3'
```

Resultado observado: rama `feature/m01b-block-model`; HEAD `9771efbecf4fb9fb1763d2cb0e99fa3280137b4a`; `?? docs/exam/`; dos stashes. No se ejecutó `stash apply/pop`.

### Integridad y auditorías de datos

- SHA-256 de archivos enumerados en `release_manifest.json`: todos coincidieron con el manifiesto.
- CSV raw: comprobaciones directas de intervalos, duplicados, continuidad, cobertura collar y contactos; resultados detallados consignados en el plan.
- Topopl del snapshot del stash: leído por `git show` en memoria; hash/conteo/rangos calculados, sin extracción a `data/raw/`.
- Composites: lectura de `data/processed/m01b/composites.csv`; se comprobaron límites, longitudes, continuidad, contactos, códigos literales y trazabilidad source IDs.
- Reproducción de composites: candidato M01 extraído por `git show` a un directorio temporal, ejecutado contra `data/raw/`; CSV generado idéntico byte por byte al derivado del checkout. El directorio temporal se eliminó al finalizar.

Resultados de composites:

```text
assays=5803; lithology=120; composites=5830; holes=44
assay/composite length sum=11574.785091049 m; difference=0
Cu mean ponderada assay=0.300527693137281 %
Cu mean ponderada composites=0.300527693137280 %
composites cruzando contacto de código distinto=0
composites sin cobertura litológica completa=0
XYZ midpoint no finito=0
residuales menores de 2 m=80
source sample IDs únicos=5803; IDs fuente faltantes=0; desconocidos=0
```

### Tests y validador del candidato aislado

- Se creó un árbol temporal con código traído por `git show`; no se aplicó el stash ni se alteró el checkout.
- Comando de test invocado dentro del árbol temporal: `C:\CN\.venv\Scripts\python.exe -m pytest -q tests`.
- Resultado real: `71 passed, 10 subtests passed in 1.42s`; exit code `0`.
- `validate_data` se invocó con loader actual y validador de `stash@{0}`, apuntando a los CSV raw del checkout; resultado: 4 `INFO` (ASSAY-03 ×2, DENS-03 ×1, REL-04 ×1), cero `ERROR`/`WARNING`.
- Desurvey/positioning del candidato en entorno temporal: 44 holes, 313 estaciones; 5.803 assays, 120 lithology, 0 alteration, 459 density; XYZ finitos; MD=0 collar exacto 44/44; cero errores de validator.
- Estas pruebas/ejecuciones verifican el candidato y no equivalen a TESTED en HEAD.

### No ejecutado

- No se ejecutó validación de cobertura/compatibilidad topográfica.
- No se generó figura 2D/3D.
- No se modificaron otros archivos derivados, `data/raw/`, IMP-002 ni otros archivos de código fuente aparte del módulo P4 autorizado. Se recuperaron selectivamente los tres módulos M01 autorizados y se añadieron los dos archivos de prueba bajo sus gates.

## Estado Git al final de las verificaciones

Se volvió a consultar `git status -sb` y HEAD tras las comprobaciones:

```text
## feature/m01b-block-model
 M src/mod1/desurvey.py
 M src/mod1/positioning.py
 M src/mod1/validator.py
?? docs/exam/
?? tests/test_m01_spatial.py
9771efbecf4fb9fb1763d2cb0e99fa3280137b4a
```

El hash SHA-256 del CSV de composites fue registrado previamente como `7a00a557bf604eba8ac45d158ba2a01a6d03caa8fccd14b020c47df478b4193c`; no se volvió a calcular en este cierre. La carpeta `docs/exam/` aparece no rastreada y contiene estos dos documentos autorizados además de los documentos T2 preexistentes.

## Bloqueos y límites pendientes

1. B09: confirmar con el docente la procedencia oficial de `Topopl.csv`; después validar cobertura y compatibilidad espacial.
2. B02/B03: los módulos recuperados siguen modificados respecto de HEAD; se requieren controles/versionado autorizados para demostrar reproducibilidad desde HEAD limpio. Las pruebas específicas M01 y la suite más reciente se ejecutaron en el árbol de trabajo; no implican HEAD limpio.
3. B04/B08/B10: visualización M01 activa, reproducibilidad/evidencia sincronizada con HEAD y trazabilidad completa siguen parciales o faltantes.
4. B05: reconciliar IMP-002 y baseline con la realidad de HEAD, sin reescribir hechos históricos.
5. B06: convertir los controles observados en evidencia reproducible, manteniendo la diferencia entre auditoría raw y resultados del candidato.
6. Códigos geológicos: falta significado oficial; conservarlos literalmente.
7. P2: decisión conceptual aprobada en `50×50×10 m` y grid candidato generado; origen local, margen/borde, extensión final y fundamento vertical siguen provisionales.
8. P3: regla de vértices conceptual; sin topo oficial no hay clasificación real.
9. P4: modelo categórico preliminar generado por punto medio; pendiente validación geológica/minera y posible refinamiento a intersección volumétrica. Composites no son corroboración geológica independiente.
10. P5/P6: la validación minera/espacial sigue pendiente. En el checkpoint 29 se generaron y revisaron visualmente el visualizador y el HTML diagnóstico P6; no constituyen validación geológica ni topográfica.
11. El gate P4 fue aprobado y ejecutado; permanece pendiente verificación geológica/minera y no equivale a `BASE_VERIFIED`.

### CHECKPOINT 29 — Implementación y revisión visual P6

- Respuesta literal del estudiante:

> Elijo la alternativa A.
>
> Autorizo instalar únicamente plotly y pytest en el entorno Python disponible para completar P6.
>
> Después:
>
> * ejecuta las pruebas focalizadas del visualizador;
> * ejecuta la suite disponible;
> * genera outputs/figures/m01b_block_model_preliminary.html;
> * inspecciona visualmente el HTML;
> * registra solo resultados reales en PLAN_G05 y EVIDENCE_G05.
>
> No instales otras dependencias, no uses topografía, no modifiques otros archivos y no hagas commit ni push.

- Instalación autorizada: `python -m pip install plotly pytest` terminó correctamente. Versiones directas instaladas: Plotly 7.1.0 y pytest 9.1.1. pip resolvió además dependencias transitivas requeridas por esos paquetes; no se añadió ni editó un manifiesto del proyecto.
- Implementación en el alcance aprobado:
  - `src/mod1/block_model_visualizer.py`: lectura/validación del CSV P4; una malla por código observado y otra por `UNKNOWN/UNASSIGNED`; trazas de sondajes M01; hover con índices, centro XYZ en m, código/estado y soporte litológico/assay; exportación HTML autónoma.
  - `tests/test_m01b_visualizer.py`: cinco pruebas sobre esquema/inconsistencias de entrada, categorías/estado, soporte, trayectorias, advertencia de límites y HTML autónomo.
  - `outputs/figures/m01b_block_model_preliminary.html`: salida autorizada, 20.253.766 bytes. Contiene 11.550 bloques, 49 trazas (BRX, OVB, POR, VOL, `UNKNOWN/UNASSIGNED` y 44 trayectorias), con filtro de leyenda por código/estado y sondajes. El grupo `UNKNOWN/UNASSIGNED` está en la leyenda y comienza oculto (`legendonly`) para no cubrir la distribución asignada; se puede activar desde el control.
- Comandos y resultados finales reales:

```text
python -m pytest tests\test_m01b_visualizer.py -q
5 passed in 1.19s

python -m pytest -q
28 passed in 1.24s
```

- Hubo fallos durante las primeras iteraciones del test por una aserción de texto y por no pasar la visibilidad de leyenda al constructor de malla; se corrigió y se ejecutaron de nuevo ambas pruebas, con los resultados finales anteriores.
- Generación: `build_visualization_from_files(data/processed/m01b/block_model_preliminary.csv, data/raw)` y `write_block_model_html(...)` produjeron 49 trazas y 11.550 bloques; códigos asignados `BRX`, `OVB`, `POR`, `VOL`; `topography_used=False`; `validation_claim=False`; el estado UNKNOWN comienza como `legendonly`.
- Inspección visual: Chrome headless renderizó el HTML local como PNG de 1600×1100 px; la imagen renderizada fue abierta y revisada. Se observan el título/advertencia de diagnóstico, las cuatro categorías asignadas, la leyenda con conteos, trayectorias y ejes XYZ. UNKNOWN aparece en la leyenda para activarse como filtro. No se incorporó topografía y no se interpretó la figura como validación geológica o topográfica.
- P6 permanece `PARTIAL`: se verifica una visualización computacional auditable, no la validez geológica/minera de las categorías ni la relación con superficie. B09 continúa `BLOCKED`. No se modificaron datos raw, no se hizo commit ni push.

### HISTÓRICO — CHECKPOINT 30 — Cierre anterior de pauta T2 M01B

- Solicitud literal del estudiante:

> P6 ya fue implementado y verificado.
>
> Continúa directamente con el cierre final de la pauta T2 M01B.
>
> Completa en PLAN_G05 y EVIDENCE_G05:
>
> * evidencias esperadas y rutas reales;
> * estado de gates;
> * conclusión técnica de qué se construyó realmente;
> * qué permanece PARTIAL/BLOCKED;
> * principal limitación de confiabilidad del modelo;
> * estado Git final;
> * siguiente paso pendiente.
>
> Usa únicamente resultados reales de esta sesión. Mantén B09 como BLOCKED y P6 como PARTIAL. No inventes validación topográfica ni geológica.
>
> No realices más cambios técnicos, instalaciones, commit ni push.

- PLAN_G05 se completó con tabla de evidencias esperadas y rutas existentes, estados de gates, conclusión técnica, principal limitación, estados `PARTIAL`/`BLOCKED`, estado Git y siguiente paso pendiente. EVIDENCE_G05 recibió este registro literal y el cierre con la evidencia real de P6 registrada en checkpoint 29.
- Estados preservados: B09 `BLOCKED`, P6 `PARTIAL`, recuperación `RECOVERY_BLOCKED`; no se atribuye validación topográfica ni geológica.
- El cierre documental recoge como resultado final P6: 5 pruebas focalizadas aprobadas, 28 pruebas de suite aprobadas, HTML autónomo generado e inspeccionado visualmente; no se ejecutaron nuevas pruebas ni se generaron nuevos artefactos durante este checkpoint.
- Estado Git al cierre documental: rama `feature/m01b-block-model`, HEAD `9771efbecf4fb9fb1763d2cb0e99fa3280137b4a`; `git diff --check` sin problemas tras actualizar PLAN_G05 y EVIDENCE_G05. Los archivos y estados detallados están enumerados en PLAN_G05. No se realizó commit ni push, no se aplicó/eliminó stash, no se instalaron dependencias en este cierre ni se modificaron archivos técnicos o datos fuente.
- Próximo paso pendiente: confirmación docente verificable de procedencia oficial de topografía antes de abrir P3 o realizar cualquier uso/clasificación de esa superficie. La validación minera/geológica permanece pendiente.

## ESTADO FINAL VIGENTE — prevalece sobre el checkpoint 30

El estado técnico final actual es el descrito al inicio: rama
`feature/m01b-block-model`, HEAD actual/documental `207ba75`, commit técnico del
modelo final `a70b546`, base `BASE_VERIFIED`, árbol limpio después del commit
técnico y suite completa con `41 passed`. B00–B10 están
`VERIFIED` con los alcances y cautelas de la tabla vigente; P3, P4, P5 y P6 están
`VERIFIED` dentro de su alcance documentado. El checkpoint 30 y los registros
anteriores se conservan como evidencia histórica, no como resumen vigente.
P2 es una decisión conceptual aprobada para el alcance preliminar, no una
selección técnica definitiva u optimizada; la cobertura de la topografía se
refiere a los centros XY necesarios para clasificar el grid, no a la nube raw
completa.
