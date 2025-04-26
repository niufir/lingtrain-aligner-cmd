#%%
import logging
import math
import os.path
from collections import Counter
from logging import Logger

#import pytesseract
from tqdm import tqdm

import os, sys
import numpy as np
from dataclasses import dataclass

from typing import List, Tuple, Union, Optional


import  typing

import fitz  # this is pymupdf
from websocket import WebSocket

PARAGRAPH_SIGN_LABEL = '%paragraph%'

@dataclass
class ValCountPayload:
    val:int
    count:int
    def isContain(self, ypos:int)->bool:
        if abs(ypos-self.val)<3: return True
        return False

@dataclass
class DrawingItemPayload:
    page_number: int
    bbox_items: typing.List[typing.Tuple[float, float, float, float]]
    width:float
    closePath:bool = True

class TitleDetectInfo:
    isExist:bool = False
    y_pos:int = -1
    sample_blocks:typing.List[typing.Dict] = [] # data from pdf lines dicts
    def __init__(self):
        return

    def filterPageTitle(self, blocks:typing.List[dict])->typing.List[dict]:
        res = []
        for bl in blocks:
            ypos = roundBBoxYpos(bl)
            txt_block = self.getText4Bock(bl)
            if len(txt_block) <50:
                if ypos == self.y_pos:
                    continue # skip block
            res.append(bl)
        pass
        return res

    def getText4Bock(self, block):
        res = []
        for l in block['lines']:
            for l in l['spans']:
                res.append(l['text'])
        return ' '.join(res)

class FooterDetectInfo:
    isExist: bool = False
    y_pos: int = -1
    med_y:float = -1.0
    sample_blocks: typing.List[typing.Dict] = []  # data from pdf lines dicts
    y_val_counst: typing.List[ValCountPayload] = []
    totalCountPages:int = 0

    def __init__(self):
        return

    def get_mode_with_counts(self, data: typing.List[Union[int, float, str]]) -> typing.List:
        if not data:
            return None, None

        counter = Counter(data)
        max_count = max(counter.values())

        modes = [ [k,v] for k, v in counter.items() ]
        return modes

    def fit(self, pages):
        def isCountAccesepted(cnt:int, total_pages:int)->bool:
            if total_pages<20:
                return cnt>5
            return ( cnt>total_pages*0.4 )or(cnt>20)

        bbox_y = []
        self.totalCountPages = len(pages)
        for ix, page in enumerate(pages):
            blocks = page['blocks']
            blocks.sort(key=lambda x: x['bbox'][1])

            for bl in blocks:
                bbox = bl['bbox']
                print(bbox)
                if bl['bbox'][1]<500: continue
                bbox_y.append( bl['bbox'][1] )
        if len(bbox_y)==0:
            self.med_y = -1.0
            return
        med_y = np.median(bbox_y)
        valcounts = self.get_mode_with_counts([int(i) for i in bbox_y])
        self.med_y = med_y
        self.y_val_counst:typing.List[ValCountPayload] = [ ValCountPayload(val=v,count=c) for v,c in valcounts]
        self.y_val_counst = [el for el in self.y_val_counst if isCountAccesepted(el.count, self.totalCountPages) ]
        return

    def filterPageFooter(self, blocks: typing.List[dict]) -> typing.List[dict]:
        res = []
        for bl in blocks:
            ypos = roundBBoxYpos(bl)
            txt_block = self.getText4Bock(bl)
            if len(txt_block) < 50:
                isSkip = False
                for foot_bl in self.y_val_counst:
                    if foot_bl.isContain(ypos):
                        isSkip = True
                        break
                if isSkip: continue
            res.append(bl)
        pass
        return res

    def getText4Bock(self, block):
        res = []
        for l in block['lines']:
            for l in l['spans']:
                res.append(l['text'])
        return ' '.join(res)


