import math
import clr
import sys
import csv
import io
from System.Collections.Generic import List
from System.IO import FileStream, FileMode, FileAccess
from col_r3_helper import *

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

# Leer registros del CSV en lotes de 100
MAX_RECORDS = 100
TOTAL_RECORDS = 1100
discarded_records = 0

messageLog = []
icsr_list_lengths = []
BATCH_COUNT = math.ceil(TOTAL_RECORDS / MAX_RECORDS)

def write(exn_handler, info, stream, icsr_list):
    discarded_records = 0
    message = ""
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
        message = f"Se encontraron {result.MappingExceptions.Count} errores durante el mapeo:"
        
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
            message += f"\n  - Error en ID {id} (índice {index}): {error_type}"
            print(message)
            discarded_records += 1
        
        # Imprimir un resumen de los tipos de errores
        print("\nResumen de tipos de errores:")
        for error_type, count in error_types.items():
            print(f"  - {error_type}: {count} ocurrencia(s)")
        
        print("Continuando con el proceso a pesar de los errores...")

    MemoryStreamGenerator.Generate(stream, result.Result, indent=False)

    return discarded_records, message

# Define the TransmissionIdentification class (assuming it's defined in your .NET assembly)
class TransmissionIdentification:
    def __init__(self, batch_number, sender_identifier, receiver_identifier, sender_name):
        self.BatchNumber = batch_number
        self.SenderIdentifier = sender_identifier
        self.ReceiverIdentifier = receiver_identifier
        self.SenderName = sender_name

