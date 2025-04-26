import shutil
import threading

from random import random, choice

import string

import os
import glob
import typing

def remove_files(dir_path: str, file_ext: str):
    """Deletes files of certain extension in specified directory"""

    # add * before the extension to match any file with this extension
    pattern = f'{dir_path}/*.{file_ext}'

    # get list of files in directory with the given extension
    files = glob.glob(pattern)

    # iterate over list of files and delete each file
    for file in files:
        os.remove(file)
    return

g_instance = None


class LogDebugHelper():

    _instance = None
    _lock = threading.Lock()


    def __new__(cls, *args, **kwargs):
        global g_instance
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LogDebugHelper, cls).__new__(cls)
                cls._instance.init(*args, **kwargs)
                g_instance = cls._instance
        return cls._instance

    def init(self, root_path, src_lang: str = None, dst_lang: str = None):
        self.src_lang = None
        self.dst_lang = None
        self.RootPath = None

        self.setRootPath(root_path)
        self.setLangInfo(src_lang, dst_lang)
        return

    def setLangInfo(self, src_lang: str, dst_lang: str = None):
        self.src_lang = src_lang
        self.dst_lang = dst_lang
        if not (self.src_lang is None or self.dst_lang is None):
            self.__make_lock_lang_file()
        return

    def __get_path_lock_file__(self):
        if (self.src_lang is None or self.dst_lang is None): return None
        postfix_name = '_' + self.src_lang + '_' + self.dst_lang
        return os.path.join(self.get_LogDir(), 'lock_file' + postfix_name + '.lock')

    def __make_lock_lang_file(self):
        pathfile = self.__get_path_lock_file__()
        if os.path.exists(pathfile):
            pass
        else:
            for ext in ['sql', 'dump', 'lock']:
                remove_files(self.get_LogDir(), ext)
            open(pathfile, 'w').close()
        return

    def ClearLogDir(self):
        pathdir = self.get_LogDir()
        if not os.path.exists(pathdir): return
        shutil.rmtree(pathdir)
        os.makedirs(pathdir)
        return

    def setRootPath(self, root_path):
        assert root_path != '', 'root_path is None'
        if not root_path: return

        self.RootPath = root_path
        self.create_directory(self.get_LogDir())
        print('\nUse directory for logging:', self.RootPath)
        return

    def extract_directory_from_file_path(self, file_path):
        directory_path = os.path.dirname(file_path)
        self.RootPath = directory_path
        return

    def get_LogDir(self):
        lng_postfix = '';
        if self.src_lang:
            lng_postfix = '_' + self.src_lang
        if self.dst_lang:
            lng_postfix = '_' + self.dst_lang
        if not self.RootPath:
            return None
        return os.path.join(self.RootPath, 'LogAlign')

    def create_directory(self, path):
        os.makedirs(path, exist_ok=True)
        return

    def getPathTxt_From(self):
        return os.path.join(self.get_LogDir(), 'from_part.txt')

    def getPathTxt_To(self):
        return os.path.join(self.get_LogDir(), 'to_part.txt')

    def getPathTextLinesDump(self):
        return os.path.join(self.get_LogDir(), 'all_text.dump')

    def getPath_DB_FullText(self):
        return os.path.join(self.get_LogDir(), 'db_full.sql')

    def getPath_DB_PartText(self):
        return os.path.join(self.get_LogDir(), 'db_part.sql')

    def generate_random_string(self, length):
        letters = string.ascii_letters
        result_str = ''.join(choice(letters) for i in range(length))
        return result_str

    def getRandomPath(self, prefix: str = None, ext: str = None):
        if not prefix: prefix = ''
        if not ext:
            ext = ''
        else:
            ext = '.' + ext
        res = prefix + self.generate_random_string(10) + ext
        res = os.path.join(self.get_LogDir(), res)
        return res

    def getPath_EmbDump(self):
        return os.path.join(self.get_LogDir(), 'embdump.dump')

    def getTmpPath(self, fname):
        return os.path.join(self.get_LogDir(), fname)

    def getPath2TextExtracted(self, pathInFile):
        fname = os.path.basename(pathInFile)
        return os.path.join(self.get_LogDir(), fname)

    def write_to_file(self, filename: str, text: typing.List[str]):
        with open(filename, 'w', encoding='utf-8') as f:
            text = [l + '\n' for l in text]
            f.writelines(text)
        return

    def getPathFileSanitazed(self, prefix) -> str:
        return os.path.join(self.get_LogDir(), prefix + '_sanitazed.txt')

    def getPathSummaryLog(self):
        return os.path.join(self.get_LogDir(), 'summary.log')

    def getPathDumpAllBookParts(self):
        return os.path.join(self.get_LogDir(), 'book_parts.dump')

    def getPathClearedPrologData(self):
        postfix_name = '_' + self.src_lang + '_' + self.dst_lang
        return os.path.join(self.get_LogDir(), postfix_name + '_cleared.dump')

    def getPathResAlignedParts(self):
        postfix_name = '_' + self.src_lang + '_' + self.dst_lang
        return os.path.join(self.get_LogDir(), postfix_name + '_res_aligned.dump')

    def getOutJsonFilePathFromOrig(self, pathfileOut: str) -> str:
        json_ext = '.json'
        if not pathfileOut.endswith(json_ext):
            pathfileOut += json_ext
        return pathfileOut
