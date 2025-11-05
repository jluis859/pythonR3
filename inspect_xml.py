import xml.etree.ElementTree as ET

def inspect_xml():
    try:
        xml_path = "FHIR/QR-ejUnoNuevo.xml"
        tree = ET.parse(xml_path)
        root = tree.getroot()

        def print_tree(element, path=""):
            for child in element:
                print(f"Path: {path}/{child.tag}, Attributes: {child.attrib}, Text: {child.text}")
                print_tree(child, path=f"{path}/{child.tag}")

        print_tree(root)
    except Exception as e:
        print(f"Error al leer el XML: {e}")

if __name__ == "__main__":
    inspect_xml()
