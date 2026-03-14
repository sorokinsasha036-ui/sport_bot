
import logging

logger = logging.getLogger(__name__)

from aiogram.fsm.state import State, StatesGroup

class SportForm(StatesGroup):    
    """ 
    Група класу для додавання нового виду спорту
    """
    name = State()  
    rules = State()     
    players = State()   
    history = State()   
    facts = State()  

logging.info("Група станів SportForm створена")  

class SearchSportForm(StatesGroup):
    """ 
    Група станів для пошуку видів спорту
    """
   
    name_query = State()

logging.info("Група станів SearchSportForm створена")

class DeleteSportForm(StatesGroup):
    """ 
    Група станів для видалення видів спорту
    """
    sport_name = State()

logging.info("Група станів DeleteSportForm створена")
