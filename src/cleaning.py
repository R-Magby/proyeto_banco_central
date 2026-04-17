"""
cleaning.py — Módulo de limpieza de datos.

Contiene funciones para:
- Ajuste de series (split de título y región)
- Limpieza de datos de PIB
- Limpieza de datos de electricidad
"""

import pandas as pd


def ajuste_df_serie(df_per_region):
    """
    Ajusta el DataFrame de búsqueda separando el 'spanishTitle' en
    columnas 'Titulo' y 'Región', y limpia ambos campos.

    Parámetros
    ----------
    df_per_region : pd.DataFrame
        DataFrame resultado de siete.buscar() con columna 'spanishTitle'.

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas adicionales 'Titulo' y 'Región' limpias.
    """
    df_temp = df_per_region.copy()
    df_temp[["Titulo", "Región"]] = df_temp.spanishTitle.str.split(" Región ", expand=True)
    df_temp['Región'] = df_temp['Región'].str.split(",", n=1, expand=True)[0]
    df_temp['Región'] = df_temp['Región'].str.replace("de ", "")
    df_temp['Región'] = df_temp['Región'].str.strip()

    df_temp['Titulo'] = df_temp['Titulo'].str.replace(",", "")
    df_temp['Titulo'] = df_temp['Titulo'].str.strip()
    return df_temp


def limpiar_datos_pib(df_final):
    """
    Limpia el DataFrame consolidado de datos PIB:
    - Elimina la columna 'statusCode'
    - Filtra filas donde Región no es NaN
    - Elimina filas con Titulo == "PIB" (para obtener solo sectores)
    - Resetea el índice

    Parámetros
    ----------
    df_final : pd.DataFrame
        DataFrame consolidado con datos regionales.

    Retorna
    -------
    pd.DataFrame
        DataFrame limpio con solo datos de servicios/sectores por región.
    """
    df_final = df_final.drop(columns=["statusCode"])
    df_final_servicios = df_final[df_final['Región'].isna() == False]
    df_final_servicios = df_final_servicios[df_final_servicios['Titulo'] != "PIB"]
    df_final_servicios = df_final_servicios.reset_index()
    return df_final_servicios


def limpiar_datos_electricidad(df):
    """
    Limpia el DataFrame de electricidad:
    - Elimina la columna 'statusCode'
    - Limpia la columna 'Región' separando por ';'

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de datos eléctricos sin limpiar.

    Retorna
    -------
    pd.DataFrame
        DataFrame de electricidad limpio.
    """
    df.drop(columns=["statusCode"], inplace=True)
    df["Región"] = df["Región"].str.split(";", n=1, expand=True)[0].rename("Región")
    return df
