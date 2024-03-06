import telebot
from telebot import types
from config import TOKEN
import time
from gpt import generate_response
import os
bot = telebot.TeleBot(TOKEN)
last_generated_response = {}
user_settings = {}
log_file_path = "C:/Users/User/PycharmProjects/pythonProject6/pythonProject/перевод/error_logs.txt"
user_messages_history = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = ("Привет! Я ИИ помощник. Задай мне вопрос, и я постараюсь на него ответить.\n\n"
                    "Также вы можете изменить количество токенов для ответов.")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [types.KeyboardButton(text) for text in ["Изменить количество токенов", "Продолжи", "Сбросить чат"]]
    markup.add(*buttons)
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

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
    except ValueError:
        msg = bot.reply_to(message, "Пожалуйста, введите корректное число.")
        bot.register_next_step_handler(msg, set_tokens)

@bot.message_handler(func=lambda message: message.text == "Продолжи")
def handle_continue(message):
    chat_id = message.chat.id
    if chat_id in last_generated_response and last_generated_response[chat_id]:
        modified_response = f"{last_generated_response[chat_id]} Продолжи"
        bot.send_message(chat_id, "Ожидайте ответа...")
        new_response = generate_response(modified_response, tokens=user_settings.get(chat_id, 200))
        last_generated_response[chat_id] = new_response
        bot.send_message(chat_id, new_response)
    else:
        bot.send_message(chat_id, "Нет последнего ответа для продолжения.")

@bot.message_handler(func=lambda message: message.text == "Сбросить чат")
def reset_chat_history(message):
    chat_id = message.chat.id
    if chat_id in last_generated_response:
        last_generated_response[chat_id] = ""
    bot.reply_to(message, "История чата сброшена. Начните новый диалог.🤗")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    wait_message = bot.send_message(chat_id, "Ожидайте ответа...")

    for i in range(1, 6):
        dot_count = i % 4
        time.sleep(2)
        bot.edit_message_text(chat_id=chat_id, message_id=wait_message.message_id,
                              text=f"Ожидайте ответа{'.' * dot_count}")

    response = generate_response(message.text, tokens=user_settings.get(chat_id, 200))
    bot.edit_message_text(chat_id=chat_id, message_id=wait_message.message_id, text=response)
    last_generated_response[chat_id] = response

if __name__ == '__main__':
    bot.infinity_polling()
