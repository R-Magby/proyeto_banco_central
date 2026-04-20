# Bitácora de Desarrollo - Proyecto Banco Central

Este archivo sirve como un registro detallado y pedagógico de todos los pasos realizados en la construcción y orquestación de este proyecto de análisis de datos.

## Introducción
El objetivo es transformar un código "versión 1" en un proyecto profesional, modular y organizado, siguiendo las mejores prácticas de ingeniería de software aplicadas a la ciencia de datos.

---

## Registro de Actividades

### [2026-04-16] 1. Inicialización de la Estructura del Proyecto
**Objetivo:** Crear la arquitectura de carpetas y archivos base para organizar el código, los datos y la documentación.

**Pasos realizados:**
- Se crearon las carpetas principales: `data/`, `notebooks/` y `src/`.
- Se inicializó el módulo `src` mediante un archivo `__init__.py`.
- Se crearon los archivos de código modular: `cleaning.py`, `transformation.py` y `analysis.py`.
- Se crearon los archivos de orquestación y configuración: `main.py`, `requirements.txt` y `README.md`.
- Se generó una estructura base en `main.py` para demostrar el concepto de orquestación.

**Justificación:**
- **`data/`**: Separa los datos brutos de los resultados procesados, asegurando la reproducibilidad.
- **`notebooks/`**: Espacio para experimentación rápida (EDA) sin ensuciar el código productivo.
- **`src/`**: Centraliza la lógica de negocio en módulos reutilizables.
- **`main.py`**: Actúa como el centro de control que coordina el flujo de trabajo (limpieza -> transformación -> análisis).
- **`requirements.txt`**: Vital para que otros puedan replicar tu entorno de trabajo.

---

## [v2.0.0] - 2026-04-20
### Actualización a Soporte Trimestral y CAGR
**Objetivo:** Integrar datos trimestrales y mejorar la precisión de los cálculos de crecimiento acumulado basándose en la nueva lógica de la versión 2 del notebook.

**Cambios realizados:**
- **Módulos `src` actualizados**: Se incorporó la lógica del PIB regional trimestral (`df_quartely`) y contribuciones porcentuales (`df_porc`).
- **Nuevas Funciones**:
    - `datos_regionales_quartely`: Descarga específica para series trimestrales con filtrado por tipo de PIB.
    - `ajuste_df_serie_quartely`: Procesamiento avanzado de títulos regionales trimestrales usando `OrdinalEncoder`.
    - `normalize_quarter_dates`: Estandarización de fechas para alineación entre PIB y Electricidad.
- **Refinamiento Estadístico**: Se actualizó `Analisis_PIB` para usar CAGR y se añadió soporte para correlación Pearson/Spearman dinámica.
- **Orquestación**: `main.py` ahora maneja los tres datasets principales (`df_anual`, `df_quartely`, `df_porc`).
- **Documentación**: Se actualizó exhaustivamente `Resumen/ReadMe.md` con los hallazgos de la v2.
