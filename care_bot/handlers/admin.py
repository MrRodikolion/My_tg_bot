from conf import admin_chat_id

from aiogram import Bot, Router, types, F
from aiogram.filters.command import Command
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat
from aiogram.types import BotCommand

admin_router = Router()


async def set_admin_commands(bot: Bot):
    await bot.set_my_commands([BotCommand(command='ans', description='/ans caht_id text')],
                              BotCommandScopeChat(chat_id=admin_chat_id))


@admin_router.message(Command('start'), F.chat.id == admin_chat_id)
async def admin_start(message: types.Message):
    await message.answer('/ans chat_id text')


@admin_router.message(Command('ans'), F.chat.id == admin_chat_id)
async def ans_question(message: types.Message, bot: Bot):
    try:
        args = message.text.split()[1:]
        chat_id = args[0]
        answer = ' '.join(args[1:])
        await bot.send_message(chat_id, answer)
    except ValueError as e:
        message_text = f'Неверная команда: {message.text}\nОшибка: {e}'
        await message.reply(message_text)
