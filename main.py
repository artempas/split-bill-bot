from telebot import *
import secure
import qr_scanner
from os import remove

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
    bot.send_message(msg.__chat.id, 'Отправьте фото QR-кода с чека')
    bot.register_next_step_handler(msg,scan_qr)


def scan_qr(msg): #TODO проверить что будет с callback_query
    if msg.photo is not None:
            bytes = bot.download_file(bot.get_file(msg.photo[-1].file_id).file_path)
            with open(f'{msg.photo[-1].file_id}.jpg','wb') as file:
                file.write(bytes)
            try:
                data = qr_scanner.data_from_qr(f'{msg.photo[-1].file_id}.jpg')
                remove(f'{msg.photo[-1].file_id}.jpg')
                if len(data)>1:
                    raise AttributeError
            except AttributeError:
                bot.send_message(msg.__chat.id, 'Более одного qr кода найдено, автоматическая проверка')
                found=False
                for qr in data:
                    if found:
                        break
                    if qr.type == 'QRCODE':
                        if qr_scanner.check_for_format(qr):
                            found=True
                            right_qr = qr
                if not found:
                    bot.send_message(msg.__chat.id, 'QR кода нужного формата не найдено') #TODO инструкция
            except ValueError:
                    bot.send_message(msg.__chat.id, 'QR кода нужного формата не найдено') #TODO инструкция
    else:
        if msg.text.startswith('/') :
            bot.send_message(msg.__chat.id, 'Отмена')
            return None
        else:
            bot.send_message(msg.__chat.id, 'Необходимо отправить фото, попробуйте ещё раз')
            bot.register_next_step_handler(msg,scan_qr)

@bot.message_handler(commands=['add_person'])
def add_person(msg):
    pass  # todo добавление чела


@bot.message_handler(commands=['remove_person'])
def remove_person(msg):
    pass


@bot.message_handler(commands=['admin'])
def admin(msg):
    pass
