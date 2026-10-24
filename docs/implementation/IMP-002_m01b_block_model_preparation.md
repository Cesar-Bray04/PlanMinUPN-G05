## ESTADO FINAL / CONTINUIDAD

- **Estado técnico final:** HEAD `a70b546` en la rama `feature/m01b-block-model`.
- **Suite técnica final:** `41 passed`.
- Este documento conserva el baseline y la implementación histórica del
  compositado M01B. Sus estados y resultados describen las etapas registradas
  en su momento; no sustituyen el estado final.
- La topografía, su clasificación e integración se documentan en
  `IMP-003_m01b_topography_integration.md`.
- La validación de intervalos/contactos por intersección 3D y la visualización
  3D integrada se documentan en `IMP-004_m01b_geological_validation.md`.
- No se infieren CRS/EPSG, datum vertical ni significado oficial de códigos
  litológicos: no están documentados formalmente.

## HISTÓRICO — Baseline previo a M01B

**Evidencia:**  
`outputs/logs/baseline_M01B.txt`

**Fecha:**  
2026-10-16 12:19:17

**Branch:**  
`feature/m01b-block-model`

**Commit:**  
`3a11c6edf57eb31f06350718ead77c96d3b29b00`

**Python:**  
Python 3.11.9

**Estado Git previo a M01B:**  
Branch `feature/m01b-block-model`; aparecen como modificados `docs/implementation/IMP-001_desurvey_architecture.md`, `src/mod1/desurvey.py`, `src/mod1/positioning.py`, `src/mod1/validator.py`, `src/mod1/visualizer.py` y `tests/test_loader.py`. Aparecen como no rastreados `data/raw/topography/`, `docs/implementation/M01B.md`, `outputs/figures/m01_drillholes_3d_DS05_EXP03.html`, `outputs/logs/`, `tests/test_desurvey.py`, `tests/test_positioning.py`, `tests/test_validator.py` y `tests/test_visualizer.py`.

**Resultado de pruebas:**  
pytest reporta 62 passed y 10 subtests passed en 1.17 s. Fallos: NO REGISTRADO EN BASELINE. Warnings: NO REGISTRADO EN BASELINE.

**Exit code:**  
0

**Estado del baseline:**  
WARNING

**Interpretación:**
pytest terminó con exit code 0 y el resumen reporta pruebas pasadas. Se clasifica como WARNING porque el git status registrado muestra archivos modificados y no rastreados al inicio de M01B. El log no registra explícitamente el conteo de fallos ni warnings de pytest.

## HISTÓRICO — Auditoría de inputs M01B

Auditoría física de `data/raw/`, `data/processed/`, `outputs/` y `src/`.
Los CSV conservan sus datos fuente sin modificación. Los tipos declarados
provienen de `data/raw/data_dictionary.csv`; los campos numéricos observados
en los CSV se leen inicialmente como texto.

