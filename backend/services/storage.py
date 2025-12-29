"""
Cloud Storage integration for FEVER ORACLE
HIPAA-compliant data archival and model artifacts storage
"""

import os
import json
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime, timedelta

IS_GCP = os.getenv("GOOGLE_CLOUD_PROJECT") is not None
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "fever-oracle")
BUCKET_REPORTS = os.getenv("GCS_BUCKET_REPORTS", "fever-oracle-reports")
BUCKET_MODELS = os.getenv("GCS_BUCKET_MODELS", "fever-oracle-models")

if IS_GCP:
    from google.cloud import storage

class CloudStorageService:
    """Cloud Storage client for data archival."""
    
    def __init__(self):
        self.project_id = PROJECT_ID
        self.is_gcp = IS_GCP
        self.bucket_reports = BUCKET_REPORTS
        self.bucket_models = BUCKET_MODELS
        
        if self.is_gcp:
            self.client = storage.Client(project=self.project_id)
    
    def _get_bucket(self, bucket_name: str):
        """Get or create a bucket."""
        if not self.is_gcp:
            return None
        
        try:
            return self.client.get_bucket(bucket_name)
        except Exception:
            bucket = self.client.create_bucket(bucket_name, location="US")
            return bucket
    
    def upload_json(
        self,
        bucket_name: str,
        blob_path: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Upload JSON data to Cloud Storage.
        
        Args:
            bucket_name: Target bucket name
            blob_path: Path within the bucket
            data: Dictionary to store as JSON
            
        Returns:
            GCS URI of uploaded file
        """
        if not self.is_gcp:
            print(f"[LOCAL] Would upload to gs://{bucket_name}/{blob_path}")
            return f"gs://{bucket_name}/{blob_path}"
        
        bucket = self._get_bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type="application/json"
        )
        
        return f"gs://{bucket_name}/{blob_path}"
    
    def upload_file(
        self,
        bucket_name: str,
        blob_path: str,
        file_obj: BinaryIO,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload a file to Cloud Storage."""
        if not self.is_gcp:
            print(f"[LOCAL] Would upload file to gs://{bucket_name}/{blob_path}")
            return f"gs://{bucket_name}/{blob_path}"
        
        bucket = self._get_bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_file(file_obj, content_type=content_type)
        
        return f"gs://{bucket_name}/{blob_path}"
    
    def download_json(self, bucket_name: str, blob_path: str) -> Optional[Dict]:
        """Download JSON data from Cloud Storage."""
        if not self.is_gcp:
            return None
        
        bucket = self._get_bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        if not blob.exists():
            return None
        
        content = blob.download_as_string()
        return json.loads(content)
    
    def archive_symptom_report(self, report: Dict[str, Any]) -> str:
        """Archive a symptom report for HIPAA compliance."""
        date = datetime.utcnow()
        blob_path = f"reports/{date.year}/{date.month:02d}/{date.day:02d}/{report['id']}.json"
        
        # Add metadata for compliance
        archive_data = {
            **report,
            "archived_at": datetime.utcnow().isoformat(),
            "retention_until": (date + timedelta(days=365*7)).isoformat()  # 7 year retention
        }
        
        return self.upload_json(self.bucket_reports, blob_path, archive_data)
    
    def save_model_artifact(
        self,
        model_name: str,
        version: str,
        artifact_path: str,
        file_obj: BinaryIO
    ) -> str:
        """Save an ML model artifact."""
        blob_path = f"models/{model_name}/{version}/{artifact_path}"
        return self.upload_file(self.bucket_models, blob_path, file_obj)
    
    def get_model_artifact(
        self,
        model_name: str,
        version: str,
        artifact_path: str
    ) -> Optional[bytes]:
        """Retrieve an ML model artifact."""
        if not self.is_gcp:
            return None
        
        blob_path = f"models/{model_name}/{version}/{artifact_path}"
        bucket = self._get_bucket(self.bucket_models)
        blob = bucket.blob(blob_path)
        
        if not blob.exists():
            return None
        
        return blob.download_as_bytes()
    
    def list_model_versions(self, model_name: str) -> list:
        """List all versions of a model."""
        if not self.is_gcp:
            return []
        
        bucket = self._get_bucket(self.bucket_models)
        prefix = f"models/{model_name}/"
        
        blobs = bucket.list_blobs(prefix=prefix, delimiter="/")
        versions = set()
        
        for blob in blobs:
            parts = blob.name.split("/")
            if len(parts) >= 3:
                versions.add(parts[2])
        
        return sorted(list(versions), reverse=True)


# Initialize Cloud Storage service
storage_service = CloudStorageService()
