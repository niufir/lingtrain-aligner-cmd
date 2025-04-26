import typing

SIG_PARAGRAPH_SPLITTER = '%%%%%'

class HelperParagraphSpliter:
    def __init__(self):
        return

    @staticmethod
    def ClearTextFromParagrapSplitter(texts:typing.List[str])->typing.List[str]:
        if type(texts) is str:
            return texts.replace(SIG_PARAGRAPH_SPLITTER,'')
        res = [ l.replace(SIG_PARAGRAPH_SPLITTER,'') for l in texts ]
        return res
