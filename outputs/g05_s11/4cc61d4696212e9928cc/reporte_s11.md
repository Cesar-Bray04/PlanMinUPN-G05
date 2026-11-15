# Modelo de bloques de recursos ACADÉMICO

Corrida `4cc61d4696212e9928cc`. G05 DS05/EXP03; 11 550 celdas.

Cu estimado: 168 bloques a 75 m; 165 a 50 m. Densidad estimada: 942. Tonelaje cuantificable: 62917363.048567 t en 942 bloques. Con Cu y tonelaje: 168 bloques, 11068119.924647 t.

## Trazabilidad

Ensayes originales → compósitos por longitud y contacto → IDW² por código preliminar. Mo y Au se reconstruyen desde ensayes; Cu se concilia con M01. Cada estimación conserva IDs, distancias, pesos y sondajes. Densidad usa desurvey M01 y mediciones íntegramente contenidas en un dominio. Residuales se preservan en QA. Volumen: recorte de TIN por huella y límites verticales; integración analítica de planos. Se conserva el estado topográfico antiguo por separado. Nulo no significa cero.

## Supuestos y límites

- Litología preliminar; continuidad entre sondajes no demostrada.
- Estimación en centro como proxy académico; soporte volumétrico no corregido.
- CRS/datum topográfico no documentados; compatibilidad local heredada como supuesto.
- Incertidumbre de estimación no cuantificada por IDW².

## Verificación

`s11_validation.json` contiene controles ejecutados. La comparación manual .60 % / 2.64 t/m³ es un microcaso PT-01, no un bloque G05. La tabla completa respalda los totales; el 3D reduce contexto si excede 6000 cajas.
