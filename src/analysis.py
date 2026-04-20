"""
analysis.py — Módulo de funciones de análisis.

Contiene:
- Análisis descriptivo de PIB regional
- Análisis de tendencias sectoriales
- Comparación pre/post COVID
- Correlación PIB-Electricidad
- Modelos de series de tiempo (ARIMA, SARIMA)
"""

import numpy as np
import pandas as pd
from scipy.stats import linregress, shapiro, spearmanr, pearsonr
from statsmodels.tsa.stattools import adfuller, kpss, grangercausalitytests


# ─────────────────────────────────────────────
# Funciones auxiliares
# ─────────────────────────────────────────────

def tendencia(x):
    """Calcula la pendiente de una regresión lineal sobre la serie x."""
    return linregress(range(len(x)), x).slope


def tasa_crecimiento_promedio(serie):
    """Calcula la tasa de crecimiento promedio logarítmica de una serie."""
    tasas = np.log(serie / serie.shift(1)).dropna()
    return tasas.mean()


def años_de_espera(pib_principal, pib_sector, g_principal, g_sector):
    """
    Calcula cuántos años tardaría un sector en alcanzar al sector principal,
    dado que crece más rápido.

    Retorna None si el sector no crece más rápido que el principal.
    """
    if g_sector < g_principal:
        return None
    else:
        return np.log(pib_principal / pib_sector) / (g_sector - g_principal)


# ─────────────────────────────────────────────
# Análisis descriptivo de PIB
# ─────────────────────────────────────────────

def Analisis_PIB(df, region, postpre=None, fecha=None):
    """
    Realiza un análisis descriptivo del PIB por sector para una región dada.

    Calcula: crecimiento acumulado, tendencia, media y desviación estándar
    de la variación interanual, y un indicador de volatilidad.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame consolidado con datos regionales.
    region : str
        Nombre de la región a analizar.
    postpre : str, optional
        'post' para datos posteriores a fecha, 'pre' para anteriores.
    fecha : str, optional
        Fecha de corte en formato compatible con pandas (ej: '01-01-2020').

    Retorna
    -------
    tuple
        (df_descri, df_descriptivo, n) donde:
        - df_descri: DataFrame con métricas por sector
        - df_descriptivo: DataFrame con datos y variación interanual
        - n: número de períodos únicos
    """
    region = region.capitalize()
    region = region.strip()
    if region in df["Región"].unique():
        pass
    else:
        return print("Debes ingresar una region valida")
    df_descriptivo = df[df['Región'] == region]

    df_descriptivo = df_descriptivo.sort_values(['Titulo', 'Date'])
    df_descriptivo["variación interanual"] = (df_descriptivo.groupby("Titulo")["value"].pct_change() * 100).round(2)

    if postpre == "post":
        df_descriptivo_pp = df_descriptivo[df_descriptivo['Date'] > fecha]
    elif postpre == "pre":
        df_descriptivo_pp = df_descriptivo[df_descriptivo['Date'] < fecha]
    elif postpre == None:
        df_descriptivo_pp = df_descriptivo.copy()
    else:
        return print("Se tiene que ingresar 'post' o 'pre'. ")

    # Analisis
    df_descri = []

    n = df_descriptivo_pp["Date"].max().year - df_descriptivo_pp["Date"].min().year

    df_descri.append(df_descriptivo_pp.groupby("Titulo")["value"].apply(lambda x: ((x.iloc[-1] / (x.iloc[0] + 1e-6))**(1/n) - 1) * 100).rename('Crecimiento acumulado'))
    df_descri.append(df_descriptivo_pp.groupby("Titulo")["value"].apply(tendencia).rename('Tendencia (Var)'))
    df_descri.append(df_descriptivo_pp.dropna().groupby("Titulo")["variación interanual"].mean().rename('Media'))
    df_descri.append(df_descriptivo_pp.dropna().groupby("Titulo")["variación interanual"].std().rename('Std'))
    df_descri = pd.concat(df_descri, axis=1)
    df_descri["Volatilidad"] = df_descri["Std"] / (df_descri["Media"].abs() + 1e-6)
    return df_descri, df_descriptivo, n


