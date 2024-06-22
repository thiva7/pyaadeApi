from invoiceData import  InvoiceParts as prt
from . import root, invoice

class Lines:
    prt = prt()

    def setLines(self , data):
        self.prt.lines(invoice, data=data)