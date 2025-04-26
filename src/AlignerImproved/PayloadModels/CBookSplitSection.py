import typing

import numpy as np


class BookSplitSection:
    def __init__(self,
                 split_from:typing.List[str],
                 split_to:typing.List[str],
                 emb1:np.ndarray,
                 emb2:np.ndarray,
                 ix_from:int,
                 ix_from_last:int,
                 ix_to:int,
                 ix_to_last:int,
                 ):
        self.split_from = split_from
        self.split_to = split_to
        self.emb1 = emb1
        self.emb2 = emb2
        self.ix_from = ix_from
        self.ix_from_last = ix_from_last
        self.ix_to = ix_to
        self.ix_to_last = ix_to_last
        return

    def combineBlock(self, block:"BookSplitSection"):
        self.split_from.extend(block.split_from)
        self.split_to.extend(block.split_to)
        self.emb1 = np.concatenate( (self.emb1, block.emb1) )
        self.emb2 = np.concatenate( (self.emb2, block.emb2) )
        self.ix_from_last = block.ix_from_last
        self.ix_to_last = block.ix_to_last
        return

    def sizeText_From_kb(self):
        res = np.sum([len(l) for l in self.split_from])
        return res//1024

    def sizeText_From(self):
        res = np.sum([len(l) for l in self.split_from])
        return res

    def sizeText_To_kb(self):
        res = np.sum([len(l) for l in self.split_to])
        return res//1024

    def sizeText_To(self):
        res = np.sum([len(l) for l in self.split_to])
        return res

    def linesCnt_From(self):
        return len(self.split_from)
    def linesCnt_To(self):
        return len(self.split_to)

    def TextInfo(self)->str:
        tab_prefix = '\t'*13
        res = f"ix_from: {self.ix_from}:{self.ix_from_last}\tix_to: {self.ix_to}:{self.ix_to_last}, block sizes: {self.sizeText_From_kb()}KB:{self.sizeText_To_kb()}KB"
        text_from = f'\n{tab_prefix}'.join( ['']  + self.split_from[:5] )
        text_to = f'\n{tab_prefix}'.join(['']  +  self.split_to[:5] )
        res += '\n' + '\t'*13 + f' TEXT BLOCK FROM:\n {text_from}'
        res += '\n' + '\t'*13 + f'TEXT BLOCK TO:\n {text_to}'
        return res
    def print(self):
        print(self.TextInfo())
        return
    def findNextPossibleHookItem(self, indx_from:int, step_without_gap:int = 0)->int:
        """

        """
        size4skip=1e5
        cumulative_size = 0
        for l_ix in range(indx_from + step_without_gap, len(self.split_from )):

            # skip 100 kb text
            line = self.split_from[l_ix]

            if step_without_gap == 0:
                if cumulative_size < size4skip:
                    cumulative_size += len(line)
                    continue

            wnd_around = self.split_from[l_ix-5:l_ix+5]
            wnd_around = [i for i in wnd_around if len(i)>15]
            if len(wnd_around) <9:
                continue

            if len(line) <50: continue
            return l_ix
        return -1

    @staticmethod
    def printCollection(collection:typing.List['BookSplitSection']):
        for i in collection:
            i.print()
        return

    @staticmethod
    def CombineSmallPartsTogether(books_splites_res:typing.List["BookSplitSection"]) -> typing.List["BookSplitSection"]:
        tmp_books_splites_res = []
        for ix in range(len(books_splites_res)):
            curblock = books_splites_res[ix]
            if len(tmp_books_splites_res) == 0:
                tmp_books_splites_res.append(curblock)
                continue

            if BookSplitSection.isSmallBlockNeedCombine(tmp_books_splites_res[-1]):
                tmp_books_splites_res[-1].combineBlock(curblock)
            elif BookSplitSection.isSmallBlockNeedCombine(curblock):
                tmp_books_splites_res[-1].combineBlock(curblock)
            else:
                tmp_books_splites_res.append(curblock)
        return tmp_books_splites_res
    @staticmethod
    def isSmallBlockNeedCombine(block:'BookSplitSection')->bool:
        Size4Small = 4e3
        if block.sizeText_From()<=Size4Small: return True
        if block.sizeText_To()<=Size4Small: return True
        return False