import hashlib
from dataclasses import dataclass
import parameters as par
from xml.etree.ElementTree import SubElement


@dataclass
class InvoiceHead:
    afm: str
    date: str  # isodate
    branch: str
    type: str
    series: str
    aa: str
    cafm: str  # Counterpart AFM

    @property
    def uid(self):
        val = f'{self.afm}-{self.date}-{self.branch}-{self.type}-{self.series}-{self.aa}'
        return hashlib.sha1(val.encode(encoding='ISO-8859-7')).hexdigest().upper()


class InvoiceParts:
    def issuer(self, parent, *, afm, country='GR', branch='0'):
        iss = SubElement(parent, "issuer")
        SubElement(iss, "vatNumber").text = afm
        SubElement(iss, "country").text = country
        SubElement(iss, "branch").text = branch
        return iss

    def counter_part(self, parent, *, afm, name='', country='GR', branch='0', street='', postalCode='', city=''):
        cpart = SubElement(parent, "counterpart")
        SubElement(cpart, "vatNumber").text = afm
        SubElement(cpart, "country").text = country
        SubElement(cpart, "branch").text = branch
        if country != 'GR' and name != '':  # οταν ειναι 1.2 η 1.3 ειναι υποχρεωτικό να υπάρχει το όνομα του συμβαλλόμενου
            SubElement(cpart, "name").text = name
        if street != '' and postalCode != '' and city != '':
            address = SubElement(cpart, "address")
            SubElement(address, "street").text = street
            SubElement(address, "postalCode").text = postalCode
            SubElement(address, "city").text = city
        return cpart

    def header(self, parent, *, series, aa, date, typ, currency='EUR', dispatchDate=None, dispatchTime=None,
               vehicleNumber=None, purpose=None):
        head = SubElement(parent, "invoiceHeader")
        SubElement(head, "series").text = series
        SubElement(head, "aa").text = aa
        SubElement(head, "issueDate").text = date
        SubElement(head, "invoiceType").text = typ
        SubElement(head, "currency").text = currency
        ####
        # exchangeRate εαν δεν ειναι EUR
        # correlatedInvoices
        # selfPricing
        ####correlatedInvoices
        if dispatchDate and dispatchTime and vehicleNumber and purpose:
            self.move_purpose(head, dispatchDate=dispatchDate, dispatchTime=dispatchTime, vehicleNumber=vehicleNumber,
                              purpose=purpose)
        ####
        # fuelInvoice
        ####
        return head

    def move_purpose(self, parent, *, dispatchDate, dispatchTime, vehicleNumber, purpose):
        SubElement(parent, "dispatchDate").text = dispatchDate
        SubElement(parent, "dispatchTime").text = dispatchTime
        SubElement(parent, "vehicleNumber").text = vehicleNumber
        SubElement(parent, "movePurpose").text = str(purpose)

    def payment(self, parent, *, typ, amount, info):
        paymeth = SubElement(parent, "paymentMethods")
        payd = SubElement(paymeth, "paymentMethodDetails")
        SubElement(payd, "type").text = typ
        SubElement(payd, "amount").text = f'{amount:.2f}'
        SubElement(payd, "paymentMethodInfo").text = info
        return payd

    def income_classification(self, parent, typ, category, amount):
        det_clas = SubElement(parent, "incomeClassification")
        SubElement(det_clas, "icls:classificationType").text = typ
        SubElement(det_clas, "icls:classificationCategory").text = category
        SubElement(det_clas, "icls:amount").text = f'{amount:.2f}'
        return det_clas

    def taxesTotals_perInvoice(self, parent, data: par.LData):
        # check if taxType is 0 in lines

        if data.per_invoice_taxes is not None:
            taxesTotals = SubElement(parent, "taxesTotals")
            for i, lin in enumerate(data.per_invoice_taxes):
                if lin.taxType != 0:
                    if int(lin.taxType) == 1:
                        taxAmount = lin.taxTypesWithheld
                    elif int(lin.taxType) == 2:
                        taxAmount = lin.taxTypesFees
                    elif int(lin.taxType) == 3:
                        taxAmount = lin.taxTypesOtherTaxes
                    elif int(lin.taxType) == 4:
                        taxAmount = lin.taxTypesStampDuty
                    else:
                        taxAmount = 0.00
                    taxes = SubElement(taxesTotals, "taxes")
                    SubElement(taxes, "taxType").text = str(lin.taxType)
                    SubElement(taxes, "taxCategory").text = str(lin.taxTypeCategory)
                    SubElement(taxes, "underlyingValue").text = str(lin.value)
                    SubElement(taxes, "taxAmount").text = str(taxAmount)

    def _details(self, parent, aa, line: par.LData):
        det = SubElement(parent, "invoiceDetails")
        SubElement(det, "lineNumber").text = str(aa)
        SubElement(det, "netValue").text = f'{line.value:.2f}'
        SubElement(det, "vatCategory").text = str(line.vatcat)
        SubElement(det, "vatAmount").text = f'{line.vat:.2f}'

        if int(line.taxType) == 1:
            SubElement(det, "withheldAmount").text = f'{line.taxTypesWithheld:.2f}'
            SubElement(det, "withheldPercentCategory").text = str(line.taxTypeCategory)
        elif int(line.taxType) == 2:
            SubElement(det, "feesAmount").text = f'{line.taxTypesFees:.2f}'
            SubElement(det, "feesPercentCategory").text = str(line.taxTypeCategory)
        elif int(line.taxType) == 3:  # 8.1 not accept it
            SubElement(det, "otherTaxesAmount").text = f'{line.taxTypesOtherTaxes:.2f}'
            SubElement(det, "otherTaxesPercentCategory").text = str(line.taxTypeCategory)
        elif int(line.taxType) == 4:
            SubElement(det, "stampDutyAmount").text = f'{line.taxTypesStampDuty:.2f}'
            SubElement(det, "stampDutyPercentCategory").text = str(line.taxTypeCategory)

        if line.vatcat == 7:  # προσθήκη κατηγορίας απαλλαγής ΦΠΑ για τις εξαιρέσεις
            SubElement(det, "vatExemptionCategory").text = f'{line.vatExc}'
        self.income_classification(det, line.ctype, line.ccat, line.value)
        return det

    def lines(self, parent, *, data: par.InvData):
        for i, lin in enumerate(data.lines):
            self._details(parent, i + 1, lin)

    def summary(self, parent, *, data: par.InvData):
        if data.per_invoice_taxes is not None and data.per_invoice_taxes != []:
            # σε επιπεδο παραστατικου
            self.taxesTotals_perInvoice(parent, data)
            totalWithheldAmount = data.total_withheld_per_invoice
            totalFeesAmount = data.total_fees_per_invoice
            totalStampDutyAmount = data.total_stampDuty_per_invoice
            totalOtherTaxesAmount = data.total_otherTaxes_per_invoice
            total_gross = data.total_gross_per_invoice
        else:
            # σε επιπεδο γραμμων
            totalWithheldAmount = data.total_withheld
            totalFeesAmount = data.total_fees
            totalStampDutyAmount = data.total_stampDuty
            totalOtherTaxesAmount = data.total_otherTaxes
            total_gross = data.total_gross

        isum = SubElement(parent, "invoiceSummary")
        SubElement(isum, "totalNetValue").text = f'{data.total_value:.2f}'
        SubElement(isum, "totalVatAmount").text = f'{data.total_vat:.2f}'
        SubElement(isum, "totalWithheldAmount").text = f'{totalWithheldAmount:.2f}'
        SubElement(isum, "totalFeesAmount").text = f'{totalFeesAmount:.2f}'
        SubElement(isum, "totalStampDutyAmount").text = f'{totalStampDutyAmount:.2f}'
        SubElement(isum, "totalOtherTaxesAmount").text = f'{totalOtherTaxesAmount:.2f}'
        SubElement(isum, "totalDeductionsAmount").text = '0.00'
        SubElement(isum, "totalGrossValue").text = f'{total_gross:.2f}'
        for cat_typ, val in data.total_per_cat.items():
            cat, typ = cat_typ
            self.income_classification(isum, typ, cat, val)
        return isum
