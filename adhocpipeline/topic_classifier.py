import os
from transformers import pipeline
import torch
import pandas as pd
import time


class TopicClassifier():

    def __init__(self,
                 classification_model=(
                     "scherrmann/GermanFinBert_FP_AdHocMultilabel"
                 ),
                 tmp_storage_path=os.path.join("data", "tmp"),
                 batch_size=512,
                 classification_threshold=0.6,
                 language="de"):
        """
        Parameters
        ----------
        classification_model : str
           name of the topic classification language model,
           downloaded from the huggingface hub
        tmp_storage_path : str
           path to folder from which parsed documents get
           loaded and to which cleaned documents get stored
        batch_size : int
           Batch size for classification model inference
        classification_threshold : str
           Threshold that defines when a label is set
        language : str
            Specify the language (default is "de"):             "de" : german
                                                                "en" : English
        """
        self.__classification_model = classification_model
        if os.path.exists(tmp_storage_path):
            self.__tmp_storage_path = tmp_storage_path
        else:
            self.__tmp_storage_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                tmp_storage_path)
        if torch.cuda.is_available():
            self.__device = "cuda"
        else:
            self.__device = "cpu"
        self.__batch_size = batch_size
        self.__classification_pipe = \
            pipeline("text-classification",
                     model=self.__classification_model,
                     device=self.__device)
        self.__classification_threshold = classification_threshold
        self.__language = language
        self.__label_names = ["Earnings", "SEO", "Management",
                              "Guidance", "Gewinnwarnung",
                              "Beteiligung", "Dividende",
                              "Restructuring", "Debt", "Law",
                              "Großauftrag", "Squeeze",
                              "Insolvenzantrag", "Insolvenzplan",
                              "Delay", "Split", "Pharma_Good",
                              "Rückkauf", "Real_Invest", "Delisting"]

    def topic_classification(self,
                             docs,
                             return_classified_docs=False,
                             store_classified_docs=True,
                             remove_cleaned_docs=True):
        bodies = docs["cleaned_body"].explode()
        # Estimate topics
        start = time.time()
        topics = self.__classification_pipe(
            bodies.tolist(),
            top_k=None,
            batch_size=self.__batch_size)
        print(f"Topic classification of {len(docs)} ad-hoc announcements "
              "took {(time.time()-start)/60:.2f} minutes.")
        # Convert each list of dictionaries into a dictionary
        # with labels as keys and scores as values
        topics = [
                     {d['label']: d['score'] for d in sublist}
                     for sublist in topics
                 ]
        # Create a DataFrame from the list of
        # dictionaries and check which topics are active
        topics = pd.DataFrame(topics) > self.__classification_threshold
        # Set column names to topics
        topics = topics[self.__label_names]
        # Only keep active topics
        topics = topics.apply(lambda row: row.index[row].tolist(), axis=1)
        # Back to list of list of topics
        topics.index = bodies.index
        topics = topics.groupby(topics.index).agg(list)
        docs["topics"] = topics
        # Remove cleaned docs
        if remove_cleaned_docs:
            path_cleaned_docs = os.path.join(
                self.__tmp_storage_path,
                "cleaned_output.pkl")
            if os.path.isfile(path_cleaned_docs):
                os.remove(path_cleaned_docs)
        # Save
        if store_classified_docs:
            docs.to_pickle(
                os.path.join(
                    self.__tmp_storage_path,
                    "classified_output.pkl"))
        # Return
        if return_classified_docs:
            return docs
