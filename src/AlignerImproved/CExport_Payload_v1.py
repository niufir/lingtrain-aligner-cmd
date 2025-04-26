from dataclasses import dataclass

from src.AlignerImproved.PayloadModels.CTextAlignItem import CTextAlignItem

MARKER_VERSION_V1 = 'version_1.0'
@dataclass
class CExport_Payload_v1:
    version:str
    data:list[CTextAlignItem] = None
    def __init__(self, version:str=MARKER_VERSION_V1, data:list[CTextAlignItem]=None):
        self.version = version
        self.data = data
        return
    def setData(self, data:list[CTextAlignItem]):
        self.data = data
        return


    