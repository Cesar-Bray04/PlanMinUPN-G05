# IMP-008 · Cuantificación G05 y recorrido hasta S12

**Fecha:** 14 de noviembre de 2026. **Grupo:** G05 Santa Elena, DS05/EXP03. **Responsable del encargo:** DD. **Implementación:** Kai operativo. **Estado:** VALIDATED en integración local, cálculo, pruebas Windows y Chrome/WebGL; pendiente aceptación pedagógica con estudiantes reales. No se declara CLOSED ni se hizo commit, push, merge o publicación.

## Actualización de integración local

Se integró sobre el checkout vigente conservando los cambios válidos de R6/IMP-006/IMP-007. El diagnóstico identificó el agente ausente en la extracción raíz; se reparó desde el ZIP verificado. Se corrigieron handles SQLite y fixtures de bloqueo Windows, se configuró el intérprete del proyecto, se completaron volumen/remanente/costos en el inspector y se regeneró la entrega grupal. **127 pruebas completas aprobadas sin exclusiones** y **17 pruebas de modelos finales aprobadas**; Chrome real comprobó carga, propiedades, consulta por ID, filtros y giro. Generaciones finales S11 `4cc61d4696212e9928cc` y S12 `c1b396f1482e4ee1d39d`, ambas VALIDATED.

El detalle, secuencia real de correcciones, archivos afectados, respaldos, comandos, entorno y límites están en [Integración local IMP-008](../INTEGRACION_LOCAL_IMP008_20261114.md) y `outputs/audit_g05/verificacion_final.json`. `.kai_local`, raw, preliminares, plantillas originales y parámetros numéricos se contrastan con el respaldo previo. El ensayo de Copilot/PyCharm se separa de aceptación humana.

**Las secciones siguientes conservan la construcción y auditoría originales del paquete. Las menciones de D: no accesible y Windows/navegador NOT RUN pertenecen a esa ejecución anterior Linux y quedan actualizadas por el corte local anterior.**

## Problema y objetivo

R6, IMP-006 e IMP-007 disponían de teoría, registro conceptual, visor preliminar y ficha individual E1. Faltaba la ejecución cuantitativa G05 y la conexión verificable entre bloques y escenarios. Esta implementación produce un modelo de bloques de recursos ACADÉMICO en S11 y un modelo preliminar de bloques de reservas ACADÉMICO en S12, con evidencia individual diferenciada del producto grupal.

## Corte y preflight

Se leyó primero el relevo adjunto y luego el informe de recuperación. Se obtuvieron los paquetes R6, IMP-006, IMP-007 y la plantilla individual vigente. Sus manifiestos permiten ensamblarlos sin conflictos en una copia aislada. La plantilla independiente coincide por SHA-256 con la última incluida en IMP-007: `278b81c4017afa315c89470e70edb7870e413b01837c4e7f4cf935f0e191a088`.

El repositorio público fuente `Cesar-Bray04/PlanMinUPN-G05`, rama `feature/m01b-block-model`, permanece en `7825c2110a111193eb8e069c6358baa0dca0eb3e`: árbol de 93 entradas sin módulos Kai/S11/S12. Los ZIP no contienen `.git`. La rama local `codex/kai-g05-teoria-s11-s12` y sus cambios sin commit fueron reportados por DD y no pudieron verificarse aquí. No se accedió a D:. La aplicación parcial de IMP-007 en ese equipo sigue sin acreditarse; se verificó el contenido de los paquetes, no el estado del disco de DD.

Se conservaron las fuentes originales en una referencia separada. El instalador compara todos los archivos antes de escribir, rechaza diferencias locales no reconocidas, respalda los archivos que sustituye y no accede a `.kai_local`. El índice aprobado distinto de los hashes conocidos debe conciliarse con el corte actual, no reemplazarse.

## Inputs y controles

