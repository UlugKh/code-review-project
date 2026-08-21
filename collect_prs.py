from github import Github
import pandas as pd
import time
import json
from datetime import datetime

# CONFIG - Replace with your token
GITHUB_TOKEN = "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"
PROJECTS = [
    "pytorch/pytorch",
    "tensorflow/tensorflow",
    "kubernetes/kubernetes",
    "microsoft/vscode",
    "langchain-ai/langchain"
]
PRS_PER_PROJECT = 300

def get_pr_data(repo, pr):
    """Extract all required PR data"""
    try:
        # Basic PR info
        pr_data = {
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
        
        # Get reviews
        for review in pr.get_reviews():
            pr_data['reviews'].append({
                'user': review.user.login if review.user else None,
                'state': review.state,
                'submitted_at': review.submitted_at.isoformat() if review.submitted_at else None,
                'body': review.body or ''
            })
            if review.user:
                pr_data['reviewers'].append(review.user.login)
        
        # Get review comments (code review comments)
        for comment in pr.get_review_comments():
            pr_data['review_comments'].append({
                'user': comment.user.login if comment.user else None,
                'body': comment.body or '',
                'created_at': comment.created_at.isoformat(),
                'path': comment.path,
                'position': comment.position
            })
        
        # Get commit messages
        for commit in pr.get_commits():
            pr_data['commit_messages'].append(commit.commit.message)
        
        # Get diff
        try:
            pr_data['diff'] = pr.diff
        except:
            pr_data['diff'] = None
            
        # Detect AI reviewer (simple heuristic: keywords in username or review body)
        ai_keywords = ['bot', 'ai', 'agent', 'copilot', 'codeball', 'mend', 'deep', 'openai', 'anthropic']
        pr_data['has_ai_reviewer'] = any(
            any(kw in r['user'].lower() for kw in ai_keywords) 
            for r in pr_data['reviews'] if r['user']
        )
        
        # Detect AI-generated code (heuristic: language patterns in commit messages or PR body)
        ai_code_indicators = ['copilot', 'chatgpt', 'claude', 'generated', 'ai-', 'llm']
        text_to_check = pr_data['title'] + ' ' + pr_data['body'] + ' ' + ' '.join(pr_data['commit_messages'])
        pr_data['has_ai_code'] = any(kw in text_to_check.lower() for kw in ai_code_indicators)
        
        return pr_data
        
    except Exception as e:
        print(f"Error processing PR #{pr.number}: {e}")
        return None

def collect_project_data(project_name):
    """Collect data for a single project"""
    print(f"\nCollecting data for: {project_name}")
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(project_name)
    
    prs_data = []
    
    # Get merged and closed PRs (including unmerged)
    for pr in repo.get_pulls(state='closed', sort='created', direction='desc'):
        if len(prs_data) >= PRS_PER_PROJECT:
            break
        if pr.merged or pr.state == 'closed':
            data = get_pr_data(repo, pr)
            if data:
                prs_data.append(data)
                print(f"  Collected PR #{pr.number} (merged: {pr.merged})")
            time.sleep(0.2)  # Rate limiting
    
    df = pd.DataFrame(prs_data)
    df.to_csv(f'{project_name.replace("/", "_")}.csv', index=False)
    
    # Save raw JSON backup
    with open(f'{project_name.replace("/", "_")}.json', 'w') as f:
        json.dump(prs_data, f, indent=2)
    
    print(f"Completed: {len(prs_data)} PRs for {project_name}")
    return df

if __name__ == "__main__":
    all_data = {}
    for project in PROJECTS:
        try:
            df = collect_project_data(project)
            all_data[project] = df
        except Exception as e:
            print(f"Failed on {project}: {e}")
    
    # Save combined dataset
    combined_df = pd.concat(all_data.values(), ignore_index=True)
    combined_df.to_csv('combined_pr_data.csv', index=False)
    print(f"\nTotal PRs collected: {len(combined_df)}")
    print("Data saved to combined_pr_data.csv")