| SOURCE | PATH | ROWS | KEY FIELDS / TYPES | UNITS | STATUS | POSITIONING STATUS | ROLE IN M01B | OBSERVATIONS |
|---|---|---:|---|---|---|---|---|---|
| assay — RAW SOURCE | `data/raw/assay.csv` | 5,803 | `sample_id` string; `hole_id` string; `dataset_id`, `project_id`, `campaign_id` string; `from_m`, `to_m`, `length_m`, `cu_pct`, `mo_pct`, `au_gt` float | Intervalos m; `cu_pct` y `mo_pct` %; `au_gt` g/t | AVAILABLE | PARTIALLY POSITIONED | Leyes observadas de intervalo; posible input para preparación posterior | 44 sondajes; 0 nulos; 0 `sample_id` duplicados; 0 intervalos con `from_m >= to_m`. Rangos: from 0–454 m, to 2–455.037201042 m, longitud 0.253548236–2 m, Cu 0.010139053–1.066962195 %, Mo 0–0 %, Au 0–0 %. Las posiciones están representadas en la visualización M01, pero no hay tabla XYZ persistida. No se selecciona longitud de composite. |
| lithology — RAW SOURCE | `data/raw/lithology.csv` | 120 | `hole_id`, `dataset_id`, `project_id`, `campaign_id`, `lith_code` string; `from_m`, `to_m`, `length_m` float | Intervalos m | AVAILABLE | PARTIALLY POSITIONED | Observación geológica para evaluar posteriormente una posible codificación de dominios | 44 sondajes; 0 nulos; 0 claves de intervalo duplicadas (`hole_id/from_m/to_m`); 0 intervalos con `from_m >= to_m`. Longitud 1–446.037201042 m. Códigos: OVB 46, POR 35, VOL 27, BRX 10, AIR 2. IMP-001 registra 120 filas procesadas con XYZ, pero no existe archivo tabular posicionado. Los significados de código no están documentados. |
| density — RAW SOURCE | `data/raw/density.csv` | 459 | `density_sample_id`, `hole_id`, `dataset_id`, `project_id`, `campaign_id` string; `from_m`, `to_m`, `length_m`, `density_t_m3` float | Intervalos m; densidad t/m³ | AVAILABLE | PARTIALLY POSITIONED | Fuente observada de densidad para análisis posterior | 44 sondajes; 0 nulos; 0 `density_sample_id` duplicados; 0 intervalos con `from_m >= to_m`. Intervalos de 1 m; densidad 2.148175384–2.768293461 t/m³. IMP-001 registra 459 filas procesadas con XYZ, pero no existe archivo tabular posicionado. La evidencia T1 registra 415 gaps de intervalos; no se define asignación ni densidad por defecto. |
| alteration — RAW SOURCE | `data/raw/alteration.csv` | 0 | `hole_id`, `dataset_id`, `project_id`, `campaign_id`, `alteration_code`, `alteration_intensity` string; `from_m`, `to_m`, `length_m` float | Intervalos m; código e intensidad sin unidad | EMPTY | NOT POSITIONED | Fuente opcional; no aporta observaciones | INFO — valid empty source. El archivo existe y conserva su estructura de encabezado, pero no contiene registros. No se generan ni inventan observaciones. |
| collar — RAW SOURCE | `data/raw/collar.csv` | 44 | `hole_id`, `dataset_id`, `project_id`, `campaign_id` string; `x`, `y`, `z`, `azimuth_deg`, `dip_deg`, `final_depth_m` float | Coordenadas y profundidad m; orientaciones degree | AVAILABLE | POSITIONED como inicio de las trayectorias de M01 | Referencia espacial y profundidad final de sondajes | 44 `hole_id` únicos; 0 nulos; 0 `hole_id` duplicados; X 242228.128433536–242971.871566464 m, Y 8196266.798008056–8196913.201991944 m, Z 3194–3532 m; profundidad 210–455.037201042 m. |
| survey — RAW SOURCE | `data/raw/survey.csv` | 313 | `hole_id`, `dataset_id`, `project_id`, `campaign_id` string; `depth_m`, `azimuth_deg`, `dip_deg` float | Profundidad m; azimuth/dip degree | AVAILABLE | POSITIONED como estaciones de trayectoria calculada por M01 | Control direccional para desurvey | 44 sondajes; 0 nulos; 0 duplicados `hole_id/depth_m`; depth 0–455.037201042 m, azimuth 18.434948823–347.833654178°, dip -84–-50°. |
| topography — RAW SOURCE | `data/raw/topography/Topopl.csv` | 218,112 puntos | `PID` entero observado; `X`, `Y`, `Z` numéricos | X/Y/Z m | AVAILABLE | POSITIONED; puntos ya tienen X/Y/Z | Referencia topográfica para considerar en preparación M01B | 0 nulos; 0 PID duplicados; 0 filas XYZ duplicadas. X 242090.504105–243287.725586 m; Y 8195892.194946–8197095.651855 m; Z 3120.858516–3596 m. El CRS/EPSG formal no está documentado. La compatibilidad espacial general fue indicada como validada por el docente; no se infiere una proyección ni transformación. |
| Trayectorias M01 — DERIVED FROM M01 | `outputs/figures/m01_drillholes_3d_DS05_EXP03.html` | HTML; no es tabla de registros | Visualización incluye collars, líneas de trayectoria y markers de assay | XYZ m; MD m | AVAILABLE | POSITIONED en la figura | Inspección visual; reutilizable como referencia visual, no como tabla estructurada | Archivo generado presente. IMP-001 registra 44 sondajes y 313 puntos de trayectoria procesados. No se encontró CSV de trayectorias en `data/processed/`. |
| Assays posicionados M01 — DERIVED FROM M01 | `outputs/figures/m01_drillholes_3d_DS05_EXP03.html`; sin tabla en `data/processed/` | 5,803 assays según registro de procesamiento de IMP-001; sin tabla persistida | Los campos previstos por positioning son los originales más `mid_m`, `x_from`, `y_from`, `z_from`, `x_mid`, `y_mid`, `z_mid`, `x_to`, `y_to`, `z_to` | MD y coordenadas m; leyes según diccionario | MISSING como tabla estructurada | PARTIALLY POSITIONED | Visualización espacial e inspección de assays | IMP-001 documenta `ASSAY_XYZ: 5803`; la figura contiene la capa de assays. No hay output tabular de coordenadas reutilizable en `data/processed/`. |
| Lithology posicionada M01 — DERIVED FROM M01 | No existe archivo derivado identificado; cálculo previsto por `src/mod1/positioning.py` | 120 según registro de procesamiento de IMP-001; sin tabla persistida | Campos originales más coordenadas from/mid/to previstos por el contrato de positioning | MD y coordenadas m | MISSING como archivo de salida | PARTIALLY POSITIONED según evidencia de procesamiento; no disponible como tabla | Podría apoyar evaluación espacial de litología tras recuperar/exportar el resultado | IMP-001 registra `LITHOLOGY_XYZ: 120`; no se encontró tabla y la figura disponible no muestra una capa de litología. |
| Density posicionada M01 — DERIVED FROM M01 | No existe archivo derivado identificado; cálculo previsto por `src/mod1/positioning.py` | 459 según registro de procesamiento de IMP-001; sin tabla persistida | Campos originales más coordenadas from/mid/to previstos por el contrato de positioning | MD y coordenadas m; densidad t/m³ | MISSING como archivo de salida | PARTIALLY POSITIONED según evidencia de procesamiento; no disponible como tabla | Requiere output estructurado antes de reutilizar espacialmente las muestras | IMP-001 registra `DENSITY_XYZ: 459`; no se encontró tabla de densidad posicionada. |
| Resumen de auditoría M01 — DERIVED FROM M01 | `outputs/tables/T1_audit_summary_DS05_EXP03.xlsx` | Workbook de 12 hojas; no es una tabla de intervalos posicionados | Hojas de metadata, files, schema, counts, rangos, relaciones, validación, intervalos, survey, missing data y fuente T1 | Según cada campo | AVAILABLE | NOT APPLICABLE | Evidencia reutilizable para inventario y auditoría de calidad | Archivo presente. No reemplaza los datos fuente ni proporciona coordenadas XYZ por intervalo. |