| Entrada | Unidad y origen | Control |
| --- | --- | --- |
| Collar 44 y survey 313 | XYZ m; profundidad m; ángulos grados, raw G05 | Manifiesto, claves, finitud, M01; desurvey sin extrapolación |
| Ensayes 5803 | Cu/Mo %, Au g/t | Identidad, intervalos, cobertura y ponderación por longitud |
| Compósitos 5830 | XYZ m; objetivo 2 m | XYZ reproducido; Cu conciliado; 5750 completos y 80 residuales preservados |
| Litología 120 intervalos | Códigos literales, raw | Contactos y pertenencia íntegra; no expandir códigos ni acreditar continuidad |
| Densidad 459 | t/m³, raw sin XYZ | Posicionamiento M01; identidad; valor positivo; excluir contacto ambiguo y dominios excluidos |
| Malla 11550 | 50 × 50 × 10 m; índices 15 × 14 × 55 | Identidad única, origen, centros y límites geométricos |
| Topografía 218112 puntos | XYZ locales, Topopl.csv | Finitud, unicidad XY, triangulación trasladada, área cubierta e integración |
| PT-01 | Radios, soporte, corte, capacidades y tasas | Parámetros numéricos conservados; estado de ejecución consultado dinámicamente |

Los datos raw se cotejan contra el manifiesto normalizando exclusivamente CRLF/LF. Los productos registran además los hashes físicos de todas sus entradas y módulos. Si cambia una fuente o una salida, dejan de estar verificados hasta su reproducción.

## Lógica y supuestos S11

- IDW² en el centro de la celda, usado como proxy académico de bloque. No se demuestra una ley media volumétrica corregida por soporte.
- Ley: radio 75 m, máximo 12 compósitos completos de 2 m, mínimo 3 y 2 sondajes. Sensibilidad a 50 m con las demás reglas constantes. Los residuales permanecen en QA.
- No se eligen simultáneamente dos compósitos que compartan ensayo de origen. Se conservan IDs de compósitos y ensayes, distancias, pesos y número de sondajes.
- Mo y Au se reconstruyen por longitud desde las muestras originales de cada compósito. Se reproduce Cu para comprobar la unión. Un faltante no se transforma en cero.
- Densidad: IDW², radio 100 m, máximo 8, mínimo 2 muestras. Cada medición se ubica por desurvey/posicionamiento existente y debe estar íntegramente dentro de una unidad. Se utilizan 443 de las 459 observaciones.
- Restricción geológica: igualdad literal de código preliminar; no representa un sólido ni continuidad validados. AIR y OVB se excluyen según PT-01. Los estados heredados se conservan.
- Volumen: trasladar XY a un origen local antes de Delaunay; recortar cada triángulo a la huella XY y a los límites Z; integrar analíticamente el volumen bajo el plano lineal. Se obtienen fracción y volumen de roca, sin equiparar PARTIAL a la caja completa.
- Tonelaje: volumen de roca por densidad respaldada. Si falta cualquiera, queda ausente y con causa. El tonelaje con densidad sola se presenta separado del que además tiene Cu.

La compatibilidad de coordenadas locales es un supuesto académico heredado. CRS y datum topográfico siguen sin documentarse. La integración precisa bajo el TIN no acredita la referencia de ese TIN.

## Resultado S11 ejecutado

| Medida | Resultado |
| --- | ---: |
| Cu estimado, radio 75 m | 168 bloques |
| Cu estimado, radio 50 m | 165 bloques |
| Densidad estimada | 942 bloques |
| Tonelaje con densidad y volumen | 62 917 363,048567 t |
| Bloques con Cu y tonelaje | 168 |
| Tonelaje con Cu, densidad y volumen | 11 068 119,924647 t |
| Estado volumétrico FULL_ROCK_TIN | 6547 |
| PARTIAL_ROCK_TIN | 806 |
| AIR_TIN | 4197 |

Los estados volumétricos nuevos no reescriben ROCK/AIR/PARTIAL de E1. Las 210 huellas cierran en 2500 m²; error máximo de área `9.094947017729282e-13 m²`.

## Lógica y supuestos S12

