import clr
import sys
import uuid
from System import Action
from System.Collections.Generic import List
from System.IO import FileStream, FileMode, FileAccess


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
from datetime import datetime

# Patient and Notification characteristics 
from fhir_patient import extract_patient_characteristics
from fhir_notification import extract_notification_characteristics

# Ruta al archivo XML
xml_path = "FHIR/QR-ejUnoNuevo.xml"

# Llamar a las funciones para extraer características
patient_data = extract_patient_characteristics(xml_path)
notification_data = extract_notification_characteristics(xml_path)


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
    
def write(exn_handler, info, stream, attachments, icsr):
    now = datetime.now
    parameters = mapping_parameters(info)
    icsrWithIncludedDocuments = IcsrWithIncludedDocuments()
    icsrWithIncludedDocuments.Icsr = icsr
    icsrWithIncludedDocuments.IncludedDocuments = attachments
    items = List[IcsrWithIncludedDocuments]()
    items.Add(icsrWithIncludedDocuments)
    mapper = E2BR3MapperFactory.CreateDefaultMapper()
    result = mapper.Map(items, parameters)

    if result.MappingExceptions.Count > 0:
        raise result.MappingExceptions[icsr]

    MemoryStreamGenerator.Generate(stream, result.Result, indent=False)

# Define your exn_handler function
def exn_handler(exception):
    print(f"Validation exception: {exception}")

# Define the TransmissionIdentification class (assuming it's defined in your .NET assembly)
class TransmissionIdentification:
    def __init__(self, batch_number, sender_identifier, receiver_identifier, sender_name):
        self.BatchNumber = batch_number
        self.SenderIdentifier = sender_identifier
        self.ReceiverIdentifier = receiver_identifier
        self.SenderName = sender_name


# Fill R3 model with data
info = TransmissionIdentification(
    batch_number="Batch123",            # N.1.2
    sender_identifier="SenderID",       # N.1.3 & N.2.r.2
    receiver_identifier="ReceiverID",   # N.1.4 & N.2.r.3
    sender_name="SenderName"
)
#case_number = str(uuid.uuid4())
case_number = "20240830_123123"
identification = IdentificationOfTheCaseSafetyReport()

#Sender information (there are more fields available)
identification.SendersOrganisation = "UMC"                                          
identification.SenderType = "1"                                                     
identification.SendersCountryCode = "SE"                                            

#Report identification
identification.WorldWideUniqueCaseIdentificationNumber = "SE-UMC-" + case_number    
identification.SendersCaseSafetyReportUniqueIdentifier = "SE-UMC-" + case_number
identification.FirstSenderOfThisCase = "1"                                          
identification.TypeOfReport = "1"                                                   
identification.DateReportWasFirstReceivedFromSource = "20040101"                    
identification.DateOfMostRecentInformationForThisReport = "20040101"                
identification.DateOfCreation = "20170906220933"                                    
identification.OtherCaseIdentifiersInPreviousTransmissions = TrueOnly(1, True)      
identification.OtherCaseIdentifiersInPreviousTransmissionsNullFlavor = NullFlavor.NI
identification.ReportNullificationAmendment = ""                                    
identification.ReasonForNullificationAmendment = ""    

# UMC extensions
identification.AefiCase = True                                                     
identification.NotificationDate = ""                                                
identification.DateOfReport = ""                                                                                
identification.ReportTitle = ""                                                     

# Other case identifiers
othercaseIdentifier = OtherCaseIdentifiers()
othercaseIdentifier.SourcesOfTheCaseIdentifier = "SourcesOfTheCaseIdentifier"
othercaseIdentifier.CaseIdentifier = "CaseIdentifier"
othercaseIdentifiers = List[OtherCaseIdentifiers]()
othercaseIdentifiers.Add(othercaseIdentifier)
identification.OtherCaseIdentifiers = othercaseIdentifiers

