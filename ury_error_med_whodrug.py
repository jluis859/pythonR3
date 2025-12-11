import pandas as pd
import os

def find_mpid_and_info(df_encontrados, marca_comercial, principio_activo):
    """
    Busca el mpid y la alerta en el dataframe de encontrados.
    Primero por marca comercial, luego por principio activo.
    """
    # Búsqueda por Marca Comercial
    if pd.notna(marca_comercial) and marca_comercial.strip() != '':
        match = df_encontrados[df_encontrados['Original'].str.lower() == marca_comercial.lower()]
        if not match.empty:
            return (
                match.iloc[0]['mpid'],
                match.iloc[0]['Alerta'],
                f"Encontrado por Marca Comercial"
            )

    # Búsqueda por Principio Activo
    if pd.notna(principio_activo) and principio_activo.strip() != '':
        # La columna 'Ingredients' puede tener múltiples valores separados por '|'
        match = df_encontrados[df_encontrados['Ingredients'].str.lower().str.contains(principio_activo.lower(), na=False)]
        if not match.empty:
            return (
                match.iloc[0]['mpid'],
                match.iloc[0]['Alerta'],
                f"Encontrado por Principio Activo"
            )
            
    return None, None, "No encontrado"


def procesar_mapeo_whodrug():
    """
    Paso 1: Procesa el mapeo inicial para encontrar MPIDs y separar en dos archivos.
    Paso 2: Procesa el archivo de errores de medicación para asignar los MPIDs encontrados.
    """
    # --- PASO 1: Procesamiento inicial de mapeo ---
    base_path = '/Users/jluis859/Python_Workspace/Python R3Model/Data_URY/'
    mapeo_path = os.path.join(base_path, 'mapeo_whodrug_errores.csv')
    whodrug_path = os.path.join(base_path, 'whodrug_py.csv')
    output_encontrados_path = os.path.join(base_path, 'mapeo_whodrug_errores_encontrados.csv')
    output_no_encontrados_path = os.path.join(base_path, 'mapeo_whodrug_errores_no_encontrados.csv')

    try:
        df_mapeo = pd.read_csv(mapeo_path)
        df_whodrug = pd.read_csv(whodrug_path)
    except FileNotFoundError as e:
        print(f"Error en Paso 1: No se pudo encontrar el archivo {e.filename}")
        return

    df_whodrug['drugCode'] = df_whodrug['drugCode'].astype(str)
    df_mapeo['Drug code'] = df_mapeo['Drug code'].astype(str)
    df_mapeo['mpid'] = ''
    df_mapeo['comentarios'] = ''

    for index, row in df_mapeo.iterrows():
        drug_code = row['Drug code']
        resultados = df_whodrug[df_whodrug['drugCode'] == drug_code]
        if not resultados.empty:
            entry_ury = resultados[resultados['iso3Code'] == 'URY']
            if not entry_ury.empty:
                df_mapeo.at[index, 'mpid'] = entry_ury.iloc[0]['country_medicinalProductID']
                df_mapeo.at[index, 'comentarios'] = 'MPID de país (URY) seleccionado'
            else:
                df_mapeo.at[index, 'mpid'] = resultados.iloc[0]['medicinalProductID']
                df_mapeo.at[index, 'comentarios'] = 'MPID genérico seleccionado'
        else:
            df_mapeo.at[index, 'comentarios'] = 'No se encontró MPID'

    df_encontrados = df_mapeo[df_mapeo['comentarios'] != 'No se encontró MPID'].copy()
    df_no_encontrados = df_mapeo[df_mapeo['comentarios'] == 'No se encontró MPID'].copy()
    df_encontrados.sort_values(by='Original', inplace=True)
    df_no_encontrados.sort_values(by='Original', inplace=True)
    df_encontrados.to_csv(output_encontrados_path, index=False, encoding='utf-8-sig')
    df_no_encontrados.to_csv(output_no_encontrados_path, index=False, encoding='utf-8-sig')

    print("Paso 1 completado. Se han generado dos archivos de mapeo.")
    print(f"- Encontrados: {output_encontrados_path}")
    print(f"- No encontrados: {output_no_encontrados_path}")

    # --- PASO 2: Procesamiento de errores de medicación ---
    errores_med_path = os.path.join(base_path, 'errores_medicacion_base.csv')
    output_errores_procesado_path = os.path.join(base_path, 'errores_medicacion_procesado.csv')

    try:
        df_errores = pd.read_csv(errores_med_path)
        df_encontrados_leido = pd.read_csv(output_encontrados_path)
    except FileNotFoundError as e:
        print(f"Error en Paso 2: No se pudo encontrar el archivo {e.filename}")
        return

    comentarios_correcto = []
    alertas_correcto = []
    comentarios_erroneo = []
    alertas_erroneo = []

    for index, row in df_errores.iterrows():
        # Procesar lado "correcto"
        mpid_c, alerta_c, com_c = find_mpid_and_info(
            df_encontrados_leido,
            row['Marca comercial correcto'],
            row['Principio activo correcto']
        )
        if mpid_c:
            df_errores.at[index, 'mpid correcto'] = mpid_c
        comentarios_correcto.append(com_c)
        alertas_correcto.append(alerta_c)

        # Procesar lado "erroneo"
        mpid_e, alerta_e, com_e = find_mpid_and_info(
            df_encontrados_leido,
            row['Marca comercial erroneo'],
            row['Principio activo erroneo']
        )
        if mpid_e:
            df_errores.at[index, 'mpid erroneo'] = mpid_e
        comentarios_erroneo.append(com_e)
        alertas_erroneo.append(alerta_e)

    # Añadir las nuevas columnas al final
    df_errores['Comentario_correcto'] = comentarios_correcto
    df_errores['Alerta_correcto'] = alertas_correcto
    df_errores['Comentario_erroneo'] = comentarios_erroneo
    df_errores['Alerta_erroneo'] = alertas_erroneo
    
    # Llenar valores NaN en las nuevas columnas con strings vacíos
    df_errores[['Alerta_correcto', 'Alerta_erroneo']] = df_errores[['Alerta_correcto', 'Alerta_erroneo']].fillna('')


    df_errores.to_csv(output_errores_procesado_path, index=False, encoding='utf-8-sig')
    
    print("\nPaso 2 completado. Se ha procesado el archivo de errores de medicación.")
    print(f"- Resultado guardado en: {output_errores_procesado_path}")


if __name__ == '__main__':
    procesar_mapeo_whodrug()