Se lee exclusivamente una generación S11 validada y se conserva su identificador. Un bloque debe tener dominio preliminar asignado, topografía y volumen admisibles, Cu y densidad respaldados y tonelaje positivo. Solo entonces se aplica el corte académico de 0,50 % Cu. Se generan `ORE_CANDIDATE`, `WASTE_CANDIDATE` o `UNCLASSIFIED`, con causas. El campo de clasificación profesional queda `NOT_ASSIGNED`.

**DECISION G05-ALLOC-01.** PT-01 no fijaba la conexión de bloques con A/B. Se añadió una regla académica explícita: asignación proporcional al tonelaje dentro de cada clase, con objetivos de hasta 66000 t de mineral y 44000 t de desmonte por 22 días, limitados por el inventario de cada clase. No se reemplaza el déficit de una clase con otra. Cada bloque tiene fracción, toneladas asignadas, remanente y costos por escenario. Es una participación fraccionaria de inventario, no orden de extracción ni accesibilidad inferidos. Esta decisión está versionada en `kai/politicas_cuantificacion_g05_v1.json` y no cambia los parámetros PT-01.

Se calculan productividad de camión con carga, ciclo y horas efectivas; flota entera redondeada hacia arriba para 5000 t/d; capacidad efectiva; CAPEX de camiones; OPEX de minado y generales sobre toneladas movidas y proceso sobre mineral procesado. No se vuelve a aplicar disponibilidad/utilización a una capacidad que ya las incorpora. El CAPEX por bloque es solo reparto contable proporcional, sin valorización ni rentabilidad de bloque.

## Resultado S12 ejecutado

| Medida | Resultado |
| --- | ---: |
| Mineral candidato | 80 bloques; 5 278 735,095685 t |
| Desmonte candidato | 88 bloques; 5 789 384,828962 t |
| Sin clasificación | 11382 bloques |
| Relaciones bloque/escenario | 23100 |
| Movimiento asignado del período | 110000 t |
| Tratamiento asignado del período | 66000 t |

| Escenario | Ciclo min | t/camión/día | Camiones meta | CAPEX USD | OPEX USD/22 días |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 30 | 870,4 | 6 | 2700000 | 1001000 |
| B | 40 | 652,8 | 8 | 3600000 | 1001000 |

Las mismas tasas y toneladas producen igual OPEX; no se inventa una diferencia de combustible. El CAPEX difiere en USD 900000. Se conservan inventario, parámetros y denominadores de período. No se modelan ingresos, recuperación, pit, accesos, precedencias o secuencia.

## Arquitectura y archivos

`src/missions/sources.py` valida y posiciona; `estimation.py` estima; `volume.py` integra; `scenarios.py` conecta inventario y escenarios; `products.py` publica generaciones y comprueba hashes; `viewer.py` produce HTML; `g05.py` orquesta. Los derivados son inmutables por identificador de entradas y código; el puntero selecciona la generación vigente. Una nueva generación S11 invalida la asociación anterior con S12.

`kai/recorrido_g05.py` coordina la secuencia y reutiliza V2. `kai/aplicacion_g05.py` registra 26 observaciones numéricas verificadas, trece por misión, en SQLite/Excel V3 por alias y corrida. La plantilla V3 se creó y renderizó con Artifact Tool. El escritor de ejecución conserva el mecanismo OOXML sin dependencias externas del registro existente. El alumno aporta valor y unidad; se rechaza un valor correcto que no esté presente en su respuesta literal. Los intentos errados se conservan sin llenar la celda. El bloqueo de Excel deja SQLite como fuente canónica.

`index.html#s11` y `#s12` integran los visores; `#teoria` mantiene la guía aprobada. E1 conserva su corte, su ficha de 21 campos y el cierre previo a S11. Los visores nuevos ofrecen Cu/Mo/Au, densidad, toneladas, fracción de roca, soporte, sensibilidad, candidatos y asignación/costos A/B. El CSV íntegro contiene todas las celdas; el dibujo limita contexto a 6000 cajas y lo indica.

Se actualizan el perfil de agente, el inicio, las preguntas situadas en S11/S12 y el estado dinámico. La metadata estática `PREVISTA_NO_EJECUTADA` de los parámetros se conserva en un archivo histórico; la fuente activa remite al manifiesto verificado en vez de declarar un booleano de ejecución. Los parámetros numéricos permanecen iguales.

