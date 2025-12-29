"""
BigQuery integration for FEVER ORACLE
Data warehouse for symptom reports and analytics
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

IS_GCP = os.getenv("GOOGLE_CLOUD_PROJECT") is not None
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "fever-oracle")
DATASET_ID = os.getenv("BIGQUERY_DATASET", "fever_oracle")

if IS_GCP:
    from google.cloud import bigquery

class BigQueryService:
    """BigQuery client for data warehouse operations."""
    
    def __init__(self):
        self.project_id = PROJECT_ID
        self.dataset_id = DATASET_ID
        self.is_gcp = IS_GCP
        
        if self.is_gcp:
            self.client = bigquery.Client(project=self.project_id)
            self._ensure_dataset_exists()
    
    def _ensure_dataset_exists(self):
        """Create dataset if it doesn't exist."""
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        try:
            self.client.get_dataset(dataset_ref)
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            self.client.create_dataset(dataset, exists_ok=True)
    
    def create_tables(self):
        """Create all required BigQuery tables."""
        if not self.is_gcp:
            print("[LOCAL] Would create BigQuery tables")
            return
        
        # Symptom Reports Table
        reports_schema = [
            bigquery.SchemaField("report_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("location", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("symptoms", "STRING", mode="REPEATED"),
            bigquery.SchemaField("severity", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("longitude", "FLOAT"),
        ]
        self._create_table("symptom_reports", reports_schema)
        
        # Predictions Table
        predictions_schema = [
            bigquery.SchemaField("prediction_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("predicted_cases", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("actual_cases", "INTEGER"),
            bigquery.SchemaField("confidence", "FLOAT"),
            bigquery.SchemaField("model_version", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        self._create_table("predictions", predictions_schema)
        
        # Alerts Table
        alerts_schema = [
            bigquery.SchemaField("alert_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("severity", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("message", "STRING"),
            bigquery.SchemaField("location", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("resolved_at", "TIMESTAMP"),
        ]
        self._create_table("alerts", alerts_schema)
    
    def _create_table(self, table_name: str, schema: List):
        """Create a table with the given schema."""
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        table = bigquery.Table(table_ref, schema=schema)
        self.client.create_table(table, exists_ok=True)
    
    def insert_symptom_report(self, report: Dict[str, Any]) -> bool:
        """Insert a symptom report into BigQuery."""
        if not self.is_gcp:
            print(f"[LOCAL] Would insert report: {report}")
            return True
        
        table_ref = f"{self.project_id}.{self.dataset_id}.symptom_reports"
        row = {
            "report_id": report["id"],
            "location": report["location"],
            "symptoms": report["symptoms"],
            "severity": report["severity"],
            "timestamp": report["timestamp"],
            "latitude": report.get("latitude"),
            "longitude": report.get("longitude"),
        }
        
        errors = self.client.insert_rows_json(table_ref, [row])
        return len(errors) == 0
    
    def get_reports_by_location(self, location: str, days: int = 7) -> List[Dict]:
        """Get symptom reports for a location in the past N days."""
        if not self.is_gcp:
            return []
        
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.symptom_reports`
        WHERE location = @location
        AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
        ORDER BY timestamp DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("location", "STRING", location),
                bigquery.ScalarQueryParameter("days", "INT64", days),
            ]
        )
        
        results = self.client.query(query, job_config=job_config)
        return [dict(row) for row in results]
    
    def get_daily_stats(self, days: int = 30) -> List[Dict]:
        """Get daily aggregated statistics."""
        if not self.is_gcp:
            return []
        
        query = f"""
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as total_reports,
            COUNT(DISTINCT location) as locations_affected,
            COUNTIF(severity = 'high') as high_severity_count
        FROM `{self.project_id}.{self.dataset_id}.symptom_reports`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("days", "INT64", days),
            ]
        )
        
        results = self.client.query(query, job_config=job_config)
        return [dict(row) for row in results]
    
    def insert_prediction(self, prediction: Dict[str, Any]) -> bool:
        """Insert a prediction record."""
        if not self.is_gcp:
            print(f"[LOCAL] Would insert prediction: {prediction}")
            return True
        
        table_ref = f"{self.project_id}.{self.dataset_id}.predictions"
        row = {
            "prediction_id": prediction["id"],
            "date": prediction["date"],
            "predicted_cases": prediction["predicted_cases"],
            "actual_cases": prediction.get("actual_cases"),
            "confidence": prediction.get("confidence"),
            "model_version": prediction.get("model_version", "v1.0"),
            "created_at": datetime.utcnow().isoformat(),
        }
        
        errors = self.client.insert_rows_json(table_ref, [row])
        return len(errors) == 0


# Initialize BigQuery service
bigquery_service = BigQueryService()
