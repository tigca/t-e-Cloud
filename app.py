import subprocess
import telebot
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent


# loggin
logging.basicConfig(level=logging.INFO)

# token from config.txt
with open('config.txt', 'r') as file:
    bot_token = file.read().strip()

# login
bot = telebot.TeleBot(bot_token)

# handler /start command


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton('🎛️ Аккаунт', callback_data='button1')
    button2 = InlineKeyboardButton('📖 FAQ', callback_data='button2')
    button3 = InlineKeyboardButton('🚫 Закрыть', callback_data='button3')
    keyboard.row(button1, button2)
    keyboard.row(button3)
    welcome_message = '<b>👋 Добро пожаловать в меню\n\n' \
                      '🐯 А тут, <a href="https://t.me/TriggerEarth">наш канал</a>\n' \
                      '🧑‍💻 И вот тут, <a href="https://t.me/trigger_chat">чат тех. поддержки</a>\n\n' \
                      '💚 Спасибо <a href="http://VIP_IPru_tw.t.me">VIP*</a>\n\n' \
                      '🤴 Версия бота: 0.1 [Beta] ⚡</b>'
    bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard, parse_mode='HTML',
                     disable_web_page_preview=True, reply_to_message_id=message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'button3')
def close_menu(call):
    # delete
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == 'button1':
        # button1
        bot.send_message(call.message.chat.id, 'soon...')
    elif call.data == 'button2':
        # button2
        bot.send_message(call.message.chat.id, 'soon...')
    elif call.data == 'button3':
        # button3
        bot.send_message(call.message.chat.id, 'soon...')


def safe_command(code: str) -> bool:
    files = ['bot.py', 'config.txt']

    for file in files:
        if file in code:
            return False

    return True


@bot.message_handler(commands=['t'])
def execute_command(message):
    command = message.text.split('/t', maxsplit=1)[1].strip()

    if not command:
        bot.reply_to(
            message, "☝️ Пустая команда, укажи команду для выполнения")
        return

    safe = safe_command(command)
    if command.startswith(("ls", "dir", "pwd", "git", "cat")) and safe:
        try:
            output = subprocess.check_output(
                command, shell=True, timeout=5, stderr=subprocess.STDOUT).decode('utf-8')
            response = f"⌨️ Команда: {command}\n\n✳️ Вывод:\n{output}"
            bot.reply_to(message, response)
        except subprocess.TimeoutExpired:
            bot.reply_to(
                message, "🥲 Превышено время ожидания выполнения команды")
        except subprocess.CalledProcessError as e:
            response = f"⌨️ Команда: {command}\n\n🚫 Ошибка:\n{e.output.decode('utf-8')}"
            bot.reply_to(message, response)
    else:
        bot.reply_to(message, "🚫 Команда не допустима")
        
@bot.inline_handler(func=lambda query: query.query.startswith('/t '))
def handle_inline_t_command(query):
    command = query.query[3:].strip()
    response = process_inline_command(command)
    bot.answer_inline_query(query.id, [InlineQueryResultArticle(id='1', title='Command result', input_message_content=InputTextMessageContent(response))])

def process_inline_command(command):
    safe = safe_command(command)
    if command.startswith(("ls", "dir", "pwd", "git", "cat")) and safe:
        try:
            output = subprocess.check_output(command, shell=True, timeout=5, stderr=subprocess.STDOUT).decode('utf-8')
            response = f"⌨️ Команда: {command}\n\n✳️ Вывод:\n{output}"
            return response
        except subprocess.TimeoutExpired:
            return "🥲 Превышено время ожидания выполнения команды"
        except subprocess.CalledProcessError as e:
            response = f"⌨️ Команда: {command}\n\n🚫 Ошибка:\n{e.output.decode('utf-8')}"
            return response
    else:
        return "🚫 Команда не допустима"

# start
if __name__ == "__main__":
    bot.polling()
