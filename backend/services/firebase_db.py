"""
Firebase Realtime Database integration for FEVER ORACLE
Real-time data synchronization for dashboard
"""

import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime

IS_GCP = os.getenv("GOOGLE_CLOUD_PROJECT") is not None

if IS_GCP:
    import firebase_admin
    from firebase_admin import credentials, db

class FirebaseRealtimeDB:
    """Firebase Realtime Database client for real-time updates."""
    
    def __init__(self):
        self.is_gcp = IS_GCP
        self.initialized = False
        
        if self.is_gcp:
            self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        try:
            # Check if already initialized
            firebase_admin.get_app()
            self.initialized = True
        except ValueError:
            # Not initialized, initialize now
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            database_url = os.getenv(
                "FIREBASE_DATABASE_URL",
                f"https://{os.getenv('GOOGLE_CLOUD_PROJECT')}-default-rtdb.firebaseio.com"
            )
            
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    "databaseURL": database_url
                })
                self.initialized = True
            else:
                # Use default credentials (for Cloud Run)
                try:
                    firebase_admin.initialize_app(options={
                        "databaseURL": database_url
                    })
                    self.initialized = True
                except Exception as e:
                    print(f"Firebase initialization failed: {e}")
    
    def set(self, path: str, data: Dict[str, Any]) -> bool:
        """Set data at a path (overwrites existing data)."""
        if not self.is_gcp or not self.initialized:
            print(f"[LOCAL] Would set {path}: {data}")
            return True
        
        try:
            ref = db.reference(path)
            ref.set(data)
            return True
        except Exception as e:
            print(f"Firebase set error: {e}")
            return False
    
    def update(self, path: str, data: Dict[str, Any]) -> bool:
        """Update data at a path (merges with existing data)."""
        if not self.is_gcp or not self.initialized:
            print(f"[LOCAL] Would update {path}: {data}")
            return True
        
        try:
            ref = db.reference(path)
            ref.update(data)
            return True
        except Exception as e:
            print(f"Firebase update error: {e}")
            return False
    
    def push(self, path: str, data: Dict[str, Any]) -> Optional[str]:
        """Push new data to a list (auto-generates key)."""
        if not self.is_gcp or not self.initialized:
            print(f"[LOCAL] Would push to {path}: {data}")
            return "local-key"
        
        try:
            ref = db.reference(path)
            new_ref = ref.push(data)
            return new_ref.key
        except Exception as e:
            print(f"Firebase push error: {e}")
            return None
    
    def get(self, path: str) -> Optional[Any]:
        """Get data at a path."""
        if not self.is_gcp or not self.initialized:
            return None
        
        try:
            ref = db.reference(path)
            return ref.get()
        except Exception as e:
            print(f"Firebase get error: {e}")
            return None
    
    def delete(self, path: str) -> bool:
        """Delete data at a path."""
        if not self.is_gcp or not self.initialized:
            print(f"[LOCAL] Would delete {path}")
            return True
        
        try:
            ref = db.reference(path)
            ref.delete()
            return True
        except Exception as e:
            print(f"Firebase delete error: {e}")
            return False
    
    # Dashboard-specific methods
    def update_live_stats(self, stats: Dict[str, Any]) -> bool:
        """Update live dashboard statistics."""
        return self.set("/dashboard/stats", {
            **stats,
            "updated_at": datetime.utcnow().isoformat()
        })
    
    def add_live_alert(self, alert: Dict[str, Any]) -> Optional[str]:
        """Add a new alert to the live feed."""
        return self.push("/dashboard/alerts", {
            **alert,
            "created_at": datetime.utcnow().isoformat()
        })
    
    def update_heatmap_zone(self, zone_id: str, data: Dict[str, Any]) -> bool:
        """Update a heatmap zone."""
        return self.update(f"/dashboard/heatmap/{zone_id}", {
            **data,
            "updated_at": datetime.utcnow().isoformat()
        })
    
    def update_predictions(self, predictions: list) -> bool:
        """Update prediction data for the chart."""
        return self.set("/dashboard/predictions", {
            "data": predictions,
            "updated_at": datetime.utcnow().isoformat()
        })


# Initialize Firebase Realtime DB service
firebase_db = FirebaseRealtimeDB()
