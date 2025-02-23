import logging


# Configure a logger with library name and desired format
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Formatter with stack level (shows line number and file name)
logging_format = "%(asctime)s - %(module)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s"
formatter = logging.Formatter(logging_format)
stream_handler = logging.StreamHandler()  # Separate handler creation
stream_handler.setFormatter(formatter)    # Set formatter on the handler
logger.addHandler(stream_handler)        # Add formatted handler to logger

# Optional NullHandler to prevent missing logs
logger.addHandler(logging.NullHandler())
