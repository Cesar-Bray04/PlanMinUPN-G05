# IMP-001 — Arquitectura básica de desurvey

## 1. Identificación

- **Implementation ID:** IMP-001
- **Module:** Arquitectura básica de desurvey
- **Date:** 2026-09-26
- **Group:** G05
- **Participants:** No especificados
- **Status:** IN_PROGRESS

## 2. Problema minero

Organizar el flujo computacional para leer collar, survey, assay, lithology,
alteration y density, calcular trayectorias de sondajes y ubicar intervalos
observados, sin alterar los datos fuente.

## 3. Objetivo

Establecer la estructura modular aprobada por el equipo. `main.py` coordina los
módulos; no contiene la lógica de lectura, validación, cálculo, posicionamiento,
visualización ni exportación.

## 4. Inputs

| Variable | Significado | Unidad | Origen | Obligatorio | Validación |
|---|---|---|---|---|---|
| collar | Ubicación, orientación inicial y profundidad final de sondajes | Según diccionario de datos | `data/raw/collar.csv` | Sí | Pendiente de implementar el plan aprobado |
| survey | Mediciones de orientación en profundidad | m y grados | `data/raw/survey.csv` | Sí | Pendiente de implementar el plan aprobado |
| assay | Intervalos y leyes observadas | m, %, g/t según campo | `data/raw/assay.csv` | Sí | Pendiente de implementar el plan aprobado |
| lithology | Intervalos y códigos litológicos observados | m | `data/raw/lithology.csv` | Sí | Pendiente de implementar el plan aprobado |
| alteration | Intervalos y códigos observados de alteración (archivo actualmente sin registros) | m | `data/raw/alteration.csv` | Sí, archivo; cero registros disponibles | Pendiente de implementar el plan aprobado |
| density | Muestras e intervalos de densidad observada | m y t/m3 | `data/raw/density.csv` | Sí | Pendiente de implementar el plan aprobado |
| data_dictionary | Definición de campos, unidades y tipos | Según campo | `data/raw/data_dictionary.csv` | Sí | Referencia de metadatos |
| release_manifest | Inventario e información del release | No aplica | `data/raw/release_manifest.json` | Sí | Referencia de metadatos |

## 5. Outputs

| Variable / resultado | Significado | Unidad | Destino |
|---|---|---|---|
| Trayectoria desurveyada | Coordenadas espaciales calculadas a lo largo de cada sondaje | m | `data/processed/` (formato pendiente) |
| Intervalos posicionados | Intervalos observados asociados a coordenadas espaciales | m | `data/processed/` (formato pendiente) |
| Visualizaciones | Presentación de resultados para revisión | Por definir | `outputs/` |

## 6. Supuestos

No se agregan supuestos de cálculo. El algoritmo de desurvey, criterios de
validación, visualizaciones y formatos de exportación siguen pendientes de
implementación según definiciones del equipo.

## 7. Lógica minera

El flujo aprobado separa la lectura y validación de entradas, el cálculo de la
trayectoria, y el posicionamiento de intervalos. No se implementó un método de
desurvey porque no está especificado en el repositorio.

## 8. Diseño computacional

### Módulos / archivos

- `src/mod1/loader.py`: carga los seis CSV de observaciones, el diccionario de
  datos y el manifiesto del release.
- `src/mod1/validator.py`: punto de integración del plan de validación aprobado.
- `src/mod1/desurvey.py`: punto de integración del método de desurvey acordado.
- `src/mod1/positioning.py`: punto de integración para posicionar intervalos.
- `src/mod1/visualizer.py`: punto de integración para visualizar resultados.
- `src/mod1/exporter.py`: punto de integración para exportar resultados acordados.
- `main.py`: orquesta el flujo.

### Funciones / clases principales

- `load_raw_data(raw_directory)`: devuelve las tablas fuente, el diccionario y
  el manifiesto en memoria.
- `validate_data(raw_data)`: pendiente de integrar las reglas aprobadas.
- `desurvey(collar, survey)`: pendiente de integrar el método acordado.
- `position_intervals(trajectory, intervals)`: pendiente de definir e implementar.
- `visualize_results(trajectory, positioned_data)`: pendiente de definir salida.
- `export_results(positioned_data, processed_directory, outputs_directory)`:
  pendiente de definir formatos.