### Disponibilidad y cobertura

- **AVAILABLE NOW:** assay (5,803 filas), lithology (120), density (459),
  collar (44), survey (313), topografía (218,112 puntos), workbook de
  auditoría y visualización HTML de M01.
- **EMPTY:** alteration. INFO — valid empty source.
- **NEEDS PROCESSING:** obtener/exportar a un formato tabular los intervalos
  posicionados de assay, lithology y density para consumo reproducible; la
  exportación definida en `src/mod1/exporter.py` aún lanza
  `NotImplementedError`.
- **MISSING:** archivos tabulares posicionados y cualquier salida `composites`,
  domains, block grid, block model o estimación. `data/processed/` contiene
  únicamente `.gitkeep`.
- **UNKNOWN / LIMITATIONS:** EPSG/CRS formal; significado geológico de los
  códigos litológicos; regla de asignación/cobertura de densidad; relación
  formal entre los identificadores de campaña del manifest (`C01`–`C03`) y
  los observados en CSV (`CAMPAIGN_01`–`CAMPAIGN_03`). La validación de
  compatibilidad topográfica general indicada por el docente se registra sin
  asignar CRS.

### Implementación, generación y disponibilidad de outputs M01

- **IMPLEMENTED:** lectura, validación, desurvey por mínima curvatura,
  posicionamiento e integración de visualización están implementados en
  `src/mod1/`.
- **GENERATED:** está presente la figura HTML M01 y el workbook T1. IMP-001
  documenta procesamiento de 44 sondajes/313 puntos de trayectoria y
  posicionamiento de 5,803 assays, 120 intervalos de lithology y 459 muestras
  de density.
- **AVAILABLE FOR M01B:** la figura y el workbook están disponibles para
  consulta; collar, survey y datos raw están disponibles. Los resultados XYZ
  tabulares de intervalos no están disponibles como archivos reutilizables.

No se tomaron decisiones de compositado, dominios, geometría/tamaño de bloque,
estimación o asignación de densidad durante esta auditoría.

