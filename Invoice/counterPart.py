from invoiceData import  InvoiceParts as prt
from . import root, invoice
from typing import Optional


class Counterpart:
    afm : str
    country : str
    branch : str
    name: Optional[str] = ''
    street: Optional[str] = ''
    postalCode: Optional[str] = ''
    city: Optional[str] = ''
    prt = prt()

    def setCounterpart(self):
        self.prt.counter_part(invoice, afm=self.afm, country=self.country, branch=self.branch, name=self.name, street=self.street, postalCode=self.postalCode, city=self.city)