from langdetect import detect

def detect_lang_4_file(pathfile)->str:
    with open(pathfile, 'r', encoding='utf-8') as f:
        text=[]
        for ix in range(100):
            text.append( f.readline() )
    text = '\n'.join( [i for i in text if i])
    return detect(text)

def detect_language(text):
    try:
        return detect(text)
    except:
        return "Language not detected"

