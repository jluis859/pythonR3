import clr
import sys
import csv
import io
import pandas as pd
from System.Collections.Generic import List
from System.IO import FileStream, FileMode, FileAccess
from sv_r3_helper import *

# Add the path to the directory containing your .NET DLL
#sys.path.append(r'C:\Repos\Python R3Model\R3Model')
sys.path.append('/Users/jluis859/Python_Workspace/Python R3Model/R3Model')

# Load the .NET assembly
clr.AddReference('Umc.R3Model.ConceptualModel')
clr.AddReference('Umc.R3Model.E2BR3')
clr.AddReference('Umc.R3Model.ICHModel')
clr.AddReference('System.Collections')
from System.Collections.Generic import List

# Import the namespaces
from Umc.R3Model.ConceptualModel import Icsr, IdentificationOfTheCaseSafetyReport, NarrativeCaseSummaryAndOtherInformation, PrimarySourcesOfInformation, InformationOnSenderOfCaseSafetyReport, LiteratureReference, StudyIdentification, PatientCharacteristics, ReactionEvent, DrugInformation, ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient, Assessment, IncludedDocument, OtherCaseIdentifiers, NullFlavor, TrueOnly, StructuredInformationonRelevantMedicalHistory, RelevantPastDrugHistory, ReportedCausesOfDeath, AutopsyDeterminedCausesOfDeath, ForAParentChildFoetusReportInformationConcerningParent, StructuredInformationOfParent, RelevantPastDrugHistoryOfParent, DiluentInformation, HealthFacility, DosageInformation, IndicationForUseInCase, DrugreactionsEventsMatrix, AdditionalInformationOnDrug, SubstanceSpecifiedSubstanceIdentifierAndStrength, CaseSummaryAndReportersCommentsInNativeLanguage
from Umc.R3Model.E2BR3.ICSRToR3.Mapping import E2BR3MapperFactory, IcsrWithIncludedDocuments, MappingParameters
from Umc.R3Model.E2BR3.ICSRToR3 import MemoryStreamGenerator
from Umc.R3Model.ConceptualModel import CausalityAssessment, CausalityAssessmentResult

from datetime import datetime

# Define functions
def mapping_parameters(info):
    now = datetime.now()
    mp = MappingParameters(
        info.BatchNumber,  
        info.SenderIdentifier,  
        info.ReceiverIdentifier, 
        authorityOrgName=info.SenderName, 
        currentDateTime=now.strftime("%Y%m%d%H%M%S")+"+0000"         
    )
    return mp
    
def write(exn_handler, info, stream, icsr_list):
    now = datetime.now()
    parameters = mapping_parameters(info)
    
    items = List[IcsrWithIncludedDocuments]()
    for icsrWithIncludedDocuments in icsr_list:
        try:
            items.Add(icsrWithIncludedDocuments)
        except Exception as e:
            print(f"Error al agregar ICSR a la lista: {e}")
            continue  # Continúa con el siguiente ítem si hay un error

    mapper = E2BR3MapperFactory.CreateDefaultMapper()
    result = mapper.Map(items, parameters)

    # Crear un diccionario para mapear los IDs con sus índices
    id_to_index = {item.Icsr.IdentificationOfTheCaseSafetyReport.WorldWideUniqueCaseIdentificationNumber: i for i, item in enumerate(items)}

    if result.MappingExceptions.Count > 0:
        print(f"Se encontraron {result.MappingExceptions.Count} errores durante el mapeo:")
        
        # Crear un diccionario para contar los tipos de errores
        error_types = {}
        
        for exception_pair in result.MappingExceptions:
            # Obtener el ICSR y la excepción del KeyValuePair
            icsr = exception_pair.Key
            exception = exception_pair.Value
            
            # Obtener el ID correspondiente
            id = icsr.IdentificationOfTheCaseSafetyReport.WorldWideUniqueCaseIdentificationNumber
            
            # Obtener el índice correspondiente al ID
            index = id_to_index.get(id)
            
            # Obtener el tipo de error (la primera línea del mensaje de error)
            error_type = str(exception).split('\n')[0]
            
            # Incrementar el contador para este tipo de error
            if error_type in error_types:
                error_types[error_type] += 1
            else:
                error_types[error_type] = 1
            
            # Imprimir el error con su ID correspondiente
            print(f"  - Error en ID {id} (índice {index}): {error_type}")
        
        # Imprimir un resumen de los tipos de errores
        print("\nResumen de tipos de errores:")
        for error_type, count in error_types.items():
            print(f"  - {error_type}: {count} ocurrencia(s)")
        
        print("Continuando con el proceso a pesar de los errores...")

    MemoryStreamGenerator.Generate(stream, result.Result, indent=False)

