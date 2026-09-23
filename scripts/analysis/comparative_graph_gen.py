import matplotlib.pyplot as plt
import numpy as np

# Context data
contexts = ['C1_Diff_Only', 'C2_Diff_PR_Body', 'C3_Diff_Commit', 'C4_Full_Context']
acc = [0.5000, 0.4397, 0.5862, 0.5259]
f1 = [0.5085, 0.5638, 0.6620, 0.6584]
recall = [0.5000, 0.7000, 0.7833, 0.8833]

x = np.arange(len(contexts))
width = 0.25

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - width, acc, width, label='Accuracy', color='skyblue')
ax.bar(x, f1, width, label='F1-Score', color='lightcoral')
ax.bar(x + width, recall, width, label='Recall', color='lightgreen')

ax.set_xlabel('Context Type')
ax.set_ylabel('Score')
ax.set_title('Performance by Context Type (Experiment 3)')
ax.set_xticks(x)
ax.set_xticklabels(contexts, rotation=15)
ax.legend()
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig('exp3_context_comparison.png', dpi=300)
print("✅ exp3_context_comparison.png")

# Prompt data
prompts = ['P1_ZeroShot', 'P2_FewShot', 'P3_ChainOfThought', 'P4_RoleBased']
acc_p = [0.5172, 0.5000, 0.5259, 0.5086]
f1_p = [0.6364, 0.6420, 0.5926, 0.5210]
recall_p = [0.8167, 0.8667, 0.6667, 0.5167]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - width, acc_p, width, label='Accuracy', color='skyblue')
ax.bar(x, f1_p, width, label='F1-Score', color='lightcoral')
ax.bar(x + width, recall_p, width, label='Recall', color='lightgreen')

ax.set_xlabel('Prompt Type')
ax.set_ylabel('Score')
ax.set_title('Performance by Prompt Type (Experiment 3)')
ax.set_xticks(x)
ax.set_xticklabels(prompts, rotation=15)
ax.legend()
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig('exp3_prompt_comparison.png', dpi=300)
print("✅ exp3_prompt_comparison.png")

# F1 Matrix Heatmap
f1_matrix = np.array([
    [0.6818, 0.6818, 0.0000, 0.0000],
    [0.5946, 0.5000, 0.6341, 0.5143],
    [0.6250, 0.6500, 0.7000, 0.6667],
    [0.6341, 0.7143, 0.6667, 0.6154]
])

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(f1_matrix, cmap='Blues', vmin=0, vmax=1)

ax.set_xticks(np.arange(4))
ax.set_yticks(np.arange(4))
ax.set_xticklabels(['P1_ZeroShot', 'P2_FewShot', 'P3_CoT', 'P4_RoleBased'], rotation=15)
ax.set_yticklabels(['C1_Diff', 'C2_PR_Body', 'C3_Commit', 'C4_Full'])

for i in range(4):
    for j in range(4):
        ax.text(j, i, f'{f1_matrix[i, j]:.3f}', ha='center', va='center', color='darkblue')

ax.set_xlabel('Prompt Type')
ax.set_ylabel('Context Type')
ax.set_title('F1-Score Matrix: Context × Prompt')
plt.colorbar(im, ax=ax, label='F1-Score')
plt.tight_layout()
plt.savefig('exp3_f1_heatmap.png', dpi=300)
print("✅ exp3_f1_heatmap.png")