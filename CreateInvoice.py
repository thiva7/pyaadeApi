import json
import xml.etree.ElementTree as ET
from utils.helper import forbiddencounterpart
import parameters as par

from afm_checks import can_be_afm
from invoiceData import InvoiceHead , InvoiceParts as prt

from xml_parse import parse_response, parse_xml_invoice
from xml.dom import minidom

def xmlinvoice2json(invoice_xml, response):
    invoice = parse_xml_invoice(invoice_xml)
    resp = parse_response(response)

    # print(resp['statusCode'])
    if resp['statusCode'] == 'Success':
        invoice['uid'] = resp['invoiceUid']
        invoice['mark'] = resp['invoiceMark']
    head = invoice['invoice']['invoiceHeader']
    json_name = f"CompleteJsons/{head['issueDate']}.{head['series']}.{head['aa']}.json"
    with open(json_name, "w", encoding='utf-8') as outfile:
        json.dump(invoice, outfile, ensure_ascii=False , indent=4) # για να αποθηκευτεί το json σε ευκολοδιάβαστη μορφή
    return invoice


AADE_ATTRIBUTES = {
    'xmlns': 'http://www.aade.gr/myDATA/invoice/v1.0',
    'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xsi:schemaLocation': "http://www.aade.gr/myDATA/invoice/v1.0/InvoicesDoc-v0.6.xsd",
    'xmlns:icls': "https://www.aade.gr/myDATA/incomeClassificaton/v1.0",
    'xmlns:ecls': "https://www.aade.gr/myDATA/expensesClassificaton/v1.0"
}



class Make_Invoice:
    def __init__(self):
        self.issuer_afm = ''
        self.issuer_branch = '0'
        self.issuer_country = 'GR'
        self.counterpart_afm = ''
        self.counterpart_branch = '0'
        self.counterpart_country = 'GR'
        self.counterpart_name = ''
        self.counterpart_street = ''
        self.counterpart_postalCode = ''
        self.counterpart_city = ''
        self.header_series = 'ΑΑ'
        self.header_aa = '1'
        self.header_issueDate = '2020-01-01'
        self.header_invoiceType = ''
        self.header_currency = 'EUR'
        self.header_dispatchDate = '' # 2020-01-01
        self.header_dispatchTime = '' # 12:00:00
        self.header_vehicleNumber = '' # 'ΕΖ 1234'
        self.header_movePurpose = '' # 8
        self.payment_type = '3'
        self.payment_amount = ''
        self.payment_info = 'Μετρητά'
        self.prt = prt()

        self.root = ET.Element("InvoicesDoc", attrib=AADE_ATTRIBUTES)
        self.invoice = ET.SubElement( self.root, "invoice")

    def is_uid_in_aade(self , api, uid, dat) -> bool:
        uids = api.request_uids(dat)
        return uid in uids

    def setIssuer(self):
        self.prt.issuer(self.invoice, afm=self.issuer_afm, country=self.issuer_country, branch=self.issuer_branch )

    def setCounterpart(self):
        if self.header_invoiceType not in forbiddencounterpart:
            self.prt.counter_part(self.invoice, afm=self.counterpart_afm ,name=self.counterpart_name, country=self.counterpart_country, branch=self.counterpart_branch ,
                                  street=self.counterpart_street,  postalCode=self.counterpart_postalCode, city=self.counterpart_city)

    def setHeader(self):
        self.prt.header(self.invoice, series=self.header_series, aa=self.header_aa,date=self.header_issueDate, typ=self.header_invoiceType, currency=self.header_currency,
                        dispatchDate=self.header_dispatchDate, dispatchTime=self.header_dispatchTime, vehicleNumber=self.header_vehicleNumber, purpose=self.header_movePurpose)

    def setPayment(self , linedata: par.LData):
        if self.payment_amount == '':
            payment_amount = linedata.total
        else:
            payment_amount = self.payment_amount
        self.prt.payment(self.invoice, typ=self.payment_type, amount=payment_amount, info= self.payment_info )

    def setLines(self, data):
        self.prt.lines(self.invoice, data=data)

    def setSummary(self, data):
        self.prt.summary(self.invoice, data=data)

    def create_xml(self):
        return ET.tostring(self.root, encoding="UTF-8", xml_declaration=True)

    def SendInvoices(self, api):
        ihd = InvoiceHead(afm=self.issuer_afm, date=self.header_issueDate, branch=self.issuer_branch,
                          type=self.header_invoiceType, series=self.header_series, aa=self.header_aa,cafm=self.counterpart_afm )

        if not can_be_afm(ihd.afm):
            return {"message": "Invalid issuer AFM"}

        if self.is_uid_in_aade(api, ihd.uid, ihd.date):
            return {"message": "Invoice already exists"}

        xml = self.create_xml()
        xmlstr = minidom.parseString(xml).toprettyxml(indent="   ")
        # print(xmlstr)
        response = api.send_invoices(xml)
        # check if response is xml or json
        if response.startswith('<?xml'):
            # xmlinvoice2json(xml, response)
            return response
        else:
            response = json.loads(response)
            return response

    def _check_response(self, response):
        if '<?xml' in response:
            root = ET.fromstring(response)
            status_code = root.find('response/statusCode').text
            if status_code == 'Success':
                # print(res)
                invoice_uid = root.find('response/invoiceUid').text
                invoiceMark = root.find('response/invoiceMark').text
                QrURL = root.find('response/qrUrl').text
                # print(f"invoice_uid: {invoice_uid}")
                # print(f"invoiceMark: {invoiceMark}")
                # print(f"QrURL: {QrURL}")
                return response
            else:
                message = root.find('.//message').text
                return f"{message}"

        else:
            return response['message']


if __name__ == '__main__':
    from aade_api import AadeApi

    ldt = par.InvData(
        lines=[
            par.LData('category1_1', 'E3_561_001', value=156, vatcat=1),
            par.LData('category1_1', 'E3_561_001', value=428, vatcat=1),
        ],
        per_invoice_taxes=[
            par.TaxData(value=156, taxType=2, taxTypeCategory=9, taxTypePrice=4.2),
            par.TaxData(value=156, taxType=1, taxTypeCategory=1),
        ]
    )
    invoice = Make_Invoice()
    invoice.issuer_afm = "123456789"
    invoice.issuer_branch = '4'
    invoice.counterpart_afm = '094077783'
    invoice.counterpart_name = 'ΑΒΓΔΕ'
    invoice.counterpart_street = 'ΖΗΘΙ'
    invoice.counterpart_postalCode = '12345'
    invoice.counterpart_city = 'ΚΑΛΑΜΑΤΑ'
    invoice.header_series = 'AB'
    invoice.header_aa = '1'
    invoice.header_issueDate = '2020-01-01'
    invoice.header_invoiceType = '1.1'
    invoice.header_movePurpose = '8'
    invoice.payment_info = "Hey, I am paying you!"
    invoice.setIssuer()
    invoice.setCounterpart()
    invoice.setHeader()
    invoice.setPayment( ldt)
    invoice.setLines(ldt)
    invoice.setSummary(ldt)
    test_api = AadeApi(True,  True)

    res = invoice.SendInvoices(test_api)
    print(invoice._check_response(res))