# Narrative
narrative = NarrativeCaseSummaryAndOtherInformation()
narrative.CaseNarrativeIncludingClinicalCourseTherapeuticMeasuresOutcomeAndAdditionalRelevantInformation = ""
narrative.ReportersComment = ""
narrative.SendersComment = ""
caseSummaryAndReportersCommentsInNativeLanguage = CaseSummaryAndReportersCommentsInNativeLanguage()
caseSummaryAndReportersCommentsInNativeLanguage.CaseSummaryAndReportersCommentsText = ""
caseSummaryAndReportersCommentsInNativeLanguage.CaseSummaryAndReportersCommentsLanguage = ""
caseSummaryAndReportersCommentsInNativeLanguages = List[CaseSummaryAndReportersCommentsInNativeLanguage]()
caseSummaryAndReportersCommentsInNativeLanguages.Add(caseSummaryAndReportersCommentsInNativeLanguage)
narrative.CaseSummaryAndReportersCommentsInNativeLanguage = caseSummaryAndReportersCommentsInNativeLanguages

#Primary Source
primary_source = PrimarySourcesOfInformation()
primary_source.Qualification = "1"
primary_source.PrimarySourceForRegulatoryPurposes = True
primary_source.ReportersTitle = ""
primary_source.ReportersGivenName = ""
primary_source.ReportersMiddleName = ""
primary_source.ReportersFamilyName = ""
primary_source.ReportersOrganisation = ""
primary_source.ReportersDepartment = ""
primary_source.ReportersStreet = ""
primary_source.ReportersCity = ""
primary_source.ReportersCounty = ""
primary_source.ReportersDepartment = ""
primary_source.ReportersStateOrProvince = ""
primary_source.ReportersPostCode = ""
primary_source.ReportersCountryCode = "SE"
primary_source.ReportersTelephone = ""
primary_source.ReportersEmail = ""
primary_source.QualificationFreetext = ""
primary_sources = List[PrimarySourcesOfInformation]()
primary_sources.Add(primary_source)

# Sender
sender_info = InformationOnSenderOfCaseSafetyReport()
sender_info.SenderType = "2"
sender_info.SendersOrganisation = "SendersOrganisation"
sender_info.SendersDepartment = ""
sender_info.SendersTitle = ""
sender_info.SendersGivenName = ""
sender_info.SendersMiddleName = ""
sender_info.SendersFamilyName = ""
sender_info.SendersStreetAddress = ""
sender_info.SendersCity = ""
sender_info.SendersStateOrProvince = ""
sender_info.SendersPostcode = ""
sender_info.SendersCountryCode = ""
sender_info.SendersTelephone = ""
sender_info.SendersFax = ""
sender_info.SendersEmailAddress = ""

# Literature reference
literature_reference = LiteratureReference()
literature_reference.LiteratureReferences = ""
literature_references = List[LiteratureReference]()
literature_references.Add(literature_reference)

study_identification = StudyIdentification()

# Populate patient characteristics
patient_characteristics = PatientCharacteristics()
patient_characteristics.PatientNameOrInitials = patient_data.PatientNameOrInitials
patient_characteristics.PatientsGivenName = patient_data.PatientsGivenName
patient_characteristics.PatientsMiddleName = patient_data.PatientsMiddleName
patient_characteristics.PatientsFamilyName = patient_data.PatientsFamilyName
patient_characteristics.PatientsStreet = patient_data.PatientsStreet
patient_characteristics.PatientsCity = patient_data.PatientsCity
patient_characteristics.PatientsCounty = patient_data.PatientsCounty
patient_characteristics.PatientsStateOrProvince = patient_data.PatientsStateOrProvince
patient_characteristics.PatientsPostCode = patient_data.PatientsPostCode
patient_characteristics.PatientsTelephone = patient_data.PatientsTelephone
patient_characteristics.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberGpMedicalRecordNumber = patient_data.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberGpMedicalRecordNumber
patient_characteristics.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberSpecialistRecordNumber = patient_data.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberSpecialistRecordNumber
patient_characteristics.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberHospitalRecordNumber = patient_data.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberHospitalRecordNumber
patient_characteristics.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberInvestigationNumber = patient_data.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberInvestigationNumber
patient_characteristics.PersonalIdentificationNumber = patient_data.PersonalIdentificationNumber
patient_characteristics.DateOfBirth = patient_data.DateOfBirth
patient_characteristics.AgeAtTimeOfOnsetOfReactionEvent = patient_data.AgeAtTimeOfOnsetOfReactionEvent
patient_characteristics.AgeAtTimeOfOnsetOfReactionEventUnit = patient_data.AgeAtTimeOfOnsetOfReactionEventUnit
patient_characteristics.GestationPeriodWhenReactionEventWasObservedInTheFoetus = patient_data.GestationPeriodWhenReactionEventWasObservedInTheFoetus
patient_characteristics.GestationPeriodWhenReactionEventWasObservedInTheFoetusUnit = patient_data.GestationPeriodWhenReactionEventWasObservedInTheFoetusUnit
patient_characteristics.Pregnant = patient_data.Pregnant
patient_characteristics.Lactating = patient_data.Lactating
patient_characteristics.PatientAgeGroupAsPerReporter = patient_data.PatientAgeGroupAsPerReporter
patient_characteristics.BodyWeight = patient_data.BodyWeight
patient_characteristics.Height = patient_data.Height
patient_characteristics.Sex = patient_data.Sex
patient_characteristics.LastMenstrualPeriodDate = patient_data.LastMenstrualPeriodDate

