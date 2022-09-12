import random
import traceback
import requests
from json import loads
from secure import check_token, check_token_reserve
import logging
from datetime import datetime

formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'bot-from-{datetime.now().date()}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
)


class Product:
    __persons: list = []
    name = ""
    price = 0.0
    price_per_person = 0.0
    quantity = 0.0
    sum = 0.0
    rdy = False
    id = 0
    message_id = 0

    def __init__(self, name: str, price: float, quantity: float, usernames=None):
        if usernames is None:
            usernames = []
        self.name = name
        self.price = price
        self.quantity = quantity
        self.sum = round(self.price * self.quantity, 2)
        self.__persons = usernames
        self.rdy = False
        if len(usernames) != 0:
            self.price_per_person = price / len(usernames)
        else:
            self.price_per_person = 0

    def __str__(self):
        return f"{self.name} : {self.id}"

    def __getitem__(self, item):
        return item in self.__persons

    def print(self):
        txt = f'{self.name}\n{(self.quantity != 1) * (str(self.price) + "*" + str(self.quantity) + "=")}{self.sum}₽'
        if self.rdy:
            txt += '\nСкидываются: ' + ' '.join(self.__persons) + ' по ' + str(self.price_per_person) + '₽'
        return txt

    def get_persons(self):
        return self.__persons

    def ready(self):
        if len(self.__persons) > 0:
            self.rdy = True
            self.price_per_person = self.sum / len(self.__persons)
            return True
        else:
            return False

    def change_person_state(self, person):

        if person in self.__persons:
            while person in self.__persons:
                self.__persons.remove(person)
            return False
        else:
            self.__persons.append(person)
            return True


class User:
    chat_id = None  # msg.__chat
    __bill_data = None  # data from bill
    persons = list()  # tuple of __persons
    products = list()  # tuple of Products

    def __init__(self, chat, bill_data, persons: iter):
        self.chat_id = chat
        self.__bill_data = bill_data
        self.persons = persons
        prods = []
        for prod in bill_data['items']:
            prods.append(Product(prod['name'], prod['price'] / 100, prod['quantity']))
        self.products = tuple(prods)

    def __str__(self):
        logging.log(logging.INFO, f'CHAT_INFO: {self.chat_id}'
                                  f'PERSONS: {self.persons}\n'
                                  f'BILL: {self.__bill_data}')

    def __getitem__(self, item):
        for product in self.products:
            if product.id == item:
                return product
        return None

    def get_bill_data(self):
        return self.__bill_data

    def set_bill_data(self, bill_data):
        self.__bill_data = bill_data
        prods = []
        for prod in bill_data['items']:
            prods.append(Product(prod['name'], prod['price'] / 100, prod['quantity']))
        self.products = tuple(prods)

    def get_persons(self):
        return self.persons

    def set_persons(self, persons):
        self.persons = persons


def request_bill(qrraw: str):
    post = {}
    for i in qrraw.split('&'):
        post[i.split('=')[0]] = i.split('=')[1]
    post['token'] = check_token
    post['qr'] = 0
    ans = requests.post('https://proverkacheka.com/api/v1/check/get', post)
    logging.log(logging.INFO, ans)
    logging.log(logging.INFO, ans.text.encode())
    try:
        ans = loads(ans.text)['data']['json']
    except TypeError:
        try:
            logging.log(logging.INFO, 'Using reserve token')
            post['token'] = check_token_reserve
            ans = requests.post('https://proverkacheka.com/api/v1/check/get', post)
            ans = loads(ans.text)['data']['json']
        except TypeError:
            logging.log(logging.INFO, loads(ans.text))
            raise TypeError(loads(ans.text))
    logging.log(logging.INFO, ans)
    return ans
