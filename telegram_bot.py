import telebot
from telebot import types
import threading
import time
from main import get_values

TOKEN = '7269388497:AAHfBGARHgsSHtLpkl3rM1FaS_TRhbYilq8'

bot = telebot.TeleBot(TOKEN)
action_handler = {}
user_state = {}

def form_message():
   temperature,humilidity,ppm,ec = get_values()
   if humilidity == -1:
       message ="Не удалось измерить температуру\nНе удалось измерить влажность\n"
   else:
       message = f"Температура {temperature} °C\nВлажности {humilidity} %\n"
   if ppm == -1:
       message += f"Не удалось измерить cодержаниe солей в жидкости и электропроводимость жидкости"
   else:
       message += f"Содержаниe твердых солей в жидкости в жидкости {ppm} ppm\nЭлектропроводность жидкости {ec} мкСм/см\n"
   return message

def set_interval(chat_id,sec):
    def func_wrapper():
        set_interval(chat_id, sec)
        bot.send_message(chat_id, form_message())
    t = threading.Timer(sec, func_wrapper)
    user_state[chat_id] = t
    t.start()
    return t

@bot.message_handler(commands = ['start'])
def url(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Узнать текущие значения")
    btn2 = types.KeyboardButton('Узнать значения с периодичностью')
    btn3 = types.KeyboardButton('Выключить периодичность')
    markup.add(btn1, btn2,btn3)
    bot.send_message(message.from_user.id, "Добро пожаловать! Я ваш бот для отслеживания состояния датчиков!", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    chat_id = message.from_user.id
    text = message.text
    if text == "выход":
        response = "Вы вышли из режима набора сообщений"
        del action_handler[chat_id]
        bot.send_message(chat_id, response)
        return
    if chat_id in action_handler:
        try:
            num = int(text)
            response = f"Установлен период {num} минут"
        except:
            response = f"не удалось определить время, попробуйте ещё раз"
            bot.send_message(chat_id, response)
            return
        del action_handler[chat_id]
        set_interval(chat_id,num*60)
        response += "\n" + form_message()
        bot.send_message(chat_id, response)
        return
    if text == "Узнать текущие значения":
        bot.send_message(chat_id, form_message())
    elif text == "Узнать значения с периодичностью":
        action_handler[chat_id] = "set_interval_values"
        response = 'Укажите периодичность значений в минутах, напишите "выход" , если вы передумали'
        bot.send_message(chat_id, response)
    elif text == "Выключить периодичность":
        timer = user_state[chat_id]
        timer.cancel()
        response = 'периодичная отправка выключена'
        try:
            pass
        except:
            response = 'Периодичная отправка не была включена'
        bot.send_message(chat_id, response)
    else:
        response = "Я пока не знаю такой команды"
        bot.send_message(chat_id, response)

bot.polling(none_stop=True, interval=0)
