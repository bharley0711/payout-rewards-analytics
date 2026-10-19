"""Load the synthetic dataset into SQLite, run every SQL file in
sql/, and save each result to outputs/ as CSV.

Run:  python3 run_analysis.py
"""

import glob
import sqlite3

import pandas as pd

con = sqlite3.connect(":memory:")
df = pd.read_csv("data/payouts.csv", keep_default_na=False)
df.to_sql("payouts", con, index=False)

for path in sorted(glob.glob("sql/*.sql")):
    sql = open(path).read()
    result = pd.read_sql_query(sql, con)
    out = "outputs/" + path.split("/")[-1].replace(".sql", ".csv")
    result.to_csv(out, index=False)
    print(f"\n== {path} -> {out} ==")
    print(result.to_string(index=False))

con.close()
print("\nAll queries ran clean. Outputs are in outputs/.")
