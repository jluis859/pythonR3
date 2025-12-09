#!/usr/bin/env python
import requests
import csv
import os
import pandas as pd
import datetime

data = {
    'token': 'ED02E0F4B455C1C84CD7F4398FB7CA4C',
    'content': 'report',
    'format': 'json',
    'report_id': '420',
    'csvDelimiter': '',
    'rawOrLabel': 'label',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'returnFormat': 'json'
}
r = requests.post('https://redcap.paho.org/api/',data=data)
print('HTTP Status: ' + str(r.status_code))



if r.status_code == 200:
    report_data = r.json()
    if report_data:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # --- Read the dictionary to map variable names to labels ---
        label_map = {}
        dict_file = os.path.join(script_dir, 'diccionario.csv')
        try:
            with open(dict_file, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    label_map[row['Variable / Field Name']] = row['Field Label']
        except FileNotFoundError:
            print(f"Advertencia: No se encontró el archivo de diccionario en '{dict_file}'. La columna 'Etiqueta' estará vacía.")
        except Exception as e:
            print(f"Error al leer el archivo de diccionario: {e}")

        # --- Use pandas to process and save the data ---
        try:
            # Convert the report data to a pandas DataFrame
            df = pd.DataFrame(report_data)

            # Ensure 'indexdate' is in datetime format and create a column for sheet names (MM-YYYY)
            # errors='coerce' will turn any unparseable dates into NaT (Not a Time)
            df['sheet_name'] = pd.to_datetime(df['indexdate'], errors='coerce').dt.strftime('%m-%Y')

            # --- Save to Excel with auto-adjusted column widths ---
            excel_output_file = os.path.join(script_dir, 'reporte.xlsx')
            
            with pd.ExcelWriter(excel_output_file, engine='openpyxl') as writer:
                # Group by the new 'sheet_name' column
                for sheet_name, group_df in df.groupby('sheet_name'):
                    # Drop the temporary 'sheet_name' column from the group
                    group_df = group_df.drop(columns=['sheet_name'])
                    
                    # Transpose the DataFrame so fields are rows and records are columns
                    df_transposed = group_df.transpose()

                    # Set the column names to 'Registro 1', 'Registro 2', etc.
                    num_records = len(group_df)
                    df_transposed.columns = [f'Registro {i+1}' for i in range(num_records)]

                    # Add the 'Etiqueta' column by mapping the index
                    df_transposed.insert(0, 'Etiqueta', df_transposed.index.map(label_map).fillna(''))

                    # Rename the index to 'Campo'
                    df_transposed.index.name = 'Campo'

                    # Write the transposed dataframe to its corresponding sheet
                    df_transposed.to_excel(writer, sheet_name=sheet_name)
                    
                    # Auto-adjust column widths for the current sheet
                    worksheet = writer.sheets[sheet_name]
                    for column_cells in worksheet.columns:
                        max_length = 0
                        column = column_cells[0].column_letter  # Get the column name
                        for cell in column_cells:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = (max_length + 2)
                        worksheet.column_dimensions[column].width = adjusted_width
            
            print(f"Los datos se han guardado correctamente en '{excel_output_file}' con hojas por mes.")

        except Exception as e:
            print(f"Ocurrió un error al procesar o guardar los archivos: {e}")
            
    else:
        print("No se recibieron datos del reporte.")
else:
    # Print the error from the API if the request failed
    print("Error en la solicitud a la API:")
    print(r.text)