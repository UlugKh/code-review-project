# Modified version of collect_prs.py
# Purpose: Resume collection after network interruption
# Collects only kubernetes, vscode, langchain
# Combines with existing pytorch/tensorflow data
# Final combined_pr_data.csv contains all 5 projects (1,500 PRs)
# CONTINUES FROM LAST SAVED PR - checkpoint support

from github import Github
import pandas as pd
import time
import json
import os

GITHUB_TOKEN = "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"
PROJECTS = ["kubernetes/kubernetes", "microsoft/vscode", "langchain-ai/langchain"]
PRS_PER_PROJECT = 300

def get_last_pr(project_name):
    """Read last collected PR number from checkpoint file"""
    checkpoint_file = f'{project_name.replace("/", "_")}_checkpoint.txt'
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return int(f.read().strip())
    return None

def save_checkpoint(project_name, pr_number):
    """Save last collected PR number"""
    checkpoint_file = f'{project_name.replace("/", "_")}_checkpoint.txt'
    with open(checkpoint_file, 'w') as f:
        f.write(str(pr_number))

def collect_project_data(project_name):
    print(f"\nCollecting: {project_name}")
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(project_name)
    prs_data = []
    
    # Check for existing file first (resume mode)
    filename = f'{project_name.replace("/", "_")}.csv'
    if os.path.exists(filename):
        existing = pd.read_csv(filename)
        prs_data = existing.to_dict('records')
        print(f"  Resuming: {len(prs_data)} PRs already collected")
    
    last_pr = get_last_pr(project_name)
    print(f"  Starting from PR #{last_pr if last_pr else 'beginning'}")
    
    for pr in repo.get_pulls(state='closed', sort='created', direction='desc'):
        if len(prs_data) >= PRS_PER_PROJECT:
            break
        
        # Skip PRs we already have
        if last_pr and pr.number <= last_pr:
            continue
            
        if pr.merged or pr.state == 'closed':
            try:
                data = {
                    'pr_id': pr.number,
                    'title': pr.title,
                    'body': pr.body or '',
                    'author': pr.user.login if pr.user else None,
                    'created_at': pr.created_at.isoformat(),
                    'merged': pr.merged,
                    'merged_at': pr.merged_at.isoformat() if pr.merged_at else None,
                    'state': pr.state,
                    'additions': pr.additions,
                    'deletions': pr.deletions,
                    'changed_files': pr.changed_files,
                    'commits_count': pr.commits,
                    'labels': [label.name for label in pr.labels],
                    'reviewers': [],
                    'review_comments': [],
                    'reviews': [],
                    'commit_messages': [],
                    'diff': None
                }
                
                for review in pr.get_reviews():
                    if review.user:
                        data['reviewers'].append(review.user.login)
                    data['reviews'].append({
                        'user': review.user.login if review.user else None,
                        'state': review.state,
                        'submitted_at': review.submitted_at.isoformat() if review.submitted_at else None,
                        'body': review.body or ''
                    })
                
                for comment in pr.get_review_comments():
                    data['review_comments'].append({
                        'user': comment.user.login if comment.user else None,
                        'body': comment.body or '',
                        'created_at': comment.created_at.isoformat(),
                        'path': comment.path,
                        'position': comment.position
                    })
                
                for commit in pr.get_commits():
                    data['commit_messages'].append(commit.commit.message)
                
                try:
                    data['diff'] = pr.diff
                except:
                    data['diff'] = None
                
                ai_keywords = ['bot', 'ai', 'agent', 'copilot', 'codeball', 'mend']
                data['has_ai_reviewer'] = any(
                    any(kw in r['user'].lower() for kw in ai_keywords) 
                    for r in data['reviews'] if r['user']
                )
                
                ai_code = ['copilot', 'chatgpt', 'claude', 'generated', 'llm']
                text = data['title'] + data['body'] + ' '.join(data['commit_messages'])
                data['has_ai_code'] = any(kw in text.lower() for kw in ai_code)
                
                prs_data.append(data)
                print(f"  PR #{pr.number} (merged: {pr.merged})")
                
                # Save checkpoint every 10 PRs
                if len(prs_data) % 10 == 0:
                    save_checkpoint(project_name, pr.number)
                    df = pd.DataFrame(prs_data)
                    df.to_csv(filename, index=False)
                    print(f"  💾 Checkpoint saved: {len(prs_data)} PRs")
                    
            except Exception as e:
                print(f"  Error on PR #{pr.number}: {e}")
                # Save checkpoint on error too
                if prs_data:
                    save_checkpoint(project_name, pr.number - 1)
                continue
            time.sleep(0.2)
    
    # Final save
    if prs_data:
        df = pd.DataFrame(prs_data)
        df.to_csv(filename, index=False)
        with open(f'{project_name.replace("/", "_")}.json', 'w') as f:
            json.dump(prs_data, f, indent=2)
        # Delete checkpoint after successful completion
        checkpoint_file = f'{project_name.replace("/", "_")}_checkpoint.txt'
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
    
    print(f"Done: {len(prs_data)} PRs for {project_name}")
    return pd.DataFrame(prs_data) if prs_data else pd.DataFrame()

if __name__ == "__main__":
    all_data = {}
    for project in PROJECTS:
        try:
            df = collect_project_data(project)
            if not df.empty:
                all_data[project] = df
        except Exception as e:
            print(f"Failed {project}: {e}")
    
    # Combine with existing data
    existing_files = ['pytorch_pytorch.csv', 'tensorflow_tensorflow.csv']
    existing_dfs = []
    for f in existing_files:
        if os.path.exists(f):
            existing_dfs.append(pd.read_csv(f))
            print(f"Loaded existing: {f}")
    
    for df in all_data.values():
        existing_dfs.append(df)
    
    if existing_dfs:
        combined = pd.concat(existing_dfs, ignore_index=True)
        combined.to_csv('combined_pr_data.csv', index=False)
        print(f"\n✅ Total combined: {len(combined)} PRs")


        