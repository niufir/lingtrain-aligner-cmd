import typing
import os, sys

from Settings import GetAppSettings
from lingtrain_aligner import preprocessor, splitter, aligner, resolver, reader, helper, vis_helper

def splitTextOnSmallParts(text1:typing.List[str], text2:typing.List[str],
                          lang_from:str, lang_to:str,
                          db_path_tmp:str = None,
                          modelname:str = 'sentence_transformer_multilingual'):
    global db_path

    text1_prepared = preprocessor.mark_paragraphs(text1)
    text2_prepared = preprocessor.mark_paragraphs(text2)

    splitted_from = splitter.split_by_sentences_wrapper(text1_prepared, lang_from)
    splitted_to = splitter.split_by_sentences_wrapper(text2_prepared, lang_to)
    if db_path_tmp is not None: db_path4work = db_path_tmp
    else:db_path4work = db_path
    if os.path.isfile(db_path4work):
        os.unlink(db_path4work)

    aligner.fill_db(db_path4work, lang_from, lang_to, splitted_from, splitted_to)

    batchsize = 300
    batchlist = list( range( int( len(splitted_to)//batchsize) +2 ) )
    # batch_ids = [0,1]

    aligner.align_db(db_path4work,
                     GetAppSettings().g_Model_Name,
                     batch_size=batchsize,
                     window=80,
                     batch_ids=batchlist,
                     save_pic=False,
                     embed_batch_size=10,
                     normalize_embeddings=True,
                     show_progress_bar=True
                     )

    conflicts_to_solve, rest = resolver.get_all_conflicts(db_path4work, min_chain_length=2, max_conflicts_len=6, batch_id=-1)

    #resolver.get_statistics(conflicts_to_solve)
    #resolver.get_statistics(rest)

    steps = 3
    batch_id = -1 #выровнять все доступные батчи

    for i in range(steps):
        conflicts, rest = resolver.get_all_conflicts(db_path4work, min_chain_length=2+i, max_conflicts_len=6*(i+1), batch_id=batch_id)
        resolver.resolve_all_conflicts(db_path4work, conflicts, model_name, show_logs=False)

        """
        vis_helper.visualize_alignment_by_db(db_path, output_path="img_test1.png", lang_name_from=lang_from, lang_name_to=lang_to, batch_size=400, size=(600,600), plt_show=True)
        """

        if len(rest) == 0: break
    paragraphs_from, paragraphs_to, meta,sent_counter_dict  = reader.get_paragraphs(db_path4work)
    res = []
    for p_from , p_to in zip( paragraphs_from['from'], paragraphs_from['to'] ):
        res.append( [p_from, p_to] )
    return res