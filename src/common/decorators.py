import time
from functools import wraps
from common.logger import logger
from clickhouse_connect.driver.exceptions import DatabaseError, OperationalError

def retry_db_operation(max_retries=3, backoff_factor=2):
    """
    Decorator que implementa retries com backoff exponencial 
    para operações no banco de dados. (Bass Tactic: Retry)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (DatabaseError, OperationalError, Exception) as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"Falha definitiva após {max_retries} tentativas: {func.__name__}")
                        raise
                    
                    sleep_time = backoff_factor ** retries
                    logger.warning(
                        f"Falha transitória na operação {func.__name__}. "
                        f"Tentativa {retries}/{max_retries}. "
                        f"Aguardando {sleep_time}s... Erro: {str(e)}"
                    )
                    time.sleep(sleep_time)
        return wrapper
    return decorator
