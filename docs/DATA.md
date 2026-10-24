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
| `data/raw/topography/Topopl.csv` | 218.112 | `PID`, `X`, `Y`, `Z` | Coordenadas/elevación expresadas en m; CRS/EPSG y datum vertical no documentados formalmente |

Los códigos litológicos observados en `lith_code` son `OVB`, `BRX`, `POR`,
`VOL` y `AIR`. El repositorio no documenta su significado oficial y se
conservan literalmente. El código literal `AIR` no equivale a
`topo_status=AIR`.

### Cobertura topográfica comprobada

| Campo | Mínimo | Máximo |
|---|---:|---:|
| X | 242090.504105 | 243287.725586 |
| Y | 8195892.194946 | 8197095.651855 |
| Z | 3120.858516 | 3596.000000 |

La cobertura del grid se comprobó en X/Y y su intersección vertical en Z. No se
afirma un CRS/EPSG ni un datum vertical.

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
  `UNKNOWN/UNASSIGNED`.

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
- No afirmar CRS/EPSG ni datum vertical, porque no están documentados
  formalmente.
