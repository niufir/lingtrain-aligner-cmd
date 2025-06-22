import logging
import os,sys
from typing import Optional

from attr import dataclass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
sys.path.append(os.path.dirname(os.path.abspath(__file__)))



# test_my_module.py
import os.path

import json



import AlignerImproved.ConfigModel
from AlignerCmd import CCmdTool

from LogDebugHelper import LogDebugHelper



g_logger: logging.Logger = None

g_IS_REMOVE_OLD:bool = False

def getLogger() -> logging.Logger:
    global g_logger
    if g_logger is not None:
        return g_logger

    log_dir = os.path.join(get_file_current_file_directory(), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = logging.FileHandler(os.path.join(log_dir, 'log_testing.log'), encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # Create a logger with a unique name
    g_logger = logging.getLogger('Test_Aligner')
    g_logger.setLevel(logging.INFO)  # Set the log level at the logger level

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    g_logger.addHandler(file_handler)
    g_logger.addHandler(console_handler)

    return g_logger


def get_file_current_file_directory() -> str:
    current_file_path = os.path.abspath(__file__)
    return os.path.dirname(current_file_path)

def readTextFile(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        contents = file.read()
    return [l for l in contents.split('\n') if len(l)>0]


def load_json_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File at {file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file at {file_path}.")
    return None


def add(a, b):
    return a + b


g_logger: logging.Logger = None

@dataclass
class Config4Test:
    path_root:str = None
    path_src:str  =None
    path_dst:str=None
    path_out:str=None
    src_lang:str=None
    dst_lang:str=None
    config: Optional[AlignerImproved.ConfigModel.ConfigAlignBook]=None
    __logHlp:Optional[LogDebugHelper] = None

    def post_init(self):
        self.validate()
        self.config = AlignerImproved.ConfigModel.ConfigAlignBook(source_book_path=self.path_src,
                                                             dest_book_path=self.path_dst,
                                                             output_book_path=self.path_out)
        self.config.SetLangs(self.src_lang, self.dst_lang)
        self.config.IsMakeOnlySanitizeData = True
        return self

    def setIsMakeOnlySanitizeData(self, isMakeOnlySanitizeData:bool = True):
        self.config.IsMakeOnlySanitizeData = isMakeOnlySanitizeData
        return

    def validate(self):
        assert os.path.exists(self.path_src)
        assert os.path.exists(self.path_dst)
        return

    def makeLogHelper(self)->LogDebugHelper:
        if self.__logHlp is None:
            logHlp = LogDebugHelper(self.path_root, src_lang=self.src_lang, dst_lang=self.dst_lang)
            logHlp.init(root_path=self.path_root, src_lang=self.src_lang, dst_lang=self.dst_lang)
            self.__logHlp = logHlp
            return  logHlp
        else:
            return self.__logHlp


def run_extract_book(config4test: Config4Test, logger:logging.Logger):
        logHlp = config4test.makeLogHelper()
        config = config4test.config
        logger.debug(f'Start with book {config4test.path_root}')
        if g_IS_REMOVE_OLD:
            logHlp.ClearLogDir()
        if os.path.exists(logHlp.getOutJsonFilePathFromOrig(  config.output_book_path ) ):
            os.remove(logHlp.getOutJsonFilePathFromOrig(config.output_book_path))
        # assert len( os.listdir(logHlp.get_LogDir()) ) ==0, "Directory is not empty"
        assert not os.path.exists(
            logHlp.getOutJsonFilePathFromOrig(config.output_book_path)), 'File exists, must be removed'
        cmdTool = CCmdTool(isTestMode=True, logger=getLogger())
        cmdTool.SetConfig(config)
        cmdTool.ProcessBooks()
        return



def remove_Align_result_files(config, logHlp:LogDebugHelper = None):
    if os.path.exists(logHlp.getOutJsonFilePathFromOrig(config.output_book_path)):
        os.remove(logHlp.getOutJsonFilePathFromOrig(config.output_book_path))
    assert not os.path.exists(
        logHlp.getOutJsonFilePathFromOrig(config.output_book_path)), 'File exists, must be removed'

def test_bookAligner_1():
    global g_logger
    g_logger = getLogger()
    g_logger.debug(f"Start test BookAligner")
    path_root= path_root= os.path.join(get_file_current_file_directory(),r'TestData\DorianGrey' ) # r'/src/AlignerImproved/TestData/DorianGrey'
    def makeConfig():
        path_src = os.path.join(path_root,'en.epub')
        path_dst = os.path.join(path_root,'ru.epub')
        path_out = os.path.join(path_root,'out.txt')

        assert os.path.exists(path_src)
        assert os.path.exists(path_dst)

        config = AlignerImproved.ConfigModel.ConfigAlignBook(source_book_path = path_src,
                                                                 dest_book_path = path_dst,
                                                                 output_book_path = path_out)
        config.SetLangs('en', 'ru')

        return config

    config: AlignerImproved.ConfigModel.ConfigAlignBook = makeConfig()
    logHlp = LogDebugHelper( path_root, src_lang='en', dst_lang='ru' )

    def run_extract_book(config: AlignerImproved.ConfigModel.ConfigAlignBook):
        g_logger.info(f'Start with book {path_root}')
        if  g_IS_REMOVE_OLD:
            logHlp.ClearLogDir()
            assert len( os.listdir(logHlp.get_LogDir()) ) ==0, "Directory is not empty"

        remove_Align_result_files(config, logHlp)
        cmdTool = CCmdTool(isTestMode=True, logger=getLogger())
        cmdTool.SetConfig(config)
        cmdTool.ProcessBooks()
        return


    run_extract_book(config)

    # test results
    path_tmp_sanitized_from = logHlp.getPathFileSanitazed('from')
    path_tmp_sanitized_to = logHlp.getPathFileSanitazed('to')
    text_from = readTextFile(path_tmp_sanitized_from)
    text_to = readTextFile(path_tmp_sanitized_to)

    g_logger.info(f"section start test_from {text_from[0]}")
    assert 'The artist is the creator of beautiful things.'.lower() in '\n'.join(text_from[:10]).lower()
    assert  'It was not till they had examined the rings that they recognised who it was' in '\n'.join(text_from[-2:])
    g_logger.info(f"section start test_to {text_to[0]}")

    txt_to_start = '\n'.join(text_to[:6])
    assert ('Художник – человек, создающий прекрасное.' in txt_to_start) or ('Портрет Дориана Грея' in txt_to_start)
    assert  'Слуги поняли, кто перед ними, только благодаря кольцам на пальцах мертвеца' in '\n'.join(text_to[-6:])

    pathRes_Json = logHlp.getOutJsonFilePathFromOrig(config.output_book_path)
    assert os.path.exists(pathRes_Json)
    jsonData = load_json_from_file(pathRes_Json)
    data_items = jsonData['data_forward_langs_direction']
    assert len(data_items) >5750

    text_from_align_items = '\n'.join([i['txt_from'] for i in data_items[:5]])
    assert 'The Picture of Dorian Gray' in text_from_align_items

    txt_to_start = '\n'.join( [i['txt_to'] for i in data_items[:10]] )
    assert  'Художник – человек, создающий прекрасное' in txt_to_start

    assert  'It was not till they had examined the rings that they recognised who it was' in  '\n'.join( [ i['txt_from'] for i in data_items[-3:]] )
    assert 'Слуги поняли, кто перед ними, только благодаря кольцам на пальцах мертвеца' in '\n'.join( [ i['txt_to'] for i in data_items[-5:] ] )


    g_logger.info(f'~~~~ End with book {path_root}')
    return

def test_bookAligner_2():
    logger = getLogger()
    logger.debug(f"Debug Start test BookAligner")
    logger.info(f"Info Start test BookAligner")
    path_root= os.path.join(get_file_current_file_directory(),r'TestData\ShagrenevSkin_EN_RU' )# r'/src/AlignerImproved/TestData/ShagrenevSkin_EN_RU'
    def makeConfig():
        path_src = os.path.join(path_root,'en.epub')
        path_dst = os.path.join(path_root,'ru.epub')
        path_out = os.path.join(path_root,'out.txt')

        assert os.path.exists(path_src)
        assert os.path.exists(path_dst)

        config = AlignerImproved.ConfigModel.ConfigAlignBook(source_book_path = path_src,
                                                                 dest_book_path = path_dst,
                                                                 output_book_path = path_out)
        config.SetLangs('en', 'ru')
        config.IsMakeOnlySanitizeData = True
        return config

    config: AlignerImproved.ConfigModel.ConfigAlignBook = makeConfig()
    logHlp = LogDebugHelper( path_root, src_lang='en', dst_lang='ru' )
    logHlp.init(root_path = path_root, src_lang='en', dst_lang='ru')

    def run_extract_book(config: AlignerImproved.ConfigModel.ConfigAlignBook):
        logger.debug(f'Start with book {path_root}')
        if  g_IS_REMOVE_OLD:
            logHlp.ClearLogDir()
        if os.path.exists(logHlp.getOutJsonFilePathFromOrig(config.output_book_path)):
            os.remove(logHlp.getOutJsonFilePathFromOrig(config.output_book_path))
        #assert len( os.listdir(logHlp.get_LogDir()) ) ==0, "Directory is not empty"
        assert not os.path.exists(logHlp.getOutJsonFilePathFromOrig(config.output_book_path)),'File exists, must be removed'
        cmdTool = CCmdTool(isTestMode=True, logger=getLogger())
        cmdTool.SetConfig(config)
        cmdTool.ProcessBooks()
        return

    run_extract_book(config)

    config: AlignerImproved.ConfigModel.ConfigAlignBook = makeConfig()
    logHlp = LogDebugHelper( path_root, src_lang='en', dst_lang='ru' )

    path_tmp_sanitized_from = logHlp.getPathFileSanitazed('from')
    path_tmp_sanitized_to = logHlp.getPathFileSanitazed('to')
    text_from = readTextFile(path_tmp_sanitized_from)
    text_to = readTextFile(path_tmp_sanitized_to)


    assert 'go to the Opera this evening, and if you like to take it so, she is Society'.lower() in  '\n'.join(text_from[-3:]).lower()
    logger.info("\n~~~ first sentences from_to:" + '\n'.join(text_from[:8 ] ))
    logger.info("\n~~~ first sentences text_to:" + '\n'.join(text_to[:18]))
    assert 'Towards the end of the month of October 1829 a young'.lower() in '\n'.join(text_from[:17 ]).lower()
    assert 'сегодня будет в Опере, она везде'.lower() in '\n'.join(text_to[-7:]).lower()
    assert 'В конце октября 1829 года один молодой человек вошел в Пале-Руаяль'.lower() in '\n'.join(text_to[:13]).lower()
    return

def test_bookAligner_3():
    logger = init_logger()
    path_root = os.path.join(get_file_current_file_directory(),
                             r'TestData\Prince')  # r'/src/AlignerImproved/TestData/ShagrenevSkin_EN_RU'

    def makeConfig():
        path_src = os.path.join(path_root, 'Prince_en.pdf')
        path_dst = os.path.join(path_root, 'Prince_ru.epub')
        path_out = os.path.join(path_root, 'out.txt')

        assert os.path.exists(path_src)
        assert os.path.exists(path_dst)

        config = AlignerImproved.ConfigModel.ConfigAlignBook(source_book_path=path_src,
                                                             dest_book_path=path_dst,
                                                             output_book_path=path_out)
        config.SetLangs('en', 'ru')
        config.IsMakeOnlySanitizeData = True
        return config

    config: AlignerImproved.ConfigModel.ConfigAlignBook = makeConfig()
    logHlp = LogDebugHelper(path_root, src_lang='en', dst_lang='ru')
    logHlp.init(root_path=path_root, src_lang='en', dst_lang='ru')
    config.IsMakeOnlySanitizeData = True

    def run_extract_book(config: AlignerImproved.ConfigModel.ConfigAlignBook):
        logger.debug(f'Start with book {path_root}')
        if g_IS_REMOVE_OLD:
            logHlp.ClearLogDir()
        if os.path.exists(logHlp.getOutJsonFilePathFromOrig(config.output_book_path)):
            os.remove(logHlp.getOutJsonFilePathFromOrig(config.output_book_path))
        # assert len( os.listdir(logHlp.get_LogDir()) ) ==0, "Directory is not empty"
        assert not os.path.exists(
            logHlp.getOutJsonFilePathFromOrig(config.output_book_path)), 'File exists, must be removed'
        cmdTool = CCmdTool(isTestMode=True, logger=getLogger())
        cmdTool.SetConfig(config)
        cmdTool.ProcessBooks()
        return

    run_extract_book(config)

    config: AlignerImproved.ConfigModel.ConfigAlignBook = makeConfig()
    logHlp = LogDebugHelper(path_root, src_lang='en', dst_lang='ru')
    logHlp.init(root_path=path_root, src_lang='en', dst_lang='ru')

    path_tmp_sanitized_from = logHlp.getPathFileSanitazed('from')
    path_tmp_sanitized_to = logHlp.getPathFileSanitazed('to')
    text_from = readTextFile(path_tmp_sanitized_from)
    text_to = readTextFile(path_tmp_sanitized_to)

    print('Chick 1 -->')
    assert 'People trying to attract the good will of a sovereign usually'.lower() in '\n'.join(
        text_from[:3]).lower()
    print('Chick 2 -->')
    assert 'and under your protection Petrarch’s words be fulﬁlled'.lower() in '\n'.join(text_from[-8:]).lower()
    print('Chick 3 -->')
    assert 'Никколо Макиавелли Его Светлости Лоренцо Медичи'.lower() in '\n'.join(text_to[:3]).lower()
    print('Chick 4 -->')
    assert 'что живёт в италийском стане'.lower() in '\n'.join(
        text_to[-4:]).lower()
    return



def test_BookAligner_v4():
    logger = init_logger()
    path_root = os.path.join(get_file_current_file_directory(),
                             r'TestData\Alice_da_ru')  # r'/src/AlignerImproved/TestData/ShagrenevSkin_EN_RU'

    src_lang = 'da'
    dst_lang = 'ru'
    def makeConfig():
        path_src = os.path.join(path_root, 'da.epub')
        path_dst = os.path.join(path_root, 'RU.epub')
        path_out = os.path.join(path_root, 'out.txt')

        assert os.path.exists(path_src)
        assert os.path.exists(path_dst)

        config = AlignerImproved.ConfigModel.ConfigAlignBook(source_book_path=path_src,
                                                             dest_book_path=path_dst,
                                                             output_book_path=path_out)
        config.SetLangs(src_lang, dst_lang)
        config.IsMakeOnlySanitizeData = True
        return config

    config: AlignerImproved.ConfigModel.ConfigAlignBook = makeConfig()
    logHlp = LogDebugHelper(path_root, src_lang=src_lang, dst_lang=dst_lang)
    logHlp.init(root_path=path_root, src_lang=src_lang, dst_lang=dst_lang)
    config.IsMakeOnlySanitizeData = True

    def run_extract_book(config: AlignerImproved.ConfigModel.ConfigAlignBook):
        logger.debug(f'Start with book {path_root}')
        if g_IS_REMOVE_OLD:
            logHlp.ClearLogDir()
        if os.path.exists(logHlp.getOutJsonFilePathFromOrig(config.output_book_path)):
            os.remove(logHlp.getOutJsonFilePathFromOrig(config.output_book_path))
        # assert len( os.listdir(logHlp.get_LogDir()) ) ==0, "Directory is not empty"
        assert not os.path.exists(
            logHlp.getOutJsonFilePathFromOrig(config.output_book_path)), 'File exists, must be removed'
        cmdTool = CCmdTool(isTestMode=True, logger=getLogger())
        cmdTool.SetConfig(config)
        cmdTool.ProcessBooks()
        return

    run_extract_book(config)

    path_tmp_sanitized_from = logHlp.getPathFileSanitazed('from')
    path_tmp_sanitized_to = logHlp.getPathFileSanitazed('to')
    text_from = readTextFile(path_tmp_sanitized_from)
    text_to = readTextFile(path_tmp_sanitized_to)

    print('Chick 2 -->')
    assert 'mindes sin egen barndom og dens lykkelige sommerdage'.lower() in '\n'.join(text_from[-4:]).lower()
    return

def test_aligner_synt1_V5():
    logger = init_logger()
    path_root = os.path.join(get_file_current_file_directory(),
                             r'TestData\Test_Align_Sync1')  # r'/src/AlignerImproved/TestData/ShagrenevSkin_EN_RU'
    config4Test = Config4Test(path_root = path_root, src_lang = 'ge', dst_lang = 'ru',
                              path_dst=os.path.join(path_root, 'balzak_betta_ru.txt'),
                              path_src=os.path.join(path_root, 'balzak_betta_de.txt'),
                              path_out=os.path.join(path_root, 'out.txt'), config=None ).post_init()
    config4Test.setIsMakeOnlySanitizeData()

    logHlp = config4Test.makeLogHelper()
    run_extract_book(config4Test, logger=logger)

    path_tmp_sanitized_from = logHlp.getPathFileSanitazed('from')
    path_tmp_sanitized_to = logHlp.getPathFileSanitazed('to')
    text_from = readTextFile(path_tmp_sanitized_from)
    text_to = readTextFile(path_tmp_sanitized_to)

    print('Chick  -->')
    assert "Balzac verachtete den Bourgeois, aber diese Abneigung entsprang" in '\n'.join(text_from[:10])
    return


def init_logger():
    logger = getLogger()
    logger.debug(f"Debug Start test BookAligner")
    logger.info(f"Info Start test BookAligner")
    return logger

