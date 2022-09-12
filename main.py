import logging
from os import remove, path, getcwd

import requests.exceptions
from telebot import *

import classes
import qr_scanner
import secure

bot = TeleBot(secure.bot_token)

# users:list[classes.User] =[]
users = []


def get_user(chat_id: int):
    for i in range(len(users)):
        if users[i].chat_id == chat_id:
            return i
    bot.send_message(chat_id, 'Произошла ошибка, попробуйте начать процесс заново\n/new_list')
    return None


@bot.message_handler(commands=['start'])
def start(msg):
    print(msg.chat.id)
    bot.send_message(msg.chat.id, 'Здравствуйте, для начала работы используйте команду /new_list')


@bot.message_handler(commands=['help'])
def help(msg):
    pass  # TODO написать инструкцию


@bot.message_handler(commands=['new_list'])
def start_new(msg):
    for user in users:
        if msg.chat.id == user.chat_id:
            for prod in user.products:
                if prod.id != 0:
                    bot.edit_message_reply_markup(msg.chat.id, prod.id, reply_markup=None)
            users.remove(user)
    bot.send_message(msg.chat.id, 'Отправьте фото QR-кода с чека')
    bot.register_next_step_handler(msg, scan_qr)


def scan_qr(msg):  # TODO проверить что будет с callback_query
    if msg.photo is not None:
        response = requests.get(
            f"https://api.telegram.org/file/bot{secure.bot_token}/{bot.get_file(msg.photo[-1].file_id).file_path}")
        with open(f'{msg.photo[-1].file_id}.png', 'wb') as file:
            file.write(response.content)
        try:
            data = qr_scanner.data_from_qr(f'{msg.photo[-1].file_id}.png')
            print(data)
            if len(data) == 0:
                print('Additional qr recognition via api.qrserver.com')
                response = requests.post('http://api.qrserver.com/v1/read-qr-code/',
                                         files={'file': ('file.png', open(f'{msg.photo[-1].file_id}.png', 'rb'))})
                if response.json()[0]['symbol'][0]['error'] is None:
                    data = response.json()[0]['symbol']
                    print('Additional qr recognition via api.qrserver.com succesful')
                else:
                    print('Additional qr recognition via api.qrserver.com unsuccesful')
                    raise ValueError
            if len(data) > 1:
                raise AttributeError
            else:
                data = data[0]
                if type(data) is dict:
                    data = data['data']
                else:
                    data = data.data.decode('utf-8')

            if not qr_scanner.check_for_format(data):
                raise ValueError

        except AttributeError:
            bot.send_message(msg.chat.id, 'Более одного qr кода найдено, автоматическая проверка')
            found = False
            for qr in data:
                if qr.type == 'QRCODE':
                    if type(qr) is dict:
                        stringified = qr['data']
                    else:
                        stringified = qr.data.decode('utf-8')
                    if qr_scanner.check_for_format(stringified):
                        found = True
                        right_qr = stringified
                        break
            if not found:
                bot.send_message(msg.chat.id, 'QR кода нужного формата не найдено')  # TODO инструкция
            else:
                data = right_qr
                bot.send_message(msg.chat.id, 'QR найден,поиск чека')
        except ValueError as exc:
            traceback.print_exc()
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            keyboard.add(types.KeyboardButton("Да"))
            keyboard.add(types.KeyboardButton("Нет"))
            bot.send_message(msg.chat.id, 'QR код не найден, хотите ввести данные с него вручную?',
                             reply_markup=keyboard)  # TODO инструкция
            bot.register_next_step_handler(msg, manual_input_confirmation)
            return None
        print(data)
        bill = classes.request_bill(data)
        users.append(classes.User(msg.chat.id, bill, []))
        bot.send_message(msg.chat.id, 'Отправьте список людей, разделяя имена запятыми')
        remove(f'{msg.photo[-1].file_id}.png')
        bot.register_next_step_handler(msg, persons_init)

    else:
        if msg.text.startswith('/'):
            bot.send_message(msg.chat.id, 'Отмена')
            return None
        else:
            bot.send_message(msg.chat.id, 'Необходимо отправить фото, попробуйте ещё раз')
            bot.register_next_step_handler(msg, scan_qr)


def manual_input_confirmation(msg: types.Message):
    if msg.text == "Да":
        bot.send_message(msg.chat.id, "Введите текст с QR", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, manual_input)
    else:
        pass


def manual_input(msg: types.Message):
    if qr_scanner.check_for_format(msg.text):
        bill = classes.request_bill(msg.text)
        users.append(classes.User(msg.chat.id, bill, []))
        bot.send_message(msg.chat.id, 'Отправьте список людей, разделяя имена запятыми')
        bot.register_next_step_handler(msg, persons_init)
    else:
        bot.send_message(msg.chat.id, "Неправильный формат")


