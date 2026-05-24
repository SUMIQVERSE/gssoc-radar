import os
import requests
from fastapi import FastAPI, BackgroundTasks
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load Environment Variables
load_dotenv()

# ==========================================
# 1. APP & DATABASE INITIALIZATION
# ==========================================
app = FastAPI()

# Supabase Setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("⚠️ WARNING: Supabase credentials missing!")
    supabase = None

# GitHub Token Setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# ==========================================
# 2. CORE BACKGROUND LOGIC (NO TIMEOUT)
# ==========================================
def process_all_projects():
    print("🚀 Background Sync Started for 300+ Repos...")
    
    try:
        JSON_URL = "https://gssoc.girlscript.org/api/projects" 
        
        response = requests.get(JSON_URL)
        if response.status_code != 200:
            print("❌ Error: JSON file load nahi hui!")
            return
            
        projects = response.json()
        processed_projects = []

        for project in projects:
            try:
                # GitHub Topics
                topics = (project.get('gh') or {}).get('topics', [])
                
                # GitHub Repo Link & Path Extraction
                repo_link = project.get("project_link", "")
                repo_path = repo_link.replace("https://github.com/", "").strip("/")
                
                stars = 0
                forks = 0
                issues = 0
                live_data = {}
                
                # GitHub API Fetch (With Token Headers)
                if repo_path:
                    api_url = f"https://api.github.com/repos/{repo_path}"
                    gh_response = requests.get(api_url, headers=GITHUB_HEADERS)
                    
                    if gh_response.status_code == 200:
                        live_data = gh_response.json()
                        stars = live_data.get("stargazers_count", 0)
                        forks = live_data.get("forks_count", 0)
                        issues = live_data.get("open_issues_count", 0)
                        
                        if not topics:
                            topics = live_data.get("topics", [])
                    else:
                        print(f"⚠️ GitHub API fail for {repo_path}: Code {gh_response.status_code}")

                # Data Insertion
                data_to_insert = {
                    "owner_repo": repo_path, 
                    "name": project.get("name", repo_path.split("/")[-1]),
                    "repo_url": repo_link,
                    "admin_name": project.get("admin_name", repo_path.split("/")[0]),
                    "tech_stack": project.get("tech_stack", []), 
                    "topics": topics,
                    "open_issues": issues, 
                    "closed_issues": project.get("closed_issues", 0), 
                    "assigned_issues": project.get("assigned_issues", 0),
                    "health_score": project.get("health_score", 0.0),
                    "open_assigned_issues": project.get("open_assigned_issues", 0),
                    "closed_assigned_issues": project.get("closed_assigned_issues", 0),
                    "description": live_data.get("description", project.get("description", "")),
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
                
                # 5. Supabase Upsert
                if supabase:
                    supabase.table("gssoc_projects").upsert(data_to_insert).execute()
                
                processed_projects.append(project)
                print(f"✅ Processed: {repo_path}")
                
            except Exception as item_error:
                print(f"❌ Error in {project.get('name', 'Unknown Repo')}: {item_error}")
                continue 

        print(f"🎉 SUCCESS! All {len(processed_projects)} projects synced in background!")
        
    except Exception as e:
        print(f"💥 Background task crashed: {e}")

# ==========================================
# 3. FASTAPI ROUTES
# ==========================================
@app.get("/sync")
def start_sync(background_tasks: BackgroundTasks):
    """
    Cron-job hit point: Yeh turant 200 OK bhejega aur piche loop chalata rahega.
    """
    background_tasks.add_task(process_all_projects)
    return {
        "status": "success", 
        "message": "Background Sync Started! 300+ repos 2-3 minute mein update ho jayenge. 🚀",
        "note": "Check Render Logs or Supabase Dashboard to see live progress."
    }

@app.get("/")
def read_root():
    return {"status": "GSSoC Radar Backend is Live & Running! 🎉"}