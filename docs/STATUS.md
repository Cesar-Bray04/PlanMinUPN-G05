# STATUS.md

Resumen operativo vigente del proyecto.

## Estado técnico final T2 M01B

- **Rama:** `feature/m01b-block-model`
- **HEAD actual/documental:** `66e1ae3`
- **Commit documental anterior:** `207ba75`
- **Commit técnico del modelo final:** `a70b546`
- **Estado base:** `BASE_ACCEPTED_WITH_LIMITATIONS` — suficiente para continuar
  el ejercicio académico M01B; no significa que todos los metadatos, fuentes
  adicionales o validaciones estén completos.
- **HEAD:** commit documental `66e1ae3`; el árbol se encontraba limpio después
  de ese commit y antes de la revisión documental actual, que no se ha
  commiteado.
- **Suite técnica final:** `41 passed`
- **`git diff --check`:** limpio antes del commit técnico
- **B00–B10:** estados diferenciados en la tabla; B01 es `PARTIAL` y B04 es
  `VERIFIED-HISTORICAL`.
- **P3–P6:** verificados únicamente dentro de los alcances computacionales/
  observacionales descritos abajo.
- **P1:** `PARTIAL`; se documentan códigos observados, sin diccionario oficial.
- **P2:** decisión conceptual para el modelo preliminar; no validado como diseño
  definitivo ni optimizado.

El detalle de decisiones, checkpoints históricos y evidencia está en
`docs/exam/T2_M01B_PLAN_G05.md` y `docs/exam/T2_M01B_EVIDENCE_G05.md`. Sus
estados vigentes prevalecen sobre los registros históricos.

## Modelo de bloques

- **Tamaño:** `50 × 50 × 10 m`
- **Forma:** `15 × 14 × 55`
- **Total:** `11.550` bloques
- **Origen usado:** `(242225, 8196250, 2990) m` (origen local provisional)

Para el modelo categórico preliminar del alcance T2 se adopta una malla
reproducible de 50 × 50 × 10 m, con forma 15 × 14 × 55 (11,550 bloques) y
origen local provisional (242225, 8196250, 2990) m. La dimensión horizontal de
50 m se eligió como escala conceptual comparable con las medianas observadas de
distancia al collar vecino más cercano (55.90 m) y de espaciamiento por sección
(54.90 m); la cobertura es heterogénea y este análisis no constituye variografía
ni demuestra un tamaño óptimo. La dimensión vertical de 10 m se conserva como
discretización adoptada, pero no está justificada formalmente por el
espaciamiento vertical observado. El origen se obtuvo por redondeo inferior
respecto del cero numérico local con incrementos de 25/25/10 m para la candidata
conceptual anterior y se retuvo al pasar a 50/50/10 m; no es una referencia
oficial. La mediana de las medianas por sección es 58.77 m.

P2 es una decisión conceptual aprobada para el alcance preliminar;
reproducibilidad y cobertura verificadas, optimización del tamaño/origen no
demostrada. Los 50 m horizontales son comparables con las medianas observadas
de 55.90 m entre collars vecinos, 54.90 m por sección y 58.77 m de las medianas
por sección; la cobertura es heterogénea. Esto no es variografía ni demuestra
un tamaño óptimo. Los 10 m verticales son una discretización adoptada sin
justificación vertical formal suficiente. El origen se obtuvo inicialmente por
redondeo inferior respecto del cero numérico local en incrementos de 25/25/10 m
y se retuvo al adoptar 50/50/10 m; es reproducible, local y provisional, no
oficial ni un alineamiento aprobado para el grid final.

## Topografía

Fuente `data/raw/topography/Topopl.csv`, con 218.112 puntos y campos
`PID`, `X`, `Y`, `Z`. Los 210 centros XY necesarios para clasificar el grid
obtuvieron elevación TIN finita y la intersección vertical en Z se comprobó.
No significa que toda la nube raw esté contenida en el grid: 69.266 puntos
están dentro de su rectángulo XY y 148.846 fuera. Además, 44/44 collars y
313/313 estaciones de trayectoria están dentro del grid. `Topopl.csv` no figura en el
`release_manifest.json` original; la referencia histórica de compatibilidad
espacial indicada por el docente no acredita procedencia oficial.

| Clasificación | Bloques |
|---|---:|
| `ROCK` | 6.853 |
| `AIR` | 4.493 |
| `PARTIAL` | 204 |

La clasificación es computacional y no estima la fracción volumétrica de roca
de cada bloque.

## Geología observada

- 120 intervalos litológicos posicionados y 76 contactos.
- `11,574.785091049 m` contabilizados dentro de la malla y `0 m` fuera.
- 978 bloques con intersección positiva y asignación respaldada por soporte.
- 68 conflictos y 10.504 bloques sin soporte.
- Conflictos y bloques sin soporte permanecen `UNKNOWN/UNASSIGNED`.
- La validación comprueba coherencia y trazabilidad contra intervalos/contactos
  observados del repositorio; no es certificación profesional externa, no
  demuestra continuidad entre sondajes ni es validación operacional.

