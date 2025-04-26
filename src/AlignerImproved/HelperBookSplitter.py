import typing

from tqdm import tqdm

from src.AlignerImproved.LoggerHelper import SingletonLoggerHelper
from src.AlignerImproved.MainAligner import BookSplitSection
from src.AlignerImproved.ParagraphMaker import ends_with_roman_numeral, isChapterPresent, calcMedDist

gLogger = SingletonLoggerHelper()
class CHelper_CleanerTexts:

    @staticmethod
    def validateBlockSize(size_bk_from:int, size_bk_to:int, kf_from_to:float)->bool:
        v = size_bk_from/size_bk_to*kf_from_to
        v = abs(1-v)
        return v<0.2

    @staticmethod
    def splitBookRawText(booksection:BookSplitSection):
        CHelper_CleanerTexts.gLogger.info('Call split book from small parts, using find similarity' + '\n' +'\t'*13 + f'ix_to:{booksection.ix_to}')
        start_pos = 0
        start_pos_small_step=0
        start_pos2 = 0
        clhlp = CHelper_CleanerTexts()
        clhlp.setTexts(booksection.split_from, booksection.split_to)
        clhlp.setEmbidingData(booksection.emb1, booksection.emb2)
        res_sections:typing.List[BookSplitSection] = []

        kf_fr_to = 1.0/( float(booksection.sizeText_From()/booksection.sizeText_To()) )
        gLogger.info(f'{"\t"*5} size correct coeff kf={kf_fr_to}')
        gLogger.info('Find similar parts:')
        tab_prefix = '\t'*5

        while True:
            ix = booksection.findNextPossibleHookItem(start_pos,start_pos_small_step)
            if ix == -1: break # possible end text
            same_text_res = clhlp.findSamePartText(ix, booksection.split_from, wnd_size=10)
            # assert same_text_res.isSameExists # TODO:  need realize code for case, when not found same text part

            gLogger.info( tab_prefix + f'find similar part with index:{ix} isSameExist:{same_text_res.isSameExists}')
            if same_text_res.isSameExists:
                if same_text_res.indx_txt_opposite<=start_pos2:
                    gLogger.info(tab_prefix+'Error find similar part of text. Possible text shufled')
                    same_text_res.isSameExists = False

            if same_text_res.isSameExists:
                start_pos_small_step=0
                if same_text_res.indx_txt_opposite<=start_pos2:
                    gLogger.info(tab_prefix+'Error find similar part of text. Possible text shufled')
                    return []

                section_new = BookSplitSection(
                    booksection.split_from[start_pos:same_text_res.indx_txt_main],
                    booksection.split_to[start_pos2:same_text_res.indx_txt_opposite],
                    booksection.emb1[start_pos:same_text_res.indx_txt_main],
                    booksection.emb2[start_pos2:same_text_res.indx_txt_opposite],
                    ix_from=start_pos, ix_from_last=same_text_res.indx_txt_main,
                    ix_to=start_pos2, ix_to_last=same_text_res.indx_txt_opposite
                )
                gLogger.info(tab_prefix +f'count section:{len(res_sections)}'+ f'\tsection info:{section_new.TextInfo()}')
                if len(res_sections) ==7:
                    pass

                size_from_bytes = section_new.sizeText_From()
                size_to_bytes = section_new.sizeText_To()
                if validateBlockSize(size_from_bytes, size_to_bytes, kf_fr_to):
                    res_sections.append(section_new)
                    start_pos = same_text_res.indx_txt_main
                    start_pos2 = same_text_res.indx_txt_opposite
                    continue
                else:
                    gLogger.info(tab_prefix + f'skip section by validation block size')

            start_pos_small_step+= ix + 1 - start_pos
            continue;
            #ix = booksection.findNextPossibleHookItem(start_pos + start_pos_small_step)


            print(same_text_res)

        res_sections.append(BookSplitSection(
            booksection.split_from[start_pos:],
            booksection.split_to[start_pos2:],
            booksection.emb1[start_pos:],
            booksection.emb2[start_pos2:],
            ix_from=start_pos, ix_from_last=-1,
            ix_to=start_pos2, ix_to_last=-1
        ))
        if len(res_sections) == 0:
            res_sections = [booksection]
        return res_sections

    @staticmethod
    def split_using_parahrps_markers(emb2, emb_1, splitted_from, splitted_to):
        chapter_indexes_1, chapter_indexes_2 = CHelper_CleanerTexts.findChapters(splitted_from, splitted_to)
        indexMapping = {}
        for ix in tqdm(chapter_indexes_1[1:]):
            dist_store = []
            for ix2 in chapter_indexes_2:
                if len(emb_1) == 0:
                    continue
                if len(emb2) == 0:
                    continue
                try:
                    pass
                    dist_store.append((ix2, calcMedDist(ix, ix2, emb_1, emb2)))
                except:
                    pass
                dist_store.append((ix2, calcMedDist(ix, ix2, emb_1, emb2)))

            dist_store.sort(key=lambda x: x[1])
            if len(dist_store) == 0:
                indexMapping[ix] = None
                continue
            nearest_index = dist_store[0][0]
            indexMapping[ix] = dist_store[0]
        indexMapping = {k: v for k, v in indexMapping.items() if (v) and (v[1] < 0.83)}
        index_store = [[k, v] for k, v in indexMapping.items()]
        index_store.sort(key=lambda x: x[0])
        prev_ix_1 = 0
        prev_ix_2 = 0
        books_splits = []
        for index1, v in tqdm(index_store):
            index2, distval = v

            text_p1 = splitted_from[prev_ix_1: index1]
            emb_p1 = emb_1[prev_ix_1: index1]

            text_p2 = splitted_to[prev_ix_2: index2]
            emb_p2 = emb2[prev_ix_2: index2]

            bk_split = BookSplitSection(text_p1, text_p2, emb_p1, emb_p2,
                                        ix_from=prev_ix_1, ix_from_last=index1,
                                        ix_to=prev_ix_2, ix_to_last=index2,
                                        )
            books_splits.append(bk_split)
            prev_ix_1 = index1
            prev_ix_2 = index2
        # add last data
        bk_split = BookSplitSection(splitted_from[prev_ix_1:], splitted_to[prev_ix_2:], emb_1[prev_ix_1:], emb2[prev_ix_2:],
                                    ix_from=prev_ix_1, ix_from_last=-1,
                                    ix_to=prev_ix_2, ix_to_last=-1,
                                    )
        books_splits.append(bk_split)
        return books_splits

    @staticmethod
    def SplitBookOnSmallParts(emb2, emb_1, splitted_from, splitted_to)->typing.List[BookSplitSection]:
        assert len(emb2) == len(splitted_to)
        assert len(emb_1) == len(splitted_from)
        books_splits = CHelper_CleanerTexts.split_using_parahrps_markers(emb2, emb_1, splitted_from, splitted_to)
        gLogger.logToSummary('Using Paragraph Splitting - Sizes splitted block (using paragraph):')
        [gLogger.logToSummary('\t size block in KB ' + str(bk.sizeText_From_kb())) for bk in books_splits]
        books_splites_res:typing.List[BookSplitSection] = []
        CHelper_CleanerTexts.printBookSplitItems(books_splits)
        for cur_sp_block in books_splits:
            if cur_sp_block.sizeText_From()<1e5:
                books_splites_res.append(cur_sp_block)
                continue
            raw_split_re = CHelper_CleanerTexts.splitBookRawText( cur_sp_block )
            books_splites_res+=raw_split_re

        books_splites_res = BookSplitSection.CombineSmallPartsTogether(books_splites_res)

        print(f'Found {len(books_splites_res)} splits for book')

        # print(f'Find raw split from_text {start_pos}:{same_text_res.indx_txt_main} and to_text {start_pos2}:{same_text_res.indx_txt_opposite}')
        CHelper_CleanerTexts.printBookSplitItems(books_splites_res)
        return books_splites_res
    @staticmethod
    def findChapters(splitted_from:typing.List[str],
                     splitted_to:typing.List[str]) -> (
            typing.Tuple)[typing.List[int], typing.List[int]
    ]:
        chapt_possible1 = []
        chapt_possible2 = []
        for ix,sl in enumerate(splitted_from):
            if not isChapterPresent(sl): continue
            if ix>len(splitted_from)-1:continue
            if splitted_from[ix+1][0]!='\t':continue
            print(sl)
            chapt_possible1.append(ix)

        for ix,sl in enumerate(splitted_to):
            if not isChapterPresent(sl): continue
            if ix>len(splitted_from)-1:continue
            if splitted_to[ix+1][0]!='\t':continue
            print(sl)
            chapt_possible2.append(ix)


        print('line numbers:',chapt_possible1)
        print('line numbers:',chapt_possible2)
        return chapt_possible1,chapt_possible2


