from os import getenv
from time import sleep
import telebot.apihelper
from telebot import *
from telebot.handler_backends import StatesGroup
from telebot.types import Message, CallbackQuery
from telebot.util import quick_markup
from models import Product, Person
import tools

state_storage = StatePickleStorage()
FILE_URL = f"https://api.telegram.org/file/bot{getenv('TELETOKEN')}/" + "{file_path}"
bot = TeleBot(getenv("TELETOKEN"), state_storage=state_storage)


class MyStates(StatesGroup):
    init = State()
    waiting_for_qr = State()
    waiting_for_persons = State()
    splitting = State()
    report_settings = State()


@bot.message_handler(commands=["start"])
def start(msg: Message):
    bot.send_message(
        msg.chat.id, "Здравствуйте, для начала работы используйте команду /new_list"
    )
    bot.set_state(msg.from_user.id, MyStates.init, msg.chat.id)
    print(bot.get_state(msg.from_user.id, msg.chat.id))


@bot.message_handler(commands=["new_list"], state=MyStates.init)
def start_new(msg: Message):
    bot.send_message(msg.chat.id, "Отправьте фото QR-кода с чека")
    bot.set_state(msg.from_user.id, MyStates.waiting_for_qr, msg.chat.id)


@bot.message_handler(content_types=["photo"], state=MyStates.waiting_for_qr)
def scan_qr(msg: Message):
    file = bot.get_file(msg.photo[-1].file_id)
    try:
        url="https://"+getenv('host')+"/images/{file_path}"
        bill = tools.request_bill(url.format(file_path=file.file_path))
    except ValueError as e:
        bot.send_message(msg.chat.id, "Не получилось получить информацию о чеке")
        return
    products = [Product.from_dict(i) for i in bill]
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as user_data:
        user_data["Products"] = products
    bot.send_message(
        msg.chat.id,
        "Данные с чека получены.\n"
        "Отправьте мне через запятую список людей, которые будут скидываться\n"
        "Например: <tg-spoiler>Саша, Маша, Райан Гослинг, Алексей</tg-spoiler>",
        parse_mode="HTML",
    )
    bot.set_state(msg.from_user.id, MyStates.waiting_for_persons, msg.chat.id)


@bot.message_handler(content_types=["text"], state=MyStates.waiting_for_persons)
def persons_init(msg: Message):
    persons = []
    for name in msg.text.split(","):
        persons.append(Person(name))
    if len(persons) < 2:
        bot.send_message(msg.chat.id, "В списке должно быть не менее двух человек")
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as user_data:
        user_data["Persons"] = persons
    kb = quick_markup(
        {"Ок": {"callback_data": "ok"}, "Изменить": {"callback_data": "edit"}}
    )
    bot.send_message(
        msg.chat.id,
        "Готово, вот список людей:\n" + "\n".join([i.name for i in persons]),
        reply_markup=kb,
    )


@bot.callback_query_handler(func=lambda x: True, state=MyStates.waiting_for_persons)
def persons_confirm(call: CallbackQuery):
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=types.ReplyKeyboardRemove(),
    )
    if call.data == "ok":
        bot.set_state(call.from_user.id, MyStates.splitting, call.message.chat.id)
        start_split(call)
    else:
        bot.send_message(
            call.message.chat.id,
            "Отправьте мне через запятую список людей, которые будут скидываться\n"
            "Например: <tg-spoiler>Саша, Маша, Райан Гослинг, Алексей</tg-spoiler>",
            parse_mode="HTML",
        )


def start_split(call: CallbackQuery):
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as user_data:
        products: list[Product] = user_data["Products"]
        persons: list[Person] = user_data["Persons"]
    messages = {}
    for index, product in enumerate(products):
        try:
            messages[
                bot.send_message(
                    call.message.chat.id,
                    product.get_text(persons),
                    reply_markup=product.get_keyboard(persons),
                )
            ] = product
        except telebot.apihelper.ApiTelegramException:
            sleep(0.5)
            messages[
                bot.send_message(
                    call.message.chat.id,
                    product.get_text(persons),
                    reply_markup=product.get_keyboard(persons),
                )
            ] = product
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as user_data:
        user_data["Messages"] = messages
        del user_data["Products"]
        user_data["Ready"] = 0
    bot.set_state(call.from_user.id, MyStates.splitting, call.message.chat.id)


