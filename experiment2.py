import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
import matplotlib.pyplot as plt
import json
import ast

df = pd.read_csv('combined_pr_data.csv')

print("="*60)
print("EXPERIMENT 2: MERGE PREDICTION")
print("="*60)

print(f"Total PRs: {len(df)}")

# Filter human-written code only
df_human = df[df['has_ai_code'] == False].copy()
print(f"Human-written PRs: {len(df_human)}")

# Feature engineering - convert string columns to lists
df_human['reviewers_list'] = df_human['reviewers'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
df_human['comments_list'] = df_human['review_comments'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
df_human['labels_list'] = df_human['labels'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# Extract features
features = pd.DataFrame()
features['additions'] = df_human['additions']
features['deletions'] = df_human['deletions']
features['changed_files'] = df_human['changed_files']
features['commits_count'] = df_human['commits_count']
features['reviewers_count'] = df_human['reviewers_list'].apply(len)
features['comments_count'] = df_human['comments_list'].apply(len)
features['labels_count'] = df_human['labels_list'].apply(len)
features['pr_length'] = df_human['additions'] + df_human['deletions']
features['has_ai_reviewer'] = df_human['has_ai_reviewer'].astype(int)

# Target
target = df_human['merged'].astype(int)

print(f"\nFeatures: {features.columns.tolist()}")
print(f"Target: Merge (1) / No Merge (0)")
print(f"Class distribution: {target.value_counts().to_dict()}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42, stratify=target)
print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\n" + "="*60)
print("MODEL 1: SUPPORT VECTOR MACHINE")
print("="*60)

svm = SVC(kernel='rbf', random_state=42, probability=True)
svm.fit(X_train_scaled, y_train)
y_pred_svm = svm.predict(X_test_scaled)
y_proba_svm = svm.predict_proba(X_test_scaled)[:, 1]

print(f"Accuracy: {accuracy_score(y_test, y_pred_svm):.4f}")
print(f"Precision: {precision_score(y_test, y_pred_svm):.4f}")
print(f"Recall: {recall_score(y_test, y_pred_svm):.4f}")
print(f"F1 Score: {f1_score(y_test, y_pred_svm):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_test, y_proba_svm):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred_svm, target_names=['Not Merged', 'Merged']))

print("\n" + "="*60)
print("MODEL 2: RANDOM FOREST")
print("="*60)

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
y_proba_rf = rf.predict_proba(X_test)[:, 1]

print(f"Accuracy: {accuracy_score(y_test, y_pred_rf):.4f}")
print(f"Precision: {precision_score(y_test, y_pred_rf):.4f}")
print(f"Recall: {recall_score(y_test, y_pred_rf):.4f}")
print(f"F1 Score: {f1_score(y_test, y_pred_rf):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_test, y_proba_rf):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred_rf, target_names=['Not Merged', 'Merged']))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': features.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print("\n" + "="*60)
print("FEATURE IMPORTANCE (Random Forest)")
print("="*60)
print(feature_importance.to_string(index=False))

# Save results
results = {
    'svm': {
        'accuracy': float(accuracy_score(y_test, y_pred_svm)),
        'precision': float(precision_score(y_test, y_pred_svm)),
        'recall': float(recall_score(y_test, y_pred_svm)),
        'f1': float(f1_score(y_test, y_pred_svm)),
        'roc_auc': float(roc_auc_score(y_test, y_proba_svm))
    },
    'random_forest': {
        'accuracy': float(accuracy_score(y_test, y_pred_rf)),
        'precision': float(precision_score(y_test, y_pred_rf)),
        'recall': float(recall_score(y_test, y_pred_rf)),
        'f1': float(f1_score(y_test, y_pred_rf)),
        'roc_auc': float(roc_auc_score(y_test, y_proba_rf))
    },
    'feature_importance': feature_importance.to_dict('records'),
    'dataset_size': len(df_human),
    'class_distribution': target.value_counts().to_dict()
}

with open('experiment2_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n✅ Results saved to experiment2_results.json")

# Plot feature importance
plt.figure(figsize=(10, 6))
plt.barh(feature_importance['feature'], feature_importance['importance'], color='steelblue')
plt.xlabel('Importance')
plt.title('Random Forest Feature Importance')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=300)
print("✅ Feature importance plot saved to feature_importance.png")

# Plot comparison
models = ['SVM', 'Random Forest']
metrics = ['Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC']
svm_scores = [results['svm']['accuracy'], results['svm']['precision'], results['svm']['recall'], results['svm']['f1'], results['svm']['roc_auc']]
rf_scores = [results['random_forest']['accuracy'], results['random_forest']['precision'], results['random_forest']['recall'], results['random_forest']['f1'], results['random_forest']['roc_auc']]

x = np.arange(len(metrics))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - width/2, svm_scores, width, label='SVM', color='skyblue')
ax.bar(x + width/2, rf_scores, width, label='Random Forest', color='lightcoral')
ax.set_xlabel('Metrics')
ax.set_ylabel('Score')
ax.set_title('Model Performance Comparison')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.legend()
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig('model_comparison.png', dpi=300)
print("✅ Model comparison plot saved to model_comparison.png")

print("\n" + "="*60)
print("✅ Experiment 2 Complete")
print("="*60)