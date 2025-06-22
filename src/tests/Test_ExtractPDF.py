# test_sample.py
import typing

import pytest
import os,sys


Path_TestData = os.path.join(os.path.dirname(__file__), 'TestData','Extract_PDF')
Out_dir = os.path.join(Path_TestData,'Out')
os.makedirs(Out_dir,exist_ok=True)

assert os.path.exists(Path_TestData)
sys.path.append(os.path.dirname(__file__))
from src.AlignerImproved.Extract_PDF import CHelperPdfText_Extact


def make_output_filepath(fpath)->str:
    return os.path.join(Out_dir, os.path.basename(fpath) + '.txt')


def readTextFile(file_path: str)->typing.List[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        contents = file.read()
    return [l for l in contents.split('\n') if len(l)>0]


def test_DorianGrey_KA():

    pdf_name = os.path.join(Path_TestData, 'DorianGrey_KA.pdf')
    output_path = make_output_filepath(pdf_name)
    extrhlp =CHelperPdfText_Extact( pdf_name, output_path )
    #extrhlp.number_page_dbg = 20
    extrhlp.RunExtract()

    return

def test_MonteKristo_KA():
    pdf_name = os.path.join(Path_TestData, 'grafi-monte-kristo_KA.pdf')
    output_path = make_output_filepath(pdf_name)
    extrhlp = CHelperPdfText_Extact( pdf_name, output_path )
    extrhlp.RunExtract()
    res_text = '\n'.join(readTextFile(output_path))
    assert "თქვენ დიხანს არ გეყვარებათ... ადამიანი, რომელიც თქვენს მსგავსად" in res_text
    assert "ჩვენი მედილეგეების სურვილების წინააღმდეგ, ეს ცოდნის ის სხივებია" in res_text
    return

def test_pdf_v2():

    pdf_name = os.path.join(Path_TestData, 'Machiavelli,+The+Prince.pdf')
    output_path = make_output_filepath(pdf_name)
    extrhlp =CHelperPdfText_Extact( pdf_name, output_path)
    # extrhlp.number_page_dbg = 124
    extrhlp.RunExtract()
    res_text =  '\n'.join( readTextFile(output_path) )
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path)>1000, f"File size is {os.path.getsize(output_path)}"
    assert 'taxation of Tuscany and Naples' in res_text
    assert '_ThePrince_TXT.indd' not in res_text
    assert 'an appeal to conquer italy and free it' not in res_text
    print(f"File size is {os.path.getsize(output_path)}")
    return





if __name__ == "__main__":
    pytest.main()
