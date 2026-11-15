# IMP-003 — Integración topográfica al modelo de bloques preliminar

## Estado final vigente

- **HEAD actual/documental:** `66e1ae3` en `feature/m01b-block-model`.
- **Commit documental anterior:** `207ba75`.
- **Commit técnico del modelo final:** `a70b546`.
- **Suite técnica final:** `41 passed`.
- **B09:** `VERIFIED` dentro del alcance computacional/topográfico implementado.
- **P3:** `VERIFIED` únicamente para integración, interpolación y clasificación
  topográfica computacionales; no valida CRS/EPSG ni datum vertical.
- El grid de referencia de P3 es `50 × 50 × 10 m`, forma `15 × 14 × 55`
  (11.550 bloques), origen local provisional `(242225, 8196250, 2990) m`.
  P2 es decisión conceptual aprobada para el alcance preliminar; cobertura y
  reproducibilidad verificadas, optimización del tamaño/origen no demostrada.
  Los 50 m horizontales son comparables con medianas observadas, pero la
  cobertura es heterogénea; 10 m en Z es discretización adoptada sin
  justificación vertical formal suficiente.
- La fuente `data/raw/topography/Topopl.csv` contiene 218.112 puntos con campos
  `PID`, `X`, `Y`, `Z`. Los 210/210 centros XY del grid obtuvieron elevación TIN
  finita, los 11.550 bloques reciben clasificación topográfica y la intersección
  vertical en Z se comprobó. Esto no significa que
  toda la nube raw esté dentro del grid: 69.266 puntos están dentro del
  rectángulo XY del modelo y 148.846 fuera.
- `Topopl.csv` está integrado técnicamente, pero no aparece en el
  `release_manifest.json` original. Existe una referencia documental/histórica
  de compatibilidad espacial indicada por el docente; no acredita procedencia
  oficial del archivo.
- CRS/EPSG de `Topopl.csv` y datum o referencia vertical de `Z`: NO
  DOCUMENTADOS EN LAS FUENTES DISPONIBLES. El release describe
  coordenadas/cartesianas locales en metros,
  pero no existe evidencia suficiente para asignar formalmente esa referencia
  a Topopl. No se infieren UTM, WGS84, PSAD56, zona ni transformación; la
  definición de `collar.csv.z` no establece el datum de la columna Z topográfica.
- La interpolación usa triangulación Delaunay (TIN) e interpolación lineal
  para obtener `topo_z_m` en los 210 centros XY únicos del grid de
  `50 × 50 × 10 m` (forma `15 × 14 × 55`, 11.550 bloques). Si una consulta no
  está cubierta, el proceso falla explícitamente; no extrapola ni escribe una
  salida parcial.
- Conteos `topo_status`: `ROCK` 6.853, `AIR` 4.493 y `PARTIAL` 204.
  `topo_status` es independiente de `lith_code`; el código litológico literal
  `AIR` no equivale a `topo_status=AIR`.
- Esta clasificación compara la elevación interpolada en el centro XY con
  `z_min`/`z_max`; no calcula la fracción volumétrica exacta sobre la huella
  completa del bloque.
- CRS/EPSG y datum vertical de `Topopl.csv` están NO DOCUMENTADOS EN LAS
  FUENTES DISPONIBLES.
- La integración geológica y la visualización 3D final se documentan en
  `IMP-004_m01b_geological_validation.md`.

## 1. Identificación

- **Implementation ID:** IMP-003
- **Module:** Integración de superficie topográfica y clasificación de bloques
- **Date:** 2026-10-23
- **Group:** G05
- **Status:** VALIDATED
- **Related gates:** B09 `VERIFIED`; P3 `VERIFIED` en alcance computacional

## 2. Problema minero

El modelo de bloques preliminar no distinguía celdas por su relación con la
superficie topográfica. Se requiere estimar la elevación de terreno en cada
posición XY del modelo y mantener esa clasificación separada de la litología
observada.

## 3. Objetivo

Generar un nuevo derivado que conserve los 11.550 bloques y sus campos
litológicos, añada `topo_z_m` y `topo_status`, y produzca una visualización 3D
con superficie, bloques y controles para inspeccionar litología o estado
topográfico.

