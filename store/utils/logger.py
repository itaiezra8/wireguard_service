from core.utils.logger import Logger
from store.utils.consts import SERVICE_NAME

db_logger = Logger(SERVICE_NAME)
logger = db_logger.get_logger()
