from dataclasses import dataclass, field

import logging
from datetime import datetime

from telebot import types


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
        return round(self.sum / len(self.__persons), 2)

    @classmethod
    def from_dict(cls, src_dict: dict):
        return cls(
            price=src_dict.get("price") / 100,
            name=src_dict.get("name"),
            quantity=src_dict.get("quantity"),
            sum=src_dict.get("sum") / 100,
        )

    def get_text(self, all_persons: list["Person"]) -> str:
        string = f"""
        <b>{self.name}</b>
<u>{self.price}₽"""
        if self.quantity != 1:
            string += f"✕ {self.quantity} = {self.sum}₽"
        string += "</u>"
        if self.__persons:
            string += "\nСкидываются:\n"
            string += "\n".join([all_persons[i].name for i in self.__persons])
            string += f"\nпо <b>{self.price_per_person}₽</b>"
        return string

    def __str__(self):
        string = f"<code>{self.name}</code>" \
                 f"\n<u>{self.price}₽"
        if self.quantity != 1:
            string += f"✕ {self.quantity} = {self.sum}₽"
        string += "</u>"
        if len(self.__persons) > 1:
            string += f" На {len(self.__persons)}х <b>{self.price_per_person}</b>"
        return string

    def get_keyboard(self, all_persons):
        keyboard = types.InlineKeyboardMarkup()
        has_any = False
        if not self.__is_ready:
            for index, person in enumerate(all_persons):
                print(self.__persons)
                if index not in self.__persons:
                    keyboard.add(
                        types.InlineKeyboardButton(
                            text=f"⬜️ {person.name}", callback_data=str(index)
                        )
                    )
                else:
                    has_any = True
                    keyboard.add(
                        types.InlineKeyboardButton(
                            text=f"✅ {person.name}", callback_data=str(index)
                        )
                    )
            if has_any:
                keyboard.add(
                    types.InlineKeyboardButton(text="Готово", callback_data="confirm")
                )
        else:
            keyboard.add(
                types.InlineKeyboardButton(text="Изменить", callback_data="edit")
            )
        return keyboard

    def toggle_person(self, person_index: int) -> bool:
        """
        If person is in list - deletes him. If it's not - adds.
        @param person_index:
        @param all_persons:
        @param product_id:
        @return: True if now person is in list, else false
        """
        if person_index in self.__persons:  # deleting person
            self.__persons.remove(person_index)
            return False
        else:  # adding person
            self.__persons.append(person_index)
            return True

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

    def toJSON(self):
        return {
            "name":self.name,
            "persons": self.__persons,
            "price":self.price,
            "quantity": self.quantity,
            "sum": self.sum,
            "is_ready": self.__is_ready
        }


@dataclass
class Person:
    name: str
    products: list[int] = field(default_factory=lambda: [])

    def __post_init__(self):
        while self.name.startswith(" "):
            self.name = self.name[1::]
        self.name = self.name[::-1]
        while self.name.startswith(" "):
            self.name = self.name[1::]
        self.name = self.name[::-1].capitalize()

    def add_product(self, product_index: int) -> bool:
        if product_index not in self.products:
            self.products.append(product_index)
            return True
        else:
            return False

    def sum(self, all_products: dict[int, Product]):
        return sum([all_products[i].price_per_person for i in self.products])

    def remove_product(self, product_index: int) -> bool:
        if product_index not in self.products:
            return False
        else:
            self.products.remove(product_index)

    def get_report(
        self, verbose: bool, all_products: dict[int, Product], first_chunk_len=4096
    ) -> list[str]:
        results = []
        first = True
        result = f"{self.name}\n"
        if verbose:
            for i in self.products:
                if (
                    len(result) + len("\n" + str(all_products[i])) >= 4096 and not first
                ) or (
                    len(result) + len("\n" + str(all_products[i])) >= first_chunk_len
                    and first
                ):
                    results.append(result)
                    result = ""
                result += "\n" + str(all_products[i])
        if len(result) + len(f" <b>ИТОГО: {self.sum(all_products)}₽</b>") >= 4096:
            results.append(result)
            result = ""
        result += (f"\n<b>ИТОГО:" if verbose else "")+f" {self.sum(all_products).__round__(2)}₽"+("</b>" if verbose else "")+'\n'
        results.append(result)
        return results
    def toJSON(self):
        return {
            "name":self.name,
            "products":self.products
        }
