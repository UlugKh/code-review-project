import pandas as pd

files = [
    'exp3_human_llm_reviews_checkpoint.csv',
    'exp3_llm_reviews_checkpoint.csv'
]

for f in files:
    print(f"\n{'='*60}")
    print(f"FILE: {f}")
    print('='*60)
    
    df = pd.read_csv(f)
    print(f"Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")
    print(f"\nFirst 2 rows:")
    print(df.head(2).to_string())