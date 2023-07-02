import telebot
from telebot import types
from config import token, public_key, private_key, url_endpoin, hi, thank, bye, data, hru
from colorthief import ColorThief as ct
# from imagekitio import ImageKit
from rembg import remove
import webcolors
import os
import json
from PIL import Image
import easygui as eg

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'старт', 'начать', 'привет'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Палитра цветов")
    btn2 = types.KeyboardButton("Убрать фон")
    btn3 = types.KeyboardButton("Сохранённые характеристики")
    btn4 = types.KeyboardButton("Очистить историю")
    markup.add(btn1, btn2, btn3, btn4)

    bot.send_message(message.chat.id,
                     f"Привет, <b>{message.chat.first_name}</b>) Я помощник дизайнера)\n\nКак я могу тебе помочь?",
                     parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=["text"])
def main(message):
    global data
    gs_data(message)
    data[message.from_user.id]['flag'] = True
    base(message)
    if data[message.from_user.id]['flag']:
        bot.send_message(message.chat.id, "Так, я - ассистент дизайнера. Если ты хочешь поболтать, обратись к моей коллеге Алисе из Яндекса 🤨")

def base(message): #базовые ответы
    global data
    gs_data(message)
    data[message.from_user.id]['flag'] = True
    for word in hi:
        if word in message.text.strip().lower():
            start(message)
            data[message.from_user.id]['flag'] = False
            break
    if data[message.from_user.id]['flag'] and data[message.from_user.id]['photo'] != '' and ("палитр" in message.text.strip().lower() or "colors" in message.text.strip().lower() or "цвет" in message.text.strip().lower()):
        color_picker(message)
        data[message.from_user.id]['flag'] = False
    elif data[message.from_user.id]['flag'] and ("палитр" in message.text.strip().lower() or "colors" in message.text.strip().lower() or "цвет" in message.text.strip().lower()):
        bot.send_message(message.chat.id, "Сначала загрузи фотографию, которую хочешь разобрать на цвета. А потом можешь смело нажимать на кнопку 'Палитра цветов'")
        data[message.from_user.id]['flag'] = False
    elif data[message.from_user.id]['flag'] and ("save" in message.text.strip().lower() or "характерист" in message.text.strip().lower() or "сохр" in message.text.strip().lower()):
        history(message)
    elif data[message.from_user.id]['flag'] and ("clear" in message.text.strip().lower() or "чистит" in message.text.strip().lower() or "удалить" in message.text.strip().lower() or "delete" in message.text.strip().lower()):
        clear(message)
    elif data[message.from_user.id]['flag'] and ("фон" in message.text.strip().lower() or "remove" in message.text.strip().lower() or "убрать" in message.text.strip().lower() or "background" in message.text.strip().lower()):
        bg_remover(message)
    reply(message, thank, "Обращайся)😉")
    reply(message, bye, "До скорого)")
    reply(message, hru, "Отлично! Спасибо, что интересуешься)")

def gs_data(message): #обнуление базы для нового пользователя
    global data
    if message.from_user.id not in data:
        data[message.from_user.id] = {'colors': {}, 'flag': True, 'photo': ''}

def reply(message, mas, text): #ответ
    global data
    gs_data(message)
    if data[message.from_user.id]['flag']:
        for word in mas:
            if word in message.text.strip().lower():
                bot.send_message(message.chat.id, text)
                data[message.from_user.id]['flag'] = False
                break