La lista exacta de archivos y hashes figura en `MANIFIESTO_INTEGRACION_G05.json`. No se modificaron raw, modelos/compósitos preliminares, gobernanza protegida ni scripts V1. No se empaquetan historiales personales.

## Etapas reales de implementación

1. Lectura del relevo y fuentes, comparación de paquetes e inspección del árbol GitHub.
2. Ensamblaje aislado por hashes y pruebas iniciales: nueve casos manuales/límite pasaron. La regresión inicial identificó dos fallos heredados por fixtures de bloqueo Windows ausentes.
3. Implementación de procedencia multielemento y densidad posicionada; corrección de un error inicial de construcción de diccionario.
4. Implementación de integración TIN y primera cuantificación. Su control de área detectó superposiciones numéricas; no se aceptaron esos tonelajes como definitivos.
5. Experimento global/local de triangulación: corrección trasladando XY antes de Qhull; nueva corrida y conciliación completa de huellas.
6. Cálculo S12 y vínculo contable por bloque; integración en el índice y código del visor.
7. Plantilla y controlador individual; ensayo automático de secuencia, error, retorno, bloqueo simulado y preservación de historia PT-01. Se mejoró la reutilización del catálogo conservando verificación de integridad antes de usarlo.
8. Verificación independiente de todos los Cu elegibles, densidad, cuadratura de volúmenes y balances por bloque; pruebas del contrato JavaScript; preparación del instalador con guardas y respaldos.

## Verificación y evidencia

La verificación final, comandos, conteos y estados se registran en `outputs/audit_g05/verificacion_final.json` y en el informe de entrega. Se ejecutaron casos manuales Cu 0,60 %, densidad 2,64 t/m³ y volumen de plano inclinado; bordes de radio; mínimos y sondajes; coincidencias; duplicación de ensayo; faltantes; invariancia de volumen ante traslación XY; contraste con cuadratura; inventario insuficiente; corte sin soporte; modificación de fuentes y salidas; balances de movimiento, tratamiento, OPEX y CAPEX; protocolo y Excel; guardas de integración.

La prueba JS usa DOM y Plotly simulados: comprueba datos, mallas finitas, propiedades, filtros y consulta por ID, pero no apariencia, WebGL ni hover real. La política del navegador remoto rechazó `file:` y se detuvo esa inspección; no se eludió. La conversación real en Copilot/PyCharm y el bloqueo real de Excel en Windows son **NOT RUN**. El protocolo humano está en `docs/PROTOCOLO_HUMANO_KAI_G05_IMP008.md`.

## Hallazgo técnico y discusión conceptual

La triangulación heredada en coordenadas grandes produjo 270692 triángulos; con las mismas 218112 observaciones trasladadas a origen local, 436181. Se detectaron pequeñas superposiciones de área. La nueva integración cierra las huellas; sus centros difieren como máximo 0,698667 m del TIN heredado y cambian dos clasificaciones centrales. La implementación nueva conserva ambos estados y no modifica el modelo E1. Corresponde revisar por separado el condicionamiento numérico de M01, fuera de este cambio.

**Para discutir con el Kai principal:** G05-ALLOC-01 vuelve verificable el vínculo de bloques con capacidades y costos, pero su asignación fraccionaria es contable. No crea accesibilidad ni precedencias. Si el objetivo posterior requiere afirmar bloques extraíbles por período, hará falta una regla física adicional y sus datos. Esa ampliación conceptual no se resolvió silenciosamente asignando reservas a bloques sobre el corte.

## Uso de IA y pendientes

Kai se usó para auditar, formular reglas explícitas, implementar, probar, reconciliar y documentar. Las respuestas de los ensayos automáticos son fixtures, no evidencia de estudiantes reales. Faltan el corte actual para conciliar la integración y la aceptación visual/conversacional en el equipo de DD. Las fuentes, resultados y paquetes están preparados; no se solicita reconstruir el trabajo ni volver a planificar la cadena.
