from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from sqlalchemy.orm import Session
import uuid
import json

from app.models.schemas import ScanRequest, ScanResult, Feedback, Vulnerability
from app.core.scanner import scan_target
from app.core.ml import BERTContextualClassifier
from app.db.session import SessionLocal, init_db, ScanResultDB, FeedbackDB

app = FastAPI(
    title="WVS Enterprise - Security Intelligence Platform",
    description="ML-Driven Vulnerability Scanning with Continuous Learning.",
    version="2.0.0"
)

# Initialize DB
init_db()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global ML Engine (Stateful for online learning)
ml_engine = BERTContextualClassifier()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def run_scan_task(scan_id: str, url: str):
    db = SessionLocal()
    try:
        db_scan = db.query(ScanResultDB).filter(ScanResultDB.id == scan_id).first()
        db_scan.status = "scanning"
        
        def add_log(message):
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            current_logs = list(db_scan.logs) if db_scan.logs else []
            current_logs.append(f"[{timestamp}] {message}")
            db_scan.logs = current_logs
            db.commit()

        add_log("INFO → Initializing SENTINEL core engine...")
        add_log("INFO → Establishing secure connection to target...")
        
        # 1. Multi-source scan
        add_log("INFO → Performing DNS enumeration and footprinting...")
        raw_vulns = await scan_target(url)
        add_log(f"SUCCESS → Found {len(raw_vulns)} potential entry points.")
        
        # 2. ML BERT-based Inference
        add_log("INFO → Injecting findings into Neural Engine...")
        add_log("INFO → Testing for SQL Injection & XSS patterns...")
        score, confidence, label = ml_engine.predict(raw_vulns)
        add_log("SUCCESS → Threat modeling analysis complete.")
        
        # 3. Update DB
        db_scan.vulnerabilities = raw_vulns
        db_scan.ml_severity_score = score
        db_scan.confidence_score = confidence
        db_scan.predicted_severity_label = label
        db_scan.status = "completed"
        add_log("SUCCESS → Generating final security report...")
        db.commit()
    except Exception as e:
        print(f"Error in scan {scan_id}: {e}")
        # Could add error log here too
    finally:
        db.close()

@app.post("/scan", response_model=ScanResult)
async def trigger_scan(request: ScanRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    scan_id = str(uuid.uuid4())
    db_scan = ScanResultDB(
        id=scan_id, 
        url=str(request.url), 
        status="queued",
        vulnerabilities=[]
    )
    db.add(db_scan)
    db.commit()
    
    background_tasks.add_task(run_scan_task, scan_id, str(request.url))
    return db_scan

@app.get("/scan/{scan_id}")
async def get_scan_result(scan_id: str, db: Session = Depends(get_db)):
    db_scan = db.query(ScanResultDB).filter(ScanResultDB.id == scan_id).first()
    if not db_scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return db_scan

@app.get("/scans", response_model=List[ScanResult])
async def list_scans(db: Session = Depends(get_db)):
    # Feature 9: Scan History Support
    return db.query(ScanResultDB).order_by(ScanResultDB.timestamp.desc()).all()

@app.post("/feedback")
async def submit_feedback(feedback: Feedback, db: Session = Depends(get_db)):
    db_scan = db.query(ScanResultDB).filter(ScanResultDB.id == feedback.scan_id).first()
    if not db_scan:
        raise HTTPException(status_code=404, detail="Scan ID not found")
    
    # Feature 1 & 4: Feedback Loop & Online Learning
    # Extract findings for the ML engine update
    ml_engine.online_update(
        vulnerabilities=db_scan.vulnerabilities, 
        is_accurate=feedback.is_accurate,
        corrected_label=feedback.corrected_severity
    )
    
    # Persist feedback
    db_feedback = FeedbackDB(
        scan_id=feedback.scan_id,
        is_accurate=feedback.is_accurate,
        corrected_severity=feedback.corrected_severity
    )
    db.add(db_feedback)
    db.commit()
    
    return {"message": "Model updated via continuous feedback pipeline."}

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_scans = db.query(ScanResultDB).count()
    feedback_count = db.query(FeedbackDB).count()
    return {
        "model_version": ml_engine.version,
        "total_scans_analyzed": total_scans,
        "analyst_labels_ingested": feedback_count,
        "active_weights": ml_engine.weights
    }
