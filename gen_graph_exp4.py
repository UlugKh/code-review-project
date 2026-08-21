import matplotlib.pyplot as plt
import numpy as np

# Context data
contexts = ['C1_Diff_Only', 'C2_Diff_PR_Desc', 'C3_Diff_Repo', 'C4_Diff_History', 'C5_Full_SE']
acc = [0.5357, 0.4167, 0.5119, 0.5238, 0.4643]
f1 = [0.3158, 0.5243, 0.5176, 0.3333, 0.5631]
recall = [0.2500, 0.7500, 0.6111, 0.2778, 0.8056]

x = np.arange(len(contexts))
width = 0.25

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x - width, acc, width, label='Accuracy', color='skyblue')
ax.bar(x, f1, width, label='F1-Score', color='lightcoral')
ax.bar(x + width, recall, width, label='Recall', color='lightgreen')

ax.set_xlabel('Context Type')
ax.set_ylabel('Score')
ax.set_title('Performance by Context Type (Experiment 4)')
ax.set_xticks(x)
ax.set_xticklabels(contexts, rotation=15)
ax.legend()
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig('exp4_context_comparison.png', dpi=300)
print("✅ exp4_context_comparison.png")

# Prompt data
prompts = ['P1_RoleBased', 'P2_FewShot', 'P3_ChainOfThought', 'P4_SelfReflection']
acc_p = [0.5429, 0.4095, 0.5048, 0.5048]
f1_p = [0.2727, 0.5634, 0.5000, 0.4583]
recall_p = [0.2000, 0.8889, 0.5778, 0.4889]

x = np.arange(len(prompts))
width = 0.25

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - width, acc_p, width, label='Accuracy', color='skyblue')
ax.bar(x, f1_p, width, label='F1-Score', color='lightcoral')
ax.bar(x + width, recall_p, width, label='Recall', color='lightgreen')

ax.set_xlabel('Prompt Type')
ax.set_ylabel('Score')
ax.set_title('Performance by Prompt Type (Experiment 4)')
ax.set_xticks(x)
ax.set_xticklabels(prompts, rotation=15)
ax.legend()
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig('exp4_prompt_comparison.png', dpi=300)
print("✅ exp4_prompt_comparison.png")

# F1 Matrix Heatmap
f1_matrix = np.array([
    [0.0000, 0.6000, 0.0000, 0.0000],
    [0.4706, 0.6000, 0.5517, 0.4444],
    [0.1818, 0.5517, 0.5833, 0.5714],
    [0.3333, 0.4167, 0.3077, 0.1818],
    [0.2353, 0.6207, 0.6207, 0.6429]
])

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(f1_matrix, cmap='Blues', vmin=0, vmax=1)

ax.set_xticks(np.arange(4))
ax.set_yticks(np.arange(5))
ax.set_xticklabels(['P1_RoleBased', 'P2_FewShot', 'P3_CoT', 'P4_SelfReflection'], rotation=15)
ax.set_yticklabels(['C1_Diff', 'C2_PR_Desc', 'C3_Repo', 'C4_History', 'C5_Full'])

for i in range(5):
    for j in range(4):
        ax.text(j, i, f'{f1_matrix[i, j]:.3f}', ha='center', va='center', color='darkblue')

ax.set_xlabel('Prompt Type')
ax.set_ylabel('Context Type')
ax.set_title('F1-Score Matrix: Context × Prompt (Experiment 4)')
plt.colorbar(im, ax=ax, label='F1-Score')
plt.tight_layout()
plt.savefig('exp4_f1_heatmap.png', dpi=300)
print("✅ exp4_f1_heatmap.png")