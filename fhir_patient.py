import xml.etree.ElementTree as ET
import datetime

class PatientCharacteristics:
    def __init__(self):
        self.PatientNameOrInitials = "Anonimo"
        self.PatientsGivenName = ""
        self.PatientsMiddleName = ""
        self.PatientsFamilyName = ""
        self.PatientsStreet = ""
        self.PatientsCity = ""
        self.PatientsCounty = ""
        self.PatientsStateOrProvince = ""
        self.PatientsPostCode = ""
        self.PatientsTelephone = ""
        self.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberGpMedicalRecordNumber = ""
        self.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberSpecialistRecordNumber = ""
        self.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberHospitalRecordNumber = ""
        self.PatientMedicalRecordNumberAndTheSourcesOfTheRecordNumberInvestigationNumber = ""
        self.PersonalIdentificationNumber = ""
        self.DateOfBirth = ""
        self.AgeAtTimeOfOnsetOfReactionEvent = ""
        self.AgeAtTimeOfOnsetOfReactionEventUnit = ""
        self.GestationPeriodWhenReactionEventWasObservedInTheFoetus = ""
        self.GestationPeriodWhenReactionEventWasObservedInTheFoetusUnit = ""
        self.Pregnant = False
        self.Lactating = False
        self.PatientAgeGroupAsPerReporter = ""
        self.BodyWeight = ""
        self.Height = ""
        self.Sex = ""
        self.LastMenstrualPeriodDate = ""

def extract_patient_characteristics(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    print("\nDatos Paciente:")
    # print("\nTodos los nodos principales en el XML:")
    # for elem in root.iter():
    #     print(f"Tag: {elem.tag}, Attributes: {elem.attrib}")
    patient_characteristics = PatientCharacteristics()

    for item in root.findall(".//item"):
        link_id = item.find("linkId")
        if link_id is not None:
            value = link_id.attrib.get('value')
            #print("Processing linkId:", value)

            if value == "idPaciente":
                element = item.find(".//answer/valueString")
                if element is not None and 'value' in element.attrib:
                    patient_characteristics.PersonalIdentificationNumber = element.attrib['value']
                    print("Extracted idPaciente:", element.attrib['value'])

            elif value == "nombreResidenciaHabitual":
                element = item.find(".//answer/valueString")
                if element is not None and 'value' in element.attrib:
                    patient_characteristics.PatientsStreet = element.attrib['value']
                    print("Extracted nombreResidenciaHabitual:", element.attrib['value'])

            elif value == "sexoPaciente":
                element = item.find(".//answer/valueCoding/code")
                if element is not None and 'value' in element.attrib:
                    # Ajuste: Mapeo para compatibilidad con E2B
                    sex_value = element.attrib['value']
                    if sex_value == "male":
                        patient_characteristics.Sex = "1"
                    elif sex_value == "female":
                        patient_characteristics.Sex = "2"
                    else:
                        patient_characteristics.Sex = "0"
                    print("Mapped sexoPaciente:", patient_characteristics.Sex)

            elif value == "fechaNacimiento":
                element = item.find(".//answer/valueDate")
                if element is not None and 'value' in element.attrib:
                    date_of_birth = datetime.datetime.strptime(element.attrib['value'], '%Y-%m-%d').strftime('%Y%m%d')
                    patient_characteristics.DateOfBirth = date_of_birth
                    print("Formatted fechaNacimiento:", date_of_birth)

    # print("Personal Identification Number:", patient_characteristics.PersonalIdentificationNumber)
    # print("Street Address:", patient_characteristics.PatientsStreet)
    # print("Sex:", patient_characteristics.Sex)
    # print("Date of Birth:", patient_characteristics.DateOfBirth)
    return patient_characteristics












