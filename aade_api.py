import requests
import xml_parse as xmlp
from dataclasses import dataclass
from environs import Env

@dataclass
class AadeUser:
    env = Env()
    env.read_env()
    user , key = env.str('_USER'), env.str('_KEY')


def isodate2gr(isodate: str) -> str:
    yyy, mmm, ddd = isodate.split('-')
    return f'{ddd}/{mmm}/{yyy}'


class AadeApi:
    def __init__(self, dev=True, verify=False):
        if dev:
            self.url = 'https://mydataapidev.aade.gr'
        else:
            # αρχίζει το πάρτυ
            self.url = 'https://mydatapi.aade.gr/myDATA'
        self.verify = verify
        self.co = AadeUser()

    @property
    def _headers(self):
        return {
            'Content-Type': 'application/xml',
            'aade-user-id': self.co.user,
            'ocp-apim-subscription-key': self.co.key
        }

    def send_invoices(self, xml):
        url = f"{self.url}/SendInvoices"
        res = requests.post(url, headers=self._headers,
                            data=xml, verify=self.verify, timeout=10)
        return res.text

    def cancel_invoice(self, mark4canceling):
        url = f"{self.url}/CancelInvoice?mark={mark4canceling}"
        res = requests.post(url, headers=self._headers,
                            verify=self.verify, timeout=10)
        return res.text

    def send_income_classification(self):
        url = f"{self.url}/SendIncomeClassification"
        print(url)

    def send_expenses_classification(self):
        url = f"{self.url}/SendExpensesClassification"
        print(url)

    def request_docs(self, isoapo, isoeos) -> str:
        apo, eos = isodate2gr(isoapo), isodate2gr(isoeos)
        url = f"{self.url}/RequestDocs?mark=1&dateFrom={apo}&dateTo={eos}"
        res = requests.get(url, headers=self._headers,
                           verify=self.verify, timeout=10)
        return res.text

    def request_transmitted_docs(self, isoapo, isoeos) -> str:
        """Ελάχιστη τιμή mark: 1"""
        apo, eos = isodate2gr(isoapo), isodate2gr(isoeos)
        url = f"{self.url}/RequestTransmittedDocs?mark=1&dateFrom={apo}&dateTo={eos}"
        res = requests.get(url, headers=self._headers,
                           verify=self.verify, timeout=10)
        return res.text

    def request_my_income(self, isoapo, isoeos) -> str:
        apo, eos = isodate2gr(isoapo), isodate2gr(isoeos)
        url = f"{self.url}/RequestMyIncome?dateFrom={apo}&dateTo={eos}"
        res = requests.get(url, headers=self._headers,
                           verify=self.verify, timeout=10)
        return res.text

    def request_my_expenses(self, isoapo, isoeos):
        apo, eos = isodate2gr(isoapo), isodate2gr(isoeos)
        url = f"{self.url}/RequestMyExpenses?dateFrom={apo}&dateTo={eos}"
        res = requests.get(url, headers=self._headers,
                           verify=self.verify, timeout=10)
        return res.text

    def request_uids(self, isodate):
        xml = self.request_transmitted_docs(isodate, isodate)
        if xml.startswith('<?xml'):
            invoices = xmlp.parse_xml_invoices(xml)
            return [i['uid'] for i in invoices]
        else:
            # is json error response
            return []


def find_send_dublicates(api: AadeApi, apo: str, eos: str) -> dict[str, list]:
    xml = api.request_transmitted_docs(apo, eos)
    invoices = xmlp.parse_xml_invoices(xml)
    uid_mark: dict[str, list] = {}
    for inv in invoices:
        uid = inv['uid']
        uid_mark[uid] = uid_mark.get(uid, [])
        uid_mark[uid].append(inv['mark'])
    return uid_mark
