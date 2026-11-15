# Plan conceptual T2 M01B — G05

## Estado vigente

- **Rama:** `feature/m01b-block-model`.
- **HEAD actual/documental:** `66e1ae3`.
- **Commit documental anterior:** `207ba75`.
- **Commit técnico del modelo final:** `a70b546` (`feat: integrate topography and geological validation into M01B block model`).
- **Git:** HEAD `66e1ae3`; esta revisión documental se encuentra en curso y no
  está incluida en un commit.
- **Suite completa:** `41 passed`.
- **`git diff --check`:** limpio antes del commit técnico final.
- **Estado base vigente:** `BASE_ACCEPTED_WITH_LIMITATIONS`, suficiente para
  continuar el ejercicio académico M01B, pero no equivalente a que todas las
  fuentes, metadatos o validaciones estén completos.
- **Alcance:** cierre técnico computacional de M01B; la validación geológica comprueba coherencia contra intervalos y contactos observados, no constituye certificación profesional externa.

### Estado vigente de B00–B10

| ID | Estado | Evidencia y límite |
|---|---|---|
| B00 | `VERIFIED` | Rama `feature/m01b-block-model`, HEAD actual/documental `66e1ae3`; commit documental anterior `207ba75` y commit técnico del modelo `a70b546`. |
| B01 | `PARTIAL` | Manifiesto e integridad del release original verificados. `Topopl.csv` está técnicamente integrado, pero no figura en el manifiesto original; procedencia oficial, CRS/EPSG y datum vertical no están acreditados/documentados. |
| B02 | `VERIFIED` | La ejecución documentada del validador reportó 4 hallazgos `INFO` y ningún `ERROR` o `WARNING`; las pruebas de la suite final pasaron. |
| B03 | `VERIFIED` | Se generaron trayectorias y posiciones XYZ utilizables: 44 sondajes/313 estaciones y 120 intervalos litológicos posicionados; las pruebas de la suite final pasaron. |
| B04 | `VERIFIED-HISTORICAL` | Capacidad histórica verificada: `stash@{0}` y `stash@{1}` contienen `src/mod1/visualizer.py`, `tests/test_visualizer.py` y `outputs/figures/m01_drillholes_3d_DS05_EXP03.html`; `baseline_M01B.txt` registra históricamente 62 tests y 10 subtests aprobados. No está activa en HEAD; la visualización vigente está cubierta por P6. |
| B05 | `VERIFIED` | Las decisiones y resultados vigentes están documentados en IMP-003 e IMP-004 y reconciliados aquí con el HEAD técnico final. |
| B06 | `VERIFIED` | Auditoría reproducida sobre los datos actuales: 5.803 assays y 120 intervalos litológicos en 44 sondajes; 0 gaps, 0 overlaps y 0 discrepancias `length_m != to_m - from_m`; 76 contactos contiguos con cambio de código y 48 assays que cruzan al menos un contacto; cobertura assay desde MD 0 hasta profundidad final en 44/44 sondajes. Las pruebas focalizadas relacionadas pasaron: 16. El alcance es coherencia/trazabilidad de datos observados, no interpretación geológica externa. |
| B07 | `VERIFIED` | La regla de compositado y sus decisiones siguen documentadas en el baseline; no se atribuye interpretación geológica a los códigos. |
| B08 | `VERIFIED` | `src/mod1/compositing.py` regeneró 5.830 composites byte por byte idénticos a `data/processed/m01b/composites.csv` versionado (SHA-256 `7a00a557bf604eba8ac45d158ba2a01a6d03caa8fccd14b020c47df478b4193c`). Longitud total: 11.574,785091049 m; Cu ponderado conservado dentro del redondeo por precisión del formato CSV (diferencia `4.55e-12`, no un fallo). Los 5.803 IDs raw están representados en 9.506 referencias de origen debido a divisiones en contactos; 5.750 composites completos y 80 residuales. Las pruebas focalizadas de compositing pasaron. |
| B09 | `VERIFIED` | Dentro del alcance computacional/topográfico implementado: `Topopl.csv` integrado, 210/210 centros XY con TIN finita, intersección en Z comprobada y 11.550 bloques clasificados. No valida CRS/datum ni implica que toda la nube esté dentro: 69.266 puntos están en el rectángulo XY y 148.846 fuera. |
| B10 | `VERIFIED` | Suite completa con 41 pruebas aprobadas, `git diff --check` limpio antes del commit, artefactos y documentación trazables, y árbol limpio tras el commit técnico final. |

