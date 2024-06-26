from invoiceData import  InvoiceParts as prt
from . import root, invoice
from typing import Optional


class InvHeader:
    series : str
    aa : str
    issueDate : str
    typ : str
    currency : str
    correlatedInvoices : Optional[str] =  None
    selfPricing : Optional[str] =  None
    dispatchDate : Optional[str] = ''
    dispatchTime : Optional[str] = ''
    vehicleNumber : Optional[str] = ''
    purpose : Optional[str] = ''
    prt = prt()

    def setHeader(self):
        self.prt.header(invoice, series=self.series, aa=self.aa, date=self.issueDate, typ=self.typ, currency=self.currency , correlatedInvoices=self.correlatedInvoices ,selfPricing=self.selfPricing ,  dispatchDate=self.dispatchDate, dispatchTime=self.dispatchTime, vehicleNumber=self.vehicleNumber, purpose=self.purpose)