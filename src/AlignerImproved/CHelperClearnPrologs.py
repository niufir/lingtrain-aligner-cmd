import os
import sys
import typing
from collections import Counter
import faiss
import joblib
import numpy as np
from sklearn.metrics import pairwise_distances
from tqdm import tqdm

from LoggerHelper import SingletonLoggerHelper, GetSingLogger
from src.lingtrain_aligner.Settings import GetAppSettings

Count_Addion_Text_Clear_Text = 100
def import_ling_align():
    try:
        from ..lingtrain_aligner import preprocessor, splitter, aligner, resolver, reader, helper, vis_helper
    except:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from lingtrain_aligner import preprocessor, splitter, aligner, resolver, reader, helper, vis_helper
        pass


SIGN_PARAGRAPH_MARKER = '%%%%%'
WND_SIZE_MERGE_PROLOGS = 10

from enum import Enum


class ETypeWindowScan(Enum):
    ScanForward = 1
    ScanBackward = 2
    ScanAround = 3

class CMergingInfo:
    def __init__(self,ix_process:int,
                 isSameExists:bool,
                 len_text:int,
                 index_txt_opposite:int,
                 text:str= ''):
        self.indx_txt_main = ix_process
        self.isSameExists = isSameExists
        self.len_text = len_text
        self.text = text
        self.indx_txt_opposite = index_txt_opposite
        self.range_index = -1 # index if queue
        self.dist_cos = -2.0
        self.dist_manh = -1e6
        assert (isinstance(index_txt_opposite, int))or(isinstance(index_txt_opposite, np.int64))
        return

    @staticmethod
    def printMergeInfoList(data:typing.List['CMergingInfo']) -> None:
        logger = SingletonLoggerHelper()
        logger.Info('~~~ Info List ~~~')
        for ix in range( len(data) ):
            info:CMergingInfo = data[ix]
            logger.Info(f'({info.indx_txt_main}, {info.isSameExists}, {info.len_text}, {info.indx_txt_opposite}), {info.text}  manh-dist {info.dist_manh} cos-dist {info.dist_cos}', )
        return

    @staticmethod
    def initRangeIndex(data:typing.List['CMergingInfo']) -> typing.List['CMergingInfo']:
        for ix in range( len(data) ):
            data[ix].range_index = ix
        return  data

    @staticmethod
    def makeMergeInfoCollectionFromTestList(data:typing.List[typing.Tuple]) -> None:
        res = []
        for item in data:
            if len(item)>3:
                info = CMergingInfo(item[0], item[1], item[2], item[3])
            else:
                info = CMergingInfo(item[0], item[1], item[2], item[0])
            res.append(info)
        return res

