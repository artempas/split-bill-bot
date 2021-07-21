import traceback


class Product:
    __usernames = []
    __name = ""
    __price = 0.0
    __price_per_person = 0.0

    def __init__(self, usernames:iter, name:str, price:float):
        self.__usernames=usernames
        self.__name=name
        self.__price=price
        self.__price_per_person=price/len(usernames)

    def __str__(self):
        return f"{self.__name} : {self.__price}"

#__________Get methods__________

    def get_people(self):
        return self.__usernames

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_price_per_person(self):
        return self.__price_per_person

#__________Set methods__________

    def add_people(self, name):
        if name not in self.__usernames:
            self.__usernames.append(name)
            return True
            #return f"Пользователь {name} успешо добавлен"
        else:
            return False
            #return f"Такое имя пользователя уже существует"

    def delete_people(self, name):
        if name in self.__usernames:
            self.__usernames.remove(name)
            self.__price_per_person = self.__price / len(self.__usernames)

            #return f"Пользователь {name} успешно удален"
            return True
        else:
            #return f"Такого пользователя нет в списке"
            return False


    def set_name(self, name):
        try:
            self.__name = name
            return True
        except BaseException:
            print(traceback.format_exc())
            return False

    def set_price(self, price):
        try:
            self.__price = price
            self.__price_per_person = self.__price / len(self.__usernames)
            return True
        except BaseException:
            print(traceback.format_exc())
            return False


class User:
    __chat = None # msg.__chat
    __bill_data = None # data from bill
    __persons = tuple() # tuple of __persons

    def __init__(self, chat, bill_data, persons:iter):
        self.__chat=chat
        self.__bill_data = bill_data
        self.__persons = persons

    def __str__(self):
        print(f'CHAT_INFO: {self.__chat.id=}|{self.__chat.username=}\n'
              f'PERSONS: {self.__persons}\n'
              f'BILL: {self.__bill_data}')
    def get_bill(self):
        return