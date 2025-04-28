import ebooklib
import numpy as np
import typing
import os
from enum import Enum
from dataclasses import dataclass
from ebooklib.epub import EpubBook, EpubItem
from bs4 import BeautifulSoup
from ebooklib.epub import EpubBook, EpubItem

def extract_text_from_epub(epub_path):
    book = EpubBook()
    book.load(epub_path)
    text = ''
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text() + '\n'
    return text


#import pyepub

#import fitz  # this is PyMuPDF

class TextBlockType(Enum):
    Default = 0
    LinePerBlock = 1



@dataclass
class CTextBlock:
    text: str
    page_number: int
    block_index: int
    isParagraph: bool
    def __init__(self, text:str, page_number:int, block_index:int, isParagraph:bool = False):
        self.text = text
        self.page_number = page_number
        self.block_index = block_index
        self.isParagraph = isParagraph
        return

    @staticmethod
    def MakeParagraphBlock()->"CTextBlock":
        res = CTextBlock("",0,0)
        res.isParagraph = True
        return res

def isCharEndLine(ch)->bool:
    if ch in [',','.','!','?']:
        return True
    return False
def yieldItemsFromBlock(block):
    if "lines" in block:  # this checks if it's a text block
        for line in block["lines"]:
            yield line
    return

def getBBox4Element(elem:typing.Dict)->typing.Tuple[float,float,float,float]:
    res = None
    if 'bbox' in elem:
        res = elem['bbox']
    return res

def getTextFromBlock(block):
    res_text = ''
    if "lines" in block:  # this checks if it's a text block
        text_in_block = []
        for line in block["lines"]:
            #text_in_line = []
            for span in line["spans"]:
                # res_text += span["text"]
                text_in_block.append(span["text"])
                #print(f"Font size: {span['size']}, Text: {span['text']}")
        res_text += ' '.join(text_in_block)
    """
    if (len(res_text)>0)and( not isCharEndLine(res_text[-1]) ):
        res_text += '. '
    res_text +='\n'"""
    return res_text


def isTextEnd_notSentence(text: str) -> bool:
    if not text: return False
    if len(text) == 0: return False
    punctuation = ['.', '!', '?']
    text_end = text[-10:].strip()
    if not text_end: return False
    if text_end[-1] in punctuation:
        return False
    else:
        return True
    return False


