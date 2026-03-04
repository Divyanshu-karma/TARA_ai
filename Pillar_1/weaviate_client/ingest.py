import json
import os
import re
from embeddings.embedder import Embedder
from weaviate_client.schema import create_schema

BASE_PATH = "classification_engine"

def build_category_text(title, description, keywords):
    return f"{title}. {description}. {' '.join(keywords)}"

def extract_class_number(filename):
    """
    Extract first numeric sequence from filename.
    Works for:
        nice_good1.json
        nice_good34.json
        s35.json
        s45.json
    """
    match = re.search(r"\d+", filename)
    if not match:
        raise ValueError(f"Cannot extract class number from filename: {filename}")
    return int(match.group())

def ingest_folder(folder_name, collection_name):
    client = create_schema()
    embedder = Embedder()

    folder_path = os.path.join(BASE_PATH, folder_name)

    for file in os.listdir(folder_path):
        if file.endswith(".json"):

            class_number = extract_class_number(file)

            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                data = json.load(f)

            for category in data:

                full_text = build_category_text(
                    category["title"],
                    category["description"],
                    category["keywords"]
                )

                vector = embedder.embed(full_text)

                client.data_object.create(
                    {
                        "classNumber": class_number,
                        "title": category["title"],
                        "description": category["description"],
                        "keywords": category["keywords"]
                    },
                    collection_name,
                    vector=vector
                )

def ingest_all():
    ingest_folder("nice_good", "nice_good")
    ingest_folder("nice_services", "nice_service")