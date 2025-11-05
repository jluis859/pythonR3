import uuid
from datetime import datetime

def generate_guid():
    """Genera un GUID único"""
    return str(uuid.uuid4())

# Define your exn_handler function
def exn_handler(exception):
    print(f"Validation exception: {exception}")

def process_date(date_string):
    """
    Process date strings in multiple formats and convert to YYYYMMDD format.
    Accepts formats: dd/mm/yy, dd/mm/yyyy, dd-mm-yyyy, dd-mm-yy
    
    Args:
        date_string: The date string to process
        
    Returns:
        str: Date in YYYYMMDD format or empty string if invalid
    """
    if not date_string or date_string.strip() == "":
        return ""
        
    date_string = date_string.strip()
    
    # Try different date formats
    formats = [
        "%d/%m/%y",    # dd/mm/yy
        "%d/%m/%Y",    # dd/mm/yyyy
        "%d-%m-%Y",    # dd-mm-yyyy
        "%d-%m-%y"     # dd-mm-yy
    ]
    
    for date_format in formats:
        try:
            fecha_obj = datetime.strptime(date_string, date_format)
            
            # Handle two-digit years (assuming 21st century for years 00-69, 20th century for 70-99)
            if date_format in ["%d/%m/%y", "%d-%m-%y"]:
                year = fecha_obj.year
                if year < 100:
                    if year < 70:
                        fecha_obj = fecha_obj.replace(year=2000 + year)
                    else:
                        fecha_obj = fecha_obj.replace(year=1900 + year)
            
            return fecha_obj.strftime("%Y%m%d")
        except ValueError:
            continue
    
    print(f"Error: La fecha '{date_string}' no es válida. Formatos aceptados: dd/mm/yy, dd/mm/yyyy, dd-mm-yyyy, dd-mm-yy")
    return ""
    
def get_qualification(qualification):
    if not qualification:
        return ""
        
    qualification = qualification.upper().strip()
    
    if qualification in ["MEDICO", "MÉDICO", "INTERNO DE MEDICINA", "TECNOLOGO MEDICO", "TECNÓLOGO MÉDICO"]:
        return "1"  # Physician
    elif qualification in ["QUIMICO FARMACEUTICO", "QUÍMICO FARMACÉUTICO", "INTERNO DE FARMACIA"]:
        return "2"  # Pharmacist
    elif qualification in ["ENFERMERA", "ENFERMERA MATRONA", "MATRONA", "KINESIOLOGO", "KINESIÓLOGO", 
                          "BIOQUIMICO", "BIOQUÍMICO", "TECNICO EN ENFERMERIA", "TÉCNICO EN ENFERMERÍA", 
                          "TECNICO PARAMEDICO", "TÉCNICO PARAMÉDICO", "OTRO PROFESIONAL DE LA SALUD"]:
        return "3"  # Other health professional
    elif qualification == "NO SEÑALA":
        return ""  # nullFlavor: UNK
    else:
        return "5"  # Consumer or other non health professional

def get_age(age, unit):
    if not age or not unit:
        return "", ""
    
    age = str(age).strip()
    unit = unit.strip().lower()

    if unit in ['a', 'años']:
        return age, "a"
    elif unit in ['m', 'meses']:
        return age, "mo"
    elif unit in ['d', 'días']:
        return age, "d"
    elif unit == 'm y 25 días':
        return str(int(age) + 1), "mo"
    elif unit == 'a 10 m':
        total_months = int(age) * 12 + 10
        return str(total_months), "mo"
    else:
        return "", ""

def get_sex(sex):
    if sex.lower() in ['M', 'mas']:
        return "1"
    elif sex.lower() in ['F', 'fem']:
        return "2"
    else:
        return ""

def process_weight(weight_value):
    """
    Procesa el valor del peso para extraer un número válido en kg.
    
    Args:
        weight_value: El valor del peso como string (ej: "10.00 kg", "100.00 libras")
        
    Returns:
        float: El peso en kg o None si no se puede procesar
    """
    if not weight_value or weight_value == "":
        return None
    
    try:
        # Convertir a string en caso de que sea un número
        weight_str = str(weight_value).strip().lower()
        
        # Eliminar caracteres no numéricos excepto punto decimal
        numeric_part = ''.join(c for c in weight_str if c.isdigit() or c == '.')
        
        # Extraer el valor numérico
        if numeric_part:
            weight_value = float(numeric_part)
            
            # Convertir libras a kg si es necesario
            if "libra" in weight_str:
                weight_value = weight_value * 0.453592  # 1 libra = 0.453592 kg
                
            # Redondear a 2 decimales
            return round(weight_value, 2)
        
        return None
    except (ValueError, TypeError):
        print(f"Error al procesar el peso: {weight_value}")
        return None

