import os
from sentence_transformers import SentenceTransformer
import torch
import pandas as pd
import time

class Embedder():
    
    def __init__(self, 
                 embedding_model = "paraphrase-multilingual-mpnet-base-v2", 
                 tmp_storage_path = "data\\tmp",
                 batch_size = 512):
        """
        Parameters
        ----------
        embedding_model : str
           name of the language model used for embedding, downloaded from the huggingface hub
           A multilingual model is prederred, to make comparisons across languages
        tmp_storage_path : str
           path to folder from which parsed documents get loaded and to which cleaned documents get stored
        batch_size : int
           Batch size for embedding model inference
        """
        self.__embedding_model = embedding_model
        if os.path.exists(tmp_storage_path):
            self.__tmp_storage_path = tmp_storage_path
        else:
            self.__tmp_storage_path =  os.path.dirname(os.path.dirname(__file__)) + "\\" + tmp_storage_path
        if torch.cuda.is_available():
            self.__device = "cuda"
        else:
            self.__device = "cpu"
        self.__batch_size = batch_size
        self.__embedder = SentenceTransformer(self.__embedding_model)

    
    def embed(self, 
                docs, 
                return_embedded_docs = False, 
                store_embedded_docs = True,
                remove_classified_docs = True):
        bodies = docs["cleaned_body"].explode()
        titles = docs["title_text"]
        # Calculate embeddings
        start = time.time()
        sentence_embeddings = self.__embedder.encode(bodies.tolist(),  batch_size = self.__batch_size).tolist()
        sentence_embeddings = pd.Series(sentence_embeddings, index = bodies.index)
        sentence_embeddings = sentence_embeddings.groupby(sentence_embeddings.index).agg(list)
        title_embeddings = self.__embedder.encode(titles.tolist(),  batch_size = self.__batch_size).tolist()
        print(f"Embedding of {len(docs)} ad-hoc announcements took {(time.time()-start)/60:.2f} minutes.")
        docs["sentence_embeddings"] = sentence_embeddings
        docs["title_embeddings"] = title_embeddings
        # Remove cleaned docs
        if remove_classified_docs:
            path_cleaned_docs = self.__tmp_storage_path + "\\classified_output.pkl"
            if os.path.isfile(path_cleaned_docs):
                os.remove(path_cleaned_docs)
        # Save
        if store_embedded_docs:
            docs.to_pickle(self.__tmp_storage_path+"\\embedded_output.pkl")
        # Return
        if return_embedded_docs:
            return docs

        