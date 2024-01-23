from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
from utils.opensearch_utils import get_index_body
import os
import time
import pandas as pd

class OpenSearchUploader():
    
    def __init__(self, 
                 upload_batch_size = 1000, 
                 tmp_storage_path = "data\\tmp", 
                 client = None, 
                 is_test_mode = False,
                 language="de"):
        """
        Parameters
        ----------
        upload_batch_size : int
           number of samples that should be uploaded to opensearch index in one iteration
        tmp_storage_path : str
           path to folder from which parsed documents get loaded and to which cleaned documents get stored
       client:
           opensearch client
       is_test_mode : bool
           Flag to indicate whether to use pipeline in test mode or not
       language : str
           Specify the language (default is "de"):            "de" : german
                                                              "en" : English
        """
        self.__upload_batch_size = upload_batch_size
        if os.path.exists(tmp_storage_path):
            self.__tmp_storage_path = tmp_storage_path
        else:
            self.__tmp_storage_path =  os.path.dirname(os.path.dirname(__file__)) + "\\" + tmp_storage_path
        if client:
            self.__client = client
        else:
            self.__client = OpenSearch(hosts = [{"host": "localhost", "port": 9200}],
                                       http_auth = ("admin", "admin"),
                                       use_ssl = True,
                                       verify_certs = False,
                                       ssl_assert_hostname = False,
                                       ssl_show_warn = False,
                                       timeout=30)
        self.__is_test_mode = is_test_mode
        self.__language = language
        self.__index_name = "ad_hoc_" + self.__language
        self.__index_name_sentence = "ad_hoc_sentence_" + self.__language
        if self.__is_test_mode:
            self.__index_name = "test_" + self.__index_name 
            self.__index_name_sentence = "test_" + self.__index_name_sentence
            
    def upload(self, docs,  remove_embedded_docs = True):
        # Split in document and sentence level
        sentences = docs[['hash', 'cleaned_body', 'topics','sentence_embeddings']]
        documents = docs[['title_text', 'date_text', 'time_text', 
               'category', 'hash', 'isin_all', 'isin', 'wkn', 'comp_name', 'file_id',
                'body_text_raw','topics','title_embeddings']]
        
        # Upload sentence 
        sentences = self.__prepare_sentences(sentences)
        self.__check_index("sentence")
        sentences["_id"] = sentences["hash"] + sentences["sentence_id"].astype(str)
        sentences = sentences.to_dict('records')
        self.__bulk_upload(sentences, self.__index_name_sentence)
        
        # Upload document
        documents = self.__prepare_documents(documents)
        self.__check_index("document")
        documents["_id"] = documents["hash"]
        documents = documents.to_dict('records')
        self.__bulk_upload(documents, self.__index_name)
        # Remove embedded docs
        if remove_embedded_docs:
            path_embedded_docs = self.__tmp_storage_path + "\\embedded_output.pkl"
            if os.path.isfile(path_embedded_docs):
                os.remove(path_embedded_docs)
        
        
    def __bulk_upload(self, docs, index_name):
        num_docs = len(docs)
        batch_idx = 0
        start = time.time()
        while batch_idx * self.__upload_batch_size < num_docs:
            max_idx = min((batch_idx + 1) * self.__upload_batch_size, num_docs)
            docs_batch = docs[batch_idx * self.__upload_batch_size : max_idx]
            bulk(self.__client,docs_batch, index = index_name)
            print(f"{max_idx/num_docs:.2%} of entry uploads done for index {index_name} after {(time.time()-start)/60:.2f} minutes.")
            batch_idx += 1
    
    def __prepare_sentences(self, sentences):
        # Explode
        sentences = sentences.explode(['cleaned_body', 'topics','sentence_embeddings'])
        # Rename columns
        sentences = sentences.rename(columns = {"cleaned_body":"sentences",
                                                "topics":"topic"})
        # Add sentence id
        sentences['sentence_id'] = sentences.groupby(sentences.index).cumcount()
        return sentences
    
    
    
    def __prepare_documents(self, documents):
        # Rename columns
        documents = documents.rename(columns = {'title_text':'title',
                                                'comp_name':'name', 
                                                'file_id':'document_id',
                                                'body_text_raw':'raw_body',
                                                'topics':'topic',
                                                'title_embeddings':'title_embedding'})
        # Adjust date
        # Sometimes, the time of the day is only given by hours:minutes, instead of hours:minutes:seconds.
        # Adjust for that first
        different_time_mask = documents.time_text.apply(len)==5
        documents.loc[different_time_mask,"time_text"] = documents.loc[different_time_mask,"time_text"] + ":00"
        documents["date"] = documents['date_text'] + "T" + documents['time_text']
        documents["date"] = pd.to_datetime(documents["date"], format="%d.%m.%YT%H:%M:%S")
        documents = documents.drop(['date_text', 'time_text'], axis=1)
        
        # Aggregate topic
        # Function to flatten and aggregate each list of lists into a single list with unique elements
        def __aggregate_list_of_lists(list_of_lists):
            # Flatten the list of lists and remove duplicates while preserving order
            return list(dict.fromkeys(item for sublist in list_of_lists for item in sublist))
        documents["topic"] = documents["topic"].apply(__aggregate_list_of_lists)

        return documents
        
        
    
    def __check_index(self, level):
        # Check whether index is available. If not, create it
        # Get list of all indices
        indices = self.__client.cat.indices(format="json")
        index_names = [index['index'] for index in indices]
        if level == "document":
            index_name =self.__index_name
        else:
            index_name = self.__index_name_sentence
        # Create index if it is missing
        if index_name not in index_names:
            body = get_index_body(level, self.__language)
            response = self.__client.indices.create(index_name, body=body)
