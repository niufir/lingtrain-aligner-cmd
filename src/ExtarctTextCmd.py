import argparse
import os
import sys
import logging
from logging import Logger

from AlignerImproved.Extarct_EPUB import extract_text_pipe as ReadEpub
from AlignerImproved.Extract_FB2 import extract_text_pipe as ReadFB2
from AlignerImproved.Extract_HTML import extract_text_pipe as ReadHTML
from AlignerImproved.Extract_PDF import Read_PDF
import shutil

EXT_SUPPORTED = ['txt', 'pdf', 'epub', 'fb2', 'html']


def check_file_extension(file_path) -> str:
    """Check and return the file extension."""
    name, extension = os.path.splitext(file_path)
    return extension.replace('.', '').lower()


def prepare_txt_file(file_src: str, file_dst: str):
    """Copy the source file to the destination."""
    shutil.copy(file_src, file_dst)
    return


class ExtractTextCmd:
    def __init__(self, logger: Logger = None):
        self.logger = logger or logging.getLogger('ExtractTextCmd.log')
    
    def arg_parse(self):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description='Extract text from various book formats.')
        parser.add_argument('--path_file', type=str, required=True,
                           help='The path to the source book file.')
        parser.add_argument('--path_out', type=str, required=False,
                           help='The path to the output text file. If not provided, will use input file path with .txt extension.')
        
        args = parser.parse_args()
        
        # Auto-generate output path if not provided
        if not args.path_out:
            name, _ = os.path.splitext(args.path_file)
            args.path_out = name + '.txt'
        
        return args
    
    def process_file(self):
        """Main processing method."""
        args = self.arg_parse()
        
        # Validate input file exists
        if not os.path.exists(args.path_file):
            raise FileNotFoundError(f"Source file not found: {args.path_file}")
        
        # Validate file extension
        ext = check_file_extension(args.path_file)
        if ext not in EXT_SUPPORTED:
            raise ValueError(f"File type '{ext}' not supported. Supported types: {EXT_SUPPORTED}")
        
        self.logger.info(f"Processing file: {args.path_file}")
        self.logger.info(f"Output path: {args.path_out}")
        self.logger.info(f"File type: {ext}")
        
        try:
            # Extract text based on file type
            if ext == 'epub':
                ReadEpub(args.path_file, args.path_out)
            elif ext == 'fb2':
                ReadFB2(args.path_file, args.path_out)
            elif ext == 'pdf':
                Read_PDF(args.path_file, args.path_out)
            elif ext == 'txt':
                prepare_txt_file(args.path_file, args.path_out)
            elif ext == 'html':
                ReadHTML(args.path_file, args.path_out)
        except Exception as e:
            self.logger.error(f"Error during {ext} extraction: {str(e)}")
            raise Exception(f"Failed to extract text from {ext} file '{args.path_file}': {str(e)}")
        
        # Verify output file was created
        if not os.path.exists(args.path_out):
            raise Exception(f"Failed to create output file: {args.path_out}")
        
        self.logger.info(f"Text extraction completed successfully: {args.path_out}")
        return args.path_out


def main():
    print("Command line arguments:", sys.argv)
    
    try:
        cmd_tool = ExtractTextCmd()
        output_path = cmd_tool.process_file()
        print(f"Text extraction completed. Output file: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