La integridad del release original sí está verificada. B01 permanece `PARTIAL`
porque la topografía adicional y sus metadatos/procedencia oficial no están
cubiertos por ese manifiesto.

### Geometría y resultados vigentes

- **Grid preliminar:** bloques de `50 × 50 × 10 m`; dimensiones `15 × 14 × 55`, total `11.550` bloques. El origen documentado es provisional, no una referencia minera oficial.
- **P2:** decisión conceptual aprobada para el alcance preliminar; reproducibilidad y cobertura verificadas, optimización del tamaño/origen no demostrada. Para el modelo categórico preliminar del alcance T2 se adopta una malla reproducible de 50 × 50 × 10 m, con forma 15 × 14 × 55 (11,550 bloques) y origen local provisional (242225, 8196250, 2990) m. La dimensión horizontal de 50 m se eligió como escala conceptual comparable con las medianas observadas de distancia al collar vecino más cercano (55.90 m) y de espaciamiento por sección (54.90 m; mediana de las medianas por sección: 58.77 m); la cobertura es heterogénea y este análisis no constituye variografía ni demuestra un tamaño óptimo. La dimensión vertical de 10 m se conserva como discretización adoptada, pero no está justificada formalmente por el espaciamiento vertical observado. El origen se obtuvo por redondeo inferior respecto del cero numérico local con incrementos de 25/25/10 m para la candidata conceptual anterior y se retuvo al pasar a 50/50/10 m; no es una referencia oficial.
- **Clasificación topográfica:** `ROCK` 6.853; `AIR` 4.493; `PARTIAL` 204. Es una clasificación computacional por elevación interpolada en XY, no una fracción volumétrica.
- **Cobertura espacial verificada:** 44/44 collars y 313/313 estaciones de trayectoria están dentro del grid; los 120 intervalos litológicos contabilizan `11,574.785091049 m` dentro y `0 m` fuera; los 210 centros XY tienen elevación TIN finita. Esto no implica que toda la nube topográfica raw esté dentro: 69.266 puntos están en el rectángulo XY del grid y 148.846 fuera.
- **Procedencia topográfica:** `Topopl.csv` está integrado técnicamente (218.112 registros `PID/X/Y/Z`), pero no aparece en el `release_manifest.json` original. Hay referencia documental/histórica de compatibilidad espacial indicada por el docente, no prueba de procedencia oficial.
- **Validación geológica observada:** 120 intervalos litológicos posicionados y 76 contactos; `11,574.785091049 m` contabilizados dentro de la malla y `0 m` fuera. Hay 978 bloques con intersección positiva, 68 conflictos y 10.504 bloques sin soporte. Conflictos y bloques sin soporte permanecen `UNKNOWN/UNASSIGNED`.
- **Visualización P6:** HTML 3D integrado con topografía, bloques, sondajes, intervalos litológicos, contactos y sección X-Z.
- **Gates vigentes:** P3 `VERIFIED` para integración/clasificación computacional; P4/P5 `VERIFIED` para coherencia y trazabilidad observacional/computacional, sin demostrar continuidad geológica entre sondajes ni certificación externa/operacional; P6 `VERIFIED` para visualización diagnóstica/interactiva.
- CRS/EPSG de `Topopl.csv` y datum/referencia vertical de `Topopl.csv.Z`: NO
  DOCUMENTADOS EN LAS FUENTES DISPONIBLES. No se infieren UTM, WGS84, PSAD56,
  zona, EPSG ni transformación. Los códigos `OVB`, `BRX`, `POR`, `VOL` y `AIR`
  se describen únicamente como `Observed lithology code`; no se interpretan.
  `lith_code=AIR` es distinto de `topo_status=AIR`.

## HISTÓRICO — diagnóstico de base B00–B10 anterior

Los estados y pendientes de esta sección reflejan el diagnóstico inicial y quedan
conservados como historial; no describen el estado técnico final vigente.

