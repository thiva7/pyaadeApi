from Invoice import *

cancel = CancelInvoice('1234567890')
print(cancel)

###################
# Με ΑΦΜ οντότητας
###################

cancel = CancelInvoice('1234567890' , entityVatNumber='1234567890')
print(cancel)