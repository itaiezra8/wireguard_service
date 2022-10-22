from core.utils.logger import Logger
from wireguard.utils.consts import SERVICE_NAME


wireguard_logger = Logger(SERVICE_NAME)
logger = wireguard_logger.get_logger()