| ID | Estado | Evidencia y pendiente |
|---|---|---|
| B00 | `VERIFIED` | Rama `feature/m01b-block-model`, HEAD `9771efbecf4fb9fb1763d2cb0e99fa3280137b4a`. `git status -sb` mostró `?? docs/exam/`; el checkout no estaba completamente limpio. |
| B01 | `VERIFIED` | Los archivos enumerados en `data/raw/release_manifest.json` existen y sus SHA-256 coincidieron con el manifiesto. `data/raw/data_dictionary.csv` define campos y unidades. La topografía no figura en ese manifiesto. |
| B02 | `PARTIAL` | `src/mod1/validator.py` se recuperó selectivamente desde `stash@{0}` al árbol de trabajo, sin aplicar el stash; sigue modificado y sin commit. En la ejecución con datos actuales reportó 4 hallazgos `INFO`, ningún `ERROR` o `WARNING`. `tests/test_m01_spatial.py` añade dos pruebas sintéticas del validador; las seis pruebas focalizadas y la suite completa disponible pasaron. No demuestra HEAD limpio ni validación minera. |
| B03 | `PARTIAL` | `src/mod1/desurvey.py` y `src/mod1/positioning.py` se recuperaron selectivamente desde `stash@{0}` al árbol de trabajo y siguen modificados/sin commit. La ejecución en memoria procesó 44 sondajes/313 puntos de trayectoria y posicionó 5.803 assays, 120 intervalos litológicos y 459 muestras de densidad; XYZ finitos y 44/44 puntos MD=0 iguales a sus collars. `tests/test_m01_spatial.py` añade cuatro pruebas sintéticas de trayectoria/interpolación; las seis pruebas focalizadas y la suite completa disponible pasaron. No demuestra HEAD limpio ni validación minera. |
| B04 | `MISSING` | No hay visualizador M01 activo ni figura M01 en `outputs/figures/` del checkout; hay código, tests y figura histórica dentro del stash. Su ausencia no bloquea por sí sola la geometría según el escenario. |
| B05 | `PARTIAL` | `docs/implementation/IMP-002_m01b_block_model_preparation.md` y un baseline histórico describen decisiones/resultados, pero contienen estado distinto del checkout actual. Falta reconciliar el registro con HEAD y con evidencia reproducible activa. |
| B06 | `PARTIAL` | Auditoría directa de `data/raw/`: 5.803 assays y 120 intervalos de litología en 44 sondajes, sin gaps/overlaps internos; 76 contactos entre códigos diferentes y 48 assays que cruzan al menos un contacto. Falta validar de forma reproducible desde el checkout y completar el diagnóstico integral. |
| B07 | `VERIFIED` | IMP-002 documenta composites objetivo de 2 m, Cu ponderado por longitud, separación por código litológico y preservación de residuales. Es la regla documentada; no valida todos los aspectos de reproducción actual. |
| B08 | `PARTIAL` | `src/mod1/compositing.py`, `tests/test_m01b_compositing.py` y `data/processed/m01b/composites.csv` existen. El CSV contiene 5.830 composites. El candidato M01 del stash + compositing actual regeneró un CSV idéntico byte por byte al del checkout; esa ruta no está activa en HEAD. |
| B09 | `BLOCKED` | `data/raw/topography/Topopl.csv` no existe en HEAD ni aparece en el manifiesto; sí está en el snapshot no rastreado de `stash@{0}`. Tiene 218.112 registros, cabecera `PID,X,Y,Z`, SHA-256 `1724a97f1fa6f6a059def896d1ba566b1e23d6f78781034bf2e3f53d2d4b1887` y rangos coincidentes con IMP-002. No hay referencia verificable que pruebe que ese archivo concreto es la fuente oficial. No se usó para clasificar. |
| B10 | `PARTIAL` | La suite disponible en el árbol de trabajo terminó con 23 pruebas aprobadas, incluidas seis para validator/desurvey/positioning y seis de block model. `git diff --check` no reportó problemas. Los módulos siguen modificados respecto de HEAD y no hay validación minera/topográfica completa; no equivale a un checkout limpio ni cierra B10. Los 71 tests y 10 subtests del candidato aislado son evidencia histórica separada. |

### Estado base histórico (anterior)

