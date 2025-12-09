import uuid
from datetime import datetime, timedelta

def generate_guid():
    """Genera un GUID único"""
    return str(uuid.uuid4())

# Define your exn_handler function
def exn_handler(exception):
    print(f"Validation exception: {exception}")

def clean_sin_datos(data_dict):
    """
    Limpia todas las variables en un diccionario, convirtiendo valores que contienen "sin dato" a cadena vacía.
    
    Args:
        data_dict: Diccionario con los datos a limpiar
        
    Returns:
        Diccionario con los valores que contienen "sin dato" convertidos a cadenas vacías
    """
    cleaned_dict = {}
    for key, value in data_dict.items():
        if isinstance(value, str) and ("sin dato" in value.lower() or "sin doto" in value.lower()):
            cleaned_dict[key] = ""
        else:
            cleaned_dict[key] = value
    return cleaned_dict


def process_date(date_string):
    if not date_string or date_string.lower().strip() == "sin datos":
        return ""
    
    # Convertir a string si no lo es
    date_string = str(date_string).strip()
    
    try:
        # Verificar si es un número de Excel (fecha serial)
        try:
            if date_string.isdigit() and len(date_string) == 5:
                # Convertir número de Excel a fecha
                excel_date = int(date_string)
                
                # Sistema 1900 (Windows Excel)
                base_date = datetime(1900, 1, 1)
                fecha_obj = base_date + timedelta(days=excel_date-2)  # -2 por ajuste de Excel
                
                result = fecha_obj.strftime("%Y%m%d")
                print(f"Convertida fecha Excel: {date_string} -> {result} (año: {fecha_obj.year}, mes: {fecha_obj.month}, día: {fecha_obj.day})")
                return result
        except (ValueError, OverflowError):
            pass
            
        # Manejar formato "mes-año" como "setiembre-16"
        month_year_result = process_month_year(date_string)
        if month_year_result:
            return month_year_result
            
        # Intentar con formato dd/mm/yyyy
        try:
            fecha_obj = datetime.strptime(date_string, "%d/%m/%Y")
            return fecha_obj.strftime("%Y%m%d")
        except ValueError:
            # Intentar con formato dd/mm/yy
            try:
                fecha_obj = datetime.strptime(date_string, "%d/%m/%y")
                return fecha_obj.strftime("%Y%m%d")
            except ValueError:
                # Si falla, intentar con formato yyyy-mm-dd
                try:
                    fecha_obj = datetime.strptime(date_string, "%Y-%m-%d")
                    return fecha_obj.strftime("%Y%m%d")
                except ValueError:
                    # Si falla, intentar con formato mm/yy (para fechas como 00/01/09)
                    try:
                        if date_string.count('/') == 2 and date_string.startswith('00/'):
                            # Extraer solo la parte mm/yy
                            mm_yy = date_string[3:]
                            fecha_obj = datetime.strptime(mm_yy, "%m/%y")
                            return fecha_obj.strftime("%Y%m00")  # Día como 00
                    except ValueError:
                        pass
                        
                    # Si todas las conversiones fallan, lanzar ValueError
                    raise ValueError(f"Formato de fecha no reconocido: {date_string}")
    except ValueError:
        print(f"Error: La fecha '{date_string}' no es válida.")
        return ""


def process_month_year(date_string):
    """
    Procesa fechas en formato "mes-año" como "setiembre-16" y devuelve el formato YYYYMM
    """
    try:
        parts = ""
        if "-" in date_string or "/" in date_string:
            if "-" in date_string:
                parts = date_string.split("-")
            if "/" in date_string:
                parts = date_string.split("/")
            if len(parts) == 2:
                month_name = parts[0].lower().strip()
                year_str = parts[1].strip()
                
                # Mapeo de nombres de meses en español
                month_map = {
                    "enero": 1, "feb.":2, "febrero": 2, "marzo": 3, "abril": 4,
                    "myo": 5, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
                    "setiembre": 9, "set": 9, "septiembre": 9, "octubre": 10,
                    "noviembre": 11, "nov.": 11, "diciembre": 12, "dic": 12
                }
                
                if month_name in month_map and year_str.isdigit():
                    month = month_map[month_name]
                    # Determinar si el año es de 2 o 4 dígitos
                    if len(year_str) == 2:
                        year = 2000 + int(year_str) if int(year_str) < 50 else 1900 + int(year_str)
                    else:
                        year = int(year_str)
                    
                    result = f"{year}{month:02d}"
                    print(f"Convertida fecha mes-año: {date_string} -> {result} (año: {year}, mes: {month})")
                    return result
    except (ValueError, KeyError):
        pass
    
    return None

