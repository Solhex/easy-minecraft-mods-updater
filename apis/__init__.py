__version__ = '1.0.0'
__all__ = ['modrinth_api']

import os

MODRINTH_API_URL = 'https://api.modrinth.com/v2'

USER_AGENT = f'Solhex/easy-minecraft-mods-updater/{__version__} (contact@solfvern.com)'
HEADERS = {'User-agent': USER_AGENT}

if not os.path.isdir('./logs'):
    os.mkdir('./logs')

from . import modrinth_api

