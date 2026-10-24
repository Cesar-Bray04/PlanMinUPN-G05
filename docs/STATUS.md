# STATUS.md

Estado vivo del proyecto.

## Estado actual

- **Último IMP validado:** IMP-004 — Validación de intervalos litológicos observados
- **Módulo en desarrollo:** Ninguno
- **Fecha de actualización:** 2026-10-24

## Módulos

| IMP | Módulo | Estado | Observación |
|---|---|---|---|
| IMP-003 | Integración topográfica al modelo de bloques preliminar | VALIDATED | TIN lineal y clasificación por elevación en XY del centro; datos y visualización generados. Validación computacional, no validación geológica ni de CRS. |
| IMP-004 | Intersección 3D de intervalos litológicos y contactos observados | VALIDATED | 120 intervalos y 76 contactos auditados; trazabilidad por bloque, códigos solo con soporte y figura diagnóstica integrada. Alcance limitado a observaciones, no interpretación profesional externa. |

## Gates M01B

| Gate | Estado | Evidencia / alcance |
|---|---|---|
| B09 — topografía oficial | VERIFIED | `Topopl.csv` está disponible y verificado en el árbol de trabajo; no cambió durante IMP-003. |
| P3 — superficie y clasificación topográfica | VERIFIED | Interpolación cubierta para los 210 centros XY del grid; 11.550 bloques clasificados y derivado/HTML generados. Estado computacional, no validación minera. |
| P4 — asignación litológica observada | VERIFIED | Intersección 3D de intervalos con bloques; 100 % de la longitud observada contabilizada; sin códigos fuera de soporte; conflictos y vacíos no asignados; contactos trazables. |
| P5 — pruebas y validación | VERIFIED | 41 pruebas aprobadas; tabla cruzada litología/topografía revisada y documentada. No representa interpretación externa; combinaciones sin significado oficial permanecen señaladas. |
| P6 — vista geología + topografía | VERIFIED | HTML integrado con superficie, bloques, intervalos, 76 contactos y sección X-Z inspeccionada. Diagnóstico, no validación operacional. |

## Próximo paso acordado

Revisar con criterio minero la aproximación de elevación única por centro XY y
confirmar formalmente CRS/datum antes de cualquier uso operacional.

## Bloqueadores

- No se documenta CRS/EPSG ni datum vertical formal para el archivo topográfico.

## Validaciones pendientes

- Revisión geológica/minera de `ROCK` / `AIR` / `PARTIAL`; la clasificación
  representa una intersección aproximada en el centro XY y no una fracción
  volumétrica.
- Confirmar CRS/EPSG, datum vertical y significado oficial de los códigos antes
  de cualquier interpretación o uso operacional. P4/P5 verifican coherencia y
  trazabilidad respecto de intervalos observados, no continuidad extrapolada.