# Populate notification characteristics
identification.SendersOrganisation = notification_data.SendersOrganisation
identification.SenderType = notification_data.SenderType
identification.SendersCountryCode = notification_data.SendersCountryCode
#identification.WorldWideUniqueCaseIdentificationNumber = notification_data.WorldWideUniqueCaseIdentificationNumber
#identification.SendersCaseSafetyReportUniqueIdentifier = notification_data.SendersCaseSafetyReportUniqueIdentifier 
identification.FirstSenderOfThisCase = notification_data.FirstSenderOfThisCase
identification.TypeOfReport = notification_data.TypeOfReport
identification.DateReportWasFirstReceivedFromSource = notification_data.DateReportWasFirstReceivedFromSource
identification.DateOfMostRecentInformationForThisReport = notification_data.DateOfMostRecentInformationForThisReport
identification.DateOfCreation = notification_data.DateOfCreation
#identification.OtherCaseIdentifiersInPreviousTransmissions = notification_data.OtherCaseIdentifiersInPreviousTransmissions
#identification.OtherCaseIdentifiersInPreviousTransmissionsNullFlavor = notification_data.OtherCaseIdentifiersInPreviousTransmissionsNullFlavor
identification.ReportNullificationAmendment = notification_data.ReportNullificationAmendment
identification.ReasonForNullificationAmendment = notification_data.ReasonForNullificationAmendment
identification.AefiCase = notification_data.AefiCase
identification.NotificationDate = notification_data.NotificationDate
identification.DateOfReport = notification_data.DateOfReport
identification.ReportTitle = notification_data.ReportTitle

# Medical history
structuredInformationonRelevantMedicalHistory = StructuredInformationonRelevantMedicalHistory()
structuredInformationonRelevantMedicalHistory.MedicalHistoryMedDRAVersion = ""
structuredInformationonRelevantMedicalHistory.MedicalHistoryMedDRAcode = 10000001
structuredInformationonRelevantMedicalHistory.StartDate = ""
structuredInformationonRelevantMedicalHistory.Continuing = False
structuredInformationonRelevantMedicalHistory.EndDate = ""
structuredInformationonRelevantMedicalHistory.Comments = ""
structuredInformationonRelevantMedicalHistory.FamilyHistory =  TrueOnly(1, True)
structuredInformationonRelevantMedicalHistorys = List[StructuredInformationonRelevantMedicalHistory]()
structuredInformationonRelevantMedicalHistorys.Add(structuredInformationonRelevantMedicalHistory)
patient_characteristics.StructuredInformationonRelevantMedicalHistory = structuredInformationonRelevantMedicalHistorys

patient_characteristics.TextForRelevantMedicalHistoryAndConcurrentConditionsNotIncludingReactionEvent = ""
patient_characteristics.ConcomitantTherapies = TrueOnly(1, True)

# Past drug history
relevantPastDrugHistory = RelevantPastDrugHistory()
relevantPastDrugHistory.NameOfDrugAsReported = "NameOfDrugAsReported"
#relevantPastDrugHistory.MpidVersionDateNumber = ""
#relevantPastDrugHistory.MedicinalProductIdentifierMpid = ""
relevantPastDrugHistory.MedicinalProductIdentifierWHODrugVersion = "20240830"
relevantPastDrugHistory.MedicinalProductIdentifierWHODrugProductId = 4765
relevantPastDrugHistory.MedicinalProductIdentifierWHODrugProductName = "MedicinalProductIdentifierWHODrugProductName"
#relevantPastDrugHistory.PhpidVersionDateNumber = ""
#relevantPastDrugHistory.PharmaceuticalProductIdentifierPhpid = ""
relevantPastDrugHistory.StartDate = ""
relevantPastDrugHistory.EndDate = ""
relevantPastDrugHistory.IndicationMedDRAVersion = "27.0"
relevantPastDrugHistory.IndicationMedDRACode = 10000001
relevantPastDrugHistory.ReactionMedDRAVersion = "27.0"
relevantPastDrugHistory.ReactionMedDRACode = 10000001
relevantPastDrugHistorys = List[RelevantPastDrugHistory]()
relevantPastDrugHistorys.Add(relevantPastDrugHistory)
patient_characteristics.RelevantPastDrugHistory = relevantPastDrugHistorys

