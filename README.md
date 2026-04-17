# Proyecto de Análisis de Datos - Banco Central

## Descripción
Este proyecto tiene como objetivo analizar datos financieros y económicos utilizando un flujo de trabajo modular y profesional.

## Estructura del Proyecto
- `data/`: Datasets crudos y procesados.
- `notebooks/`: Jupyter Notebooks para Análisis Exploratorio de Datos (EDA).
- `src/`: Código fuente modular (limpieza, transformación, análisis).
- `main.py`: Orquestador principal del flujo.
- `requirements.txt`: Dependencias del proyecto.
- `bitacora.md`: Registro histórico de pasos y aprendizaje.

## Cómo ejecutar

### Opción A: Ejecución Local
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar el orquestador: `python main.py`

### Opción B: Ejecución con Docker (Recomendado)
Si tienes Docker instalado, no necesitas instalar librerías localmente:
1. Construir la imagen: `docker compose build`
2. Ejecutar el proyecto: `docker compose up`

Este método asegura que el entorno de ejecución sea idéntico al desarrollo.