@bot.callback_query_handler(
    func=lambda data: data.data.isdigit(), state=MyStates.splitting
)
def toggle_person(data: CallbackQuery):
    with bot.retrieve_data(data.from_user.id, data.message.chat.id) as user_data:
        product: Product = user_data["Messages"][data.message.message_id]
        is_present = product.toggle_person(int(data.data))
        if is_present:
            user_data["Persons"][int(data.data)].add_product(data.message.message_id)
        else:
            user_data["Persons"][int(data.data)].remove_product(data.message.message_id)
        user_data["Messages"][data.message.message_id] = product
        text = product.get_text(user_data["Persons"])
        kb = product.get_keyboard(user_data["Persons"])
    bot.edit_message_text(
        chat_id=data.message.chat.id,
        message_id=data.message.id,
        text=text,
        reply_markup=kb,
    )


@bot.callback_query_handler(
    func=lambda data: not data.data.isdigit(), state=MyStates.splitting
)
def toggle_product(data: CallbackQuery):
    with bot.retrieve_data(data.from_user.id, data.message.chat.id) as user_data:
        product: Product = user_data["Messages"][data.message.message_id]
        if product.toggle_product():
            if product.is_ready:
                bot.answer_callback_query(data.id, "Готово")
                user_data["Ready"] += 1
            else:
                bot.answer_callback_query(data.id, "Изменение")
                user_data["Ready"] -= 1
        else:
            bot.answer_callback_query(data.id, "Скинуться должен хотя бы один")
            return
        bot.edit_message_text(
            product.get_text(user_data["Persons"]),
            data.message.chat.id,
            data.message.message_id,
            reply_markup=product.get_keyboard(user_data["Persons"]),
        )
        user_data["verbose"] = user_data.get("verbose") or False
        user_data["separate"] = (
            user_data.get("separate") if user_data.get("separate") is not None else True
        )
        if user_data["ready"] == len(user_data["Messages"]):
            for message in user_data["Mesages"]:
                bot.edit_message_reply_markup(
                    data.message.chat.id,
                    message,
                    reply_markup=types.ReplyKeyboardRemove(),
                )
            kb = types.ReplyKeyboardMarkup()
            kb.add(
                [
                    types.InlineKeyboardButton(
                        f"Подробный {'✅' if user_data.get('verbose') else '❎'}"
                    ),
                    types.InlineKeyboardButton(
                        f"Отдельными сообщениями {'✅' if user_data.get('separate') else '❎'}"
                    ),
                ]
            )
            kb.add([types.InlineKeyboardButton("Получить")])
            bot.set_state(
                data.from_user.id, MyStates.report_settings, data.message.chat.id
            )
            bot.send_message(
                data.message.chat.id,
                "В каком виде хотите получить отчёт?",
                reply_markup=kb,
            )


@bot.message_handler(
    content_types=["text"], regexp="^Получить&", state=MyStates.report_settings
)
def send_report(msg: Message):
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as user_data:
        if user_data["separate"]:
            for user in user_data["Persons"]:
                report = user.get_report(verbose=user_data["verbose"])
                for text in report:
                    try:
                        bot.send_message(msg.chat.id, text, parse_mode="HTML")
                    except telebot.apihelper.ApiTelegramException:
                        sleep(0.5)
                        bot.send_message(msg.chat.id, text, parse_mode="HTML")
        else:
            first_chunk_len = 4096
            chunks = []
            for user in user_data["Persons"]:
                report = user.get_report(
                    verbose=user_data["verbose"], first_chunk_len=first_chunk_len
                )
                if chunks:
                    if len(chunks[-1] + report[0]) < 4096:
                        chunks[-1] += report.pop(0)
                chunks += report
                first_chunk_len = 4096 - len(chunks[-1])
            for text in chunks:
                bot.send_message(msg.chat.id, text, parse_mode="HTML")
    bot.set_state(msg.from_user.id, MyStates.init, msg.chat.id)
    bot.send_message(
        msg.chat.id, "Чтобы разделить ещё один счёт отправьте мне команду /new_list"
    )


@bot.message_handler(content_types=["text"], state=MyStates.report_settings)
def report_settings(msg: Message):
    with bot.retrieve_data(msg.from_user.id, msg.chat.id) as user_data:
        if "Подробный" in msg.text:
            user_data["verbose"] = not user_data["verbose"]
        elif "Отдельными сообщениями" in msg.text:
            user_data["separate"] = not user_data["separate"]
        else:
            bot.send_message(msg.chat.id, "Отвечайте нажатиями на кнопки")
        kb = types.ReplyKeyboardMarkup()
        kb.add(
            [
                types.InlineKeyboardButton(
                    f"Подробный {'✅' if user_data.get('verbose') else '❎'}"
                ),
                types.InlineKeyboardButton(
                    f"Отдельными сообщениями {'✅' if user_data.get('separate') else '❎'}"
                ),
            ]
        )
        kb.add([types.InlineKeyboardButton("Получить")])
        bot.send_message(msg.chat.id, "Настройки отчёта", reply_markup=kb)


if __name__ == "__main__":
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.polling(non_stop=True)
