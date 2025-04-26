import logging
from logging import Logger

import argparse
from pprint import pprint
import os, sys

from AlignerImproved.Settings import ConfigApp
from AlignerImproved.ConfigModel import ConfigAlignBook
from AlignerImproved.LoggerHelper import SingletonLoggerHelper
from AlignerImproved.LoggerCreation import getLogger4Run


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from AlignerImproved.Extarct_EPUB import extract_text_pipe as ReadEpub
from AlignerImproved.Extract_FB2 import extract_text_pipe as ReadFB2
from AlignerImproved.Extract_HTML import extract_text_pipe as ReadHTML
from AlignerImproved.Extract_PDF import Read_PDF
from AlignerImproved.LanguageDetect import detect_lang_4_file
from AlignerImproved.LogDebugHelper import LogDebugHelper

from dataclasses import asdict

from AlignerImproved.MainAligner import AlignBook

EXT_SUPPORTED=['txt','pdf','epub','fb2','html']


def check_file_extension(file_path)->str:
    # Use os.path.splitext to split the file path into name and extension
    name, extension = os.path.splitext(file_path)
    # Return the extension
    return extension.replace('.','').lower()


import shutil


def Prepare_Txt_File(file_src: str, file_dsc):
    # Copy the source file to the destination
    shutil.copy(file_src, file_dsc)
    return 

class CCmdTool:
    def __init__(self, isTestMode:bool=False,
                 isMakeOnlySanitizeData:bool=False,
                 logger:Logger=None,
                 ):
        self.isTestMode = isTestMode
        self.config: ConfigAlignBook = None

        self.Logger:Logger
        if logger:
            self.Logger = logger
        else:
            self.Logger:Logger = logging.getLogger('CmdAllignTool.log')
        if isTestMode:
            pass
        else:
            self.SetConfig( self.ArgParse() )
            self.config.IsMakeOnlySanitizeData = isMakeOnlySanitizeData
        return

    def SetConfig(self, config: ConfigAlignBook):
        if not config: return
        self.config = config

        path_dir_src = os.path.dirname( config.source_book_path )
        assert os.path.exists(config.source_book_path), f'Source file not exist. Possible not set current dir. Current value:{path_dir_src}'
        dir_path = os.path.dirname(config.output_book_path)
        dir_path = dir_path if len(dir_path)>0 else os.getcwd()
        logHlp:LogDebugHelper = LogDebugHelper( dir_path, src_lang=config.lng_src, dst_lang=config.lng_dest )
        self.Logger:Logger =  getLogger4Run( logHlp.get_LogDir() )
        return

    def ArgParse(self)-> ConfigAlignBook:
        parser = argparse.ArgumentParser(description='Process book paths.')
        parser.add_argument('--isSkipSanitizing', action='store_true', help='Skip sanitizing the book content.')
        parser.add_argument('--pathBookFrom', type=str, required=True,
                            help='The path to the source book file.')
        parser.add_argument('--pathBookTo', type=str, required=True,
                            help='The path to the destination book file.')
        parser.add_argument('--pathBookOut', type=str, required=True,
                            help='The path to the output book file.')
        parser.add_argument('--pathHomeDir', type=str, required=False,
                            help='The path home dir.')

        args = parser.parse_args()
        # Hereafter, you can use these parsed arguments like this:
        source_book_path = args.pathBookFrom
        destination_book_path = args.pathBookTo
        output_book_path = args.pathBookOut
        conf  = ConfigAlignBook(source_book_path, destination_book_path, output_book_path, args.isSkipSanitizing)
        return conf

    def readFileWrapper(self, file_path:str)->str:
        lghlp = LogDebugHelper(None)
        dir_path = os.path.dirname(file_path)
        if dir_path=='':
            dir_path = os.getcwd()
            print(f'Use current directory as root for logging: {dir_path}')
        lghlp.setRootPath( dir_path )
        out_file = lghlp.getPath2TextExtracted(file_path)
        ext_file = check_file_extension(file_path)
        if ext_file == 'epub':
            ReadEpub( file_path, out_file)
        elif ext_file == 'fb2':
            ReadFB2( file_path, out_file)
        elif ext_file == 'pdf':
            Read_PDF( file_path, out_file)
        elif ext_file == 'txt':
            Prepare_Txt_File(file_path, out_file)
        elif ext_file =='html':
            ReadHTML(file_path, out_file)
        else:
            raise Exception(f"File type '{ext_file}' not supported.")
        assert os.path.exists(out_file)
        return out_file

    def SetLogger(self, logger:Logger):
        self.Logger = logger
        global_logger = SingletonLoggerHelper()
        global_logger.SetLogger(logger)
        return

    def ProcessBooks(self):
        if not self.config: raise Exception('Config for working not setted')
        conf = self.config
        ext_src = check_file_extension(conf.source_book_path)
        ext_dest = check_file_extension(conf.dest_book_path)

        if ext_src not in EXT_SUPPORTED:
            print('The file extension is not supported:',ext_src)
            return
        if ext_dest not in EXT_SUPPORTED:
            print('The file extension is not supported:',ext_dest)
            return

        self.config.dest_book_txt_path = self.readFileWrapper(self.config.dest_book_path)
        self.config.src_book_txt_path = self.readFileWrapper(self.config.source_book_path)

        lng_dest = detect_lang_4_file(self.config.dest_book_txt_path)
        lng_src = detect_lang_4_file(self.config.src_book_txt_path)
        ConfigApp().setLange(lng_src, lng_dest)
        print(f'Language book src {lng_src} - {self.config.src_book_txt_path}')
        print(f'Language book src {lng_dest} - {self.config.dest_book_txt_path}')
        self.config.SetLangs(lng_src, lng_dest)
        LogDebugHelper().setLangInfo(lng_src, lng_dest)

        AlignBook( config=self.config, logger=self.Logger )
        return

def main():
    import sys
    print("Command line arguments:", sys.argv)

    cmdTool = CCmdTool()
    pprint( asdict(cmdTool.config) )
    cmdTool.ProcessBooks()
    return

if __name__ == "__main__":
    # This is where you can call your main function or do main processing
    main()
    pass
