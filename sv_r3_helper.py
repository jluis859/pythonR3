import uuid
from datetime import datetime

def generate_guid():
    """Genera un GUID único"""
    return str(uuid.uuid4())

# Define your exn_handler function
def exn_handler(exception):
    print(f"Validation exception: {exception}")

def process_date(date_string):
    if not date_string or date_string.strip() == "":
        return ""
    try:
        fecha_obj = datetime.strptime(date_string, "%d/%m/%y")
        return fecha_obj.strftime("%Y%m%d")
    except ValueError:
        print(f"Error para la fecha '{date_string}'.")
        return ""

def process_date_time(date_time_string):
    """
    Processes a date-time string and returns it in the ICH E2B(R3) format.
    
    Args:
        date_time_string: The date-time string in format "DD/MM/YY HH:MM"
        
    Returns:
        str: Date in ICH E2B(R3) format (CCYYMMDDHHMMSS)
             If only date is provided, returns CCYYMMDD
    """
    if not date_time_string or date_time_string.strip() == "":
        return ""
    
    try:
        # Split the string into date and time parts
        parts = date_time_string.strip().split()
        
        # Process the date part
        date_part = parts[0]
        fecha_obj = datetime.strptime(date_part, "%d/%m/%y")
        formatted_date = fecha_obj.strftime("%Y%m%d")
        
        # If there's a time part, include it in the result
        if len(parts) > 1:
            time_part = parts[1]
            time_obj = datetime.strptime(time_part, "%H:%M")
            formatted_time = time_obj.strftime("%H%M%S")
            return formatted_date + formatted_time
        else:
            # Return just the date if no time is provided
            return formatted_date
    
    except ValueError as e:
        print(f"Error processing date-time '{date_time_string}': {e}")
        return ""

def get_action_taken(action_text):
    """
    Maps the action taken text to the corresponding code according to ICH E2B(R3) standards.
    
    Args:
        action_text: The text describing the action taken
        
    Returns:
        str: The action taken code (1, 2, 3, 4, 0, or 9)
    """
    if not action_text:
        return "0"  # Unknown
        
    action_text = action_text.lower().strip()

    action_text = action_text.lstrip('—-–')
    action_text = action_text.strip()
    
    # 1 = Drug withdrawn (Medicamento Retirado)
    if "medicamento retirado" in action_text:
        # Prioridad más alta - si se retiró el medicamento, ese es el código principal
        return "1"
    
    # 2 = Dose reduced (Dosis Reducida)
    if "dosis reducida" in action_text:
        # Segunda prioridad - si se redujo la dosis
        return "2"
    
    # 3 = Dose increased (Dosis Aumentada)
    if "dosis aumentada" in action_text:
        # Tercera prioridad - si se aumentó la dosis
        return "3"
    
    # 4 = Dose not changed (Dosis no Modificada)
    if "dosis no modificada" in action_text:
        # Cuarta prioridad - si no se modificó la dosis
        return "4"
    
    # 9 = Not applicable
    if "observación/seguimiento médico del paciente" in action_text or "tratamiento terapéutico" in action_text:
        # Quinta prioridad - si solo hay observación o tratamiento terapéutico
        return "9"
    
    # 0 = Unknown (default)
    return "0"

def get_qualification(qualification):
    if qualification.lower() == 'medico consultante':
        return "1"
    elif qualification.lower() == 'farmacéutico':
        return "2"
    elif qualification.lower() == 'otro profesional de la salud':
        return "3"
    elif qualification.lower() == 'referente farmacovigilancia':
        return "3"
    else:
        return "3"
    
def get_type_of_report(type_of_report):
    if type_of_report.lower() == 'consulta espontánea':
        return "1"
    elif type_of_report.lower() == 'reporte de estudio':
        return "2"
    else:
        return "3"
    
def get_age(years, months, weeks, days, hours):
    """
    Determines the age value and unit based on multiple age fields.
    Returns the most significant non-zero age value and its corresponding unit.
    
    Args:
        years: Age in years
        months: Age in months
        weeks: Age in weeks
        days: Age in days
        hours: Age in hours
        
    Returns:
        tuple: (age_value, age_unit) where age_unit is one of: "a" (years), 
               "mo" (months), "wk" (weeks), "d" (days), "hr" (hours)
    """
    # Convert all values to strings and strip whitespace
    years = str(years).strip() if years else "0"
    months = str(months).strip() if months else "0"
    weeks = str(weeks).strip() if weeks else "0"
    days = str(days).strip() if days else "0"
    hours = str(hours).strip() if hours else "0"
    
    # Convert to integers for comparison
    try:
        years_int = int(years)
        months_int = int(months)
        weeks_int = int(weeks)
        days_int = int(days)
        hours_int = int(hours)
    except ValueError:
        return "", ""
    
    # Return the most significant non-zero age value
    if years_int > 0:
        return years, "a"
    elif months_int > 0:
        return months, "mo"
    elif weeks_int > 0:
        return weeks, "wk"
    elif days_int > 0:
        return days, "d"
    elif hours_int > 0:
        return hours, "hr"
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
    
    # 1 = recovered/resolved
    if "recuperado/resuelto sin secuelas" in outcome_value:
        return "1"
    
    # 2 = recovering/resolving
    if "en proceso de recuperación o resolviéndose" in outcome_value:
        return "2"
    
    # 3 = not recovered/not resolved/ongoing
    if "no recuperado/no resuelto" in outcome_value:
        return "3"
    
    # 4 = recovered/resolved with sequelae
    if "recuperado/resuelto con secuelas" in outcome_value:
        return "4"
    
    # 5 = fatal
    if "fallecido" in outcome_value:
        return "5"
    
    # 0 = unknown
    if "desconocido" in outcome_value:
        return "0"
    
    # Si no coincide con ninguno de los valores conocidos, asumimos desconocido
    return "0"