## 4. Inputs

| Variable | Significado | Unidad | Origen | Obligatorio | Validación |
|---|---|---|---|---|---|
| `Topopl.csv` (`PID`, `X`, `Y`, `Z`) | Puntos observados de topografía | X/Y/Z en m | `data/raw/topography/Topopl.csv` | Sí | Encabezados requeridos; XYZ finitos; al menos tres puntos; XY únicos y triangulables |
| Modelo preliminar (`i`, `j`, `k`, límites, centros, litología y soportes) | Geometría y datos litológicos existentes | Coordenadas en m | `data/processed/m01b/block_model_preliminary.csv` | Sí | Esquema, estados litológicos y filas validadas por el lector existente |

El inventario verificado reporta 218.112 registros, rango Z de 3120.858516 a
3596.0 m y cobertura que intersecta el intervalo vertical del grid (2990–3540
m). Los 210 centros XY únicos del grid están cubiertos por el TIN. Dentro del
rectángulo XY del grid se encuentran 69.266 puntos topográficos y 148.846 fuera;
la integración no afirma que toda la nube raw esté contenida. El CRS/EPSG de
Topopl y el datum vertical de Z no están documentados formalmente.

## 5. Outputs

| Variable / resultado | Significado | Unidad | Destino |
|---|---|---|---|
| `topo_z_m` | Elevación interpolada en el centro XY de cada bloque | m | `data/processed/m01b/block_model_preliminary_topography.csv` |
| `topo_status` | Relación del bloque con la superficie | Categoría | Mismo CSV; separada de `lith_code`/`lith_status` |
| Visualización 3D | Superficie TIN, bloques, litología, estados y trayectorias | HTML autónomo | `outputs/figures/m01b_block_model_topography.html` |

Los derivados preliminares anteriores se conservaron sin sobrescritura.

## 6. Supuestos

| ID | Supuesto | Justificación | Impacto |
|---|---|---|---|
| SUP-01 | Una elevación interpolada en el centro XY representa la superficie para la clasificación del bloque | Regla aprobada para el modelo preliminar | No determina la fracción volumétrica real bajo una superficie inclinada |
| SUP-02 | La cobertura interpolable corresponde al interior de la envolvente convexa del TIN | Interpolación lineal por triangulación de puntos XY | No se extrapola fuera de esa envolvente; la interpolación no comprueba vacíos topográficos internos |

## 7. Lógica minera

La superficie es una triangulación de Delaunay sobre los puntos XY observados;
la elevación dentro de cada triángulo se interpola linealmente. El cálculo se
realiza una vez por cada centro XY único del grid: 210 ubicaciones para la malla
de 15 × 14 × 55 bloques. Si cualquier centro no tiene interpolación finita, el
proceso falla y no escribe una salida parcial.

Para cada bloque, con elevación interpolada `topo_z_m` y límites verticales
`z_min`, `z_max`:

- `AIR` si `topo_z_m <= z_min` (bloque completamente por encima o en el límite
  inferior de la superficie).
- `ROCK` si `topo_z_m >= z_max` (bloque completamente por debajo o en el límite
  superior de la superficie).
- `PARTIAL` si `z_min < topo_z_m < z_max` (superficie cruza el intervalo
  vertical del bloque).

`lith_code` y `lith_status` se copian sin cambios. Un código litológico literal
`AIR` no sustituye ni determina `topo_status`.

## 8. Diseño computacional

### Módulos / archivos

- `src/mod1/topography.py`: lectura, validación, TIN lineal, control de cobertura,
  clasificación y escritura del nuevo CSV.
- `src/mod1/block_model_visualizer.py`: lectura del esquema enriquecido y figura
  con TIN, bloques por litología o estado, sondajes y hover de atributos.
- `tests/test_m01b_topography.py`: casos sintéticos, cobertura real, preservación
  litológica e inspección estructural de la figura.
- `requirements.txt`: dependencia `scipy>=1.11,<2`.
- `data/processed/m01b/block_model_preliminary_topography.csv`: nuevo derivado.
- `outputs/figures/m01b_block_model_topography.html`: figura offline autónoma.
- `docs/STATUS.md`: estado de B09/P3 y validaciones pendientes.

