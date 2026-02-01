import subprocess
import json
import pandas as pd

print("Exporting data from MongoDB...")

# Run mongosh command to get JSON
cmd = [
    'mongosh',
    'mongodb+srv://cluster0.bf0mqcv.mongodb.net/aqi_features',
    '--username', 'aqi_admin',
    '--password', 'alialiali123',
    '--quiet',
    '--eval', 'JSON.stringify(db.raw_data.find().sort({timestamp: 1}).toArray())'
]

print("Running mongosh command...")
result = subprocess.run(cmd, capture_output=True, text=True)

print("Parsing JSON data...")
# Remove any extra output and get just the JSON
output = result.stdout.strip()

# Find the actual JSON array (starts with [ and ends with ])
start = output.find('[')
end = output.rfind(']') + 1
json_str = output[start:end]

data = json.loads(json_str)

print(f"Processing {len(data)} records...")

# Convert to DataFrame
df = pd.DataFrame(data)

# Clean up _id column
if '_id' in df.columns:
    df = df.drop('_id', axis=1)

# Convert timestamp from nested format if needed
if 'timestamp' in df.columns and isinstance(df['timestamp'].iloc[0], dict):
    df['timestamp'] = df['timestamp'].apply(lambda x: x.get('$date', x))

# Save to CSV
output_path = 'notebooks/aqi_data.csv'
df.to_csv(output_path, index=False)

print(f"\n✓ Successfully exported {len(df)} records to {output_path}")
print(f"✓ Columns: {list(df.columns)}")
print(f"✓ Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")