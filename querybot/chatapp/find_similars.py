import faiss
import numpy as np
import pickle
import os
import json
import tensorflow as tf
from .feature_extractor import extract_features
from django.conf import settings

tf.config.run_functions_eagerly(True)

INDEX_PATH = os.path.join(settings.BASE_DIR, "your index file path.index")
METADATA_PATH = os.path.join(settings.BASE_DIR, "your metadata path.pkl")

if not os.path.exists(INDEX_PATH):
    print(f"Error: FAISS index file '{INDEX_PATH}' not found.")
    exit(1)

index = faiss.read_index(INDEX_PATH)

if not os.path.exists(METADATA_PATH):
    print(f"Error: Metadata file '{METADATA_PATH}' not found.")
    exit(1)

with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)
    print(metadata[:10])

json_dir = os.path.join(settings.BASE_DIR, "static/assets/all_data.json")
with open(json_dir, 'r') as file:
    all_data = json.load(file)

def extract_image_id(image_name):
    """Extract the image ID from the filename."""
    image_id = image_name.split('-')[0]
    if image_id in all_data:
        return image_id

def normalize_features(features):
    """Normalize the feature vector for cosine similarity."""
    norm = np.linalg.norm(features, axis=1, keepdims=True)
    return features / norm

def find_neighbours(query_img, top_k=20):
    if not os.path.exists(query_img):
        print(f"Error: File {query_img} not found.")
        return []

    try:
        query_features = extract_features(query_img)
        if not isinstance(query_features, tf.Tensor):
            print("Error: extract_features did not return a tensor.")
            return []

        query_features = query_features.numpy().reshape(1, -1)
        if query_features.shape[1] != index.d:
            print(f"Error: Feature dimension mismatch! Expected {index.d}, got {query_features.shape[1]}")
            return []

        distances, indices = index.search(query_features, top_k * 3)  # Fetch more to ensure top_k unique properties
        print(f"Django Distances: {distances}, Indices: {indices}")

        seen_ids = set()
        unique_similar_images = []

        for idx in indices[0]:
            if idx >= 0:
                image_name = metadata[idx]
                image_id = image_name.split('-')[0]

                if image_id in all_data and image_id not in seen_ids:
                    seen_ids.add(image_id)
                    unique_similar_images.append(metadata[idx])

                if len(seen_ids) >= top_k:  # Ensure top_k unique properties
                    break

        print(f"Django Unique Images: {unique_similar_images}")
        return unique_similar_images

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return []

def find_similar_properties(img_path, neighbours = 10):
    # img_path = os.path.join(settings.BASE_DIR, f"media/{img_name}")
    similar_images = find_neighbours(img_path, neighbours)

    similar_properties_dict = []

    for image in similar_images:
        image_id = image.split('-')[0]  # Extract property ID
        if image_id in all_data:
            property_details = all_data[image_id].copy()
            property_details["image_id"] = image  # Associate a single image per property
            similar_properties_dict.append(property_details)

    return similar_properties_dict