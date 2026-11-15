# Validación del piloto visual G05

**Fecha de corte:** 11 de noviembre de 2026. **Objeto:** paquete docente de lectura, no nueva corrida de ingeniería ni certificación de recursos. **Fuente fijada:** G05 `feature/m01b-block-model`, commit `7825c2110a111193eb8e069c6358baa0dca0eb3e`, checkout limpio al verificarlo.

## Resultado de los controles

| Control | Resultado y evidencia | Límite |
|---|---|---|
| Identidad y procedencia | **PASS.** `release_manifest.json` identifica Santa Elena, DS05/EXP03 y datos sintéticos. Los ocho SHA-256 raw del manifiesto coinciden con los blobs canónicos del commit. | `Topopl.csv` no está incluido en ese manifiesto. |
| Indicadores de exploración | **PASS.** Recuento directo de los cinco CSV raw: 44 collars, 313 survey, 5803 ensayes, 120 litologías, 459 densidades observadas. Las tres campañas suman esos totales. | Las densidades son medidas de muestra. |
| Compositado y ejemplo | **PASS.** `composites.csv` contiene 5830 filas, 5750 de 2 m y 80 residuales. El contacto a 9 m y el ejemplo de 8–11 m se cotejaron con los CSV de ensaye, litología y compósitos. | No se reejecutó el algoritmo de compositado. |
| Geometría y clasificación | **PASS.** El CSV integrado tiene 11 550 índices únicos con forma 15 × 14 × 55 y tamaño uniforme 50 × 50 × 10 m. ROCK 6853 + AIR 4493 + PARTIAL 204 = 11 550. ASSIGNED 978 + UNKNOWN/UNASSIGNED 10 572 = 11 550. | PARTIAL no tiene fracción volumétrica calculada. |
| Litología | **PASS.** BRX 54 + OVB 36 + POR 463 + VOL 425 = 978 asignados; 68 conflictos + 10 504 sin soporte = 10 572 sin asignar. | No se revalidó geológicamente la continuidad; códigos sin definición oficial. |
| Propiedades cuantitativas | **PASS como ausencia.** El CSV integrado no posee columnas de leyes, densidad o tonelaje de bloque. Las siete pantallas señalan esa ausencia; no contienen resultados DS00. | No permite recursos, reservas ni plan operacional. |
| Integridad del 3D | **PASS de archivo y render inicial.** El HTML integrado original coincide byte por byte con la entrega local del grupo y se preservó en `visor/`. Contiene metadato de 11 550 bloques. Chromium/Chrome produjo una imagen con superficie, bloques coloreados, sondajes, sección X–Z, leyenda y clases visibles: [`08_modelo_3d_chrome.png`](capturas/08_modelo_3d_chrome.png). | Una captura no prueba rotación, zoom, hover, selector, carga en iframe ni respuesta en otros equipos. |
| Sondajes 3D de portada | **PASS de trazabilidad de datos.** Se extrajeron las 44 trazas `drillholes` del HTML original: 313 puntos XYZ y 44 IDs coincidentes con `collar.csv`; campañas 16/20/8. La figura [`sondajes_3d_g05.png`](assets/sondajes_3d_g05.png) se generó con esas mismas coordenadas y se inspeccionó visualmente. | La nueva vista interactiva `visor/sondajes_3d.html` aún no tiene prueba directa de render en Chrome tras el cambio. La imagen fija queda como respaldo visible. |
| Visor educativo | **PASS de render de la versión anterior y de revisión estática de la nueva.** Chrome/Chromium abrió las siete rutas `index.html#...` y generó capturas [`01` a `07`](capturas/) antes de corregir la portada. Los enlaces locales, la sintaxis JS y la correspondencia de las 44 trayectorias nuevas con la fuente se comprobaron después del cambio. | El render final de portada y la interacción por clic, arrastre, zoom y hover siguen pendientes de comprobación en Chrome. |
| Pruebas históricas G05 | **REPORTADAS.** El repositorio consigna 41 PASS. | No se reejecutaron en esta fase; no equivalen a validación minera independiente. |

Los detalles de cada cifra y archivo están en [`procedencia/MAPA_INDICADORES.md`](procedencia/MAPA_INDICADORES.md) y los SHA en `procedencia/FUENTES_G05.json` / `MANIFIESTO_PAQUETE.json`. La diferencia de fin de línea Windows CRLF frente a los blobs Git LF explica por qué algunos hashes del checkout difieren del manifiesto original. Los hashes del paquete corresponden a los **bytes entregados**.

## Inspección visual y funcionalidad pendiente

Se usó el Chrome instalado en este equipo en modo **headless**, con ventana de 1440 × 1000 para las pantallas y 1800 × 1100 para el HTML 3D original. Las capturas evidencian el estado inicial de cada pantalla y un render 3D. No se midió formalmente rendimiento, consumo de memoria ni compatibilidad en otros equipos; el HTML 3D de unos 52 MB puede ser pesado.

Las ocho capturas principales son `01_proyecto.png` a `08_modelo_3d_chrome.png`. **Las dos capturas de la primera pantalla corresponden a la versión anterior con el esquema conceptual**, antes de sustituirlo por los sondajes 3D a petición de DD. Se conservan como antecedente visual y no prueban el nuevo render de portada. `assets/sondajes_3d_g05.png` sí representa las trayectorias de G05, pero es una figura generada desde los datos y no una captura del navegador.

La herramienta de interacción del navegador bloqueó abrir la URL local `file://` por su política de protocolos. Por ello **no se verificaron mediante interacción real** los clics del menú, el botón «Cargar 3D aquí», el selector de capas, la rotación, el zoom, los tooltips ni el cambio de visibilidad. Esto incluye la nueva vista interactiva de sondajes en la portada. El código contiene esos controles y el 3D integrado original renderizó en la captura anterior, pero esos hechos no sustituyen la prueba interactiva de la versión revisada. DD puede actualizar la página local en Chrome y comprobar especialmente que los sondajes se vean, giren y respondan al hover antes de usar el piloto con estudiantes.

## Frontera de aprobación

El piloto queda **listo para revisión docente**, sin afirmar aprobación humana o institucional. La adaptación de P0/S11.1 a esta primera sesión es de contenido; el producto evaluable, puntaje y encaje curricular requieren decisión de DD. El agente Kai Planeamiento, el registro individual automático y la continuidad entre sesiones no se implementaron ni comprobaron aquí.
