from invoiceData import  InvoiceParts as prt
from . import root, invoice

class Payment:
    typ: str
    amount: float
    info: str
    prt = prt()

    def setPayment(self):
        self.prt.payment(invoice, typ=self.typ, amount=float(self.amount), info=self.info)