## 9. Etapas de implementación

### Etapa 1 — 2026-09-26

- **Objetivo:** establecer la estructura modular aprobada.
- **Trabajo realizado:** se creó el paquete `src/mod1`, el cargador CSV, los
  puntos de integración para etapas con reglas pendientes y la orquestación.
- **Actualización:** el loader incluye alteration, diccionario y manifiesto;
  alteration se entrega al módulo de posicionamiento. Se comprobó la lectura del
  release del proyecto (incluido alteration vacío) y se añadieron pruebas del
  loader para tablas completas y vacías.
- **Resultado:** estructura base creada; el flujo no puede ejecutarse completo
  hasta integrar las definiciones pendientes.
- **Pendiente:** incorporar validaciones y método de desurvey acordados, y definir
  contrato de posicionamiento, visualización y exportación.

## 10. Decisiones

### DECISION-01

**Problema:** mantener la arquitectura mínima modular para el flujo de desurvey.

**Alternativas consideradas:** estructura plana aprobada por el equipo en
`src/mod1/`, frente a una arquitectura con múltiples paquetes por dominio.

**Alternativa seleccionada:** `src/mod1/` con módulos por responsabilidad.

**Justificación:** corresponde a la estructura básica revisada y aprobada por G05.

**Impacto:** `main.py` queda como orquestador y cada etapa tiene un archivo propio.

## 11. Archivos creados o modificados

```text
main.py
src/__init__.py
src/mod1/__init__.py
src/mod1/loader.py
src/mod1/validator.py
src/mod1/desurvey.py
src/mod1/positioning.py
src/mod1/visualizer.py
src/mod1/exporter.py
tests/test_loader.py
docs/implementation/IMP-001_desurvey_architecture.md
```

## 12. Pruebas realizadas

### Comandos ejecutados

```text
python -m compileall -q main.py src tests
Resultado: PASS

Pruebas de tests/test_loader.py invocadas directamente con Python
Resultado: PASS (2 pruebas)

python -m pytest tests\test_loader.py -q
Resultado: NOT RUN; pytest no está instalado en el entorno.
```

### Resultado real

- **Status:** PASS para compilación y pruebas directas del loader; pytest no disponible.
- **Tests passed:** 2 pruebas del loader invocadas directamente.
- **Tests failed:** 0.
- **Comprobación con datos del proyecto:** 44 collar, 313 survey, 5803 assay,
  120 lithology, 0 alteration, 459 density y 54 filas del diccionario; se leyó
  el manifiesto del release `EXP03`.

## 13. Validación minera

- [ ] Unidades consistentes.
- [ ] Signos económicos correctos cuando corresponda.
- [ ] Magnitudes razonables.
- [ ] Restricciones operacionales respetadas.
- [ ] Casos extremos revisados.
- [ ] Caso manual independiente revisado cuando es posible.

### Evidencia / comentario

Pendiente: no se ha implementado la lógica de cálculo.

## 14. Limitaciones y pendientes

### LIMITATION-01

El workflow está estructurado, pero el validador, el cálculo de trayectoria,
posicionamiento, visualización y exportación lanzan `NotImplementedError` hasta
que el equipo complete las definiciones necesarias.

## 15. Uso del agente de IA

- [x] Arquitectura.
- [x] Implementación.
- [x] Documentación.

Comentario: se implementó la estructura aprobada por G05 sin definir reglas
técnicas que no están documentadas.

## 16. Checklist de cierre

- [x] Problema minero documentado.
- [x] Inputs documentados.
- [ ] Unidades verificadas.
- [x] Supuestos identificados.
- [ ] Lógica minera documentada.
- [ ] Implementación terminada.
- [ ] Pruebas ejecutadas o justificadas como `NOT RUN`.
- [ ] Validación computacional realizada.
- [ ] Validación minera realizada.
- [x] Archivos modificados registrados.
- [x] Limitaciones registradas.
- [ ] Registro actualizado.

El módulo permanece `IN_PROGRESS`; la arquitectura está creada, no cerrada.