### Dependencias relevantes

- SciPy 1.17.1 (`scipy.spatial.Delaunay`,
  `scipy.interpolate.LinearNDInterpolator`).
- NumPy para arreglos de coordenadas y triángulos.
- Plotly para la visualización interactiva.

## 9. Etapas de implementación

### HISTÓRICO — Etapa 1 — 2026-10-23

- **Objetivo:** implementar P3 sin alterar datos raw ni derivados existentes.
- **Trabajo realizado:** se añadió interpolación TIN, fallo explícito ante
  cobertura insuficiente, clasificación independiente de litología, tests,
  controles de visualización por litología/estado y nuevos artefactos.
- **Resultado:** 210/210 centros XY interpolados; 11.550 bloques escritos.
- **Limitaciones identificadas entonces:** revisión geológica/minera y
  confirmación formal de CRS/datum. La revisión de coherencia contra
  observaciones geológicas y la integración se documentan en IMP-004; CRS y
  datum siguen sin documentación formal.

## 10. Decisiones

### DECISION-01 — TIN con interpolación lineal

**Problema:** los puntos disponibles no constituyen un grid rectangular regular
X/Y y no se encontró SciPy instalado inicialmente.

**Alternativas consideradas:** asumir una grilla regular o usar triangulación
TIN; extrapolar fuera del dominio o detener el proceso.

**Alternativa seleccionada:** Delaunay sobre XY con interpolación lineal,
rechazando consultas no cubiertas. Se añadió SciPy al manifiesto.

**Justificación:** respeta la geometría de puntos dispersos sin inventar
elevaciones fuera de la envolvente interpolable y no requiere remuestrear la
fuente.

**Impacto:** los resultados dependen de la triangulación entre observaciones y
no incorporan un modelo de superficie geológico adicional.

### DECISION-02 — Clasificación por elevación del centro XY

Se usa el mismo `topo_z_m` para todos los niveles de una columna XY y se compara
con los límites verticales. No se estima porcentaje parcial de volumen.

### DECISION-03 — Estados topográficos independientes

`topo_status` se agrega como campo separado; los bloques pueden inspeccionarse
por litología o por estado topográfico. Los bloques sin litología comienzan
ocultos en el modo de litología para no obstruir la superficie y se incluyen al
seleccionar el modo de estado topográfico.

## 11. Archivos creados o modificados

```text
src/mod1/topography.py
src/mod1/block_model_visualizer.py
tests/test_m01b_topography.py
requirements.txt
data/processed/m01b/block_model_preliminary_topography.csv
outputs/figures/m01b_block_model_topography.html
docs/implementation/IMP-003_m01b_topography_integration.md
docs/STATUS.md
```

No se modificó `data/raw/`, el CSV preliminar anterior ni el HTML anterior.

## HISTÓRICO — 12. Pruebas de la etapa IMP-003

### Comandos ejecutados

```text
python -m pytest tests\test_m01b_topography.py -q
5 passed in 8.02s

python -m pytest -q
33 passed in 9.92s
```

### Resultado real

- **Status:** PASS
- **Tests passed:** 5 pruebas específicas; 33 pruebas de suite completa.
- **Tests failed:** 0 en ambas ejecuciones finales.

Las pruebas de esta etapa verifican interpolación lineal, no extrapolación, estados y límites
de intersección, XY duplicados y encabezados, cobertura del modelo con la
topografía real, conservación litológica y capas/modos de la visualización.

### Validación del derivado y artefactos

- Topografía cargada: 218.112 puntos; TIN con 270.738 triángulos.
- Modelo preliminar: 11.550 bloques y 210 centros XY únicos; los 210/210
  centros produjeron elevación finita.
- Conteos `topo_status`: `AIR` 4.493; `PARTIAL` 204; `ROCK` 6.853.
- Rango interpolado en centros XY: 3183.347651521489–3554.0 m.
- Conservación de `lith_code` y `lith_status`: 11.550/11.550 coincidieron con
  el modelo anterior.
- HTML: 53 trazas (superficie TIN, capas litológicas, UNKNOWN, tres capas
  topográficas y trayectorias de 44 sondajes); `topography_used=true` y
  `validation_claim=false`.
