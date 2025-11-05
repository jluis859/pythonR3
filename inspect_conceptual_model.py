import clr
import sys
from System import Type
from System.Reflection import Assembly

#assembly = Assembly.LoadFile(r'C:\Repos\Python R3Model\R3Model\Umc.R3Model.ConceptualModel.dll')
assembly = Assembly.LoadFile(r'/Users/jluis859/Python_Workspace/Python R3Model/R3Model/Umc.R3Model.ConceptualModel.dll')

Icsr_type = assembly.GetType('Umc.R3Model.ConceptualModel.Icsr')
IdentificationOfTheCaseSafetyReport_type = assembly.GetType('Umc.R3Model.ConceptualModel.IdentificationOfTheCaseSafetyReport')
NarrativeCaseSummaryAndOtherInformation_type = assembly.GetType('Umc.R3Model.ConceptualModel.NarrativeCaseSummaryAndOtherInformation')
PrimarySourcesOfInformation_type = assembly.GetType('Umc.R3Model.ConceptualModel.PrimarySourcesOfInformation')
InformationOnSenderOfCaseSafetyReport_type = assembly.GetType('Umc.R3Model.ConceptualModel.InformationOnSenderOfCaseSafetyReport')
LiteratureReference_type = assembly.GetType('Umc.R3Model.ConceptualModel.LiteratureReference')
StudyIdentification_type = assembly.GetType('Umc.R3Model.ConceptualModel.StudyIdentification')
PatientCharacteristics_type = assembly.GetType('Umc.R3Model.ConceptualModel.PatientCharacteristics')
ReactionEvent_type = assembly.GetType('Umc.R3Model.ConceptualModel.ReactionEvent')
DrugInformation_type = assembly.GetType('Umc.R3Model.ConceptualModel.DrugInformation')
ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient_type = assembly.GetType('Umc.R3Model.ConceptualModel.ResultsOfTestsAndProceduresRelevantToTheInvestigationOfThePatient')
Assessment_type = assembly.GetType('Umc.R3Model.ConceptualModel.Assessment')
IncludedDocument_type = assembly.GetType('Umc.R3Model.ConceptualModel.IncludedDocument')
OtherCaseIdentifiers_type = assembly.GetType('Umc.R3Model.ConceptualModel.OtherCaseIdentifiers')
StructuredInformationonRelevantMedicalHistory_type = assembly.GetType('Umc.R3Model.ConceptualModel.StructuredInformationonRelevantMedicalHistory')
RelevantPastDrugHistory_type = assembly.GetType('Umc.R3Model.ConceptualModel.RelevantPastDrugHistory')
ReportedCausesOfDeath_type = assembly.GetType('Umc.R3Model.ConceptualModel.ReportedCausesOfDeath')
AutopsyDeterminedCausesOfDeath_type = assembly.GetType('Umc.R3Model.ConceptualModel.AutopsyDeterminedCausesOfDeath')
ForAParentChildFoetusReportInformationConcerningParent_type = assembly.GetType('Umc.R3Model.ConceptualModel.ForAParentChildFoetusReportInformationConcerningParent')
StructuredInformationOfParent_type = assembly.GetType('Umc.R3Model.ConceptualModel.StructuredInformationOfParent')
RelevantPastDrugHistoryOfParent_type = assembly.GetType('Umc.R3Model.ConceptualModel.RelevantPastDrugHistoryOfParent')
DiluentInformation_type = assembly.GetType('Umc.R3Model.ConceptualModel.DiluentInformation')
HealthFacility_type = assembly.GetType('Umc.R3Model.ConceptualModel.HealthFacility')
DosageInformation_type = assembly.GetType('Umc.R3Model.ConceptualModel.DosageInformation')
IndicationForUseInCase_type = assembly.GetType('Umc.R3Model.ConceptualModel.IndicationForUseInCase')
DrugreactionsEventsMatrix_type = assembly.GetType('Umc.R3Model.ConceptualModel.DrugreactionsEventsMatrix')
AdditionalInformationOnDrug_type = assembly.GetType('Umc.R3Model.ConceptualModel.AdditionalInformationOnDrug')
SubstanceSpecifiedSubstanceIdentifierAndStrength_type = assembly.GetType('Umc.R3Model.ConceptualModel.SubstanceSpecifiedSubstanceIdentifierAndStrength')
CaseSummaryAndReportersCommentsInNativeLanguage_type = assembly.GetType('Umc.R3Model.ConceptualModel.CaseSummaryAndReportersCommentsInNativeLanguage')


# Adjust the class and attribute here to incpect the attributes
property_info = IdentificationOfTheCaseSafetyReport_type.GetProperty('WorldWideUniqueCaseIdentificationNumber')

# Get the custom attributes
attributes = property_info.GetCustomAttributes(False)

# Print the attributes
for attribute in attributes:
    print(f"Attribute: {attribute}")
    for prop in attribute.GetType().GetProperties():
        value = prop.GetValue(attribute, None)
        print(f"  {prop.Name}: {value}")

# Get all properties of IdentificationOfTheCaseSafetyReport_type
properties = IdentificationOfTheCaseSafetyReport_type.GetProperties() 
print("Properties:")
for prop in properties:
    print(f"  {prop.Name}")

# Get all properties of Assessment_type
properties = Assessment_type.GetProperties() 
print("Assessment Properties:")
for prop in properties:
    print(f"  {prop.Name}")

# Get CausalityAssessments property details
causalityAssessments_property = Assessment_type.GetProperty('CausalityAssessments')
print("\nCausalityAssessments Property Details:")
print(f"  PropertyType: {causalityAssessments_property.PropertyType}")

# Try to get the element type if it's a collection
if causalityAssessments_property.PropertyType.IsGenericType:
    element_type = causalityAssessments_property.PropertyType.GetGenericArguments()[0]
    print(f"  Element Type: {element_type}")
    
    # Get properties of the element type
    element_properties = element_type.GetProperties()
    print("\nCausalityAssessment Properties:")
    for prop in element_properties:
        print(f"  {prop.Name}")

# Get properties of CausalityAssessment
element_type = causalityAssessments_property.PropertyType.GetGenericArguments()[0]
element_properties = element_type.GetProperties()
print("\nCausalityAssessment Properties:")
for prop in element_properties:
    print(f"  {prop.Name}")
    
    # Get property type details
    print(f"    Type: {prop.PropertyType}")
    
    # If it's a collection, get the element type
    if prop.PropertyType.IsGenericType:
        inner_element_type = prop.PropertyType.GetGenericArguments()[0]
        print(f"    Element Type: {inner_element_type}")
        
        # Get properties of the inner element type
        inner_element_properties = inner_element_type.GetProperties()
        print(f"    Properties of {inner_element_type}:")
        for inner_prop in inner_element_properties:
            print(f"      {inner_prop.Name}")


properties = StudyIdentification_type.GetProperties() 
print("StudyIdentification_type Properties:")
for prop in properties:
    print(f"  {prop.Name}")