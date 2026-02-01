from src.data.fetch_data import fetch_latest_data
from datetime import datetime

print("Testing fetch_latest_data()...")
print("=" * 50)

df = fetch_latest_data()

print(f"\n✅ Records fetched: {len(df)}")
print(f"\n📅 Date range:")
print(f"   Start: {df['timestamp'].min()}")
print(f"   End:   {df['timestamp'].max()}")
print(f"\n🕐 Current time: {datetime.now()}")

print(f"\n📊 Columns: {list(df.columns)}")
print(f"\n🔍 First 5 rows:")
print(df.head())

print(f"\n✅ Data looks good!" if len(df) > 0 else "\n❌ No data fetched!")