import sys
import csv
import requests
import os

# Add the path to the directory containing your .NET DLL
#sys.path.append(r'C:\Repos\Python R3Model\R3Model')
sys.path.append('/Users/jluis859/Python_Workspace/Python R3Model/R3Model')

def process_meddra_fields(record, prefix, meddra_mapping, has_suffix):
    """Processes fields to find and add MedDRA codes."""
    meddra_codes = []
    if has_suffix:
        # Handles fields like 'comorbilidad___1', 'comorbilidad___2'
        field_prefix_with_separator = f"{prefix}___"
        for key, value in record.items():
            if key.startswith(field_prefix_with_separator) and value == '1':
                variable_name, choice = key.split('___', 1)
                if variable_name == prefix and variable_name in meddra_mapping and choice in meddra_mapping[variable_name]:
                    meddra_code = meddra_mapping[variable_name][choice]
                    meddra_codes.append(meddra_code)
    else:
        # Handles single fields like 'anafilaxia_d7'
        if record.get(prefix) == '1' and prefix in meddra_mapping:
            # For single fields, the choice is always '1' (for 'Yes')
            if '1' in meddra_mapping[prefix]:
                meddra_codes.append(meddra_mapping[prefix]['1'])
    
    record[f"{prefix}_meddra"] = ' | '.join(meddra_codes)

def insert_header(headers, prefix, last_field_index, has_suffix):
    """Inserts a new MedDRA header into the list of headers at the correct position."""
    if has_suffix:
        target_column = f"{prefix}___{last_field_index}"
    else:
        target_column = prefix
    
    new_header = f"{prefix}_meddra"
    try:
        insert_pos = headers.index(target_column) + 1
        headers.insert(insert_pos, new_header)
    except ValueError:
        # Fallback if column not found, append at the end
        if new_header not in headers:
            headers.append(new_header)

data = {
    'token': 'ED02E0F4B455C1C84CD7F4398FB7CA4C',
    'content': 'record',
    'action': 'export',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}
r = requests.post('https://redcap.paho.org/api/',data=data)
r.encoding = 'utf-8'
print('HTTP Status: ' + str(r.status_code))
json_data = r.json()
print(json_data)

# Save the JSON response to a CSV file

# Create directory if it doesn't exist
output_dir = 'Data_COL'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Write to CSV
if json_data:
    # Assuming all records have the same keys
    keys = json_data[0].keys()
    with open('Data_COL/redcap.csv', 'w', newline='', encoding='utf-8-sig') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(json_data)

# Load MedDRA mapping
meddra_mapping = {}
with open('Data_COL/mapeo meddra.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = [h.strip() for h in next(reader)]
    csv_reader = csv.DictReader(f, fieldnames=header)
    
    # Re-open and build the reader with corrected headers
    f.seek(0)
    next(reader) # Skip header
    reader = csv.DictReader(f, fieldnames=header)

    for row in reader:
        variable_name = row.get('Variable / Field Name')
        if not variable_name:
            continue
            
        meddra_codes_str = row.get('MedDRA', '')
        
        if not meddra_codes_str:
            continue

        # Parse "1, 10012601 | 2, 10020188" or just "10002218"
        code_map = {}
        parts = meddra_codes_str.split('|')
        if len(parts) == 1 and ',' not in parts[0]:
            # It's a single code for a 'Yes'/'1' value
            code_map['1'] = parts[0].strip()
        else:
            # It's a multi-choice field
            for part in parts:
                part = part.strip()
                if ',' in part:
                    try:
                        key, value = part.split(',', 1)
                        code_map[key.strip()] = value.strip()
                    except ValueError:
                        print(f"Skipping invalid MedDRA map part: {part}")
        
        meddra_mapping[variable_name] = code_map

# Define the prefixes, their last index, and if they have suffixes
field_definitions = {
    # prefix: (last_index, has_suffix)
    'comorbilidad': (8, True),
    'diabetes': (3, True),
    'transplante': (4, True),
    'autoinmune': (4, True),
    'ttnos_grales_d7': (6, True),
    'ttnos_grales_d14': (6, True),
    'ttnos_grales_d30': (6, True),
    'anafilaxia_d7': (0, False),
    'anafilaxia_d14': (0, False),
    'anafilaxia_d30': (0, False),
    'gi_esavi_d7': (4, True),
    'gi_esavi_d14': (4, True),
    'gi_esavi_d30': (4, True),
    'cutanea_esavi_d7': (4, True),
    'cutanea_esavi_d14': (4, True),
    'cutanea_esavi_d30': (4, True),
    'psiq_esavi_d7': (3, True),
    'psiq_esavi_d14': (3, True),
    'psiq_esavi_d30': (3, True),
    'snc_esavi_d7': (3, True), 
    'snc_esavi_d14': (3, True),
    'snc_esavi_d30': (3, True),
    'ritm_esavi_d7': (0, False),
    'ritm_esavi_d14': (0, False),
    'ritm_esavi_d30': (0, False),
    'sincope_esavi_d7': (0, False),
    'sincope_esavi_d14': (0, False),
    'sincope_esavi_d30': (0, False),
    'esavi_grave_d7': (8, True),
    'esavi_grave_d14': (8, True),
    'esavi_grave_d30': (8, True),
    'evento_gestante_d7': (3, True),
    'evento_gestante_d14': (3, True),
    'evento_gestante_d30': (3, True),
}

# Process records
for record in json_data:
    for prefix, (last_index, has_suffix) in field_definitions.items():
        process_meddra_fields(record, prefix, meddra_mapping, has_suffix)

# Define the mapping for the 'vacuna' column
vacuna_mapping = {
    '1': '5955740', #R DPP® (BioManguinhos) 
    '2': '4232902', #Stamaril ® (Sanofi Pasteur)
    '3': '333' #SinSaVac™ Chumakov FSC
}

# Process records to add 'whodrug' column
for record in json_data:
    vacuna_value = record.get('vacuna')
    # Get the mapped value, or an empty string if no match is found
    whodrug_value = vacuna_mapping.get(vacuna_value, '') 
    record['whodrug'] = whodrug_value

# Write processed data to a new CSV, preserving order
if json_data:
    # Get original headers from the first record
    headers = list(json_data[0].keys())
    
    # Insert new MedDRA headers
    for prefix, (last_index, has_suffix) in field_definitions.items():
        insert_header(headers, prefix, last_index, has_suffix)

    # Insert 'whodrug' header after 'vacuna'
    try:
        vacuna_pos = headers.index('vacuna') + 1
        headers.insert(vacuna_pos, 'whodrug')
    except ValueError:
        # Fallback if 'vacuna' column not found, append at the end
        if 'whodrug' not in headers:
            headers.append('whodrug')

    # Ensure the final header list is unique while preserving order
    final_headers = []
    for header in headers:
        if header not in final_headers:
            final_headers.append(header)

    with open('Data_COL/redcap_processed.csv', 'w', newline='', encoding='utf-8-sig') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=final_headers)
        dict_writer.writeheader()
        dict_writer.writerows(json_data)

print("Processed data saved to Data_COL/redcap_processed.csv")