def history(message): #сохранённые характеристики
    global data
    gs_data(message)
    data[message.from_user.id]['flag'] = True
    history = ''
    if data[message.from_user.id]['flag'] and data[message.from_user.id]['colors'] != {} and ("history" in message.text.strip().lower() or "характерист" in message.text.strip().lower() or "сохр" in message.text.strip().lower()):
        for key, value in data[message.from_user.id]['colors'].items():
            history += key + '\n'
            for el in value:
                history += el + '\n'
        bot.send_message(message.chat.id, history)
        with open('DB.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, sort_keys=False, ensure_ascii=False)
        data[message.from_user.id]['flag'] = False
    elif data[message.from_user.id]['flag'] and ("save" in message.text.strip().lower() or "характерист" in message.text.strip().lower() or "сохр" in message.text.strip().lower()):
        bot.send_message(message.chat.id, 'Нет данных. Для просмотра сохранённых характеристик нужно сначала обработать фото')
        data[message.from_user.id]['flag'] = False

def clear(message):
    global data
    gs_data(message)
    data[message.from_user.id]['flag'] = True
    if data[message.from_user.id]['flag'] and data[message.from_user.id]['colors'] != {} and ("clear" in message.text.strip().lower() or "чистит" in message.text.strip().lower() or "удалить" in message.text.strip().lower() or "delete" in message.text.strip().lower()):
        data[message.from_user.id]['colors'] = {}
        data[message.from_user.id]['photo'] = ''
        print(data)
        bot.send_message(message.chat.id, 'История палитр цветов очищена')
        data[message.from_user.id]['flag'] = False
    elif data[message.from_user.id]['flag'] and ("clear" in message.text.strip().lower() or "чистит" in message.text.strip().lower() or "удалить" in message.text.strip().lower() or "delete" in message.text.strip().lower()):
        bot.send_message(message.chat.id, 'История палитр цветов пуста')
        data[message.from_user.id]['flag'] = False

def bg_remover(message):
    try:
        global data
        gs_data(message)
        data[message.from_user.id]['flag'] = True
        if data[message.from_user.id]['flag'] and data[message.from_user.id]['photo'] != '' and ("фон" in message.text.strip().lower() or "remove" in message.text.strip().lower() or "убрать" in message.text.strip().lower() or "background" in message.text.strip().lower()):
            input_path = data[message.from_user.id]['photo']
            output_path = f"rembg/{data[message.from_user.id]['photo'].split('/')[2]}"
            # os.makedirs(os.path.dirname(output_path), exist_ok=True)
            bot.send_message(message.chat.id, "Обрабатываю фото...")
            with open(input_path, 'rb') as i:
                with open(output_path, 'wb') as o:
                    input = i.read()
                    output = remove(input)
                    o.write(output)
            bot.send_photo(message.chat.id, photo=open(output_path, 'rb'))
            data[message.from_user.id]['flag'] = False
        elif data[message.from_user.id]['flag'] and ("фон" in message.text.strip().lower() or "remove" in message.text.strip().lower() or "убрать" in message.text.strip().lower() or "background" in message.text.strip().lower()):
            bot.send_message(message.chat.id, "Сначала загрузи фотографию, которую хочешь обработать. А потом можешь смело нажимать на кнопку 'Убрать фон'")
            data[message.from_user.id]['flag'] = False
    except Exception as ex:
        bot.reply_to(message, ex)


@bot.message_handler(content_types=["photo"])
def image(message):
    try:
        gs_data(message)
        data[message.from_user.id]['flag'] = True
        data[message.from_user.id]['photo'] = ''
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'files/' + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        if src not in data[message.from_user.id]['colors']:
            data[message.from_user.id]['colors'][src] = []
        data[message.from_user.id]['photo'] = src
        msg = bot.send_message(message.chat.id, "Выбери, что ты хочешь сделать с фото")
        bot.register_next_step_handler(msg, color_picker)
    except Exception as ex:
        bot.reply_to(message, ex)

def color_picker(message):
    try:
        global data
        gs_data(message)
        data[message.from_user.id]['flag'] = True
        src = ''
        if "save" in message.text.strip().lower() or "характерист" in message.text.strip().lower() or "сохр" in message.text.strip().lower():
            history(message)
        elif data[message.from_user.id]['flag'] and ("clear" in message.text.strip().lower() or "чистит" in message.text.strip().lower() or "удалить" in message.text.strip().lower() or "delete" in message.text.strip().lower()):
            clear(message)
        elif data[message.from_user.id]['flag'] and ("фон" in message.text.strip().lower() or "remove" in message.text.strip().lower() or "убрать" in message.text.strip().lower() or "background" in message.text.strip().lower()):
            bg_remover(message)
        for key, value in data[message.from_user.id]['colors'].items():
            if value == []:
                src = key
                data[message.from_user.id]['flag'] = True
                break
            else:
                data[message.from_user.id]['flag'] = False
        if data[message.from_user.id]['flag'] and ("палитра" in message.text.strip().lower() or "colors" in message.text.strip().lower() or "цвета" in message.text.strip().lower()):
            bot.send_message(message.chat.id, "Ты отправил фото, содержащее цвета:")
            palette = ''
            color_palette = ct(src).get_palette(color_count=11, quality=11)
            for color in color_palette:
                palette += webcolors.rgb_to_hex(color) + "\n"
            bot.send_message(message.chat.id, palette)
            for el in palette.splitlines():
                data[message.from_user.id]['colors'][src].append(el)
                # bot.send_message(chat_id=update.message.chat_id, text=f"<a href='https://www.colorhexa.com/{el[1:]}.png'>{el}</a>",parse_mode=ParseMode.HTML)
            print(data)
            data[message.from_user.id]['flag'] = False
        elif "палитр" in message.text.strip().lower() or "colors" in message.text.strip().lower() or "цвет" in message.text.strip().lower():
            bot.send_message(message.chat.id, "Ты отправил фото, содержащее цвета:")
            palette = ''
            src = data[message.from_user.id]['photo']
            for color in data[message.from_user.id]['colors'][src]:
                palette += color + "\n"
            bot.send_message(message.chat.id, palette)
            print(data)
            data[message.from_user.id]['flag'] = False
    except Exception as ex:
        bot.reply_to(message, ex)


#[(116, 117, 118), (200, 145, 93), (21, 29, 20), (131, 165, 185), (67, 45, 27), (163, 199, 212)]

@bot.message_handler(content_types=["audio", "video", "document", "sticker", "voice", "poll"])
def get_strange_msg(message):
    bot.send_message(message.chat.id, "Очень круто, но я предпочитаю общаться обычными текстовыми сообщениями и картинками")


bot.polling(none_stop=True, interval=0) #отправка нон-стоп запросов на сервер