- Tamaños observados: CSV nuevo 1.553.207 bytes; HTML nuevo 52.852.590 bytes.
- Chrome headless renderizó el HTML a PNG 1600×1100 para inspección visual. Se
  observaron la superficie TIN, el grid de bloques, la leyenda, los controles
  de color, las trayectorias y la advertencia de alcance diagnóstico.
- Se verificó que los hashes del raw, modelo preliminar y HTML anterior se
  mantuvieron iguales durante la generación.

## 13. Validación y límites de alcance

- [x] Unidades de coordenadas/elevación manejadas en metros conforme a los
  datos disponibles.
- [x] Se verificaron límites verticales y los tres casos sintéticos de
  clasificación/intersección.
- [x] Se comprobó cobertura de todos los centros XY del grid con la fuente real.
- P3 queda `VERIFIED` para integración y clasificación topográfica
  computacional.
- La validación geológica observacional/computacional posterior está completada
  y documentada en `IMP-004_m01b_geological_validation.md` (P4/P5/P6
  `VERIFIED`). La casilla histórica de IMP-003 no indica que esos gates estén
  pendientes.
- La certificación profesional externa o validación operacional permanece fuera
  de alcance; también siguen sin documentación formal el CRS/EPSG y el datum
  vertical, y sin documentar el significado oficial de los códigos litológicos.
- [ ] Confirmación formal de CRS/EPSG y datum vertical.
- [ ] Validación de campo o comparación independiente de la superficie.

### Evidencia / comentario

B09 está `VERIFIED` y P3 está `VERIFIED` para cobertura, interpolación y
clasificación computacionales del alcance aprobado, según el estado final
vigente indicado al inicio. La validación observacional/computacional posterior
está documentada en IMP-004; las casillas de esta etapa no implican que P4/P5/P6
estén pendientes. La certificación profesional externa/operacional queda fuera
de alcance. No se certifican CRS/datum ni se atribuye significado oficial a los
códigos litológicos.

## 14. Limitaciones y pendientes

### LIMITATION-01 — Aproximación por centro XY

Una sola elevación por columna no calcula qué proporción volumétrica del bloque
está sobre o bajo una superficie inclinada; `PARTIAL` solo identifica el cruce
del intervalo vertical en el centro.

### LIMITATION-02 — TIN y sistema de referencia

La triangulación interpola linealmente entre puntos dentro de la envolvente
convexa; no extrapola fuera de ella, pero tampoco prueba la ausencia de vacíos
internos o discontinuidades. CRS/EPSG y datum vertical no están documentados
formalmente. La visualización HTML autónoma tiene aproximadamente 53 MB por la
superficie y la geometría de bloques; puede requerir memoria adicional al abrir.

### FUTURE-01 — Limitación vigente

Validar datum y alineación espacial con una referencia independiente y evaluar
si la clasificación por centro XY es suficiente antes de emplear el modelo en
decisiones operacionales.

## 15. Uso del agente de IA

- [x] Arquitectura.
- [x] Algoritmo.
- [x] Implementación.
- [x] Pruebas.
- [x] Depuración.
- [x] Revisión de unidades.
- [x] Documentación.

## 16. Checklist de cierre de la etapa

- [x] Problema minero documentado.
- [x] Inputs y unidades documentados.
- [x] Supuestos identificados.
- [x] Lógica minera documentada.
- [x] Implementación terminada.
- [x] Pruebas específicas y suite completa ejecutadas.
- [x] Validación computacional realizada.
- La validación geológica observacional/computacional posterior se completó y
  está documentada en `IMP-004_m01b_geological_validation.md`; esta casilla de
  cierre de la etapa IMP-003 no significa que P4/P5/P6 estén pendientes.
- La certificación profesional externa/operacional permanece fuera de alcance.
- [x] Archivos y limitaciones registrados.

El cierre de implementación y las pruebas enumeradas en esta sección
corresponden a la etapa histórica de IMP-003. El estado técnico final vigente,
la suite actual y la relación con la integración de IMP-004 se resumen en
**Estado final vigente** al inicio de este documento.
