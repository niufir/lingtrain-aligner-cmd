import logging

import numpy as np
import sys

import os

from src.AlignerImproved.PayloadModels.CBookSplitSection import BookSplitSection
from src.lingtrain_aligner.Settings import GetAppSettings, SetDefModelName
from src.lingtrain_aligner.HelperParagraphSpliter import HelperParagraphSpliter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from AlignBookItemResult import AlignBookItemResult
from ConfigModel import ConfigAlignBook
from ExportTextsHelper import ExportTextsHelper
from LogDebugHelper import LogDebugHelper
from LoggerHelper import  SingletonLoggerHelper
from PayloadModels.CTextAlignItem import CTextAlignItem
from HelperBookSplitter  import CHelperBookSplitter

import joblib

from scipy.spatial import distance

try:
        from ..lingtrain_aligner import preprocessor, splitter, aligner, resolver, reader, helper, vis_helper
except:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from lingtrain_aligner import preprocessor, splitter, aligner, resolver, reader, helper, vis_helper
        pass



import typing
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

from CBookConfig import BookConfig
from ParagraphMaker import *
from CHelperClearnPrologs import CHelper_CleanerTexts



gLogger:SingletonLoggerHelper = SingletonLoggerHelper()
g_LogHlp:LogDebugHelper = None


def getPath_change_file_extension(file_path, new_extension='txt'):
    base = os.path.splitext(file_path)[0]
    new_file_path = base +'.'+ new_extension
    return new_file_path

gBookConfig: BookConfig = None
def setBookData(pathLngSrc:str,
                pathLngDst:str,
                pathFileOut:str,
                lng_src:str,
                lng_dst:str):
    global gBookConfig
    conf = BookConfig(
        pathLngSrc=pathLngSrc,
        pathLngDst=pathLngDst,
        pathFileOut=pathFileOut,
        lng_abr_src=lng_src,
        lng_abr_dst=lng_dst,
    )
    gBookConfig = conf
    return



def makeBookConfig()->BookConfig:
    if gBookConfig is None:
        raise Exception("Default BookConfig is not support")
        book1 = BookConfig(pathLngSrc=r"" ,
                           pathLngDst=r"" ,
                           lng_abr_src = r"en",
                           lng_abr_dst = r"ru",
                           pathFileOut = r""
                           )
        return book1
    else: return gBookConfig
    return


def formarPrintableText(line_store:typing.List[str])->str:
        res = ( ' '.join(line_store).replace('%%%%%.','')
                .replace('%%%%%?','')
                .replace('%%%%%%%%%%%%%%%','\n\n')
                .replace('%%%%%','\n')
                )

        return res

def formarPrintableTextLine(line:str)->str:
    res = ( line.replace('%%%%%.','')
            .replace('%%%%%?','')
            .replace('%%%%%%%%%%%%%%%','\n\n')
            .replace('%%%%%','\n')
            )

    return res


def save_aligng3file_depr(res_aligns:typing.List[CTextAlignItem], path_file:str):
        print('Save aliging data to file:', path_file)
        with (open(path_file, 'w', encoding='utf-8' ) as f):
            for item in res_aligns:
                p_from, p_to  = item.txt_from, item.txt_to
                p_from = formarPrintableTextLine(p_from)

                p_to = formarPrintableTextLine(p_to)
                f.write(f'[{item.isValid}]\n')
                f.write(p_from)
                f.write('\n')
                f.write(p_to)
                f.write('\n\n')
        return


def ReadBookFromConfig(book1:BookConfig)->typing.Tuple[typing.List[str], typing.List[str]]:
    text1 = book1.openSrcBook().read().replace('\xa0', ' ')
    text2 = book1.openDstBook().read().replace('\xa0', ' ')
    print('len text1', len(text1))
    print('len text2', len(text2))
    text1 = text1.split("\n")
    text2 = text2.split('\n')
    text1 = [transformChapterLine(l) for l in text1]
    text1 = [splitStringByPoints(l) for l in text1]
    text2 = [transformChapterLine(l) for l in text2]
    text2 = [splitStringByPoints(l) for l in text2]
    print('count lines text1', len(text1))
    print('count lines text2', len(text2))
    return text1, text2




