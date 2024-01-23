# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 10:47:44 2024

@author: scherrmann
"""

from adhocpipeline.topic_classifier import TopicClassifier
import os
import pandas as pd

def test_topic_classification(language = "de",
                              tmp_storage_path = "tests\\data\\tmp"):
    
    # Load cleaned docs
    storage_path = os.path.dirname(os.path.dirname(__file__)) + "\\" + tmp_storage_path
    cleaned_docs = pd.read_pickle(storage_path + "\\cleaned_output.pkl")
    # Topic classifier
    topic_classifier = TopicClassifier(tmp_storage_path = tmp_storage_path,
                                       language = language)
    classified_docs = topic_classifier.topic_classification(cleaned_docs, 
                                          return_classified_docs = True, 
                                          store_classified_docs = True, 
                                          remove_cleaned_docs = False)
    return classified_docs

if __name__ == '__main__':
    classified_docs = test_topic_classification()