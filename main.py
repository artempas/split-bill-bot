from telebot import *
import secure

bot = TeleBot(secure.token)

@bot.message_handler(commands=['start'])
def start(msg):
    pass #TODO