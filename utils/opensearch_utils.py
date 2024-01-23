def get_index_body(level, language):
    if language =="de":
        lang_str = "german"
    else:
        lang_str = "english"
    
    if level == "document":
        body = {
            "settings": {
                "index": {
                      "knn": True
                    },
                "analysis": {
                    "analyzer": {
                        lang_str: {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "stop",
                                "porter_stem"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "category": {"type": "keyword"},
                    "name": {"type": "keyword"},
                    "date": {"type": "date"},
                    "document_id": {"type": "integer"},
                    "hash": {"type": "keyword"},
                    "isin": {"type": "keyword"},
                    "isin_all": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": lang_str},
                    "title_embedding": {
                          "type": "knn_vector",
                          "dimension": 768,
                          "method": {
                          "name": "hnsw",
                          "space_type": "cosinesimil",
                          "engine": "nmslib"}},
                    "raw_body": {"type": "text", "analyzer": lang_str},
                    "topic": {"type": "keyword"},
                    "wkn": {"type": "keyword"}
                }
            }
        }
        
    else:
        body = {
            "settings": {
                "index": {
                      "knn": True
                    },
                "analysis": {
                    "analyzer": {
                        lang_str: {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "stop",
                                "porter_stem"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "hash": {"type": "keyword"},
                    "sentences": {"type": "text", "analyzer": lang_str},
                    "sentence_embeddings": {
                          "type": "knn_vector",
                          "dimension": 768,
                          "method": {
                          "name": "hnsw",
                          "space_type": "cosinesimil",
                          "engine": "nmslib"}},
                    "sentence_id" :  {"type": "integer"},
                    "topic": {"type": "keyword"}
                }
            }
        }
    return body
