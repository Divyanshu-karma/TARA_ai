def search_classes(client, collection_name, query_vector, limit=100):
    result = (
        client.query
        .get(collection_name, ["classNumber"])
        .with_near_vector({"vector": query_vector})
        .with_additional(["certainty"])
        .with_limit(limit)
        .do()
    )

    # Dynamically fetch collection key (Weaviate capitalizes it)
    get_section = result["data"]["Get"]

    if not get_section:
        return []

    actual_key = list(get_section.keys())[0]

    return get_section[actual_key]