"""
transformation.py — Módulo de transformaciones y preparación de datos para exportación.

Contiene:
- Cálculo de participación regional
- Preparación de DataFrames para exportar a CSV
- Diccionario de traducción de nombres de regiones
"""

import numpy as np
import pandas as pd
from src.analysis import tendencia


# ─────────────────────────────────────────────
# Diccionario de traducción de regiones
# (para compatibilidad con archivos GeoJSON y exportación)
# ─────────────────────────────────────────────

TRANS_REG = {
    'Del libertador general bernardo ohiggins': "Libertador General Bernardo O'Higgins",
    'Del maule': 'Maule',
    'Del biobío': 'Bío-Bío',
    'La araucanía': 'La Araucanía',
    'Aysén del general carlos ibáñez del campo': 'Aisén del General Carlos Ibáñez del Campo',
    'Magallanes y la antártica chilena': 'Magallanes y Antártica Chilena',
    'Metropolitana santiago': 'Región Metropolitana de Santiago',
    'Los ríos': 'Los Ríos',
    'Arica y parinacota': 'Arica y Parinacota',
    'Ñuble': 'Ñuble'
}


# ─────────────────────────────────────────────
# Funciones de transformación
# ─────────────────────────────────────────────

def calcular_participacion_regional(df_final):
    """
    Calcula el porcentaje de participación de cada región en el PIB total
    por año, y determina la tendencia (alcista/bajista).

    Parámetros
    ----------
    df_final : pd.DataFrame
        DataFrame consolidado con datos regionales (incluyendo Titulo == "PIB").

    Retorna
    -------
    pd.DataFrame
        DataFrame con participación porcentual por año y columna Tendencia.
    """
    temp = df_final[df_final["Titulo"] == "PIB"]
    temp_values = (temp["value"] / temp.groupby("Date")["value"].transform('sum') * 100).round(2)
    num_id = df_final.Región.unique().shape[0] - 1
    num_col = 12

    participacion_reg = pd.DataFrame(
        index=df_final.Región.unique()[1:],
        columns=range(2013, 2025),
        data=temp_values.values.reshape(num_id, num_col)
    )
    participacion_reg["Tendencia"] = pd.cut(
        participacion_reg.apply(tendencia, axis=1),
        bins=[-np.inf, 0, np.inf],
        labels=["Bajista", "Alcista"]
    )
    return participacion_reg


def preparar_exportacion_pib(df_final, trans_reg=None):
    """
    Prepara el DataFrame de PIB para exportación a CSV.

    Parámetros
    ----------
    df_final : pd.DataFrame
        DataFrame consolidado con datos regionales.
    trans_reg : dict, optional
        Diccionario de traducción de regiones. Si es None, usa TRANS_REG.

    Retorna
    -------
    pd.DataFrame
        DataFrame listo para exportar con nombres de regiones traducidos.
    """
    if trans_reg is None:
        trans_reg = TRANS_REG
    df_pib_export = df_final[df_final["Titulo"] == "PIB"].copy()
    df_pib_export["Región"] = df_pib_export["Región"].replace(trans_reg)
    return df_pib_export


def preparar_exportacion_servicios(df_final, trans_reg=None):
    """
    Prepara el DataFrame de servicios (sectores) para exportación a CSV.

    Parámetros
    ----------
    df_final : pd.DataFrame
        DataFrame consolidado con datos regionales.
    trans_reg : dict, optional
        Diccionario de traducción de regiones.

    Retorna
    -------
    pd.DataFrame
        DataFrame listo para exportar.
    """
    if trans_reg is None:
        trans_reg = TRANS_REG
    df_serv_export = df_final[df_final.Región.isna() == False].copy()
    df_serv_export = df_serv_export[df_serv_export["Titulo"] != "PIB"]
    df_serv_export.Titulo = df_serv_export.Titulo.str.replace("PIB ", "")
    df_serv_export["Región"] = df_serv_export["Región"].replace(trans_reg)
    return df_serv_export


def preparar_exportacion_tendencias(list_tendencia, trans_reg=None):
    """
    Prepara el DataFrame de tendencias sectoriales para exportación a CSV.

    Parámetros
    ----------
    list_tendencia : list
        Lista de resultados de proyeccion_sector_alcista por región.
    trans_reg : dict, optional
        Diccionario de traducción de regiones.

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas: Región, serv_actual, serv_tendencia, years.
    """
    if trans_reg is None:
        trans_reg = TRANS_REG
    df_tendencia_export = pd.DataFrame(
        list_tendencia,
        columns=["Región", "serv_actual", "serv_tendencia", "years"]
    )
    df_tendencia_export.serv_actual = df_tendencia_export.serv_actual.str.replace("PIB ", "")
    df_tendencia_export.serv_tendencia = df_tendencia_export.serv_tendencia.str.replace("PIB ", "")
    df_tendencia_export["Región"] = df_tendencia_export["Región"].replace(trans_reg)
    return df_tendencia_export
