# Modelo preliminar de bloques de reservas ACADÉMICO

S11 fuente `4cc61d4696212e9928cc`; S12 `c1b396f1482e4ee1d39d`.

Mineral candidato: 5278735.095685 t; desmonte candidato: 5789384.828962 t. Período: 22 días; asignados 66000.000000 t de mineral y 44000.000000 t de desmonte.

## Vínculo verificable por bloque

G05-ALLOC-01, regla académica nueva, explícita y versionada: cada clase participa proporcionalmente a su tonelaje. Mineral se limita al menor entre inventario, capacidad de planta y objetivo presupuestario de mineral. Desmonte se limita a su inventario y al remanente presupuestario. No se suplen déficits de una clase con otra. Fracción asignada = toneladas objetivo alcanzables de la clase / inventario de la clase; cada bloque conserva su remanente. Es una asignación de inventario fraccionaria para comparar capacidades, no una secuencia de extracción ni un porcentaje de reservas recuperables. Las 23 100 relaciones bloque/escenario incluyen también exclusiones con asignación nula. El CSV conserva costos variables por bloque y reparto contable del CAPEX.

## A/B

|Escenario|Productividad t/camión/día|Camiones meta|CAPEX USD|OPEX USD/período|
|---|---:|---:|---:|---:|
|A|870.400|6|2700000.00|1001000.00|
|B|652.800|8|3600000.00|1001000.00|

El cambio de ciclo modifica productividad y flota. Las tasas OPEX permanecen iguales: no se inventa un consumo de combustible diferente. CAPEX corresponde a camiones para la meta PT-01; no es inversión total del proyecto. Los costos se aplican a toneladas asignadas, no al inventario completo. La comparación favorece A en adquisición bajo esos supuestos; no demuestra rentabilidad ni acceso a esos bloques.

## Límites

- Litología preliminar; continuidad entre sondajes no demostrada.
- Estimación en centro como proxy académico; soporte volumétrico no corregido.
- CRS/datum topográfico no documentados; compatibilidad local heredada como supuesto.
- Incertidumbre de estimación no cuantificada por IDW².
- Sin pit, accesos, precedencias, secuencia, recuperación ni rentabilidad modelados.
- Asignación proporcional de inventario por clase; no identifica bloques físicamente extraíbles en el período.
