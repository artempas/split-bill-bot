import random
import traceback
from dataclasses import dataclass

import requests
from json import loads
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


@dataclass
class Product:
    persons: list[str]
    name: str
    price: float
    quantity: float
    sum: float
    rdy = False
    id: int
    message_id: int

    @property
    def price_per_person(self) -> float:
        return self.price/len(self.persons)




