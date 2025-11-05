import xml.etree.ElementTree as ET

class NotificationCharacteristic:
    def __init__(self):
        import uuid
        from datetime import datetime
        
        case_number = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Basic Report Information
        self.NotificationDate = ""
        self.ReportTitle = ""
        self.WorldWideUniqueCaseIdentificationNumber = f"SE-UMC-{case_number}"
        self.SendersCaseSafetyReportUniqueIdentifier = f"SE-UMC-{case_number}"
        self.FirstSenderOfThisCase = "1"
        self.TypeOfReport = "1"
        self.DateReportWasFirstReceivedFromSource = datetime.now().strftime("%Y%m%d")
        self.DateOfMostRecentInformationForThisReport = datetime.now().strftime("%Y%m%d")
        self.DateOfCreation = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Message Format Information
        self.MessageFormatVersion = "2.1"
        self.MessageFormatRelease = "2.0"
        self.MessageNumb = "0"
        self.MessageSenderIdentifier = ""
        self.MessageReceiverIdentifier = ""
        self.MessageDateFormat = "204"
        self.ReportType = []
        self.ReportFormatVersion = "2.1"
        self.FollowupNumber = None
        
        # Case Identification
        self.PrimarySrc = ""
        self.ReceiverType = None
        self.OtherCaseIds = None
        self.OtherCaseIdentifiersInPreviousTransmissions = True
        self.OtherCaseIdentifiersInPreviousTransmissionsNullFlavor = "NI"
        self.ReportNullificationAmendment = ""
        self.ReasonForNullificationAmendment = ""
        
        # UMC Extensions
        self.AefiCase = True
        self.DateOfReport = ""
        
        # Doctor Information
        self.DoctorFamilyName = ""
        self.DoctorGivenName = ""
        self.DoctorOrganization = ""
        
        # Sender Information
        self.SendersOrganisation = "UMC"
        self.SendersDepartment = ""
        self.SendersSupervisedBy = ""
        self.SendersCity = ""
        self.SendersState = ""
        self.SendersCountryCode = "SE"
        self.SendersEmailAddress = ""
        self.SendersPhoneNumber = ""
        self.SendersGivenName = ""
        self.SendersFamilyName = ""
        self.SendersPostalCode = ""
        self.SendersStreetAddress = ""
        self.SenderType = "1"
        

def extract_notification_characteristics(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    print("\nDatos Notificacion:")
    # print("\nTodos los nodos principales en el XML:")
    # for elem in root.iter():
    #     print(f"Tag: {elem.tag}, Attributes: {elem.attrib}")

    datos_notificacion = NotificationCharacteristic()

    for item in root.findall(".//item"):
        link_id = item.find("linkId")
        if link_id is not None:
            value = link_id.attrib.get('value')
            #print("Processing linkId:", value)

            if value == "fechaNotificacion":
                element = item.find(".//answer/valueDate")
                if element is not None and 'value' in element.attrib:
                    datos_notificacion.NotificationDate = element.attrib['value']
                    print("Extracted fechaNotificacion:", element.attrib['value'])

            elif value == "tituloReporte":
                element = item.find(".//answer/valueString")
                if element is not None and 'value' in element.attrib:
                    datos_notificacion.ReportTitle = element.attrib['value']
                    print("Extracted tituloReporte:", element.attrib['value'])

            elif value == "idCasoUnico":
                element = item.find(".//answer/valueString")
                if element is not None and 'value' in element.attrib:
                    datos_notificacion.WorldWideUniqueCaseIdentificationNumber = element.attrib['value']
                    print("Extracted idCasoUnico:", element.attrib['value'])

            elif value == "idReporteUnico":
                element = item.find(".//answer/valueString")
                if element is not None and 'value' in element.attrib:
                    datos_notificacion.SendersCaseSafetyReportUniqueIdentifier = element.attrib['value']
                    print("Extracted idReporteUnico:", element.attrib['value'])

            elif value == "primerRemitente":
                element = item.find(".//answer/valueString")
                if element is not None and 'value' in element.attrib:
                    datos_notificacion.FirstSenderOfThisCase = element.attrib['value']
                    print("Extracted primerRemitente:", element.attrib['value'])

            elif value == "tipoReporte":
                element = item.find(".//answer/valueString")
                if element is not None and 'value' in element.attrib:
                    datos_notificacion.TypeOfReport = element.attrib['value']
                    print("Extracted tipoReporte:", element.attrib['value'])

            elif value == "fechaRecepcion":
                element = item.find(".//answer/valueDate")
                if element is not None and 'value' in element.attrib:
                    datos_notificacion.DateReportWasFirstReceivedFromSource = element.attrib['value']
                    print("Extracted fechaRecepcion:", element.attrib['value'])

            elif value == "fechaInformacionReciente":
                element = item.find(".//answer/valueDate")
                if element is not None and 'value' in element.attrib:
                    datos_notificacion.DateOfMostRecentInformationForThisReport = element.attrib['value']
                    print("Extracted fechaInformacionReciente:", element.attrib['value'])

            elif value == "fechaCreacion":
                element = item.find(".//answer/valueDate")
                if element is not None and 'value' in element.attrib:
                    datos_notificacion.DateOfCreation = element.attrib['value']
                    print("Extracted fechaCreacion:", element.attrib['value'])

            # Agrega más condiciones para otros campos según sea necesario

    
    # print("Notification Date:", datos_notificacion.NotificationDate)
    # print("Report Title:", datos_notificacion.ReportTitle)
    # print("World Wide Unique Case Identification Number:", datos_notificacion.WorldWideUniqueCaseIdentificationNumber)
    # print("Sender's Case Safety Report Unique Identifier:", datos_notificacion.SendersCaseSafetyReportUniqueIdentifier)
    # print("First Sender Of This Case:", datos_notificacion.FirstSenderOfThisCase)
    # print("Type Of Report:", datos_notificacion.TypeOfReport)
    # print("Date Report Was First Received From Source:", datos_notificacion.DateReportWasFirstReceivedFromSource)
    # print("Date Of Most Recent Information For This Report:", datos_notificacion.DateOfMostRecentInformationForThisReport)
    # print("Date Of Creation:", datos_notificacion.DateOfCreation)

    return datos_notificacion
