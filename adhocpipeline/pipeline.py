from adhocpipeline.crawler import Crawler
from adhocpipeline.parser import Parser
from adhocpipeline.cleaner import Cleaner
from adhocpipeline.topic_classifier import TopicClassifier
from adhocpipeline.embedder import Embedder
from adhocpipeline.open_search_uploader import OpenSearchUploader
from utils.time import get_time_periods
from opensearchpy import OpenSearch
from datetime import datetime
import os
import pandas as pd
import time

class Pipeline():
    
    def __init__(self, 
                 language = "de",
                 start_date = "01.01.2014",
                 end_date = datetime.now().strftime("%d.%m.%Y"),
                 begin_from_start_date = False,
                 topic_classification_model = "scherrmann/GermanFinBert_FP_AdHocMultilabel",
                 topic_classification_threshold = 0.6,
                 topic_classification_batch_size = 512,
                 embedding_model = "paraphrase-multilingual-mpnet-base-v2",
                 embedding_batch_size = 512,
                 upload_batch_size = 1000, 
                 tmp_storage_path = "data\\tmp",
                 is_test_mode = False, 
                 start_from = "crawler"):
        """
        Parameters
        ----------
        language : str
            Specify the language (default is "de"):            "de" : german
                                                               "en" : English
        start_date : str
            the start date for the crawler (given in the format dd.mm.yyyy). Only used if no index exists or if begin_from_start_date == True
        end_date : str
            the end date for the crawler (given in the format dd.mm.yyyy). Only used if no index exists or if begin_from_start_date == True
        begin_from_start_date : bool
            Force the crawler to begin from start date. Otherwise, start dat ewill be deduced from index
        topic_classification_model : str
           name of the topic classification language model, downloaded from the huggingface hub
        topic_classification_threshold : str
          Threshold that defines when a label is set
        topic_classification_batch_size : int
           Batch size for topic classification model inference
        embedding_model : str
            Name of the language model used for embedding, downloaded from the huggingface hub
            A multilingual model is preferred, to make comparisons across languages
        embedding_batch_size : int
           Batch size for embedding model inference
        upload_batch_size : int
           number of samples that should be uploaded to opensearch index in one iteration
        tmp_storage_path : str
           path to folder from which parsed documents get loaded and to which cleaned documents get stored
        is_test_mode : bool
         Flag to indicate whether to use pipeline in test mode or not
         start_from : str
            Specifies from which node to start from in the pipeline. Requires that the respective predecessors output is stored in tmp_storage_path.
            possible values are: "crawler" (default), "parser", "cleaner", "topic_classifier", "embedder", "uploader"
        """
        self.__language = language
        self.__start_date = start_date
        self.__end_date = end_date
        self.__begin_from_start_date = begin_from_start_date
        self.__topic_classification_model = topic_classification_model
        self.__topic_classification_threshold = topic_classification_threshold
        self.__topic_classification_batch_size = topic_classification_batch_size
        self.__embedding_model = embedding_model
        self.__embedding_batch_size = embedding_batch_size
        self.__upload_batch_size = upload_batch_size
        if os.path.exists(tmp_storage_path):
            self.__tmp_storage_path = tmp_storage_path
        else:
            self.__tmp_storage_path = os.path.dirname(os.path.dirname(__file__)) + "\\" + tmp_storage_path
        self.__is_test_mode = is_test_mode
        self.__start_from = start_from
        
        self.__index_name = "ad_hoc_" + self.__language
        self.__index_name_sentence = "ad_hoc_sentence_" + self.__language
        if self.__is_test_mode:
            self.__index_name = "test_" + self.__index_name
            self.__index_name_sentence = "test_" + self.__index_name_sentence
        if self.__is_test_mode:
            self.__html_path = os.path.dirname(os.path.dirname(__file__)) + "\\tests\\data\\AdHocHtml\\" + self.__language 
        else:
            self.__html_path = os.path.dirname(os.path.dirname(__file__)) + "\\data\\AdHocHtml\\" + self.__language 
        self.__client = OpenSearch(hosts = [{"host": "localhost", "port": 9200}],
                                   http_auth = ("admin", "admin"),
                                   use_ssl = True,
                                   verify_certs = False,
                                   ssl_assert_hostname = False,
                                   ssl_show_warn = False,
                                   timeout=30)
        # Pipeline
        self.crawler = Crawler(language = self.__language, 
                               is_test_mode = self.__is_test_mode)
        self.parser = Parser(language = self.__language,
                             tmp_storage_path = self.__tmp_storage_path,
                             is_test_mode = self.__is_test_mode)
        self.cleaner = Cleaner(language = self.__language,
                               tmp_storage_path = self.__tmp_storage_path)
        self.topic_classifier = TopicClassifier(classification_model = "scherrmann/GermanFinBert_FP_AdHocMultilabel", 
                                                tmp_storage_path = self.__tmp_storage_path,
                                                batch_size = self.__topic_classification_batch_size,
                                                classification_threshold = self.__topic_classification_threshold,
                                                language = self.__language)
        self.embedder = Embedder(embedding_model = self.__embedding_model, 
                                 tmp_storage_path = self.__tmp_storage_path,
                                 batch_size = self.__embedding_batch_size)
        self.uploader = OpenSearchUploader(upload_batch_size = self.__upload_batch_size, 
                                           tmp_storage_path = self.__tmp_storage_path,
                                           client = self.__client,
                                           is_test_mode = self.__is_test_mode,
                                           language = self.__language)
        
    def update(self, cache_intermediate_results = True, delete_intermediate_results = True):
        start = time.time()
        
        # Crawl
        if self.__start_from == "crawler":
            time_periods = get_time_periods(self.__get_crawler_start_date(),self.__end_date, 30)
            for period in time_periods:
                self.crawler.crawl(start_date = period[0], end_date = period[1])
        
        # Parse
        if self.__start_from in ["crawler", "parser"]:
            document_ids = self.__get_files_to_parse()
            if len(document_ids) == 0:
                print("No files to parse. Either the crawler did not add new files or these files already exist in the index")
                return
            parsed_docs = self.parser.parse(document_ids = document_ids, 
                                            return_parsed_docs = True, 
                                            store_parsed_docs = cache_intermediate_results)
        # Clean
        if self.__start_from in ["crawler", "parser", "cleaner"]:
            if 'parsed_docs' not in locals():
                parsed_docs = pd.read_pickle(self.__tmp_storage_path + "\\parsed_output.pkl")
            cleaned_docs = self.cleaner.clean(parsed_docs, 
                                              return_cleaned_docs = True, 
                                              store_cleaned_docs = cache_intermediate_results,
                                              remove_parsed_docs = delete_intermediate_results)
            del parsed_docs
        
        # Topic classification
        if self.__start_from in ["crawler", "parser", "cleaner", "topic_classifier"]:
            if 'cleaned_docs' not in locals():
                cleaned_docs = pd.read_pickle(self.__tmp_storage_path + "\\cleaned_output.pkl")
            classified_docs = self.topic_classifier.topic_classification(cleaned_docs, 
                                                                         return_classified_docs = True, 
                                                                         store_classified_docs = cache_intermediate_results,
                                                                         remove_cleaned_docs = delete_intermediate_results)
            del cleaned_docs
        
        # Embed
        if self.__start_from in ["crawler", "parser", "cleaner", "topic_classifier", "embedder"]:
            if 'classified_docs' not in locals():
                classified_docs = pd.read_pickle(self.__tmp_storage_path + "\\classified_output.pkl")
            embedded_docs = self.embedder.embed(classified_docs, 
                                                return_embedded_docs = True, 
                                                store_embedded_docs = cache_intermediate_results,
                                                remove_classified_docs = delete_intermediate_results)
            del classified_docs
        
        # Upload
        if self.__start_from in ["crawler", "parser", "cleaner", "topic_classifier", "embedder", "uploader"]:
            if 'embedded_docs' not in locals():
                embedded_docs = pd.read_pickle(self.__tmp_storage_path + "\\embedded_output.pkl")
            self.uploader.upload(embedded_docs,  
                                 remove_embedded_docs = delete_intermediate_results)
        
        print(f"Time to run pipeline for {len(embedded_docs)} documents: {(time.time()-start)/60:.2f} minutes.")
        
    def __get_crawler_start_date(self):
        if self.__begin_from_start_date:
            return self.__start_date
        if self.__index_name not in self._get_index_list():
            return self.__start_date
        max_date = self.__get_max_date_index()
        return max_date.strftime("%d.%m.%Y")
        
    def __get_files_to_parse(self):
        # Returns all html files that are not indexed yet
        html_files = self.__get_html_file_names()
        indexed_documents = self.__get_all_document_ids_index()
        return [x for x in html_files if x not in indexed_documents]
        
    
    def _get_index_list(self):
        indices = self.__client.cat.indices(format="json")
        index_names = [index['index'] for index in indices]
        return index_names
    
    def __get_max_date_index(self):
        if self.__index_name not in self._get_index_list():
            return None
        # Aggregation query to get max date
        aggs_query = {
            "size": 0, # We don't need the actual documents
            "aggs": {
                "max_date": {
                    "max": {
                        "field": "date"
                        }
                    }
                }
            }
        # Execute the query
        response = self.__client.search(index=self.__index_name, body=aggs_query)
        max_date = response['aggregations']['max_date']['value_as_string']
        return datetime.strptime(max_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    def __get_all_document_ids_index(self):
        if self.__index_name not in self._get_index_list():
            return []
        # Initial search request
        initial_query = {
            "size": 1000,  # Number of results per "page"
            "_source": ["document_id"],  # Include only the "id" field
            "query": {
                "match_all": {}
            }
        }
        initial_response = self.__client.search(index=self.__index_name, body=initial_query, scroll='2m')  # 2m is the scroll duration
        
        # List to store ids
        ids = []
        
        # Scroll until no more results
        while True:
            # Extract ids
            ids.extend([doc['_source']['id'] for doc in initial_response['hits']['hits']])
            
            # Get the next batch of results
            scroll_id = initial_response['_scroll_id']
            initial_response = self.__client.scroll(scroll_id=scroll_id, scroll='2m')
        
            # Break if no more results
            if not initial_response['hits']['hits']:
                break
        
        # Cleanup scroll context
        self.__client.clear_scroll(scroll_id=scroll_id)
        return ids
    
    def __delete_index(self, index_name):
        # Check if the index exists
        if self.__client.indices.exists(index=index_name):
            # Delete the index
            response = self.__client.indices.delete(index=index_name)
            print(f"Index '{index_name}' deleted successfully.")
            print(response)
        else:
            print(f"Index '{index_name}' does not exist, no need to delete.")
    
    def delete_indices(self):
        self.__delete_index(self.__index_name)
        self.__delete_index(self.__index_name_sentence)
            
    def delete_tmp_files(self):
        # Iterate over all files in the folder
        for filename in os.listdir(self.__tmp_storage_path):
            file_path = os.path.join(self.__tmp_storage_path, filename) 
            os.unlink(file_path)  # Delete the file
    
    def delete_html_files(self):
        # Iterate over all files in the folder
        for filename in os.listdir(self.__html_path):
            file_path = os.path.join(self.__html_path, filename) 
            os.unlink(file_path)  # Delete the file
    
    def __get_html_file_names(self):
        files = pd.Series(os.listdir(self.__html_path ))
        files = files.str.replace('.html', '', regex=False)
        return files.astype(int)
    
    
