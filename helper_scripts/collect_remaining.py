from github import Github
import pandas as pd
import time
import json
import os

GITHUB_TOKEN = "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"
PROJECTS = ["microsoft/vscode", "langchain-ai/langchain"]
PRS_PER_PROJECT = 300

def collect_project_data(project_name):
    print(f"\n{'='*50}")
    print(f"Collecting: {project_name}")
    print(f"{'='*50}")
    
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(project_name)
    prs_data = []
    
    filename = f'{project_name.replace("/", "_")}.csv'
    
    # Check if partially collected
    collected_ids = set()
    if os.path.exists(filename):
        existing = pd.read_csv(filename)
        if not existing.empty:
            prs_data = existing.to_dict('records')
            collected_ids = set(existing['pr_id'])
            print(f"  Already have {len(prs_data)} PRs")
    
    count = 0
    for pr in repo.get_pulls(state='closed', sort='created', direction='desc'):
        if len(prs_data) >= PRS_PER_PROJECT:
            break
            
        # Skip if we already have this PR
        if pr.number in collected_ids:
            continue
            
        count += 1
        if count % 10 == 0:
            print(f"  Processed {count} PRs, collected {len(prs_data)}")
            
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
                print(f"  ✅ PR #{pr.number}")
                
                # Save every 5 PRs
                if len(prs_data) % 5 == 0:
                    pd.DataFrame(prs_data).to_csv(filename, index=False)
                    
            except Exception as e:
                print(f"  ⚠️ Error on PR #{pr.number}: {str(e)[:40]}")
                continue
            time.sleep(0.15)
    
    if prs_data:
        pd.DataFrame(prs_data).to_csv(filename, index=False)
        with open(f'{project_name.replace("/", "_")}.json', 'w') as f:
            json.dump(prs_data, f, indent=2)
    
    print(f"\n✅ {project_name}: {len(prs_data)} PRs")
    return pd.DataFrame(prs_data) if prs_data else pd.DataFrame()

if __name__ == "__main__":
    all_data = {}
    for project in PROJECTS:
        try:
            df = collect_project_data(project)
            if not df.empty:
                all_data[project] = df
        except Exception as e:
            print(f"❌ Failed {project}: {e}")
    
    # Combine all
    files = ['pytorch_pytorch.csv', 'tensorflow_tensorflow.csv', 
             'kubernetes_kubernetes.csv', 'microsoft_vscode.csv', 'langchain-ai_langchain.csv']
    dfs = []
    for f in files:
        if os.path.exists(f):
            dfs.append(pd.read_csv(f))
            print(f"Loaded: {f} ({len(pd.read_csv(f))} PRs)")
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        combined.to_csv('combined_pr_data.csv', index=False)
        print(f"\n{'='*50}")
        print(f"✅ TOTAL: {len(combined)} PRs")
        print(f"{'='*50}")

        