`RECOVERY_BLOCKED`, no `BASE_VERIFIED`. M01 fue recuperado selectivamente al árbol de trabajo con autorización y ahora cuenta con seis pruebas sintéticas focalizadas; la suite disponible obtuvo 17 aprobaciones. Aun así, los tres módulos están modificados respecto de HEAD, no se verificó un checkout limpio y falta reconciliar IMP-002 con el estado actual. También falta confirmar con el docente la procedencia oficial de la topografía y verificarla. B09 bloquea cualquier clasificación real aire/roca/parcial y su validación.

## HISTÓRICO — decisiones conceptuales registradas

### P1 — códigos, límites y estados

- Se conservarán los códigos `OVB`, `BRX`, `POR`, `VOL`, `AIR` literalmente, sin interpretación, agrupación ni renombramiento hasta obtener diccionario/confirmación geológica oficial.
- Propuesta del estudiante: asignar categoría solo con soporte de un único código observado; ante conflicto, usar `UNKNOWN/UNASSIGNED`.
- Para preservar límites, el estudiante escogió conceptualmente exigir concordancia entre observaciones y dejar sin asignar los conflictos.
- Limitación aceptada: no se ha definido la medición de concordancia; faltan significado geológico de códigos y posicionamiento activo.

### P2 — geometría preliminar, decisión conceptual aprobada; validación final pendiente

- Rango conjunto observado de collars y puntos medios de composites: X `242228.128434–242971.871566 m`; Y `8196266.798008–8196913.201992 m`; Z `2995.885049–3532.000000 m`. Extensiones: X `743.743133 m`, Y `646.403984 m`, Z `536.114951 m`.
- `25 × 25 × 10 m` quedó como candidata conceptual. Conteo ilustrativo por `ceil(extensión/dimensión)`: `30 × 26 × 54 = 42.120` celdas. No es un grid aprobado ni un conteo definitivo.
- Refinamiento conceptual posterior: al alinear origen inferior a múltiplos regulares de las dimensiones de bloque con respecto al cero numérico local, se propuso `(X,Y,Z)=(242225, 8196250, 2990) m`. La envolvente provisional queda cubierta por `30 × 27 × 55 = 44.550` bloques, con máximo de malla `(242975, 8196925, 3540) m`. Márgenes respecto de la envolvente observada: bajo X/Y/Z `3.128434 / 16.798008 / 5.885049 m`; sobre X/Y/Z `3.128434 / 11.798008 / 8.000000 m`. Es una propuesta aritmética conceptual, no origen oficial ni aprobación de `P2_GRID`.
- Se compararon además `12,5 × 12,5 × 5 m` (`60 × 52 × 108 = 336.960` celdas) y `50 × 50 × 20 m` (`15 × 13 × 27 = 5.265` celdas). La comparación usa carga relativa por número de celdas, no tiempo medido.
- El estudiante eligió mantener el origen y conteo anteriores como candidatos conceptuales; el origen se basa en el cero de coordenadas locales, no en referencia oficial. El análisis descriptivo mostró vecindad horizontal típica mayor que 25 m, por lo que se comparó con una única alternativa más gruesa de 50 × 50 × 10 m.
- Espaciamiento descriptivo de collars: para los 44 collars, vecino más cercano horizontal con mediana `55.90 m`, Q1 `22.81 m`, Q3 `89.02 m`, mínimo `10.17 m`, máximo `180.00 m`; 12/44 vecinos más cercanos están a `≤25 m`, 14/44 a `≤50 m`, 37/44 a `≤100 m`. Direcciones exploratorias del vecino más cercano: 16 pares orientados principalmente en X, 18 en Y y 10 diagonales. En las 810 celdas XY nominales de 25×25 m de la candidata, 42 contienen collars (40 con un sondaje y 2 con dos).
- Soporte downhole y secciones: `5.830` composites, de los cuales `5.750` miden 2 m y `80` son residuales; no se observaron gaps ni overlaps entre composites consecutivos por sondaje. En secciones de elevación de 10 m definidas respecto de Z=2990, 52 de 55 secciones tienen al menos dos sondajes con composites; por sección hay mediana 17 sondajes (Q1 4, Q3 43; rango 2–44). Entre sondajes dentro de esas secciones, las distancias al vecino horizontal más cercano tienen mediana `54.90 m` (Q1 `24.74 m`, Q3 `106.16 m`); la mediana de las medianas por sección es `58.77 m` (rango `36.23–179.66 m`). La cobertura observada es heterogénea.
- Los 2 m describen longitud downhole, no espaciado vertical; el ángulo de trayectoria condiciona su proyección espacial. Estas estadísticas son descriptivas, no variografía ni criterio formal de selección de tamaño.
- Conclusión P2 sobre tamaño: `25 × 25 × 10 m` requiere revisión por resolución horizontal fina frente a la vecindad observada. La alternativa conceptual revisada es `50 × 50 × 10 m`: con origen provisional conservado `(242225, 8196250, 2990) m`, produce `15 × 14 × 55 = 11.550` bloques y máximo `(242975, 8196950, 3540) m`. Es más coherente en horizontal con la mediana de vecino más cercano de collars (`55.90 m`) y la mediana por sección (`54.90 m`), aunque la cobertura es heterogénea. La dimensión vertical de 10 m sigue sin justificación formal; intervalos de 2 m son downhole, no espaciado vertical.
- A solicitud expresa del estudiante, P2 se aprobó conceptualmente para avanzar al siguiente gate técnico con `50 × 50 × 10 m`. Bajo el gate P4 aprobado se generó la malla candidata de `15 × 14 × 55 = 11.550` bloques usando el origen provisional. La geometría sigue siendo preliminar, no una definición minera final: origen local no oficial, envolvente provisional, márgenes condicionados a trayectoria/topografía, criterio de borde y justificación vertical formal permanecen como limitaciones. No se usó topografía.

