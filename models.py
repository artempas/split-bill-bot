from dataclasses import dataclass, field

import logging
from datetime import datetime

from telebot import types

formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'bot-from-{datetime.now().date()}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
)


@dataclass(eq=True, unsafe_hash=True)
class Product:
    name: str
    price: float
    quantity: float
    sum: float
    __persons: list[int] = field(default_factory=lambda: [])

    __is_ready = False

    @property
    def price_per_person(self) -> float:
        return round(self.price / len(self.__persons), 2)

    @classmethod
    def from_dict(cls, src_dict: dict, persons: list[int] = None):
        return cls(
            price=src_dict.get("price") / 100,
            name=src_dict.get("name"),
            quantity=src_dict.get("quantity"),
            __persons=persons or [],
            sum=src_dict.get('sum') / 100
        )

    def get_text(self, all_persons: list["Person"]):
        string = f'''
        <b>{self.name}</b>
        <u>{self.price}₽
        '''
        if self.quantity != 1:
            string += f"✕ {self.quantity} = {self.sum}₽"
        string += "</u>"
        if self.__persons:
            string += "Скидываются:\n"
            string += '\n'.join([all_persons[i].name for i in self.__persons])
            string += f'\n по <b>{self.price_per_person}₽</b>'

    def __str__(self):
        string = f'''
                <b>{self.name}</b>
                <u>{self.price}₽
                '''
        if self.quantity != 1:
            string += f"✕ {self.quantity} = {self.sum}₽"
        string += "</u>"
        if len(self.__persons) > 1:
            string += f"\nНа {len(self.__persons)}х <b>{self.price_per_person}</b>"

    def get_keyboard(self, all_persons):
        keyboard = types.InlineKeyboardMarkup()
        has_any = False
        if not self.__is_ready:
            for index, person in enumerate(all_persons):
                if person not in self.__persons:
                    keyboard.add(
                        types.InlineKeyboardButton(
                            text=f"⬜️ {person.name}",
                            callback_data=str(index)
                        )
                    )
                else:
                    has_any = True
                    keyboard.add(
                        types.InlineKeyboardButton(
                            text=f"✅ {person.name}",
                            callback_data=str(index)
                        )
                    )
            if has_any:
                keyboard.add(types.InlineKeyboardButton(
                    text="Готово",
                    callback_data="confirm"
                ))
        else:
            keyboard.add(types.InlineKeyboardButton(
                text="Изменить",
                callback_data="edit"
            ))

    def toggle_person(self, person_index: int, all_persons: list["Person"], product_id: int) -> bool:
        """
        If person is in list - deletes him. If it's not - adds.
        @param person_index:
        @param all_persons:
        @param product_id:
        @return: True if now person is in list, else false
        """
        if person_index in self.__persons:  # deleting person
            self.__remove_ppp_from_all(all_persons, product_id)
            self.__persons.remove(person_index)
            self.__add_ppp_to_all(all_persons, product_id)
            return False
        else:  # adding person
            self.__remove_ppp_from_all(all_persons, product_id)
            self.__persons.append(person_index)
            self.__add_ppp_to_all(all_persons, product_id)
            return True

    def __remove_ppp_from_all(self, all_persons: list["Person"], product_id: int):
        for index in self.__persons:
            all_persons[index].remove_product(product_id, self.price_per_person)

    def __add_ppp_to_all(self, all_persons: list["Person"], product_id: int):
        for index in self.__persons:
            all_persons[index].add_product(product_id, self.price_per_person)

    def toggle_product(self) -> bool:
        if self.__is_ready:
            self.__is_ready = False
            return True
        if self.__persons:
            self.__is_ready = True
            return True
        return False

    @property
    def is_ready(self):
        return self.__is_ready

    @property
    def persons(self):
        return self.__persons


@dataclass
class Person:
    name: str
    products: list[int] = field(default_factory=lambda: [])
    sum: float = 0

    def __post_init__(self):
        while self.name.startswith(' '):
            self.name = self.name[1::]
        self.name = self.name[::-1]
        while self.name.startswith(' '):
            self.name = self.name[1::]
        self.name = self.name[::-1].capitalize()

    def add_product(self, product_index: int, price_per_person: float) -> bool:
        if product_index not in self.products:
            self.products.append(product_index)
            self.sum += price_per_person
            return True
        else:
            return False

    def remove_product(self, product_index: int, price_per_person: float) -> bool:
        if product_index not in self.products:
            return False
        else:
            self.products.remove(product_index)
            self.sum -= price_per_person
            if self.sum < 0:
                raise Exception("Sum<0!")

    def get_report(self, verbose: bool, all_products: dict[int, Product], first_chunk_len=4096) -> list[str]:
        results=[]
        first=True
        result = f"<b>{self.name}</b>\n"
        if verbose:
            for i in self.products:
                if (len(result)+len('\n'+str(all_products[i]))>=4096 and not first) or (len(result)+len('\n'+str(all_products[i]))>=first_chunk_len and first):
                    results.append(result)
                    result=''
                result += '\n'+str(all_products[i])
        if len(result) + len(f"<b>ИТОГО: {self.sum}₽</b>") >= 4096:
            results.append(result)
            result = ''
        result += f"<b>ИТОГО: {self.sum}₽</b>"
        results.append(result)
        return results