def persons_init(msg):
    person_index = get_user(msg.chat.id)
    if person_index is None:
        bot.send_message(msg.chat.id, 'Произошла ошибка, попробуйте начать процесс заново\n/new_list')
        return None
    persons = []
    for name in msg.text.split(','):
        while name.startswith(' '):
            name = name[1::]
        name = name[::-1]
        while name.startswith(' '):
            name = name[1::]
        name = name[::-1].capitalize()
        persons.append(name)
    persons = list(set(persons))
    users[person_index].persons = persons
    bot.send_message(msg.chat.id, 'Готово, вот список людей:\n' + '\n'.join([str(i).capitalize() for i in
                                                                             persons]) + '\nНапоминаем, что вы сможете добавить/удалить людей только сейчас с помощью /add_person и /remove_person')
    bot.send_message(msg.chat.id, 'Если вы готовы перейти к делению чека, просто нажмите /start_split')


@bot.message_handler(commands=['start_split'])
def start_split(msg):
    person_index = get_user(msg.chat.id)
    if person_index is None:
        bot.send_message(msg.chat.id, 'Произошла ошибка, попробуйте начать процесс заново\n/new_list')
        return None
    if len(users[person_index].persons) < 2:
        bot.send_message(msg.chat.id,
                         'Должно быть больше двух людей\n Добавить новых людей можно с помощью /add_person')
        return None
    for product in users[person_index].products:
        message = bot.send_message(msg.chat.id, product.print())
        product.id = message.message_id
        print(product)
        bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id,
                                      reply_markup=product_keyboard(users[person_index], product))


def product_keyboard(user: classes.User, product: classes.Product):
    ppl_row = []
    for i in range(len(user.persons)):
        if product[user.persons[i]]:
            ppl_row.append(
                types.InlineKeyboardButton(f'✔️{user.persons[i]}', callback_data=f'p&{product.id}&{i}'))
        else:
            ppl_row.append(
                types.InlineKeyboardButton(f'✖️{user.persons[i]}', callback_data=f'p&{product.id}&{i}'))
    return types.InlineKeyboardMarkup(
        [ppl_row, [types.InlineKeyboardButton('✅ Готово', callback_data=f'p&{product.id}&confirm')]])


@bot.callback_query_handler(func=lambda dat: dat.data.split('&')[0] == 'p')
def product_buttons(data):
    print(data.data)
    user_index = get_user(data.message.chat.id)
    if user_index is None:
        return None
    user = users[user_index]
    product = user[int(data.data.split('&')[1])]
    if data.data.split('&')[2] == 'confirm':
        if product.ready():
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('✏️ Изменить', callback_data=f'p&{product.id}&edit'))
            bot.edit_message_text(product.print(), data.message.chat.id, data.message.id)
            bot.edit_message_reply_markup(chat_id=data.message.chat.id, message_id=data.message.id,
                                          reply_markup=kb)
            bot.answer_callback_query(data.id, 'Сохранено')
            for prod in user.products:
                if not prod.rdy:
                    return
            ppl = {}
            for person in user.persons:
                ppl[person] = 0
            for prod in user.products:
                for person in prod.get_persons():
                    ppl[person] += prod.price_per_person
                bot.edit_message_reply_markup(data.message.chat.id, prod.id, reply_markup=None)
            txt = 'ИТОГ:\n'
            for person in ppl:
                txt += person + ' - ' + str(ppl[person]) + '₽\n'
            bot.send_message(data.message.chat.id, txt)
            users.remove(user)

        else:
            bot.answer_callback_query(data.id, 'Хотя бы один человек должен скинуться на продукт')

    elif data.data.split('&')[2].isdigit():
        buyer = user.persons[int(data.data.split('&')[2])]
        if product.change_person_state(buyer):
            bot.answer_callback_query(data.id, '✔️' + buyer)
        else:
            bot.answer_callback_query(data.id, '✖️' + buyer)
        kb = product_keyboard(user, product)
        bot.edit_message_reply_markup(chat_id=data.message.chat.id, message_id=data.message.id, reply_markup=kb)
    elif data.data.split('&')[2] == 'edit':
        product.rdy = False
        bot.edit_message_text(product.print(), data.message.chat.id, data.message.id)
        kb = product_keyboard(user, product)
        bot.edit_message_reply_markup(chat_id=data.message.chat.id, message_id=data.message.id, reply_markup=kb)


@bot.message_handler(commands=['add_person'])
def add_person(msg):
    user = get_user(msg.chat.id)
    if user is not None:
        bot.send_message(msg.chat.id, 'Введите имя:')
        bot.register_next_step_handler(msg, adding_person)
    else:
        bot.send_message(msg.chat.id, "Сначала нажмите на /new_list")


def adding_person(msg):
    user = get_user(msg.chat.id)
    while msg.text.startswith(' '):
        msg.text = msg.text[1::]
    msg.text = msg.text[::-1]
    while msg.text.startswith(' '):
        msg.text = msg.text[1::]
    msg.text = msg.text[::-1].capitalize()
    if msg.text not in users[user].persons:
        users[user].persons.append(msg.text)
        bot.send_message(msg.chat.id, f'{msg.text} добавлен(а) в список')

    else:
        bot.send_message(msg.chat.id, f'{msg.text} уже есть в списке')


@bot.message_handler(commands=['remove_person'])
def remove_person(msg):
    pass


@bot.message_handler(commands=['admin'])
def admin(msg):
    pass


if __name__ == '__main__':
    while True:
        try:
            bot.polling(non_stop=True)
        except requests.exceptions.ReadTimeout:
            time.sleep(5)