### P3 — relación topográfica

- El estudiante eligió conceptualmente evaluar la relación superficie–vértices para reconocer bloques totalmente sobre/bajo superficie y posibles bloques mixtos.
- No calcula fracción de roca por sí solo. P3 queda pendiente de B09; no se hizo clasificación topográfica real.

### P4 — asignación categórica

- Decisión conceptual vigente: tratar los intervalos litológicos como fuente categórica y usar los composites únicamente para ubicar el soporte de assay. El estudiante señaló que `lith_code` en composites fue heredado de los intervalos litológicos, por lo que las etiquetas no son observaciones geológicas independientes.
- La propuesta anterior de exigir concordancia entre ambas fuentes se refina: los composites no se consideran corroboración geológica adicional. Se conserva su función de soporte/trazabilidad de assays.
- Regla implementada bajo gate aprobado: posicionar intervalos con la ruta M01 recuperada, asignar cada intervalo por su punto medio XYZ, y asignar código literal solo si todos los intervalos con punto medio en una celda tienen el mismo código no vacío. Sin soporte, código vacío o conflicto implica `UNKNOWN/UNASSIGNED`; no hay voto mayoritario ni extrapolación. Composites solo incrementan `assay_composite_support_count`.
- Salida `data/processed/m01b/block_model_preliminary.csv`: 11.550 bloques; 107 celdas con soporte litológico, 102 asignadas y 5 en conflicto; 11.443 sin soporte quedan `UNKNOWN/UNASSIGNED`. Se conservaron `OVB`, `BRX`, `POR`, `VOL`, `AIR` literalmente; las asignaciones generadas fueron `OVB` 39, `POR` 32, `VOL` 23 y `BRX` 8. Los dos soportes `AIR` no generaron categoría asignada; no se hizo clasificación topográfica ni conversión AIR/ROCK.
- Composites: 5.830 puntos medios sumados en `assay_composite_support_count`, sin efecto sobre las categorías litológicas. P4 permanece `PARTIAL`: la regla de punto medio es soporte categórico conservador, no intersección volumétrica ni validación geológica/minera; significado oficial de códigos pendiente.

### P5 — pruebas y validación

- El estudiante eligió registrar pruebas computacionales y validación minera como evidencias parciales y no aceptar P5 completo hasta verificarlas por una ruta reproducible.
- Prioridad conceptual elegida: pruebas y reproducibilidad desde HEAD cuando se autorice recuperar M01. La evidencia existente —71 tests y 10 subtests del candidato aislado y regeneración idéntica de 5.830 composites— no verifica los stubs M01 del checkout actual.
- Tras recuperación selectiva autorizada se añadieron seis pruebas sintéticas focalizadas para validator, desurvey y positioning; las seis pasaron. La suite disponible completa pasó 17 pruebas.
- Con gate P4 posterior se añadieron seis pruebas de block model; pasaron y la suite disponible completa terminó con 23 pruebas aprobadas.
- Esta evidencia verifica pruebas computacionales en el árbol de trabajo, pero no demuestra por sí sola validez geológica, no valida topografía ni resuelve B09. P5 permanece `PARTIAL`; las validaciones mineras y espaciales siguen pendientes.

