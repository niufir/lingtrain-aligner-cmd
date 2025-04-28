from dataclasses import dataclass



@dataclass
class ConfigAlignBook:
    source_book_path:str
    dest_book_path:str
    output_book_path:str
    src_book_txt_path:str
    dest_book_txt_path:str

    lng_src:str
    lng_dest:str

    IsMakeOnlySanitizeData:bool = False
    IsTestMode:bool = False
    isBidirect:bool = False
    modelName:str = None

    def __init__(self, source_book_path, dest_book_path, output_book_path,
                 isSkipSanitize:bool=False,
                 isTestMode:bool=False,
                 isBidirect:bool=False,
                 model_name:str=None,):
        self.source_book_path = source_book_path
        self.dest_book_path = dest_book_path
        self.output_book_path = output_book_path
        self.src_book_txt_path = None
        self.dest_book_txt_path = None
        self.IsTestMode = isTestMode
        self.lng_src:str = None
        self.lng_dest:str = None
        self.isSkipSanitize = isSkipSanitize
        self.isBidirect = isBidirect
        self.modelName = model_name
        return
    
    def setTestMode(self):
        self.IsTestMode = True
        return

    def SetLangs(self, lng_src:str, lng_dest:str):
        assert isinstance(lng_src, str)
        assert isinstance(lng_dest, str)
        assert len(lng_src) > 0
        assert len(lng_dest) > 0
        assert lng_src != lng_dest
        self.lng_src = lng_src
        self.lng_dest = lng_dest

        return
