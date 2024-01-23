from adhocpipeline.parser import Parser
import os
import pandas as pd

def test_parser(language = "de",
                tmp_storage_path = "tests\\data\\tmp"):
    
    parser = Parser(language = language,
                         tmp_storage_path = tmp_storage_path,
                         is_test_mode = True)
    # Returns all html files that are not indexed yet
    html_files = pd.Series(os.listdir(parser._file_path))
    html_files = html_files.str.replace('.html', '', regex=False)
    parsed_docs = parser.parse(html_files, return_parsed_docs = True, store_parsed_docs = True)
    return parsed_docs

if __name__ == '__main__':
    parsed_docs = test_parser()