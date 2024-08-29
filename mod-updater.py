__version__ = '0.2'

import hashlib
import argparse
import requests
from requests.exceptions import HTTPError
import os
import logging

parser = argparse.ArgumentParser(
    prog='Minecraft Mod Updater',
    description='Gets your minecraft mods and them updates')
parser.add_argument(
    'gameversion', metavar='gameversion',
    action='store', type=str,
    help=f'The version of the game (e.g. 1.16.5 24w34a 1.21)')
args = parser.parse_args()

logger = logging.getLogger(__name__)
mod_api_url = (r'https://api.modrinth.com/v2')

def get_sha1(
        filepath,
        buffer_size=65536) -> str:
    """Gets the sha1 hash of a file."""
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            sha1.update(data)
    logger.debug(f'Gotten sha1 hash: {sha1.hexdigest()} from {filepath}')

    return sha1.hexdigest()

# def get_mod_file_info(
#         mod_hash,
#         mod_hash_type='sha1',
#         api_url=mod_api_url,
#         header=None) -> tuple | None:
#     """Gets the ID of a mod from its file."""
#     if header is None:
#         header = {}
#     logger.debug(f'Using header: {header}')
#
#     request = requests.get(
#         f'{api_url}/version_file/{mod_hash}',
#         params={'algorithm': mod_hash_type},
#         headers=header
#     )
#     logger.info(f'Getting the info of hash {mod_hash} with algorithm {mod_hash_type}')
#
#     if request.status_code != 200:
#         logger.warning(f'Mod info not found! Status info: {request.status_code}')
#         return None
#
#     mod_info = request.json()
#
#     return mod_info
def download_file(url, path='./') -> str:
    """Downloads a file from a URL."""
    filename = url.split('/')[-1]
    logger.info(f'Downloading {filename}')
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(path, filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return filename



def update_mod(
        mod_hash: str,
        game_version: str,
        loader: str,
        header=None) -> None:
    """Updates a mod."""
    requests.post()


def main():
    log_format = '[%(asctime)s]:[%(levelname)s]: %(message)s'
    logging.basicConfig(
        filename='mod-updater.log',
        level=logging.DEBUG,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.info('Script started')
    print(f'Auto mod updater script started! Version {__version__}')

    script_dir = os.path.split(os.path.realpath(__file__))[0]
    logger.debug(f'Current script directory: {script_dir}')

    # if script_dir.split(os.sep)[-1] != '.minecraft':
    #     logger.critical('Script not in the .minecraft directory')
    #     print('[Error] Script must be in the .minecraft directory.')
    #     exit()
    # elif os.path.isdir('./mods') == False:
    #     logger.critical('Mod folder not found')
    #     print('[Error] Mod folder does not exist.')
    logger.debug(args)

    user_agent = f'Solhex/minecraft-mod-auto-updater/{__version__} (contact@solfvern.com)'
    headers = {'User-agent': user_agent}
    logger.debug(f'Set header to: {headers}')

    mod_dir = f'{script_dir}/mods'
    mod_dir_list = os.listdir(mod_dir)
    logger.debug(f'Mod dir set to: {mod_dir}')
    for mod in mod_dir_list:
        if mod.split('.')[-1] != 'jar':
            logger.info(f'Skipping {mod}')
            print(f'Skipping {mod}')
            continue

        logger.debug(f'Checking {mod} for updates')
        print(f'Checking {mod} for updates')
        mod_hash = get_sha1(f'./mods/{mod}')
        update_mod(mod_hash, game_version=args.gameversion, loader=args.loader, header=headers)


if __name__ == '__main__':
    main()
