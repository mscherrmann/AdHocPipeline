# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 10:47:44 2024

@author: scherrmann
"""

from adhocpipeline.embedder import Embedder
import os
import pandas as pd


def test_embedder(tmp_storage_path=os.path.join("tests", "data", "tmp")):

    # Load cleaned docs
    storage_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "tmp_storage_path")
    classified_docs = pd.read_pickle(
        os.path.join(storage_path, "classified_output.pkl"))
    # Embedder
    embedder = Embedder(tmp_storage_path=tmp_storage_path)
    embedded_docs = embedder.embed(classified_docs,
                                   return_embedded_docs=True,
                                   store_embedded_docs=True,
                                   remove_classified_docs=False)
    return embedded_docs


if __name__ == '__main__':
    embedded_docs = test_embedder()
