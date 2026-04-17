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
    LISTA_SERVICIOS_ANUALES,
    LISTA_ELECTRICIDAD,
)
from src.cleaning import ajuste_df_serie, limpiar_datos_pib, limpiar_datos_electricidad
from src.transformation import (
    preparar_exportacion_pib,
    preparar_exportacion_servicios,
)
from src.analysis import Analisis_PIB, proyeccion_sector_alcista


def main():
    print("=" * 60)
    print("  Proyecto de Análisis Económico Regional de Chile")
    print("  Fuente: Banco Central de Chile — API bcchapi")
    print("=" * 60)

    # ─── PASO 1: Conexión a la API ───────────────────────────
    print("\n[1/5] Conectando a la API del Banco Central...")
    siete = conectar_api(file="user.txt")
    print("      ✓ Conexión exitosa.")

    # ─── PASO 2: Carga de datos PIB ──────────────────────────
    print("\n[2/5] Descargando datos de PIB regional...")
    df_servicios_per_region = buscar_series(siete, LISTA_SERVICIOS_ANUALES[0])
    df_servicios_per_region = ajuste_df_serie(df_servicios_per_region)
    df_final = datos_regionales(df_servicios_per_region, file_credenciales="user.txt")
    print(f"      ✓ {df_final.shape[0]} registros descargados.")
    print(f"      ✓ Regiones: {df_final.Región.nunique()}")

    # ─── PASO 3: Limpieza ────────────────────────────────────
    print("\n[3/5] Limpiando datos...")
    df_final = df_final.drop(columns=["statusCode"])
    df_final_servicios = limpiar_datos_pib(
        df_final.copy()  # Pasamos copia para no perder df_final con PIB total
    )
    print(f"      ✓ Datos de servicios por región: {df_final_servicios.shape[0]} registros.")

    # ─── PASO 4: Análisis (ejemplo) ──────────────────────────
    print("\n[4/5] Ejecutando análisis descriptivo...")
    regiones = df_final.Región.unique()[1:]  # Excluir None
    print(f"      Analizando {len(regiones)} regiones...")

    for reg in regiones[:3]:  # Muestra las primeras 3 como ejemplo
        resultado = Analisis_PIB(df_final, reg)
        if resultado is not None:
            df_descri, _, _ = resultado
            print(f"\n      → {reg}:")
            print(f"        Sectores analizados: {len(df_descri)}")
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
