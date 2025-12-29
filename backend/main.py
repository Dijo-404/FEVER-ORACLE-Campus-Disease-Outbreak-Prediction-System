"""
FEVER ORACLE Backend
FastAPI server for campus disease outbreak prediction
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random
import uvicorn

app = FastAPI(
    title="FEVER ORACLE API",
    description="Campus Disease Outbreak Prediction System API",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Models ============

class SymptomReport(BaseModel):
    location: str
    symptoms: List[str]
    severity: str

class SymptomReportResponse(BaseModel):
    success: bool
    message: str
    report_id: str
    health_tip: str

class StatsResponse(BaseModel):
    total_reports: int
    reports_today: int
    active_clusters: int
    risk_level: str
    trend: str

class Alert(BaseModel):
    id: str
    severity: str
    title: str
    message: str
    location: str
    time: str

class HeatmapZone(BaseModel):
    id: str
    name: str
    report_count: int
    risk_level: str
    coordinates: dict

class PredictionPoint(BaseModel):
    date: str
    actual: Optional[int]
    predicted: int

# ============ In-Memory Storage (Demo) ============

reports_db: List[dict] = []

HEALTH_TIPS = [
    "Stay hydrated and get plenty of rest.",
    "Consider wearing a mask in crowded areas.",
    "Monitor your symptoms and seek care if they worsen.",
    "Wash hands frequently to prevent spread.",
    "Avoid close contact with others until symptoms improve.",
    "Maintain a healthy diet to support your immune system.",
    "Get adequate sleep to help your body recover.",
]

LOCATIONS = [
    {"id": "north-dorms", "name": "North Dorms", "coordinates": {"x": 20, "y": 15}},
    {"id": "south-dorms", "name": "South Dorms", "coordinates": {"x": 20, "y": 85}},
    {"id": "east-dorms", "name": "East Dorms", "coordinates": {"x": 80, "y": 50}},
    {"id": "west-dorms", "name": "West Dorms", "coordinates": {"x": 10, "y": 50}},
    {"id": "science-block", "name": "Science Block", "coordinates": {"x": 50, "y": 30}},
    {"id": "engineering", "name": "Engineering Building", "coordinates": {"x": 70, "y": 35}},
    {"id": "library", "name": "Library", "coordinates": {"x": 45, "y": 50}},
    {"id": "cafeteria-a", "name": "Cafeteria A", "coordinates": {"x": 35, "y": 70}},
    {"id": "cafeteria-b", "name": "Cafeteria B", "coordinates": {"x": 65, "y": 70}},
    {"id": "student-center", "name": "Student Center", "coordinates": {"x": 50, "y": 60}},
    {"id": "gym", "name": "Gym & Recreation", "coordinates": {"x": 85, "y": 80}},
]

# ============ Endpoints ============

@app.get("/")
async def root():
    return {
        "name": "FEVER ORACLE API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": [
            "/api/health",
            "/api/symptoms",
            "/api/stats",
            "/api/alerts",
            "/api/heatmap",
            "/api/predictions"
        ]
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/symptoms", response_model=SymptomReportResponse)
async def submit_symptoms(report: SymptomReport):
    """Submit anonymous symptom report"""
    report_id = f"RPT-{len(reports_db) + 1:06d}"
    
    report_data = {
        "id": report_id,
        "location": report.location,
        "symptoms": report.symptoms,
        "severity": report.severity,
        "timestamp": datetime.now().isoformat()
    }
    reports_db.append(report_data)
    
    health_tip = random.choice(HEALTH_TIPS)
    
    return SymptomReportResponse(
        success=True,
        message="Report submitted successfully",
        report_id=report_id,
        health_tip=health_tip
    )


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get dashboard statistics"""
    total_reports = len(reports_db) + random.randint(150, 200)  # Demo data
    reports_today = random.randint(12, 35)
    active_clusters = random.randint(2, 5)
    
    # Determine risk level based on reports
    if reports_today > 30:
        risk_level = "high"
        trend = "increasing"
    elif reports_today > 15:
        risk_level = "moderate"
        trend = "stable"
    else:
        risk_level = "low"
        trend = "decreasing"
    
    return StatsResponse(
        total_reports=total_reports,
        reports_today=reports_today,
        active_clusters=active_clusters,
        risk_level=risk_level,
        trend=trend
    )


@app.get("/api/alerts", response_model=List[Alert])
async def get_alerts():
    """Get active alerts"""
    alerts = [
        Alert(
            id="ALT-001",
            severity="warning",
            title="Elevated Reports Detected",
            message="Increased symptom reports in North Dorms area. Monitoring closely.",
            location="North Dorms",
            time="15 minutes ago"
        ),
        Alert(
            id="ALT-002",
            severity="info",
            title="Cluster Analysis Complete",
            message="AI analysis detected a potential cluster forming in Cafeteria B.",
            location="Cafeteria B",
            time="1 hour ago"
        ),
        Alert(
            id="ALT-003",
            severity="success",
            title="Risk Level Decreased",
            message="Science Block risk level has decreased from moderate to low.",
            location="Science Block",
            time="3 hours ago"
        ),
    ]
    return alerts


@app.get("/api/heatmap", response_model=List[HeatmapZone])
async def get_heatmap():
    """Get campus heatmap data"""
    heatmap_data = []
    
    for loc in LOCATIONS:
        # Count reports for this location
        location_reports = len([r for r in reports_db if r.get("location", "").lower() == loc["name"].lower()])
        
        # Add demo data
        report_count = location_reports + random.randint(0, 25)
        
        # Determine risk level
        if report_count > 20:
            risk_level = "high"
        elif report_count > 10:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        heatmap_data.append(HeatmapZone(
            id=loc["id"],
            name=loc["name"],
            report_count=report_count,
            risk_level=risk_level,
            coordinates=loc["coordinates"]
        ))
    
    return heatmap_data


@app.get("/api/predictions", response_model=List[PredictionPoint])
async def get_predictions():
    """Get outbreak predictions for the next 7 days"""
    predictions = []
    today = datetime.now()
    
    # Generate past 7 days (actual data) and future 7 days (predictions)
    for i in range(-7, 8):
        date = today + timedelta(days=i)
        date_str = date.strftime("%b %d")
        
        if i < 0:
            # Past data (actual)
            base = 15 + abs(i) * 2
            actual = base + random.randint(-3, 5)
            predicted = base + random.randint(-2, 4)
        elif i == 0:
            # Today
            actual = random.randint(18, 28)
            predicted = actual + random.randint(-2, 3)
        else:
            # Future (prediction only)
            actual = None
            # Trend upward slightly for demo
            predicted = 20 + i * 3 + random.randint(-2, 4)
        
        predictions.append(PredictionPoint(
            date=date_str,
            actual=actual,
            predicted=predicted
        ))
    
    return predictions


# ============ Run Server ============

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