### P6 — visualización diagnóstica

- El estudiante eligió conceptualmente iniciar con secciones o vistas 2D de datos disponibles, sin llamarlas visualización del modelo de bloques.
- Ventaja indicada: inspeccionar distribución, contactos y soporte sin grid ni topografía. Limitación indicada: no representa volumen 3D ni valida relación con superficie.
- Bajo gate posterior se implementó `src/mod1/block_model_visualizer.py`, pruebas en `tests/test_m01b_visualizer.py` y el HTML interactivo autónomo `outputs/figures/m01b_block_model_preliminary.html`. La figura contiene 11.550 bloques: 8 BRX, 39 OVB, 32 POR, 23 VOL y 11.448 `UNKNOWN/UNASSIGNED`; además, incluye 44 trazas de sondajes. Las categorías y los sondajes pueden filtrarse desde la leyenda; `UNKNOWN/UNASSIGNED` aparece en la leyenda y se activa bajo demanda para no ocultar inicialmente los bloques asignados.
- El hover incluye índices, centro XYZ (m), código/estado litológico, conteos/códigos de soporte y soporte de composites; las trayectorias muestran MD y XYZ. La inspección se realizó con captura HTML en Chrome headless y revisión de la imagen renderizada; se observaron título/advertencia, leyenda, categorías asignadas y trayectorias. La salida declara que no usa topografía ni constituye validación geológica/topográfica.
- Pruebas reales finales: `python -m pytest tests\test_m01b_visualizer.py -q` → 5 aprobadas; `python -m pytest -q` → 28 aprobadas. P6 permanece `PARTIAL`: la salida visual diagnóstica existe, pero no prueba validez geológica, minera ni topográfica.

## HISTÓRICO — gating y alcance anterior

- Se aprobaron y ejecutaron gates limitados para recuperar selectivamente tres módulos M01, crear pruebas sintéticas en `tests/`, construir el grid preliminar con asignación categórica por punto medio e implementar el visualizador diagnóstico 3D P6. No se aprobó ni ejecutó clasificación topográfica/minera.
- P2 fue aprobado conceptualmente y su geometría candidata se generó bajo el gate P4. P3 y validación minera completa (`P5_VALIDATION`) siguen pendientes. P6 tiene visualizador y salida generada bajo el gate aprobado, pero no equivale a validación geológica/topográfica.
- B02/B03 permanecen `PARTIAL`; B09 permanece `BLOCKED`. Bajo `RECOVERY_BLOCKED` no procede atribuir validación minera/topográfica ni asumir topografía oficial, geometría final, interpretación geológica o resultados no comprobados.

## HISTÓRICO — cierre anterior a IMP-003/IMP-004

### Evidencias esperadas y artefactos/rutas reales

| Evidencia esperada | Ruta real y estado |
|---|---|
| Tabla de bloques preliminar con índices, geometría, categoría y conteos de soporte | `data/processed/m01b/block_model_preliminary.csv` — generada: 11.550 bloques. |
| Implementación reproducible de grid/asignación categórica | `src/mod1/block_model.py` — presente; la asignación usa puntos medios de intervalos litológicos, no intersección volumétrica. |
| Pruebas del block model | `tests/test_m01b_block_model.py` — seis pruebas focalizadas reportadas previamente como aprobadas. |
| Pruebas de visualización | `tests/test_m01b_visualizer.py` — 5 aprobadas en la etapa P6. |
| Visualizador y salida 3D auditable | `src/mod1/block_model_visualizer.py` y `outputs/figures/m01b_block_model_preliminary.html` — presentes; HTML autónomo generado e inspeccionado visualmente. |
| Trazabilidad de decisiones y resultados G05 | `docs/exam/T2_M01B_PLAN_G05.md` y `docs/exam/T2_M01B_EVIDENCE_G05.md` — actualizados. |
| Topografía oficial verificada y clasificación superficie/bloques | No disponible/verificada; B09 `BLOCKED`. No se usó topografía ni se clasificó `AIR/ROCK`. |

