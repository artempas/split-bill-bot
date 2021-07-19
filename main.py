from telebot import *
import secure

bot = TeleBot(secure.token)

users = {}  # chat_id:qr+.users


@bot.message_handler(commands=['start'])
def start(msg):
    pass  # TODO написать приветствие


@bot.message_handler(commands=['help'])
def help(msg):
    pass  # TODO написать инструкцию


@bot.message_handler(commands=['new_list'])
def start_new(msg):
    pass  # todo основной процесс


@bot.message_handler(commands=['add_person'])
def add_person(msg):
    pass  # todo добавление чела


@bot.message_handler(commands=['remove_person'])
def remove_person(msg):
    pass


@bot.message_handler(commands=['admin'])
def admin(msg):
    pass
