import pandas as pd
import matplotlib.pyplot as plt
import json
from collections import Counter

df = pd.read_csv('combined_pr_data.csv')

print("="*60)
print("EXPERIMENT 1 - DATASET STATISTICS (TRIMMED)")
print("="*60)
print(f"Total PRs: {len(df)}")
print(f"Merged PRs: {df['merged'].sum()}")
print(f"Unmerged PRs: {len(df) - df['merged'].sum()}")
print(f"Merge rate: {df['merged'].mean()*100:.1f}%")
print(f"\nAvg additions: {df['additions'].mean():.1f}")
print(f"Avg deletions: {df['deletions'].mean():.1f}")
print(f"Avg changed files: {df['changed_files'].mean():.1f}")
print(f"Avg commits: {df['commits_count'].mean():.1f}")
print(f"Avg reviewers: {df['reviewers'].apply(lambda x: len(eval(x) if isinstance(x, str) else x)).mean():.1f}")
print(f"Avg review comments: {df['review_comments'].apply(lambda x: len(eval(x) if isinstance(x, str) else x)).mean():.1f}")
print(f"\nPRs with AI reviewer: {df['has_ai_reviewer'].sum()}")
print(f"PRs with AI-generated code: {df['has_ai_code'].sum()}")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

merged_counts = df['merged'].value_counts()
axes[0,0].bar(['Merged', 'Not Merged'], merged_counts, color=['green', 'red'])
axes[0,0].set_title('Merge Status')
axes[0,0].set_ylabel('Count')

axes[0,1].hist(df['review_comments'].apply(lambda x: len(eval(x) if isinstance(x, str) else x)), bins=20, color='blue', alpha=0.7)
axes[0,1].set_title('Review Comments Distribution')
axes[0,1].set_xlabel('Number of Comments')

axes[0,2].hist(df['reviewers'].apply(lambda x: len(eval(x) if isinstance(x, str) else x)), bins=10, color='orange', alpha=0.7)
axes[0,2].set_title('Reviewers per PR')
axes[0,2].set_xlabel('Number of Reviewers')

df['pr_length'] = df['additions'] + df['deletions']
axes[1,0].hist(df['pr_length'], bins=30, color='purple', alpha=0.7)
axes[1,0].set_title('PR Length Distribution')
axes[1,0].set_xlabel('Lines Changed')

ai_data = [df['has_ai_code'].sum(), len(df) - df['has_ai_code'].sum()]
axes[1,1].bar(['AI Generated', 'Human'], ai_data, color=['orange', 'blue'])
axes[1,1].set_title('AI-Generated Code')
axes[1,1].set_ylabel('Count')

all_labels = []
for labels in df['labels']:
    try:
        labels = eval(labels) if isinstance(labels, str) else labels
        if isinstance(labels, list):
            all_labels.extend(labels)
    except:
        pass

if all_labels:
    label_counts = Counter(all_labels).most_common(10)
    labels, counts = zip(*label_counts)
    axes[1,2].bar(labels, counts, color='teal', alpha=0.7)
    axes[1,2].set_title('Top 10 Labels')
    axes[1,2].set_xlabel('Label')
    plt.setp(axes[1,2].xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('analysis_plots.png', dpi=300)
print("\n✅ Plots saved to analysis_plots.png")

print("\nSample PR data:")
print(df[['pr_id', 'title', 'merged', 'additions', 'deletions']].head(10))