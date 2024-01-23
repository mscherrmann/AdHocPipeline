import codecs
import os
import spacy
import spacy_fastlang
import pandas as pd
import time
from utils.parsing_utils import parse_ad_hoc
from utils.cleaning_utils import sentence_split
from utils.time import date_conv

class Parser():
    
    def __init__(self,  language="de", tmp_storage_path = "data\\tmp", is_test_mode = False):
        """
        Parameters
        ----------
        language : str
            Specify the language (default is "de"):            "de" : german
                                                               "en" : English     
        tmp_storage_path : str
           path to folder in which parsed output should be stored temporarily
        is_test_mode : bool
         Flag to indicate whether to use pipeline in test mode or not  
        """
        self.__language = language
        self.__is_test_mode = is_test_mode
        if self.__is_test_mode:
            self._file_path = os.path.dirname(os.path.dirname(__file__)) + "\\tests\\data\\AdHocHtml\\" + language
        else:
            self._file_path = os.path.dirname(os.path.dirname(__file__)) + "\\data\\AdHocHtml\\" + language
        if os.path.exists(tmp_storage_path):
            self.__tmp_storage_path = tmp_storage_path
        else:
            self.__tmp_storage_path =  os.path.dirname(os.path.dirname(__file__)) + "\\" + tmp_storage_path

    
    def parse(self, document_ids, return_parsed_docs = False, store_parsed_docs = True):
        if len(document_ids) == 0:
            return []
        # Load spacy models
        spacy.require_gpu()
        nlpDe = spacy.load("de_dep_news_trf", disable=["ner","lemmatizer"])
        nlpEn = spacy.load('en_core_web_trf', disable=["ner","lemmatizer"])
        nlpEn.add_pipe("language_detector")
        
        # Parse
        parsed_docs = []
        start = time.time()
        for announcement_idx, filename in enumerate(document_ids):
            raw_html = codecs.open(self._file_path+"\\"+str(filename) + ".html", 'r').read()
            if (announcement_idx + 1) % 25 == 0:
                print(f"Parsed {(announcement_idx + 1)/ len(document_ids):.2%} of ad-hoc announcements after {(time.time()-start)/60:.2f} minutes.")
            try:
                doc = parse_ad_hoc(raw_html,filename)
                doc["body_text_raw"] = " ".join(doc["body_text"])
                doc = sentence_split(doc, nlpDe=nlpDe, nlpEn=nlpEn)
            except:
                print(f"Parsing error in file: {filename}")
                #doc=sentence_split(doc, nlpDe=nlpDe, nlpEn=nlpEn)
                raise
            parsed_docs.append(doc)
        parsed_docs = pd.DataFrame(parsed_docs)
        
        # Remove different languages
        parsed_docs = parsed_docs.loc[parsed_docs.language == self.__language,:]
        parsed_docs = parsed_docs.reset_index(drop=True)
        
        
        # Bring dates in unique format
        time_str = parsed_docs["date_text"].str.split(" ").str[0]
        time_str = time_str.apply(date_conv)
        parsed_docs["date_text"] = time_str
        # Some files are duplicates since they are filed in different corporate forms. Remove them
        parsed_docs = parsed_docs.drop_duplicates(subset=['file_id'])
        parsed_docs = parsed_docs.reset_index(drop=True)
        # Save
        if store_parsed_docs:
            parsed_docs.to_pickle(self.__tmp_storage_path+"\\parsed_output.pkl")
        # Return
        if return_parsed_docs:
            return parsed_docs
    

    

        