## HISTÓRICO — Análisis de assay previo al compositado

### Fuente y alcance

- **Archivo analizado:** `data/raw/assay.csv` (RAW SOURCE), release DS05/EXP03.
- **Registros / sondajes:** 5.803 intervalos y 44 `hole_id`.
- **Columnas:** `sample_id`, `hole_id`, `dataset_id`, `project_id`,
  `campaign_id`, `from_m`, `to_m`, `length_m`, `cu_pct`, `mo_pct`, `au_gt`.
- **Variables de ley:** Cu (`cu_pct`, %), Mo (`mo_pct`, %) y Au (`au_gt`,
  g/t), según `data/raw/data_dictionary.csv`.
- **Nulos/vacíos:** 0 en las 11 columnas.
- Los cuantiles se calcularon con interpolación lineal Type 7
  (`h=(n-1)p`). Las verificaciones geométricas de igualdad y continuidad usan
  tolerancia `1e-8 m`; los intervalos se ordenaron por `hole_id`, `from_m` y
  `to_m`. Gaps aquí significa discontinuidades internas; además se comprobó
  el inicio y final de cobertura contra collar.

### Calidad geométrica de intervalos

| Control | Resultado | Clasificación |
|---|---:|---|
| `from_m >= to_m` | 0 | INFO — sin errores detectados |
| `length_m <= 0` | 0 | INFO — sin errores detectados |
| `length_m` no coincide con `to_m - from_m` (tolerancia 1e-8 m) | 0 | INFO — sin errores detectados |
| IDs `sample_id` duplicados | 0 | INFO — sin duplicados |
| Claves de intervalo `hole_id/from_m/to_m` duplicadas | 0 | INFO — sin duplicados |
| Gaps internos entre intervalos assay contiguos | 0 | INFO — sin gaps |
| Overlaps internos entre intervalos assay contiguos | 0 | INFO — sin overlaps |
| Sondajes que empiezan en MD 0 | 44/44 | INFO |
| Sondajes cuyo assay finaliza en `final_depth_m` de collar | 44/44 | INFO |

La cobertura por sondaje es de 105–228 intervalos. Hay 30 intervalos menores
de 2 m; los 30 son el último intervalo del sondaje correspondiente. Esto no
se corrige ni se trata como error geométrico.

### Distribución de longitud

| Estadístico | Resultado (m) |
|---|---:|
| Count | 5.803 |
| Min | 0,253548236 |
| P10 | 2,000000000 |
| P25 | 2,000000000 |
| Median | 2,000000000 |
| Mean | 1,994620901 |
| P75 | 2,000000000 |
| P90 | 2,000000000 |
| Max | 2,000000000 |

Exactamente 5.773 registros (99,483 %) miden 2 m; los 30 restantes (0,517 %)
son terminales y menores de 2 m. La distribución de estos residuales es:
8 menores de 0,5 m; 8 entre 0,5 y <1 m; 8 entre 1 y <1,5 m; 5 entre 1,5 y
<1,9 m; y 1 entre 1,9 y <2 m. Dieciséis residuales (0,276 % del total)
miden menos de 1 m. No se selecciona longitud final de composite.

### Distribución de leyes y revisión de anomalías

