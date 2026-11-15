# Publicación IMP-008 · G05 Santa Elena

Esta rama parte de `feature/m01b-block-model` en `7825c2110a111193eb8e069c6358baa0dca0eb3e`. Integra el recorrido Kai E1 → S11 → S12, las fichas individuales vacías, los controladores, los visualizadores y los productos técnicos grupales de Santa Elena DS05/EXP03. No contiene `.kai_local` ni resultados de estudiantes.

## Productos activos

- S11: `4cc61d4696212e9928cc`, verificado por `src.missions.products.product_status` como `VALIDATED`.
- S12: `c1b396f1482e4ee1d39d`, verificado por el mismo mecanismo como `VALIDATED` y vinculado a la corrida S11 anterior.
- `outputs/Entregable_Grupal_G05_S11_S12.zip` contiene los modelos, controles y fuentes de este grupo. Los entregables individuales se generan localmente por alias y no se publican.

La guía de métodos ofrece ejemplos sintéticos. `index.html#s11` y `#s12` muestran los resultados académicos G05 calculados. Los modelos no equivalen a recursos o reservas profesionales.

## Validación de la rama candidata

- `python -m pytest -q`: **121 passed**. Se excluyó del repositorio de publicación `tests/test_integracion_g05.py`, porque requiere el instalador local `scripts/integrar_g05.py` y solo prueba el traslado de un paquete al checkout de DD; las pruebas de ruta, fichas, modelos y productos permanecen.
- `node scripts/qa_modelos_g05.cjs`: **PASS** en el contrato de ambos HTML de visor; no es comprobación visual en navegador.
- `product_status`: ambas corridas activas `VALIDATED`.
- `node scripts/qa_guia_teoria.cjs`: **NOT RUN** en esta copia por falta del módulo local `playwright`; la guía sí fue auditada previamente en el checkout de integración. Este documento no atribuye esa auditoría a la rama publicada.

La conversación real con Kai en Copilot/PyCharm y la aceptación pedagógica humana continúan pendientes. Los resultados de G05 no se deben copiar a G01–G04.
