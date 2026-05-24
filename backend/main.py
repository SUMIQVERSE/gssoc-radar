from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

async def fetch_github_metrics(owner_repo: str):
    url = f"https://api.github.com/repos/{owner_repo}/issues?state=all&per_page=100"
    response = requests.get(url, headers=GITHUB_HEADERS)
    
    if response.status_code != 200:
        return {"total_open": 0, "total_closed": 0, "open_assigned": 0, "closed_assigned": 0}
        
    issues = response.json()
    actual_issues = [i for i in issues if "pull_request" not in i]
    
    total_open = sum(1 for i in actual_issues if i['state'] == 'open')
    total_closed = sum(1 for i in actual_issues if i['state'] == 'closed')
    
    open_assigned = sum(1 for i in actual_issues if i['state'] == 'open' and i.get('assignee') is not None)
    closed_assigned = sum(1 for i in actual_issues if i['state'] == 'closed' and i.get('assignee') is not None)
    
    return {
        "total_open": total_open,
        "total_closed": total_closed,
        "open_assigned": open_assigned,
        "closed_assigned": closed_assigned
    }

@app.get("/sync")
async def sync_gssoc_data():
    gssoc_url = "https://gssoc.girlscript.org/api/projects"
    
    try:
        gssoc_data = requests.get(gssoc_url).json()
    except Exception as e:
        return {"error": "Failed to fetch GSSoC API"}
    
    processed_projects = []
    
    for project in gssoc_data.get('projects', []):
        owner_repo = project.get('owner_repo')
        if not owner_repo: continue
            
        print(f"Processing: {owner_repo}")
        live_metrics = await fetch_github_metrics(owner_repo)
        
        total_open = live_metrics['total_open']
        total_closed = live_metrics['total_closed']
        open_assigned = live_metrics['open_assigned']
        closed_assigned = live_metrics['closed_assigned']
        
        total_assigned = open_assigned + closed_assigned
        
        if total_open > 0:
            health_score = round((total_assigned / (total_open + total_closed)) * 100, 2)
        else:
            health_score = 0
            
        project_record = {
            "owner_repo": owner_repo,
            "name": project.get('name', 'Unknown'),
            "description": project.get('description', ''),
            "repo_url": project.get('repo_url', ''),
            "admin_name": project.get('admin_name', ''),
            "tech_stack": project.get('tech_stack', []),
            "topics": (project.get('gh') or {}).get('topics', []),
            "open_issues": total_open,
            "closed_issues": total_closed,
            "open_assigned_issues": open_assigned,
            "closed_assigned_issues": closed_assigned,
            "assigned_issues": total_assigned,
            "health_score": health_score
        }
        processed_projects.append(project_record)
        
    supabase_endpoint = f"{SUPABASE_URL}/rest/v1/gssoc_projects?on_conflict=owner_repo"
    
    db_response = requests.post(supabase_endpoint, headers=SUPABASE_HEADERS, json=processed_projects)
    
    if db_response.status_code not in [200, 201]:
        print("Supabase Error:", db_response.text) 
        return {"status": "failed", "error": db_response.json()}
    
    return {"status": "success", "synced_count": len(processed_projects)}