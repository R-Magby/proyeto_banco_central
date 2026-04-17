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

**Justificación Pedagógica:**
- **`data/`**: Separa los datos brutos de los resultados procesados, asegurando la reproducibilidad.
- **`notebooks/`**: Espacio para experimentación rápida (EDA) sin ensuciar el código productivo.
- **`src/`**: Centraliza la lógica de negocio en módulos reutilizables.
- **`main.py`**: Actúa como el centro de control que coordina el flujo de trabajo (limpieza -> transformación -> análisis).
- **`requirements.txt`**: Vital para que otros puedan replicar tu entorno de trabajo.
