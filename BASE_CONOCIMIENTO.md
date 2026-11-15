# G05 · Santa Elena — base de conocimiento de ingeniería

**Uso:** sustento factual del primer recorrido visual de PlanMinUPN 2.0.  
**Corte fuente:** [`Cesar-Bray04/PlanMinUPN-G05`, `feature/m01b-block-model`, commit `7825c2110a111193eb8e069c6358baa0dca0eb3e`](https://github.com/Cesar-Bray04/PlanMinUPN-G05/tree/7825c2110a111193eb8e069c6358baa0dca0eb3e).  
**Identidad:** G05 · `santa_elena` · DS05 · EXP03. Release académico sintético de exploración. No representa una mina operativa ni una declaración de recursos o reservas.

## Cómo leer los estados

- **COMPROBADO:** recuento o propiedad cotejada ahora contra un archivo fuente del commit; véase [`datos/resumen_verificado.json`](datos/resumen_verificado.json).
- **DECISIÓN DOCUMENTADA:** criterio consignado por el grupo en sus registros. Que esté documentado no lo convierte en diseño minero definitivo.
- **SUPUESTO TÉCNICO:** aproximación adoptada para poder construir el modelo preliminar.
- **PENDIENTE:** producto o dato que no existe como resultado grupal verificado.
- **LIMITACIÓN:** frontera de interpretación del producto disponible.

Las rutas y SHA-256 de cada fuente figuran en [`procedencia/FUENTES_G05.json`](procedencia/FUENTES_G05.json). Los dos CSV derivados incorporados al paquete permiten auditar los indicadores de compositado y bloques sin ejecutar Python. Los archivos raw permanecen en el repositorio original G05.

## 1. Identificación del proyecto

**Qué hicimos:** trabajamos el proyecto académico Santa Elena del grupo G05. **Por qué:** todas las observaciones y resultados deben pertenecer a la misma identidad de datos. **Decisión:** usar el release de exploración DS05/EXP03 del repositorio G05. **Parámetro:** rama y commit fijados arriba. **Resultado:** identidad y fuentes identificables. **Significado:** ningún resultado de DS00 u otro grupo se atribuye a Santa Elena. **Estado:** COMPROBADO en `data/raw/release_manifest.json` y Git.

## 2. Datos disponibles de exploración

**Qué hicimos:** inventariamos el release. **Por qué:** una interpretación depende de saber qué se observó. **Decisión:** conservar los archivos originales y sus unidades. **Parámetros:** tres campañas; datos de profundidad y XYZ en m; Cu/Mo en %, Au en g/t; densidad observada en t/m³. **Resultado:** 44 collars, 313 survey, 5803 ensayes, 120 intervalos litológicos, 459 densidades observadas y 0 intervalos de alteración. **Significado:** hay fuentes para estudiar geometría, soporte y categorías, pero no una propiedad de bloque automática. **Estado:** COMPROBADO con el manifiesto y el recuento de CSV. Fuente: `data/raw/release_manifest.json`, `data/raw/*.csv`, `docs/DATA.md`.

| Campaña | Sondajes | Survey | Ensayes | Litología | Densidad observada |
|---|---:|---:|---:|---:|---:|
| CAMPAIGN_01 | 16 | 113 | 2183 | 33 | 173 |
| CAMPAIGN_02 | 20 | 137 | 2620 | 64 | 206 |
| CAMPAIGN_03 | 8 | 63 | 1000 | 23 | 80 |

## 3. Sondajes

**Qué hicimos:** vinculamos collars y mediciones survey por `hole_id`. **Por qué:** el collar fija el inicio y survey registra los cambios de orientación con la profundidad. **Decisión:** mantener la identidad de cada sondaje y campaña. **Parámetros:** 44 sondajes y 313 estaciones survey. **Resultado:** el repositorio dispone de la geometría necesaria para ubicar intervalos; sus pruebas documentan 44/44 collars y 313/313 estaciones dentro de la malla. **Significado:** se puede mostrar dónde se muestreó sin confundir la trayectoria con un dominio geológico continuo. **Estado:** recuento COMPROBADO; cobertura espacial y pruebas DOCUMENTADAS en `docs/STATUS.md`.

## 4. Posicionamiento espacial

**Qué hicimos:** el proyecto calculó trayectorias e intervalos XYZ a partir de collar y survey. **Por qué:** un tramo medido por profundidad no tiene posición 3D sin esa transformación. **Decisión:** emplear la ruta de desurvey/posicionamiento M01 documentada y conservar el vínculo con el intervalo observado. **Parámetro:** coordenadas cartesianas locales en metros. **Resultado:** 120 intervalos litológicos posicionados y 76 contactos reportados; el HTML original dibuja sondajes e intervalos. **Significado:** la posición es un resultado geométrico derivado, no una medición directa de ley de bloque. **Estado:** DECISIÓN y verificación COMPUTACIONAL DOCUMENTADAS en `docs/implementation/IMP-004_m01b_geological_validation.md`; no se reejecutó el algoritmo en este piloto.

## 5. Compositado

**Qué hicimos:** transformamos ensayes en intervalos compósitos trazables. **Por qué:** comparar tramos de soporte parecido evita mezclar directamente longitudes de muestra diferentes. **Decisión:** ponderar Cu por longitud y separar códigos litológicos observados, preservando residuos. **Parámetro:** 2 m como longitud objetivo. **Resultado:** 5830 compósitos; 5750 completos y 80 residuales. El CSV incorporado conserva `source_sample_ids` y `residual_flag`. **Significado:** una ley de compósito describe el tramo correspondiente, no la ley de todo un bloque. **Estado:** conteos y SHA del CSV COMPROBADOS; regla y reproducción previa DOCUMENTADAS en `docs/exam/T2_M01B_PLAN_G05.md`.

## 6. Longitud seleccionada y ejemplo real

**Qué hicimos:** conservamos los contactos aunque interrumpan la longitud objetivo. **Por qué:** un contacto separa intervalos de códigos observados diferentes. **Decisión:** no mezclar OVB y VOL para completar 2 m. **Parámetro:** en `SE-C01-001`, contacto a profundidad 9 m. **Resultado:** el ensaye `SE-C01-001-A0005` va de 8 a 10 m; aparece en un compósito residual OVB de 8–9 m y contribuye también al compósito VOL de 9–11 m. **Significado:** 2 m es una meta de soporte, no una licencia para borrar límites ni inventar ensayes. **Estado:** COMPROBADO contra `data/raw/assay.csv`, `data/raw/lithology.csv` y [`datos/composites.csv`](datos/composites.csv). La ventana 8–13 m del visor es un **ejemplo**, no toda la campaña.

## 7. Geometría de bloques

**Qué hicimos:** construimos una malla cartesiana local. **Por qué:** las celdas permiten ordenar espacialmente las observaciones y sus estados. **Decisión:** 50 × 50 × 10 m para el alcance preliminar T2. **Parámetros:** origen local provisional `(242225, 8196250, 2990) m`; forma 15 × 14 × 55. **Resultado:** **11 550 bloques geométricos**, cada uno con índices y límites XYZ comprobados en [`datos/block_model_preliminary_geology_topography.csv`](datos/block_model_preliminary_geology_topography.csv). **Significado:** no es una malla optimizada ni una cubicación de roca. **Estado:** geometría COMPROBADA; fundamento horizontal DOCUMENTADO en `docs/STATUS.md` (medianas observadas próximas a 55 m). **Limitación:** la dimensión vertical de 10 m no tiene justificación formal suficiente y el origen no es una referencia oficial.

## 8. Topografía

**Qué hicimos:** integramos `Topopl.csv` mediante TIN lineal y clasificamos la posición vertical de los bloques usando una elevación en el centro XY de cada columna. **Por qué:** distinguir celdas bajo, sobre y cruzadas por la superficie. **Decisión:** estados `ROCK`, `AIR` y `PARTIAL` separados de la litología. **Parámetros:** 218 112 puntos fuente y 210 centros XY de la malla. **Resultado:** 6853 ROCK, 4493 AIR y 204 PARTIAL en el CSV integrado; el registro del equipo informa elevación finita en 210/210 centros. **Significado:** PARTIAL identifica cruce, **no** fracción volumétrica de roca. **Estado:** recuentos COMPROBADOS; método y cobertura DOCUMENTADOS en `docs/implementation/IMP-003_m01b_topography_integration.md`. **Limitación:** `Topopl.csv` no consta en el manifiesto original DS05/EXP03; procedencia oficial, CRS/EPSG y datum vertical no están acreditados.

## 9. Litología observada

**Qué hicimos:** ubicamos los intervalos litológicos y sus contactos. **Por qué:** son el soporte categórico observado que puede relacionarse con celdas. **Decisión:** conservar literalmente `OVB`, `BRX`, `POR`, `VOL` y `AIR`, sin expandir su significado. **Parámetros:** 120 intervalos y 76 contactos documentados. **Resultado:** el HTML original permite ver intervalos y contactos. **Significado:** `lith_code=AIR` y `topo_status=AIR` son campos distintos; un color no prueba continuidad entre sondajes. **Estado:** códigos y 120 filas COMPROBADOS; 76 contactos DOCUMENTADOS en `docs/implementation/IMP-004_m01b_geological_validation.md`. **Limitación:** falta diccionario litológico oficial.

## 10. Asignación preliminar

**Qué hicimos:** asignamos código al bloque solo cuando una intersección 3D positiva aporta un único código literal concordante. **Por qué:** evitar extrapolaciones y mayorías sin respaldo. **Decisión:** dejar conflictos y ausencia de soporte como `UNKNOWN/UNASSIGNED`. **Parámetros:** regla de intersección descrita en IMP-004. **Resultado:** 978 ASSIGNED (BRX 54, OVB 36, POR 463, VOL 425); 68 conflictos y 10 504 sin soporte, que suman 10 572 sin asignación. **Significado:** «sin asignar» significa que la regla no obtuvo soporte suficiente; no significa ley cero, lastre ni error automático del algoritmo. **Estado:** conteos COMPROBADOS en el CSV; método y revisión observacional DOCUMENTADOS. **Limitación:** no existe continuidad geológica validada entre sondajes.

## 11. Estimaciones cuantitativas

**Qué hicimos:** verificamos el alcance del modelo integrado. **Por qué:** una cifra ausente no debe parecer resultado. **Decisión:** no convertir observaciones de ensaye o densidad en propiedades de bloques sin método y soporte nuevos. **Parámetro:** el CSV integrado no contiene columnas de Cu/Mo/Au, densidad ni tonelaje de bloque. **Resultado:** **sin leyes, densidades ni tonelajes estimados por bloque** en este piloto. **Significado:** no hay base para inventario mineral cuantitativo, recursos o reservas. **Estado:** PENDIENTE; ausencia de columnas COMPROBADA. Las 459 densidades mencionadas arriba son **mediciones de muestra**.

## 12. Visualización

**Qué hicimos:** preservamos el HTML 3D integrado original G05, autocontenido, sin ejecutar código histórico. **Por qué:** permite observar la superficie, los bloques, sondajes, intervalos, contactos y una sección X–Z. **Decisión:** abrirlo bajo demanda debido a su tamaño cercano a 52 MB. Para la portada, aislamos las **44 trazas de sondaje y sus 313 puntos XYZ ya presentes en ese HTML**; no recalculamos desurvey. **Parámetros:** metadato original `block_count=11550`, `validation_claim=false`; trazas de `legendgroup=drillholes`. **Resultado:** [`visor/m01b_block_model_geology_topography.html`](visor/m01b_block_model_geology_topography.html) conserva el modelo integrado; [`visor/sondajes_3d.html`](visor/sondajes_3d.html) muestra solo las trayectorias en la primera pantalla. **Significado:** el HTML integrado incluye la malla completa, mientras la portada enfoca los sondajes observados y posicionados; ninguna de las dos vistas demuestra continuidad geológica. **Estado:** fuentes, IDs y puntos de trayectorias COMPROBADOS; el alcance de inspección visual queda en `VALIDACION.md`.

## 13. Limitaciones reales

**Qué hicimos:** mantenemos visibles las incertidumbres. **Por qué:** el modelo preliminar enseña tanto lo que se logró como lo que queda por demostrar. **Decisión:** no presentar validación computacional como certificación geológica o operacional. **Parámetros pendientes:** procedencia/CRS/datum de Topopl, significado oficial de códigos, fracción de roca en PARTIAL y soporte entre sondajes. **Resultado:** etiquetas de alcance en cada pantalla. **Significado:** ni los 41 PASS **reportados** por G05 ni la vista 3D prueban recursos, reservas o un plan de minado. **Estado:** LIMITACIÓN DOCUMENTADA en `docs/STATUS.md` e IMP-003/004; pruebas históricas no reejecutadas en la Fase 02.

## 14. Próximos productos de ingeniería

**Qué hicimos:** identificamos dependencias futuras sin construirlas. **Por qué:** el estudiante necesita saber cuál es el siguiente conocimiento exigible. **Decisión:** pedir primero confirmación documental de Topopl y diccionario de códigos; revisar alcance geométrico/topográfico y soporte geológico antes de cuantificar. **Parámetro:** ningún método de estimación, radio, variograma, ley de corte o densidad de bloque ha sido aprobado aquí para G05. **Resultado:** lista de pendientes visible en la pantalla «Estado actual». **Significado:** cualquier S11 cuantitativo o S12 grupal requerirá una decisión y validación propias, no copiar los resultados docentes DS00. **Estado:** PROPUESTA DE SECUENCIA, no decisión técnica histórica del grupo.

## Evidencia de integridad y procedencia

El manifiesto del release coincide con los ocho **blobs canónicos Git** de datos raw. En Windows, `core.autocrlf=true` cambia los bytes de fin de línea al clonar: por eso los SHA-256 del checkout pueden diferir aunque sus registros y el blob del commit correspondan. [`FUENTES_G05.json`](procedencia/FUENTES_G05.json) conserva ambos hashes. Los recuentos, índices, dimensiones y estados de los dos CSV derivados se comprobaron sobre el commit fijado; el HTML original incorporado coincide byte por byte con el HTML entregado localmente por el grupo en `MODELO DE BLOQUES 3D.zip`.

## Lectura de decisiones R4

Las tarjetas de `index.html#decisiones` separan: decisión o registro del grupo, consecuencia técnica, método profesional (información, alternativas, criterio y comprobación) y significado para este proyecto. El método profesional es un refuerzo general; no se atribuye como justificación del estudiante. Los datos y estados anteriores se conservan.
