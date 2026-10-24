# IMP-004 — Validación de intervalos litológicos observados en bloques

## Estado final vigente

- **HEAD técnico final:** `a70b546` en `feature/m01b-block-model`.
- **Suite técnica final:** `41 passed`.
- **P4, P5 y P6:** `VERIFIED` dentro del alcance aprobado y descrito en este
  documento.
- **Alcance:** coherencia y trazabilidad respecto de intervalos litológicos y
  contactos observados en el repositorio; no es certificación profesional
  externa ni validación operacional.
- La validación contabilizó 120 intervalos posicionados y 76 contactos;
  `11,574.785091049 m` dentro de la malla y `0 m` fuera. Se asignaron 978 bloques
  con intersección positiva; 68 conflictos y 10.504 bloques sin soporte
  permanecen `UNKNOWN/UNASSIGNED`. Los códigos vacíos también quedan sin
  asignación. No se usa voto mayoritario ni se extrapolan códigos a bloques
  vecinos; cada bloque asignado conserva IDs y soporte de intervalos fuente.
- `lith_code`/`lith_status` son independientes de `topo_status`. La tabla
  cruzada litología-topografía fue revisada; los 7 casos `OVB` con
  `topo_status=AIR` se conservan como observaciones cautelares, sin recodificar.
  `AIR` litológico no equivale a `topo_status=AIR`.
- P6 corresponde a `outputs/figures/m01b_block_model_geology_topography.html`:
  visualización integrada con superficie topográfica, bloques, sondajes,
  intervalos litológicos, 76 contactos, `UNKNOWN/UNASSIGNED`, controles
  separados de litología/topografía, sección X-Z y hover con datos de soporte
  para auditoría.
- Pruebas de la etapa geológica: 13 focalizadas aprobadas; suite técnica final:
  41 aprobadas. `git diff --check` quedó limpio antes del commit técnico final.
- Se mantienen las limitaciones de IMP-003: CRS/EPSG y datum vertical no
  documentados formalmente; no está documentado el significado oficial de
  `OVB`, `BRX`, `POR`, `VOL` o `AIR`.
- Fuera de alcance: estimación de leyes, recursos/reservas, pit y
  secuenciamiento.

## 1. Identificación

- **Implementation ID:** IMP-004
- **Module:** Intersección 3D de litología observada, auditoría de contactos e integración diagnóstica con topografía
- **Date:** 2026-10-24
- **Group:** G05
- **Status:** VALIDATED
- **Related gates:** P4, P5 y cierre visual P6; B09 y P3 permanecen `VERIFIED`

## 2. Alcance

La validación se limita a la coherencia y trazabilidad entre los intervalos
litológicos fuente, sus contactos posicionados y los bloques que intersectan.
No representa interpretación geológica fuera de los códigos observados,
validación profesional externa, validación de campo ni validación operacional.
Los códigos conservan su escritura literal; el release no documenta su
significado.

## 3. Inputs y outputs

| Variable / resultado | Significado | Unidad | Origen / destino |
|---|---|---|---|
| Intervalos litológicos, collars y surveys | Observaciones fuente y geometría de sondajes | MD y XYZ en m | `data/raw/` — solo lectura |
| Composites posicionados | Conteo independiente de soporte assay | MD y XYZ en m | `data/processed/m01b/composites.csv` |
| Bloques con soporte geológico | Código, estado, longitud MD soportada e IDs fuente | m | `data/processed/m01b/block_model_preliminary_geology.csv` |
| Bloques integrados | Soporte geológico y `topo_z_m`/`topo_status` separados | m | `data/processed/m01b/block_model_preliminary_geology_topography.csv` |
| Figura diagnóstica | Superficie, bloques, sondajes, intervalos, contactos y sección X-Z | XYZ en m | `outputs/figures/m01b_block_model_geology_topography.html` |

## 4. Lógica de intersección y clasificación

1. `position_intervals` interpola los límites de cada intervalo y conserva los
   tramos XYZ que atraviesa entre estaciones consecutivas de la trayectoria
   desurveyada. Se representa cada tramo entre estaciones como una línea recta;
   no se recalcula la curva de mínima curvatura ni se extrapola fuera de la
   trayectoria.
2. Cada tramo se divide en los parámetros donde cruza límites X/Y/Z de la malla.
   El punto medio de cada subtramo determina una sola celda mediante la
   convención semiabierta de índices. Así, un tramo coincidente con una cara
   interna se asigna de forma determinista a un lado y un contacto de longitud
   cero no crea soporte en ambos bloques.
3. La longitud downhole del subtramo se acumula en la celda intersectada o como
   longitud observada fuera de la malla. Cada intervalo registra
   `observed_length_m`, `inside_length_m` y `outside_length_m`; las celdas
   conservan IDs `hole_id:from_m-to_m`.
4. Un bloque es `ASSIGNED` solo si cuenta con intersección positiva, todos sus
   intervalos de soporte tienen código no vacío y existe un único código
   literal. Conflictos → `CODE_CONFLICT`; soporte con código vacío →
   `EMPTY_CODE`; ausencia de soporte → `NO_LITHOLOGY_SUPPORT`. Los tres casos
   quedan con `UNKNOWN/UNASSIGNED` y `lith_code` vacío, sin voto mayoritario ni
   extrapolación.
5. Los composites solo incrementan `assay_composite_support_count`. La
   interpolación topográfica añade `topo_z_m`/`topo_status` sin usar ni
   modificar `lith_code`; el código literal `AIR` no equivale al estado
   topográfico `AIR`.

## 5. Resultados observados

- Se procesaron **120 intervalos** en **11.550 bloques** y se identificaron
  **76 contactos contiguos con cambio de código**.
