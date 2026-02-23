import pandas as pd
import glob

# Find the CSV file
csv_file = glob.glob("data/*.csv")[0]
print(f"Loading: {csv_file}")

df = pd.read_csv(csv_file, encoding="latin-1")

print(f"\nRows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"\nColumn names:")
for col in df.columns:
    print(f"  {col}")

import pandas as pd
import glob

csv_file = glob.glob("data/*.csv")[0]
df = pd.read_csv(csv_file, encoding="latin-1")

print(f"Total cases: {len(df)}")
print(f"Terms covered: {df['term'].min()} to {df['term'].max()}")

print(f"\n--- ISSUE AREAS ---")
print(df['issueArea'].value_counts().sort_index())

print(f"\n--- DECISION DIRECTION ---")
print(df['decisionDirection'].value_counts())

print(f"\n--- RECENT CASES (2020+) ---")
recent = df[df['term'] >= 2020]
print(f"Cases since 2020: {len(recent)}")
print(f"\nSample case names:")
for name in recent['caseName'].head(10):
    print(f"  {name}")