# ─────────────────────────────────────────────
# Proyección de sectores alcistas
# ─────────────────────────────────────────────

def proyeccion_sector_alcista(df, region, pib="Historico"):
    """
    Identifica sectores que podrían desplazar al sector dominante de una región.

    Criterios:
    - ratio > 0.2: Descarta sectores irrelevantes en escala
    - crecimiento_acumulado_sector > crecimiento_acumulado_principal
    - tendencia_sector > tendencia_principal

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de servicios por región.
    region : str
        Nombre de la región a analizar.
    pib : str
        'Historico' usa promedio histórico, 'Ultimo' usa dato 2024.

    Retorna
    -------
    list
        Lista de [sector_actual, sector_alcista, años_estimados].
    """
    lista_alcista = []

    region = region.capitalize()
    region = region.strip()

    if region in df["Región"].unique():
        pass
    else:
        return print("Debes ingresar una region valida")

    df_descriptivo = df[df['Región'] == region]
    df_descriptivo = df_descriptivo[df_descriptivo["Titulo"] != "PIB"]
    if pib == "Historico":
        ratio = df_descriptivo.groupby("Titulo")["value"].mean()
        id_pib_principal = ratio.idxmax()

    elif pib == "Ultimo":
        ratio = df_descriptivo[df_descriptivo["Date"] == "01-01-2024"].set_index("Titulo")["value"]
        id_pib_principal = ratio.idxmax()

    else:
        print("Se debe elegir pib 'Historico' o 'Ultimo'.")

    pib_principal_mean = ratio.max()
    sectores_candidatos = ratio[ratio / pib_principal_mean > 0.2].index.tolist()

    # Crecimiento acumulado
    df_crecimiento = df_descriptivo.groupby("Titulo")["value"].apply(lambda x: (x.iloc[-1] / (x.iloc[0] + 1e-6) - 1) * 100).rename('Crecimiento acumulado')
    # Tendencia
    df_tendencia = df_descriptivo.groupby("Titulo")["value"].apply(tendencia).rename('Tendencia')
    # Condiciones
    for serv in sectores_candidatos:
        if df_crecimiento[id_pib_principal] < df_crecimiento[serv]:
            if df_tendencia[id_pib_principal] < df_tendencia[serv]:
                g_sector_1 = df_descriptivo.groupby("Titulo")["value"].apply(tasa_crecimiento_promedio)[id_pib_principal]
                g_sector_x = df_descriptivo.groupby("Titulo")["value"].apply(tasa_crecimiento_promedio)[serv]
                pib_sector_1 = df_descriptivo[df_descriptivo["Titulo"] == id_pib_principal]["value"].iloc[-1]
                pib_sector_x = df_descriptivo[df_descriptivo["Titulo"] == serv]["value"].iloc[-1]
                n = años_de_espera(pib_sector_1, pib_sector_x, g_sector_1, g_sector_x)
                if n > 1 and n < 30:
                    lista_alcista.append([id_pib_principal, serv, n])

    return lista_alcista


# ─────────────────────────────────────────────
# Análisis COVID
# ─────────────────────────────────────────────

def tendencia_labels(pre, post):
    """
    Clasifica el cambio de tendencia entre períodos pre y post.

    Retorna: 'Aceleracion', 'Desaceleracion', 'Quiebre estructural',
             'Recuperacion', 'Deterioro', o 'Mejora parcial'.
    """
    if pre > 0:
        if post > 0:
            if pre < post:
                return "Aceleracion"
            else:
                return "Desaceleracion"
        else:
            return "Quiebre estructural"
    else:
        if post < 0:
            if pre < post:
                return "Mejora parcial"
            else:
                return "Deterioro"
        else:
            return "Recuperacion"


