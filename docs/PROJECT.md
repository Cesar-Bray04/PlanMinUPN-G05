# Proyecto T2 M01B — Modelo de bloques preliminar

## Identificación

- **Proyecto:** PlanMinUPN / Planeamiento de Minado 2026-2
- **Grupo:** G05
- **Dataset:** Santa Elena / DS05 / EXP03
- **Rama:** `feature/m01b-block-model`
- **HEAD actual/documental:** `207ba75`
- **Commit técnico del modelo final:** `a70b546`

## Propósito

Construir un modelo de bloques geológico preliminar 3D, sin estimación de leyes,
a partir de collar, survey, assay, lithology, density y la topografía
`Topopl.csv`, integrada técnicamente; su procedencia oficial no queda acreditada
por el manifiesto del release.

## Alcance técnico final

- Desurvey y positioning de sondajes.
- Compositing M01B.
- Construcción de un grid regular.
- Integración topográfica y clasificación de bloques.
- Asignación litológica por intersección 3D de intervalos observados.
- Validación computacional y observacional.
- Visualización 3D integrada.

## Grid final

- **Dimensiones de bloque:** `50 × 50 × 10 m`
- **Forma:** `15 × 14 × 55`
- **Total:** `11.550` bloques
- **Origen local provisional:** `(242225, 8196250, 2990) m`

Para el modelo categórico preliminar del alcance T2 se adopta una malla
reproducible de 50 × 50 × 10 m, con forma 15 × 14 × 55 (11,550 bloques) y
origen local provisional (242225, 8196250, 2990) m. La dimensión horizontal de
50 m se eligió como escala conceptual comparable con las medianas observadas de
distancia al collar vecino más cercano (55.90 m) y de espaciamiento por sección
(54.90 m; mediana de las medianas por sección: 58.77 m); la cobertura es
heterogénea y este análisis no constituye variografía ni demuestra un tamaño
óptimo. La dimensión vertical de 10 m se conserva como discretización adoptada,
pero no está justificada formalmente por el espaciamiento vertical observado.
El origen se obtuvo por redondeo inferior respecto del cero numérico local con
incrementos de 25/25/10 m para la candidata conceptual anterior y se retuvo al
pasar a 50/50/10 m; no es una referencia oficial.

P2 es una decisión conceptual aprobada para el alcance preliminar; la
reproducibilidad y cobertura están verificadas, pero no se ha demostrado la
optimización del tamaño ni del origen.

## Resultados principales

- **Compositing:** 5.830 composites reproducibles byte por byte desde 5.803
  assays fuente; derivado: `data/processed/m01b/composites.csv`.
- **Topografía:** 218.112 puntos en `data/raw/topography/Topopl.csv`, campos
  `PID`, `X`, `Y`, `Z`; los 210 centros XY del grid tienen elevación TIN finita.
  Esto no significa que toda la nube raw esté dentro del grid: 69.266 puntos
  quedan en su rectángulo XY y 148.846 fuera. Los 44 collars y 313 estaciones
  de trayectoria también están dentro; los intervalos litológicos contabilizan
  11,574.785091049 m dentro y 0 m fuera.
- **Clasificación topográfica:** 6.853 `ROCK`, 4.493 `AIR` y 204 `PARTIAL`.
- **Geología observada:** 120 intervalos litológicos posicionados y 76 contactos.
- **Asignación:** 978 bloques asignados con soporte/intersección positiva;
  68 conflictos y 10.504 bloques sin soporte permanecen
  `UNKNOWN/UNASSIGNED`.
- **Pruebas técnicas finales:** 41 aprobadas.

## Visualización final

`outputs/figures/m01b_block_model_geology_topography.html`: visualización 3D
integrada con superficie topográfica, bloques, sondajes, intervalos litológicos,
contactos, estados `UNKNOWN/UNASSIGNED`, controles de litología/topografía y
sección X-Z.

## Limitaciones

- CRS/EPSG de `Topopl.csv` y datum/referencia vertical de `Z`: no documentados.
  No se infieren UTM, WGS84, PSAD56, zona ni transformación. El release describe
  coordenadas/cartesianas locales en metros, pero no hay evidencia suficiente
  para asignar formalmente ese CRS a Topopl.
- No está documentado el significado oficial de `OVB`, `BRX`, `POR`, `VOL` y
  `AIR`; se conservan como códigos observados.
- La validación geológica verifica coherencia con intervalos y contactos
  observados del repositorio; no es certificación profesional externa.
- `Topopl.csv` no figura en el `release_manifest.json` original. Existe una
  referencia documental/histórica de compatibilidad espacial indicada por el
  docente, pero no acredita la procedencia oficial del archivo.
- Fuera de alcance: estimación Cu/Mo/Au, recursos/reservas, pit final y
  secuenciamiento.
