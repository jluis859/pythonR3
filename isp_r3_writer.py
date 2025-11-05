import clr
import sys
import csv
import io
from System.Collections.Generic import List
from System.IO import FileStream, FileMode, FileAccess
from isp_r3_helper import *

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

data_isp_list = []
with open('Data_ISP/esavi_test.csv', 'r', encoding='utf-8-sig') as file:
    csv_reader = csv.DictReader(io.StringIO(file.read()))
    for _ in range(MAX_RECORDS):
        try:
            data_isp = next(csv_reader)
            data_isp_list.append(data_isp)
        except StopIteration:
            break

# Crear una lista para almacenar todos los ICSRs
icsr_list = List[IcsrWithIncludedDocuments]()

# Procesar cada registro
for data_isp in data_isp_list:
    fecha_reporte_isp = process_date(data_isp['Fecha Notificacion'])
    
    # Fill R3 model with data
    info = TransmissionIdentification(
        batch_number="Batch123",            # N.1.2
        sender_identifier="Test",   # N.1.3 & N.2.r.2
        #sender_identifier="ISP Chile",   # N.1.3 & N.2.r.2
        receiver_identifier="UMC",          # N.1.4 & N.2.r.3
        sender_name="TEST 1"
        #sender_name="ISP Chile"
    )

    #print(data_ury.keys())
    #case_number = data_isp['Referencia']
    case_number = "1234"
    identification = IdentificationOfTheCaseSafetyReport()                                        

    #Report identification
    identification.WorldWideUniqueCaseIdentificationNumber = "TEST-" + case_number    
    identification.SendersCaseSafetyReportUniqueIdentifier = "TEST-" + case_number 
    identification.FirstSenderOfThisCase = "1"                                          
    identification.TypeOfReport = "1"       
    identification.DateReportWasFirstReceivedFromSource = fecha_reporte_isp                   
    identification.DateOfMostRecentInformationForThisReport = fecha_reporte_isp    
    identification.DateOfCreation = fecha_reporte_isp         
    identification.OtherCaseIdentifiersInPreviousTransmissions = TrueOnly(1, True)      
    identification.OtherCaseIdentifiersInPreviousTransmissionsNullFlavor = NullFlavor.NI
    identification.ReportNullificationAmendment = ""                                    
    identification.ReasonForNullificationAmendment = ""    

    # UMC extensions
    identification.AefiCase = True                                                     
    identification.NotificationDate = fecha_reporte_isp                                                
    identification.DateOfReport = fecha_reporte_isp         
    # Not working ReportTitle: Organizacion + "RAM/Error" + Medicamento Sospechoso                                                                 
    identification.ReportTitle = "TEST-" + case_number

    # Other case identifiers
    othercaseIdentifier = OtherCaseIdentifiers()
    othercaseIdentifier.SourcesOfTheCaseIdentifier = "TEST-" + case_number
    othercaseIdentifier.CaseIdentifier = case_number
    othercaseIdentifiers = List[OtherCaseIdentifiers]()
    othercaseIdentifiers.Add(othercaseIdentifier)
    identification.OtherCaseIdentifiers = othercaseIdentifiers

    # Narrative
    narrative = NarrativeCaseSummaryAndOtherInformation()

    # Construir la narrativa incluyendo las semanas de gestación si están disponibles
    narrative_text = data_isp['Descripcion ESAVI']
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
    primary_source.Qualification = get_qualification(data_isp['Profesion'])
    primary_source.PrimarySourceForRegulatoryPurposes = True
    primary_source.ReportersOrganisation = "Test"
    primary_source.ReportersDepartment = ""
    primary_source.ReportersCountryCode = "UY"
    primary_source.ReportersTelephone = ""
    primary_source.QualificationFreetext = ""
    primary_sources = List[PrimarySourcesOfInformation]()
    primary_sources.Add(primary_source)

    # Sender
    sender_info = InformationOnSenderOfCaseSafetyReport()
    sender_info.SendersOrganisation = "TEST"    
    sender_info.SendersDepartment = "TEST"
    sender_info.SenderType = "1"                                       
    sender_info.SendersCountryCode = "UY"   

    # Patient characteristics
    patient_characteristics = PatientCharacteristics()
    patient_characteristics.PatientNameOrInitials = "ANONIMO"

    # Edad
    patient_characteristics.AgeAtTimeOfOnsetOfReactionEvent = data_isp['Edad N']

    # Determinar la unidad de edad según el valor en data_isp
    age_unit = data_isp.get('Edad U', '').upper().strip()
    if age_unit == 'AÑOS' or age_unit == 'ANOS':
        patient_characteristics.AgeAtTimeOfOnsetOfReactionEventUnit = "a"  # Years (annum)
    elif age_unit == 'MESES':
        patient_characteristics.AgeAtTimeOfOnsetOfReactionEventUnit = "mo"  # Months
    elif age_unit == 'DIAS':
        patient_characteristics.AgeAtTimeOfOnsetOfReactionEventUnit = "d"  # Days
    else:
        patient_characteristics.AgeAtTimeOfOnsetOfReactionEventUnit = "a"  # Default to years if not specified

        # Embarazo
    if data_isp.get('Embarazo', '').strip().upper() == "SÍ" or data_isp.get('Embarazo', '').strip().upper() == "SI":
        patient_characteristics.Pregnant = True
    else:
        patient_characteristics.Pregnant = False

    patient_characteristics.Lactating = False

    # Peso
    # weight_value = process_weight(data_isp['Peso Paciente'])
    # if weight_value:
    #     patient_characteristics.BodyWeight = str(weight_value)
    # else:
    #     patient_characteristics.BodyWeight = ""
    # patient_characteristics.Height = ""

    # Sexo
    if data_isp['Sexo'] == "Hombre":
        patient_characteristics.Sex = "1"
    elif data_isp['Sexo'] == "Mujer":
        patient_characteristics.Sex = "2"
    elif data_isp['Sexo'] == "Desconocido":
        patient_characteristics.SexNullFlavor = NullFlavor.UNK
    else:
        patient_characteristics.SexNullFlavor = NullFlavor.UNK

    # Medical history
    #patient_characteristics.TextForRelevantMedicalHistoryAndConcurrentConditionsNotIncludingReactionEvent = ""
    #patient_characteristics.ConcomitantTherapies = TrueOnly(1, True)

    def create_reaction_event(reaction_id, reaction_text, meddra_code, fecha_evento, 
                            results_in_death=False, life_threatening=False, 
                            caused_prolonged_hospitalisation=False, disabling_incapacitating=False,
                            congenital_anomaly_birth_defect=False, other_medically_important_condition=False,
                            country_code="UY", language="spa", meddra_version="27.0"):
        reaction_event = ReactionEvent()
        reaction_event.ReactionReferenceId = reaction_id
        reaction_event.ReactionEventAsReportedByThePrimarySource = reaction_text
        reaction_event.ReactionEventAsReportedByThePrimarySourceLanguage = language
        reaction_event.DateOfStartOfReactionEvent = fecha_evento
        reaction_event.OutcomeOfReactionEventAtTheTimeOfLastObservation = get_outcome(data_isp['Estado Paciente ESAVI'])
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
    ram_key = 'ESAVI WHOART'
    meddra_key = 'MedDRA code'
    
    # Obtener todas las fechas de inicio de eventos que pueden estar separadas por ||
    fechas_evento = [f.strip() for f in data_isp['Fecha Inicio ESAVI'].split('||') if f.strip()]
    
    # Verificar si existe la RAM y tiene un código MedDRA válido
    if ram_key in data_isp and data_isp[ram_key] and meddra_key in data_isp:
        # Separar las reacciones y códigos MedDRA por el delimitador "||"
        reactions = [r.strip() for r in data_isp[ram_key].split('||') if r.strip()]
        meddra_codes = [c.strip() for c in data_isp[meddra_key].split('||') if c.strip()]
        
        # Asegurarse de que tenemos el mismo número de reacciones y códigos
        min_length = min(len(reactions), len(meddra_codes))
        
        for i in range(min_length):
            try:
                meddra_code = meddra_codes[i]
                
                # Verificar si el código MedDRA es válido (no está vacío y no es -1)
                if meddra_code and meddra_code != '-1':
                    # Obtener la fecha correspondiente al índice actual
                    if i < len(fechas_evento):
                        fecha_evento_i = process_date(fechas_evento[i])
                    else:
                        fecha_evento_i = process_date(fechas_evento[0]) if fechas_evento else ""
                    
                    # Crear un diccionario con la información de la reacción
                    reaction_info = {
                        'text': reactions[i],
                        'code': int(meddra_code),
                        'fecha': fecha_evento_i
                    }
                    
                    valid_reactions.append(reaction_info)
                    print(f"Reacción agregada: {reaction_info['text']} con código MedDRA: {reaction_info['code']} y fecha: {fecha_evento_i}")
            except ValueError:
                print(f"Advertencia: No se pudo convertir el código MedDRA '{meddra_codes[i]}' a un entero. Omitiendo esta reacción.")

    # Verificar si hay al menos una reacción válida
    if not valid_reactions:
        print("ERROR: No se encontró ninguna reacción válida con código MedDRA. Se requiere al menos una reacción.")
        raise Exception("No se encontraron reacciones válidas con código MedDRA. El proceso ha sido detenido.")

    # Ahora crear los objetos ReactionEvent para cada reacción válida
    for reaction in valid_reactions:
        reaction_id = generate_guid()  # Genera un GUID único para cada reacción
        
        # Determinar la seriedad basada en los datos de El Salvador
        is_serious = data_isp.get('Seriedad Final') == 'Si'
        
        # Inicializar variables para los criterios de seriedad
        results_in_death = False
        life_threatening = False
        caused_prolonged_hospitalisation = False
        disabling_incapacitating = False
        congenital_anomaly_birth_defect = False
        other_medically_important_condition = False
        
        # Si es serio, determinar el criterio específico
        if is_serious:
            criterio = data_isp.get('Clasificacion Seriedad Final', '')
            
            if criterio == 'RESULTA EN MUERTE':
                results_in_death = True
            elif criterio == 'AMENAZA LA VIDA':
                life_threatening = True
            elif criterio == 'CAUSA HOSPITALIZACION' or criterio == 'PROLONGA HOSPITALIZACION':
                caused_prolonged_hospitalisation = True
            elif criterio == 'INCAPACITANTE':
                disabling_incapacitating = True
            elif criterio == 'OTRA CONDICION MEDICA IMPORTANTE':
                other_medically_important_condition = True
        
        fecha_evento = reaction['fecha']

        reaction_event = create_reaction_event(
            reaction_id=reaction_id,
            reaction_text=reaction['text'],
            meddra_code=reaction['code'],
            fecha_evento=fecha_evento,
            results_in_death=results_in_death,
            life_threatening=life_threatening,
            caused_prolonged_hospitalisation=caused_prolonged_hospitalisation,
            disabling_incapacitating=disabling_incapacitating,
            congenital_anomaly_birth_defect=congenital_anomaly_birth_defect,
            other_medically_important_condition=other_medically_important_condition
        )
        # Adds reactions to list
        reaction_events.Add(reaction_event)

    def create_drug_information(drug_id, drug_name, who_drug_id, active_ingredient, dosage_text, route_admin, characterisation_role="1"):
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

    # Dummy
    drug_id = generate_guid() 
    drug_info = create_drug_information(
        drug_id=drug_id,
        drug_name="drug_name",
        who_drug_id= '-1',
        active_ingredient="active_ingredient",
        dosage_text="dosage_text",
        route_admin="route_admin"
    )
    
    drug_informations.Add(drug_info)

    # # Procesar todos los medicamentos sospechosos (FS1 a FS8)
    # for i in range(1, 9):
    #     drug_key = f'Farmaco Sospechoso {i}'
    #     drug_pa_key = f'Principio Activo FS{i}'
    #     who_drug_key = f'WHODRUG FS{i}'
    #     who_drug_pa_key = f'WHODRUG PA FS{i}'
    #     active_ingredient_key = f'Principio Activo FS{i}'
    #     dosage_key = f'Dosis Total FS{i}'
    #     route_key = f'Via Administracion FS{i}'
        
    #     # Verificar si existe el medicamento
    #     if (drug_key in data_ury and data_ury[drug_key]) or (drug_pa_key in data_ury and data_ury[drug_pa_key]):
    #         drug_id = generate_guid()  # Genera un GUID único para cada medicamento
    #         drug_name = data_ury[drug_key]
    #         if not drug_name or drug_name == '':
    #             drug_name = data_ury.get(drug_pa_key, '')
    #         who_drug_id = data_ury.get(who_drug_key, '')
    #         if not who_drug_id or who_drug_id == '-1':
    #             who_drug_id = data_ury.get(who_drug_pa_key, '')

    #         active_ingredient = data_ury.get(active_ingredient_key, '')
    #         dosage_text = data_ury.get(dosage_key, '')
    #         route_admin = data_ury.get(route_key, '')
            
    #         # Crear el objeto DrugInformation y agregarlo a la lista
    #         drug_info = create_drug_information(
    #             drug_id=drug_id,
    #             drug_name=drug_name,
    #             who_drug_id=who_drug_id,
    #             active_ingredient=active_ingredient,
    #             dosage_text=dosage_text,
    #             route_admin=route_admin
    #         )
            
    #         drug_informations.Add(drug_info)
    #         print(f"Medicamento {i} agregado: {drug_name}")

    # # Concomitantes
    # for i in range(1, 5):
    #     drug_key = f'Farmaco Concomitante {i}'
    #     drug_pa_key = f'Principio Activo FC{i}'
    #     who_drug_key = f'WHODRUG FC{i}'
    #     who_drug_pa_key = f'WHODRUG PA FC{i}'
    #     active_ingredient_key = f'Principio Activo FC{i}'
        
    #     # Verificar si existe el medicamento
    #     if (drug_key in data_ury and data_ury[drug_key]) or (drug_pa_key in data_ury and data_ury[drug_pa_key]):
    #         drug_id = generate_guid()  # Genera un GUID único para cada medicamento
    #         drug_name = data_ury[drug_key]
    #         if not drug_name or drug_name == '':
    #             drug_name = data_ury.get(drug_pa_key, '')
    #         who_drug_id = data_ury.get(who_drug_key, '')
    #         if not who_drug_id or who_drug_id == '-1':
    #             who_drug_id = data_ury.get(who_drug_pa_key, '')

    #         active_ingredient = data_ury.get(active_ingredient_key, '')
    #         dosage_text = ''
    #         route_admin = ''
            
    #         # Crear el objeto DrugInformation y agregarlo a la lista
    #         drug_info = create_drug_information(
    #             drug_id=drug_id,
    #             drug_name=drug_name,
    #             who_drug_id=who_drug_id,
    #             active_ingredient=active_ingredient,
    #             dosage_text=dosage_text,
    #             route_admin=route_admin,
    #             characterisation_role="2"
    #         )
            
    #         drug_informations.Add(drug_info)
    #         print(f"Medicamento Concomitante {i} agregado: {drug_name}")

    # Crear el objeto Assessment con la información de causalidad
    assessment = Assessment()

    causalityAssessments = List[CausalityAssessment]()

    # Crear un objeto CausalityAssessment
    causalityAssessment = CausalityAssessment()
    causalityAssessment.MethodOfAssessment = "WHO-UMC"  # Método de evaluación (WHO-UMC, Naranjo, etc.)
    causalityAssessment.SourceOfAssessment = "Farmacovigilancia - Ministerio de Salud Pública"  # Fuente de la evaluación

    # Crear la lista de CausalityAssessmentResult
    causalityAssessmentResults = List[CausalityAssessmentResult]()

    # Filtrar solo los medicamentos sospechosos para la evaluación de causalidad
    suspected_drugs = [drug for drug in drug_informations if drug.CharacterisationOfDrugRole == "1"]

    # Para cada medicamento y reacción, crear un resultado de causalidad
    # for reaction_event in reaction_events:
    #     for drug_info in suspected_drugs:
    #         causalityAssessmentResult = CausalityAssessmentResult()
    #         causalityAssessmentResult.DrugReferenceId = drug_info.DrugReferenceId
    #         causalityAssessmentResult.ReactionReferenceId = reaction_event.ReactionReferenceId
            
    #         # Obtener el resultado de la evaluación de causalidad del CSV
    #         if data_ury.get('Causalidad VigiFlow', ''):
    #             causalityAssessmentResult.ResultOfAssessment = data_ury['Causalidad VigiFlow']
    #         else:
    #             causalityAssessmentResult.ResultOfAssessment = ""  # Valor por defecto
                
    #         causalityAssessmentResults.Add(causalityAssessmentResult)

    # Asignar los resultados de causalidad al objeto CausalityAssessment
    causalityAssessment.CausalityAssessmentResults = causalityAssessmentResults

    # Agregar el objeto CausalityAssessment a la lista
    causalityAssessments.Add(causalityAssessment)

    # Asignar la lista de CausalityAssessment al objeto Assessment
    assessment.CausalityAssessments = causalityAssessments

    # Create an instance of the Icsr class and set its properties
    icsr = Icsr()
    icsr.IdentificationOfTheCaseSafetyReport = identification
    icsr.NarrativeCaseSummaryAndOtherInformation = narrative
    icsr.PrimarySourcesOfInformations = primary_sources
    icsr.InformationOnSenderOfCaseSafetyReport = sender_info
    icsr.PatientCharacteristics = patient_characteristics
    icsr.ReactionEvents = reaction_events
    icsr.DrugInformations = drug_informations
    icsr.Assessment = assessment

    # Crear IcsrWithIncludedDocuments y agregarlo a la lista
    icsrWithIncludedDocuments = IcsrWithIncludedDocuments()
    icsrWithIncludedDocuments.Icsr = icsr
    icsrWithIncludedDocuments.IncludedDocuments = List[IncludedDocument]()  # Lista vacía de documentos incluidos
    icsr_list.Add(icsrWithIncludedDocuments)

# Fuera del bucle, escribir todos los ICSRs
stream = FileStream(f"Output/isp_output.xml", FileMode.Create, FileAccess.Write)

# Write E2B R3 XML to the file
write(exn_handler, info, stream, icsr_list)


