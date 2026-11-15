# DATA.md

Inventario de datos raw y derivados usados en T2 M01B. Los nombres y códigos
observados se conservan literalmente; no se atribuyen significados que no estén
documentados en el repositorio.

## Fuentes raw

| Archivo | Registros | Campos | Unidades documentadas |
|---|---:|---|---|
| `data/raw/collar.csv` | 44 | `hole_id`, `dataset_id`, `project_id`, `campaign_id`, `x`, `y`, `z`, `azimuth_deg`, `dip_deg`, `final_depth_m` | `x/y/z/final_depth_m`: m; `azimuth_deg/dip_deg`: grados |
| `data/raw/survey.csv` | 313 | `hole_id`, `dataset_id`, `project_id`, `campaign_id`, `depth_m`, `azimuth_deg`, `dip_deg` | `depth_m`: m; `azimuth_deg/dip_deg`: grados |
| `data/raw/assay.csv` | 5.803 | `sample_id`, `hole_id`, `dataset_id`, `project_id`, `campaign_id`, `from_m`, `to_m`, `length_m`, `cu_pct`, `mo_pct`, `au_gt` | `from_m/to_m/length_m`: m; `cu_pct/mo_pct`: %; `au_gt`: g/t |
| `data/raw/lithology.csv` | 120 | `hole_id`, `dataset_id`, `project_id`, `campaign_id`, `from_m`, `to_m`, `length_m`, `lith_code` | `from_m/to_m/length_m`: m |
| `data/raw/density.csv` | 459 | `density_sample_id`, `hole_id`, `dataset_id`, `project_id`, `campaign_id`, `from_m`, `to_m`, `length_m`, `density_t_m3` | `from_m/to_m/length_m`: m; `density_t_m3`: t/m³ |
| `data/raw/alteration.csv` | 0 | Fuente oficial vacía; conserva su esquema, sin registros | No aplicable |
| `data/raw/topography/Topopl.csv` | 218.112 | `PID`, `X`, `Y`, `Z` | Coordenadas/elevación expresadas en m; CRS/EPSG y datum vertical NO DOCUMENTADOS EN LAS FUENTES DISPONIBLES |

`Topopl.csv` está integrado técnicamente y es utilizable para la cobertura
computacional del grid, pero no aparece en el `data/raw/release_manifest.json`
original. Hay una referencia documental/histórica de compatibilidad espacial
indicada por el docente; no debe presentarse como prueba de procedencia oficial
del archivo ni como inclusión en el release manifest.

Los únicos códigos litológicos observados en `lith_code` son `OVB`, `BRX`,
`POR`, `VOL` y `AIR`; la fuente los identifica únicamente como `Observed
lithology code`. No se expanden ni interpretan y se conservan literalmente. El
código literal `lith_code=AIR` no equivale a `topo_status=AIR`.

### Cobertura topográfica comprobada

| Campo | Mínimo | Máximo |
|---|---:|---:|
| X | 242090.504105 | 243287.725586 |
| Y | 8195892.194946 | 8197095.651855 |
| Z | 3120.858516 | 3596.000000 |

La cobertura topográfica comprobada corresponde a los 210 centros XY únicos
necesarios para clasificar el grid: todos obtuvieron elevación TIN finita; la
intersección vertical con el grid también se comprobó en Z. No significa que
toda la nube raw esté dentro del grid: 69.266 puntos están dentro del
rectángulo XY del modelo y 148.846 fuera.

El release documenta coordenadas/cartesianas locales en metros, pero no hay
evidencia suficiente para asignar formalmente esa referencia a `Topopl.csv`.
Su CRS/EPSG es NO DOCUMENTADO EN LAS FUENTES DISPONIBLES; no se infieren UTM,
WGS84, PSAD56, zona, EPSG ni transformación. El datum o referencia vertical de
`Topopl.csv.Z` también es NO DOCUMENTADO EN LAS FUENTES DISPONIBLES; la
descripción de `collar.csv.z` no permite inferirlo.

## Derivados principales

| Archivo | Contenido y estado |
|---|---|
| `data/processed/m01b/composites.csv` | 5.830 composites: 5.750 de 2 m y 80 residuales. Reproducido byte por byte desde el código y las fuentes actuales. SHA-256: `7a00a557bf604eba8ac45d158ba2a01a6d03caa8fccd14b020c47df478b4193c`. |
| `data/processed/m01b/block_model_preliminary.csv` | Grid preliminar de 11.550 bloques, previo a la integración topográfica y a la asignación geológica final por intersección 3D. |
| `data/processed/m01b/block_model_preliminary_topography.csv` | 11.550 bloques con clasificación topográfica: `ROCK` 6.853, `AIR` 4.493, `PARTIAL` 204. |
| `data/processed/m01b/block_model_preliminary_geology.csv` | Resultado de asignación litológica por intersección 3D de intervalos observados; conserva la trazabilidad y los estados sin asignación. |
| `data/processed/m01b/block_model_preliminary_geology_topography.csv` | Modelo integrado dentro del alcance T2: topografía, litología observada, trazabilidad de soporte y estados `UNKNOWN/UNASSIGNED`. |

El grid usado tiene bloques de `50 × 50 × 10 m`, forma `15 × 14 × 55` y
11.550 bloques. El origen usado es `(242225, 8196250, 2990) m`; es un origen
local provisional.

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
oficial.

P2 es una decisión conceptual aprobada para el alcance preliminar;
reproducibilidad y cobertura verificadas, optimización del tamaño/origen no
demostrada. Los 50 m en X/Y son comparables con las medianas observadas de
55.90 m entre collars vecinos, 54.90 m por sección y 58.77 m para la mediana de
las medianas por sección; la cobertura espacial es heterogénea. No es
variografía ni demuestra un tamaño óptimo. Los 10 m en Z son una discretización
adoptada, sin justificación vertical formal suficiente.

## Auditorías observacionales

- 44 sondajes; 5.803 intervalos assay y 120 intervalos litológicos.
- En assay y litología: 0 gaps, 0 overlaps y 0 discrepancias entre `length_m`
  y `to_m - from_m`.
- 76 contactos contiguos con cambio de código; 48 assays cruzan al menos un
  contacto.
- La cobertura assay va desde MD 0 hasta la profundidad final del collar en
  44/44 sondajes.
- `11,574.785091049 m` de longitud litológica observada contabilizada dentro de
  la malla y 0 m fuera.
- 978 bloques asignados con soporte/intersección positiva; 68 conflictos y
  10.504 bloques sin soporte. Conflictos y falta de soporte permanecen
  `UNKNOWN/UNASSIGNED`. La cantidad sin soporte es consecuencia de la regla
  conservadora (solo asigna con intersección y soporte concordante), no debe
  interpretarse por sí sola como error del algoritmo.

La validación geológica se limita a coherencia y trazabilidad contra los
intervalos/contactos observados del repositorio; no constituye certificación
profesional externa.

## Reglas de integridad y uso

- `data/raw/` es inmutable; los procesos leen las fuentes y no las sobrescriben.
- Los datos transformados y modelos derivados se guardan en `data/processed/`.
- Los resultados visuales y logs se guardan en `outputs/`.
- No interpretar los códigos litológicos sin documentación oficial; conservar
  los valores observados literalmente.
- No confundir el código litológico literal `AIR` con el estado topográfico
  `topo_status=AIR`, que es una clasificación independiente.
- CRS/EPSG y datum vertical de `Topopl.csv` están NO DOCUMENTADOS EN LAS
  FUENTES DISPONIBLES; no asignar referencia con base en `collar.csv.z`.
