import os
import glob
import json
import logging
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Setup global server logger (runs in worker processes too)
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/server.log", level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from src.config import PROCESSED_FILE, PROCESSING_QUEUE_DIR, SENDER_EMAIL
from src.pipeline import run_outreach, get_latest_contacts_file
from src.template import generate_email_html

app = FastAPI(title="Outreach Applier API")

active_jobs = {}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/files")
async def list_files():
    """List all CSV files in the processing_queue directory with their processing stats"""
    if not os.path.exists(PROCESSING_QUEUE_DIR):
        return []
    files = glob.glob(os.path.join(PROCESSING_QUEUE_DIR, "*.csv"))
    
    result = []
    for f in files:
        filename = os.path.basename(f)
        try:
            df = pd.read_csv(f)
            total_rows = len(df)
            if 'verdict_group' in df.columns:
                processed = len(df[df['verdict_group'].notna() & (df['verdict_group'] != '')])
                success = len(df[df['verdict_group'].astype(str).str.lower() == 'success'])
                fail = len(df[df['verdict_group'].astype(str).str.lower().str.contains('error|failed')])
            elif 'verdict' in df.columns:
                processed = len(df[df['verdict'].notna() & (df['verdict'] != '')])
                success = len(df[df['verdict'].astype(str).str.lower() == 'sent'])
                fail = len(df[df['verdict'].astype(str).str.lower() == 'failed'])
            else:
                processed = 0
                success = 0
                fail = 0
        except Exception:
            total_rows, processed, success, fail = 0, 0, 0, 0
            
        result.append({
            "filename": filename,
            "created_at": os.path.getctime(f),
            "total_rows": total_rows,
            "processed": processed,
            "success": success,
            "fail": fail
        })
    return result

@app.get("/api/files/{filename}")
async def get_file_content(filename: str):
    """Return records from a specific CSV file"""
    file_path = os.path.join(PROCESSING_QUEUE_DIR, filename)
    if not os.path.exists(file_path):
        return {"status": "not_found", "message": "The file does not exist. It may have been deleted.", "data": []}
    try:
        df = pd.read_csv(file_path)
        df.fillna('', inplace=True)
        return {"status": "success", "message": "File loaded successfully.", "data": df.to_dict(orient='records')}
    except pd.errors.EmptyDataError:
        return {"status": "empty", "message": "File exists but has no rows.", "data": []}
    except Exception as e:
        return {"status": "error", "message": f"System error loading CSV: {str(e)}", "data": []}

@app.get("/api/history")
async def get_history():
    """Return all processed records from the global history excel file"""
    if not os.path.exists(PROCESSED_FILE):
        return []
    try:
        df = pd.read_excel(PROCESSED_FILE)
        df.fillna('', inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/logs")
async def get_logs():
    """Return all pipeline execution logs"""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        df = pd.read_csv(LOG_FILE)
        df.fillna('', inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}

LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs', 'pipeline_logs.csv'))

@app.get("/api/status/{filename}")
async def get_status(filename: str):
    """Check if a pipeline job is currently running for this file"""
    return {"is_running": active_jobs.get(filename, False)}

def log_job_request(filename: str, mode: str):
    """Log the pipeline request to a CSV file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=["Timestamp", "Filename", "Mode", "Status"])
        df.to_csv(LOG_FILE, index=False)
        
    new_log = pd.DataFrame([{
        "Timestamp": timestamp,
        "Filename": filename,
        "Mode": mode,
        "Status": "Triggered"
    }])
    new_log.to_csv(LOG_FILE, mode='a', header=False, index=False)

PROFILE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'profile.json'))

def get_current_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "name": "John Doe",
        "email": SENDER_EMAIL or "john.doe@example.com",
        "experience": "2+ years"
    }

@app.get("/api/profile")
def get_profile():
    return get_current_profile()

@app.post("/api/profile")
async def update_profile(request: Request):
    data = await request.json()
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f)
    return {"message": "Profile updated successfully"}

APP_CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app_config.json'))

@app.get("/api/config")
def get_app_config():
    if os.path.exists(APP_CONFIG_FILE):
        try:
            with open(APP_CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "roles": ["Software Development Engineer", "Backend Developer"],
        "templates": [{"id": "formal", "name": "Formal (Standard)"}]
    }

@app.get("/api/preview")
def preview_email(name: str = "Hiring Manager", company: str = "Example Corp", role: str = "SDE", template: str = "formal"):
    p = get_current_profile()
    html = generate_email_html(name, company, role=role, template_type=template, sender_name=p.get('name'), sender_exp=p.get('experience'), sender_email=p.get('email'))
    return {"html": html}

@app.post("/api/upload")
async def upload_file(request: Request, filename: str):
    """Upload a CSV file directly via raw body to avoid multipart dependencies"""
    if not filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    if not os.path.exists(PROCESSING_QUEUE_DIR):
        os.makedirs(PROCESSING_QUEUE_DIR, exist_ok=True)
        
    file_path = os.path.join(PROCESSING_QUEUE_DIR, filename)
    body = await request.body()
    with open(file_path, "wb") as f:
        f.write(body)
        
    return {"message": f"Successfully uploaded {filename}"}

@app.post("/api/run/{filename}")
async def trigger_pipeline(filename: str, background_tasks: BackgroundTasks, mode: str = 'all', role: str = 'SDE', template: str = 'formal'):
    """Trigger the email automation pipeline for a specific file in the background"""
    if active_jobs.get(filename):
        raise HTTPException(status_code=409, detail="A job is already running for this file. Please wait.")
        
    file_path = os.path.join(PROCESSING_QUEUE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    active_jobs[filename] = True
        
    def run_job():
        try:
            p = get_current_profile()
            run_outreach(file_path, mode=mode, role=role, template_type=template, profile=p)
        finally:
            active_jobs[filename] = False
    
    log_job_request(filename, mode)
    background_tasks.add_task(run_job)
    return {"message": f"Pipeline started for {filename} (mode: {mode})! Please refresh after a few moments."}

# Mount the frontend UI (this allows the backend to serve the frontend as a fallback)
ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outreach-ui', 'dist'))
if not os.path.exists(ui_path):
    ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outreach-ui'))

if os.path.exists(ui_path):
    app.mount("/", StaticFiles(directory=ui_path, html=True), name="ui")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
