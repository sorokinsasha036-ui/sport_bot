
import logging

logger = logging.getLogger(__name__)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class SportCallback(CallbackData, prefix="sport"):
    """ 
    Клас callback-даних для кнопок вибору спорту.
    """
    id: int

def sport_keyboard_markup(sports: list[dict]) -> InlineKeyboardMarkup:
    """ 
    Створює inline-клавіатуру зі списком видів спорту.
    """
    logging.info("Створенння клавіатури для вибору спорту")

    buttons = [
        [InlineKeyboardButton(text=sport["name"], callback_data=f"sport:{i}")]
        for i, sport in enumerate(sports)
    ]
    logging.debug(f"Кількість кнопок спорту: {len(buttons)}")
    return InlineKeyboardMarkup(inline_keyboard=buttons)

data_sport = ["Правила", "Факти", "Гравці", "Історія"]

def create_data_keyboard():
    """ 
    Створює inline-клавіатуру з кнопками інформації про спорт.
    """
    logging.info("Створення клавіатури з даними про спорт")

    builder = InlineKeyboardBuilder()

    for button in data_sport:
        logging.debug(f"Додається кнопка: {button}")

        builder.button(text=button, callback_data=f"data_{button.lower()}")
    builder.adjust(1, repeat=True)
    return builder.as_markup()

def main_reply_keyboard():
    """ 
    Створює головну reply-клавіатуру Telegram-бота.
    """
    logging.info("Створення головної клавіатури бота")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/help"), KeyboardButton(text="/sport")],
            [KeyboardButton(text="/add_sport"), KeyboardButton(text="/search_sport"), KeyboardButton(text="/delete_sport")]
        ],
        resize_keyboard=True
    )
    logging.debug("Головна клавіатура створена")
    return keyboard