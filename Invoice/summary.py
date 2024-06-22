from invoiceData import  InvoiceParts as prt
from . import root, invoice

class Summary:
    prt = prt()

    def setSummary(self , data):
        self.prt.summary(invoice, data=data)