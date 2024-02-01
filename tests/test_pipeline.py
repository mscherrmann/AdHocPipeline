from adhocpipeline.pipeline import Pipeline
import os


def test_pipeline(language="de",
                  start_date="01.03.2021",
                  end_date="01.04.2021",
                  begin_from_start_date=True,
                  start_from="crawler",
                  tmp_storage_path=os.path.join("tests", "data", "tmp"),
                  clear_test_data=True):
    # Pipeline
    pipe = Pipeline(language=language,
                    start_date=start_date,
                    end_date=end_date,
                    begin_from_start_date=begin_from_start_date,
                    tmp_storage_path=tmp_storage_path,
                    is_test_mode=True,
                    start_from=start_from)
    if clear_test_data:
        pipe.delete_indices()
        pipe.delete_tmp_files()
        pipe.delete_html_files()
    pipe.update(cache_intermediate_results=True,
                delete_intermediate_results=False)


if __name__ == '__main__':
    test_pipeline()
