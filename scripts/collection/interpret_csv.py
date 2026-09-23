import pandas as pd
import json

df = pd.read_csv('combined_pr_data.csv')

# Per-project counts
projects = {
    'pytorch': 0,
    'tensorflow': 0,
    'kubernetes': 0,
    'vscode': 0,
    'langchain': 0
}

# Count PRs per project (approximate - by PR ID ranges or create project column)
# Since you have separate files, just tell me:
print("Check individual CSV file sizes:")
import os
for f in ['pytorch_pytorch.csv', 'tensorflow_tensorflow.csv', 
          'kubernetes_kubernetes.csv', 'microsoft_vscode.csv', 'langchain-ai_langchain.csv']:
    if os.path.exists(f):
        d = pd.read_csv(f)
        print(f"{f}: {len(d)} PRs")

# Summary stats for report
stats = {
    'total_prs': len(df),
    'merged': int(df['merged'].sum()),
    'unmerged': int(len(df) - df['merged'].sum()),
    'merge_rate': float(df['merged'].mean()),
    'avg_additions': float(df['additions'].mean()),
    'avg_deletions': float(df['deletions'].mean()),
    'avg_files': float(df['changed_files'].mean()),
    'avg_commits': float(df['commits_count'].mean()),
    'avg_reviewers': float(df['reviewers'].apply(lambda x: len(eval(x) if isinstance(x, str) else x)).mean()),
    'avg_comments': float(df['review_comments'].apply(lambda x: len(eval(x) if isinstance(x, str) else x)).mean()),
    'has_ai_reviewer': int(df['has_ai_reviewer'].sum()),
    'has_ai_code': int(df['has_ai_code'].sum())
}

print("\n" + "="*50)
print("REPORT STATISTICS")
print("="*50)
for k, v in stats.items():
    print(f"{k}: {v}")

# Save for report
with open('report_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("\n✅ Saved to report_stats.json")