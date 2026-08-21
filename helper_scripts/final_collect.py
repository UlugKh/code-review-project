from github import Github
import pandas as pd
import time
import json
import os
import urllib3
urllib3.disable_warnings()

GITHUB_TOKEN = "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"
PROJECTS = {
    "microsoft/vscode": 300,
    "langchain-ai/langchain": 300
}

def collect_project_data(project_name, target):
    print(f"\n{'='*50}")
    print(f"Collecting: {project_name} (need {target})")
    print(f"{'='*50}")
    
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(project_name)
    
    filename = f'{project_name.replace("/", "_")}.csv'
    
    existing_ids = set()
    if os.path.exists(filename):
        existing = pd.read_csv(filename)
        existing_ids = set(existing['pr_id'])
        print(f"  Already have: {len(existing_ids)} PRs")
    
    prs_data = []
    count = 0
    new_count = 0
    
    for pr in repo.get_pulls(state='closed', sort='created', direction='desc'):
        if len(existing_ids) + new_count >= target:
            break
            
        if pr.number in existing_ids:
            continue
            
        count += 1
        if count % 20 == 0:
            print(f"  Scanned {count}, collected {new_count}")
            
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
                
                try:
                    for review in pr.get_reviews():
                        if review.user:
                            data['reviewers'].append(review.user.login)
                        data['reviews'].append({
                            'user': review.user.login if review.user else None,
                            'state': review.state,
                            'submitted_at': review.submitted_at.isoformat() if review.submitted_at else None,
                            'body': review.body or ''
                        })
                except:
                    pass
                
                try:
                    for comment in pr.get_review_comments():
                        data['review_comments'].append({
                            'user': comment.user.login if comment.user else None,
                            'body': comment.body or '',
                            'created_at': comment.created_at.isoformat(),
                            'path': comment.path,
                            'position': comment.position
                        })
                except:
                    pass
                
                try:
                    for commit in pr.get_commits():
                        data['commit_messages'].append(commit.commit.message)
                except:
                    pass
                
                try:
                    data['diff'] = pr.diff
                except:
                    pass
                
                ai_keywords = ['bot', 'ai', 'agent', 'copilot', 'codeball', 'mend']
                data['has_ai_reviewer'] = any(
                    any(kw in r['user'].lower() for kw in ai_keywords) 
                    for r in data['reviews'] if r['user']
                )
                
                ai_code = ['copilot', 'chatgpt', 'claude', 'generated', 'llm']
                text = data['title'] + data['body'] + ' '.join(data['commit_messages'])
                data['has_ai_code'] = any(kw in text.lower() for kw in ai_code)
                
                prs_data.append(data)
                new_count += 1
                print(f"  ✅ PR #{pr.number} ({new_count}/{target - len(existing_ids)})")
                
                if new_count % 5 == 0:
                    combined = prs_data.copy()
                    if os.path.exists(filename):
                        existing = pd.read_csv(filename)
                        combined_df = pd.concat([existing, pd.DataFrame(combined)], ignore_index=True)
                    else:
                        combined_df = pd.DataFrame(combined)
                    combined_df.to_csv(filename, index=False)
                    
            except Exception as e:
                print(f"  ⚠️ PR #{pr.number} error: {str(e)[:30]}")
                continue
            time.sleep(0.15)
    
    # Final save
    if prs_data:
        if os.path.exists(filename):
            existing = pd.read_csv(filename)
            combined_df = pd.concat([existing, pd.DataFrame(prs_data)], ignore_index=True)
        else:
            combined_df = pd.DataFrame(prs_data)
        combined_df.to_csv(filename, index=False)
        
        with open(f'{project_name.replace("/", "_")}.json', 'w') as f:
            all_data = combined_df.to_dict('records')
            json.dump(all_data, f, indent=2)
    
    final_count = len(pd.read_csv(filename)) if os.path.exists(filename) else 0
    print(f"\n✅ {project_name}: {final_count} PRs")
    return pd.read_csv(filename) if os.path.exists(filename) else pd.DataFrame()

if __name__ == "__main__":
    for project, target in PROJECTS.items():
        try:
            df = collect_project_data(project, target)
        except Exception as e:
            print(f"❌ Failed {project}: {e}")
            continue
    
    # Combine all
    files = ['pytorch_pytorch.csv', 'tensorflow_tensorflow.csv', 
             'kubernetes_kubernetes.csv', 'microsoft_vscode.csv', 'langchain-ai_langchain.csv']
    dfs = []
    for f in files:
        if os.path.exists(f):
            df = pd.read_csv(f)
            dfs.append(df)
            print(f"Loaded: {f} ({len(df)} PRs)")
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        combined.to_csv('combined_pr_data.csv', index=False)
        print(f"\n{'='*50}")
        print(f"✅ TOTAL: {len(combined)} PRs")
        print(f"{'='*50}")