| Variable | Unidad | Count | Missing | Min | P25 | Median | Mean | P75 | P90 | P95 | P99 | Max |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cu_pct` | % | 5.803 | 0 | 0,010139053 | 0,063010921 | 0,239996656 | 0,301229883 | 0,494937152 | 0,690965699 | 0,782483950 | 0,977118439 | 1,066962195 |
| `mo_pct` | % | 5.803 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `au_gt` | g/t | 5.803 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Mo y Au son cero en todos los registros: es un patrón constante observado,
no nulos; su significado y origen requieren confirmación. Para Cu, 59 muestras
(aprox. 1,02 %) superan el P99 calculado; el valor máximo es 1,066962195 %
(`SE-C02-008-A0098`). Una revisión exploratoria por cercas de Tukey (1,5 ×
IQR) no identifica valores Cu fuera de cercas: la cerca superior es
1,142826499 %. Estas reglas solo señalan observaciones para revisión; no
determinan validez, no se eliminaron ni capearon valores y no se calculó
cutoff ni se clasificó mineral/lastre.

### Relación preliminar con lithology

`data/raw/lithology.csv` contiene 120 intervalos para los mismos 44 sondajes.
La inspección registra 76 contactos contiguos entre códigos distintos, sin
gaps ni overlaps en la secuencia de lithology. Códigos observados: OVB (46),
POR (35), VOL (27), BRX (10) y AIR (2); sus significados geológicos siguen
sin documentarse.

Hay 48 intervalos assay (0,827 % de 5.803) que cruzan al menos un contacto de
lithology, incluyendo los intervalos de 8–10 m que atraviesan el contacto
repetido en 9 m. Un assay observado que cruza un límite no puede atribuirse a
un solo código litológico sin una regla aprobada. Por tanto, lithology aporta
límites observados relevantes para revisar en la etapa de compositado, pero
esta auditoría no crea dominios ni decide cómo subdividir o asignar esas
muestras.

### Alternativas de longitud para evaluación

Las alternativas siguientes son escenarios de discusión sustentados en la
distribución observada; ninguna es una decisión aprobada.

| Longitud candidata | Evidencia y ventaja | Desventaja / porcentaje afectado | Residuales esperados |
|---|---|---|---|
| 2,0 m | Coincide exactamente con 5.773/5.803 (99,483 %) muestras; preserva el soporte dominante con mínimo remuestreo. | 30/5.803 (0,517 %) son menores de 2 m y requieren una política explícita; 48 assays ya cruzan contactos litológicos. | Evaluar conservar el intervalo terminal variable o combinarlo con el anterior mediante ponderación por longitud si se aprueba. Cualquier combinación debe respetar la política geológica pendiente. |
| 1,0 m | Escenario de soporte más corto para comparación, aunque no es una moda observada. | Los 5.773 intervalos de 2 m (99,483 %) tendrían que dividirse para producir composites de 1 m; esto no añade observaciones y puede aparentar una precisión no contenida en la muestra original. Los 30 terminales (0,517 %) también requieren tratamiento. | Mantener residuales terminales variables o definir una regla aprobada para integrarlos; no duplicar leyes como si fueran nuevas mediciones. |

No se recomienda ni selecciona automáticamente una alternativa. La evidencia
favorece evaluar 2 m primero, pero la decisión requiere aprobación y una regla
para residuales, contactos geológicos y los 48 assays que ya cruzan contactos.

### Diagnósticos generados

Solo se generaron productos de diagnóstico; no se generaron composites ni se
modificó la fuente:

- `outputs/tables/assay_length_statistics_DS05_EXP03.csv`
- `outputs/tables/assay_length_frequency_DS05_EXP03.csv`
- `outputs/tables/assay_grade_statistics_DS05_EXP03.csv`
- `outputs/tables/assay_interval_diagnostics_DS05_EXP03.csv`
- `outputs/tables/assay_by_hole_coverage_DS05_EXP03.csv`
- `outputs/tables/assay_lithology_boundary_crossings_DS05_EXP03.csv`
- `outputs/tables/assay_potential_review_flags_DS05_EXP03.csv`
- `outputs/figures/assay_length_distribution_DS05_EXP03.svg`

### Incertidumbres y pendientes en la etapa previa al compositado

- Confirmar por qué `mo_pct` y `au_gt` son cero en todos los registros.
- Aprobar la longitud de composite y el tratamiento de los 30 residuales.
- Definir cómo preservar/revisar contactos litológicos cuando los intervalos
  assay o composites los atraviesen; aún no hay dominios aprobados.
- Los flags de Cu alto son descriptivos y no sustituyen revisión geológica,
  analítica ni de QA/QC. No se dispone aquí de reglas de capping ni de datos
  QA/QC documentados.
- En esta etapa previa a la implementación documentada a continuación, no se
  había implementado `compositing.py` ni generado composites.

## HISTÓRICO — Implementación del compositado

### DECISION-01 aplicada

Se aplicó la decisión aprobada para usar longitud objetivo de 2,0 m y Cu
(`cu_pct`, %) como variable primaria. El cálculo se limita a intervalos
independientes por `hole_id` y tramo continuo de `lith_code`. No se calcularon
Mo ni Au; no se asignaron dominios, densidad por defecto, block model ni
estimaciones.

### Arquitectura y flujo

- `src/mod1/loader.py::load_raw_data` carga assay, lithology, collar y survey
  sin modificar las fuentes.
- `src/mod1/validator.py::validate_data` se reutiliza para impedir el proceso
  si los inputs tienen findings de severidad ERROR.
- `src/mod1/desurvey.py::desurvey` produce la trayectoria del sondaje.
- `src/mod1/compositing.py::split_assays_at_lithology_contacts` intersecta
  cada assay con los intervalos litológicos observados, corta en los contactos
  y conserva `lith_code` y los IDs de muestra de origen. Exige cobertura
  litológica completa y no ambigua.
- `src/mod1/compositing.py::composite_assays` recorre los segmentos ordenados
  por sondaje, separa al cambiar `lith_code` y acumula hasta 2,0 m. Calcula
  Cu con ponderación por longitud. Un remanente final menor de 2,0 m se
  conserva con `residual_flag=true`; no se transfiere a través de un cambio
  litológico.
- `src/mod1/positioning.py::position_intervals` posiciona los composites
  finalizados; el punto medio espacial se escribe como `x_mid`, `y_mid`,
  `z_mid`, y el punto medio medido como `mid_m`.
- `build_m01b_composites` orquesta la carga, validación, desurvey, corte,
  compositado, posicionamiento y escritura. No se añadieron ramas a `main.py`.

Comparaciones geométricas usan tolerancia de `1e-8 m`. El archivo de salida
incluye además `source_sample_count` y `source_sample_ids` para trazar los
assays que contribuyeron a cada composite. Las coordenadas de salida son las
del sistema local fuente; no se asigna CRS.

### Archivos creados

- `src/mod1/compositing.py`
- `tests/test_m01b_compositing.py`
- `data/processed/m01b/composites.csv`

No se modificó `data/raw/`; no se implementaron otros módulos de M01B.

### Pruebas ejecutadas

El Python global no tenía pytest disponible; las pruebas se ejecutaron con
pytest 9.1.1 en `C:\CN\.venv\Scripts\python.exe`.

```text
python -m pytest tests/test_m01b_compositing.py -v
Resultado: PASS
Tests passed: 9
Tests failed: 0

