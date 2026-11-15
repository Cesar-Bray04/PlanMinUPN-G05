# Aprender con Kai · G05

Abre la carpeta en PyCharm y selecciona **Kai Planeamiento** en Copilot. Preséntate o usa tu alias para retomar. Kai te explica una idea, te indica qué mirar y espera una decisión con tu razón. Puedes decir «no sé» y trabajarla con su ayuda.

1. E1 termina en el modelo geológico preliminar. Kai cierra y espera antes de S11.
2. S11 compara visualmente los métodos y aplica IDW² sobre G05. Abre [Métodos y teoría](index.html#teoria) y luego [S11](index.html#s11).
3. S12 usa el S11 validado y relaciona cada bloque candidato con capacidades, flota y costos. Abre [S12](index.html#s12).

En cada visor pulsa «Cargar visor aquí», elige una propiedad y consulta un bloque. Gris conserva faltantes. Las cajas representan la malla; la ficha muestra la fracción de roca calculada bajo la topografía. La guía de métodos conserva ejemplos ilustrativos separados de los resultados del grupo.

Tus entregables individuales son la ficha E1 de 21 observaciones, la bitácora conceptual V2 y la aplicación S11/S12 de 26 observaciones. Tú dices lo observado; Kai comprueba valor y unidad antes de escribirlo. No necesitas llenar plantillas ni enviar capturas. Con el mismo alias puedes retomar; los historiales anteriores se conservan separados. Los productos técnicos del grupo son otros archivos.

## Para DD

IMP-008 quedó integrado y recalculado en `D:\PlanMinUPN_Integracion\Kai PL Min\PlanMinUPN_G05_Kai_Teoria_R6`, rama `codex/kai-g05-teoria-s11-s12`, HEAD `7825c2110a111193eb8e069c6358baa0dca0eb3e`. Se conservaron las modificaciones válidas previas y se respaldó el checkout antes de escribir. El diagnóstico y los respaldos están en [Integración local](docs/INTEGRACION_LOCAL_IMP008_20261114.md).

El controlador activo es `kai/recorrido_g05.py`. Los registros V1/V2 y ficha E1 continúan separados y compatibles. `MISION_S11.cmd` y `MISION_S12.cmd` ejecutan las misiones; `VERIFICAR_PRODUCTOS_G05.cmd` comprueba integridad. Usan primero `.venv\Scripts\python.exe`; si no existe, prueban `py -3.12`. Este checkout tiene un entorno Python 3.12.0 con las dependencias numéricas instaladas del equipo; el Python 3.11 global no las tiene. Configura PyCharm con `.venv\Scripts\python.exe`. No se hizo commit ni push.

Consulta [IMP-008](docs/implementation/IMP-008_g05_recursos_reservas_academicos.md) para resultados, supuestos y verificación. Las comprobaciones de Chrome/WebGL, Windows y Copilot/PyCharm se documentan por separado de la aceptación humana con estudiantes.
