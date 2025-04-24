from loguru import logger

logger.add("logs/app.log", rotation="1 MB", retention="10 days", level="INFO")

def get_logger():
    return logger
