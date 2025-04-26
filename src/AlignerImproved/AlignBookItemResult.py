import typing

from dataclasses import dataclass

from PayloadModels.CTextAlignItem import CTextAlignItem


@dataclass
class AlignBookItemResult:
    AlignData:typing.List[CTextAlignItem] = None
    TextSizeFrom:int = 0
    TextSizeTo:int = 0
    ErrorsFrom:int = 0
    ErrorsFromPers:float = 0.0
    ErrorsTo:int = 0
    def __init__(self):
        return

    def setAlignData(self, data:typing.List[CTextAlignItem]):
        assert type(data) is list
        self.AlignData:typing.List[CTextAlignItem] = data
        self.calcStats()
        return

    def calcStats(self):
        size_from = 0
        size_to = 0
        errors_from = 0
        for item in self.AlignData:
            size_from += len(item.txt_from)
            size_to += len(item.txt_to)
            if item.isValid == False:
                errors_from += len(item.txt_from)

        self.TextSizeFrom = size_from
        self.TextSizeTo = size_to
        self.ErrorsFromPers = float(errors_from)/float(size_from)
        return


        return
