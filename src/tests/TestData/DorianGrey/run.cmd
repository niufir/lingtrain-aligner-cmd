pushd %~dp0

call conda activate nlp312

call chcp 65001

call python D:\projects\GO\langstrain\parrallel_texts_project\lingtrain-aligner\src\AlignerImproved\AlignerCmd.py --pathBookFrom="The Picture of Dorian Gray - Oscar Wilde_en.epub"   --pathBookTo="Уайлд Оскар. Портрет Дориана Грея (сборник) - royallib.com.epub"   --pathBookOut="en-ru.epub" 
