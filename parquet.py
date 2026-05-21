import pyarrow.parquet as pq
import pyarrow.csv as csv

table = csv.read_csv("csv/Automated_Traffic_Volume_Counts_20260520.csv")
pq.write_table(table, "traffic_vol_current.parquet")

myTable = pq.read_table("traffic_vol_current.parquet")
print(myTable)
