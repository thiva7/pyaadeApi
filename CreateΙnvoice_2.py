from Invoice import *
from xml.etree import ElementTree as ET
from xml.dom import minidom
import parameters as par
from environs import Env

env = Env()
env.read_env()


issuer = issuer()
issuer.afm = env.str('_AFM')
issuer.country = 'GR'
issuer.branch = '0'
issuer.setIssuer()

counterpart = Counterpart()
counterpart.afm = '094077783'
counterpart.country = 'GR'
counterpart.branch = '9'
counterpart.name = 'name'
counterpart.street = 'str'
counterpart.postalCode = '32200'
counterpart.city = 'chalkida'
counterpart.setCounterpart()

header = Header_()
header.series = 'AD'
header.aa = '19'
header.issueDate = '2020-01-01'
header.typ = '1.1'
header.currency = 'EUR'
header.purpose = '8'
header.setHeader()


payment = Payment()
payment.typ = '3'
payment.amount = '100'
payment.info = 'Μετρητά'
payment.setPayment()

ldt = par.InvData(
    lines=[
        par.LData('category1_1', 'E3_561_001', value=156, vatcat=1),
        par.LData('category1_1', 'E3_561_001', value=428, vatcat=1 ),
    ] ,
    per_invoice_taxes= [
        # par.TaxData(value=156, taxType=2, taxTypeCategory=9 , taxTypePrice=4.2),
        # par.TaxData(value=156, taxType=1, taxTypeCategory=1),
    ]
)

lines = Lines()
lines.setLines(ldt)

summary = Summary()
summary.setSummary(ldt)

xml = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
xmlstr = minidom.parseString(xml).toprettyxml(indent="   ")
# print(xmlstr)



ihd = InvoiceHead(afm=issuer.afm, date=header.issueDate, branch=issuer.branch, type=header.typ, series=header.series , aa=header.aa, cafm=counterpart.afm)


sendInvoice = SendInvoice()
sendInvoice.xml = xml

# res = sendInvoice.SendInvoices( ihd )
# l = sendInvoice._check_response(res)
# print(l)
#
Cance =  CancelInvoice(Mark='400001929239180')

print(Cance)