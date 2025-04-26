import os
__g_PathDir_cachingModels = "./models_cache"
__g_DefaultModelName = None


def SetGlobalPathDir_cachingModels(path):
    global __g_PathDir_cachingModels
    if not os.path.exists(path): return
    __g_PathDir_cachingModels = path
    return

def GetGlobalPathDir_cachingModels():
    return __g_PathDir_cachingModels

def SetDefModelName(nn_model_name:str):
    global __g_DefaultModelName
    __g_DefaultModelName = nn_model_name

def GetDefModelName():
    return __g_DefaultModelName