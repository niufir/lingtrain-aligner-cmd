from io import TextIOWrapper
class BookConfig:
    def __init__(self, pathLngSrc: str, pathLngDst: str, lng_abr_src: str, lng_abr_dst: str,
                 pathFileOut: str):
        self.pathLngSrc = pathLngSrc
        self.pathLngDst = pathLngDst
        self.lng_abr_src = lng_abr_src
        self.lng_abr_dst = lng_abr_dst
        self.pathFileOut = pathFileOut
        return

    def openSrcBook(self) -> TextIOWrapper:
        return open(self.pathLngSrc, 'r', encoding='utf-8')

    def openDstBook(self) -> TextIOWrapper:
        return open(self.pathLngDst, 'r', encoding='utf-8')