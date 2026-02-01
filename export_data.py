import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.storage.mongodb_client import mongodb_client
from src.utils.config import Config
import pandas as pd

print("Exporting data from MongoDB...")

feature_db = mongodb_client.get_feature_store()
raw_collection = feature_db[Config.RAW_DATA_COLLECTION]

cursor = raw_collection.find().sort("timestamp", 1)
df = pd.DataFrame(list(cursor))

if '_id' in df.columns:
    df = df.drop('_id', axis=1)

df.to_csv('notebooks/aqi_data.csv', index=False)
print(f"Exported {len(df)} records to notebooks/aqi_data.csv")
print("Done!")