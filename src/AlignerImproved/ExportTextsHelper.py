import typing

from src.AlignerImproved.PayloadModels.CTextAlignItem import CTextAlignItem

MARKER_VERSION_V1 = 'version_1.0'

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
