from dataclasses import dataclass


@dataclass
class CTextAlignItem:

    txt_from:str = ''
    txt_to:str = ''
    isValid:bool = False
    cos_dist:float = -1.0
    manhattan_dist:float = -1.0

    def __init__(self,txt_from: str, txt_to:str, isValid=True):
        assert isinstance(txt_from, str)
        assert isinstance(txt_to, str)
        self.txt_from = txt_from
        self.txt_to = txt_to
        self.isValid = isValid
        self.cos_dist = -1.0
        self.manhattan_dist = -1.0
        return
    def setWrong(self):
        self.isValid = False
        return

    def setDistances(self, cos_dist:float, manhattan_dist:float):
        self.cos_dist = cos_dist
        self.manhattan_dist = manhattan_dist
        return

    def ToDict(self):
        return {
            'txt_from': self.txt_from,
            'txt_to': self.txt_to,
            'isValid': self.isValid,
            'cosDist':float(self.cos_dist),
            'manhattanDist':float(self.manhattan_dist),
        }