# Death information
patient_characteristics.DateOfDeath = ""
reportedCausesOfDeath = ReportedCausesOfDeath()
reportedCausesOfDeath.ReportedCausesOfDeathFreeText = ""
reportedCausesOfDeath.ReportedCausesOfDeathMedDRAVersion = "27.0"
reportedCausesOfDeath.ReportedCausesOfDeathMedDRACode = 10000001
reportedCausesOfDeaths = List[ReportedCausesOfDeath]()
reportedCausesOfDeaths.Add(reportedCausesOfDeath)
patient_characteristics.ReportedCausesOfDeath = reportedCausesOfDeaths
patient_characteristics.WasAutopsyDone = False

autopsyDeterminedCausesOfDeath = AutopsyDeterminedCausesOfDeath()
autopsyDeterminedCausesOfDeath.AutopsyDeterminedCausesOfDeathFreeText = ""
autopsyDeterminedCausesOfDeath.AutopsyDeterminedCausesOfDeathMedDRAVersion = "27.0"
autopsyDeterminedCausesOfDeath.AutopsyDeterminedCausesOfDeathMedDRACode = 10000001
autopsyDeterminedCausesOfDeaths = List[AutopsyDeterminedCausesOfDeath]()
autopsyDeterminedCausesOfDeaths.Add(autopsyDeterminedCausesOfDeath)
patient_characteristics.AutopsyDeterminedCausesOfDeath = autopsyDeterminedCausesOfDeaths

# Parent information (in case of parent child report)
forAParentChildFoetusReportInformationConcerningParent = ForAParentChildFoetusReportInformationConcerningParent()
forAParentChildFoetusReportInformationConcerningParent.ParentIdentification = ""
forAParentChildFoetusReportInformationConcerningParent.DateOfBirthOfParent = ""
forAParentChildFoetusReportInformationConcerningParent.AgeOfParent = ""
forAParentChildFoetusReportInformationConcerningParent.AgeOfParentUnit = ""
forAParentChildFoetusReportInformationConcerningParent.LastMenstrualPeriodDateOfParent = ""
forAParentChildFoetusReportInformationConcerningParent.BodyWeightKgOfParent = ""
forAParentChildFoetusReportInformationConcerningParent.HeightCmOfParent = ""
forAParentChildFoetusReportInformationConcerningParent.SexOfParent = ""

structuredInformationOfParent = StructuredInformationOfParent()
structuredInformationOfParent.ParentMedicalHistoryMedDRAVersion = "27.0"
structuredInformationOfParent.ParentMedicalHistoryMedDRAcode = 10000001
structuredInformationOfParent.ParentStartDate = ""
structuredInformationOfParent.ParentContinuing = False
structuredInformationOfParent.ParentEndDate = ""
structuredInformationOfParent.ParentComments = ""
structuredInformationOfParents = List[StructuredInformationOfParent]()
structuredInformationOfParents.Add(structuredInformationOfParent)
forAParentChildFoetusReportInformationConcerningParent.StructuredInformationOfParent = structuredInformationOfParents
forAParentChildFoetusReportInformationConcerningParent.TextForRelevantMedicalHistoryAndConcurrentConditionsOfParent = ""

