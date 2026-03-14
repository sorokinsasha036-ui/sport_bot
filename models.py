
import logging

logger = logging.getLogger(__name__)

from pydantic import BaseModel


class Sport(BaseModel):
    """ 
    Модель виду спорту
    """
    name: str               
    rules: str              
    players: list[str]       
    history: str            
    facts: str