python -m pytest
Resultado: PASS
Tests passed: 71
Tests failed: 0
```

Los nueve tests usan intervalos sintéticos pequeños y comprueban combinación
de assays de 1 m, ponderación de Cu, conservación de assay de 2 m, residual,
corte exacto en contacto, separación por lith_code, conservación de metros,
intervalos válidos y posicionamiento XYZ.

### Validación con datos reales

| Métrica | Resultado |
|---|---:|
| Assays originales | 5.803 |
| Metros originales | 11.574,785091049 m |
| Segmentos después de cortar contactos | 5.851 |
| Composites | 5.830 |
| Metros compositados | 11.574,785091049 m |
| Diferencia de metros (compositados - originales) | 0,000000000 m |
| Composites de 2,0 m | 5.750 |
| Residual composites | 80 |
| Rango de longitud de composite | 0,037201042–2,000000000 m |
| Media ponderada de Cu original | 0,300527693137281 % |
| Media ponderada de Cu compositado | 0,300527693137280 % |

Los 48 assays de la auditoría que cruzaban contactos producen 48 segmentos
adicionales; la suma de longitudes se mantiene. Los 80 residuales se
distribuyen así: 11 menores de 0,5 m; 9 entre 0,5 y <1 m; 55 entre 1 y
<1,5 m; y 5 entre 1,5 y <2 m. Conteo de composites por `lith_code`:
AIR 2, BRX 448, OVB 229, POR 3.019 y VOL 2.132. Los 80 residuales están
incluidos en esos conteos.

Se comprobó que todas las filas de salida tienen valores, `from_m < to_m`,
longitud positiva coherente con los límites, flag residual coherente con
longitud y `lith_code` cubierto por la litología fuente. La diferencia entre
medias ponderadas de Cu es aproximadamente `-4,44e-16 %`, atribuible a
redondeo numérico.

### Limitaciones y pendientes

- `composites.csv` es una salida derivada regenerable; la fuente raw permanece
  inmutable.
- Los códigos de lithology se preservan tal cual; sus significados geológicos
  no están documentados en el release.
- Los assays cortados en contactos heredan el mismo Cu observado en la muestra
  original en cada segmento. Esto implementa la regla aprobada de corte y
  ponderación, pero no representa un remuestreo analítico.
- La posición XYZ de cada composite proviene de la interpolación lineal
  existente sobre la trayectoria discretizada de M01.
- No se implementaron domains, block model ni estimación.