class CEpubReader:
    def __init__(self, epub_path:str, path_out):
        self.epub_path = epub_path
        self.path_out = path_out
        self.median_bbox_text = None # bbox mediana - for check new paragraph
        return

    def extract_text_from_epub(self):
        assert self.epub_path is not None
        assert self.path_out is not None
        assert os.path.exists(self.epub_path),f'File {self.epub_path} not found'


        return

    def yieldBookItems(self, doc: ebooklib.epub.EpubBook):
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            page_text = ''

            for ix, block in enumerate(blocks):
                yield page_num, ix, block
        return

    def isBlockNewParagraph(self, block:typing.Dict):
        if self.median_bbox_text is None: return False

        bbox_positions = []
        for line_item in yieldItemsFromBlock(block):
            bbox = getBBox4Element(line_item)
            if not bbox: continue
            bbox_positions.append(bbox[0])
            break
        if len(bbox_positions)==0: return False

        if bbox_positions[0]>self.median_bbox_text+5: return True
        return False


    def calcMedianaBBox(self, doc: ebooklib.epub.EpubBook):
        bbox_positions = self.GetBlockLinesBBoxes(doc)
        med = np.median(np.array(bbox_positions))
        print(med)
        self.median_bbox_text = med
        return self.median_bbox_text

    def GetBlockLinesBBoxes(self, doc):
        bbox_positions = []
        for page_num, page, block in self.yieldBookItems(doc):
            for line_item in yieldItemsFromBlock(block):
                bbox = getBBox4Element(line_item)
                if not bbox: continue
                bbox_positions.append(bbox[0])
        return bbox_positions

    def checkTypeFomat(self, doc)->TextBlockType:
        cnt_lines_per_block = []
        block_len = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            page_text = ''
            for ix, block in enumerate(blocks):
                text_from_block = getTextFromBlock(block)
                if len(text_from_block)!=0:
                    block_len.append( len(text_from_block) )
                if 'lines' in block:
                    cnt_lines_per_block.append( len(block["lines"]) )
        block_text_size = np.median(np.array(block_len))
        lines_per_block_lne = np.median(np.array(cnt_lines_per_block))
        if abs( lines_per_block_lne-1)<1.0:
            return TextBlockType.LinePerBlock
        return TextBlockType.Default

    def CombineSplittedLines(self, txt:typing.List[str]):
        res = []
        for ix, l in enumerate(txt):
            if (len(l.strip())==0):continue;
            if len(res)==0:
                res.append(l.rstrip())
                continue
            l_prev = res[-1]
            if l_prev[-1] == '-':
                res[-1] = res[-1].rstrip()[:-1] + l.strip()
            else:
                res.append(l.rstrip())
        return res

    def readEpubDoc_BlockAsSingleLine(self, doc)->typing.List[CTextBlock]:
        block_store = []
        bbox_offset = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            for ix, block in enumerate(blocks):
                bbox_offset.append(  block['bbox'][0] )
        bbox_offset_m = np.median(bbox_offset)
        print(f'Median offset lines {bbox_offset_m}')

        bbox_store = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            page_text = ''
            text_items = []
            for ix, block in enumerate(blocks):
                bbox_store.append(( page_num, block ))
        text_store = []
        for page_num,block in bbox_store:
            text_from_block = getTextFromBlock(block)
            if 'lines' not in block: continue
            isNewParagraph = block['bbox'][0]>bbox_offset_m+10
            lines_x_offset = block['lines'][0]['bbox'][0]
            if lines_x_offset > bbox_offset_m+10:
                isNewParagraph = True

            if isNewParagraph:
                text_store = self.CombineSplittedLines(text_store)
                block_store.append(CTextBlock(' '.join(text_store),
                                              page_number=page_num,
                                              block_index=ix,
                                              isParagraph=False))
                text_store = []
                block_store.append(CTextBlock(' ',
                                              page_number=page_num,
                                              block_index=ix,
                                              isParagraph=isNewParagraph))
            text_store.append(text_from_block)

        # fix line splitting
        text_store = self.CombineSplittedLines(text_store)
        block_store.append(CTextBlock(' '.join(text_store),
                                      page_number=page_num,
                                      block_index=ix,
                                      isParagraph=False))
        return block_store

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            page_text = ''
            text_items = []
            for ix, block in enumerate(blocks):
                text_from_block = getTextFromBlock(block)
                isNewParagraph = self.isBlockNewParagraph(block)
                if isNewParagraph and (text_from_block[0] == '"'):
                    isNewParagraph = False
                if isNewParagraph:
                    print('New paragraph->', text_from_block)
                if not isNewParagraph:
                    text_items.append(text_from_block)
                    continue
                else:
                    text = ' '.join(text_from_block)
                    block_store.append(CTextBlock(text,
                                                  page_number=page_num,
                                                  block_index=ix,
                                                  isParagraph=isNewParagraph))
            continue
        return block_store

    def read_epub2(self, file_path):
        assert os.path.exists(file_path)
        doc = fitz.open(file_path)
        text = ""

        self.calcMedianaBBox(doc)

        type_text_formating = self.checkTypeFomat(doc)
        print(type_text_formating)

        block_store = []
        if type_text_formating==TextBlockType.LinePerBlock:
            block_store = self.readEpubDoc_BlockAsSingleLine(doc)
        else:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("dict")["blocks"]
                page_text = ''

                for ix, block in enumerate(blocks):
                    text_from_block = getTextFromBlock(block)
                    if 'accordance with the instructions' in text_from_block:
                        print(text_from_block)
                    isNewParagraph = self.isBlockNewParagraph(block)
                    if isNewParagraph and (text_from_block[0]=='"'):
                        isNewParagraph = False
                    if isNewParagraph:
                        print('New paragraph->', text_from_block)


                    block_store.append(CTextBlock(text_from_block,
                                                  page_number=page_num,
                                                  block_index=ix,
                                                  isParagraph=isNewParagraph))
                    continue
                    if (ix == 0) and (isTextEnd_notSentence(text)):
                        text += ' ' + text_from_block
                        continue
                    else:
                        page_text += text_from_block
                    if 'The central part of Illusions Perdues' in text_from_block:
                        print(page_text)
                        getTextFromBlock(block)

                    if page_text[-1] != '\n':
                        page_text += ' '

                dict_ = page.get_text('dict')
                # page_text = page.get_text()
                text += page_text

        text_items = []
        block_processed: typing.List[CTextBlock] = []

        block_paragraph = [ [ix, b] for ix, b in enumerate(block_store) if block_store[ix].isParagraph ]
        if len(block_paragraph)==0:
            block_paragraph = [[ix, b] for ix, b in enumerate(block_store) ]
        assert len(block_paragraph)>0


        for block in block_store:
            if len(block_processed) == 0:
                block_processed.append(block)
                continue
            prev_block = block_processed[-1]
            # check, is need combine in one
            if block.isParagraph:
                # fix prev bloc, if need
                if (isTextEnd_notSentence(prev_block.text)):
                    prev_block.text += '. '
                block.text = '\t' + block.text
            elif ((isTextEnd_notSentence(prev_block.text)) and
                    (prev_block.page_number != block.page_number)):
                block_processed[-1].text = block_processed[-1].text.rstrip() + ' ' + block.text
                continue

            block_processed.append(block)
            continue

        block_store = block_processed
        for block in block_store:
            if isTextEnd_notSentence(block.text):
                block.text += '.'
            continue

        text_items = []
        for text_block in block_store:
            text_items.append(text_block.text)

        text = '\n'.join(text_items)

        return text

    def read_epub(file_path):
        book = pyepub.PyEpub.from_file(file_path)
        content = ''

        for doc, html in book.get_content().items():
            soup = BeautifulSoup(html, features="html.parser")
            content += soup.get_text(separator='\n')

        return content

    def extract_text_from_epub2(self) -> bool:
        res = True
        try:
            res_text = extract_text_from_epub(self.epub_path)
            res_text = re.sub(r'([a-z])- *\n', r'\1', res_text)
            res_text = re.sub(r'-\n+', '', res_text)
            res_text = re.sub(r'-\n+', '', res_text)
            file_name = getPath_change_file_extension(pahttext)
            print('Save in file', file_name)
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(res_text)
        except Exception as e:
            print(e)
            res = False

        return res

    def extract_text_epub_v2(self):
        res_text = self.read_epub2(self.epub_path)
        res_text = re.sub(r'([a-z])- *\n', r'\1', res_text)
        res_text = re.sub(r'-\n+', '', res_text)
        res_text = re.sub(r'-\n+', '', res_text)
        res_text = (res_text.replace('.”','”.').replace(',”','”,')
                    .replace('!”','!”.').replace('?”','?”.').replace('”..','”.'))
        # file_name = getPath_change_file_extension(pahttext)
        # print('Save in file', file_name)
        with open(self.path_out, 'w', encoding='utf-8') as f:
            f.write(res_text)
        return

    def ExtractText(self):
        return self.extract_text_epub_v2()


def getPath_change_file_extension(file_path, new_extension='txt'):
    base = os.path.splitext(file_path)[0]
    new_file_path = base +'.'+ new_extension
    return new_file_path



def extract_text_pipe( pahttext:str, pathFileOut:str ):
    ext_reader = CEpubReader(pahttext, pathFileOut)
    ext_reader.ExtractText()
    return


def main():
    pahttext = r""
    path_out=r""
    ext_reader = CEpubReader(pahttext, path_out)
    ext_reader.ExtractText()
    return

if __name__ == "__main__":
    # Test function here
    main()