## Compositing

- Fuente: 5.803 assays; producto: 5.830 composites.
- La salida se regeneró byte por byte idéntica a
  `data/processed/m01b/composites.csv`.
- **SHA-256:** `7a00a557bf604eba8ac45d158ba2a01a6d03caa8fccd14b020c47df478b4193c`

## Visualización final P6

`outputs/figures/m01b_block_model_geology_topography.html` es la visualización
3D integrada con superficie topográfica, bloques, sondajes, intervalos
litológicos, contactos, estados `UNKNOWN/UNASSIGNED`, controles de
litología/topografía y sección X-Z. Es una vista diagnóstica y no una
certificación geológica, un modelo de recursos/reservas ni un modelo
operacional.

## Estado vigente B00–B10

| ID | Estado | Alcance y cautela |
|---|---|---|
| B00 | `VERIFIED` | Rama `feature/m01b-block-model`; HEAD `66e1ae3`, commit documental anterior `207ba75` y commit técnico `a70b546` identificados. |
| B01 | `PARTIAL` | Manifiesto e integridad del release original verificados. `Topopl.csv` está técnicamente integrado, pero no figura en el manifiesto; procedencia oficial, CRS/EPSG y datum vertical no están acreditados/documentados. |
| B02 | `VERIFIED` | Validador ejecutado; 4 hallazgos `INFO`, ningún `ERROR` o `WARNING`; suite final aprobada. |
| B03 | `VERIFIED` | Trayectorias y posiciones XYZ disponibles para 44 sondajes y 120 intervalos litológicos. |
| B04 | `VERIFIED-HISTORICAL` | Capacidad demostrada en evidencia histórica de `stash@{0}`/`stash@{1}` y baseline; no está activa en HEAD. La visualización vigente está cubierta por P6. |
| B05 | `VERIFIED` | Decisiones/resultados reconciliados con el estado técnico final en IMP-003/IMP-004 y documentos T2. |
| B06 | `VERIFIED` | Auditoría observacional: 5.803 assays, 120 intervalos, 44 sondajes, sin gaps/overlaps ni discrepancias de longitud; 76 contactos, 48 assays que cruzan contactos y cobertura assay completa desde MD 0 hasta profundidad final. No implica interpretación geológica externa. |
| B07 | `VERIFIED` | Regla de compositado documentada, incluida ponderación por longitud y conservación de residuales. |
| B08 | `VERIFIED` | 5.830 composites reproducibles byte por byte; hash indicado arriba y trazabilidad a los assays fuente. |
| B09 | `VERIFIED` | Dentro del alcance computacional implementado: `Topopl.csv` está integrado; los 210/210 centros XY tienen elevación TIN finita y los 11.550 bloques reciben clasificación topográfica. No valida CRS/datum ni cubre toda la nube; 69.266 puntos raw están dentro del rectángulo XY y 148.846 fuera. |
| B10 | `VERIFIED` | Suite final con 41 aprobaciones, diff-check limpio antes del commit técnico/documental y artefactos trazables. |

## Limitaciones vigentes

- CRS/EPSG de `Topopl.csv`: NO DOCUMENTADO EN LAS FUENTES DISPONIBLES. No inferir
  UTM, WGS84, PSAD56, zona, EPSG ni transformación. La referencia a coordenadas
  cartesianas locales en el release no asigna formalmente CRS a Topopl.
- Datum o referencia vertical de `Topopl.csv.Z`: NO DOCUMENTADO EN LAS FUENTES
  DISPONIBLES; `collar.csv.z` no es evidencia del datum topográfico.
- Los códigos observados `OVB`, `BRX`, `POR`, `VOL` y `AIR` se describen
  únicamente como `Observed lithology code`; no se expanden ni interpretan.
  `lith_code=AIR` es distinto de `topo_status=AIR`.
- La validación geológica se limita a coherencia con observaciones/contactos
  del repositorio; no es certificación profesional externa, no demuestra
  continuidad entre sondajes y no es validación operacional. Los 10.504 bloques
  sin soporte resultan de la regla conservadora y no indican por sí solos un
  error del algoritmo.
- El alcance no incluye estimación de leyes, recursos/reservas, pit ni
  secuenciamiento.

## Cierre académico

El M01B queda técnicamente implementado y reproducible para el alcance académico
T2, con 41 pruebas aprobadas. La integración de topografía, litología observada
y visualización 3D diagnóstica está operativa. P2 es una decisión conceptual
preliminar, no un diseño definitivo; P3–P6 se consideran verificados solo dentro
de los alcances computacionales/observacionales descritos. Persisten las
limitaciones de procedencia/metadatos espaciales de Topopl y de significado
oficial de los códigos.
