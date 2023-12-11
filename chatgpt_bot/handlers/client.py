from aiogram import Bot, Router, types, F
from aiogram.filters.command import Command
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
import g4f

try:
    from ..database import db
except BaseException:
    from database import db

client_router = Router()


class FSMClient(StatesGroup):
    waiting_conversation = State()

    model = State()

async def set_client_commands(bot: Bot):
    await bot.set_my_commands([BotCommand(command='models', description='выбор модели'),
                               BotCommand(command='clear', description='очистить историю')])

@client_router.message(Command('start'))
async def start(message: types.Message):
    await message.answer('/models выбор модели\n/clear очистить историю')


@client_router.message(Command('clear'))
async def clear_history(message: types.Message, state: FSMContext):
    await db.clear_messages(message.from_user.id)
    await message.answer('переписка очищена')


@client_router.message(Command('models'))
async def models_info(message: types.Message, state: FSMContext):
    await message.answer(
        'выберете модель:\n/llama2 крутая для кода но только на англ\n/gpt_4 не учитывет предыдущие сообщения\n/gpt_35')


@client_router.message(Command('llama2'))
async def set_gpt4(message: types.Message, state: FSMContext):
    await state.update_data(model=g4f.models.llama2_70b)


@client_router.message(Command('gpt_4'))
async def set_gpt4(message: types.Message, state: FSMContext):
    await state.update_data(model=g4f.models.gpt_4)


@client_router.message(Command('gpt_35'))
async def set_gpt4(message: types.Message, state: FSMContext):
    await state.update_data(model=g4f.models.gpt_35_turbo_16k)


@client_router.message(F.text[0] != '/')
async def conversation_processing(message: types.Message, state: FSMContext):
    sended_message = await message.answer('думаем')

    try:
        await state.update_data(waiting_conversation=message.text)

        await db.add_message(message.from_user.id, message.text)
        messages_history = await db.get_messages(message.from_user.id)

        try:
            model = (await state.get_data())['model']
        except BaseException:
            model = g4f.models.gpt_35_turbo_16k

        if model == g4f.models.llama2_70b:
            response = await g4f.ChatCompletion.create_async(
                model=model,
                messages=messages_history[-1:],
                provider=g4f.Provider.Llama2)
        elif model == g4f.models.gpt_4:
            response = await g4f.ChatCompletion.create_async(
                model=model,
                messages=messages_history[-1:],
                provider=g4f.Provider.GeekGpt)
        else:
            response = await g4f.ChatCompletion.create_async(
                model=model,
                messages=messages_history,
                provider=g4f.Provider.ChatgptAi)

        await sended_message.edit_text(response)

        await db.add_assistant_message(message.from_user.id, response)

    except BaseException as e:
        await sended_message.edit_text(f'что-то пошло не так:\n{e}')
