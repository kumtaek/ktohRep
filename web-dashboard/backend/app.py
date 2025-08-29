"""
Source Analyzer Web Dashboard - Backend API
FastAPI-based REST API with WebSocket support for real-time updates
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

# Add phase1/src to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "phase1" / "src"))

from database.metadata_engine import MetadataEngine
from models.database import DatabaseManager
from utils.confidence_validator import ConfidenceValidator, ConfidenceCalibrator, GroundTruthEntry
from utils.confidence_calculator import ConfidenceCalculator
import yaml

# FastAPI app initialization
app = FastAPI(
    title="Source Analyzer Dashboard API",
    description="REST API for Source Analyzer Web Dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class AppState:
    def __init__(self):
        self.config = None
        self.db_manager = None
        self.confidence_validator = None
        self.confidence_calculator = None
        self.active_connections: List[WebSocket] = []
        self.current_analysis = None

app_state = AppState()

# Pydantic models
class ProjectInfo(BaseModel):
    project_id: int
    name: str
    root_path: str
    created_at: str
    updated_at: str

class AnalysisResult(BaseModel):
    project_id: int
    total_files: int
    success_count: int
    error_count: int
    java_files: int
    jsp_files: int
    xml_files: int
    total_classes: int
    total_methods: int
    total_sql_units: int

class ConfidenceReport(BaseModel):
    mean_absolute_error: float
    median_absolute_error: float
    error_distribution: Dict[str, Dict[str, Any]]
    total_validations: int

class GroundTruthEntryModel(BaseModel):
    file_path: str
    parser_type: str
    expected_confidence: float
    expected_classes: int = 0
    expected_methods: int = 0
    expected_sql_units: int = 0
    verified_tables: List[str] = []
    complexity_factors: Dict[str, Any] = {}
    notes: str = ""
    verifier: str = "web_user"

class AnalysisRequest(BaseModel):
    project_path: str
    project_name: str
    incremental: bool = False

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize system components"""
    try:
        # Load configuration
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                app_state.config = yaml.safe_load(f)
        else:
            # Default configuration
            app_state.config = {
                'database': {'path': 'source_analyzer.db'},
                'confidence': {'weights': {'ast': 0.4, 'static': 0.3, 'db_match': 0.2, 'heuristic': 0.1}},
                'validation': {'ground_truth_path': 'ground_truth_data.json'}
            }
        
        # Initialize database manager
        app_state.db_manager = DatabaseManager(app_state.config)
        app_state.db_manager.initialize()
        
        # Initialize confidence system
        app_state.confidence_calculator = ConfidenceCalculator(app_state.config)
        app_state.confidence_validator = ConfidenceValidator(app_state.config, app_state.confidence_calculator)
        
        print("✅ Source Analyzer Dashboard API initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        raise

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# API Routes
@app.get("/", tags=["Health"])
async def root():
    return {"message": "Source Analyzer Dashboard API", "status": "running"}

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database_connected": app_state.db_manager is not None
    }