def COVID_comparacion(df_pre, df_post, n_pre, n_post):
    """
    Compara métricas de un sector/región entre períodos pre y post COVID.

    Calcula: Diff CAGR, Estado del CAGR, Cambio en Tendencia,
    Cambio en Volatilidad, y Diff Media.

    Parámetros
    ----------
    df_pre : pd.DataFrame
        Resultado de Analisis_PIB para el período pre-COVID.
    df_post : pd.DataFrame
        Resultado de Analisis_PIB para el período post-COVID.
    n_pre : int
        Número de períodos pre-COVID.
    n_post : int
        Número de períodos post-COVID.

    Retorna
    -------
    pd.DataFrame
        DataFrame con las métricas de comparación.
    """
    df_postpre = ((df_post['Crecimiento acumulado'] ** (1 / n_post) - 1) - (df_pre['Crecimiento acumulado'] ** (1 / n_pre) - 1)).to_frame()
    df_postpre = df_postpre.rename(columns={"Crecimiento acumulado": "Diff CAGR"})
    df_postpre["Estado del CARG"] = pd.cut(
        df_postpre["Diff CAGR"],
        bins=[-np.inf, -0.2, 0.2, np.inf],
        labels=["Deterioro", "Estancado", "Fortalecido"]
    )
    temp = df_pre[['Tendencia (Var)']].merge(
        df_post['Tendencia (Var)'],
        left_index=True, right_index=True,
        suffixes=("_pre", "_post")
    )
    df_postpre["Cambio en Tendencia"] = temp.apply(
        lambda row: tendencia_labels(row["Tendencia (Var)_pre"], row["Tendencia (Var)_post"]), axis=1
    )
    df_postpre["Cambio en Volatilidad"] = np.where(
        df_pre["Std"] / df_pre["Media"].abs() < df_post["Std"] / df_post["Media"].abs(),
        "Mayor Inestabilidad", "Estabilizador"
    )
    df_postpre["Diff Media"] = (df_post["Media"] - df_pre['Media'])
    return df_postpre


# ─────────────────────────────────────────────
# Correlación PIB-Electricidad
# ─────────────────────────────────────────────

def correlacion_con_lag(serie_x, serie_y, lag=1, method='pearson'):
    """
    Correlaciona serie_x rezagada con serie_y.
    lag=1: ¿el valor del año anterior de X se relaciona con Y hoy?

    Parámetros
    ----------
    serie_x : pd.Series
        Serie independiente (ej: electricidad).
    serie_y : pd.Series
        Serie dependiente (ej: PIB).
    lag : int
        Número de períodos de rezago.
    method : str
        'pearson' o 'spearman'

    Retorna
    -------
    tuple
        (correlación, p-value)
    """
    x_lag = serie_x.shift(lag).dropna()
    common_index = x_lag.index.intersection(serie_y.index)
    
    if len(common_index) == 0:
        return float('nan'), float('nan')
        
    x_lag_aligned = x_lag.loc[common_index]
    y_alineado = serie_y.loc[common_index]
    
    if method == 'pearson':
        corr, pvalue = pearsonr(x_lag_aligned, y_alineado)
    elif method == 'spearman':
        corr, pvalue = spearmanr(x_lag_aligned, y_alineado)
    else:
        raise ValueError("Method must be 'pearson' or 'spearman'")
    return corr, pvalue


def comparativa_tendencia(df_1, df_2):
    """
    Compara la tendencia normalizada entre dos DataFrames (ej: PIB vs Electricidad).

    Retorna la diferencia de pendientes normalizadas.
    """
    x_norm = (df_1["value"] - df_1["value"].mean()) / df_1["value"].std()
    pendiente_1 = tendencia(x_norm)
    y_norm = (df_2["value"] - df_2["value"].mean()) / df_2["value"].std()
    pendiente_2 = tendencia(y_norm)
    diff = pendiente_1 - pendiente_2
    return diff


# ─────────────────────────────────────────────
# Pruebas estadísticas avanzadas
# ─────────────────────────────────────────────

