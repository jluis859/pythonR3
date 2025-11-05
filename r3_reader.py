import clr
import sys
from System.IO import FileStream, FileMode, FileAccess
from System.Xml.XPath import XPathDocument

# Add the path to the directory containing your .NET DLL
#sys.path.append(r'C:\Repos\Python R3Model\R3Model')
sys.path.append('/Users/jluis859/Python_Workspace/Python R3Model/R3Model')

# Load the .NET assembly
clr.AddReference('Umc.R3Model.ConceptualModel')
clr.AddReference('Umc.R3Model.E2BR3')
clr.AddReference('Umc.R3Model.ICHModel')
clr.AddReference('System.Collections')


# Import the namespaces
from Umc.R3Model.ConceptualModel import Icsr, IdentificationOfTheCaseSafetyReport, NarrativeCaseSummaryAndOtherInformation, PrimarySourcesOfInformation, InformationOnSenderOfCaseSafetyReport, LiteratureReference, StudyIdentification, PatientCharacteristics, ReactionEvent, DrugInformation, ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient, Assessment, IncludedDocument, OtherCaseIdentifiers, NullFlavor, TrueOnly, StructuredInformationonRelevantMedicalHistory, RelevantPastDrugHistory, ReportedCausesOfDeath, AutopsyDeterminedCausesOfDeath, ForAParentChildFoetusReportInformationConcerningParent, StructuredInformationOfParent, RelevantPastDrugHistoryOfParent, DiluentInformation, HealthFacility, DosageInformation, IndicationForUseInCase, DrugreactionsEventsMatrix, AdditionalInformationOnDrug, SubstanceSpecifiedSubstanceIdentifierAndStrength, CaseSummaryAndReportersCommentsInNativeLanguage
from Umc.R3Model.E2BR3.R3ToICSR import R3Mapper, R3MapperFactory
from Umc.R3Model.E2BR3.R3ToICSR.Model import TransformationResult, TransformationResultItem

# Open the file using FileStream
file_stream = FileStream("input_ex1.xml", FileMode.Open, FileAccess.Read)

# Convert FileStream to XPathDocument
xpath_doc = XPathDocument(file_stream)

r3Mapper = R3MapperFactory.CreateDefaultMapper()

# Map the R3 to the internal data model
transformationResult = r3Mapper.Map(xpath_doc)

# Don't forget to close the file stream
file_stream.Close()

# Use the informarion that has been mapped, since the R3Message can contain multiple ICSRs they can be found in the list in TransformationResultItems
# TransformationResult contains two fields 
#  - IchIcsrTransmissionIdentificationBatchWrapper where you can find batch information
#  - List of TransformationItems
# TransformationItem contains three fields
#  - IchIcsrMessageHeaderMessageWrapper contain information about the message header (IcsrId, MessageIdentifier, MessageSenderIdentifier, MessageReceiverIdentifier, DateOfMessageCreation)
#  - Icsr where you will find all relevant ICSR information
#  - List of IncludedDocuments where you will find all attachments (Id, MediaType, FileName, Attachment)

for item in transformationResult.TransformationResultItems: 
    print("Item")
    print(item.Icsr.IdentificationOfTheCaseSafetyReport.WorldWideUniqueCaseIdentificationNumber)