- Longitud downhole observada: **11,574.785091049 m**; dentro de la malla:
  **11,574.785091049 m**; fuera: **0 m**. El mayor desbalance absoluto por
  intervalo fue **2,27e-13 m**, por redondeo numérico.
- **978** bloques quedaron asignados (`BRX` 54, `OVB` 36, `POR` 463, `VOL` 425).
  Los otros **10.572** son `UNKNOWN/UNASSIGNED`: **10.504** sin soporte y **68**
  conflictos. Los 68 conflictos se conservaron sin asignar:
  `AIR|OVB` 2; `BRX|POR` 14; `OVB|POR` 14; `OVB|POR|VOL` 3; `OVB|VOL` 24;
  `POR|VOL` 11. Las dos celdas con soporte literal `AIR` también contienen
  `OVB`; no se generó una categoría `AIR` asignada.
- Las **978/978** asignaciones tienen longitud de soporte positiva, ID de
  intervalo y código incluido en los códigos de soporte. No se propagaron
  códigos a bloques vecinos. Toda la longitud observada quedó contabilizada
  dentro o fuera de la malla.
- Los **120 IDs de intervalo** aparecen en el soporte de al menos un bloque;
  en este dataset la longitud fuera de malla fue cero.

### Revisión cruzada litología / topografía

`topo_status` se mantuvo independiente y sus conteos coinciden con P3:
`AIR` 4.493; `PARTIAL` 204; `ROCK` 6.853.

| Código/estado litológico | AIR topo | PARTIAL topo | ROCK topo |
|---|---:|---:|---:|
| `BRX` | 0 | 0 | 54 |
| `OVB` | 7 | 20 | 9 |
| `POR` | 0 | 0 | 463 |
| `VOL` | 0 | 2 | 423 |
| `UNKNOWN/UNASSIGNED` | 4.486 | 182 | 5.904 |

Se revisaron y documentaron como combinaciones que requieren cautela los
**7 bloques `OVB`/topo `AIR`**, los **20 `OVB`/`PARTIAL`** y los **2
`VOL`/`PARTIAL`**. Sin una definición oficial para los códigos litológicos,
estos cruces no permiten declarar contradicción geológica ni recodificar el
modelo; se conservan como observaciones independientes para revisión posterior.
Los bloques desconocidos reflejan falta/conflicto de soporte, no una unidad
geológica interpretada.

## 6. Pruebas e inspección

- `python -m pytest tests\test_m01b_geological_validation.py tests\test_m01b_visualizer.py -q`
  → **13 passed**.
- `python -m pytest -q` → **41 passed**, 0 fallidas.
- `git diff --check` → sin problemas en la verificación de esta etapa. La
  verificación antes del commit técnico final se registra en **Estado final
  vigente**.
- Los casos focalizados cubren intersección de varios bloques, contabilización
  dentro/fuera, conflicto sin mayoría, código vacío, ausencia de propagación,
  cruce de esquina/contactos de medida cero, quiebres de trayectoria y
  persistencia de IDs/longitudes de soporte. La prueba de visualización verifica
  capas de intervalos y contactos y el panel de sección.
- Se abrió el HTML integrado con Chrome headless y se inspeccionó la captura
  local de **1800×1100 px**. Se observan la superficie TIN, bloques codificados,
  trayectorias, intervalos observados, leyenda de 76 contactos y la sección
  X-Z en `j=7` (`Y=8196600–8196650 m`). La figura conserva
  `validation_claim=false`; es diagnóstica, no una certificación.
- La figura HTML tiene **71 trazas** y mide **52.479.274 bytes**. Los dos CSV
  geológicos miden **1.658.226** y **1.924.416 bytes** respectivamente.

## 7. Archivos afectados durante la etapa IMP-004

```text
src/mod1/positioning.py
src/mod1/block_model.py
src/mod1/block_model_visualizer.py
tests/test_m01b_geological_validation.py
tests/test_m01b_visualizer.py
data/processed/m01b/block_model_preliminary_geology.csv
data/processed/m01b/block_model_preliminary_geology_topography.csv
outputs/figures/m01b_block_model_geology_topography.html
docs/implementation/IMP-004_m01b_geological_validation.md
docs/STATUS.md
```

Este registro de archivos y Git corresponde al estado al cierre de la etapa
IMP-004, previo al commit técnico final; no es el estado Git actual.

No se modificó ningún archivo de `data/raw/`; `git diff -- data/raw` no reporta
cambios en el árbol de trabajo. `Topopl.csv` conserva el estado staged previo al
gate, sin cambios de este trabajo. No se sobrescribieron el modelo preliminar ni
el derivado/HTML de topografía. No hubo commit ni push.

## 8. Estado final de gates

- **P4 — `VERIFIED`** para intersección computacional, contabilización de los
  intervalos, asignación conservadora, contactos posicionados y trazabilidad a
  observaciones. No significa interpretación geológica profesional ni
  continuidad validada entre sondajes.
- **P5 — `VERIFIED`** para las pruebas automatizadas, regeneración, controles de
  soporte y revisión documentada de la tabla litología/topografía. Los cruces
  que no pueden interpretarse por falta de diccionario permanecen explícitos y
  no se presentan como discrepancias resueltas.
- **P6 — `VERIFIED`** para el artefacto diagnóstico integrado, controles
  litológicos/topográficos y sección inspeccionada. No implica validación
  operacional ni externa.

Permanecen vigentes las limitaciones de IMP-003: CRS/EPSG y datum vertical no
documentados, superficie representada mediante elevación interpolada en el
centro XY del bloque y ausencia de interpretación oficial de códigos. No se
infiere fracción volumétrica por la clasificación topográfica.