### Estado de gates al cierre

| Etapa/gate | Estado registrado |
|---|---|
| Recuperación de M01 | Recuperación selectiva aprobada y ejecutada en el árbol de trabajo; B02/B03 `PARTIAL`, no se demuestra HEAD limpio. |
| `P2_GRID` | Decisión conceptual aprobada para 50×50×10 m, origen provisional (242225, 8196250, 2990), forma 15×14×55; el grid de 11.550 celdas se generó bajo el gate P4. No es geometría minera final. |
| `P3_TOPO` | `BLOCKED`: procedencia de la topografía no confirmada. No se usó topo ni se hizo clasificación AIR/ROCK. |
| `P4` — asignación categórica | Gate aprobado y ejecutado; salida preliminar generada. P4 sigue `PARTIAL` por el criterio de punto medio, conflictos/sin soporte y ausencia de validación minera/geológica. |
| `P5_VALIDATION` | `PARTIAL`: pruebas computacionales ejecutadas, pero no validación geológica, minera ni topográfica completa. |
| `P6_VISUALIZER` | Gate aprobado y ejecutado; pruebas, HTML e inspección visual completados. P6 permanece `PARTIAL`, pues la figura es diagnóstica, no una validación. |

- **Evidencia computacional:** seis pruebas focalizadas de block model y 23 pruebas de suite reportadas hasta P4; en P6, `python -m pytest tests\test_m01b_visualizer.py -q` → 5 aprobadas y `python -m pytest -q` → 28 aprobadas. `git diff --check` terminó sin problemas al cierre P6. El CSV contiene 11.550 filas/índices únicos, 102 categorías asignadas, 11.448 `UNKNOWN/UNASSIGNED` y 5.830 conteos de soporte assay. El HTML autónomo mide 20.253.766 bytes, incluye 11.550 bloques (49 trazas: 4 códigos, 1 grupo `UNKNOWN/UNASSIGNED` y 44 trayectorias) y declara `topography_used=false`, `validation_claim=false`. Las pruebas M01 previas en memoria procesaron 44 sondajes/313 estaciones, 5.803 assays, 120 intervalos litológicos y 459 densidades; XYZ finitos, coincidencia MD=0 con 44/44 collars; validador con cuatro `INFO` y cero `ERROR`/`WARNING`.
- **Conclusión técnica:** se construyó un modelo categórico preliminar sobre la malla candidata aprobada, con códigos literales asignados solo por concordancia de los intervalos litológicos que aportan soporte a la celda. Composites solo cuentan soporte assay. Se produjo una vista 3D interactiva con categorías asignadas, UNKNOWN filtrable, trayectorias, leyenda y hover de auditoría. Estos artefactos y sus pruebas acreditan ejecución computacional en el árbol de trabajo; no establecen interpretación o validez geológica/minera, reproducibilidad desde HEAD limpio ni clasificación topográfica.
- **Principal limitación de confiabilidad:** cada intervalo se representa por su punto medio para asignarlo a una celda; no se calcula cuánto volumen de la celda ocupa cada litología. Por ello, una asignación unánime en los puntos observados no valida continuidad ni dominio geológico del volumen completo. Además, 11.448/11.550 celdas permanecen `UNKNOWN/UNASSIGNED`; la topografía y el significado oficial de los códigos no están confirmados.
- **Estados:** B00, B01 y B07 `VERIFIED`; B02, B03, B05, B06, B08 y B10 `PARTIAL`; B04 `MISSING` respecto de visualización M01; B09 `BLOCKED`. P2 decisión conceptual aprobada con geometría provisional; P3 bloqueada; P4/P5/P6 `PARTIAL`. Recuperación `RECOVERY_BLOCKED`, no `BASE_VERIFIED`.
- **Pendientes:** confirmar con el docente la procedencia oficial de `Topopl.csv`; solo después revisar cobertura, unidades y alineación y decidir si se abre P3. También falta completar la validación geológica/minera, confirmar el significado de los códigos, evaluar el criterio de punto medio y cerrar la reproducibilidad desde HEAD limpio. La geometría P2 aún tiene origen, extensión, borde y fundamento vertical provisionales.
- **Git final:** rama `feature/m01b-block-model`, HEAD `9771efbecf4fb9fb1763d2cb0e99fa3280137b4a`. En el último `git status --short`: modificados `src/mod1/desurvey.py`, `src/mod1/positioning.py`, `src/mod1/validator.py`; no rastreados `data/processed/m01b/block_model_preliminary.csv`, `docs/exam/`, `outputs/figures/m01b_block_model_preliminary.html`, `src/mod1/block_model.py`, `src/mod1/block_model_visualizer.py`, `tests/test_m01_spatial.py`, `tests/test_m01b_block_model.py` y `tests/test_m01b_visualizer.py`. No hubo commit ni push; stash no aplicado ni eliminado. No se modificaron datos fuente ni gobernanza.
- **Siguiente paso pendiente:** resolver B09 obteniendo confirmación docente verificable de procedencia. Hasta entonces, no usar la topografía ni ejecutar clasificación topográfica; las tareas posteriores de validación minera/geológica permanecen pendientes. Este cierre documental y la visualización P6 no cierran técnicamente la pauta.

