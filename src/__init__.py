"""
Paquete src — Módulos del proyecto de análisis económico regional de Chile.

Módulos disponibles:
- data_loader: Conexión API y descarga de datos
- cleaning: Limpieza y ajuste de DataFrames
- transformation: Transformaciones y preparación para exportación
- analysis: Funciones de análisis, COVID, correlación y modelos ARIMA/SARIMA

Nota: Algunos módulos requieren bcchapi y statsmodels.
      Instalar con: pip install -r requirements.txt
"""

# Importaciones que no dependen de paquetes externos pesados
from src.cleaning import (
    ajuste_df_serie,
    limpiar_datos_pib,
    limpiar_datos_electricidad,
)

from src.analysis import (
    tendencia,
    Analisis_PIB,
    proyeccion_sector_alcista,
    COVID_comparacion,
    correlacion_con_lag,
    comparativa_tendencia,
    modelo_ARIMA,
    modelo_SARIMA,
)

# Importaciones que requieren bcchapi (pueden fallar si no está instalado)
try:
    from src.data_loader import (
        conectar_api,
        buscar_series,
        datos_regionales,
        LISTA_SERVICIOS_ANUALES,
        LISTA_ELECTRICIDAD,
        LISTA_DATASET,
    )
except ImportError:
    print("Advertencia: bcchapi no está instalado. Instalar con: pip install bcchapi")

from src.transformation import (
    calcular_participacion_regional,
    preparar_exportacion_pib,
    preparar_exportacion_servicios,
    preparar_exportacion_tendencias,
    TRANS_REG,
)
