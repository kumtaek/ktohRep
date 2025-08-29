"""
Source Analyzer Web Dashboard - Backend API
FastAPI-based REST API with WebSocket support for real-time updates
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, RedirectResponse, JSONResponse
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
    include_ext: Optional[str] = None  # 예: ".java,.jsp,.xml"
    include_dirs: Optional[str] = None # 예: "src/main/java,src/main/webapp"

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
        
        # 정적 파일 마운트(원본 파일 미들웨어)
        repo_root = Path(__file__).parent.parent.parent
        project_dir = repo_root / "PROJECT"
        dbschema_dir = repo_root / "DB_SCHEMA"
        if project_dir.exists():
            app.mount("/project", StaticFiles(directory=str(project_dir)), name="project")
        if dbschema_dir.exists():
            app.mount("/dbschema", StaticFiles(directory=str(dbschema_dir)), name="dbschema")

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
        # SourceAnalyzer와 통합 실행
        from main import SourceAnalyzer

        # 구성 갱신: 파일 패턴 오버라이드(확장자/디렉토리 필터)
        cfg = app_state.config or {}
        file_patterns = cfg.setdefault('file_patterns', {})
        include = []
        if request.include_ext:
            for ext in [x.strip() for x in request.include_ext.split(',') if x.strip()]:
                if not ext.startswith('.'):
                    ext = '.' + ext
                include.append(f"**/*{ext}")
        if request.include_dirs:
            for d in [x.strip() for x in request.include_dirs.split(',') if x.strip()]:
                # 일반적으로 하위에서 표준 확장자 포함
                include.extend([f"{d}/**/*.java", f"{d}/**/*.jsp", f"{d}/**/*.xml"])
        if include:
            file_patterns['include'] = include

        analyzer = SourceAnalyzer(str(Path(__file__).parent.parent.parent / 'config' / 'config.yaml'))

        # 비동기 분석 실행
        result = await analyzer.analyze_project(
            request.project_path,
            request.project_name,
            request.incremental
        )

        # Broadcast analysis start
        await manager.broadcast(json.dumps({
            "type": "analysis_started",
            "data": {
                "project_path": request.project_path,
                "project_name": request.project_name,
                "timestamp": datetime.now().isoformat()
            }
        }))
        return {"message": "Analysis completed", "summary": result.get('summary', {}), "files_analyzed": result.get('files_analyzed', 0)}
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

# -------------------------------
# Export & File Open Endpoints
# -------------------------------

def _db_session():
    if not app_state.db_manager:
        raise HTTPException(status_code=500, detail="DB 미초기화")
    return app_state.db_manager.get_session()

@app.get("/api/export/{kind}.{fmt}", tags=["Export"])
async def export_data(kind: str, fmt: str, project_id: Optional[int] = Query(None)):
    """DB 기반 내보내기: classes/methods/sql/edges → csv/txt"""
    kind = kind.lower()
    fmt = fmt.lower()
    if kind not in {"classes","methods","sql","edges"}:
        raise HTTPException(status_code=400, detail="지원되지 않는 kind")
    if fmt not in {"csv","txt"}:
        raise HTTPException(status_code=400, detail="지원되지 않는 형식")

    from models.database import Class, Method, SqlUnit, Edge, File as SAFile
    import csv
    import io
    session = _db_session()
    try:
        if kind == 'classes':
            q = session.query(Class, SAFile).join(SAFile, Class.file_id == SAFile.file_id)
            if project_id:
                q = q.filter(SAFile.project_id == project_id)
            rows = [(c.class_id, c.fqn, c.name, c.start_line, c.end_line, f.path) for c,f in q.all()]
            headers = ["class_id","fqn","name","start","end","file_path"]
        elif kind == 'methods':
            q = session.query(Method, Class, SAFile).join(Class, Method.class_id==Class.class_id).join(SAFile, Class.file_id==SAFile.file_id)
            if project_id:
                q = q.filter(SAFile.project_id == project_id)
            rows = [(m.method_id, m.name, m.signature, m.return_type, m.start_line, m.end_line, c.fqn, f.path) for m,c,f in q.all()]
            headers = ["method_id","name","signature","return_type","start","end","class_fqn","file_path"]
        elif kind == 'sql':
            q = session.query(SqlUnit, SAFile).join(SAFile, SqlUnit.file_id==SAFile.file_id)
            if project_id:
                q = q.filter(SAFile.project_id == project_id)
            rows = [(s.sql_id, s.origin, s.mapper_ns, s.stmt_id, s.stmt_kind, s.start_line, s.end_line, f.path) for s,f in q.all()]
            headers = ["sql_id","origin","namespace","stmt_id","stmt_kind","start","end","file_path"]
        else:
            q = session.query(Edge)
            rows = [(e.edge_id, e.src_type, e.src_id, e.dst_type, e.dst_id, e.edge_kind, e.confidence) for e in q.all()]
            headers = ["edge_id","src_type","src_id","dst_type","dst_id","edge_kind","confidence"]

        if fmt == 'csv':
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(headers)
            for r in rows:
                w.writerow(list(r))
            buf.seek(0)
            return StreamingResponse(buf, media_type='text/csv', headers={'Content-Disposition': f'attachment; filename="{kind}.csv"'})
        else:
            content = '\n'.join(['\t'.join(map(lambda x: '' if x is None else str(x), r)) for r in rows])
            return StreamingResponse(io.StringIO(content), media_type='text/plain')
    finally:
        session.close()

@app.get("/api/file/download", tags=["Files"])
async def download_file(path: str = Query(..., description="절대경로 또는 /project,/dbschema 하위 상대경로")):
    """원본 파일 다운로드(보안상 PROJECT/DB_SCHEMA 하위 또는 DB의 파일경로만 권장)"""
    p = Path(path)
    if not p.is_absolute():
        # /project 또는 /dbschema 경로로부터 상대경로일 경우 서버 로컬 경로로 맵핑
        repo_root = Path(__file__).parent.parent.parent
        if path.startswith('/project/'):
            p = (repo_root / 'PROJECT' / Path(path).relative_to('/project')).resolve()
        elif path.startswith('/dbschema/'):
            p = (repo_root / 'DB_SCHEMA' / Path(path).relative_to('/dbschema')).resolve()
        else:
            # 기타 상대경로는 프로젝트 루트 기준 해석
            p = (repo_root / path).resolve()
    
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    return FileResponse(str(p))

@app.get("/api/open/owasp/{code}", tags=["Docs"])
async def open_owasp_doc(code: str):
    """OWASP/ CWE 문서로 리다이렉트"""
    code_u = code.upper()
    owasp_map = {
        'A01': 'https://owasp.org/Top10/A01_2021-Broken_Access_Control/',
        'A02': 'https://owasp.org/Top10/A02_2021-Cryptographic_Failures/',
        'A03': 'https://owasp.org/Top10/A03_2021-Injection/',
    }
    if code_u.startswith('CWE-'):
        return RedirectResponse(url=f"https://cwe.mitre.org/data/definitions/{code_u.split('-')[1]}.html")
    url = owasp_map.get(code_u, 'https://owasp.org/www-project-top-ten/')
    return RedirectResponse(url=url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
