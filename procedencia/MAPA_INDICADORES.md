# Mapa de indicadores del piloto G05

**Corte único:** repositorio `Cesar-Bray04/PlanMinUPN-G05`, rama `feature/m01b-block-model`, commit `7825c2110a111193eb8e069c6358baa0dca0eb3e`. Rutas de fuente relativas a ese commit. Los SHA-256 están en [`FUENTES_G05.json`](FUENTES_G05.json); los de los archivos entregados estarán en `MANIFIESTO_PAQUETE.json`.

| Dato presentado | Fuente primaria o registro | Cómo se comprobó / alcance |
|---|---|---|
| G05, Santa Elena, DS05/EXP03, release sintético | `data/raw/release_manifest.json`; `docs/PROJECT.md` | Identidad y bandera `synthetic_data` leídas del manifiesto. |
| 3 campañas; 44 sondajes, 313 survey, 5803 ensayes, 120 intervalos litológicos, 459 densidades observadas | `data/raw/collar.csv`, `survey.csv`, `assay.csv`, `lithology.csv`, `density.csv`; `data/raw/release_manifest.json` | Recuento de filas y por `campaign_id`; totales contrastados con manifiesto. Son registros de exploración, no propiedades de bloques. |
| 218 112 puntos topográficos | `data/raw/topography/Topopl.csv` | Filas recuentadas. Este archivo no figura en el manifiesto original del release; su procedencia, CRS y datum siguen pendientes. |
| Objetivo de compositado 2 m; Cu ponderado por longitud; respeto de contactos y residuos | `docs/exam/T2_M01B_PLAN_G05.md`, `docs/STATUS.md`; `data/processed/m01b/composites.csv` | Regla documentada; longitud y bandera `residual_flag` cotejadas en el CSV. |
| 5830 compósitos: 5750 completos, 80 residuales | `data/processed/m01b/composites.csv` | Filas y banderas recuentadas. El CSV está incluido en `datos/composites.csv`. |
| Ejemplo `SE-C01-001`, contacto 9 m, ensaye `A0005` 8–10 m, residuo OVB 8–9 m y VOL 9–11 m | `data/raw/assay.csv`, `data/raw/lithology.csv`, `data/processed/m01b/composites.csv` | Se cruzaron intervalos por `hole_id` y profundidad. La ventana 8–13 m es solo un caso pedagógico real. |
| Malla 15 × 14 × 55; 11 550 celdas; tamaño 50 × 50 × 10 m; origen local provisional | `data/processed/m01b/block_model_preliminary_geology_topography.csv`; `docs/implementation/IMP-002_m01b_block_model_preparation.md` | Índices únicos, límites XYZ y diferencias de coordenadas recuentados. No se calculó volumen minable. |
| Comparación horizontal con separación mediana cercana a 55 m; límite de justificación de los 10 m verticales | `docs/STATUS.md`; `docs/implementation/IMP-002_m01b_block_model_preparation.md` | Justificación y reserva documentadas por el grupo; no se optimizó la malla en esta fase. |
| TIN lineal, clasificación por centro XY, cobertura 210/210 centros | `docs/implementation/IMP-003_m01b_topography_integration.md` | Método y cobertura **reportados** por G05; no se reejecutó la interpolación. |
| ROCK 6853, AIR 4493, PARTIAL 204 | `data/processed/m01b/block_model_preliminary_geology_topography.csv` | Recuento de `topo_status`. PARTIAL no expresa fracción de roca. |
| 978 ASSIGNED, 10 572 UNKNOWN/UNASSIGNED; BRX 54, OVB 36, POR 463, VOL 425 | `data/processed/m01b/block_model_preliminary_geology_topography.csv` | Recuento de `lith_status` y `lith_code`. Los códigos se conservan literales. |
| 68 conflictos y 10 504 sin soporte | `data/processed/m01b/block_model_preliminary_geology_topography.csv` | Recuento de `lith_assignment_reason`. Ambas categorías permanecen sin código asignado. |
| Regla de intersección 3D con código único; 76 contactos; 44/44 collars y 313/313 survey dentro de malla | `docs/implementation/IMP-004_m01b_geological_validation.md`; `docs/STATUS.md` | Método, contactos y controles **documentados** por G05; no se reejecutó el algoritmo. |
| HTML integrado con 11 550 bloques y `validation_claim=false` | `outputs/figures/m01b_block_model_geology_topography.html` | Metadatos y trazas inspeccionados. El HTML del paquete conserva los bytes del checkout y coincide con la entrega local `MODELO DE BLOQUES 3D.zip`. Capas visibles y total incluido son conceptos distintos. |
| Portada de sondajes 3D: 44 trayectorias y 313 puntos XYZ, campañas 16/20/8 | Las 44 trazas `legendgroup=drillholes` del mismo HTML integrado; `data/raw/collar.csv` | Se copiaron las coordenadas XYZ ya incluidas en el HTML sin recalcular desurvey. Los IDs únicos coinciden con los 44 collars y la suma de puntos es 313. `visor/sondajes_3d_data.js` conserva esos valores; `assets/sondajes_3d_g05.png` es una perspectiva gráfica de ellos. |
| 41 PASS históricos | `docs/STATUS.md`, `docs/exam/T2_M01B_EVIDENCE_G05.md` | Resultado **reportado**, no una suite reejecutada en el piloto. |
| Sin leyes, densidad ni tonelaje estimados por bloque | `data/processed/m01b/block_model_preliminary_geology_topography.csv`; `docs/STATUS.md` | Ausencia de esas columnas constatada; no se sustituyen con DS00 ni con observaciones de muestra. |

[`datos/resumen_verificado.json`](../datos/resumen_verificado.json) concentra los recuentos que consume el visor. Su copia `resumen.js` permite abrir `index.html` como `file://` sin servidor local.
