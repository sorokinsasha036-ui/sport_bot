
import logging

logger = logging.getLogger(__name__)

import json
import os
from external import log_function_call

FILE_PATH = "data.json"
DATA_FILE = "data.json"

@log_function_call
def get_sport(id: int | None = None):
    """
    Отримує види спорту з JSON файлу.
    """
    logging.info("Запит на отримання спорту")
    if not os.path.exists(FILE_PATH):
        logging.warning("Файл data.json не знайдено")
        return []

    with open(FILE_PATH, "r", encoding="utf-8") as f:

        data = json.load(f)

    logging.debug(f"Завантажено {len(data)} видів спорту")

    if id is not None:
        logging.info(f"Пошук спорту з id={id}")
        for sport in data:
            if sport["id"] == id:
                logging.info(f"Знайдено спорт: {sport['name']}")
                return sport
        return None 

    return data

@log_function_call
def add_sport(sport: dict):
    """ 
    Додає новий вид спорту у файл data.json.
    """
    logging.info(f"Додається новий спорт: {sport.get('name')}")
    sports = get_sport()

    sports.append(sport)

    logging.debug(f"Тепер у базі {len(sports)} видів спорту")

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(sports, f, ensure_ascii=False, indent=4)

    logging.info("Спорт успішно збережено у data.json")

@log_function_call
def delete_sport_by_name(sport_name: str) -> bool:
    """
    Видаляє спорт за назвою з JSON.
    Повертає True, якщо спорт було видалено, False — якщо не знайдено.
    """
    
    if not os.path.exists(DATA_FILE):
        logging.warning("Файл data.json не знайдено")
        return False

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        sports = json.load(f)

    sport = next((s for s in sports if s["name"].lower() == sport_name.lower()), None)
    if not sport:
        return False

    sports.remove(sport)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sports, f, ensure_ascii=False, indent=4)

    logging.info(f"Вид спорту '{sport_name}' видалено")
    return True


