from invoiceData import  InvoiceParts as prt
from . import root, invoice , api_url

import xml.etree.ElementTree as ET
import json
from xml.dom import minidom
from afm_checks import can_be_afm

class SendInvoice:
    xml: str


    def is_uid_in_aade(self, api, uid, dat) -> bool:
        uids = api.request_uids(dat)
        return uid in uids

    def SendInvoices(self,  ihd ):
        if not can_be_afm(ihd.afm):
            return '{"message" :  Invalid issuer AFM}'
        if self.is_uid_in_aade(api_url, ihd.uid, ihd.date):
            return {"message": "Invoice already exists"}

        response = api_url.send_invoices(self.xml)
        # check if response is xml or json
        if response.startswith('<?xml'):
            return response
        else:
            response = json.loads(response)
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