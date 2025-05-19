import typing

from dataclasses import dataclass, asdict

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

@dataclass
class OrigBookParagrapphs:
    p_from:typing.List[typing.List[str]]
    p_to:typing.List[typing.List[str]]

    def __init__(self):
        self.p_from = []
        self.p_to = []
        return




@dataclass
class AlignBookResult:
    AlignItems_ForwardDirection:typing.List[AlignBookItemResult] # it field contain data for book, aligned with norma language direction
    AlignItems_BackwardDirection:typing.List[AlignBookItemResult]# it filed contain data for book, with reverse langugage direction
    def __init__(self):
        self.AlignItems_ForwardDirection = []
        self.AlignItems_BackwardDirection = []
        return

    def JoinBookParts_ForwardDir(self)->typing.List[CTextAlignItem]:
        res = []
        for item in self.AlignItems_ForwardDirection:
            res += item.AlignData[:]
        return res

    def JoinBookParts_BackwardDir(self)->typing.List[CTextAlignItem]:
        res = []
        for item in self.AlignItems_BackwardDirection:
            res += item.AlignData[:]
        return res

    def GetParagraphs_Dict_Oring_version(self)->typing.Dict[str,str]:
        res = OrigBookParagrapphs()
        for item in self.AlignItems_ForwardDirection:
            for i in item.AlignData:
                res.p_from.append([i.txt_from])
                res.p_to.append([i.txt_to])
        res_dict= asdict(res)
        res_dict['from'] = res_dict['p_from']
        res_dict['to'] = res_dict['p_to']
        return res_dict

    def GetDelemiters_Oring_version(self)->typing.List[int]:
        res =[]
        ix= 1
        for item in self.AlignItems_ForwardDirection:
            for i in item.AlignData:
                res.append(ix)
                ix+=1
        return res

    def GetSentCounters_Orign_version(self)->typing.Dict[str,int]:
        res = {'from':len(self.AlignItems_ForwardDirection),'to':len(self.AlignItems_ForwardDirection)}
        return res