relevantPastDrugHistoryOfParent = RelevantPastDrugHistoryOfParent()
relevantPastDrugHistoryOfParent.NameOfDrugAsReported = ""
#relevantPastDrugHistoryOfParent.MpidVersionDateNumber = ""
#relevantPastDrugHistoryOfParent.MedicinalProductIdentifierMpid = ""
relevantPastDrugHistoryOfParent.MedicinalProductIdentifierWHODrugVersion = "20240830"
relevantPastDrugHistoryOfParent.MedicinalProductIdentifierWHODrugProductId = 4765
relevantPastDrugHistoryOfParent.MedicinalProductIdentifierWHODrugProductName = "MedicinalProductIdentifierWHODrugProductName"
relevantPastDrugHistoryOfParent.PhpidVersionDateNumber = ""
relevantPastDrugHistoryOfParent.PharmaceuticalProductIdentifierPhpid = ""
relevantPastDrugHistoryOfParent.StartDate = ""
relevantPastDrugHistoryOfParent.EndDate = ""
relevantPastDrugHistoryOfParent.IndicationMedDRAVersion = "27.0"
relevantPastDrugHistoryOfParent.IndicationMedDRACode = 10000001
relevantPastDrugHistoryOfParent.ReactionMedDRAVersion = "27.0"
relevantPastDrugHistoryOfParent.ReactionMedDRACode = 10000001
relevantPastDrugHistoryOfParents = List[RelevantPastDrugHistoryOfParent]()
relevantPastDrugHistoryOfParents.Add(relevantPastDrugHistoryOfParent)
forAParentChildFoetusReportInformationConcerningParent.RelevantPastDrugHistoryOfParent = relevantPastDrugHistoryOfParents
patient_characteristics.ForAParentChildFoetusReportInformationConcerningParent = forAParentChildFoetusReportInformationConcerningParent


# Reaction (add all reactions to this list)
reaction_events = List[ReactionEvent]()

reaction_event = ReactionEvent()
reaction_event.ReactionReferenceId = "878893d3-42a5-41e5-8767-af8b63fc6cd0" # TODO: Generate GUID instead
reaction_event.ReactionEventAsReportedByThePrimarySource = "ReactionEventAsReportedByThePrimarySource"
reaction_event.ReactionEventAsReportedByThePrimarySourceLanguage = "eng"
reaction_event.ReactionEventAsReportedByThePrimarySourceTranslation = ""
reaction_event.TermHighlightedByTheReporter = ""
reaction_event.DateOfStartOfReactionEvent = ""
reaction_event.DateOfEndOfReactionEvent = ""
reaction_event.DurationOfReactionEvent = ""
reaction_event.DurationOfReactionEventUnit = ""
reaction_event.OutcomeOfReactionEventAtTheTimeOfLastObservation = ""
reaction_event.IdentificationOfTheCountryWhereTheReactionEventOccurred = ""
reaction_event.ReactionEventMedDRAVersion = "27.0"
reaction_event.ReactionEventMedDRACode = 10000001
reaction_event.MedicalConfirmationByHealthcareProfessional = False

#Seriousness information (Use either TrueOnly or the Nullflavor row)

#reaction_event.ResultsInDeath = TrueOnly(1, True)
reaction_event.ResultsInDeathNullFlavor = NullFlavor.NI
#reaction_event.LifeThreatening = TrueOnly(1, True)
reaction_event.LifeThreateningNullFlavor = NullFlavor.NI
#reaction_event.CausedProlongedHospitalisation = TrueOnly(1, True)
reaction_event.CausedProlongedHospitalisationNullFlavor = NullFlavor.NI
#reaction_event.DisablingIncapacitating =TrueOnly(1, True)
reaction_event.DisablingIncapacitatingNullFlavor = NullFlavor.NI
#reaction_event.CongenitalAnomalyBirthDefect = TrueOnly(1, True)
reaction_event.CongenitalAnomalyBirthDefectNullFlavor = NullFlavor.NI
#reaction_event.OtherMedicallyImportantCondition = TrueOnly(1, True)
reaction_event.OtherMedicallyImportantConditionNullFlavor = NullFlavor.NI

# Adds reactions to list
reaction_events.Add(reaction_event)


# Drug section (add items to list)
drug_informations = List[DrugInformation]()
drug_information = DrugInformation()
drug_information.DrugReferenceId = "878893d3-42a5-41e5-8767-af8b63fc6cd0" # TODO: Generate GUID instead
drug_information.CharacterisationOfDrugRole = "1"
drug_information.MedicinalProductNameAsReportedByThePrimarySource = "MedicinalProductNameAsReportedByThePrimarySource"
#drug_information.MpidVersionDateNumber = ""
#drug_information.MedicinalProductIdentifierMpid = ""
drug_information.MedicinalProductIdentifierWHODrugVersion = "20240830"
drug_information.MedicinalProductIdentifierWHODrugProductId = 4765
drug_information.MedicinalProductIdentifierWHODrugProductName = "MedicinalProductIdentifierWHODrugProductName"
#drug_information.PhpidVersionDateNumber = ""
#drug_information.PharmaceuticalProductIdentifierPhpid = ""
drug_information.IdentificationOfTheCountryWhereTheDrugWasObtained = ""
drug_information.InvestigationalProductBlinded = TrueOnly(1, True)
drug_information.AuthorisationApplicationNumber = ""
drug_information.CountryOfAuthorisationApplication = ""
drug_information.NameOfHolderApplicant = ""

