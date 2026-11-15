# Validación técnica y límites de Kai R6

**Fecha:** 13 de noviembre de 2026, Lima. **Rama:** `codex/kai-g05-teoria-s11-s12`.

## Implementación

- Base corregida R5.3.1 integrada al checkout G05, conservando su registro y ruta V1.
- Perfil activo R6 y contenido de ocho competencias iniciales, dieciséis unidades S11 y seis unidades S12. Son unidades conceptuales; no veintidós entregas técnicas ni una nueva rúbrica.
- Continuidad V2 separada, con SQLite canónico, Excel derivado, checkpoints, nombres consentidos, control de secuencia y reintentos idempotentes.
- Guía visual ampliada y enlazada desde el visor. Los logotipos originales se muestran mediante encuadre CSS, preservando los PNG.

## Evidencia ejecutada

La regresión conjunta pasó **50 pruebas** en una carpeta temporal: 34 de V1 y 16 de V2. Incluye continuidad entre procesos, compatibilidad de Excel, separación entre aliases, error/refuerzo, checkpoints, etapas, protección del historial V1 y recuperación tras fallos de exportación. Las dos pruebas históricas de bloqueo utilizan el helper Windows original, reubicado solo en el entorno aislado. El entorno de pruebas se ejecuta en UTF-8 para mantener la misma interpretación de texto entre procesos.

Las pruebas usan respuestas ficticias y valoraciones sintéticas. No demuestran que un modelo conversacional evalúe correctamente a una persona. El tipo RAZONAMIENTO_PROPIO es una declaración del tutor, no una inferencia semántica producida por SQLite.

La guía pasó **10 controles en Chrome sin solicitudes de red**: anclas únicas, logos locales, decisión inicialmente oculta, compositados 2/5/10 m con contactos y residuos, longitudes proporcionales, cambio de malla con observaciones constantes, ocho fichas completas, revelación manual de IDW², una situación visible sin calificar un clic y ancho móvil de 390 px sin desborde. Se generaron seis capturas para revisión visual.

Los controles de integridad finales comparan el checkout original, datos, algoritmos, gobernanza, visores, ruta/motor V1 y la copia piloto original mediante hashes. El expediente externo contiene los resultados y el manifiesto final; no incluye historiales reales.

## Cómo repetir los controles técnicos

Desde un entorno Python disponible, `python scripts/validar_kai_teoria.py` ejecuta V1/V2 en un temporal sin historiales. El argumento opcional `--log` guarda la salida. Para la prueba visual, `node scripts/qa_guia_teoria.cjs RUTA_DE_SALIDA` requiere Playwright y Chrome instalados. No se instalaron dependencias en este repositorio para la revisión.

## Pendientes y alcance

La conversación real en Copilot/PyCharm y el dictamen pedagógico siguen pendientes del [protocolo humano](PROTOCOLO_HUMANO_KAI_R6.md). No se ha comprobado que un IDE concreto haya cargado este perfil. La carpeta está preparada para abrirla por separado, sin cambiar otra sesión.

La ruta es teórica: no ejecuta estimaciones, validaciones cuantitativas S11/S12, explotación ni economía real G05. El inicio de S12 usa el ejemplo conceptual PT-01 y los estados mantienen los productos grupales como no verificados. No se declaran recursos/reservas profesionales, notas oficiales ni aprobación institucional. No hay sincronización entre equipos ni autenticación institucional.

La rama y los archivos son locales y permanecen sin commit ni push. La candidata para revisión no acredita aceptación humana ni publicación.
