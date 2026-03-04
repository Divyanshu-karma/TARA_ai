from collections import defaultdict
from embeddings.embedder import Embedder
from weaviate_client.schema import create_schema
from weaviate_client.search import search_classes

def get_collection_name(class_number: int):
    if 1 <= class_number <= 34:
        return "nice_good"
    elif 35 <= class_number <= 45:
        return "nice_service"
    else:
        raise ValueError("Invalid Nice class number")

def classify(class_number: int, identification: str):
    client = create_schema()
    embedder = Embedder()

    collection_name = get_collection_name(class_number)

    query_vector = embedder.embed(identification)

    results = search_classes(client, collection_name, query_vector)

    class_scores = defaultdict(float)

    for r in results:
        cls = r["classNumber"]
        score = r["_additional"]["certainty"]

        if score > class_scores[cls]:
            class_scores[cls] = score

    best_class = max(class_scores, key=class_scores.get)
    best_score = class_scores[best_class]

    declared_score = class_scores.get(class_number, 0.0)

    competing_scores = {
        cls: score for cls, score in class_scores.items()
        if cls != class_number
    }

    best_competing_class = None
    best_competing_score = 0.0

    if competing_scores:
        best_competing_class = max(competing_scores, key=competing_scores.get)
        best_competing_score = competing_scores[best_competing_class]

    dominance = declared_score - best_competing_score

    return {
        "collectionUsed": collection_name,
        "declaredClass": class_number,
        "declaredScore": declared_score,
        "bestPredictedClass": best_class,
        "bestPredictedScore": best_score,
        "bestCompetingClass": best_competing_class,
        "bestCompetingScore": best_competing_score,
        "dominance": dominance
    }