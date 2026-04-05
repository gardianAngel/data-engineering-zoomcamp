import sys
import pandas as pd

print("argument", sys.argv)

month = int(sys.argv[1])

print(f"Running pipeline for month {month}")

df = pd.DataFrame({"day": [1, 2], "number_passangers": [3, 4]})
df["month"]= month
print(df.head())
df.to_parquet(f"output_day{sys.argv[1]}.parquet")