def test_estacionariedad(serie, signficancia=0.05):
    """
    Realiza pruebas ADF y KPSS para determinar la estacionariedad de una serie.

    ADF: H0 = Serie tiene raíz unitaria (No estacionaria).
    KPSS: H0 = Serie es estacionaria.

    Retorna
    -------
    dict
        Resultados de ambas pruebas y recomendación.
    """
    # ADF
    adf_res = adfuller(serie.dropna(), autolag='AIC')
    adf_pval = adf_res[1]
    adf_stat = adf_res[0]

    # KPSS
    kpss_res = kpss(serie.dropna(), regression='c', nlags="auto")
    kpss_pval = kpss_res[1]
    kpss_stat = kpss_res[0]

    # Diagnóstico simplificado
    estacionaria = False
    if adf_pval < signficancia and kpss_pval > signficancia:
        diagnostico = "Estacionaria (ADF y KPSS coinciden)"
        estacionaria = True
    elif adf_pval > signficancia and kpss_pval < signficancia:
        diagnostico = "No Estacionaria (ADF y KPSS coinciden)"
    elif adf_pval < signficancia and kpss_pval < signficancia:
        diagnostico = "Estacionaria en Diferencia (Trend Stationary)"
    else:
        diagnostico = "Inconcluso (Necesita mayor revisión)"

    return {
        'adf_pvalue': adf_pval,
        'kpss_pvalue': kpss_pval,
        'diagnostico': diagnostico,
        'estacionaria': estacionaria
    }


def analisis_causalidad_granger(serie_x, serie_y, max_lags=4):
    """
    Realiza la prueba de causalidad de Granger para ver si X ayuda a predecir Y.

    Retorna
    -------
    dict
        P-values mínimos encontrados para diferentes rezagos.
    """
    df = pd.concat([serie_y, serie_x], axis=1).dropna()
    res = grangercausalitytests(df, max_lags, verbose=False)
    p_values = [round(res[i + 1][0]['ssr_chi2test'][1], 4) for i in range(max_lags)]
    return {
        'min_p_value': min(p_values),
        'p_values_per_lag': p_values,
        'causalidad': min(p_values) < 0.05
    }


# ─────────────────────────────────────────────
# Modelos de Series de Tiempo
# ─────────────────────────────────────────────

class modelo_ARIMA:
    """
    Wrapper para modelo ARIMA aplicado a datos de electricidad regional.

    Parámetros
    ----------
    data : pd.DataFrame
        DataFrame con columnas 'Región', 'Date', 'value'.
    corte : int
        Año de corte para separar train/test.
    region : str
        Nombre de la región.
    scaling_log : bool
        Si True, aplica transformación logarítmica a los valores.
    """
    def __init__(self, data, corte, region, scaling_log=False):
        self.data = data[data["Región"] == region].copy()

        if scaling_log == True:
            self.data.value = np.log(self.data.value)

        data_train = self.data[self.data["Date"].dt.year < corte]
        data_train = data_train.set_index('Date')
        data_train = data_train.asfreq('MS')

        data_test = self.data[self.data["Date"].dt.year >= corte]
        data_test = data_test.set_index('Date')
        data_test = data_test.asfreq('MS')

        self.train = data_train.value
        self.test = data_test.value

        self.model_fit = None
        self.forecast = None
        self.rmse = None

    def fit(self, order):
        from statsmodels.tsa.arima.model import ARIMA
        model = ARIMA(self.train, order=order)
        self.model_fit = model.fit()

    def predict(self):
        self.forecast = self.model_fit.forecast(steps=len(self.test))
        return self.forecast

    def evaluate(self, imprimir=True):
        from sklearn.metrics import mean_squared_error
        if imprimir == True:
            print(f"AIC: {self.model_fit.aic}")
            print(f"BIC: {self.model_fit.bic}")
        self.rmse = np.sqrt(mean_squared_error(self.test, self.forecast))
        return self.rmse

    def model_summary(self):
        return self.model_fit.summary()

    def residual(self):
        import matplotlib.pyplot as plt
        residuals = self.model_fit.resid
        residuals.hist(bins=30)
        plt.show()

    def plot(self):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.plot(self.train.index, self.train, label='Train', color='blue')
        plt.plot(self.test.index, self.test, label='Test', color='green')
        plt.plot(self.test.index, self.forecast, label='Forecast', color='red')
        plt.legend()
        plt.title('ARIMA Forecast vs Actual')
        plt.show()

    def buscar_parametros(self, orders):
        best_score = float("inf")
        best_params = None
        for order in orders:
            try:
                self.fit(order)
                self.predict()
                rmse = self.evaluate(imprimir=False)
                if rmse < best_score:
                    best_score = rmse
                    best_params = (order)
            except:
                continue
        return best_params, best_score

    def export_data(self):
        return self.train, self.test


