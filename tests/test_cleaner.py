# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 10:47:44 2024

@author: scherrmann
"""

from adhocpipeline.cleaner import Cleaner
import os
import pandas as pd

def test_cleaner(language = "de",
                 tmp_storage_path = "tests\\data\\tmp"):
    
    # Load parsed docs
    storage_path = os.path.dirname(os.path.dirname(__file__)) + "\\" + tmp_storage_path
    parsed_docs = pd.read_pickle(storage_path + "\\parsed_output.pkl")
    # Clean
    cleaner = Cleaner(language = language, tmp_storage_path = tmp_storage_path)
    cleaned_docs = cleaner.clean(parsed_docs, 
                                 return_cleaned_docs = True, 
                                 store_cleaned_docs = True, 
                                 remove_parsed_docs = False)
    return cleaned_docs

if __name__ == '__main__':
    cleaned_docs = test_cleaner()