def is_pregnant(sex, days_pregnant, weeks_pregnant, months_pregnant, trimesters_pregnant):
    # Primero verificar si es mujer
    if sex.upper() != 'F':
        return False
    
    # Verificar si hay algún valor en cualquiera de los campos de embarazo
    if (days_pregnant and days_pregnant != '0') or \
       (weeks_pregnant and weeks_pregnant != '0') or \
       (months_pregnant and months_pregnant != '0') or \
       (trimesters_pregnant and trimesters_pregnant != '0'):
        return True
    
    return False

def is_hospitalized(hospitalization_value):
    if not hospitalization_value:
        return False
        
    hospitalization_value = hospitalization_value.lower().strip()
    
    # Lista de valores que indican hospitalización
    hospitalization_positive_values = [
        'si', 'sí', 'cti', 'si cti', 'sí cti', 'si (ver)', 'si 5 días', 'si 5 dias',
        'sí, cti', 'si, cti', 'sí, cti -prolongó', 'si, cti -prolongo',
        'si. cti', 'si. cti pediatrico', 'cuidados intermedios', 'en emergencia',
        'prolongo', 'prolongó', 'prolongo', 'prolongó hospitalización', 'prolongo hospitalizacion',
        'prolongó la hospitalización', 'prolongo la hospitalizacion'
    ]
    
    # Lista de valores que indican NO hospitalización
    hospitalization_negative_values = [
        'no', 'sin dato', 'sin datos'
    ]
    
    # Verificar si el valor indica hospitalización
    for value in hospitalization_positive_values:
        if value in hospitalization_value:
            return True
            
    # Verificar si el valor indica NO hospitalización
    for value in hospitalization_negative_values:
        if hospitalization_value == value:
            return False
            
    # Si no coincide con ninguno de los valores conocidos, asumimos que no hay hospitalización
    return False

def is_serious(serious_value):
    if not serious_value:
        return False
        
    serious_value = serious_value.lower().strip()
    
    # Lista de valores que indican que el evento es grave
    serious_positive_values = [
        'grave', 'gravedad potencial', 'seria', 'severa', 'severo', 
        'si', 'sí', 'si para la paciente', 'si?', 'sí?'
    ]
    
    # Lista de valores que indican que el evento NO es grave
    serious_negative_values = [
        'no', 'no corresponde', 'no si', 'no????', 's/d', 'sin dao', 
        'sin dato', 'sin datos', 'leve', 'moderada', 'moderado'
    ]
    
    # Verificar si el valor indica que es grave
    for value in serious_positive_values:
        if value in serious_value:
            return True
            
    # Verificar si el valor indica que NO es grave
    for value in serious_negative_values:
        if value in serious_value:
            return False
            
    # Si no coincide con ninguno de los valores conocidos, asumimos que no es grave
    return False

def is_fatal(fatal_value):
    if not fatal_value:
        return False
        
    fatal_value = fatal_value.lower().strip()
    
    # Solo el valor "si" indica que el evento fue mortal
    if fatal_value == 'si' or fatal_value == 'sí':
        return True
    
    # Para todos los demás casos ("no", "????", o cualquier otro), retornamos False
    return False

def get_sender_type(sender_type):
    sender_type = sender_type.lower().strip()
    
    if sender_type == "laboratorio farmacéutico":
        return "1"  # Pharmaceutical Company
    elif sender_type == "autoridad regulatoria":
        return "2"  # Regulatory Authority
    elif sender_type == "profesional de la salud":
        return "3"  # Health Professional
    elif sender_type == "paciente" or sender_type == "paciente / consumidor":
        return "7"  # Patient / Consumer
    elif sender_type == "otro":
        return "6"  # Other (e.g. distributor or other organisation)
    else:
        return ""  # Default empty if no match

def get_outcome(outcome_value):
    if not outcome_value:
        return ""  # unknown
        
    outcome_value = outcome_value.lower().strip()
    
    # 1 = recovered/resolved without sequelae
    if "recuperado sin secuelas" in outcome_value:
        return "1"
    
    # 2 = recovering/resolving
    if "en recuperación" in outcome_value:
        return "2"
    
    # 3 = not recovered/not resolved
    if "no recuperado" in outcome_value:
        return "3"
    
    # 4 = recovered/resolved with sequelae
    if "recuperado con secuelas" in outcome_value:
        return "4"
    
    # 5 = fatal
    if "fallecido" in outcome_value:
        return "5"
    
    # 0 = unknown
    if "desconocido" in outcome_value:
        return "0"
    
    # If no match, assume unknown
    return "0"