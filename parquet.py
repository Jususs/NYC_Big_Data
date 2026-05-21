import os
import shutil
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as csv
import pandas as pd

# table = csv.read_csv("csv/nyc_weather.csv")
# pq.write_table(table, "weather.parquet")

# myTable = pq.read_table("vehicle_collisions.parquet")
# myTable = pq.read_table("traffic_vol_hist.parquet")
# myTable = pq.read_table("traffic_vol_current.parquet")
# myTable = pq.read_table("permitted_event_hist.parquet")
myTable = pq.read_table("weather.parquet")
# print(myTable)

df = myTable.to_pandas() # to handle date fields better
# df['parsed_date'] = pd.to_datetime(df['CRASH DATE'], format='%m/%d/%Y' ,errors='coerce')
# df['parsed_date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
# df['parsed_date'] = pd.to_datetime(df['Start Date/Time'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
df['parsed_date'] = pd.to_datetime(df['DATE'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')
df['year'] = df['parsed_date'].dt.year.astype('Int64').astype(str)
df['month'] = df['parsed_date'].dt.month.astype('Int64').astype(str)

df = df.drop(columns=['parsed_date']) #optional

myTable = pa.Table.from_pandas(df)

# root_path="vehicle_collisions_partitioned"
# root_path="traffic_vol_hist_partitioned"
# root_path="traffic_vol_current_partitioned"
# root_path="permitted_event_hist_partitioned"
root_path="weather_partitioned"
metadata_collector = []

if os.path.exists(root_path):
    shutil.rmtree(root_path, ignore_errors=True)
os.makedirs(root_path, exist_ok=True)

pq.write_to_dataset(myTable, root_path=root_path, partition_cols=["year", "month"], metadata_collector=metadata_collector)
# pq.write_to_dataset(myTable, root_path=root_path, partition_cols=["Yr", "M"], metadata_collector=metadata_collector)

physical_schema = myTable.drop(["year", "month"]).schema #otherweise error - "This schema has X columns, other has X-1"
# physical_schema = myTable.drop(["Yr", "M"]).schema #otherweise error - "This schema has X columns, other has X-1"
pq.write_metadata(physical_schema, f"{root_path}/_common_metadata") #make table schema accessible
pq.write_metadata(physical_schema, f"{root_path}/_metadata", metadata_collector=metadata_collector)
print("=== Saved parquet to partitions ===")

dataset = pq.ParquetDataset(root_path + "/")
table_partitioned = dataset.read()
print("=== Parquet partitioned ===")
print(table_partitioned)
print(f"=== Created subdirectories: ===\n {[folder.path for folder in os.scandir(root_path + "/") if folder.is_dir()]}")