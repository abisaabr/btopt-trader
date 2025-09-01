from loguru import logger
logger.add("logs/btopt.log", rotation="10 MB", enqueue=True, backtrace=True, diagnose=True)
