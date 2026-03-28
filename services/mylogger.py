import logging

# Create a custom logger
logger = logging.getLogger(__name__)

# Set level of logger
logger.setLevel(logging.DEBUG)

# Create a file handler
handler = logging.FileHandler('../logger.log')

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(handler)