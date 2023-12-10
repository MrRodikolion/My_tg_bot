try:
    from ..conf import admin_chat_id
    from ..database import db
except BaseException:
    from conf import admin_chat_id
    from database import db

from aiogram import Bot, Router, types, F
from aiogram.filters.command import Command
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat

admin_router = Router()

question_btns = [
    [InlineKeyboardButton(text='<', callback_data='back'), InlineKeyboardButton(text='ans', callback_data='ans'),
     InlineKeyboardButton(text='>', callback_data='next')]]
question_keyboard = InlineKeyboardMarkup(inline_keyboard=question_btns)


class Waiters(StatesGroup):
    waiting_answer = State()

    question_id = State()
    processed_question = State()


async def set_admin_commands(bot: Bot):
    await bot.set_my_commands([BotCommand(command='question', description='оветить на вопросы')],
                              BotCommandScopeChat(chat_id=admin_chat_id))


@admin_router.message(Command('start'), F.chat.id == admin_chat_id)
async def admin_start(message: types.Message, state: FSMContext):
    await message.answer('/ans chat_id text', reply_markup=ReplyKeyboardRemove())
    await state.update_data(question_id=0)


@admin_router.message(Command('ans'), F.chat.id == admin_chat_id)
async def ans_question(message: types.Message, state: FSMContext, bot: Bot):
    try:
        args = message.text.split()[1:]
        chat_id = args[0]
        answer = ' '.join(args[1:])
        await bot.send_message(chat_id, answer)
    except ValueError as e:
        message_text = f'Неверная команда: {message.text}\nОшибка: {e}'
        await message.reply(message_text)


@admin_router.message(Command('questions'), F.chat.id == admin_chat_id)
async def view_all_questions(message: types.Message, state: FSMContext):
    questions = await db.get_unsolved_questions()
    q_id = (await state.get_data())['question_id']

    await state.update_data(processed_question=questions[q_id])

    message_text = f'{questions[q_id][0]} {questions[q_id][1]} \n\"{questions[q_id][2]}\"'
    await message.answer(message_text, reply_markup=question_keyboard)


@admin_router.callback_query(F.data == 'ans')
async def ans_to_question(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Waiters.waiting_answer)
    await call.message.answer('Напишите ответ')
    await call.answer()


@admin_router.message(Waiters.waiting_answer, F.chat.id == admin_chat_id)
async def processing_ans(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(waiting_answer=message.text)
    question_id, user_id, *_ = (await state.get_data())['processed_question']

    await bot.send_message(user_id, message.text)
    await db.make_un_to_solved(question_id)


@admin_router.callback_query(F.data == 'next')
async def next_question(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    q_id = (await state.get_data())['question_id'] + 1

    questions = await db.get_unsolved_questions()
    if q_id >= len(questions):
        return

    message_text = f'{questions[q_id][0]} {questions[q_id][1]} \n\"{questions[q_id][2]}\"'
    await call.message.edit_text(message_text, reply_markup=question_keyboard)

    await state.update_data(processed_question=questions[q_id])
    await state.update_data(question_id=q_id)


@admin_router.callback_query(F.data == 'back')
async def next_question(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    q_id = (await state.get_data())['question_id'] - 1

    questions = await db.get_unsolved_questions()
    if q_id < 0:
        return

    message_text = f'{questions[q_id][0]} {questions[q_id][1]} \n\"{questions[q_id][2]}\"'
    await call.message.edit_text(message_text, reply_markup=question_keyboard)

    await state.update_data(processed_question=questions[q_id])
    await state.update_data(question_id=q_id)


@admin_router.message(Command('send'))
async def send(message: types.Message, bot: Bot):
    message_text = message.text[message.text.find(' '):]
    users = await db.get_users()
    for user in users:
        user_id = user[1]
        await bot.send_message(user_id, message_text)
