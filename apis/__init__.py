__version__ = '1.0.1'
__all__ = ['modrinth_api']

import os
import logging

MODRINTH_API_URL = 'https://api.modrinth.com/v2'

USER_AGENT = f'Solhex/easy-minecraft-mods-updater/{__version__} (contact@solfvern.com)'
HEADERS = {'User-agent': USER_AGENT}
LOG_MODE = logging.INFO

if not os.path.isdir('./logs'):
    os.mkdir('./logs')

from . import modrinth_api

