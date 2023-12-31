import subprocess
import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle,
    InputTextMessageContent, CallbackQuery, Message
)

import asyncio
from functools import wraps, partial
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorClient

from utils import database

logging.basicConfig(level=logging.INFO)
with open('config.txt', 'r') as file:
    bot_token = file.read()

bot = Bot(bot_token)
dp = Dispatcher(bot)
users = {}

url = 'mongodb+srv://triggercloudbot:6PXxLZUwEQ0eS72O@cluster0.www1qqg.mongodb.net/?retryWrites=true&w=majority'
db = database(AsyncIOMotorClient(url).db.cloud)

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
def check(cmd: str):
    return subprocess.check_output(cmd, shell=True).decode()

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

async def buymb(user_id: int, mb) -> bool:
    try:
        if not (user := await db.find(user_id)):
            await db.insert({
                '_id': user_id,
                'users': [],
                'total': mb,
                'used': 0
            })
            
            return True
        else:
            user = await db.find(user_id)
            total = user['total']

            await db.edit(user_id, 'total', total+mb)

            return True
    except Exception as error:
        print(error)

        return False

@dp.message_handler(commands=['createuser'])
async def createuser(message: Message):
    name = message.get_args()
    if not name:
        return await message.reply('Укажите ник')
    
    name = name.split()[0]

    if len(name) < 4 or len(name) > 20:
        return await message.reply('❌ Длина ника должна быть больше 4 и меньше 20')

    users = await db.find(message.from_user.id)
    is_copy = await db.db.find_one({'user': name})

    if users:
        if users['user']:
            return await message.reply('❌ Нельзя создавать больше 1 сервера')
        elif is_copy:
            return await message.reply('❌ Сервер с таким названием уже существует')
        
    await db.edit(message.from_user.id, 'user', name)
    await message.reply(f'✔ Вы создали сервер, <b>{name}</b>', parse_mode='HTML')

@dp.message_handler(commands=['buymb'])
async def custombuyhandler(message: Message):
    global users

    if users.get(message.from_user.id, False):
        tobuy = None

        try:
            tobuy = int(message.get_args().split()[0])
        except:
            del users[message.from_user.id]
            return await message.reply('❌ Вы неправильно указали мегабайты! (Пример: buymb 512)')

        if (mb := await buymb(message.from_user.id, tobuy)):
            del users[message.from_user.id]

            await message.reply(f'💵 Вы купили <b>{str(tobuy)}МБ</b>', parse_mode='HTML')
        else:
            del users[message.from_user.id]
            
            await message.reply(f'❌ Ошибка: {mb}')

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
                      '🤴 Версия бота: 0.2 [Beta] ⚡</b>'
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
        InlineKeyboardButton('💵 Данные', callback_data='data')
    )
    keyboard.row(InlineKeyboardButton('☕ Поддержка', url='https://t.me/+8OUdVbortIw4MTQy'))
    keyboard.row(InlineKeyboardButton('🚫 Закрыть', callback_data='button3'))

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
async def handle_button_click(call: CallbackQuery):
    try:
        if call.data == 'data':
            tries = 5

            async def find():
                nonlocal tries

                if tries:
                    tries -= 1
                    user = await db.find(call.from_user.id)

                    if user:
                        used = user['used']
                        total = user['total']

                        keyboard = InlineKeyboardMarkup()
                        keyboard.row(
                            InlineKeyboardButton('🛍 Купить ресурсы', callback_data='buy'),
                            InlineKeyboardButton('🚫 Закрыть', callback_data='button3')
                        )

                        await bot.edit_message_text(
                            f'❇️ Всего: <b>{total} мб</b>\n'
                            f'🔥 Потрачено: <b>{used} мб</b>',
                            call.message.chat.id,
                            call.message.message_id,
                            parse_mode='HTML'
                        )
                        await bot.edit_message_reply_markup(
                            call.message.chat.id,
                            call.message.message_id,
                            call.inline_message_id,
                            keyboard
                        )

                        tries = 0
                    else:
                        await db.insert({'_id': call.from_user.id, 'user': '', 'used': 0, 'total': 0})
                        await asyncio.sleep(0.5)
                        await find()
            
            await find()
        elif call.data == 'buy':
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('256MB ', callback_data='mbbuy_256'))
            keyboard.add(InlineKeyboardButton('512MB ', callback_data='mbbuy_512'))
            keyboard.add(InlineKeyboardButton('1024MB', callback_data='mbbuy_1024'))
            keyboard.add(InlineKeyboardButton('КастомMB', callback_data='custombuy'))
            keyboard.add(InlineKeyboardButton('🧿 Назад', callback_data='data'))

            await bot.edit_message_text(
                f'➡ Выберите тариф',
                call.message.chat.id,
                call.message.message_id
            )
            await bot.edit_message_reply_markup(
                call.message.chat.id,
                call.message.message_id,
                call.inline_message_id,
                keyboard
            )
        elif (data := call.data.split('_'))[0] == 'mbbuy':
            # ваватиг сюда суй свою оплату ес чо

            if await buymb(call.from_user.id, int(data[-1])):
                await bot.edit_message_text(
                    f'Вы купили {data[-1]} мегабайт',
                    call.message.chat.id,
                    call.message.message_id
                )
                await bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    call.inline_message_id,
                    InlineKeyboardMarkup().add(InlineKeyboardButton('➡ Вернуться', callback_data='data'))
                )
        elif call.data == 'custombuy':
            global users

            users[call.from_user.id] = True

            await call.answer('Используйте команду: "/buymb кол-во"', show_alert=True)
        elif call.data == 'connections':
            if not (users := await db.find(call.from_user.id))['user']:
                await bot.edit_message_text(
                    'Используйте команду "/createuser"',
                    call.message.chat.id,
                    call.message.message_id
                )

                return await bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    call.inline_message_id,
                    InlineKeyboardMarkup().add(InlineKeyboardButton('➡ Вернуться', callback_data='account'))
                )
            
            keyboard = InlineKeyboardMarkup()
            user = (await db.find(call.from_user.id))['user']
            
            keyboard.add(InlineKeyboardButton('➡ Вернуться', callback_data='account'))

            await bot.edit_message_text(
                'Ваши подключения: \n'
                f'ssh -p 56222 {user}@52.29.107.118',
                call.message.chat.id,
                call.message.message_id
            )
    except Exception as error:
        import traceback
        print(traceback.format_exc())

@dp.message_handler(commands=['t'])
async def execute_command(message):
    command = message.text.split('/t', maxsplit=1)[1].strip()

    if not command:
        await message.reply("☝️ Пустая команда, укажи команду для выполнения")
        return

    safe = safe_command(command)
    if command.startswith(("ls", "dir", "pwd", "cat")) and safe:
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

async def check_res():
    while True:
        users = await db.db.find_one({})
        print(users)
        for user in users:
            if (us := user['user']):
                output = (await check(f'sudo du -sh /home/{us}')).decode()
                used = output.split()[0].lower()
                total = 0
                if 'k' in used:
                    used.replace('k', '')
                    total += float(used)
                if 'g' in used:
                    used.replace('g', '')
                    total += float(used)
                if 'm' in used:
                    used.repalce('m', '')
                    total += float(used)

                if used > user['total']:
                    import re

                    pids = (await check(f'fuser -v /home/{us}')).decode()

                    pid_pattern = r'\s\d+\s'
                    pids = [pid.strip() for pid in re.findall(pid_pattern, pids)]

                    for pid in pids:
                        print(await check(f'kill {int(pid)}'))

        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.ensure_future(check_res())
    executor.start_polling(dp, skip_updates=True, on_startup=print('[-] started'))
