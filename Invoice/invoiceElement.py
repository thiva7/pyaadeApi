import xml.etree.ElementTree as ET
from aade_api import SetApi



AADE_ATTRIBUTES = {
    'xmlns': 'http://www.aade.gr/myDATA/invoice/v1.0',
    'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xsi:schemaLocation': "http://www.aade.gr/myDATA/invoice/v1.0/InvoicesDoc-v0.6.xsd",
    'xmlns:icls': "https://www.aade.gr/myDATA/incomeClassificaton/v1.0",
    'xmlns:ecls': "https://www.aade.gr/myDATA/expensesClassificaton/v1.0"
}


root = ET.Element("InvoicesDoc", attrib=AADE_ATTRIBUTES)
invoice = ET.SubElement( root, "invoice")

api_url = SetApi()