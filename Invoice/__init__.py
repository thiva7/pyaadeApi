from .invoiceElement import invoice , root
import parameters as par
from . import issuer as isur
from . import counterPart
from . import invheader
from . import payment
from . import lines
from . import summary
from . import sendInvoice
from invoiceData import InvoiceHead

def issuer():
    issuer_ = isur.Issuer()
    return issuer_

def Counterpart():
    coumterpart = counterPart.Counterpart()
    return coumterpart

def Header_():
    header_ = invheader.InvHeader()
    return header_

def Payment():
    payment_ = payment.Payment()
    return payment_

def Lines():
    line = lines.Lines()
    return line

def Summary():
    summary_ = summary.Summary()
    return summary_

def SendInvoice():
    send = sendInvoice.SendInvoice()
    return send

