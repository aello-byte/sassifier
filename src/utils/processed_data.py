import json
import os

processed_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ingest')
PROCESSED_FILE = os.path.join(processed_dir,"processed_video_ids.json")

def load_processed_ids():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_ids(processed_ids):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed_ids), f)