# Dose information (add to list)
dosageInformations = List[DosageInformation]()

dosageInformation = DosageInformation()
dosageInformation.Dose = ""
dosageInformation.DoseUnit = ""
dosageInformation.DoseNumber = ""
dosageInformation.NumberOfUnitsInTheInterval = ""
dosageInformation.DefinitionOfTheTimeIntervalUnit = ""
dosageInformation.DateAndTimeOfStartOfDrug = ""
dosageInformation.DateAndTimeOfLastAdministration = ""
dosageInformation.DurationOfDrugAdministration = ""
dosageInformation.DurationOfDrugAdministrationUnit = ""
dosageInformation.BatchLotNumber = ""
dosageInformation.ExpiryDate = ""
dosageInformation.ReconstitutionDate = ""
dosageInformation.DosageText = ""
dosageInformation.PharmaceuticalDoseForm = "PharmaceuticalDoseForm"
dosageInformation.PharmaceuticalDoseFormTermIDVersionDateNumber = "20240830"
dosageInformation.PharmaceuticalDoseFormTermID = "PDF-10219000"
dosageInformation.PharmaceuticalDoseFormCodeSystem = "0.4.0.127.0.16.1.1.2.1"
dosageInformation.RouteOfAdministration = "RouteOfAdministration"
dosageInformation.RouteOfAdministrationTermIDVersionDateNumber = "20240830"
dosageInformation.RouteOfAdministrationTermID = "ROA-20053000"
dosageInformation.RouteOfAdministrationCodeSystem = "0.4.0.127.0.16.1.1.2.6"
dosageInformation.ParentRouteOfAdministration = "ParentRouteOfAdministration"
dosageInformation.ParentRouteofAdministrationTermIDVersionDateNumber = "20240830"
dosageInformation.ParentRouteOfAdministrationTermID = "ROA-20053000"
dosageInformation.ParentRouteOfAdministrationCodeSystem = "0.4.0.127.0.16.1.1.2.6"
diluentInformation = DiluentInformation()
diluentInformation.DiluentName = ""
diluentInformation.DiluentBatchLotNumber = ""
diluentInformation.DiluentExpiryDate = ""
dosageInformation.DiluentInformation = diluentInformation
healthFacility = HealthFacility()
healthFacility.HealthFacilityOrganisation = ""
healthFacility.HealthFacilityStreetAddress = ""
healthFacility.HealthFacilityCity = ""
healthFacility.HealthFacilityCounty = ""
healthFacility.HealthFacilityStateOrProvince = ""
healthFacility.HealthFacilityPostcode = ""
healthFacility.HealthFacilityTelephone = ""
dosageInformation.HealthFacility = healthFacility

# Add to list
dosageInformations.Add(dosageInformation)
drug_information.DosageInformations = dosageInformations

drug_information.CumulativeDoseToFirstReaction = ""
drug_information.CumulativeDoseToFirstReactionUnit = ""
drug_information.GestationPeriodAtTimeOfExposure = ""
drug_information.GestationPeriodAtTimeOfExposureUnit = ""

indicationForUseInCase = IndicationForUseInCase()
indicationForUseInCase.IndicationAsReportedByThePrimarySource = ""
indicationForUseInCase.IndicationMedDRAVersion = "27.0"
indicationForUseInCase.IndicationMedDRACode = 10000001
indicationForUseInCases = List[IndicationForUseInCase]()
indicationForUseInCases.Add(indicationForUseInCase)
drug_information.IndicationForUseInCases = indicationForUseInCases
drug_information.ActionsTakenWithDrug = ""

# Drug reaction matrix (add to list)
drugreactionsEventsMatrixes = List[DrugreactionsEventsMatrix]()

