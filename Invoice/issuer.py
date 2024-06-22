from invoiceData import  InvoiceParts as prt
from . import root, invoice
from typing import Optional
class Issuer:
    afm : str
    country : str
    branch : str
    prt = prt()

    def setIssuer(self):
        self.prt.issuer(invoice, afm=self.afm, country=self.country, branch=self.branch )