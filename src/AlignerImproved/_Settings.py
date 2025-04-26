import dataclasses

@dataclasses.dataclass
class ConfigApp__:
    g_Model_Name: str = None
    DIST_EDGE: float = None
    DIST_EDGE_ClearPrologs: float = None
    EMB_SHAPE_VALUE:int = 0

    IsUseRareLang:bool = False

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigApp, cls).__new__(cls)
            cls._instance.init_once()
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
        return

    def setLange(self, lang_src:str, lang_dst:str):
        if ( lang_src not in LANG_POPULAR )or( lang_dst not in LANG_POPULAR):
            self.IsUseRareLang = True
            self.init_once()
        return

    def init_once(self):
        self.g_Model_Name: str = MODELS_AVALIABLE[0]
        if self.g_Model_Name == MODELS_AVALIABLE[0]:
            self.DIST_EDGE = DIST_EDGE_v_sentence_transformer_multilingual
            self.EMB_SHAPE_VALUE = EMB_SHAPE_sentence_transformer_multilingual
            self.DIST_EDGE_ClearPrologs = DIST_EDGE_ClearPrologs_v_sentence_transformer_multilingual
            if self.IsUseRareLang:
                self.DIST_EDGE_ClearPrologs = DIST_EDGE_ClearPrologs_v_sentence_transformer_multilingual_Rare_lang
        if self.g_Model_Name == MODELS_AVALIABLE[1]:
            self.DIST_EDGE = DIST_EDGE_v_sentence_transformer_multilingual_labse
            self.EMB_SHAPE_VALUE = EMB_SHAPE_sentence_transformer_multilingual_labse
            self.DIST_EDGE_ClearPrologs = DIST_EDGE_ClearPrologs_v_sentence_transformer_multilingual_labse
        return

def GetAppSettings()->ConfigApp:
    return ConfigApp()


    
