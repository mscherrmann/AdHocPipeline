from utils.cleaning_utils import clean_body_text
import os
import time

class Cleaner():
    
    def __init__(self, language = "de", tmp_storage_path = "data\\tmp"):
        """
        Parameters
        ----------
        language : str
            Specify the language (default is "de"):            "de" : german
                                                               "en" : English    
        tmp_storage_path : str
           path to folder from which parsed documents get loaded and to which cleaned documents get stored
        """
        self.__language = language
        if os.path.exists(tmp_storage_path):
            self.__tmp_storage_path = tmp_storage_path
        else:
            self.__tmp_storage_path =  os.path.dirname(os.path.dirname(__file__)) + "\\" + tmp_storage_path

    
    def clean(self,docs, return_cleaned_docs = False, store_cleaned_docs = True, remove_parsed_docs = True):
        cleaned_docs = []
        removed_sentences = []
        start = time.time()
        for announcement_idx ,l in enumerate(docs["body_text"]):
            clean_doc, removed = clean_body_text(docs.loc[announcement_idx ,"body_text"],
                                                 docs.loc[announcement_idx ,"comp_name"], 
                                                 docs.loc[announcement_idx ,"contains_verb"],
                                                 self.__language)
            cleaned_docs.append(clean_doc)
            removed_sentences.append(removed)
            if (announcement_idx  + 1) % 25 == 0:
                print(f"Cleaned {announcement_idx / len(docs):.2%} of ad-hoc announcements after {(time.time()-start)/60:.2f} minutes.")
                
        docs["cleaned_body"]=cleaned_docs
        docs["removed_sentences"]=removed_sentences
        # Filter documents without data
        filtering = docs["cleaned_body"].apply(lambda x: len(x) > 0)
        docs = docs.loc[filtering,:]
        # Remove parsed docs
        if remove_parsed_docs:
            path_parsed_docs = self.__tmp_storage_path + "\\parsed_output.pkl"
            if os.path.isfile(path_parsed_docs):
                os.remove(path_parsed_docs)
        # Save
        if store_cleaned_docs:
            docs.to_pickle(self.__tmp_storage_path+"\\cleaned_output.pkl")
        # Return
        if return_cleaned_docs:
            return docs