# Define the TransmissionIdentification class (assuming it's defined in your .NET assembly)
class TransmissionIdentification:
    def __init__(self, batch_number, sender_identifier, receiver_identifier, sender_name):
        self.BatchNumber = batch_number
        self.SenderIdentifier = sender_identifier
        self.ReceiverIdentifier = receiver_identifier
        self.SenderName = sender_name

# Leer hasta 100 registros del Excel
MAX_RECORDS = 100
TEST_MODE = False

data_sv_list = []
with open('Data_SV/base_SIFAVES_50_registro.csv', 'r', encoding='utf-8-sig') as file:
    csv_reader = csv.DictReader(io.StringIO(file.read()))
    for _ in range(MAX_RECORDS):
        try:
            data_sv = next(csv_reader)
            data_sv_list.append(data_sv)
        except StopIteration:
            break

# Crear una lista para almacenar todos los ICSRs
icsr_list = List[IcsrWithIncludedDocuments]()
reporteIndex = 1

# Procesar cada registro
for data_sv in data_sv_list:
    fecha_reporte_msp = process_date(data_sv['Fecha de Ingreso al Sistema'])
    fecha_evento = process_date_time(data_sv['Fecha/ Hora inicio Reacción']) 
    fecha_evento_fin = process_date(data_sv['Fecha Resolución Evento']) 
    

    # Fill R3 model with data
    info = TransmissionIdentification(
        batch_number="Batch123",            # N.1.2
        sender_identifier="TEST",   # N.1.3 & N.2.r.2
        receiver_identifier="UMC",          # N.1.4 & N.2.r.3
        sender_name="TEST"
    )

    if not TEST_MODE:
        info = TransmissionIdentification(
            batch_number="Batch123",            # N.1.2
            sender_identifier="SRS SV",   # N.1.3 & N.2.r.2
            receiver_identifier="UMC",          # N.1.4 & N.2.r.3
            sender_name="SRS El Salvador"
        )

    #print(data_sv.keys())
    case_number = data_sv['Código Reporte']
    identification = IdentificationOfTheCaseSafetyReport()                                        

    #Report identification
    if TEST_MODE:
        identification.WorldWideUniqueCaseIdentificationNumber = "TEST-" + case_number    
        identification.SendersCaseSafetyReportUniqueIdentifier = "TEST-" + case_number 
    else:
        identification.WorldWideUniqueCaseIdentificationNumber = "SV-SRS-" + case_number    
        identification.SendersCaseSafetyReportUniqueIdentifier = "SV-SRS-" + case_number 
    identification.FirstSenderOfThisCase = "1"                                          
    identification.TypeOfReport = get_type_of_report(data_sv['Forma Detección'])      
    identification.DateReportWasFirstReceivedFromSource = fecha_reporte_msp                   
    identification.DateOfMostRecentInformationForThisReport = fecha_reporte_msp    
    identification.DateOfCreation = fecha_reporte_msp         
    identification.OtherCaseIdentifiersInPreviousTransmissions = TrueOnly(1, True)      
    identification.OtherCaseIdentifiersInPreviousTransmissionsNullFlavor = NullFlavor.NI
    identification.ReportNullificationAmendment = ""                                    
    identification.ReasonForNullificationAmendment = ""    

    # UMC extensions
    identification.AefiCase = False                                                     
    identification.NotificationDate = fecha_reporte_msp                                                
    identification.DateOfReport = fecha_reporte_msp           
    identification.ReportTitle = case_number + ": " + data_sv['Título Reporte']

    print(f"\nReporte SRS {reporteIndex}: {identification.ReportTitle}")
    reporteIndex+=1

    # Other case identifiers
    othercaseIdentifier = OtherCaseIdentifiers()
    if TEST_MODE:   
        othercaseIdentifier.SourcesOfTheCaseIdentifier = "TEST-" + case_number
    else: 
        othercaseIdentifier.SourcesOfTheCaseIdentifier = "SV-SRS-" + case_number
    othercaseIdentifier.CaseIdentifier = case_number
    othercaseIdentifiers = List[OtherCaseIdentifiers]()
    othercaseIdentifiers.Add(othercaseIdentifier)
    identification.OtherCaseIdentifiers = othercaseIdentifiers

    # Narrative
    narrative = NarrativeCaseSummaryAndOtherInformation()

    # Construir la narrativa
    narrative_text = ""
    if data_sv.get('Fecha Detección Caso'):
        narrative_text += "Fecha detección: " + data_sv['Fecha Detección Caso']
    
    if data_sv.get('Descripción Clínica / Cuadro / evento Crr'):
        if narrative_text:
            narrative_text += " | "
        narrative_text += "Cuadro: " + data_sv['Descripción Clínica / Cuadro / evento Crr']

    if data_sv.get('Información Adicional Crr'):
        if narrative_text:
            narrative_text += " | "
        narrative_text += "Info adicional: " + data_sv['Información Adicional Crr']

    reporter_text = ""

    narrative.CaseNarrativeIncludingClinicalCourseTherapeuticMeasuresOutcomeAndAdditionalRelevantInformation = narrative_text

    narrative.ReportersComment = reporter_text
    narrative.SendersComment = ""
    caseSummaryAndReportersCommentsInNativeLanguage = CaseSummaryAndReportersCommentsInNativeLanguage()
    caseSummaryAndReportersCommentsInNativeLanguage.CaseSummaryAndReportersCommentsText = ""
    caseSummaryAndReportersCommentsInNativeLanguage.CaseSummaryAndReportersCommentsLanguage = ""
    caseSummaryAndReportersCommentsInNativeLanguages = List[CaseSummaryAndReportersCommentsInNativeLanguage]()
    caseSummaryAndReportersCommentsInNativeLanguages.Add(caseSummaryAndReportersCommentsInNativeLanguage)
    narrative.CaseSummaryAndReportersCommentsInNativeLanguage = caseSummaryAndReportersCommentsInNativeLanguages

    #Primary Source
    primary_source = PrimarySourcesOfInformation()
    primary_source.Qualification = get_qualification(data_sv['Tipo Notificador'])
    primary_source.PrimarySourceForRegulatoryPurposes = True
    primary_source.ReportersOrganisation = data_sv['Unidad Efectora']
    primary_source.ReportersGivenName = data_sv['Nombre Notificador']
    primary_source.ReportersDepartment = ""
    if TEST_MODE:
        primary_source.ReportersCountryCode = "UY"
    else:
        primary_source.ReportersCountryCode = "SV"
    primary_source.ReportersTelephone = ""
    primary_source.QualificationFreetext = ""
    primary_sources = List[PrimarySourcesOfInformation]()
    primary_sources.Add(primary_source)

    # Sender
    sender_info = InformationOnSenderOfCaseSafetyReport()
    if TEST_MODE:   
        sender_info.SendersOrganisation = "TEST SendersOrganisation"   
        sender_info.SendersDepartment = "TEST SendersDepartment" 
        sender_info.SendersStreetAddress = "TEST SendersStreetAddress"
        sender_info.SendersCity = "TEST SendersCity"
        sender_info.SendersStateOrProvince = "TEST State"
        sender_info.SendersPostcode = "01009"
        sender_info.SendersCountryCode = "UY"
        sender_info.SendersTelephone = "55555555"
    else: 
        sender_info.SendersOrganisation = "SRS"
        sender_info.SendersDepartment = "DEPARTAMENTO DE FARMACOVIGILANCIA Y COSMETOVIGILANCIA SRS"
        sender_info.SendersStreetAddress = "Blv. Merliot y Av. Jayaque, Edif. DNM, 2 Nivel, Urb. Jardines del Volcan"
        sender_info.SendersCity = "Santa Tecla"
        sender_info.SendersStateOrProvince = "La Libertad"
        sender_info.SendersPostcode = "CP-0511"
        sender_info.SendersCountryCode = "SV"
        sender_info.SendersTelephone = "+503 25225056"

    sender_info.SenderType = "2" 

    # Patient characteristics
    patient_characteristics = PatientCharacteristics()
    patient_characteristics.PatientNameOrInitials = data_sv['Iniciales']

    # Edad y unidad de edad
    years = data_sv['Edad Años']
    months = data_sv['Edad Meses']
    weeks = data_sv['Edad Semanas']
    days = data_sv['Edad Días']
    hours = data_sv['Edad Horas']
    
    age_value, age_unit = get_age(years, months, weeks, days, hours)
    
    patient_characteristics.AgeAtTimeOfOnsetOfReactionEvent = age_value
    patient_characteristics.AgeAtTimeOfOnsetOfReactionEventUnit = age_unit

    dob = process_date(data_sv['Fecha Nacimiento'])

    patient_characteristics.DateOfBirth = dob

    # Fecha de muerte
    deathDate = process_date(data_sv['Fecha Muerte Paciente'])
    patient_characteristics.DateOfDeath = deathDate

    # Embarazo
    patient_characteristics.Pregnant = is_pregnant(
        data_sv['Sexo'], 
        data_sv['Días de Embarazo'], 
        data_sv['Semanas de Embarazo'], 
        data_sv['Meses de Embarazo'], 
        data_sv['Trimestres de Embarazo']
    )

    patient_characteristics.Lactating = False

    # Peso
    weight_value = process_weight(data_sv['Peso Paciente'])
    if weight_value:
        patient_characteristics.BodyWeight = str(weight_value)
    else:
        patient_characteristics.BodyWeight = ""
    # patient_characteristics.Height = ""

    # Sexo
        # Sexo
    if data_sv['Sexo'] == "M":
        patient_characteristics.Sex = "1"
    elif data_sv['Sexo'] == "F":
        patient_characteristics.Sex = "2"
    elif data_sv['Sexo'] == "D":
        patient_characteristics.SexNullFlavor = NullFlavor.UNK
    else:
        patient_characteristics.SexNullFlavor = NullFlavor.UNK

    # Medical history 
    medical_history_text = ""
    if data_sv.get('Antecedentes Médicos Crr'):
        medical_history_text += data_sv['Antecedentes Médicos Crr']

    if data_sv.get('Reacción a otros medicamentos'):
        if medical_history_text:
            medical_history_text += " | "
        medical_history_text += "Reaccion otros medicamentos: " + data_sv['Reacción a otros medicamentos']

    if data_sv.get('Otras Reacciones Crr'):
        if medical_history_text:
            medical_history_text += " | "
        medical_history_text += "Otras Reacciones: " + data_sv['Otras Reacciones Crr']
    
    patient_characteristics.TextForRelevantMedicalHistoryAndConcurrentConditionsNotIncludingReactionEvent = medical_history_text
    #patient_characteristics.ConcomitantTherapies = TrueOnly(1, True)

    def create_reaction_event(reaction_id, reaction_text, meddra_code, fecha_evento, fecha_evento_fin = "",
                            results_in_death=False, life_threatening=False, 
                            caused_prolonged_hospitalisation=False, disabling_incapacitating=False,
                            congenital_anomaly_birth_defect=False, other_medically_important_condition=False,
                            #country_code="UY", language="spa", meddra_version="27.0"):
                            country_code="SV", language="spa", meddra_version="27.0"):
        reaction_event = ReactionEvent()
        reaction_event.ReactionReferenceId = reaction_id
        reaction_event.ReactionEventAsReportedByThePrimarySource = reaction_text
        reaction_event.ReactionEventAsReportedByThePrimarySourceLanguage = language
        reaction_event.DateOfStartOfReactionEvent = fecha_evento
        reaction_event.DateOfEndOfReactionEvent = fecha_evento_fin
        reaction_event.OutcomeOfReactionEventAtTheTimeOfLastObservation = get_outcome(data_sv['Condición paciente'])
        reaction_event.IdentificationOfTheCountryWhereTheReactionEventOccurred = country_code
        reaction_event.ReactionEventMedDRAVersion = meddra_version
        reaction_event.ReactionEventMedDRACode = meddra_code
        
        #Seriousness information (Use either TrueOnly or the Nullflavor row)
        if results_in_death:
            reaction_event.ResultsInDeath = TrueOnly(1, True)
        else:
            reaction_event.ResultsInDeathNullFlavor = NullFlavor.NI
        
        if life_threatening:
            reaction_event.LifeThreatening = TrueOnly(1, True)
        else:
            reaction_event.LifeThreateningNullFlavor = NullFlavor.NI
        
        if caused_prolonged_hospitalisation:
            reaction_event.CausedProlongedHospitalisation = TrueOnly(1, True)
        else:
            reaction_event.CausedProlongedHospitalisationNullFlavor = NullFlavor.NI
        
        if disabling_incapacitating:
            reaction_event.DisablingIncapacitating = TrueOnly(1, True)
        else:
            reaction_event.DisablingIncapacitatingNullFlavor = NullFlavor.NI
        
        if congenital_anomaly_birth_defect:
            reaction_event.CongenitalAnomalyBirthDefect = TrueOnly(1, True)
        else:
            reaction_event.CongenitalAnomalyBirthDefectNullFlavor = NullFlavor.NI
        
        if other_medically_important_condition:
            reaction_event.OtherMedicallyImportantCondition = TrueOnly(1, True)
        else:
            reaction_event.OtherMedicallyImportantConditionNullFlavor = NullFlavor.NI
        
        return reaction_event

        # Reaction (add all reactions to this list)
    reaction_events = List[ReactionEvent]()

    # Crear una lista para almacenar las reacciones válidas
    valid_reactions = []

    # Procesar la reacción principal
    ram_key = 'LLT MODIFICADO'
    meddra_key = 'LLT CODE'
    
    # Verificar si existe la RAM y tiene un código MedDRA válido
    if ram_key in data_sv and data_sv[ram_key] and meddra_key in data_sv:
        try:
            meddra_code = data_sv.get(meddra_key, '')
            
            # Verificar si el código MedDRA es válido (no está vacío y no es -1)
            if meddra_code and meddra_code != '-1':
                # Crear un diccionario con la información de la reacción
                reaction_info = {
                    'text': data_sv[ram_key],
                    'code': int(meddra_code)
                }
                
                valid_reactions.append(reaction_info)
                print(f"Reacción agregada: {reaction_info['text']} con código MedDRA: {reaction_info['code']}")
        except ValueError:
            print(f"Advertencia: No se pudo convertir '{meddra_key}' a un entero. Valor encontrado: {data_sv.get(meddra_key)}. Omitiendo esta reacción.")

    # Verificar si hay al menos una reacción válida
    if not valid_reactions:
        print("ERROR: No se encontró ninguna reacción válida con código MedDRA. Se requiere al menos una reacción.")
        raise Exception("No se encontraron reacciones válidas con código MedDRA. El proceso ha sido detenido.")

    # Ahora crear los objetos ReactionEvent para cada reacción válida
    for reaction in valid_reactions:
        reaction_id = generate_guid()  # Genera un GUID único para cada reacción
        
        # Determinar la seriedad basada en los datos de El Salvador
        is_serious = data_sv.get('Razón de seriedad') == '1'
        
        # Inicializar variables para los criterios de seriedad
        results_in_death = False
        life_threatening = False
        caused_prolonged_hospitalisation = False
        disabling_incapacitating = False
        congenital_anomaly_birth_defect = False
        other_medically_important_condition = False
        
        # Si es serio, determinar el criterio específico
        if is_serious:
            criterio = data_sv.get('Criterio', '')
            
            if criterio == 'No hubo muerte en el evento':
                # Aqui que se hace? hay que poner algo cuando es serio.
                other_medically_important_condition = True
            elif criterio == 'Amenaza de la Vida':
                life_threatening = True
            elif criterio == 'Anomalía Congénita':
                congenital_anomaly_birth_defect = True
            elif criterio == 'Hospitalización/Prolongada':
                caused_prolonged_hospitalisation = True
            elif criterio == 'Muerte':
                results_in_death = True
            elif criterio == 'Otra Condición Médica Importante':
                other_medically_important_condition = True
        
        reaction_event = create_reaction_event(
            reaction_id=reaction_id,
            reaction_text=reaction['text'],
            meddra_code=reaction['code'],
            fecha_evento=fecha_evento,
            fecha_evento_fin=fecha_evento_fin,
            results_in_death=results_in_death,
            life_threatening=life_threatening,
            caused_prolonged_hospitalisation=caused_prolonged_hospitalisation,
            disabling_incapacitating=disabling_incapacitating,
            congenital_anomaly_birth_defect=congenital_anomaly_birth_defect,
            other_medically_important_condition=other_medically_important_condition
        )
        # Adds reactions to list
        reaction_events.Add(reaction_event)

    def create_drug_information(drug_id, drug_name, who_drug_id, active_ingredient, dosage_text, route_admin, characterisation_role="1", action_taken=""):
        drug_information = DrugInformation()    
        drug_information.DrugReferenceId = drug_id
        drug_information.CharacterisationOfDrugRole = characterisation_role # Sospechoso
        drug_information.MedicinalProductNameAsReportedByThePrimarySource = drug_name
        
        # WHO Drug information
        if who_drug_id and who_drug_id != '-1':
            try:
                drug_information.MedicinalProductIdentifierWHODrugVersion = "20240830"
                drug_information.MedicinalProductIdentifierWHODrugProductId = int(who_drug_id)
            except ValueError:
                print(f"Advertencia: No se pudo convertir WHO Drug ID '{who_drug_id}' a un entero.")
        
        # Dose information
        dosageInformations = List[DosageInformation]()
        dosageInformation = DosageInformation()
        dosageInformation.Dose = ""
        dosageInformation.DoseUnit = ""
        dosageInformation.DoseNumber = ""
        dosageInformation.DosageText = dosage_text
        dosageInformation.RouteOfAdministration = route_admin
        dosageInformations.Add(dosageInformation)
        drug_information.DosageInformations = dosageInformations
        drug_information.ActionsTakenWithDrug = action_taken

        print(f"ActionsTakenWithDrug: {drug_information.ActionsTakenWithDrug}")

        #TODO revisar todas las variables de medicamento hay varias que faltan como la fecha de inicio y fin
        
        # Additional information on drug
        additionalInformationOnDrugs = List[AdditionalInformationOnDrug]()
        additionalInformationOnDrug = AdditionalInformationOnDrug()
        additionalInformationOnDrug.AdditionalInformationOnDrugCoded = ""
        additionalInformationOnDrugs.Add(additionalInformationOnDrug)
        drug_information.AdditionalInformationOnDrugs = additionalInformationOnDrugs
        drug_information.AdditionalInformationOnDrug = ""
        
        # Substance information - Principio activo
        if active_ingredient:
            substanceSpecifiedSubstanceIdentifierAndStrengths = List[SubstanceSpecifiedSubstanceIdentifierAndStrength]()
            substanceSpecifiedSubstanceIdentifierAndStrength = SubstanceSpecifiedSubstanceIdentifierAndStrength()
            substanceSpecifiedSubstanceIdentifierAndStrength.SubstanceSpecifiedSubstanceName = active_ingredient
            substanceSpecifiedSubstanceIdentifierAndStrengths.Add(substanceSpecifiedSubstanceIdentifierAndStrength)
            drug_information.SubstanceSpecifiedSubstanceIdentifierAndStrengths = substanceSpecifiedSubstanceIdentifierAndStrengths
        
        return drug_information

    # Drug section (add items to list)
    drug_informations = List[DrugInformation]()
    drug_name=data_sv['IFA(S) SOSPECHOSO(S) (SPA)']
    who_drug_id= data_sv['IFA(S) SOSPECHOSO(S) (SPA) MPID']
    # Sospechoso
    drug_id = generate_guid() 
    drug_info = create_drug_information(
        drug_id=drug_id,
        drug_name=drug_name,
        who_drug_id= who_drug_id,
        active_ingredient="-",
        dosage_text=data_sv['A # d Dosis']+data_sv['A Dosis U'],
        route_admin=data_sv['ROA Crr'],
        action_taken=get_action_taken(data_sv['Acción tomada'])
    )

    print(f"Medicamento sospechoso agregado: {drug_name} - {who_drug_id}")
        
    drug_informations.Add(drug_info)

    # Concomitantes,
    for i in range(1, 8):
        drug_key = f'IFA CC {i}'
        who_drug_key = f'IFA CC {i} MPID'
        dosage_text_key_1 = f'CC # d Dosis {i}'
        dosage_text_key_2 = f'CC Dosis U {i}'
        route_admin_key = f'CC ROA {i}'
        
        # Verificar si existe el medicamento
        if (drug_key in data_sv and data_sv[drug_key]):
            drug_id = generate_guid()  # Genera un GUID único para cada medicamento
            drug_name = data_sv[drug_key]
            who_drug_id = data_sv.get(who_drug_key, '')

            active_ingredient = ''
            dosage_text = dosage_text_key_1 + dosage_text_key_2
            route_admin = route_admin_key
            
            # Crear el objeto DrugInformation y agregarlo a la lista
            drug_info = create_drug_information(
                drug_id=drug_id,
                drug_name=drug_name,
                who_drug_id=who_drug_id,
                active_ingredient=active_ingredient,
                dosage_text=dosage_text,
                route_admin=route_admin,
                characterisation_role="2",
                action_taken=""
            )
            
            drug_informations.Add(drug_info)
            print(f"Medicamento Concomitante {i} agregado: {drug_name}")

   # Crear el objeto Assessment con la información de causalidad
    assessment = Assessment()

    causalityAssessments = List[CausalityAssessment]()

    # Crear un objeto CausalityAssessment
    causalityAssessment = CausalityAssessment()
    causalityAssessment.MethodOfAssessment = data_sv['Metodo de analisis para clasificación']  # Método de evaluación (WHO-UMC, Naranjo, etc.)
    if TEST_MODE:
        causalityAssessment.SourceOfAssessment = "TEST"  # Fuente de la evaluación
    else:
        causalityAssessment.SourceOfAssessment = "SRS-SV"  # Fuente de la evaluación

    # Crear la lista de CausalityAssessmentResult
    causalityAssessmentResults = List[CausalityAssessmentResult]()
    
    # Filtrar solo los medicamentos sospechosos para la evaluación de causalidad
    suspected_drugs = [drug for drug in drug_informations if drug.CharacterisationOfDrugRole == "1"]

    # Para cada medicamento y reacción, crear un resultado de causalidad
    for reaction_event in reaction_events:
        for drug_info in suspected_drugs:
            causalityAssessmentResult = CausalityAssessmentResult()
            causalityAssessmentResult.DrugReferenceId = drug_info.DrugReferenceId
            causalityAssessmentResult.ReactionReferenceId = reaction_event.ReactionReferenceId
            
            # Obtener el resultado de la evaluación de causalidad del CSV
            if data_sv.get('Clasificación por causalidad RAM', ''):
                causalityAssessmentResult.ResultOfAssessment = data_sv['Clasificación por causalidad RAM']
            else:
                causalityAssessmentResult.ResultOfAssessment = ""  # Valor por defecto
                
            causalityAssessmentResults.Add(causalityAssessmentResult)

    print(f"Causalidad agregado: {data_sv['Metodo de analisis para clasificación']} - {data_sv['Clasificación por causalidad RAM']}")

    # Asignar los resultados de causalidad al objeto CausalityAssessment
    causalityAssessment.CausalityAssessmentResults = causalityAssessmentResults

    # Agregar el objeto CausalityAssessment a la lista
    causalityAssessments.Add(causalityAssessment)

    # Asignar la lista de CausalityAssessment al objeto Assessment
    assessment.CausalityAssessments = causalityAssessments

    # Test results (add to list)
    test_results = List[ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient]()
    test_result = ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient()
    test_result.TestResult = data_sv['Otros Procedimientos Realizados Crr']
    test_results.Add(test_result)

    # Create an instance of the Icsr class and set its properties
    icsr = Icsr()
    icsr.IdentificationOfTheCaseSafetyReport = identification
    icsr.NarrativeCaseSummaryAndOtherInformation = narrative
    icsr.PrimarySourcesOfInformations = primary_sources
    icsr.InformationOnSenderOfCaseSafetyReport = sender_info
    icsr.PatientCharacteristics = patient_characteristics
    icsr.ReactionEvents = reaction_events
    icsr.DrugInformations = drug_informations
    icsr.ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient = test_results
    icsr.Assessment = assessment

    # Crear IcsrWithIncludedDocuments y agregarlo a la lista
    icsrWithIncludedDocuments = IcsrWithIncludedDocuments()
    icsrWithIncludedDocuments.Icsr = icsr
    icsrWithIncludedDocuments.IncludedDocuments = List[IncludedDocument]()  # Lista vacía de documentos incluidos
    icsr_list.Add(icsrWithIncludedDocuments)

# Fuera del bucle, escribir todos los ICSRs
stream = FileStream(f"Output/sv_output.xml", FileMode.Create, FileAccess.Write)

# Write E2B R3 XML to the file
write(exn_handler, info, stream, icsr_list)


