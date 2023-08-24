import subprocess
import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle,
    InputTextMessageContent, CallbackQuery, Message
)

import asyncio
from functools import wraps, partial

logging.basicConfig(level=logging.INFO)
with open('config.txt', 'r') as file:
    bot_token = file.read()

# login
bot = Bot(bot_token)
dp = Dispatcher(bot)

# handler /start command

def to_async(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run 

def safe_command(code: str) -> bool:
    files = ['bot.py', 'config.txt', 'Dockerfile']

    for file in files:
        if file in code:
            return False

    return True

@to_async
def run(command: str) -> str:
    try:
        return subprocess.check_output(
            command, shell=True, timeout=5, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.TimeoutExpired:
        return "🥲 Превышено время ожидания выполнения команды"
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8')

@to_async
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



@dp.message_handler(commands=['start'])
async def start(message: Message):
    keyboard = InlineKeyboardMarkup()

    account = InlineKeyboardButton('📖 Аккаунт', callback_data='account')
    faq = InlineKeyboardButton('📖 FAQ', callback_data='button2')

    close = InlineKeyboardButton('🚫 Закрыть', callback_data='button3')
    keyboard.row(faq, account)
    keyboard.row(close)

    welcome_message = '<b>👋 Добро пожаловать в меню\n\n' \
                      '🐯 А тут, <a href="https://t.me/TriggerEarth">наш канал</a>\n' \
                      '🧑‍💻 И вот тут, <a href="https://t.me/trigger_chat">чат тех. поддержки</a>\n\n' \
                      '💚 Спасибо <a href="http://VIP_IPru_tw.t.me">VIP*</a>\n\n' \
                      '🤴 Версия бота: 0.1 [Beta] ⚡</b>'
    await message.reply(
        welcome_message, 
        reply_markup=keyboard, 
        parse_mode='HTML',
        disable_web_page_preview=True
    )


@dp.callback_query_handler(lambda call: call.data == 'button3')
async def close_menu(call):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(call.id)

@dp.callback_query_handler(lambda call: call.data == 'account')
async def account_menu(call: CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('✈ Оплата', callback_data='money'),
        InlineKeyboardButton('🔷 Подключения', callback_data='connections'),
        InlineKeyboardButton('💵 Тарифы', callback_data='tarif')
    )
    keyboard.row(InlineKeyboardButton('☕ Поддержка', url='https://t.me/+8OUdVbortIw4MTQy'))

    await bot.edit_message_text(
        '<b>❇️ Передвигайся по кнопкам</b>',
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML'
    )
    await bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        call.inline_message_id,
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda _: True)
async def handle_button_click(call):
    if call.data == 'button1':
        # button1
        await bot.send_message(call.message.chat.id, 'soon...')
    elif call.data == 'button2':
        # button2
        await bot.send_message(call.message.chat.id, 'soon...')


@dp.message_handler(commands=['t'])
async def execute_command(message):
    command = message.text.split('/t', maxsplit=1)[1].strip()

    if not command:
        await message.reply("☝️ Пустая команда, укажи команду для выполнения")
        return

    safe = safe_command(command)
    if command.startswith(("ls", "dir", "pwd", "git", "cat")) and safe:
        output = await run(command)
        response = f"⌨️ Команда: {command}\n\n✳️ Вывод:\n{output}"
        await message.reply(response)
    else:
        await message.reply("🚫 Команда не допустима")
        
@dp.inline_handler(lambda query: query.query.startswith('/t '))
async def handle_inline_t_command(query):
    command = query.query[3:].strip()
    response = await process_inline_command(command)
    await bot.answer_inline_query(
        query.id,
        [
            InlineQueryResultArticle(
                id='1', 
                title='Command result', 
                input_message_content=InputTextMessageContent(response)
            )
        ]
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=print('Started'))
