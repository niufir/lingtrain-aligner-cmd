# test_sample.py
import typing

import pytest
import os,sys

# from AlignerImproved.Extarct_EPUB import CEpubReader
from src.AlignerImproved.Extarct_EPUB import CEpubReader

Path_TestData = os.path.join(os.path.dirname(__file__), 'TestData','Extract_EPUB')
Out_dir = os.path.join(Path_TestData,'Out')
os.makedirs(Out_dir,exist_ok=True)

assert os.path.exists(Path_TestData)
sys.path.append(os.path.dirname(__file__))
# from AlignerImproved.Extract_PDF import CHelperPdfText_Extact
from src.AlignerImproved.Extract_PDF import CHelperPdfText_Extact

Path_TestData = os.path.join(os.path.dirname(__file__), 'TestData','Extract_EPUB')
Out_dir = os.path.join(Path_TestData,'Out')
os.makedirs(Out_dir,exist_ok=True)


def make_output_filepath(fpath)->str:
    return os.path.join(Out_dir, os.path.basename(fpath) + '.txt')

def readTextFile(file_path: str)->typing.List[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        contents = file.read()
    return [l for l in contents.split('\n') if len(l)>0]



def test_sample():
    pdf_name = os.path.join(Path_TestData, 'vol_1_31377-images.epub')
    output_path = make_output_filepath(pdf_name)
    extrhlp = CEpubReader( pdf_name, output_path )
    #extrhlp.number_page_dbg = 20
    extrhlp.ExtractText()

    text = '\n'.join( readTextFile(output_path) )
    assert len(text)>0
    assert "broken head, Coppelius had disappeared in the crush and confusion." in text
    assert 'Several years afterwards it was reported that, outside the door of a pretty country house in a remote district, Clara had been seen sitting hand in hand with a pleasant gentleman,' in text
    return

def test_smp_2():
    fpath = os.path.join(Path_TestData, 'El_conde_de_Montecristo_ES.epub')
    output_path = make_output_filepath( fpath )
    extrhlp = CEpubReader( fpath, output_path )
    #extrhlp.number_page_dbg = 20
    extrhlp.ExtractText()

    text = '\n'.join( readTextFile(output_path) )
    assert len(text)>0
    assert "capitán Leclerc deteniéndoos" in text
    return

if __name__ == "__main__":
    pytest.main()
