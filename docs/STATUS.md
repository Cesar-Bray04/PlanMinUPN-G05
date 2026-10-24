# STATUS.md

Resumen operativo vigente del proyecto.

## Estado técnico final T2 M01B

- **Rama:** `feature/m01b-block-model`
- **HEAD técnico final:** `a70b546`
- **Estado base:** `BASE_VERIFIED`
- **Árbol de trabajo después del commit técnico final:** limpio
- **Suite técnica final:** `41 passed`
- **`git diff --check`:** limpio antes del commit técnico
- **B00–B10:** `VERIFIED`, con los alcances y cautelas resumidos abajo
- **P3, P4, P5 y P6:** `VERIFIED` dentro del alcance aprobado y documentado

El detalle de decisiones, checkpoints históricos y evidencia está en
`docs/exam/T2_M01B_PLAN_G05.md` y `docs/exam/T2_M01B_EVIDENCE_G05.md`. Sus
estados vigentes prevalecen sobre los registros históricos.

## Modelo de bloques

- **Tamaño:** `50 × 50 × 10 m`
- **Forma:** `15 × 14 × 55`
- **Total:** `11.550` bloques
- **Origen usado:** `(242225, 8196250, 2990) m` (origen local provisional)

## Topografía

Fuente `data/raw/topography/Topopl.csv`, con 218.112 puntos y campos
`PID`, `X`, `Y`, `Z`. La cobertura del grid se comprobó en X/Y y la
intersección vertical en Z.

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
  observados del repositorio; no es certificación profesional externa.

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
certificación operacional.

## Estado vigente B00–B10

| ID | Estado | Alcance y cautela |
|---|---|---|
| B00 | `VERIFIED` | Rama, HEAD final y árbol limpio tras el commit técnico. |
| B01 | `VERIFIED` | Fuentes, integridad, campos y unidades comprobados; topografía detallada en B09. |
| B02 | `VERIFIED` | Validador ejecutado; 4 hallazgos `INFO`, ningún `ERROR` o `WARNING`; suite final aprobada. |
| B03 | `VERIFIED` | Trayectorias y posiciones XYZ disponibles para 44 sondajes y 120 intervalos litológicos. |
| B04 | `VERIFIED` | Capacidad histórica acreditada en `stash@{0}`/`stash@{1}` y baseline. El visualizador heredado no está activo en HEAD; P6 es la vista vigente. |
| B05 | `VERIFIED` | Decisiones/resultados reconciliados con el estado técnico final en IMP-003/IMP-004 y documentos T2. |
| B06 | `VERIFIED` | Auditoría observacional: 5.803 assays, 120 intervalos, 44 sondajes, sin gaps/overlaps ni discrepancias de longitud; 76 contactos, 48 assays que cruzan contactos y cobertura assay completa desde MD 0 hasta profundidad final. No implica interpretación geológica externa. |
| B07 | `VERIFIED` | Regla de compositado documentada, incluida ponderación por longitud y conservación de residuales. |
| B08 | `VERIFIED` | 5.830 composites reproducibles byte por byte; hash indicado arriba y trazabilidad a los assays fuente. |
| B09 | `VERIFIED` | Topografía disponible; 218.112 puntos `PID/X/Y/Z`, cobertura del grid en X/Y e intersección en Z. |
| B10 | `VERIFIED` | Suite final con 41 aprobaciones, diff-check limpio antes del commit y artefactos trazables. |

## Limitaciones vigentes

- CRS/EPSG no documentado formalmente.
- Datum vertical no documentado.
- No está documentado el significado oficial de `OVB`, `BRX`, `POR`, `VOL`
  o `AIR`; los códigos se conservan literalmente.
- La validación geológica se limita a coherencia con observaciones/contactos
  del repositorio; no es certificación profesional externa.
- El alcance no incluye estimación de leyes, recursos/reservas, pit ni
  secuenciamiento.
