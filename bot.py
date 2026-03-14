
import logging

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("bot.log", mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ]
)

import asyncio
import sys
import random
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, URLInputFile
from config import TOKEN
from aiogram import F
from keyboards import main_reply_keyboard
from external import async_log_function_call

from commands import (
    START_COMMAND,
    HELP_COMMAND,
    SPORT_COMMAND,
    ADD_SPORT_COMMAND,
    SEARCH_SPORT_COMMAND,
    DELETE_SPORT_COMMAND,
    BOT_COMMANDS
)
    
from data import get_sport, add_sport, delete_sport_by_name
from keyboards import sport_keyboard_markup, SportCallback
from keyboards import create_data_keyboard 
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from models import Sport
from aiogram.fsm.context import FSMContext
from state_machine import SportForm, SearchSportForm, DeleteSportForm

dp = Dispatcher()

@dp.message(START_COMMAND)
@async_log_function_call
async def command_start_handler(message: Message) -> None:
    """
    Обробляє команду /start.
    """
    name = message.from_user.full_name or "User"
    keyboard = main_reply_keyboard()
    await message.answer(f"Привіт, {html.bold(name)}!", reply_markup=keyboard)

@dp.message(SPORT_COMMAND)
@async_log_function_call
async def show_sport(message: Message):
    """
    Показує список доступних видів спорту.
    """
    logging.info("Спорт від користувача")
    sport = get_sport()
    keyboard = sport_keyboard_markup(sport)
    await message.answer("Оберіть вид спорту:", reply_markup=keyboard)
    
@dp.callback_query(SportCallback.filter())
@async_log_function_call
async def sport_callback(callback: CallbackQuery, callback_data: SportCallback):
    logging.info("Вибір спорту користувача")
    sports = get_sport()  

    index = callback_data.id
    sport = sports[index]

    text = (
        f"<b>{sport['name']}</b>\n\n"
        f"<b>Правила:</b> {sport['rules']}\n\n"
        f"<b>Відомі спортсмени:</b> {', '.join(sport['players'])}\n\n"
        f"<b>Історія:</b> {sport['history']}\n\n"
        f"<b>Цікаві факти:</b> {sport['facts']}"
    )

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer() 

@dp.message(ADD_SPORT_COMMAND)
@async_log_function_call
async def add_sport_start(message: Message, state: FSMContext):
    """
    Починає процес додавання спорту до списку
    """
    logging.info("Додавання спорту")
    await message.answer("Введіть назву спорту:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SportForm.name)
 
@dp.message(SportForm.name)
@async_log_function_call
async def process_name(message: Message, state: FSMContext):
    """
    Введення користувачем назву спорту
    """
    logging.info("Введена назва спорту")
    await state.update_data(name=message.text)
    await message.answer("Введіть правила спорту:")
    await state.set_state(SportForm.rules)
   
@dp.message(SportForm.rules)
@async_log_function_call
async def process_rules(message: Message, state: FSMContext):
    """
    Введення користувачем правила спорту
    """
    logging.info("Введені правила спорту")
    await state.update_data(rules=message.text)
    await message.answer("Введіть відомих гравців: ")
    await state.set_state(SportForm.players)

@dp.message(SportForm.players)
@async_log_function_call
async def process_players(message: Message, state: FSMContext):
    """
    Введення користувачем відомих гравців спорту
    """
    logging.info("Введено гравців користувачем")
    players_list = [p.strip() for p in message.text.split(",")]
    await state.update_data(players=players_list)
    await message.answer("Введіть історію спорту: ")
    await state.set_state(SportForm.history)

@dp.message(SportForm.history)
@async_log_function_call
async def process_history(message: Message, state: FSMContext):
    """
    Введення користувачем історії спорту
    """
    logging.info("Введено історію спорту")
    await state.update_data(history=message.text)
    await message.answer("Введіть цікаві факти про спорт: ")
    await state.set_state(SportForm.facts)

@dp.message(SportForm.facts)
@async_log_function_call
async def process_facts(message: Message, state: FSMContext):
    """
    Введення користувачем факти про спорт
    """
    logging.info("Введені цікаві факти про спорт")
    await state.update_data(facts=message.text)

    user_data = await state.get_data()

    sport_obj = Sport(**user_data)

    add_sport(sport_obj.model_dump())

    logging.info(f"Спорт '{sport_obj.name}' успішно додано")

    await message.answer(f"Спорт '{sport_obj.name}' успішно збережено")

    await state.clear()

@dp.message(HELP_COMMAND)
@async_log_function_call
async def cmd_help(message: Message):
    """
    Показує список доступних команд бота.
    """
    logging.info(f"/help від користувача")
    text = (
        "<b>Ось що я вмію:</b>\n\n"
        "/start - Перезапустити бота\n"
        "/help - Довідка\n"
        "/sport - Список видів спорту\n"
        "/add_sport - Додати новий спорт\n"
        "/search_sport - Пошук спорту\n"
        "/delete_sport - Видалення спорту"

    )
    await message.answer(text)

@dp.message(SEARCH_SPORT_COMMAND)
@async_log_function_call
async def search_sport_start(message: Message, state: FSMContext):
    """
    Починає процес пошуку виду спорту.
    Просить користувача ввести назву спорту.
    """
    logging.info("/search_sport від користувача")
    await message.answer("Введіть назву спорту, який хочете знайти:")
    await state.set_state(SearchSportForm.name_query)

@dp.message(SearchSportForm.name_query)
@async_log_function_call
async def process_search(message: Message, state: FSMContext):
    """
    Шукає спорт у базі за назвою,
    введеною користувачем.
    """
    user_input = message.text.lower()
    sports_list = get_sport()  

    found = None
    for sport in sports_list:
        if sport["name"].lower() == user_input:
            found = sport
            break

    if found:
        logging.info("Спорт знайдено")
        text = (
            f"<b>{found['name']}</b>\n\n"
             f"<b>Правила:</b> {found['rules']}\n\n"
            f"<b>Відомі спортсмени:</b> {', '.join(found['players'])}\n\n"
            f"<b>Історія:</b> {found['history']}\n\n"
            f"<b>Цікаві факти:</b> {found['facts']}"
        )
        await message.answer(text, parse_mode="HTML")
    else:
        logging.info("Спорт не знайдено")
        await message.answer("На жаль, такий спорт не знайдено")

    await state.clear()

@dp.message(DELETE_SPORT_COMMAND)
@async_log_function_call
async def delete_sport_start(message: Message, state: FSMContext):
    """
    Починає процес видалення спорту.
    """
    await message.answer("Введіть назву спорту, який хочете видалити:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(DeleteSportForm.sport_name)

@dp.message(DeleteSportForm.sport_name)
@async_log_function_call
async def delete_sport_name(message: Message, state: FSMContext):
    """
    Видаляє вид спорту з JSON файлу
    """
    sport_name_input = message.text.lower()
    success = delete_sport_by_name(sport_name_input)


    if not success:
        await message.answer("Такий спорт не знайдено. Спробуйте ще раз")
        logging.info(f"Користувач {message.from_user.id} ввів невідомий спорт для видалення: {sport_name_input}")
        return

    await message.answer(f"Вид спорту '{sport_name_input}' успішно видалено")
    logging.info(f"Користувач {message.from_user.id} видалив вид спорту '{sport_name_input}'")
    await state.clear()

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(BOT_COMMANDS)
    logging.info("Бот запущено")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    

    
   
    
    


