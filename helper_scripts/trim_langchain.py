import pandas as pd

# Load langchain data
df = pd.read_csv('langchain-ai_langchain.csv')

# Keep only the 300 most recent PRs (highest PR numbers = most recent)
df_trimmed = df.sort_values('pr_id', ascending=False).head(300)

# Save back
df_trimmed.to_csv('langchain-ai_langchain.csv', index=False)
print(f"Trimmed langchain from {len(df)} to {len(df_trimmed)} PRs")