class CHelper_CleanerTexts:

    SIZE_WND_CHECK_SAME_TEXT = 5
    SIZE_WND_SIMILARITY = 120

    def __init__(self):
        self.emb_1 = None
        self.emb2 = None
        self.nbrs = None
        self.nbrs_t1 = None
        self.splitted_to = None
        self.splitted_from = None
        return

    def setTexts(self, txt_from:typing.List[str], txt_to:typing.List[str]):
        self.splitted_from = txt_from
        self.splitted_to = txt_to
        return

    def setEmbidingData(self, emb1, emb2):
        self.emb_1 = emb1
        self.emb2 = emb2
        #self.nbrs = NearestNeighbors(n_neighbors=10, algorithm='auto').fit(emb2)
        #self.nbrs_t1 = NearestNeighbors(n_neighbors=10, algorithm='auto').fit(self.emb_1)

        self.nbres_faiss = faiss.IndexFlatL2(emb2.shape[1])
        self.nbres_faiss.add(emb2)

        self.nbres_faiss_t1 = faiss.IndexFlatL2(self.emb_1.shape[1])
        self.nbres_faiss_t1.add(self.emb_1)
        return

    def findSimilarUsingIndex_In_From(self, request):
        is_inpur_1d = False
        if  len( request.shape) == 1:
            request = request.reshape(1,-1)
            is_inpur_1d = True

        res = self.nbres_faiss_t1.search(request, 10 )
        res_index = res[1]
        res_dist = res[0]

        return res_dist, res_index

    def findSimilarUsingIndex_In_To(self, request:np.ndarray):
        #is_inpur_1d = False
        if  len( request.shape) == 1:
            request = request.reshape(1,-1)
            #is_inpur_1d = True

        res = self.nbres_faiss.search(request, 10 )
        res_index = res[1]
        res_dist = res[0]

        return  res_dist, res_index

    def loadCachedData(self):
        name_emb_dump = "emb_all.dump"
        emb_1, emb2 = joblib.load(name_emb_dump)

        print('emb 1: ',emb_1.shape, ' emb 2: ',emb2.shape)
        print('load text')
        splitted_from, splitted_to = joblib.load('text.dump')
        print('cont lints text1=', len(splitted_from))
        print('count lines in text2=', len(splitted_to))
        self.setEmbidingData(emb_1, emb2)
        return

    def getSliceWindowFromEmb(self,
                              emb_store:typing.List,
                              indx:int,
                              wnd_halw_size:int = 5,
                              scanType:ETypeWindowScan = ETypeWindowScan.ScanAround
                              )->typing.List:
        if scanType == ETypeWindowScan.ScanAround:
            ix_start = max(0, indx - wnd_halw_size)
            ix_end = min(len(emb_store), indx + wnd_halw_size)
        elif scanType == ETypeWindowScan.ScanForward:
            ix_start = max(0, indx)
            ix_end = min(len(emb_store), indx + 2*wnd_halw_size)
        elif scanType == ETypeWindowScan.ScanBackward:
            ix_start = max(0, indx-2*wnd_halw_size)
            ix_end = min(len(emb_store), indx )
        else:
            raise ValueError(f'Value {scanType} is not supported')
        return emb_store[ix_start:ix_end]

    def calcMedDist(self, emb1, emb2):
        dist = pairwise_distances(emb1, emb2, metric='manhattan')
        res = np.median( [ np.min(dist[ix]) for ix in range(dist.shape[0]) ] )
        return res

    def calcMedDist_cos(self, emb1, emb2):
        dist = pairwise_distances(emb1, emb2, metric='cosine')
        res = np.median( [ np.min(dist[ix]) for ix in range(dist.shape[0]) ] )
        return res

    def calcMinDistance4Section_cos(self, emb2,
                                    indx_with_delta:typing.List[typing.Tuple[int,int]],
                                    wnd1,
                                    wnd_size:int = None,
                                    scanType:ETypeWindowScan = ETypeWindowScan.ScanAround
                                    ) -> typing.List[typing.Tuple[int, float]]:
        res = []
        for ix,_ in indx_with_delta:
            if wnd_size:
                wnd2 = self.getSliceWindowFromEmb(emb2, ix, wnd_halw_size=wnd_size, scanType=scanType)
            else:
                wnd2 = self.getSliceWindowFromEmb(emb2, ix, scanType=scanType)

            if len(wnd2)==0: continue;
            if len(wnd1)==0: continue

            cur_med_dist = self.calcMedDist_cos(wnd1, wnd2)

            # todo: possible use cos dist for calc similarity between texts
            #med_dist_cos = self.calcMedDist_cos(wnd1, wnd2)
            #print(f'cos dis={med_dist_cos}')

            #med_dist_cos = self.calcMedDist_cos(wnd1, wnd2)

            res.append([ix, cur_med_dist])
            # if cur_med_dist<15: break
        return res

    def calcMinDistance4Section(self, emb2,
                                 indx_with_delta:typing.List[typing.Tuple[int,int]],
                                 wnd1,
                                wnd_size:int = None,
                                scanType:ETypeWindowScan = ETypeWindowScan.ScanAround
                                 ) -> typing.List[typing.Tuple[int, float]]:
        """

        Calculate the minimum distance for each section. Distance from src text to dest text.
        For calcualte distance use window with several item, and calc median distance per several sentences

        Parameters:
        - emb2 (type: Any): The input emb2 parameter.
        - indx_with_delta (type: List[Tuple[int,int]]): A list of tuples containing integer indices and delta values.
        - wnd1 (type: Any): The input wnd1 parameter.

        Returns:
        - res (type: List[Tuple[int,float]]): A list of tuples containing integer indices and float distances.

        """
        res = []
        for ix,_ in indx_with_delta:
            if wnd_size:
                wnd2 = self.getSliceWindowFromEmb(emb2, ix, wnd_halw_size=wnd_size, scanType=scanType)
            else:
                wnd2 = self.getSliceWindowFromEmb(emb2, ix, scanType=scanType)

            if len(wnd2)==0: continue;
            if len(wnd1)==0: continue

            cur_med_dist = self.calcMedDist(wnd1, wnd2)

            # todo: possible use cos dist for calc similarity between texts
            #med_dist_cos = self.calcMedDist_cos(wnd1, wnd2)
            #print(f'cos dis={med_dist_cos}')

            #med_dist_cos = self.calcMedDist_cos(wnd1, wnd2)

            res.append([ix, cur_med_dist])
            if cur_med_dist<15: break
        return res
        # print('index ix','dist=', calcMedDist(wnd1, wnd2))

    def findSamePartText(self, ix_process:int, text_corpora:typing.List[str],
                         wnd_size:int = None,
                         scanDir:ETypeWindowScan = ETypeWindowScan.ScanAround
                         , Edge_value:float = GetAppSettings().DIST_EDGE)->CMergingInfo:
        err_cont_max = 0
        #if 'She was at the Bouffons last night' in text_corpora[ix_process]:
        #    pass
        e_1 = self.emb_1[ix_process]
        print(text_corpora[ix_process])
        _, indices =  self.findSimilarUsingIndex_In_To(e_1) # self.nbrs.kneighbors([e_1])
        index_delta = [abs(i - ix_process) for i in indices[0]]

        indx_with_delta = [ (i1,i2) for i1, i2 in zip(indices[0], index_delta) ]

        # sort by delta index - order - delta between index from txt1 and index from txt2.
        # similar text may be located in nearest indexes
        indx_with_delta.sort(key=lambda x: x[1])
        wnd1 = self.getSliceWindowFromEmb( self.emb_1, ix_process, scanType=scanDir )
        store_ix_dist = self.calcMinDistance4Section( self.emb2, indx_with_delta,wnd1, wnd_size=wnd_size, scanType=scanDir )
        store_ix_dist.sort(key=lambda x: x[1])
        isSameExists = True
        if store_ix_dist[0][1]> Edge_value:
            isSameExists = False
            err_cont_max +=1
        store_ix_dist_cos = self.calcMinDistance4Section_cos(self.emb2, indx_with_delta,wnd1, wnd_size=wnd_size, scanType=scanDir )
        store_ix_dist_cos.sort(key=lambda x: x[1])

            #if err_cont_max > 15: break

        # cmp_store.append([ix_process, isSameExists, len(splitted_from[ix_process]) ] )
        # print(ix_process, len(self.splitted_from))
        res_merge = CMergingInfo(ix_process, isSameExists,
                                 self.calcTextLen( text_corpora[ix_process] ),
                                 store_ix_dist[0][0],
                                 text=text_corpora[ix_process])
        res_merge.dist_manh = store_ix_dist[0][1]
        res_merge.dist_cos = store_ix_dist_cos[0][1]
        return res_merge

    def findSamePartText_2_to_1(self, ix_process:int, text_corpora:typing.List[str],
                                scanDir:ETypeWindowScan = ETypeWindowScan.ScanAround, wnd_size=None,
                                Edge_value:float = GetAppSettings().DIST_EDGE):
        err_cont_max = 0
        e_2 = self.emb2[ix_process]
        distances, indices = self.findSimilarUsingIndex_In_From(e_2) # self.nbrs_t1.kneighbors([e_2])
        if 'Вчера она была в Итальянском театре' in text_corpora[ix_process]:
            pass
        if 'разве я этого не предсказывала' in text_corpora[ix_process]:
            pass

        index_delta = [abs(i - ix_process) for i in indices[0]]
        indx_with_delta = [ (i1,i2) for i1, i2 in zip(indices[0], index_delta) ]
        indx_with_delta.sort(key=lambda x: x[1])
        wnd1 = self.getSliceWindowFromEmb(self.emb2, ix_process, scanType=scanDir)
        store_ix_dist = self.calcMinDistance4Section(self.emb_1, indx_with_delta, wnd1, scanType=scanDir)
        store_ix_dist.sort(key=lambda x: x[1])
        isSameExists = True
        if store_ix_dist[0][1]> Edge_value:
            isSameExists = False
            err_cont_max +=1
            #if err_cont_max > 15: break
        store_ix_dist_cos = self.calcMinDistance4Section_cos(self.emb_1, indx_with_delta,wnd1, wnd_size=wnd_size, scanType=scanDir )
        store_ix_dist_cos.sort(key=lambda x: x[1])
        if len(store_ix_dist_cos)==0:
            store_ix_dist_cos = [[-1,-1]]

        # cmp_store.append([ix_process, isSameExists, len(splitted_from[ix_process]) ] )
        res_merge = CMergingInfo(ix_process,
                                 isSameExists,
                                 self.calcTextLen( text_corpora[ix_process] ),
                                 store_ix_dist[0][0],
                                 text=text_corpora[ix_process])

        res_merge.dist_manh = store_ix_dist[0][1]
        res_merge.dist_cos = store_ix_dist_cos[0][1]
        return res_merge


    def SplitFromStart(self,cmp_store:typing.List[CMergingInfo], isTestOld:bool = False):
        def filter_isShotSent( cmp_item:CMergingInfo):
            if not cmp_item.isSameExists:
                return cmp_item.len_text<=25
            return cmp_item.len_text<=10

        def checkPostTrueFind( cmp_store_after_true: typing.List[CMergingInfo] )->bool:
            if isTestOld: return True
            res = True
            if len(cmp_store_after_true)<WND_SIZE_MERGE_PROLOGS: return False
            cnt_true = np.sum([i.isSameExists for i in cmp_store_after_true  ])
            if cnt_true * 100.0/len(cmp_store_after_true) < 30:
                res = False
            return res

        def tryBackwardTrace(ixres:int, cmp_store:typing.List[CMergingInfo])->int:
            wnd_backward_size = 7
            max_backward_offset = 40
            res_fixed = ixres
            cmp_store = [i for i in cmp_store if i.dist_cos>-2]
            if len(cmp_store)==0: return ixres
        
            for ix in range(ixres-1,max(-1, ixres-max_backward_offset),-1):
                mask_wnd = [ i.dist_manh<GetAppSettings().DIST_EDGE_ClearPrologs*1.04 for i in cmp_store[ix:ix+wnd_backward_size]]
                opposite_indexes =[i.indx_txt_opposite for i in cmp_store[ix:ix+wnd_backward_size]]
                value_counts = Counter(opposite_indexes)
                if len(value_counts)<len(mask_wnd)-3: break
                
                if len(mask_wnd)<3: continue;
                # in checked window not true
                if np.sum(mask_wnd)<2:
                    break
                if cmp_store[ix].dist_manh<( GetAppSettings().DIST_EDGE_ClearPrologs*1.04):
                    res_fixed = ix
            return res_fixed

        CMergingInfo.initRangeIndex(cmp_store)
        CMergingInfo.printMergeInfoList(cmp_store)
        wnd_size = WND_SIZE_MERGE_PROLOGS
        res_ix = -1
        cmp_store = [i for i in cmp_store if not filter_isShotSent(i)]

        index_median = np.median([cmp_item.indx_txt_opposite for cmp_item in cmp_store if cmp_item.isSameExists])

        value_counts = Counter([cmp_item.indx_txt_opposite for cmp_item in cmp_store if cmp_item.isSameExists])


        for ix in range(len(cmp_store)-1):
            # delta = cmp_store[ix+1].indx_txt_opposite-cmp_store[ix].indx_txt_opposite
            delta = index_median - cmp_store[ix].indx_txt_opposite
            if (abs(delta)>50 )and( (cmp_store[ix].dist_manh> 17) ): # or(delta<0):
                cmp_store[ix].isSameExists = False

        CMergingInfo.printMergeInfoList(cmp_store)

        for ix in range(len(cmp_store) - wnd_size):
            wnd_data = cmp_store[ix:ix+wnd_size]
            wnd_data_full = wnd_data
            wnd_data = [i for i in wnd_data if
                        (i.isSameExists)or( (i.isSameExists==False)and(filter_isShotSent(i)) )]
            wnd_data = wnd_data[:wnd_size]
            size_Truth_merged = np.sum( [ i.len_text for i in wnd_data if i.isSameExists ] )
            size_False_merded =  np.sum( [ i.len_text for i in wnd_data if not i.isSameExists ] )
            value_counts = Counter([cmp_item.indx_txt_opposite for cmp_item in wnd_data if cmp_item.isSameExists])
            if size_False_merded == 0: size_False_merded = 1.0

            if np.sum([i.isSameExists for i in wnd_data])<wnd_size-3:
                continue
            elif (len(value_counts)<len(wnd_data)-3):
                continue
            elif np.sum([i.isSameExists for i in wnd_data])<wnd_size:
                if (not cmp_store[ix].isSameExists)and (not wnd_data_full[0].isSameExists):# first is False - skip
                    continue
                elif cmp_store[ix].isSameExists:
                    if not checkPostTrueFind( cmp_store[ix + int(wnd_size*1.5):] ):
                        continue
                    res_ix = cmp_store[ix].range_index
                    break
                else:
                    continue
            elif ( (float(size_Truth_merged)/float(size_False_merded))>4)and( size_Truth_merged>200 ):
                pass
            else:
                continue
            if not checkPostTrueFind( cmp_store[ix + int(wnd_size*1.5):] ):
                continue

            res_ix = cmp_store[ix].range_index
            break
        if res_ix != -1:
            ix = tryBackwardTrace( ix, cmp_store)
            res_ix = cmp_store[ix].range_index
            print('success')
        return res_ix

    def findWrongProlog(self,
                        fun_findsSameText:typing.Callable,
                        emb_data:typing.List,
                        isReverse:bool = False,

                        )->int:
        cnt_wnd4check = CHelper_CleanerTexts.SIZE_WND_SIMILARITY
        cmp_store:typing.List[CMergingInfo] = []

        text_corpora = None
        if len(emb_data) == len(self.splitted_from):
            text_corpora = self.splitted_from
        else:
            text_corpora = self.splitted_to

        if not isReverse:
            ix_start = 0
            ix_end = min((len(emb_data)),cnt_wnd4check)
            while True:
                # fill cmp store with comparation results
                for ix_process in tqdm( range ( ix_start, ix_end )):
                    cmp_store.append( fun_findsSameText(ix_process, text_corpora, scanDir = ETypeWindowScan.ScanForward,
                                                        Edge_value = GetAppSettings().DIST_EDGE_ClearPrologs) )
                ix_split = self.SplitFromStart( cmp_store )
                if ix_split == -1:
                    cmp_store = []
                    assert CHelper_CleanerTexts.SIZE_WND_SIMILARITY > 3*WND_SIZE_MERGE_PROLOGS + 2
                    ix_start += CHelper_CleanerTexts.SIZE_WND_SIMILARITY - 3*WND_SIZE_MERGE_PROLOGS - 2
                    ix_end += CHelper_CleanerTexts.SIZE_WND_SIMILARITY - 3*WND_SIZE_MERGE_PROLOGS - 2
                    if ix_end >= len(emb_data):
                        return None
                    continue
                #ix_split += ix_start

                # try search caption
                ix_split_new = ix_split
                for ix_back in range(ix_split, max( ix_split - 5,0),-1):
                    if cmp_store[ix_back].len_text<20:
                        ix_split_new = ix_back
                        break
                ix_split = ix_split_new
                break
        else:
            # find epilog
            start_pos = len(emb_data)-1
            end_pos = start_pos-CHelper_CleanerTexts.SIZE_WND_SIMILARITY
            while True:
                for ix_process in tqdm( range( start_pos , end_pos, -1) ):
                    cmp_store.append(fun_findsSameText(ix_process, text_corpora, scanDir = ETypeWindowScan.ScanBackward,
                                                       Edge_value = GetAppSettings().DIST_EDGE_ClearPrologs ))
                # ix_split - index with true item. must be include in result

                ix_split = self.SplitFromStart(cmp_store)
                if ix_split == -1:
                    cmp_store:typing.List[CMergingInfo] = []
                    assert CHelper_CleanerTexts.SIZE_WND_SIMILARITY > 3*CHelper_CleanerTexts.SIZE_WND_CHECK_SAME_TEXT+2
                    start_pos -=  (CHelper_CleanerTexts.SIZE_WND_SIMILARITY - 3*CHelper_CleanerTexts.SIZE_WND_CHECK_SAME_TEXT-2)
                    end_pos -= (CHelper_CleanerTexts.SIZE_WND_SIMILARITY - 3*CHelper_CleanerTexts.SIZE_WND_CHECK_SAME_TEXT-2)
                    if start_pos <= 0:
                        print('Error - cant find same text from epilog. ')
                        return None, None
                    continue


                #for ix_back in range(ix_split, 0,-1):
                #    if cmp_store[ix_back].dist_manh<GetAppSettings().DIST_EDGE_ClearPrologs:

                break

        index_from_direcdt = cmp_store[ix_split].indx_txt_main
        return index_from_direcdt

    def calcTextLen(self, txt)->int:
        rl = len( txt.replace(SIGN_PARAGRAPH_MARKER,'') )
        return rl

    def FindWrongPrologWrapper(self):

        index_from_direcdt = self.findWrongProlog(self.findSamePartText, self.emb_1)# cmp_store[ix_split][0]
        index_to_direcd =  self.findWrongProlog(self.findSamePartText_2_to_1, self.emb2)

        return index_from_direcdt, index_to_direcd

    def FindWrongEpilog(self):
        ix_from_split_after = self.findWrongProlog(self.findSamePartText, self.emb_1, isReverse=True) # cmp_store_before_t2[ ix_split_after_2][0]
        ix_to_split_after = self.findWrongProlog(self.findSamePartText_2_to_1, self.emb2, isReverse=True) # cmp_store_before_t2[ ix_split_after_2][0]

        ix_to_split_after = self.Adjust_Epilog_Cleared(ix_to_split_after, self.splitted_to)
        ix_from_split_after = self.Adjust_Epilog_Cleared(ix_from_split_after, self.splitted_from)

        return ix_from_split_after, ix_to_split_after

    def Adjust_Epilog_Cleared(self, ix_to_split_after, text_data:typing.List[str]):
        size_addition = 0
        if not((SIGN_PARAGRAPH_MARKER in text_data[ix_to_split_after])):
            for ix in range(ix_to_split_after+1, len(text_data)):
                size_addition += len(text_data[ix])
                if ((SIGN_PARAGRAPH_MARKER in text_data[ix])
                        and (size_addition < Count_Addion_Text_Clear_Text)):
                    ix_to_split_after = ix
                    break
                if size_addition >= Count_Addion_Text_Clear_Text: break
        return ix_to_split_after

    def saveText2File(self, data, fname):
        print('Save data to file', fname)
        with open(fname, 'w', encoding='utf-8') as f:
                for l in data:
                    f.write(l+'\n')
        return
    def ClearText_dbg(self):
        self.loadCachedData()
        splitted_from, splitted_to = joblib.load('text.dump')
        self.setTexts(splitted_from, splitted_to)
        ix_prologs = self.FindWrongPrologWrapper()

        ix_epilogs = self.FindWrongEpilog()
        print('Indexes prolog', ix_prologs)
        print('Indexes epilog', ix_epilogs)
        splitted_from = self.splitted_from[ ix_prologs[0]:ix_epilogs[0] ]
        splitted_to = self.splitted_to[ ix_prologs[1]:ix_epilogs[1] ]
        # for debugger
        self.saveText2File(splitted_from,'dbg_split_from.txt')
        self.saveText2File(splitted_to,'dbg_split_to.txt')
        return

    def ClearText(self, emb_1:np.ndarray, emb_2:np.ndarray,
                  text_from:typing.List[str],
                  text_to:typing.List[str]):

        self.setTexts(text_from, text_to)
        self.setEmbidingData(emb_1, emb_2)

        ix_prologs = self.FindWrongPrologWrapper()
        ix_epilogs = self.FindWrongEpilog()

        GetSingLogger().info(f'Indexes prolog {ix_prologs}' )
        GetSingLogger().info(f'Indexes epilog {ix_epilogs} cut count = {len(text_from) - ix_epilogs[0]} cut count = {len(text_to) - ix_epilogs[1]}'                             )
        splitted_from = self.splitted_from[ ix_prologs[0]:ix_epilogs[0] +1 ]
        splitted_to = self.splitted_to[ ix_prologs[1]:ix_epilogs[1] +1 ]

        emb_1  =self.emb_1[ix_prologs[0]:ix_epilogs[0] +1 ]
        emb_2 = self.emb2[ ix_prologs[1]:ix_epilogs[1] + 1 ]
        return emb_1, emb_2, splitted_from, splitted_to

    @staticmethod
    def Split2SmallBooks(cmp_store:typing.List[CMergingInfo], isTestOld:bool = False):
        hlp = CHelper_CleanerTexts()
        return hlp.SplitFromStart(cmp_store, isTestOld=isTestOld)

def main_tst():
    sys.exit(0)
    text_cleaner = CHelper_CleanerTexts()
    text_cleaner.ClearText_dbg()
    return

if __name__ == '__main__':
    main_tst()