drugreactionsEventsMatrix = DrugreactionsEventsMatrix()
drugreactionsEventsMatrix.TimeIntervalBetweenBeginningOfDrugAdministrationAndStartOfReactionEvent = ""
drugreactionsEventsMatrix.TimeIntervalBetweenBeginningOfDrugAdministrationAndStartOfReactionEventUnit = ""
drugreactionsEventsMatrix.TimeIntervalBetweenLastDoseOfDrugAndStartOfReactionEvent = ""
drugreactionsEventsMatrix.TimeIntervalBetweenLastDoseOfDrugAndStartOfReactionEventUnit = ""
drugreactionsEventsMatrix.DidReactionRecurOnReadministration = ""
drugreactionsEventsMatrix.ReactionReferenceId = "878893d3-42a5-41e5-8767-af8b63fc6cd0" # Use ID from previously created reactions
drugreactionsEventsMatrixes.Add(drugreactionsEventsMatrix)
drug_information.DrugreactionsEventsMatrixes = drugreactionsEventsMatrixes

# Additional information on drug (add to list)
additionalInformationOnDrugs = List[AdditionalInformationOnDrug]()
additionalInformationOnDrug = AdditionalInformationOnDrug()
additionalInformationOnDrug.AdditionalInformationOnDrugCoded = ""
additionalInformationOnDrugs.Add(additionalInformationOnDrug)
drug_information.AdditionalInformationOnDrugs = additionalInformationOnDrugs
drug_information.AdditionalInformationOnDrug = ""

# Substance information (add to list) - used when more specific information is unavailable
substanceSpecifiedSubstanceIdentifierAndStrengths = List[SubstanceSpecifiedSubstanceIdentifierAndStrength]()
substanceSpecifiedSubstanceIdentifierAndStrength = SubstanceSpecifiedSubstanceIdentifierAndStrength()
substanceSpecifiedSubstanceIdentifierAndStrength.SubstanceSpecifiedSubstanceName = ""
substanceSpecifiedSubstanceIdentifierAndStrength.SubstanceSpecifiedSubstanceTermIdVersion = ""
substanceSpecifiedSubstanceIdentifierAndStrength.SubstanceSpecifiedSubstanceTermId = ""
substanceSpecifiedSubstanceIdentifierAndStrength.SubstanceSpecifiedStrength = ""
substanceSpecifiedSubstanceIdentifierAndStrength.SubstanceSpecifiedStrengthUnit = ""
substanceSpecifiedSubstanceIdentifierAndStrengths.Add(substanceSpecifiedSubstanceIdentifierAndStrength)
drug_information.SubstanceSpecifiedSubstanceIdentifierAndStrengths = substanceSpecifiedSubstanceIdentifierAndStrengths

drug_informations.Add(drug_information)

# Test results (add to list)
test_results = List[ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient]()
test_result = ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient()
test_result.TestDate = "20240830"
test_result.TestName = ""
test_result.TestNameMedDRAVersion = "27.0"
test_result.TestNameMedDRACode = 10000001
test_result.TestResultCode = ""
test_result.TestResult = ""
test_result.TestResultInclusive = False
test_result.TestResultUnit = ""
test_result.ResultUnstructuredData = ""
test_result.NormalLowValue = ""
test_result.NormalHighValue = ""
test_result.Comments = ""
test_result.MoreInformationAvailable = False
test_results.Add(test_result)

assessment = Assessment()

# Create an instance of the Icsr class and set its properties
icsr = Icsr()
icsr.IdentificationOfTheCaseSafetyReport = identification
icsr.NarrativeCaseSummaryAndOtherInformation = narrative
icsr.PrimarySourcesOfInformations = primary_sources
icsr.InformationOnSenderOfCaseSafetyReport = sender_info
icsr.LiteratureReferences = literature_references
icsr.StudyIdentification = study_identification
icsr.PatientCharacteristics = patient_characteristics
icsr.ReactionEvents = reaction_events
icsr.DrugInformations = drug_informations
icsr.ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient = test_results
icsr.Assessment = assessment

includedDocument = IncludedDocument()
attachments = List[IncludedDocument]() # Your attachments list



# Create the file
stream = FileStream("output.xml", FileMode.Create, FileAccess.Write)  # Your stream object

# Write E2B R3 XML to the file
write(exn_handler, info, stream, attachments, icsr)
print("\nE2B R3 XML file has been generated successfully: output.xml")