for batch_index in range(BATCH_COUNT):
    start_record = batch_index * MAX_RECORDS
    
    data_ury_list = []
    with open('Data_COL/redcap.csv', 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(io.StringIO(file.read()))
        
        # Saltar registros hasta el inicio del lote actual
        for _ in range(start_record):
            try:
                next(csv_reader)
            except StopIteration:
                break
                
        # Leer los registros del lote actual
        for _ in range(MAX_RECORDS):
            try:
                data_ury = next(csv_reader)
                data_ury_list.append(data_ury)
            except StopIteration:
                break

    # Crear una lista para almacenar todos los ICSRs
    icsr_list = List[IcsrWithIncludedDocuments]()

    # Procesar cada registro
    for data_ury in data_ury_list:

        data_ury = clean_sin_datos(data_ury)

        fecha_reporte_msp = process_date("8/12/25")
        fecha_evento = process_date(data_ury['Fecha del Error de Medicacion'])

        # Fill R3 model with data
        info = TransmissionIdentification(
            batch_number="Batch_{BATCH_COUNT}",            # N.1.2
            sender_identifier="FV Ministerio Salud UY",       # N.1.3 & N.2.r.2
            receiver_identifier="UMC",   # N.1.4 & N.2.r.3
            sender_name="FV UY"
        )

        #print(data_ury.keys())
        case_number = data_ury['safety_id'].split('-')[-1]
        identification = IdentificationOfTheCaseSafetyReport()

        #Sender information (there are more fields available)
        #identification.SendersOrganisation = "Farmacovigilancia - Ministerio de Salud Pública Uruguay"                                          
        #identification.SenderType = "1"                                                     
        #identification.SendersCountryCode = "UY"                                            

        #Report identification
        identification.WorldWideUniqueCaseIdentificationNumber = data_ury['safety_id']    
        identification.SendersCaseSafetyReportUniqueIdentifier = data_ury['safety_id']     
        identification.FirstSenderOfThisCase = "1"                                          
        identification.TypeOfReport = "1"       
        identification.DateReportWasFirstReceivedFromSource = fecha_reporte_msp                   
        identification.DateOfMostRecentInformationForThisReport = fecha_reporte_msp    
        identification.DateOfCreation = fecha_reporte_msp         
        identification.OtherCaseIdentifiersInPreviousTransmissions = TrueOnly(1, True)      
        identification.OtherCaseIdentifiersInPreviousTransmissionsNullFlavor = NullFlavor.NI
        identification.ReportNullificationAmendment = ""                                    
        identification.ReasonForNullificationAmendment = ""    

        print(f"\nRegistro: {identification.WorldWideUniqueCaseIdentificationNumber}")

        # UMC extensions
        identification.AefiCase = False                                                     
        identification.NotificationDate = fecha_reporte_msp                                                
        identification.DateOfReport = fecha_reporte_msp         
        # Not working ReportTitle: Organizacion + "RAM/Error" + Medicamento Sospechoso                                                                 
        identification.ReportTitle = "Error de " + data_ury['Tipo de error'] + " | " + data_ury['safety_id']

        # Other case identifiers
        othercaseIdentifier = OtherCaseIdentifiers()
        othercaseIdentifier.SourcesOfTheCaseIdentifier = ""
        othercaseIdentifier.CaseIdentifier = case_number
        othercaseIdentifiers = List[OtherCaseIdentifiers]()
        othercaseIdentifiers.Add(othercaseIdentifier)
        identification.OtherCaseIdentifiers = othercaseIdentifiers

        # Narrative
        narrative = NarrativeCaseSummaryAndOtherInformation()

        # Construir la narrativa
        narrative_text = ""
        if data_ury.get('Tipo de error'):
            narrative_text += "Tipo de error: " + data_ury['Tipo de error']
        
        if data_ury.get('Posibles causas identificadas'):
            if narrative_text:
                narrative_text += " | "
            narrative_text += "Posible causa identificada: " + data_ury['Posibles causas identificadas']

        if data_ury.get('Desenlace'):
            if narrative_text:
                narrative_text += " | "
            narrative_text += "Desenlace: " + data_ury['Desenlace']
        
        reporter_text = ""

        narrative.CaseNarrativeIncludingClinicalCourseTherapeuticMeasuresOutcomeAndAdditionalRelevantInformation = narrative_text

        narrative.ReportersComment = reporter_text
        narrative.SendersComment = "Pendiente de evaluación de causalidad:" + data_ury['Comentario evaluacion']
        caseSummaryAndReportersCommentsInNativeLanguage = CaseSummaryAndReportersCommentsInNativeLanguage()
        caseSummaryAndReportersCommentsInNativeLanguage.CaseSummaryAndReportersCommentsText = ""
        caseSummaryAndReportersCommentsInNativeLanguage.CaseSummaryAndReportersCommentsLanguage = ""
        caseSummaryAndReportersCommentsInNativeLanguages = List[CaseSummaryAndReportersCommentsInNativeLanguage]()
        caseSummaryAndReportersCommentsInNativeLanguages.Add(caseSummaryAndReportersCommentsInNativeLanguage)
        narrative.CaseSummaryAndReportersCommentsInNativeLanguage = caseSummaryAndReportersCommentsInNativeLanguages

        #Primary Source
        primary_source = PrimarySourcesOfInformation()
        
        qualification = ""
        tipo_emisor = data_ury.get('Tipo de emisor')
        if tipo_emisor == 'Otro':
            qualification = "3"
        elif tipo_emisor == 'Profesional de la salud':
            qualification = "2"
        
        primary_source.Qualification = qualification

        primary_source.PrimarySourceForRegulatoryPurposes = True
        primary_source.ReportersOrganisation = data_ury['Notificador']
        primary_source.ReportersDepartment = ""
        primary_source.ReportersStreet = ""
        primary_source.ReportersCountryCode = "UY"
        primary_source.ReportersTelephone = ""
        primary_source.QualificationFreetext = ""
        primary_sources = List[PrimarySourcesOfInformation]()
        primary_sources.Add(primary_source)

        # Sender
        sender_info = InformationOnSenderOfCaseSafetyReport()
        sender_info.SendersOrganisation = "Ministerio de Salud Pública Uruguay"      
        sender_info.SenderType = "3" # Profesional de la salud                                          
        sender_info.SendersCountryCode = "UY"   

        # Patient characteristics
        patient_characteristics = PatientCharacteristics()
        patient_characteristics.PatientNameOrInitials = data_ury['Iniciales']
        patient_characteristics.PersonalIdentificationNumber = ""

        # Edad
        patient_characteristics.DateOfBirth = ""
        
        age_str = data_ury.get('Edad', '').strip()
        if age_str and age_str.isdigit():
            age, age_unit = get_age(age_str, data_ury.get('Unidad'))
        else:
            age, age_unit = "", ""
            
        patient_characteristics.AgeAtTimeOfOnsetOfReactionEvent = age
        patient_characteristics.AgeAtTimeOfOnsetOfReactionEventUnit = age_unit
        # Embarazo
        # patient_characteristics.Pregnant = False
        # patient_characteristics.GestationPeriodWhenReactionEventWasObservedInTheFoetus = ""
        # patient_characteristics.GestationPeriodWhenReactionEventWasObservedInTheFoetusUnit = ""
        
        # patient_characteristics.PatientAgeGroupAsPerReporter = ""

        # patient_characteristics.Lactating = False

        # Peso
        #patient_characteristics.BodyWeight = ""
        # patient_characteristics.Height = ""

        # Sexo
        sexo = get_sex(data_ury.get('Sexo'))
        if sexo:
            patient_characteristics.Sex = sexo
        else:
            patient_characteristics.SexNullFlavor = NullFlavor.UNK

        # forAParentChildFoetusReportInformationConcerningParent = ForAParentChildFoetusReportInformationConcerningParent()
        # forAParentChildFoetusReportInformationConcerningParent.AgeOfParent = data_ury['edad_madre']
        # forAParentChildFoetusReportInformationConcerningParent.AgeOfParentUnit = "a"
        # forAParentChildFoetusReportInformationConcerningParent.SexOfParent = "2"

        # patient_characteristics.ForAParentChildFoetusReportInformationConcerningParent = forAParentChildFoetusReportInformationConcerningParent

        #patient_characteristics.TextForRelevantMedicalHistoryAndConcurrentConditionsNotIncludingReactionEvent = ":" +data_ury['fecha_fin_gestacion']

        # Medical history
        #patient_characteristics.TextForRelevantMedicalHistoryAndConcurrentConditionsNotIncludingReactionEvent = ""
        #patient_characteristics.ConcomitantTherapies = TrueOnly(1, True)

        #TODO study otros tipo de estudio
        # StudyIdentification_type Properties:
        # StudyRegistrations
        # StudyName
        # StudyNameNullFlavor
        # SponsorStudyNumber
        # SponsorStudyNumberNullFlavor
        # StudyTypeWhereReactionsEventsWereObserved
        study_identification = StudyIdentification()
        # study_identification.StudyName = "Reporte de estudio: Vigilancia de seguridad de la vacuna Abrysvo contra VRS en binomio Madre-Hijo"
        #study_identification.StudyNameNullFlavor = NullFlavor.NI
        #study_identification.SponsorStudyNumber = data_ury['id'] 
        #study_identification.SponsorStudyNumberNullFlavor = NullFlavor.NI
        # study_identification.StudyTypeWhereReactionsEventsWereObserved = "3"
        #study_identification.StudyTypeWhereReactionsEventsWereObservedNullFlavor = NullFlavor.NI

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
            reaction_event.OutcomeOfReactionEventAtTheTimeOfLastObservation = ""
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

        meddra_code = data_ury['meddra code']

        reaction_info = {
                        'text': data_ury.get('meddra term', ''),
                        'code': int(meddra_code)
                    }
        
        reaction_id = generate_guid()  # Genera un GUID único para cada reacción
                
        reaction_event = create_reaction_event(
            reaction_id=reaction_id,
            reaction_text=reaction_info['text'],
            meddra_code=reaction_info['code'],
            fecha_evento=fecha_evento,
        )
        # Adds reactions to list
        reaction_events.Add(reaction_event)

        def create_drug_information(drug_id, drug_name, who_drug_id, dossage_text, pharmaceutical_dose_form="", characterisation_role="1"):
            drug_information = DrugInformation()    
            drug_information.DrugReferenceId = drug_id
            drug_information.CharacterisationOfDrugRole = characterisation_role # Sospechoso
            drug_information.MedicinalProductNameAsReportedByThePrimarySource = drug_name
            drug_information.CountryOfAuthorisationApplication = "UY"
            drug_information.NameOfHolderApplicant = ""
            
            drug_information.MedicinalProductIdentifierWHODrugVersion = "20240830"
            #drug_information.MedicinalProductIdentifierWHODrugProductId = who_drug_id
            drug_information.MedicinalProductIdentifierWHODrugProductId = 3878715  # Placeholder value

            # Dose information
            dosageInformations = List[DosageInformation]()
            dosageInformation = DosageInformation()
            dosageInformation.Dose = ""
            dosageInformation.DoseUnit = ""
            dosageInformation.DoseNumber = ""
            dosageInformation.DosageText = dossage_text
            dosageInformation.PharmaceuticalDoseForm = pharmaceutical_dose_form
            dosageInformation.RouteOfAdministration = ""
            dosageInformations.Add(dosageInformation)
            drug_information.DosageInformations = dosageInformations
            dosageInformation.DateAndTimeOfStartOfDrug = "" 

            #10090260 indicacion inmunizacion materna
            indicationForUseInCase = IndicationForUseInCase()
            indicationForUseInCase.IndicationAsReportedByThePrimarySource = ""
            indicationForUseInCase.IndicationMedDRAVersion = "27.0"
            #indicationForUseInCase.IndicationMedDRACode = ""
            indicationForUseInCases = List[IndicationForUseInCase]()
            indicationForUseInCases.Add(indicationForUseInCase)
            drug_information.IndicationForUseInCases = indicationForUseInCases
            #drug_information.ActionsTakenWithDrug = ""
            
            # Additional information on drug
            additionalInformationOnDrugs = List[AdditionalInformationOnDrug]()
            additionalInformationOnDrug = AdditionalInformationOnDrug()
            additionalInformationOnDrug.AdditionalInformationOnDrugCoded = "7"
            additionalInformationOnDrugs.Add(additionalInformationOnDrug)
            drug_information.AdditionalInformationOnDrugs = additionalInformationOnDrugs
            drug_information.AdditionalInformationOnDrug = data_ury.get('Accion tomada', '')
            
            return drug_information

        # Drug section (add items to list)
        drug_informations = List[DrugInformation]()
        
        drug_id = generate_guid()  # Genera un GUID único para cada medicamento
        drug_name = data_ury.get('Marca comercial erroneo', '')
        if not drug_name:
            drug_name = data_ury.get('Principio activo erroneo', '')
        who_drug_id = data_ury['mpid erroneo'] # WHO Drug ID
        dosage_text = data_ury['Dosis erroneo']
        pharmaceutical_dose_form = data_ury.get('Forma Farmaceutica erroneo', '')
        
        # Crear el objeto DrugInformation y agregarlo a la lista
        drug_erroneo = create_drug_information(
            drug_id=drug_id,
            drug_name=drug_name,
            who_drug_id=who_drug_id,
            dossage_text=dosage_text,
            pharmaceutical_dose_form=pharmaceutical_dose_form,
            characterisation_role="1"
        )

        drug_informations.Add(drug_erroneo)
        print(f"Medicamento erroneo agregado: {drug_name}")

        drug_id = generate_guid()  # Genera un GUID único para cada medicamento
        drug_name = data_ury['Marca comercial correcto']
        if not drug_name:
            drug_name = data_ury.get('Principio activo correcto', '')
        who_drug_id = data_ury['mpid correcto'] # WHO Drug ID
        dosage_text = data_ury['Dosis correcto']
        pharmaceutical_dose_form = data_ury.get('Forma Farmaceutica correcto', '')
        
        # Crear el objeto DrugInformation y agregarlo a la lista
        drug_correcto = create_drug_information(
            drug_id=drug_id,
            drug_name=drug_name,
            who_drug_id=who_drug_id,
            dossage_text=dosage_text,
            pharmaceutical_dose_form=pharmaceutical_dose_form,
            characterisation_role="4"
        )
        
        drug_informations.Add(drug_correcto)
        print(f"Medicamento correcto agregado: {drug_name}")

        

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
        # suspected_drugs = [drug for drug in drug_informations if drug.CharacterisationOfDrugRole == "1"]

        # # Para cada medicamento y reacción, crear un resultado de causalidad
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
        icsr.StudyIdentification = study_identification
        icsr.ReactionEvents = reaction_events
        icsr.DrugInformations = drug_informations
        icsr.Assessment = assessment

        # Crear IcsrWithIncludedDocuments y agregarlo a la lista
        icsrWithIncludedDocuments = IcsrWithIncludedDocuments()
        icsrWithIncludedDocuments.Icsr = icsr
        icsrWithIncludedDocuments.IncludedDocuments = List[IncludedDocument]()  # Lista vacía de documentos incluidos
        icsr_list.Add(icsrWithIncludedDocuments)

    # Fuera del bucle, escribir todos los ICSRs
    stream = FileStream(f"Output/uruguay/ury_output_error_med_{batch_index+1}.xml", FileMode.Create, FileAccess.Write)
    
    message = ""
    # Write E2B R3 XML to the file

    discarded_records, message = write(exn_handler, info, stream, icsr_list)
    messageLog.append(message)
    icsr_list_lengths.append(len(icsr_list) - discarded_records)

    message = f"\nICSRs en el batch {batch_index+1}: {len(icsr_list) - discarded_records}"
    print(message)
    messageLog.append(message)

    discarded_records = 0

# Al final del script, imprimir el resumen de los lotes procesados
message = "\nResumen de lotes procesados:"
for batch_index, icsr_list_length in enumerate(icsr_list_lengths, start=1):
    message += f"\n  - Batch {batch_index}: {icsr_list_length} ICSRs"

message += f"\nTotal de ICSRs en la lista: {sum(icsr_list_lengths)}"
print(message)
messageLog.append(message)

with open('Output/uruguay/messageLog_error_med.txt', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Message Log'])  # Cabecera del archivo CSV
    for message in messageLog:
        writer.writerow([message])  # Escribir cada mensaje de log en una fila



