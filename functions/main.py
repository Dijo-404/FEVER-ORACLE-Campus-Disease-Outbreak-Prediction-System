"""
Cloud Functions for FEVER ORACLE
Event-driven serverless functions
"""

import os
import json
import functions_framework
from google.cloud import pubsub_v1
from google.cloud import bigquery
from datetime import datetime

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "fever-oracle")


@functions_framework.cloud_event
def on_symptom_report(cloud_event):
    """
    Triggered when a new symptom report is published to Pub/Sub.
    Processes the report and updates analytics.
    """
    # Decode the Pub/Sub message
    data = json.loads(cloud_event.data["message"]["data"].decode("utf-8"))
    report = data.get("data", {})
    
    print(f"Processing symptom report: {report.get('id')}")
    
    # Insert into BigQuery
    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_ref = f"{PROJECT_ID}.fever_oracle.symptom_reports"
        
        row = {
            "report_id": report.get("id"),
            "location": report.get("location"),
            "symptoms": report.get("symptoms", []),
            "severity": report.get("severity"),
            "timestamp": report.get("timestamp", datetime.utcnow().isoformat()),
        }
        
        errors = client.insert_rows_json(table_ref, [row])
        
        if errors:
            print(f"BigQuery insert errors: {errors}")
        else:
            print(f"Report {report.get('id')} stored in BigQuery")
            
    except Exception as e:
        print(f"Error processing report: {e}")
    
    return "OK"


@functions_framework.cloud_event
def on_alert_triggered(cloud_event):
    """
    Triggered when a new alert is published.
    Sends notifications to relevant stakeholders.
    """
    data = json.loads(cloud_event.data["message"]["data"].decode("utf-8"))
    alert = data.get("data", {})
    
    print(f"Processing alert: {alert.get('id')}")
    
    # TODO: Send email/SMS notifications
    # TODO: Update Firebase Realtime Database
    # TODO: Log to Cloud Logging
    
    return "OK"


@functions_framework.http
def generate_daily_report(request):
    """
    HTTP-triggered function to generate daily health reports.
    Called by Cloud Scheduler.
    """
    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        # Query daily statistics
        query = """
        SELECT 
            DATE(timestamp) as report_date,
            COUNT(*) as total_reports,
            COUNT(DISTINCT location) as locations_affected,
            COUNTIF(severity = 'severe') as severe_count,
            COUNTIF(severity = 'moderate') as moderate_count,
            COUNTIF(severity = 'mild') as mild_count
        FROM `{project}.fever_oracle.symptom_reports`
        WHERE DATE(timestamp) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
        GROUP BY report_date
        """.format(project=PROJECT_ID)
        
        results = list(client.query(query).result())
        
        if results:
            report = dict(results[0])
            print(f"Daily report generated: {report}")
            
            # Store report in Cloud Storage
            # TODO: Implement storage
            
            return json.dumps({"status": "success", "report": report})
        
        return json.dumps({"status": "no_data"})
        
    except Exception as e:
        print(f"Error generating report: {e}")
        return json.dumps({"status": "error", "message": str(e)}), 500


@functions_framework.http
def retrain_model(request):
    """
    HTTP-triggered function to retrain the prediction model.
    Called by Cloud Scheduler.
    """
    try:
        from google.cloud import aiplatform
        
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location="us-central1")
        
        # TODO: Implement model retraining pipeline
        # - Fetch training data from BigQuery
        # - Train new model
        # - Deploy to endpoint if accuracy improved
        
        print("Model retraining triggered")
        return json.dumps({"status": "training_started"})
        
    except Exception as e:
        print(f"Error starting retraining: {e}")
        return json.dumps({"status": "error", "message": str(e)}), 500


@functions_framework.http
def health_check(request):
    """Health check endpoint for Cloud Functions."""
    return json.dumps({
        "status": "healthy",
        "service": "fever-oracle-functions",
        "timestamp": datetime.utcnow().isoformat()
    })