class CHelperPdfText_Extact:
    def __init__(self, pathfile:str, pathOutput:str = None, log_level = logging.DEBUG):
        self.path_pdf = pathfile
        self.path_output = pathOutput
        self.number_page_dbg:int = -1
        self.Font_size_med = -1
        self.footerDetector = FooterDetectInfo()

        if self.path_output:
            dir_Log = os.path.dirname(self.path_output)
            assert os.path.isdir(dir_Log)
            log_file_path = os.path.join( dir_Log, 'trace.log')
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(log_level)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)

            self.titleDetector = TitleDetectInfo()

            logging.basicConfig(filename=log_file_path, level=log_level,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.logger = logging.getLogger(__name__)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(log_level)
            self.logger.debug('Start debugging')
            self.logger.info("Info logging test")
        return

    def calcSizesInfo(self, pages:typing.List[dict]):
        size_store = []
        for page in pages:
            try:
                for block in page['blocks']:
                    for line in block['lines']:
                        for span in line['spans']:
                            sptxt = span['text']
                            if len(sptxt) < 10: continue
                            size_store.append(span['size'])
            except:
                pass
        med_font_size = np.median(size_store)
        self.logger.info(f"Median Size for font:{med_font_size}")
        self.Font_size_med = med_font_size
        return

    def calcFontSize4Line(self, line:dict)->float:
        s = []
        for span in line['spans']:
              s.append(span['size'])
        return np.median(s)

    def calcParagraphOffset(self,page_blocks:typing.List)->float:
        bbox_x = []
        for blk in page_blocks:
            for l in blk['lines']:
                bbox_x.append( l['bbox'][0] )
        md = np.median(bbox_x)
        bbox_x = [ i for i in bbox_x if i<(md+md*0.1)]
        md = np.mean(bbox_x)
        return md+5

    def filterBlocks_SkipSmallBreakedOrders( self, blocks:typing.List ):
        bbox_y_end = 0
        res_blocks = []
        for bl in blocks:
            bbox = bl['bbox']
            if bbox_y_end == 0:
                bbox_y_end = bbox[1]+bbox[3]
                res_blocks.append(bl)
                continue

            if ( bbox[1]<bbox_y_end )and(bbox[3]<60): # possible header element on page
                # skip block
                continue
            res_blocks.append(bl)
        return res_blocks

    def filterBlocks_Header_Footer(self, blocks:typing.List):

        def isFirstItem_Skip_TitleFooter(block_coll:typing.List)->bool:
            res = False
            blocks_y_store = [bl['bbox'][3] for bl in block_coll]
            bl_delta = []
            while True:
                for ix in range(0, len(blocks_y_store) - 1):
                    bl_delta.append(blocks_y_store[ix + 1] - blocks_y_store[ix])
                if len(bl_delta) < 3: break
                if (bl_delta[0] < 0) and (bl_delta[1] > 0 and bl_delta[2] > 0):
                    res = True
                break
            return res

        blocks.sort(key = lambda bl:bl['bbox'][1])
        bbox_pY = []
        res_blocks = []
        isSkipFirstItem = isFirstItem_Skip_TitleFooter(blocks)
        for ix, bl in enumerate(blocks):
            bbox = bl['bbox']
            if 'lines' not in bl: continue;
            if (ix== 0)and(isSkipFirstItem):
                continue
            if ( len(bbox_pY) == 0):
                bbox_pY.append(bbox[3])
                res_blocks.append(bl)
                continue
            txt_bl = self.format_text_from_raw_block(bl)
            isLastElement = ix == ( len(blocks) -1)
            if bbox[1] + 100 < bbox_pY[-1]:
                msg = self.format_text_from_block(bl['lines'],1e6)
                self.logger.debug("\t skip block: " + msg.replace('\n',' -->') )
                continue
            elif len(txt_bl)<20 and (isLastElement):
                msg = self.format_text_from_block(bl['lines'],1e6)
                self.logger.debug("\t skip block: " + msg.replace('\n',' -->') )
                continue

            res_blocks.append(bl)
            bbox_pY.append(bbox[1])
        return res_blocks

    def clear_blocks( self, blocks:typing.List ):
        res = []
        for ix, block in enumerate(blocks):
            if ix<4:
                if block['bbox'][1]>440: continue
            block_h = block['bbox'][3]-block['bbox'][1]

            # check - technical line on buttom page.
            if (block_h<10)and(block['bbox'][1]>520):
                self.logger.debug('Skip block - butttom page technical line with text:' + self.format_text_from_raw_block(block))
                continue
            if (block['bbox'][0]<0):
                self.logger.debug('Skip block, xpos bbox low zero:' + self.format_text_from_raw_block(block))
                continue
            res.append(block)
        return res

    def sanitizeBlockText(self, block_txt:str)->str:
        res = ((block_txt.replace('  ',' ').replace('  ',' ')
                .replace(' ,',',')).replace(' :',':').replace('„ ','„')
               .replace(' “','“')).replace(' .','.').replace(" ;",';')
        return res

    def recrateBlocks(self, block_coll:typing.List[str])->typing.List[str]:
        res = []
        for block in block_coll:
            isPoint = False
            if len(res) == 0:
                res.append(self.sanitizeBlockText(block))
                continue
            if len(res) == 0:
                pass
            elif len( res[-1] ) == 0:
                pass
            else:
                isPoint = res[-1][-1] == '.'
            if isPoint:
                res.append(self.sanitizeBlockText(block))
            else:
                res[-1] += ' ' + self.sanitizeBlockText(block)
        return res

    def fixEndPointIfNeed(self, sline: str) -> str:
        if not sline: return ''
        if sline.strip() == '': return sline
        if sline and sline[-1] not in ['.', '!', '?']:
            pass
            #sline += '.'
        return sline

    def isLine_HeaderByFont(self, line:dict)->bool:
        txtsize = self.calcFontSize4Line(line)
        if txtsize<self.Font_size_med*1.1:
            return False
        return True

    def format_text_from_raw_block(self, block:typing.Dict):
        if 'lines' not in block: return ''
        return self.format_text_from_block(block['lines'], 1e6)

    def format_text_from_block(self, lines_items:typing.List,
                               paragraph_offset:float)->str:
        """

        :param lines_items: list of dict
        :return:
        """
        ypos = [el['bbox'][1] for el in lines_items]
        med_y_pos = np.median(ypos)
        ypos_delta = [ abs(med_y_pos - y) for y in ypos ]
        bool_is_equ = [d<2 for d in ypos_delta]
        is_same_line = False
        if np.sum(bool_is_equ) == len(bool_is_equ):
            is_same_line = True

        isSpecial_align_not_paragraph = False
        x_pos = [ roundFloat( el['bbox'][0] ) for el in lines_items]
        if (len(set(x_pos))==1)and(len(x_pos)>2):
            isSpecial_align_not_paragraph = True

        res_text = []
        for line in lines_items:
            box_4_check = 0
            fontsize4line = self.calcFontSize4Line(line)

            if is_same_line:
                if len(res_text) == 0:
                    box_4_check= lines_items[0]['bbox'][0]
            else:
                box_4_check= line['bbox'][0]
            if (box_4_check > paragraph_offset)and(not isSpecial_align_not_paragraph ):
                    res_text.append(PARAGRAPH_SIGN_LABEL)
                    pass
            isLineHeader = self.isLine_HeaderByFont(line)
            if isLineHeader:
                res_text.append(PARAGRAPH_SIGN_LABEL)

            txt_line = []
            for span in line["spans"]:
                text = span["text"].strip()
                if len(text) == 0: continue
                # todo: remove next code
                if 'Как клиент приходит к пониманию ценности' in text:
                    print('alert debug sdfnadsfon' )
                    isLineHeader = self.isLine_HeaderByFont(line)
                # print(text)
                if isLineHeader:
                    if text[-1]!='.':
                        text += '.'
                txt_line.append(text)


            res_text_line = ' '.join(txt_line)
            res_text.append(res_text_line)
            if isLineHeader:
                res_text.append(PARAGRAPH_SIGN_LABEL)
    
        if isSpecial_align_not_paragraph:
            res_text.insert(0, PARAGRAPH_SIGN_LABEL)
            res_text.append(PARAGRAPH_SIGN_LABEL)
            
        # post processing texts
        res_text_combined = []
        for ix, l in enumerate(res_text):
            if len(res_text_combined) == 0:
                res_text_combined.append(l)
                continue

            prev_line = res_text_combined[-1]
            if len(prev_line) == 0:
                res_text_combined.append(l)
                continue

            if PARAGRAPH_SIGN_LABEL in l:
                res_text_combined.append(l)
                continue

            if prev_line[-1] == '-':
                nl = prev_line[:-1] + l
            else:
                nl = prev_line.rstrip() + ' ' + l.strip()
            res_text_combined[-1] = nl

            pass
        res_text = res_text_combined
        if is_same_line:
            res_text = ' '.join(res_text)
        else:
            res_text = [self.fixEndPointIfNeed(l) for l in res_text]
            res_text = '\n'.join(res_text)
            pass
        assert type(res_text) == str
        return res_text

    def FormatTexFromPageBlocks(self, blocks:typing.List[str])->str:
        restxt = []
        for l in blocks:
            if l == PARAGRAPH_SIGN_LABEL:
                restxt.append('\t')
                continue

            if len(l) == 0: continue
            if len(restxt)==0:
                restxt.append(l)
                continue

            last_line = restxt[-1]
            if len(last_line) == 0:
                restxt.append(l)
                continue

            if last_line[-1] not in ['.','!','?']:
                restxt[-1] += ' ' + l.strip() + ' '
            else:
                restxt.append(l)
        if len(restxt)==0:
            print('alert res text ==0')

        res = '\n'.join(restxt)
        res = res.replace(' ,',',').replace(' .','.')
        return res

    def extract_drawings_per_page(self, doc):
        """
        Extracts drawing elements from each page and stores them
        in a list with the corresponding page number.
        """
        drawings_per_page = []
        for page_num, page in enumerate(doc):
            lines = page.get_drawings()
            for line in lines:
                if  line["type"] != "s": continue
                dritem = DrawingItemPayload(bbox_items=line['rect'], page_number=page_num+1, width=line['width'], closePath=line['closePath'] )
                drawings_per_page.append(dritem)

        return drawings_per_page

    def TryDetect_PageHeaderWithNumber(self, pages:typing.List):

        def is_string_only_digit(input_string: str) -> bool:
            return input_string.isdigit()

        alert_blocks = []
        for page in pages:
            for block in page['blocks']:
                is_need_break = False
                if not 'lines' in block: continue
                for line in block['lines']:
                    for span in line['spans']:
                        sptxt = span['text']
                        if is_string_only_digit(sptxt):
                            alert_blocks.append(block)
                            is_need_break = True
                            break

                if is_need_break:
                        break
        bl_y_pos = [ roundBBoxYpos(i) for i in alert_blocks ]
        while True:
            freq_data = most_frequent(bl_y_pos)
            if freq_data is None:break
            ypos, count = freq_data
            if count*100/len(pages) < 10: break
            self.titleDetector.sample_blocks = [ bl for bl in alert_blocks if roundBBoxYpos(bl)== ypos ]
            self.titleDetector.y_pos = ypos
            self.titleDetector.isExist = True
            break
        return
    
    def RunExtract(self):
        #txt = self.read_pdf( self.path_pdf )
        # pdf_path = pathfile  # replace with your PDF file path
        doc = fitz.open(self.path_pdf)
        # TODO:: find horizontal lines, try detect header/footer on page and skip, when text extact
        dr_items = self.extract_drawings_per_page( doc )

        for page in doc:
            lines = page.get_drawings()
            for line in lines:
                if line["type"] == "hline":  # 'hline' indicates horizontal line
                    line_width = line["width"]
                    self.logger.debug(f"Found horizontal line on page { 1} with width: {line_width}")

        pages = [p.get_text('dict') for p in doc]
        self.TryDetect_PageHeaderWithNumber(pages)
        self.footerDetector.fit(pages)

        self.calcSizesInfo(pages)
        if self.number_page_dbg>=0:
            pages = [pages[self.number_page_dbg]]
        self.logger.info(f'Read {len(pages)} pages')


        all_blocks_collection = []
        for page in tqdm( list(pages) ):
            blocks = [bl for bl in page['blocks'] if bl['type'] == 0]
            blocks4skip = [bl for bl in page['blocks'] if bl['type'] != 0]
            if len(blocks4skip) > 0:
                pass
            blocks = self.filterBlocks_SkipSmallBreakedOrders(blocks)
            blocks = self.titleDetector.filterPageTitle(blocks)
            blocks = self.footerDetector.filterPageFooter(blocks)
            # blocks = self.filterBlocks_Header_Footer(blocks)
            all_blocks_collection.append(blocks)

        self.logger.info(f'Count pages {len(pages)}')
        self.logger.info(f'Count blocks {len(all_blocks_collection)}' )

        all_blocks_collection = [self.clear_blocks(all_blocks_collection[i]) for i in range(len(all_blocks_collection))]

        alltext_blocks = []
        # for page_dict in pages:
        # blocks =[ bl for bl in  page_text['blocks'] if bl['type']==0]
        for ix, block_per_page in enumerate( all_blocks_collection ):

            paragraph_offset = self.calcParagraphOffset(block_per_page)
            # print(f'\t paragraph offset: {paragraph_offset}')
            cblock:typing.List[str] = []
            for block in block_per_page:
                cblock.append(self.format_text_from_block(block["lines"], paragraph_offset))
                continue

            if len(alltext_blocks) == 0:
                alltext_blocks.append(cblock)
                continue

            alltext_blocks.append(cblock)

        alltext_blocks = [self.FormatTexFromPageBlocks(i) for i in alltext_blocks]
        alltext_blocks_tmp=[]
        for ix, block_per_page in enumerate( alltext_blocks ):
            if 'თუ შეხვდებით ორბელიანს' in block_per_page:
                pass
            if len(alltext_blocks_tmp) == 0:
                alltext_blocks_tmp.append(block_per_page)
                continue
            prev_block = alltext_blocks_tmp[-1]
            if not prev_block.endswith(('.', '?', '!')):
                alltext_blocks_tmp[-1] = alltext_blocks_tmp[-1].strip() +' ' + block_per_page
                continue
            alltext_blocks_tmp.append(block_per_page)
        alltext_blocks = alltext_blocks_tmp

        res_text = '\n'.join(alltext_blocks).replace(PARAGRAPH_SIGN_LABEL, '\n\t')

        #res_text = '\n'.join([self.sanitizeBlockText(i) for i in self.recrateBlocks(alltext_blocks)]).replace('-\n', '').replace('\n',
        #                                                                                                        '').replace(
        #    '%paragraph%', '\n\n')
        #res_text[:13000].split('\n\n')
        with open(self.path_output, 'w', encoding='utf-8') as f:
            f.write(res_text)
        print('Save file:', self.path_output)
        """
        for i in self.recrateBlocks(alltext_blocks):
            print(self.sanitizeBlockText(i))
            print("~~~~~~~~~~~~~~~~~~~")
            """

        return

def Read_PDF(pathfile, output_path):
    CHelperPdfText_Extact(pathfile, output_path).RunExtract()
    return

def main():

    return

def most_frequent(arr)->typing.Tuple[typing.Any,int]:
    counter = Counter(arr)
    most_common = counter.most_common(1)
    return most_common[0] if most_common else None

def roundFloat(f:float)->int:
    return math.floor(f)

def roundBBoxYpos(block:typing.Dict)->int:
    return roundFloat( block['bbox'][1] )



if __name__ == "__main__":
    main()


