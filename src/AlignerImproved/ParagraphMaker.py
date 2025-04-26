import typing

import hashlib
import re

import numpy as np
from sklearn.metrics import euclidean_distances


def checkIfRomanNumeral(numeral:str):
    """Controls that the userinput only contains valid roman numerals"""
    if len(numeral ) ==0:
        return False
    numeral = numeral.upper()
    validRomanNumerals = ["M", "D", "C", "L", "X", "V", "I", "(", ")"]
    valid = True
    for letters in numeral:
        if letters not in validRomanNumerals:
            valid = False
            break
    return valid


def ends_with_roman_numeral(s):
    # pattern = r'M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'
    pattern = r'\bM{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\b'
    pattern = r'M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'
    pattern = r'.*(?<=\b)(I|II|III|IV|V|VI|VII|VIII|IX|X|XX|XXX|XL|L|LX|LXX|LXXX|XC|C|CC|CCC|CD|D|DC|DCC|DCCC|CM|M|MM|MMM)(?=\b)$'
    s = s.split(' ')[-1]
    s = re.sub(r'[^a-zA-Z]', '', s)
    return checkIfRomanNumeral(s)


def transformChapterLine(s:str)->str:
    if len(s)>15: return s
    if ends_with_roman_numeral(s):
        s = s+'.'
    return s
def splitStringByPoints(s:str)->str:

    res = s
    while True:
        isFindWrong = False
        s = res
        for ix in range(len(s)-1):

            if s[ix] in [ '.', ',', '!', '?' ]:
                pass
                if s[ix+1] == ' ':continue;
                if (not s[ix-1].isupper())and(s[ix+1].isupper()):
                    res = res[:ix+1] + ' ' + res[ix+1:]
                    isFindWrong = True
                    break # for
        if not isFindWrong: break
        continue
    return res


    items = s.split('.')
    res = []
    if len(items)<2: return s;
    for ix in range(len(items)):
        if len(res)==0:
            res.append(items[ix] + '.')
            continue
        last_char = res[-1][-2]
        if last_char.isupper():
            res[-1] += items[ix] + '.'
        else:
            res[-1]+=' '+items[ix] + '.'
            res.append(items[ix] + '.')
    res_str =''.join(res)
    return res_str

def isChapterPresent(l:str)->bool:
    line_orig = l
    l = l.lower()
    if l.startswith('capítulo '): return True
    if l.startswith('часть '): return True
    # CHAPTER
    if l.startswith('CHAPTER '.lower()): return True
    # Глава
    if l.startswith('Глава '.lower()): return True
    if len(l)>40: return False
    if ends_with_roman_numeral(line_orig): return True # possible need check only one word in line and it digit
    return  False

COUNT_LINES_COMPARE_TEXT_SECTION  = 15
def calcMedDist(ix, ix2, emb1, emb2):
    eslice1 = emb1[ix:ix+COUNT_LINES_COMPARE_TEXT_SECTION]
    eslice2 = emb2[ix2:ix2+COUNT_LINES_COMPARE_TEXT_SECTION]
    dist = euclidean_distances(eslice1, eslice2)
    res = np.median( [ np.min(dist[ix]) for ix in range(dist.shape[0]) ] )
    return res

def calculate_sha1(s):
    hash_object = hashlib.sha1(s.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig

def makeAlignsDirectly(paragraphs):
    return [ [p_from, p_to] for  p_from , p_to in zip(paragraphs['from'], paragraphs['to']) ]
