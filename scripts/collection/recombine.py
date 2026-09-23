import pandas as pd
import os

files = ['pytorch_pytorch.csv', 'tensorflow_tensorflow.csv', 
         'kubernetes_kubernetes.csv', 'microsoft_vscode.csv', 'langchain-ai_langchain.csv']

dfs = []
for f in files:
    if os.path.exists(f):
        df = pd.read_csv(f)
        dfs.append(df)
        print(f"{f}: {len(df)} PRs")

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('combined_pr_data.csv', index=False)

print(f"\n✅ TOTAL: {len(combined)} PRs")
print(f"Merged: {combined['merged'].sum()}")
print(f"Unmerged: {len(combined) - combined['merged'].sum()}")
print(f"Merge rate: {combined['merged'].mean()*100:.1f}%")