# ─────────────────────────────────────────────
# Análisis Multivariado Trimestral
# ─────────────────────────────────────────────

def test_normalidad_shapiro(df, column="value", alfa=0.05):
    """
    Evalua normalidad mediante test de Shapiro-Wilk sobre un DataFrame agrupado por region.
    
    Retorna
    -------
    list, list
        (regiones_normales, regiones_no_normales)
    """
    regiones_distrib_norm = []
    regiones_no_distrib_norm = []
    for reg in df["Región"].unique():
        data = df[df["Región"] == reg][column].dropna().values
        if len(data) >= 3:
            stat, pvalue = shapiro(data)
            if pvalue > alfa:
                regiones_distrib_norm.append(reg)
            else:
                regiones_no_distrib_norm.append(reg)
    return regiones_distrib_norm, regiones_no_distrib_norm


def analisis_correlacion_pib_electricidad_trimestral(df_pib_quartely, df_elec_monthly, normalize_dates_func):
    """
    Calcula correlación entre la electricidad y PIB por region usando métodos dinámicos 
    (Pearson/Spearman) basándose en pruebas de normalidad.
    """
    df_pib = df_pib_quartely[df_pib_quartely["Titulo"] == "PIB"].copy()
    
    # Homogenizar nombres problematicos conocidos para cruzar
    df_pib = df_pib[~df_pib["Región"].isin(['Aysén del general carlos ibáñez del campo', 'Magallanes y la antártica chilena', 'Metropolitana santiago'])]
    df_elec = df_elec_monthly.copy()
    df_elec["Región"] = df_elec["Región"].str.replace("Del libertador general bernardo o'higgins", 'Del libertador general bernardo ohiggins', regex=False)
    df_pib["Región"] = df_pib["Región"].str.replace("Del ñuble", 'Ñuble', regex=False)
    
    # Test de normalidad del PIB
    regiones_norm, regiones_no_norm = test_normalidad_shapiro(df_pib)
    
    # Agrupación trimestral de electricidad (Suma de los meses que lo componen)
    df_elec['Date'] = pd.to_datetime(df_elec['Date'])
    df_elec = df_elec.set_index('Date')
    df_elec_quart = df_elec.groupby('Región')["value"].resample('QS-JAN').sum().reset_index()
    
    df_corre = pd.DataFrame()
    for reg in df_pib["Región"].unique():
        temp_pib = df_pib[df_pib.Región == reg].copy()
        temp_elec = df_elec_quart[df_elec_quart.Región == reg].copy()
        
        # Alinear dias 1 para los trimestres (normalizacion)
        temp_pib['Date'] = normalize_dates_func(temp_pib['Date'])
        
        # Filtros min date
        min_year = 2017 if reg == "Ñuble" else 2013
        temp_pib = temp_pib[temp_pib["Date"].dt.year >= min_year]
        temp_elec = temp_elec[temp_elec["Date"].dt.year >= min_year]
        
        try:
            common_start = max(temp_pib['Date'].min(), temp_elec['Date'].min())
            common_end = min(temp_pib['Date'].max(), temp_elec['Date'].max())
            
            temp_pib = temp_pib[(temp_pib['Date'] >= common_start) & (temp_pib['Date'] <= common_end)]
            temp_elec = temp_elec[(temp_elec['Date'] >= common_start) & (temp_elec['Date'] <= common_end)]
            
            serie_pib = temp_pib.set_index('Date')['value']
            serie_elec = temp_elec.set_index('Date')['value']
            
            method = 'spearman' if reg in regiones_no_norm else 'pearson'
            
            corr_contem, pvalue_contem = correlacion_con_lag(serie_pib, serie_elec, lag=0, method=method)
            corr_lag, pvalue_lag = correlacion_con_lag(serie_elec, serie_pib, lag=1, method=method)
            corr_lag_pe, pvalue_lag_pe = correlacion_con_lag(serie_pib, serie_elec, lag=1, method=method)
            
            row = pd.DataFrame({
                "Contemporaneo": [corr_contem], "p_1>0.05": [pvalue_contem > 0.05],
                "Lag: Elec -> PIB": [corr_lag], "p_2>0.05": [pvalue_lag > 0.05],
                "Lag: PIB -> Elec": [corr_lag_pe], "p_3>0.05": [pvalue_lag_pe > 0.05],
                "correlacion": method
            }, index=[reg])
            df_corre = pd.concat([df_corre, row])
        except Exception:
            pass
            
    return df_corre

