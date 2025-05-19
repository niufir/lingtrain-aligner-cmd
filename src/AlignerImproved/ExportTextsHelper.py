import sys, os
import typing
import json
from dataclasses import dataclass

sys.path.append( os.path.dirname(os.path.dirname(os.path.dirname(__file__)) ) )

from src.AlignerImproved.AlignBookItemResult import AlignBookResult
from src.AlignerImproved.PayloadModels.CTextAlignItem import CTextAlignItem

MARKER_VERSION_V1 = 'version_1.0'
MARKER_VERSION_V2 = 'version_2.0'

@dataclass
class ExportData_V2:
    version: str
    data_forward_langs_direction: typing.List[CTextAlignItem]
    data_backward_langs_direction: typing.List[CTextAlignItem]
    author: typing.Optional[str]
    title: typing.Optional[str]
    year: typing.Optional[str]

    def to_dict(self):
        return {
            'version': self.version,
            'data_forward_langs_direction': self.data_forward_langs_direction,
            'data_backward_langs_direction': self.data_backward_langs_direction,
            'author': self.author,
            'title': self.title,
            'year': self.year
        }

class ExportTextsHelper:
    def __init__(self):
        return

    @staticmethod
    def exportAsJson_v1(res_aligns:typing.List[CTextAlignItem], path_file:str):
        res = {}
        res['version'] = MARKER_VERSION_V1
        res['data'] = [ item.ToDict() for item in res_aligns ]
        import json
        with open(path_file, "w", encoding='utf-8') as f:
            json.dump(res, f)
        return

    @staticmethod
    def exportAsJson_v2(    book_data:AlignBookResult, 
                            path_file:str,
                            author:str=None,
                            title:str=None,
                            year:str=None):

        res = ExportData_V2(
            version=MARKER_VERSION_V2,
            data_forward_langs_direction=[item.ToDict() for item in book_data.JoinBookParts_ForwardDir()],
            data_backward_langs_direction=[item.ToDict() for item in book_data.JoinBookParts_BackwardDir()],
            author=author,
            title=title,
            year=year
        )
        with open(path_file, "w", encoding='utf-8') as f:
            json.dump(res.to_dict(), f)
        return

    @staticmethod
    def save_aligng3file( res_aligns:typing.List[CTextAlignItem], path_file:str ):
        print('Save aliging data to file:', path_file)
        with (open(path_file, 'w', encoding='utf-8' ) as f):
            for item in res_aligns:
                p_from, p_to  = item.txt_from, item.txt_to
                p_from = ExportTextsHelper.formarPrintableTextLine(p_from)

                p_to = ExportTextsHelper.formarPrintableTextLine(p_to)
                f.write(f'[{item.isValid}]\n')
                f.write(p_from)
                f.write('\n')
                f.write(p_to)
                f.write('\n\n')
        return

    @staticmethod
    def formarPrintableTextLine(line:str)->str:
        res = ( line.replace('%%%%%.','')
                .replace('%%%%%?','')
                .replace('%%%%%%%%%%%%%%%','\n\n')
                .replace('%%%%%','\n')
                )

        return res

    @staticmethod
    def SaveSplitText2File(lines: typing.List[str], path_file: str):
        with open(path_file, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line)
                f.write('\n')
        return
