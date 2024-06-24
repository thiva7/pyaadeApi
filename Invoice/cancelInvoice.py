from invoiceData import  InvoiceParts as prt
from . import root, invoice, api_url
import xml.etree.ElementTree as ET

class CancelInvoice:


    def SendCancel(self, Mark , entityVatNumber):
        response = api_url.cancel_invoice(Mark , entityVatNumber=entityVatNumber)
        return response

    def getResponse(self, response):
        if '<?xml' in response:
            root = ET.fromstring(response)
            status_code = root.find('response/statusCode').text
            if status_code == 'Success':
                return response
            else:
                message = root.find('.//message').text
                return f"{message}"
        else:
            return response['message']