def get_qualification(qualification):
    if qualification.lower() == 'médico':
        return "1"
    elif qualification.lower() == 'farmacéutico':
        return "2"
    elif qualification.lower() == 'consumidor u otro profesional no sanitario':
        return "5"
    else:
        return "" 
def get_age(age, unit):
    if not age or not unit:
        return "", ""
    
    age = str(age).strip()
    unit = unit.strip().lower()

    if unit in ['a', 'años', 'año', 'anos', 'ano']:
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
    if sex.lower() in ['m', 'mas']:
        return "1"
    elif sex.lower() in ['f', 'fem']:
        return "2"
    else:
        return ""

def is_pregnant(pregnancy_value, gestation_weeks):
    pregnancy_options = [
        "6 semanas", "7 semanas", "si", "si - 2do. Trim", 
        "si 11 semanas", "si 20 semanas", "si, 1er trimestre", 
        "si, 34 semanas", "si, 1° trimestre"
    ]
    is_pregnancy_option = pregnancy_value.lower().strip() in [option.lower() for option in pregnancy_options]
    has_gestation_weeks = gestation_weeks.strip() != ""
    
    return is_pregnancy_option or has_gestation_weeks

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
    recovered_values = [
        'recuperado', 'recuperada', 'recuperado cl.', 
        'maniobras de reanimación, recuperado', 'recuperado',
        'niega efectos adversos', 'sin complicaciones', 'sin daño', 'sin síntomas', 'no presento evento adverso',
    ]
    
    # 2 = recovering/resolving
    recovering_values = [
        'en recuperación', 'en recuperacion', 'en recuperción', 'en evolución', 'recuperación', 'recuperacion',
        'en evolucion', 'en consulta'
    ]
    
    # 3 = not recovered/not resolved/ongoing
    not_recovered_values = [
        'empeoramiento', 'empeoro', 'igual', 'determino hospitalización', 'no recuperado'
        'determino hospitalizacion', 'grave', 'continúa igual', 'continua igual'
    ]
    
    # 4 = recovered/resolved with sequelae
    sequelae_values = [
        
    ]
    
    # 5 = fatal
    fatal_values = [
        'fallece', 'fallecida', 'fallecimiento', 'muerte'
    ]
    
    # 0 = unknown
    unknown_values = [
        'desconoce', 'desconocida', 'se desconoce', 'sin dato', 'sin datos',
        'ver informe', 'otro', 'otros', 'otros?', 'otos', 'no corresponde',
        'no lo ingirió', 'no ingirió', 'hemodialisis', 'mantiene secuelas de patología de fondo'
    ]
    
    # Verificar en qué categoría cae el valor
    for value in recovered_values:
        if value in outcome_value:
            return "1"
            
    for value in recovering_values:
        if value in outcome_value:
            return "2"
            
    for value in not_recovered_values:
        if value in outcome_value:
            return "3"
            
    for value in sequelae_values:
        if value in outcome_value:
            return "4"
            
    for value in fatal_values:
        if value in outcome_value:
            return "5"
            
    for value in unknown_values:
        if value in outcome_value:
            return "0"
            
    # Si no coincide con ninguno de los valores conocidos, asumimos desconocido
    return "0"



# Notas
# Colocar Semanas de gestación en Caso Narrativo DONE
# Imputabilidad valores de número se van a buscar. Done
# Nueva integrante Fiorella
# Mapear outcome DONE
# Se mapeara el tipo de emisor y causalidad por parte de Ceci DONE


# ToDo concomitantes, falta ponerles codigo whodrug DONE
# Importar varios reportes DONE
# Vacunas
# Revisar si no hay RAM, revisar las otras variables.

# Revisar que tengan principio activo
# REVISAR: - Error en ID UY-MSP-TEST2-2007-1080 (índice 5): Required field is null or empty: C.3.1#

# info = TransmissionIdentification(
#         batch_number="Batch123",            # N.1.2
#         sender_identifier="SenderID",       # N.1.3 & N.2.r.2
#         receiver_identifier="ReceiverID",   # N.1.4 & N.2.r.3
#         sender_name="SenderName"
#     )

# Revisar critirios adicionales:
# Cumple requisitos minimos.
# Validadores de las dos fechas.
# Revisar duplicados.