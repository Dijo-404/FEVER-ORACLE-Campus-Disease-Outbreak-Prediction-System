"""
Cloud Monitoring integration for FEVER ORACLE
Provides custom metrics for system health and performance
"""

import os
import time
from typing import Optional
from functools import wraps

# Check if running in GCP environment
IS_GCP = os.getenv("GOOGLE_CLOUD_PROJECT") is not None
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "fever-oracle")

if IS_GCP:
    from google.cloud import monitoring_v3
    from google.api import metric_pb2, label_pb2

class CloudMonitoring:
    """Cloud Monitoring client for custom metrics."""
    
    def __init__(self):
        self.project_id = PROJECT_ID
        self.is_gcp = IS_GCP
        
        if self.is_gcp:
            self.client = monitoring_v3.MetricServiceClient()
            self.project_name = f"projects/{self.project_id}"
    
    def write_metric(
        self,
        metric_type: str,
        value: float,
        labels: Optional[dict] = None
    ):
        """
        Write a custom metric to Cloud Monitoring.
        
        Args:
            metric_type: The metric type (e.g., 'symptom_reports_count')
            value: The metric value
            labels: Optional labels for the metric
        """
        if not self.is_gcp:
            print(f"[LOCAL] Metric: {metric_type} = {value}, labels={labels}")
            return
        
        series = monitoring_v3.TimeSeries()
        series.metric.type = f"custom.googleapis.com/fever_oracle/{metric_type}"
        series.resource.type = "global"
        
        # Add labels if provided
        if labels:
            for key, val in labels.items():
                series.metric.labels[key] = str(val)
        
        # Create data point
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        
        point = monitoring_v3.Point()
        point.value.double_value = value
        point.interval.end_time.seconds = seconds
        point.interval.end_time.nanos = nanos
        
        series.points = [point]
        
        # Write the time series
        self.client.create_time_series(
            name=self.project_name,
            time_series=[series]
        )
    
    def record_symptom_report(self, location: str, severity: str):
        """Record a symptom report metric."""
        self.write_metric(
            "symptom_reports_count",
            1,
            {"location": location, "severity": severity}
        )
    
    def record_api_latency(self, endpoint: str, latency_ms: float):
        """Record API endpoint latency."""
        self.write_metric(
            "api_latency_ms",
            latency_ms,
            {"endpoint": endpoint}
        )
    
    def record_active_clusters(self, count: int):
        """Record number of active outbreak clusters."""
        self.write_metric("active_clusters", count)
    
    def record_risk_level(self, level: str):
        """Record current campus risk level."""
        level_map = {"low": 1, "moderate": 2, "high": 3}
        self.write_metric(
            "risk_level",
            level_map.get(level, 0),
            {"level": level}
        )
    
    def record_prediction_accuracy(self, accuracy: float):
        """Record ML model prediction accuracy."""
        self.write_metric("prediction_accuracy", accuracy)


def monitor_endpoint(endpoint_name: str):
    """Decorator to monitor API endpoint latency."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                latency_ms = (time.time() - start_time) * 1000
                monitoring.record_api_latency(endpoint_name, latency_ms)
        return wrapper
    return decorator


# Initialize monitoring client
monitoring = CloudMonitoring()
