# Proyecto T2 M01B — Modelo de bloques preliminar

## Identificación

- **Proyecto:** PlanMinUPN / Planeamiento de Minado 2026-2
- **Grupo:** G05
- **Dataset:** Santa Elena / DS05 / EXP03
- **Rama:** `feature/m01b-block-model`
- **HEAD técnico final:** `a70b546`

## Propósito

Construir un modelo de bloques geológico preliminar 3D, sin estimación de leyes,
a partir de collar, survey, assay, lithology, density y topografía oficial.

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
- **Origen:** `(242225, 8196250, 2990) m`

## Resultados principales

- **Compositing:** 5.830 composites reproducibles byte por byte desde 5.803
  assays fuente; derivado: `data/processed/m01b/composites.csv`.
- **Topografía:** 218.112 puntos en `data/raw/topography/Topopl.csv`, campos
  `PID`, `X`, `Y`, `Z`; cobertura del grid comprobada en X/Y e intersección en Z.
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

- CRS/EPSG no documentado formalmente; datum vertical no documentado.
- No está documentado el significado oficial de `OVB`, `BRX`, `POR`, `VOL` y
  `AIR`; se conservan como códigos observados.
- La validación geológica verifica coherencia con intervalos y contactos
  observados del repositorio; no es certificación profesional externa.
- Fuera de alcance: estimación Cu/Mo/Au, recursos/reservas, pit final y
  secuenciamiento.
