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

def bulk_mod_info(
        mod_hash_list: list,
        mod_hash_type='sha1',
        api_url=mod_api_url,
        header=None) -> tuple | None:
    """Gets the information of multiple mods."""
    logger.debug(f'Starting bulk_mod_info')
    if header is None:
        header = {}
    logger.debug(f'Using header: {header}')

    body = {
        'hashes': mod_hash_list,
        'algorithm': mod_hash_type
    }
    logger.debug(f'JSON body: {body}')
    try:
        response = requests.post(
            f'{api_url}/version_files',
            json=body,
            headers=header
        )
    except HTTPError as err:
        logger.error(f'HTTP error occurred: {err}')
        logger.debug(response.text)
        print(f'[Error] Error occurred when locating updates: {err}')
    except Exception as err:
        logger.critical(f'Unexpected error occurred: {err}')
        print(f'[Critical] Unexpected error occurred: {err}')

    return response.json()

def bulk_mod_update_info(
        mod_hash_list: list,
        game_version: str,
        loader: str,
        mod_hash_type='sha1',
        api_url=mod_api_url,
        header=None) -> dict:
    """Gets the update information of a bunch of mods using a list
    of their hashes.
    """
    logger.debug(f'Starting bulk_mod_update_info')
    if header is None:
        header = {}
    logger.debug(f'Using header: {header}')

    body = {
        'hashes': mod_hash_list,
        'algorithm': mod_hash_type,
        'loaders': [loader],
        'game_versions': [game_version]
    }
    logger.debug(f'JSON body: {body}')
    try:
        response = requests.post(
            f'{api_url}/version_files/update',
            json=body,
            headers=header)
        response.raise_for_status()
    except HTTPError as err:
        logger.error(f'HTTP error occurred: {err}')
        logger.debug(response.text)
        print(f'[Error] Error occurred when locating updates: {err}')
    except Exception as err:
        logger.critical(f'Unexpected error occurred: {err}')
        print(f'[Critical] Unexpected error occurred: {err}')
    else:
        return response.json()
    return {}

def update_mod(
        update_link: str,
        old_mod_file_name: str,
        mod_dir='./mods',
        delete_old_mod=True):
    """Downloads a mod and replaces it if needed"""
    try:
        download_file(update_link, path=mod_dir)
    except HTTPError as err:
        logger.error(f'HTTP error occurred: {err}')
        print(f'[Error] HTTP error occurred: {err}')
    except Exception as err:
        logger.critical(f'Unexpected error occurred: {err}')
        print(f'[Critical] Unexpected error occurred: {err}')

    if delete_old_mod:
        os.remove(os.path.join(mod_dir, old_mod_file_name))
        logger.info(f'Deleted old mod file: {old_mod_file_name}')
        print(f'Deleted old mod file: {old_mod_file_name}')


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
