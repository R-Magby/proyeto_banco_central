"""
main.py — Orquestador principal del proyecto de análisis económico regional de Chile.

Este script coordina todo el flujo de trabajo:
1. Conexión a la API del Banco Central
2. Carga de datos (PIB regional y Electricidad)
3. Limpieza de los datos crudos
4. Análisis descriptivo
5. Exportación de resultados

Uso:
    python main.py
"""

from src.data_loader import (
    conectar_api,
    buscar_series,
    datos_regionales,
    datos_regionales_quartely,
    LISTA_SERVICIOS_ANUALES,
    LISTA_ELECTRICIDAD,
)
from src.cleaning import (
    ajuste_df_serie, 
    limpiar_datos_pib, 
    limpiar_datos_electricidad,
    ajuste_df_serie_quartely,
    normalize_quarter_dates
)
from src.transformation import (
    preparar_exportacion_pib,
    preparar_exportacion_servicios,
)
from src.analysis import (
    Analisis_PIB, 
    proyeccion_sector_alcista, 
    test_estacionariedad,
    analisis_correlacion_pib_electricidad_trimestral
)


def main():
    print("=" * 60)
    print("  Proyecto de Análisis Económico Regional de Chile")
    print("  Fuente: Banco Central de Chile — API bcchapi")
    print("=" * 60)

    # ─── PASO 1: Conexión a la API ───────────────────────────
    print("\n[1/5] Conectando a la API del Banco Central...")
    siete = conectar_api(file="user.txt")
    print("      ✓ Conexión exitosa.")

    # ─── PASO 2: Carga de datos PIB Anual y Electricidad ─────
    print("\n[2/5] Descargando datos básicos...")
    df_servicios_per_region = buscar_series(siete, LISTA_SERVICIOS_ANUALES[0])
    df_servicios_per_region = ajuste_df_serie(df_servicios_per_region)
    df_final = datos_regionales(df_servicios_per_region, file_credenciales="user.txt")
    
    df_series_electricidad = buscar_series(siete, LISTA_ELECTRICIDAD[0])
    df_electricidad = datos_regionales(ajuste_df_serie(df_series_electricidad), file_credenciales="user.txt")

    # Carga de datos PIB Trimestrales
    print("      ✓ Descargando PIB Trimestral (resolviendo series)...")
    x_q = buscar_series(siete, "referencia 2018")
    df_pib_q_meta = ajuste_df_serie_quartely(x_q)
    df_quartely = datos_regionales_quartely(df_pib_q_meta, 1.0, file_credenciales="user.txt")

    # Carga de datos PIB Contribución Porcentual
    print("      ✓ Descargando PIB Contribución Porcentual...")
    x_p = buscar_series(siete, "contribución porcentual respecto de igual periodo del año anterior, referencia 2018")
    x_p = x_p[(x_p.spanishTitle.str.contains("PIB Región")) & (x_p.frequencyCode == "QUARTERLY")]
    df_pib_p_meta = ajuste_df_serie(x_p)
    df_porc = datos_regionales(df_pib_p_meta, file_credenciales="user.txt")
    
    print(f"      ✓ {df_final.shape[0]} registros anuales descargados.")
    print(f"      ✓ {df_quartely.shape[0]} registros trimestrales descargados.")
    print(f"      ✓ {df_porc.shape[0]} registros porcentuales descargados.")
    print(f"      ✓ Regiones: {df_final.Región.nunique()}")

    # ─── PASO 3: Limpieza ────────────────────────────────────
    print("\n[3/5] Limpiando datos...")
    df_final_servicios = limpiar_datos_pib(df_final.copy())
    df_electricidad = limpiar_datos_electricidad(df_electricidad)
    print(f"      ✓ Datos de servicios por región (Anuales): {df_final_servicios.shape[0]} registros.")

    # ─── PASO 4: Análisis (ejemplo) ──────────────────────────
    print("\n[4/5] Ejecutando análisis descriptivo y diagnosticos trimestrales...")
    regiones = df_final.Región.unique()[1:]  # Excluir None
    
    # Análisis Trimestral: Correlación PIB y Electricidad
    if not df_quartely.empty and not df_electricidad.empty:
        print("\n      --- Análisis Trimestral (Electricidad vs PIB) ---")
        df_corre = analisis_correlacion_pib_electricidad_trimestral(df_quartely, df_electricidad, normalize_quarter_dates)
        print("      Resultados Resumidos de Correlación:")
        print(df_corre[['Contemporaneo', 'Lag: Elec -> PIB', 'Lag: PIB -> Elec']].head(5))

    print(f"\n      Analizando {len(regiones)} regiones (Anual)...")
    for reg in regiones[:3]:  # Muestra las primeras 3 como ejemplo
        resultado = Analisis_PIB(df_final, reg)
        if resultado is not None:
            df_descri, _, _ = resultado
            print(f"\n      → {reg}:")
            print(f"        Sectores analizados: {len(df_descri)}")
            try:
                pib_total = df_final[(df_final.Región == reg) & (df_final.Titulo == "PIB")]
                if not pib_total.empty:
                    diag = test_estacionariedad(pib_total["value"])
                    print(f"        Diagnóstico PIB: {diag['diagnostico']} (ADF p={diag['adf_pvalue']:.4f})")
            except Exception as e:
                print(f"        ! Error en diagnóstico: {e}")
                
    print("      ✓ Análisis completado.")

    # ─── PASO 5: Exportación ─────────────────────────────────
    print("\n[5/5] Exportando datos a CSV...")
    df_pib_export = preparar_exportacion_pib(df_final)
    df_pib_export.to_csv('data/datos_pib.csv', index=False, encoding='utf-8')

    df_serv_export = preparar_exportacion_servicios(df_final)
    df_serv_export.to_csv('data/datos_serv.csv', index=False, encoding='utf-8')

    print("      ✓ data/datos_pib.csv exportado.")
    print("      ✓ data/datos_serv.csv exportado.")

    print("\n" + "=" * 60)
    print("  Orquestación finalizada con éxito.")
    print("=" * 60)

if __name__ == "__main__":
    main()
