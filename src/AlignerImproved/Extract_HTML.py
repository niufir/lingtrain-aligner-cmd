import codecs
import logging
import os
import typing


class CHelperHtmlExtractor:
    def __init__(self,pathfile:str, pathOutput:str = None, log_level = logging.DEBUG):
        self.path_pdf = pathfile
        self.path_output = pathOutput
        if self.path_output:
            dir_Log = os.path.dirname(self.path_output)
            assert os.path.isdir(dir_Log)
            log_file_path = os.path.join( dir_Log, 'trace.log')
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(log_level)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)

            logging.basicConfig(filename=log_file_path, level=log_level,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.logger = logging.getLogger(__name__)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(log_level)
            self.logger.debug('Start debugging')
            self.logger.info("Info logging test")
        pass

    def read_default_codepage(self):
        try:
            with codecs.open(self.path_pdf, 'r',errors='ignore') as file:
                html_content = file.read()
        except:
            html_content = None
            pass
        return  html_content

    def Extract(self)->str:
        from bs4 import BeautifulSoup
        try:
            # Open the HTML file
            with codecs.open(self.path_pdf, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except FileNotFoundError:
            self.logger.error(f"File not found: {self.path_pdf}")
            return ""
        except Exception as e:
            self.logger.error(f"Error reading file {self.path_pdf}: {str(e)}")
            html_content = self.read_default_codepage()
            if not html_content:
                return ""

        # Extract text from HTML using BeautifulSoup
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text(separator=" ")
            return text_content.strip()
        except Exception as e:
            self.logger.error(f"Error parsing HTML content with BeautifulSoup: {str(e)}")
            return ""

    def CheckIsLinesEmpyAll(self, text_items:typing.List[str])->bool:
        res = True
        for l in text_items:
            if len(l.strip())>0: return False
        return res

    def lineIsEmpty(self,l:str)->bool:
        return len(l.strip())==0

    def postProcessText(self, text)->str:
        text = text.replace('\r','')
        items = text.split('\n')
        items=[i.strip() for i in items]
        res = []
        for ix, curline in enumerate(items):
            if len(curline)==0:
                continue

            if 'Marseilles for a ship to come' in curline:
                pass
            next_items = items[ix+1:ix+1+2]
            isNextPureLines = self.CheckIsLinesEmpyAll(next_items)
            last_item = curline[-1]
            if isNextPureLines:
                if  last_item.endswith(('.', '!', '?')):
                    pass
                else:
                    curline+='.'
            else:
                if self.lineIsEmpty(curline): continue

            # check is last line not end sentence character
            if len(res)==0:
                res.append(curline)
                continue

            prevline = res[-1]
            if prevline.endswith(('.', '!', '?')):
                res.append(curline)
            else:
                res[-1]+=' ' + curline
            continue


        return '\n'.join(res)

    def RunExtract(self):
        res_text = self.Extract()
        res_text = self.postProcessText(res_text)
        with open(self.path_output, 'w', encoding='utf-8') as f:
            f.write(res_text)
        print('Save file:', self.path_output)
        return

def extract_text_pipe( pahttext:str, pathFileOut:str ):
    ext_reader = CHelperHtmlExtractor( pahttext, pathFileOut )
    ext_reader.RunExtract()
    return

def main():
    pathfile = r""
    pathOutput = r""
    extractor = CHelperHtmlExtractor(pathfile, pathOutput)
    extractor.RunExtract()
    return

if __name__ == "__main__":
    main()
    # Example usage:
