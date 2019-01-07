import datetime
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import PurePath, Path

import yaml

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format('.', os.path.basename(__file__))),
        logging.StreamHandler()
    ])

logger = logging.getLogger()


def create_folder():
    cur_date = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
    Path(cur_date).mkdir(exist_ok=True)
    logger.info(f'Folder to backup: {cur_date}')
    return Path(cur_date)


def pathToName(pth: str):
    st = pth.replace(':\\', '_').replace('\\\\', '_').replace('\\', '_')
    if st[-1] == '_': return st[:-1]
    return st


def compressFolder(folder, dest):
    if not os.path.isdir(folder):
        logger.error(f'{folder} is not a folder or doesn\'t exist, omitted')
        return

    t = time.time()
    logger.info(f'Compressing: {folder}')

    files = []
    for r, d, f in os.walk(folder):
        for file in f:
            files.append(os.path.join(r, file))

    ZipFile = zipfile.ZipFile(dest.joinpath(pathToName(folder + ".zip")), "w")
    for f in files:
        ZipFile.write(filename=f, arcname=os.path.relpath(f, folder), compress_type=zipfile.ZIP_DEFLATED)

    logger.info(f'(ok) time: {(time.time() - t):.3f} s')


def compressFile(file, dest):
    if not os.path.isfile(file):
        logger.error(f'{file} is not dir, omitted')
        return

    t = time.time()
    logger.info(f'Compressing: {file}')
    file_zip = zipfile.ZipFile(str(dest.joinpath(pathToName(file))) + '.zip', 'w')
    try:
        file_zip.write(file, arcname=PurePath(file).name, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        logger.info(f'(ok) time: {(time.time() - t):.3f} s')
    except Exception as e:
        logger.error(f'(Er) time: {(time.time() - t):.3f} s')
        logger.error(e)
    finally:
        file_zip.close()


def divider(f):
    def tmp(*args, **kwargs):
        logger.info("-" * 80)
        logger.info(f.__name__)
        logger.info("-" * 80)
        res = f(*args, **kwargs)
        return res

    return tmp


class Backup:
    """
    Do backup of files and folders with optional encryption.
    Required path to YAML file with configuration.
    If encryption is chosen, need full path to the 7z executable file.
    Methods:
        do_folders_backup() - create folder with zipped files in current folder
        do_files_backup()   -
        encrypt()           - encrypt all file in the folders with password using 7z
        move_backup()       - move backup from current folder to the destination
        clean_old()         - delete old backups
    """

    def __init__(self, config_path):
        try:
            logger.info('Reading config...')
            self.__cfg = yaml.load(open(config_path, 'rt'))
            self.__encrypt = self.__cfg['encrypt']
            if self.__encrypt:
                try:
                    self.__psw = open(self.__cfg['psw_file']).readline().strip()
                except Exception as e:
                    logger.error(e)
                    sys.exit(1)

            if self.__encrypt:
                if not self.__psw:
                    logger.error('Error: Password is not properly set up')
                    raise AttributeError
            self.__dst = self.__cfg['backup_destination']
            self.__keep_version = self.__cfg['keep_versions']
            self.__dt_fld = create_folder()

            # TODO: check if folder doesn't copy itself.
        except Exception as e:
            logger.error(e)
            sys.exit(1)

    # noinspection SpellCheckingInspection
    @divider
    def do_folders_backup(self):  # Folders backup
        # TODO: implement .gitignore for folders
        # TODO: show what is compressing in logs

        if len(self.__cfg['dir_paths']) > 0:
            logger.info(f"Folders to compress: {len(self.__cfg['dir_paths'])}")
            for folder in self.__cfg['dir_paths']:
                compressFolder(folder, self.__dt_fld)

    @divider
    def do_files_backup(self):  # Files backup
        if len(self.__cfg['file_paths']) > 0:
            logger.info(f"Files to compress: {len(self.__cfg['file_paths'])}")
            for file in self.__cfg['file_paths']:
                compressFile(file, self.__dt_fld)

    @divider
    def move_backup(self):
        try:
            logger.info('Moving files...')
            shutil.move(str(self.__dt_fld), self.__dst)
            logger.info('Moved successfully')
        except Exception as e:
            logger.error('Moving files...')
            logger.error(e)

    @divider
    def clean_old(self):
        if self.__keep_version <= 0:
            logger.info(f'keep_version is: {self.__keep_version}. Cleaning is ignored.')
            return
        r = re.compile('\\d{4}\\.\\d\\d\\.\\d\\d-\\d\\d\\.\\d\\d\\.\\d\\d')
        fld_lst = [fld[0] for fld in os.walk(self.__dst) if r.match(os.path.basename(fld[0]))]
        fld_lst.sort()
        while len(fld_lst) > self.__keep_version:
            fld_to_delete = fld_lst.pop(0)
            try:
                shutil.rmtree(fld_to_delete)
                logger.info(f'Deleted old version: {fld_to_delete} : (ok)')
            except Exception as e:
                logger.error(f'Error on deleting version: {fld_to_delete} : (Error)')
                logger.error(e)

    @divider
    def encrypt(self):
        if not self.__encrypt:
            logger.info("Encryption is off")
        else:
            try:
                appPath = "C:\\Program Files\\7-Zip"
                zApp = "7z.exe"
                progDir = os.path.join(appPath, zApp)

                rc = subprocess.Popen(
                    [progDir, 'a', str(self.__dt_fld.name) + '.7z', '-sdel', '-mhe=on', 'x=0', '-p' + self.__psw, '-y', "*.*"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(self.__dt_fld.resolve()))
                streamdata = rc.communicate()[0]

                if rc.returncode == 0:
                    logger.info('Encryption done successfully')
                else:
                    logger.info(rc.stderr)
                    logger.info('Encryption was unsuccessful')
            except Exception as e:
                logger.error(e)


def main():
    logger.info('=' * 100)
    backup = Backup('config.yaml')
    backup.do_folders_backup()
    backup.do_files_backup()
    backup.encrypt()
    backup.move_backup()
    backup.clean_old()


if __name__ == '__main__': main()