@app.get("/api/projects", response_model=List[ProjectInfo], tags=["Projects"])
async def get_projects():
    """Get all projects"""
    try:
        session = app_state.db_manager.get_session()
        try:
            from models.database import Project
            projects = session.query(Project).all()
            return [
                ProjectInfo(
                    project_id=p.project_id,
                    name=p.name,
                    root_path=p.root_path,
                    created_at=p.created_at.isoformat() if p.created_at else "",
                    updated_at=p.updated_at.isoformat() if p.updated_at else ""
                )
                for p in projects
            ]
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/analysis", response_model=AnalysisResult, tags=["Analysis"])
async def get_project_analysis(project_id: int):
    """Get analysis results for a specific project"""
    try:
        session = app_state.db_manager.get_session()
        try:
            from models.database import File, Class, Method, SqlUnit
            
            # Count files by type
            files = session.query(File).filter(File.project_id == project_id).all()
            java_files = sum(1 for f in files if f.language == 'java')
            jsp_files = sum(1 for f in files if f.language == 'jsp')  
            xml_files = sum(1 for f in files if f.language == 'xml')
            
            # Count classes and methods
            total_classes = session.query(Class).join(File).filter(File.project_id == project_id).count()
            total_methods = session.query(Method).join(Class).join(File).filter(File.project_id == project_id).count()
            total_sql_units = session.query(SqlUnit).join(File).filter(File.project_id == project_id).count()
            
            return AnalysisResult(
                project_id=project_id,
                total_files=len(files),
                success_count=len(files),  # Simplified - assume all files processed successfully
                error_count=0,
                java_files=java_files,
                jsp_files=jsp_files,
                xml_files=xml_files,
                total_classes=total_classes,
                total_methods=total_methods,
                total_sql_units=total_sql_units
            )
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/confidence/report", response_model=ConfidenceReport, tags=["Confidence"])
async def get_confidence_report():
    """Get confidence validation report"""
    try:
        validation_result = app_state.confidence_validator.validate_confidence_formula()
        
        if 'error' in validation_result:
            raise HTTPException(status_code=400, detail=validation_result['error'])
        
        return ConfidenceReport(
            mean_absolute_error=validation_result.get('mean_absolute_error', 0.0),
            median_absolute_error=validation_result.get('median_absolute_error', 0.0),
            error_distribution=validation_result.get('error_distribution', {}),
            total_validations=validation_result.get('total_validations', 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/confidence/calibrate", tags=["Confidence"])
async def calibrate_confidence():
    """Calibrate confidence formula weights"""
    try:
        calibration_result = app_state.confidence_validator.calibrate_weights()
        
        if calibration_result.get('recommendation') == 'apply':
            calibrator = ConfidenceCalibrator(app_state.confidence_validator)
            if calibrator.apply_calibration(app_state.confidence_calculator):
                # Broadcast update to connected clients
                await manager.broadcast(json.dumps({
                    "type": "confidence_calibrated",
                    "data": calibration_result
                }))
                
        return calibration_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ground-truth", tags=["Ground Truth"])
async def get_ground_truth_entries():
    """Get all ground truth entries"""
    try:
        entries = []
        for entry in app_state.confidence_validator.ground_truth_data:
            entries.append({
                "file_path": entry.file_path,
                "parser_type": entry.parser_type,
                "expected_confidence": entry.expected_confidence,
                "expected_classes": entry.expected_classes,
                "expected_methods": entry.expected_methods,
                "expected_sql_units": entry.expected_sql_units,
                "verified_tables": entry.verified_tables,
                "notes": entry.notes,
                "verifier": entry.verifier,
                "verification_date": entry.verification_date
            })
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ground-truth", tags=["Ground Truth"])
async def add_ground_truth_entry(entry: GroundTruthEntryModel):
    """Add a new ground truth entry"""
    try:
        gt_entry = GroundTruthEntry(
            file_path=entry.file_path,
            parser_type=entry.parser_type,
            expected_confidence=entry.expected_confidence,
            expected_classes=entry.expected_classes,
            expected_methods=entry.expected_methods,
            expected_sql_units=entry.expected_sql_units,
            verified_tables=entry.verified_tables,
            complexity_factors=entry.complexity_factors,
            notes=entry.notes,
            verifier=entry.verifier
        )
        
        app_state.confidence_validator.add_ground_truth_entry(gt_entry)
        
        # Broadcast update to connected clients
        await manager.broadcast(json.dumps({
            "type": "ground_truth_added",
            "data": {"file_path": entry.file_path, "expected_confidence": entry.expected_confidence}
        }))
        
        return {"message": "Ground truth entry added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analysis/start", tags=["Analysis"])
async def start_analysis(request: AnalysisRequest):
    """Start a new project analysis"""
    try:
        # This would integrate with the existing SourceAnalyzer
        # For now, return a placeholder response
        
        # Broadcast analysis start
        await manager.broadcast(json.dumps({
            "type": "analysis_started",
            "data": {
                "project_path": request.project_path,
                "project_name": request.project_name,
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        return {
            "message": "Analysis started",
            "project_path": request.project_path,
            "project_name": request.project_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back for now - can add more sophisticated handling
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)