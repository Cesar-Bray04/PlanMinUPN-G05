# PlanMinUPN

## Kai G05 R6 en esta rama

Recorrido teórico implementado desde exploración hasta S11 y S12, reutilizando el piloto corregido R5.3.1. Abre [Inicio Kai R6](INICIO_KAI_R6.md) para usarlo, [el visor G05](index.html) para observar el modelo y [la guía visual](docs/guia_visual_estimacion.html) para estudiar.

La ruta V2 conserva continuidad local separada del historial V1. IMP-008 incorpora estimación IDW² G05, volumen bajo TIN y escenarios A/B, con productos S11/S12 verificados y aplicación individual de 26 observaciones separada de la ficha E1 de 21. Los datos y algoritmos preliminares permanecen intactos. Los candidatos académicos no acreditan reservas profesionales. Consulta el [registro IMP-008](docs/implementation/IMP-008_g05_recursos_reservas_academicos.md) y el [informe de integración local](docs/INTEGRACION_LOCAL_IMP008_20261114.md) para evidencia y límites; [IMP-005](docs/implementation/IMP-005_kai_teoria_s11_s12.md) conserva la historia de la etapa teórica.

Repositorio base del curso **Planeamiento de Minado — Ingeniería de Minas, UPN, 2026-2**.

Este repositorio es el baseline que los equipos de estudiantes utilizarán para desarrollar su proyecto de planeamiento minero con **Python + GitHub + PyCharm + agentes de Inteligencia Artificial**.

## Principio del curso

> **Primero minería. Después código.**
>
> La IA puede escribir código. El ingeniero debe saber qué código necesita, qué representa y si el resultado es correcto.

## Uso previsto

Cada equipo debe trabajar en su propio repositorio generado a partir de este baseline. El repositorio del equipo conserva la estructura, reglas de gobernanza y plantillas del curso, mientras que el grupo desarrolla progresivamente la lógica minera, los algoritmos, las pruebas y la documentación.

## Inicio rápido para estudiantes

1. Clonar el repositorio del grupo en PyCharm.
2. Crear y activar un entorno virtual de Python.
3. Activar GitHub Copilot y/o JetBrains AI Assistant.
4. En PyCharm, verificar que la regla `.aiassistant/rules/00_course_governance.md` esté configurada como **Always** en `Settings | Tools | AI Assistant | Rules`.
5. Iniciar la primera conversación con el agente usando:

```text
Antes de realizar cualquier cambio, lee completamente AGENTS.md y las reglas del proyecto.
Inspecciona la estructura actual del repositorio y explícame:
1. qué entiendes del proyecto;
2. cuál es tu rol como agente;
3. cuáles son las reglas que debes respetar;
4. cuál es el estado actual del repositorio.
No escribas código todavía.
```

## Regla de cierre de módulos

Un módulo **no está terminado** hasta que exista su registro técnico en:

```text
docs/implementation/IMP-XXX_nombre_del_modulo.md
```

El registro debe documentar el problema minero, inputs, unidades, supuestos, lógica, etapas de implementación, decisiones, archivos afectados, pruebas ejecutadas, validación minera, limitaciones y uso del agente.

## Gobernanza

Los archivos de gobernanza son administrados por el docente y no deben ser modificados por estudiantes sin autorización expresa:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/CODEOWNERS`
- `.aiassistant/rules/00_course_governance.md`
- `docs/templates/MODULE_IMPLEMENTATION_TEMPLATE.md`

---

**Docente:** Ing. Danny Daniel Valderrama Gutiérrez  
**Curso:** Planeamiento de Minado — MINN1508A  
**Periodo:** 2026-2
