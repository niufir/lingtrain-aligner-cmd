import re

from bs4 import BeautifulSoup
import os, sys
import xml.etree.ElementTree as ET

def extract_encoding(xml_declaration):
    match = re.search('encoding="([^"]*)"', xml_declaration)
    if match:
        return match.group(1)
    else:
        return None


class FB2_Reader:
    def __init__(self, pathfile:str, path_out:str=None):
        assert os.path.exists(pathfile)
        assert path_out is not None and (len(path_out)>0)
        self.pathfile = pathfile
        self.path_out = path_out
        self.m_cont = ''
        self.m_TreeItems = None
        return

    def readFB2File(self):
        encoding = self.getEncodingFromFile(self.pathfile)
        print('Encoding:', encoding)
        if encoding is None: return None
        with open( self.pathfile, 'r', encoding=encoding) as file:
            contents = file.read()
        return contents;

    def getEncodingFromFile( self, fileName ):
        line=''
        with open(fileName,'r',errors='ignore') as f:
            line=f.readline()
        return self.extract_encoding(line)

    def extract_encoding(self, xml_declaration):
        match = re.search('encoding="([^"]*)"', xml_declaration)
        if match:
            return match.group(1)
        else:
            return None
        return None

    def extract_text_from_fb2(self, file_path):

        encoding = self, self.getEncodingFromFile(file_path)
        print('Encoding:', encoding)
        if encoding is None: return None
        with open(file_path, 'r', encoding=encoding) as file:
            contents = file.read()
        print('size readed text',len(contents))
        g_cont = contents

        soup = BeautifulSoup(contents, 'xml')
        text = [element.text for element in soup.find_all('p')]
        el_all =  [element for element in soup.find_all('p')]
        return '\n'.join(text), el_all

    def getPath_change_file_extension(self,file_path, new_extension='txt'):
        base = os.path.splitext(file_path)[0]
        new_file_path = base +'.'+ new_extension
        return new_file_path


    def printTail(self,dt):
        if dt is None: return ''
        return str(dt)

    def item2str(self, item):
        res = self.printTail( item.text )
        if ( (item.tail is not None) and(len(item.tail)>0)and( '\n' in item.tail ) ):
                res = '\t' + res
        for i in item:
            res += self.printTail(i.text) + self.printTail(i.tail)
        return res


    def extarctTextFromDB2_v2(self, isDebug:bool=False):
        def remove_braces(s):
            return re.sub(r'\{.*?\}', '', s)

        self.cont = self.readFB2File()
        tree = ET.ElementTree(ET.fromstring(self.cont))
        items = list( tree.getroot().iter())
        self.TreeItems = items

        texts = []
        for ix,item in enumerate(items):

            tg_cleared = remove_braces(item.tag)
            #print(item.text)
            if tg_cleared != 'p': continue
            tail = ' '.join([child.tail for child in item if child.tail])
            text = item.text if item.text is not None else ''
            prefix = ''
            if isDebug:
                prefix = f'{ix} ~~~~ '
            cur_text = prefix + self.item2str( item )
            if 'Глава' in cur_text:
                pass
            texts.append( cur_text )

        sentence_endings = ['.', '!', '?']
        for ix in range(1,len(texts)-1):
            next_line = texts[ix+1]
            if next_line[0] == '\t':
                if texts[ix][-1] not in sentence_endings:
                    texts[ix] += '. '

        text = '\n'.join(texts)
        self.save_to_text_file( text )
        return

    def save_to_text_file(self, text):
        with open(self.path_out, 'w', encoding='utf-8') as f:
            f.write( text )
        print(f"Text successfully saved to {self.path_out}")
        return self.path_out
    

def extract_text_pipe( pahttext:str, pathFileOut:str ):
    ext_reader = FB2_Reader( pahttext, pathFileOut )
    ext_reader.extarctTextFromDB2_v2()
    return


def main():
    # Example usage:
    file_path = r""
    file_out = r""
    extract_text_pipe( file_path, file_out )
    return

if __name__ == "__main__":
  main()
