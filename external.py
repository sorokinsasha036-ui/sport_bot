
import logging
from functools import wraps

def async_log_function_call(func):
    """Декоратор для логування викликів асинхронних функцій"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        msg = f"Відбувся виклик функції '{func.__name__}'"
        logger.info(msg)

        return await func(*args, **kwargs)

    return wrapper

def log_function_call(func):
    """Декоратор для логування викликів звичайних функцій (def)"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        msg = f"Відбувся виклик функції '{func.__name__}'"
        logger.info(msg)
        return func(*args, **kwargs)
    return wrapper