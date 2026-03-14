
import logging
logger = logging.getLogger(__name__)

from aiogram.filters import Command
from aiogram.types import BotCommand

logging.debug("Створення фільтрів команд")

START_COMMAND = Command("start")
HELP_COMMAND = Command("help")
SPORT_COMMAND = Command("sport")
ADD_SPORT_COMMAND = Command("add_sport")
SEARCH_SPORT_COMMAND = Command("search_sport")
DELETE_SPORT_COMMAND = Command("delete_sport")

logging.debug("Фільтри команд успішно створено")

""" 
Список команд бота.
"""

BOT_COMMANDS = [
   BotCommand(command="start", description="Почати розмову"),
   BotCommand(command="help", description="Звернутися до довідки"),
   BotCommand(command="sport", description="Обрати вид спорту"),
   BotCommand(command="add_sport", description="Додати свій вид спорту"),
   BotCommand(command="search_sport", description="Пошук спорту"),
   BotCommand(command="delete_sport", description="Видалити вид спорту")
]