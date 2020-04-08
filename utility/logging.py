import logging
import logging.handlers
from pathlib import Path

Path('logs/twitchio').mkdir(parents=True, exist_ok=True)
Path('logs/raw_data').mkdir(parents=True, exist_ok=True)
Path('logs/asyncio').mkdir(parents=True, exist_ok=True)
Path('logs/aiohttp').mkdir(parents=True, exist_ok=True)

twitchio_logger = logging.getLogger('twitchio')
twitchio_logger.setLevel(logging.DEBUG)
twitchio_logger_handler = logging.handlers.TimedRotatingFileHandler(filename='logs/twitchio/twitchio.log',
                                                                    when='midnight', backupCount=500000, encoding='UTF-8')
twitchio_logger_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s %(name)s: %(message)s'))
twitchio_logger.addHandler(twitchio_logger_handler)

asyncio_logger = logging.getLogger('asyncio')
asyncio_logger.setLevel(logging.DEBUG)
asyncio_logger_handler = logging.handlers.TimedRotatingFileHandler(filename='logs/asyncio/asyncio.log',
                                                                   when='midnight', backupCount=500000, encoding='UTF-8')
asyncio_logger_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s %(name)s: %(message)s'))
asyncio_logger.addHandler(asyncio_logger_handler)

# aiohttp_client_logger = logging.getLogger('aiohttp')
# aiohttp_client_logger.setLevel(logging.DEBUG)
# aiohttp_client_logger_handler = logging.handlers.TimedRotatingFileHandler(filename='logs/aiohttp/client.log',
#                                                                           when='midnight', backupCount=500000, encoding='UTF-8')
# aiohttp_client_logger_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s %(name)s: %(message)s'))
# aiohttp_client_logger.addHandler(aiohttp_client_logger_handler)

raw_data_logger = logging.getLogger('raw data')
raw_data_logger.setLevel(logging.DEBUG)
raw_data_handler = logging.handlers.TimedRotatingFileHandler(filename='logs/raw_data/raw_data.log',
                                                             when='midnight', backupCount=500000, encoding='UTF-8')
raw_data_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s %(name)s: %(message)s'))
raw_data_logger.addHandler(raw_data_handler)
