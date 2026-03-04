import weaviate
from config.settings import WEAVIATE_URL, WEAVIATE_API_KEY

def get_client():
    return weaviate.Client(
        url=WEAVIATE_URL,
        auth_client_secret=weaviate.AuthApiKey(WEAVIATE_API_KEY)
    )

def create_schema():
    client = get_client()

    base_schema = {
        "vectorizer": "none",
        "properties": [
            {"name": "classNumber", "dataType": ["int"]},
            {"name": "title", "dataType": ["text"]},
            {"name": "description", "dataType": ["text"]},
            {"name": "keywords", "dataType": ["text[]"]}
        ]
    }

    for collection_name in ["nice_good", "nice_service"]:
        if not client.schema.exists(collection_name):
            schema = base_schema.copy()
            schema["class"] = collection_name
            client.schema.create_class(schema)

    return client