class modelo_SARIMA:
    """
    Wrapper para modelo SARIMA aplicado a datos de electricidad regional.

    Parámetros
    ----------
    data : pd.DataFrame
        DataFrame con columnas 'Región', 'Date', 'value'.
    corte : int
        Año de corte para separar train/test.
    region : str
        Nombre de la región.
    scaling_log : bool
        Si True, aplica transformación logarítmica a los valores.
    """
    def __init__(self, data, corte, region, scaling_log=False):
        self.data = data[data["Región"] == region].copy()

        if scaling_log == True:
            self.data.value = np.log(self.data.value)

        data_train = self.data[self.data["Date"].dt.year < corte]
        data_train = data_train.set_index('Date')
        data_train = data_train.asfreq('MS')

        data_test = self.data[self.data["Date"].dt.year >= corte]
        data_test = data_test.set_index('Date')
        data_test = data_test.asfreq('MS')

        self.train = data_train.value
        self.test = data_test.value

        self.model_fit = None
        self.forecast = None
        self.rmse = None

    def fit(self, order, seasonal_order):
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        model = SARIMAX(self.train, order=order, seasonal_order=seasonal_order)
        self.model_fit = model.fit(method='lbfgs')

    def predict(self):
        self.forecast = self.model_fit.forecast(steps=len(self.test))
        return self.forecast

    def evaluate(self, imprimir=True):
        from sklearn.metrics import mean_squared_error
        if imprimir == True:
            print(f"AIC: {self.model_fit.aic}")
            print(f"BIC: {self.model_fit.bic}")
        self.rmse = np.sqrt(mean_squared_error(self.test, self.forecast))
        return self.rmse

    def residual(self):
        import matplotlib.pyplot as plt
        residuals = self.model_fit.resid
        residuals.hist(bins=30)
        plt.show()

    def plot(self):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.plot(self.train.index, self.train, label='Train', color='blue')
        plt.plot(self.test.index, self.test, label='Test', color='green')
        plt.plot(self.test.index, self.forecast, label='Forecast', color='red')
        plt.legend()
        plt.title('SARIMA Forecast vs Actual')
        plt.show()

    def buscar_parametros(self, orders, seasonal_orders):
        best_score = float("inf")
        best_params = None
        for order in orders:
            for s_order in seasonal_orders:
                try:
                    self.fit(order, s_order)
                    self.predict()
                    rmse = self.evaluate(imprimir=False)
                    if rmse < best_score:
                        best_score = rmse
                        best_params = (order, s_order)
                except:
                    continue
        return best_params, best_score

    def export_data(self):
        return self.train, self.test
