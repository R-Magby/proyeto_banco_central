"""
data_loader.py — Módulo de carga de datos desde la API del Banco Central de Chile.

Contiene:
- Conexión a la API via bcchapi
- Descarga masiva de series regionales
- Constantes con los nombres de las series disponibles
"""

import bcchapi
import requests
import pandas as pd


# ─────────────────────────────────────────────
# Constantes: Listas de búsqueda de series
# ─────────────────────────────────────────────

LISTA_DATASET = ["Tasa de desocupación, ", 'Empleo: ']
LISTA_ELECTRICIDAD = ['Generación eléctrica, MWh; ', 'Distribución eléctrica, MWh;']
LISTA_TURISMO = ["Encuesta mensual de alojamiento turístico (EMAT)"]
LISTA_SERVICIOS_QUAR = [", volumen a precios del año anterior encadenado, referencia 2018 (miles de millones de pesos encadenados)"]
LISTA_SERVICIOS_ANUALES = [' precios corrientes, base 2018']
LISTA_EMPRESA = ['Región de Arica y Parinacota, Número de constituciones en registro de empresas y sociedades a nivel regional; mensual;  cantidad; MINECON']
LISTA_CC = {
    'Saldo promedio de cuentas corrientes de personas naturales en moneda extranjera;',
    'Saldo promedio de cuentas corrientes de personas naturales en moneda nacional;',
    'Número de cuentas corrientes de personas naturales en moneda extranjera; ',
    'Número de cuentas corrientes de personas naturales en moneda nacional;'
}


# ─────────────────────────────────────────────
# Funciones de conexión y carga
# ─────────────────────────────────────────────

def conectar_api(file="user.txt"):
    """
    Inicializa la conexión con la API del Banco Central usando bcchapi.

    Parámetros
    ----------
    file : str
        Ruta al archivo con las credenciales (email en línea 1, password en línea 2).

    Retorna
    -------
    bcchapi.Siete
        Objeto de conexión a la API.
    """
    siete = bcchapi.Siete(file=file)
    return siete


def buscar_series(siete, termino):
    """
    Busca series disponibles en la API del Banco Central.

    Parámetros
    ----------
    siete : bcchapi.Siete
        Objeto de conexión a la API.
    termino : str
        Término de búsqueda.

    Retorna
    -------
    pd.DataFrame
        DataFrame con las series encontradas.
    """
    return siete.buscar(termino)


def _leer_credenciales(file="user.txt"):
    """
    Lee las credenciales desde el archivo user.txt.

    Retorna
    -------
    tuple
        (email, password)
    """
    with open(file, 'r') as f:
        lines = f.read().strip().split('\n')
    return lines[0].strip(), lines[1].strip()


def datos_regionales(df_servicios_per_region, file_credenciales="user.txt"):
    """
    Descarga los datos de cada serie regional desde la API REST del Banco Central.

    Esta función itera sobre cada seriesId del DataFrame de búsqueda y descarga
    los datos observados, agregando las columnas Titulo y Región.

    Parámetros
    ----------
    df_servicios_per_region : pd.DataFrame
        DataFrame resultado de buscar_series + ajuste_df_serie, con columnas
        'seriesId', 'Titulo', 'Región'.
    file_credenciales : str
        Ruta al archivo con credenciales (user.txt).

    Retorna
    -------
    pd.DataFrame
        DataFrame consolidado con columnas: Date, value, Titulo, Región.
    """
    user, password = _leer_credenciales(file_credenciales)

    dfs_serv_reg = []
    url = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
    df_temp = df_servicios_per_region.reset_index()

    for idx, serie in enumerate(df_temp.seriesId.values):
        params = {
            "user": user,
            "pass": password,
            "function": "GetSeries",
            "timeseries": serie,
            "firstdate": "2000-01-01",
            "lastdate": "2026-01-01"
        }
        response = requests.get(url, params=params).json()

        try:
            df = pd.DataFrame(response["Series"]["Obs"])
            df["Titulo"] = df_temp["Titulo"][idx]
            df['Región'] = df_temp["Región"][idx]
            dfs_serv_reg.append(df)
        except:
            print(f"Error en serie {serie}")

    df_final = pd.concat(dfs_serv_reg)

    df_final["Región"] = df_final['Región'].str.strip()
    df_final["Región"] = df_final['Región'].str.capitalize()
    df_final["value"] = df_final["value"].astype(float)
    df_final['indexDateString'] = pd.to_datetime(df_final['indexDateString'])
    df_final.rename(columns={'indexDateString': 'Date'}, inplace=True)

    return df_final


    return df_final


def datos_regionales_quartely(df_per_region, tipo, file_credenciales="user.txt"):
    """
    Descarga los datos de cada serie trimestral desde la API REST del Banco Central.
    Filtra por id_tipo y setea un tiempo hasta julio de 2027.
    """
    user, password = _leer_credenciales(file_credenciales)
    dfs_serv_reg = []
    
    df_temp = df_per_region[df_per_region["id_tipo"] == tipo]
    df_temp = df_temp.reset_index()
    url = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
    
    if "Tipo" in df_per_region.columns and len(df_per_region[df_per_region["id_tipo"] == tipo]["Tipo"].unique()) > 0:
        tipo_selecionado = df_per_region[df_per_region["id_tipo"] == tipo]["Tipo"].unique()[0]
        print(f"El tipo de PIB que se eligio fue {tipo_selecionado}")
    
    for idx, serie in enumerate(df_temp.seriesId.values):
        params = {
            "user": user,
            "pass": password,
            "function": "GetSeries",
            "timeseries": serie,
            "firstdate": "2000-01-01",
            "lastdate": "2027-07-01"
        }
        response = requests.get(url, params=params).json()

        try:
            df = pd.DataFrame(response["Series"]["Obs"])
            df["Titulo"] = df_temp["Titulo"][idx]
            df['Región'] = df_temp["Región"][idx]
            dfs_serv_reg.append(df)
        except Exception as e:
            print(f"Error en serie {serie}: {e}")
            
    if len(dfs_serv_reg) == 0:
        return pd.DataFrame()
        
    df_final = pd.concat(dfs_serv_reg)
    df_final["Región"] = df_final['Región'].str.strip()
    df_final["Región"] = df_final['Región'].str.capitalize()
    df_final["value"] = df_final["value"].astype(float)
    df_final['indexDateString'] = pd.to_datetime(df_final['indexDateString'])
    df_final.rename(columns={'indexDateString': 'Date'}, inplace=True)
    return df_final
