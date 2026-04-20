# 📊 Análisis Económico Regional de Chile — Datos Banco Central

## Descripción
Este proyecto tiene como objetivo analizar datos financieros y económicos utilizando un flujo de trabajo modular y profesional. Se utilizaron datos del banco central de chile a travez de su API. En el se realizaron analisis de datos anuales y trimestrales, ademas de un analisis de contribución porcentual de los sectores economicos al PIB regional. Analisis COVID, correlacion con generacion de electricidad, tendencia de actividad economica y series de tiempo. 
Para más detalles consultar [Resumen](Resumen/ReadMe.md)

## Estructura del Proyecto
- `data/`: Datasets crudos y procesados.
- `Resumen/`: Resumen de los analisis realizados (Tablas y dashboard en Power BI).
- `notebooks/`: Jupyter Notebooks para Análisis Exploratorio de Datos (EDA).
- `src/`: Código fuente modular (limpieza, transformación, análisis, descarga).
- `main.py`: Orquestador principal del flujo.
- `requirements.txt`: Dependencias del proyecto.

## Herramientas
Python | Pandas | Numpy | scipy | statsmodels |Matplotlib | Seaborn | Scikit-learn | Git | Docker | Power BI

## Cómo ejecutar

### Opción A: Ejecución Local
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar el orquestador: `python main.py`

### Opción B: Ejecución con Docker (Recomendado)
Si tienes Docker instalado, no necesitas instalar librerías localmente:
1. Construir la imagen: `docker compose build`
2. Ejecutar el proyecto: `docker compose up`

Este método asegura que el entorno de ejecución sea idéntico al desarrollo.

## Hallazgos Principales
- Identificacion de regiones alcista y bajistas en cuanto a contribucion al PIB nacional.
- Prediccion de la actividad economica dominante en el futuro en algunas regiones (Los lagos: servicios personales -> 3 años aprox -> manufacturero) 
- Estudio del impacto del COVID en el PIB.
- Serie de tiempo con ARIMA y SARIMA, este ultimo con un error del 9%
- Modelo lineal para la prediccion del PIB por volumen con un error del 7.4%, para la region de Antofagasta.
