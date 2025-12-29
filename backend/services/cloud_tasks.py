"""
Cloud Tasks integration for FEVER ORACLE
Task queue for alert scheduling and async processing
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

IS_GCP = os.getenv("GOOGLE_CLOUD_PROJECT") is not None
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "fever-oracle")
LOCATION = os.getenv("CLOUD_TASKS_LOCATION", "us-central1")
QUEUE_NAME = os.getenv("CLOUD_TASKS_QUEUE", "fever-oracle-tasks")

if IS_GCP:
    from google.cloud import tasks_v2
    from google.protobuf import timestamp_pb2

class CloudTasksService:
    """Cloud Tasks client for async task processing."""
    
    def __init__(self):
        self.project_id = PROJECT_ID
        self.location = LOCATION
        self.queue_name = QUEUE_NAME
        self.is_gcp = IS_GCP
        
        if self.is_gcp:
            self.client = tasks_v2.CloudTasksClient()
            self.queue_path = self.client.queue_path(
                self.project_id, self.location, self.queue_name
            )
    
    def create_task(
        self,
        url: str,
        payload: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
        task_id: Optional[str] = None
    ) -> str:
        """
        Create a new Cloud Task.
        
        Args:
            url: Target URL to call
            payload: JSON payload for the request
            schedule_time: Optional time to execute the task
            task_id: Optional custom task ID
            
        Returns:
            Task name
        """
        if not self.is_gcp:
            print(f"[LOCAL] Would create task for {url} with payload: {payload}")
            return "local-task-id"
        
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode()
            }
        }
        
        if task_id:
            task["name"] = f"{self.queue_path}/tasks/{task_id}"
        
        if schedule_time:
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(schedule_time)
            task["schedule_time"] = timestamp
        
        response = self.client.create_task(
            parent=self.queue_path,
            task=task
        )
        
        return response.name
    
    def schedule_alert(
        self,
        alert_data: Dict[str, Any],
        target_url: str,
        delay_seconds: int = 0
    ) -> str:
        """
        Schedule an alert to be sent.
        
        Args:
            alert_data: Alert information
            target_url: URL to send the alert to
            delay_seconds: Delay before sending
            
        Returns:
            Task ID
        """
        schedule_time = None
        if delay_seconds > 0:
            schedule_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
        
        return self.create_task(
            url=target_url,
            payload={
                "type": "send_alert",
                "alert": alert_data,
                "scheduled_at": datetime.utcnow().isoformat()
            },
            schedule_time=schedule_time,
            task_id=f"alert-{alert_data.get('id', 'unknown')}"
        )
    
    def schedule_report_processing(
        self,
        report_data: Dict[str, Any],
        target_url: str
    ) -> str:
        """Schedule a symptom report for processing."""
        return self.create_task(
            url=target_url,
            payload={
                "type": "process_report",
                "report": report_data,
                "created_at": datetime.utcnow().isoformat()
            },
            task_id=f"report-{report_data.get('id', 'unknown')}"
        )
    
    def schedule_model_retraining(
        self,
        model_name: str,
        target_url: str,
        delay_hours: int = 24
    ) -> str:
        """Schedule ML model retraining."""
        schedule_time = datetime.utcnow() + timedelta(hours=delay_hours)
        
        return self.create_task(
            url=target_url,
            payload={
                "type": "retrain_model",
                "model_name": model_name,
                "scheduled_for": schedule_time.isoformat()
            },
            schedule_time=schedule_time,
            task_id=f"retrain-{model_name}-{int(schedule_time.timestamp())}"
        )
    
    def schedule_daily_report(
        self,
        report_type: str,
        target_url: str,
        run_at_hour: int = 8
    ) -> str:
        """Schedule a daily report generation."""
        now = datetime.utcnow()
        schedule_time = now.replace(hour=run_at_hour, minute=0, second=0)
        
        if schedule_time <= now:
            schedule_time += timedelta(days=1)
        
        return self.create_task(
            url=target_url,
            payload={
                "type": "generate_report",
                "report_type": report_type,
                "date": now.strftime("%Y-%m-%d")
            },
            schedule_time=schedule_time,
            task_id=f"report-{report_type}-{now.strftime('%Y%m%d')}"
        )


# Initialize Cloud Tasks service  
cloud_tasks = CloudTasksService()
