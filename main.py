from os import getenv
from pyzbar.pyzbar import decode
import cv2
import requests.exceptions
from dotenv import load_dotenv
from telebot import *
from telebot.handler_backends import StatesGroup
from telebot.types import Message

import classes
import tools

load_dotenv()
state_storage = StatePickleStorage()

bot = TeleBot(getenv('TELETOKEN'), state_storage=state_storage)


class MyStates(StatesGroup):
    init = State()
    waiting_for_qr = State()
    waiting_for_persons = State()
    splitting = State()


@bot.message_handler(commands=['start'], state='*')
def start(msg: Message):
    bot.send_message(msg.chat.id, 'Здравствуйте, для начала работы используйте команду /new_list')
    bot.set_state(msg.from_user.id, MyStates.init, msg.chat.id)


@bot.message_handler(commands=['new_list'], state=MyStates.init)
def start_new(msg: Message):
    bot.send_message(msg.chat.id, 'Отправьте фото QR-кода с чека')
    bot.set_state(msg.from_user.id, MyStates.waiting_for_qr, msg.chat.id)


@bot.message_handler(content_types=['image'], state=MyStates.waiting_for_qr)
def scan_qr(msg: Message):
    file = bot.get_file(msg.photo[-1].file_id)
    file_url = f"https://api.telegram.org/file/bot{getenv('TELETOKEN')}/{file.file_path}"
    img=cv2.imread(file_url)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    qr_codes = decode(gray)
    regex=re.compile('^t=[0-9]+T[0-9]+&s=[0-9]*\.[0-9]+&fn=[0-9]+&i=[0-9]+&fp=[0-9]+&n=\d$')
    for qr_code in qr_codes:
        data = qr_code.data.decode("utf-8")
        if regex.match(data):
            break
    else:
        bot.send_message(msg.chat.id, "Ни одного QR не найдено :(")
        return
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as user_data:
        #TODO stopped here
        user_data['bill'] = tools.request_bill(data)

    bot.send_message(msg.chat.id, 'Отправьте список людей, разделяя имена запятыми')
    bot.register_next_step_handler(msg, persons_init)


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
