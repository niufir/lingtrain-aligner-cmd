from logging import Logger

import typing, os


class SingletonLoggerHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonLoggerHelper, cls).__new__(cls)
            cls._instance.__singleton_init__()
        return cls._instance

    def __init__(self,):
        return
    def SetLogger(self , ext_logger:Logger):
        self.ext_logger = ext_logger
        return

    def reset(self):
        self.__SummaryInfo: typing.List[str] = []
        return

    def setPathSummaryLog(self, cumulLogPaht:str):
        self.sammaryLogPath = cumulLogPaht
        return
    def __singleton_init__(self):
        self.reset()
        self.ext_logger:Logger = None
        self.sammaryLogPath = None
        return

    def logToSummary(self, msg: str):
        self.__SummaryInfo.append(msg)
        if self.ext_logger:
            self.ext_logger.info(msg)
        else:
            print(msg)
        return

    def printSummary(self):
        print("Summary Info:")
        for i in self.__SummaryInfo:
            print(i)

        if self.sammaryLogPath:
            with open(self.sammaryLogPath, 'a',encoding='utf-8') as f:
                for i in self.__SummaryInfo:
                    f.write(i+'\n')
                    self.ext_logger.info(i)
        return

    def Info(self, msg: str):
        if self.ext_logger:
            self.ext_logger.info(msg)
        else:
            print(msg)
        return
    def info(self, msg: str):
        self.Info(msg)
        return
    def Error(self, msg: str):
        if self.ext_logger:
            self.ext_logger.error(msg)
        return
    def Trace(self, msg: str):
        print(msg)
        return

def GetSingLogger()->SingletonLoggerHelper:
    return SingletonLoggerHelper()