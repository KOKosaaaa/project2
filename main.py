import telebot
from telebot import types
import gpt
from config import TOKEN
import os
import time


user_messages_history = {}
user_settings = {}
bot = telebot.TeleBot(TOKEN)
log_file_path = "C:/Users/User/PycharmProjects/pythonProject6/pythonProject/перевод/error_logs.txt"
last_generated_response = ""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = ("Привет! Я помощник. Задай мне вопрос, и я постараюсь ответить в рифму.🤗\n\n"
                    "Так же можно изменить количество токинов")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Изменить количество токенов"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Изменить количество токенов")
def settings(message):
    msg = bot.send_message(message.chat.id, "Введите новое количество токенов:")
    bot.register_next_step_handler(msg, set_tokens)

def set_tokens(message):
    chat_id = message.chat.id
    try:
        tokens = int(message.text)
        user_settings[chat_id] = tokens
        bot.reply_to(message, f"Количество токенов установлено: {tokens}")
        bot.send_message(chat_id, "Теперь вы можете задать мне вопрос.")
    except ValueError:
        msg = bot.reply_to(message, "Пожалуйста, введите корректное число.")
        bot.register_next_step_handler(msg, set_tokens)

@bot.message_handler(commands=['debug'])
def send_debug_logs(message):
    allowed_users = ['KOKOS_uc']
    if message.from_user.username in allowed_users:
        if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 0:
            with open(log_file_path, "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "Файл логов пуст или не существует.")
    else:
        bot.reply_to(message, "У вас нет доступа к этой команде.")

@bot.message_handler(commands=['reset'])
def reset_chat_history(message):
    chat_id = message.chat.id
    user_messages_history[chat_id] = []
    bot.reply_to(message, "История чата очищена. Начните новый диалог.🤗")

def process_user_message(chat_id, text):
    global last_generated_response
    response = "Ответ ИИ на ваш запрос."
    last_generated_response = response
    bot.send_message(chat_id, "Ожидайте запроса ⏳")
    bot.send_message(chat_id, response)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    if chat_id not in user_messages_history:
        user_messages_history[chat_id] = []
    user_messages_history[chat_id].append(message.text)
    process_user_message(chat_id, message.text)

@bot.message_handler(func=lambda message: True)
def handle_non_text(message):
    bot.reply_to(message, "Простите, я могу обработать только текст.😓")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_messages_history:
        user_messages_history[chat_id] = []
    user_messages_history[chat_id].append(message.text)
    process_user_message(chat_id, message.text)


def process_user_message(chat_id, text):
    global last_generated_response
    messages_context = " ".join(user_messages_history[chat_id][-5:])
    tokens = user_settings.get(chat_id, 200)
    message = bot.send_message(chat_id, "Ожидайте запроса ⏳")
    time.sleep(1)
    last_generated_response = gpt.generate_response(messages_context, tokens=tokens)
    bot.edit_message_text(last_generated_response, chat_id, message.message_id)
    send_continuation_buttons(chat_id)

def send_continuation_buttons(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Перефразируй"), types.KeyboardButton("/reset"))
    bot.send_message(chat_id, "Хотите перефразировать ?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Перефразируй")
def handle_continue(message):
    chat_id = message.chat.id
    process_user_message(chat_id, last_generated_response)

if __name__ == '__main__':
    bot.infinity_polling()
