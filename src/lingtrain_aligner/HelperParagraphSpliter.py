import typing

SIG_PARAGRAPH_SPLITTER = '%%%%%'

class HelperParagraphSpliter:
    def __init__(self):
        return

    @staticmethod
    def ClearTextFromParagrapSplitter(texts:typing.List[str])->typing.List[str]:
        res = [ l.replace(SIG_PARAGRAPH_SPLITTER,'') for l in texts ]
        return res