## Estado vigente al cierre

El estado vigente es rama `feature/m01b-block-model`, HEAD actual/documental
`66e1ae3`, commit documental anterior `207ba75` y commit técnico del modelo
final `a70b546`. El árbol estaba limpio tras `66e1ae3` antes de esta revisión,
cuyos cambios siguen sin commit. La suite completa tuvo `41 passed`;
`git diff --check` quedó limpio antes del commit técnico final y antes del cierre
documental anterior.

P2 permanece como decisión conceptual aprobada para el alcance preliminar;
reproducibilidad y cobertura están verificadas, pero no la optimización del
tamaño ni del origen. La cobertura topográfica indicada arriba aplica a los
centros XY del grid, no a toda la nube raw.

| Estado actual | Resultado |
|---|---|
| B00–B10 | Estados diferenciados según la tabla B00–B10 anterior; no se afirma que todos estén completamente verificados. |
| P1 | `PARTIAL`: códigos literales y observaciones documentados, pero sin diccionario oficial ni interpretación de dominios. |
| P2 | Decisión conceptual para el modelo preliminar; reproducibilidad/cobertura comprobadas, optimización y validación como diseño definitivo no demostradas. |
| P3 | `VERIFIED` para integración e interpolación TIN en 210/210 centros XY y clasificación computacional de 11.550 bloques; no valida CRS/datum ni cobertura de toda la nube. |
| P4 | `VERIFIED` para intersección, contabilización, asignación conservadora y trazabilidad de los intervalos observados; no demuestra continuidad entre sondajes ni certificación profesional. |
| P5 | `VERIFIED` para pruebas/regeneración y controles observacionales descritos; no es validación operacional ni profesional externa. |
| P6 | `VERIFIED` como visualización diagnóstica/interactiva; no es modelo de recursos, reservas ni operacional. |
| Topografía | `Topopl.csv`, 218.112 puntos `PID/X/Y/Z`; 210/210 centros XY con elevación TIN finita; 11.550 bloques clasificados. No significa cobertura de toda la nube raw: 69.266 puntos dentro del rectángulo XY y 148.846 fuera. |
| Geología | 120 intervalos posicionados; 76 contactos; 11,574.785091049 m dentro y 0 m fuera; 978 bloques con intersección positiva, 68 conflictos y 10.504 sin soporte. Conflictos/sin soporte: `UNKNOWN/UNASSIGNED`; los bloques sin soporte reflejan la regla conservadora y no son por sí solos un error del algoritmo. |
| BASE | `BASE_ACCEPTED_WITH_LIMITATIONS`: base suficiente para continuar el ejercicio académico; no implica metadatos o validación completos. |
| D0 | Estado diagnóstico registrado en el resumen vigente; la pauta/documentación no asigna un estado final independiente a D0. |
| Gate final | Cierre técnico/documental para el alcance académico T2, reproducible con 41 pruebas aprobadas y limitaciones de fuente explícitas; no certificación profesional ni operacional. |
| Límites | CRS/EPSG y datum vertical: NO DOCUMENTADOS EN LAS FUENTES DISPONIBLES; códigos sin significado oficial; Topopl no incluido en el manifiesto original. |
