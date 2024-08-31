__version__ = '1.1.1'

import hashlib
import argparse
import requests
from requests.exceptions import HTTPError
import os
import logging

from apis.modrinth_api import ModrinthApi

parser = argparse.ArgumentParser(
    prog='Minecraft Mod Updater',
    description='Gets your minecraft mods and them updates')
parser.add_argument(
    'gameversion', metavar='gameversion',
    action='store', type=str,
    help='The version of the game (e.g. 1.16.5 24w34a 1.21)')
parser.add_argument(
    '-p', '--path',
    metavar='path', action='store',
    type=str, help='Path to the .minecraft path, '
                   'if not used script will assume its in the .minecraft folder')
parser.add_argument(
    '-k', '--keep',
    action='store_true', help='Keeps the old mods')
parser.add_argument(
    '-V', '--version',
    action='version', version=__version__)
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

def download_mod(
        update_link: str,
        mod_dir='./mods') -> None:
    """Downloads a mod"""
    try:
        download_file(update_link, path=mod_dir)
    except HTTPError as err:
        logger.error(f'HTTP error occurred: {err}')
        print(f'[Error] HTTP error occurred: {err}')
    except Exception as err:
        logger.critical(f'Unexpected error occurred: {err}')
        print(f'[Critical] Unexpected error occurred: {err}')

def main():
    log_format = '[%(asctime)s]:[%(levelname)s]: %(message)s'
    logging.basicConfig(
        filename='mod-updater.log',
        level=logging.INFO,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S')
    logger.info('Script started')
    print(f'Auto mod updater script started! Version {__version__}')
    logger.debug(f'Script args: {args}')

    minecraft_dir = os.path.split(os.path.realpath(__file__))[0]
    if args.path is not None:
        minecraft_dir = os.path.normpath(args.path)
    logger.debug(f'Current script directory: {minecraft_dir}')

    if minecraft_dir.split(os.sep)[-1] != '.minecraft':
        logger.critical('Either script must be in the .minecraft directory or have -p set to it. '
                        f'Was set to: {minecraft_dir}')
        print('[Error] Script must be in the .minecraft directory or -p set to it. '
              f'Was set to: {minecraft_dir}')
        exit()
    elif not os.path.isdir('./mods'):
        logger.critical('Mod folder not found')
        print('[Error] Mod folder does not exist.')
        exit()

    modrinth = ModrinthApi()

    mod_dir = f'{minecraft_dir}/mods'
    mod_dir_list = os.listdir(mod_dir)
    logger.debug(f'Mod dir set to: {mod_dir}')

    mods_fname_dict = {}
    mod_hash_list = []
    for mod in mod_dir_list:
        if mod.split('.')[-1] != 'jar':
            logger.info(f'Skipping {mod}')
            print(f'Skipping {mod}')
            continue
        logger.debug(f'Getting {mod} hash')
        print(f'Checking {mod} for updates')
        mod_hash = get_sha1(f'./mods/{mod}')
        mods_fname_dict[mod_hash] = mod
        mod_hash_list.append(mod_hash)

    if not mod_hash_list:
        logger.warning('No mods found!')
        print('No mods found!')
        exit()
    
    mods_info_dict = modrinth.get_multiple_mods_details(mod_hash_list)
    if 'error' in mods_info_dict.keys():
        print(f'[Error] {mods_info_dict['error']}\nNo updates can be performed quitting.')
        exit()
    logger.debug(f'Bulk mods info: {mods_info_dict}')

    loader_mods_dict = {}
    mods_loader_dict = {}
    mods_update_info = {}
    for mod in mods_info_dict:
        loader = mods_info_dict[mod]['loaders'][0]
        if loader not in loader_mods_dict:
            loader_mods_dict[loader] = [mod]
            mods_update_info[loader] = {}
        else:
            loader_mods_dict[loader].append(mod)
        mods_loader_dict[mod] = loader
    logger.debug(f'Loader mods dict: {loader_mods_dict}')
    logger.debug(f'Mods loader dict: {mods_loader_dict}')

    for loader in loader_mods_dict:
        mods_update_info[loader] = modrinth.get_multiple_mods_update_info(
            loader_mods_dict[loader],
            game_version=args.gameversion,
            loader=loader)
        logger.debug(f'Bulk updated mods info for {loader}: {mods_update_info[loader]}')
        if 'error' in mods_info_dict.keys():
            print(f'[Error] {mods_update_info[loader]}\nNo updates can be performed quitting.')
            exit()
    logger.debug(f'Mods update info: {mods_update_info}')

    mods_updated_count = 0
    for mod in mod_hash_list:
        logger.info(f'Checking {mods_fname_dict[mod]} ({mod}) for updates')
        mod_update_files = mods_update_info[mods_loader_dict[mod]][mod]['files']
        mod_dl_url = mod_update_files[0]['url']
        new_mod_filename = mod_update_files[0]['filename']

        if mod == mod_update_files[0]['hashes']['sha1']:
            logger.info(f'Mod {mods_fname_dict[mod]} is already updated')
            print(f'Mod {mods_fname_dict[mod]} is already updated')
            continue

        logger.debug(f'Update link for {mods_fname_dict[mod]}: {mod_update_files[0]['url']}')
        print(f'Updating {mods_fname_dict[mod]} to {new_mod_filename}')

        download_mod(mod_dl_url, mod_dir)

        if not args.keep:
            os.remove(os.path.join(mod_dir, mods_fname_dict[mod]))
            logger.info(f'Deleted old mod file: {mods_fname_dict[mod]}')
            print(f'Deleted old mod file: {mods_fname_dict[mod]}')

        mods_updated_count += 1

    logger.info(f'{mods_updated_count} mods updated successfully')
    print(f'{mods_updated_count} mods updated successfully')


if __name__ == '__main__':
    main()
