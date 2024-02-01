from adhocpipeline.open_search_uploader import OpenSearchUploader
import os
import pandas as pd


def test_open_search_uploader(
        language="de",
        tmp_storage_path=os.path.join("tests", "data", "tmp")):

    # Load embedded docs
    storage_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        tmp_storage_path)
    embedded_docs = pd.read_pickle(
        os.path.join(storage_path, "embedded_output.pkl"))
    # Uploader
    uploader = OpenSearchUploader(tmp_storage_path=tmp_storage_path,
                                  is_test_mode=True,
                                  language=language)
    uploader.upload(embedded_docs,
                    remove_embedded_docs=False)
    return embedded_docs


if __name__ == '__main__':
    embedded_docs = test_open_search_uploader()
