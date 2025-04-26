import os,sys
from dataclasses import dataclass

import pathlib

current_dir = pathlib.Path(__file__).resolve()
parent_dir = current_dir.parent
parent_2up_dir = current_dir.parents[1]

sys.path.append(str(parent_dir))
sys.path.append(str(parent_2up_dir))
from lingtrain_aligner.CacheFolderSettings import SetGlobalPathDir_cachingModels, GetGlobalPathDir_cachingModels

MODELS_AVALIABLE = ["sentence_transformer_multilingual", "sentence_transformer_multilingual_labse"]


DIST_EDGE_v_sentence_transformer_multilingual = 18.5
DIST_EDGE_ClearPrologs_v_sentence_transformer_multilingual = 19.5
DIST_EDGE_ClearPrologs_v_sentence_transformer_multilingual_Rare_lang = 20.7

DIST_EDGE_v_sentence_transformer_multilingual_labse = 22.0
DIST_EDGE_ClearPrologs_v_sentence_transformer_multilingual_labse = 24.0

EMB_SHAPE_sentence_transformer_multilingual = 512
EMB_SHAPE_sentence_transformer_multilingual_labse = 768

LANG_POPULAR = ['ru','en','es','it','fr','de','pl']

@dataclass
class ConfigApp:
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


    