def getDbPath()->str:
    return 'full_db.sql'

def write_to_file(filename, text):
    gLogger.Trace('Write data to tile ' + filename)
    with open(filename, 'w', encoding='utf-8') as f:
        text = [l +'\n' for l in text]
        f.writelines(text)
    return


import typing
def splitTextOnSmallParts(text1:typing.List[str],
                          text2:typing.List[str],
                          book1:BookConfig,
                          db_path_tmp:str = None,
                          emb_store:typing.Dict[str, typing.List] = None,
                          )->typing.List:
    global db_path

    lang_from = book1.lng_abr_src
    lang_to = book1.lng_abr_dst

    text1_prepared = preprocessor.mark_paragraphs(text1)
    text2_prepared = preprocessor.mark_paragraphs(text2)

    splitted_from = splitter.split_by_sentences_wrapper(text1_prepared, lang_from)
    splitted_to = splitter.split_by_sentences_wrapper(text2_prepared, lang_to)

    db_path4work = book1.pathFileOut+'.sql'
    if os.path.isfile(db_path4work):
        os.unlink(db_path4work)

    aligner.fill_db(db_path4work, lang_from, lang_to, splitted_from, splitted_to)

    batchsize = 300
    batchlist = list( range( int( len(splitted_to)//batchsize) +2 ) )
    # batch_ids = [0,1]

    aligner.align_db(db_path4work, \
                     g_Model_Name, \
                     batch_size=batchsize, \
                     window=80, \
                     batch_ids=batchlist, \
                     save_pic=False,
                     embed_batch_size=10, \
                     normalize_embeddings=True, \
                     show_progress_bar=True,
                     emb_store=emb_store,
                     )

    conflicts_to_solve, rest = resolver.get_all_conflicts(db_path4work, min_chain_length=2, max_conflicts_len=6, batch_id=-1)

    #resolver.get_statistics(conflicts_to_solve)
    #resolver.get_statistics(rest)

    steps = 3
    batch_id = -1 #выровнять все доступные батчи

    for i in range(steps):
        conflicts, rest = resolver.get_all_conflicts(db_path4work, min_chain_length=2+i, max_conflicts_len=6*(i+1), batch_id=batch_id)
        resolver.resolve_all_conflicts(db_path4work, conflicts, g_Model_Name, show_logs=False)

        """
        vis_helper.visualize_alignment_by_db(db_path, output_path="img_test1.png", lang_name_from=lang_from, lang_name_to=lang_to, batch_size=400, size=(600,600), plt_show=True)
        """

        if len(rest) == 0: break
    paragraphs_from, paragraphs_to, meta,sent_counter_dict  = reader.get_paragraphs(db_path4work)
    res = []
    for p_from , p_to in zip( paragraphs_from['from'], paragraphs_from['to'] ):
        res.append(CTextAlignItem(p_from, p_to))

    return res

def sanitizeMarkers(line:str)->str:
        rres = line.replace('%%%%%','')
        return rres



def processSmallPart(book1:BookConfig,text1_prepared, text2_prepared,
                     emb_store:typing.Dict, index_part:int )->AlignBookItemResult:

    db_path = g_LogHlp.getRandomPath( 'db_local','sql' )# 'local_db.sql'
    lang_from = book1.lng_abr_src
    lang_to = book1.lng_abr_dst
    text1_prepared = preprocessor.mark_paragraphs(text1_prepared)
    text2_prepared = preprocessor.mark_paragraphs(text2_prepared)

    splitted_from_all = splitter.split_by_sentences_wrapper(text1_prepared, book1.lng_abr_src)
    splitted_to_all = splitter.split_by_sentences_wrapper(text2_prepared, book1.lng_abr_dst)
    if os.path.isfile(db_path):
        os.unlink(db_path)

    aligner.fill_db(db_path, book1.lng_abr_src, book1.lng_abr_dst, splitted_from_all, splitted_to_all)

    batch_size=300
    batchlist = list( range( int( len(splitted_to_all)//batch_size) +2 ) )


    #batch_size=300
    batch_ids = batchlist#[0, 1, 2, 3]
    #[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,24]

    aligner.align_db(db_path,
                     GetAppSettings().m_Model_Name,
                     batch_size=batch_size,
                     window=100,
                     batch_ids=batch_ids,
                     save_pic=False,
                     embed_batch_size=10,
                     normalize_embeddings=True,
                     show_progress_bar=True,
                     emb_store=emb_store
                     #emb_store=None
                     )

    #vis_helper.visualize_alignment_by_db(db_path, output_path="alignment_vis.png", lang_name_from=lang_from, lang_name_to=lang_to, batch_size=400, size=(800,800), plt_show=True)

    conflicts_to_solve, rest = resolver.get_all_conflicts(db_path, min_chain_length=2, max_conflicts_len=6, batch_id=-1)

    resolver.get_statistics(conflicts_to_solve)
    resolver.get_statistics(rest)
    steps = 2
    batch_id = -1 #выровнять все доступные батчи

    for i in range(steps):
        conflicts, rest = resolver.get_all_conflicts(db_path, min_chain_length=2+i, max_conflicts_len=6*(i+1), batch_id=batch_id)
        resolver.resolve_all_conflicts(db_path, conflicts, GetAppSettings().m_Model_Name, show_logs=False, emb_store=emb_store)
        #vis_helper.visualize_alignment_by_db(db_path, output_path="img_test1.png", lang_name_from=lang_from, lang_name_to=lang_to, batch_size=400, size=(600,600), plt_show=True)

        if len(rest) == 0: break


    paragraphs_from, paragraphs_to, meta,sent_counter_dict  = reader.get_paragraphs(db_path)
    ix =0
    def makeAlignsDirectly(paragraphs)->typing.List[CTextAlignItem]:
        res = []
        for  p_from , p_to in zip(paragraphs['from'], paragraphs['to']):
            if isinstance(p_from, list):
                p_from = '. '.join(p_from)
            if isinstance(p_to, list):
                p_to = '. '.join(p_to)
            res.append(CTextAlignItem(p_from, p_to))
        return res

    def MakeHTMLBook(paragraphs_from,paragraphs_to, meta,sent_counter_dict, pathOut):
        reader.create_book(paragraphs=paragraphs_from,
                           lang_ordered=['from','to'],
                           delimeters=paragraphs_to,
                           metas=meta,
                           sent_counter=sent_counter_dict,
                           output_path=pathOut,
                           template="none" )
        print("Create html book with path", pathOut)
        return

    def isNeedSplitParagraph(paragraph:typing.List[str]) -> bool:
        return False;
        words = nltk.word_tokenize(' '.join( paragraph ))
        # print(len(words), ' => ', len(set( words )) )
        return len(set( words ))>=50


    large_blocks:typing.List[CTextAlignItem] = makeAlignsDirectly(paragraphs_from)
    ExportTextsHelper.save_aligng3file(large_blocks, book1.pathFileOut)

    # Mark align parts as wrong
    stat_err_from_len = MarkingWrongErrorsItems(db_path, lang_from, lang_to, large_blocks, splitted_from_all)

    res_aligns:typing.List[CTextAlignItem] = []

    #for p_from , p_to in tqdm(zip( paragraphs_from['from'], paragraphs_from['to'] ), total=len(paragraphs_from['from'])):
    for p_from , p_to, item_block in tqdm(zip( paragraphs_from['from'], paragraphs_from['to'],large_blocks ), total=len(paragraphs_from['from'])):
        item_block: CTextAlignItem = item_block
        if (item_block.isValid)and(isNeedSplitParagraph(p_from)):
            splitted_from = splitter.split_by_sentences_wrapper(p_from, book1.lng_abr_src)
            splitted_to = splitter.split_by_sentences_wrapper(p_to, book1.lng_abr_dst)
            try:
                paragraps_news = splitTextOnSmallParts( splitted_from,
                                                        splitted_to,
                                                        book1,
                                                        "rdtmpdb.sql" ,
                                                        emb_store=emb_store)
                res_aligns += paragraps_news[:]
                pass
            except:
                res_aligns.append(CTextAlignItem('. '.join(p_from), '. '.join(p_to)))
        else:
            res_aligns.append(CTextAlignItem('. '.join(p_from), '. '.join(p_to), isValid=item_block.isValid))

    ExportTextsHelper.save_aligng3file(res_aligns,book1.pathFileOut)
    MakeHTMLBook(paragraphs_from,
                 paragraphs_to,meta,
                 sent_counter_dict,
                 getPath_change_file_extension(book1.pathFileOut, 'html')
                 )

    validation_info, error_index_log = vis_helper.validHlp_IdsMergeStore(db_path)


    stat_err_to_len = 0

    if validation_info>5:
        if False:
            vis_helper.visualize_alignment_by_db(db_path,
                                                 output_path= os.path.join(g_LogHlp.get_LogDir(), "alignment_vis.png"),
                                                 lang_name_from=book1.lng_abr_src,
                                                 lang_name_to=book1.lng_abr_dst,
                                                 batch_size=400, size=(800,800), plt_show=True)

        path_err_log = os.path.join(g_LogHlp.RootPath,'errors.txt')
        print('Write errors in file ', path_err_log)
        with open( path_err_log, 'w', encoding='utf8') as f:
            for ix_err in error_index_log:
                try:
                    f.write( '~~~~~~~~~~\n' + '\n'.join(paragraphs_from['from'][ix_err[0]]) +'\n'+ ''.join(paragraphs_from['to'][ix_err[0]]) + '\n')
                except Exception as e:
                    pass

    AddDistancesToAlignItems(emb_store, res_aligns)

    print('Data saved',book1.pathFileOut)
    alres = AlignBookItemResult()
    alres.setAlignData(res_aligns)
    gLogger.logToSummary( f'part index:{index_part}\t Errors percent = {validation_info}%\tsize_from={stat_err_from_len}\tsize_to={stat_err_to_len}')
    return alres


def MarkingWrongErrorsItems(db_path, lang_from, lang_to, large_blocks, splitted_from_all):
    stat_err_from_len = 0
    err_perc, ix_list = vis_helper.validHlp_IdsMergeStore(db_path)
    for ix_wrong_from, _ in ix_list:
        ix_wrong_from = ix_wrong_from
        if ix_wrong_from >= len(splitted_from_all):
            continue
        text_wrong = splitted_from_all[ix_wrong_from]
        print(ix_wrong_from, text_wrong)
        txt_4_check = sanitizeMarkers(text_wrong)
        item_4_wrong = [itm for itm in large_blocks if txt_4_check in itm.txt_from]
        if len(item_4_wrong) > 0:
            item_4_wrong = item_4_wrong[0]
            item_4_wrong.setWrong()
            stat_err_from_len += len(' '.join(item_4_wrong.txt_from))
    return stat_err_from_len


def AddDistancesToAlignItems(emb_store, res_aligns):
    print('Add distances in align items')
    for ix in tqdm( range(len(res_aligns)) ):
        item: CTextAlignItem = res_aligns[ix]
        hash_from = calculate_sha1(item.txt_from)
        hash_to = calculate_sha1(item.txt_to)
        if hash_from not in emb_store:
            tmp_emb_res=[]
            aligner.getEmb4Part([item.txt_from], tmp_emb_res, isShowProgress=False)
            item_emb_from = tmp_emb_res[0][0]
        else:
            item_emb_from = emb_store[hash_from]
        if hash_to not in emb_store:
            tmp_emb_res =[]
            aligner.getEmb4Part([item.txt_to],tmp_emb_res, isShowProgress=False)
            item_emb_to = tmp_emb_res[0][0]

        else:
            item_emb_to = emb_store[hash_to]

        cosd = distance.cosine(item_emb_from, item_emb_to)
        manhd = distance.cityblock(item_emb_from, item_emb_to)
        item.setDistances(cosd, manhd)
    return res_aligns


def makeResultBookFromParts(data:typing.List[AlignBookItemResult]):

    if not data:
        data = joblib.load(g_LogHlp.getPathDumpAllBookParts())
    assert isinstance(data[0],AlignBookItemResult), f'Current type {type(data)} is not AlignBookItemResult'
    cumul_book = []
    book_cfg = makeBookConfig()
    for item in data:
        cumul_book+=item.AlignData[:]
    #print(data[0])
    print('Save result to file: ', book_cfg.pathFileOut)
    ExportTextsHelper.exportAsJson_v1(cumul_book, g_LogHlp.getOutJsonFilePathFromOrig(book_cfg.pathFileOut)  )
    ExportTextsHelper.save_aligng3file(cumul_book, book_cfg.pathFileOut)
    #save_aligng3file(cumul_book, book_cfg.pathFileOut)
    return


def AlignBook(
              config:ConfigAlignBook,
            logger:logging.Logger=None
              ):
    global g_LogHlp
    global gLogger


    pathLngSrc:str = config.src_book_txt_path
    pathLngDst:str = config.dest_book_txt_path
    pathFileOut:str = config.output_book_path
    lng_src:str = config.lng_src
    lng_dst:str = config.lng_dest
    assert os.path.exists(pathLngSrc),f'Path not exist {pathLngSrc}'
    assert os.path.exists(pathLngDst), f'Path not exist {pathLngDst}'
    assert lng_src != lng_dst
    assert lng_src is not None and lng_dst is not None

    gLogger = SingletonLoggerHelper()
    gLogger.SetLogger(logger)
    gLogger.Info('Run AlignBook')

    if pathLngSrc:
        setBookData(pathLngSrc = pathLngSrc,
                        pathLngDst= pathLngDst,
                        pathFileOut = pathFileOut,
                        lng_src = lng_src,
                    lng_dst = lng_dst)
    book1:BookConfig = makeBookConfig()
    dir_path = os.path.dirname(book1.pathFileOut)
    dir_path = dir_path if len(dir_path)>0 else os.getcwd()
    logHlp = LogDebugHelper( dir_path, src_lang=lng_src, dst_lang=lng_dst )
    g_LogHlp = logHlp
    if config.IsTestMode: g_LogHlp.ClearLogDir()

    SetDefModelName(GetAppSettings().m_Model_Name)

    gLogger.setPathSummaryLog(g_LogHlp.getPathSummaryLog() )
    gLogger.info(f'Root path for log data: {logHlp.RootPath}' )
    gLogger.logToSummary(f'\n~~~ Start Process Book {lng_src}:{lng_dst}~~~')
    gLogger.logToSummary(f'Path out file->{pathFileOut}')
    gLogger.logToSummary(f'\t\t with langs: {lng_src}<->{lng_dst}')

    text1, text2  = ReadBookFromConfig(book1)
    text1_prepared = preprocessor.mark_paragraphs(text1)
    text2_prepared = preprocessor.mark_paragraphs(text2)

    splitted_from:typing.List[str] = splitter.split_by_sentences_wrapper(text1_prepared, book1.lng_abr_src)
    splitted_to:typing.List[str] = splitter.split_by_sentences_wrapper(text2_prepared, book1.lng_abr_dst)
    # splitted_from = [i.replace('%%%%%','') for i in splitted_from]
    # splitted_to = [i.replace('%%%%%','') for i in splitted_to]
    joblib.dump([splitted_from, splitted_to], logHlp.getPathTextLinesDump())

    name_emb_dump = logHlp.getPath_EmbDump()
    db_path, emb = MakeEmbidings(book1, logHlp, name_emb_dump, splitted_from, splitted_to)

    pathDump = logHlp.getPathClearedPrologData()

    if False:
        if config.isSkipSanitize:
            joblib.dump([emb[0], emb[1], splitted_from, splitted_to], pathDump)
            emb_1, emb2, splitted_from, splitted_to = emb[0], emb[1], splitted_from, splitted_to
        elif not os.path.exists(pathDump) or True:
            emb2, emb_1, splitted_from, splitted_to = ClearPrologEpilogFromBook(emb, logHlp, splitted_from, splitted_to)
            joblib.dump([emb2, emb_1, splitted_from, splitted_to], pathDump)
        else:
            gLogger.info('Load cleared text from files')
            emb2, emb_1, splitted_from, splitted_to = joblib.load( pathDump )
        assert emb_1.shape[1] == GetAppSettings().EMB_SHAPE_VALUE, "Error, possible use different models in config and in loading embidings"
        if config.IsMakeOnlySanitizeData:
            gLogger.Info("Stop process book - set flaf IsMakeOnlySanitizeData")
            return
    else:
        emb2, emb_1, splitted_from, splitted_to = joblib.load(pathDump)

    aligner.fill_db(db_path, book1.lng_abr_src, book1.lng_abr_dst, splitted_from, splitted_to)

    hash_emb_store_1 = makeHashMapFromBookTexts(emb2, emb_1, splitted_from, splitted_to)

    books_splits:typing.List[BookSplitSection] = CHelperBookSplitter.SplitBookOnSmallParts(emb2, emb_1, splitted_from, splitted_to)

    # db_path = '1asfa_dbg.sql'
    """
    txt_p1 = books_splits[0].split_from
    txt_p2 = books_splits[0].split_to
    

    tmp = [ i[0] for i in aligner.handle_marks(txt_p1)[0]]
    tmp2 = [ i[0] for i in aligner.handle_marks(txt_p2)[0]]

    logHlp.write_to_file( logHlp.getPathTxt_From(), tmp )
    logHlp.write_to_file( logHlp.getPathTxt_To(), tmp2 )
    """

    # todo:: save all books splits in separated files in own subdirectory for improve debugging

    pathDumpResAligned = logHlp.getPathResAlignedParts()
    if not os.path.exists(pathDumpResAligned) or True:
        total_aligned_book:typing.List[AlignBookItemResult] = alignSplittedPartOfBook(book1, books_splits, hash_emb_store_1, logHlp)
        joblib.dump(total_aligned_book, pathDumpResAligned)
    else:
        total_aligned_book:typing.List[AlignBookItemResult] = joblib.load( pathDumpResAligned )

    if config.isBidirect:
        emb2, emb_1 = (emb_1, emb2)
        splitted_from, splitted_to = ( splitted_to, splitted_from)
        hash_emb_store_1 = makeHashMapFromBookTexts(emb2, emb_1, splitted_from, splitted_to)
        books_splits: typing.List[BookSplitSection] = CHelperBookSplitter.SplitBookOnSmallParts(emb2, emb_1,
                                                                                                splitted_from,
                                                                                                splitted_to)

        total_aligned_book: typing.List[AlignBookItemResult] = alignSplittedPartOfBook(book1, books_splits,
                                                                                       hash_emb_store_1, logHlp)

        makeResultBookFromParts(total_aligned_book)
        pass
    
    print('Save result in dump file')
    joblib.dump(total_aligned_book, g_LogHlp.getPathDumpAllBookParts() )
    makeResultBookFromParts( total_aligned_book )
    gLogger.printSummary()
    print("End")
    return


def makeHashMapFromBookTexts(emb2:np.ndarray, emb_1:np.ndarray,
                             splitted_from:typing.List[str], splitted_to:typing.List[str])->typing.Dict[str,np.ndarray]:

    split_from_sanit = aligner.handle_marks(splitted_from)[0]
    split_from_sanit = [i[0] for i in split_from_sanit]
    split_to_sanit = aligner.handle_marks(splitted_to)[0]
    split_to_sanit = [i[0] for i in split_to_sanit]
    hash_emb_store_1 = {calculate_sha1(HelperParagraphSpliter.ClearTextFromParagrapSplitter(txt)): val for txt, val in
                        zip(split_from_sanit, emb_1)}
    hash_emb_store_2 = {calculate_sha1(HelperParagraphSpliter.ClearTextFromParagrapSplitter(txt)): val for txt, val in
                        zip(split_to_sanit, emb2)}
    hash_emb_store_1.update(hash_emb_store_2)
    return hash_emb_store_1


def alignSplittedPartOfBook(book1, books_splits, hash_emb_store_1, logHlp)->typing.List[AlignBookItemResult]:
    total_aligned_book = []
    for ix, split_item in enumerate(books_splits[:]):
        # if ix<37: continue;
        print("Number part for process - ", ix)
        txt_p1 = split_item.split_from
        txt_p2 = split_item.split_to
        tmp = [i[0] for i in aligner.handle_marks(txt_p1)[0]]
        tmp2 = [i[0] for i in aligner.handle_marks(txt_p2)[0]]
        write_to_file(logHlp.getPathTxt_From(), tmp)
        write_to_file(logHlp.getPathTxt_To(), tmp2)

        joblib.dump([book1, tmp, tmp2, hash_emb_store_1], logHlp.getTmpPath('dbg_align_part.dump'))
        res = processSmallPart(book1, tmp, tmp2, hash_emb_store_1, ix)
        total_aligned_book.append(res)
    return total_aligned_book

def ClearPrologEpilogFromBook(emb:typing.List[np.ndarray],
                                logHlp:LogDebugHelper,
                              splitted_from:typing.List[str],
                              splitted_to:typing.List[str]):
    # clean prolog and epilog in book
    assert len(emb[0]) == len(splitted_from)
    assert len(emb[1]) == len(splitted_to)
    clHelper = CHelper_CleanerTexts()
    emb_1, emb2, splitted_from, splitted_to = clHelper.ClearText(emb[0], emb[1], splitted_from, splitted_to)
    assert len(emb_1) == len(splitted_from)
    assert len(emb2) == len(splitted_to)
    ExportTextsHelper.SaveSplitText2File(splitted_from, logHlp.getPathFileSanitazed('from'))
    ExportTextsHelper.SaveSplitText2File(splitted_to, logHlp.getPathFileSanitazed('to'))
    return emb2, emb_1, splitted_from, splitted_to


def MakeEmbidings(book1, logHlp, name_emb_dump, splitted_from, splitted_to):
    db_path = logHlp.getPath_DB_FullText()
    if os.path.isfile(db_path):
        os.unlink(db_path)
    aligner.fill_db(db_path, book1.lng_abr_src, book1.lng_abr_dst, splitted_from, splitted_to)
    if not os.path.exists(name_emb_dump):
        emb = aligner.getEmbidingsAllTexts(db_path, GetAppSettings().m_Model_Name)
        joblib.dump(emb, name_emb_dump)
    emb = joblib.load(name_emb_dump)
    assert len(emb[0]) == len(splitted_from)
    assert len(emb[1]) == len(splitted_to)
    return db_path, emb


def dbg_splitBook_onSmall_parts():
    emb2, emb_1, splitted_from, splitted_to = joblib.load(gPathDumpBookSplits)
    return SplitBookOnSmallParts( emb2, emb_1, splitted_from, splitted_to)


def printBookSplitItems(books_splites_res):
    for ix, bk_split in enumerate(books_splites_res):
        msg = f'\t size block {ix} FROM  {bk_split.ix_from}:{bk_split.ix_from_last}/{bk_split.ix_to}:{bk_split.ix_to_last} Sizes: {bk_split.sizeText_From_kb()} KB:{bk_split.sizeText_To_kb()}KB. Lines count {bk_split.linesCnt_From()}:{bk_split.linesCnt_To()} '
        gLogger.logToSummary(msg)
        txt_split_from = bk_split.split_from[0] if len(bk_split.split_from)>0 else '-1'
        txt_split_to = bk_split.split_to[0] if len(bk_split.split_to)>0 else '-1'
        msg = f'\t\t text from/to:->{txt_split_from}\n\t\t->{txt_split_to}'
        gLogger.logToSummary(msg)

def main():
    return

if __name__ == '__main__':
    main()



#%%
