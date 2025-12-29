"""
Cloud Logging integration for FEVER ORACLE
Provides structured logging to Google Cloud Logging
"""

import os
import logging
import sys
from typing import Optional

# Check if running in GCP environment
IS_GCP = os.getenv("GOOGLE_CLOUD_PROJECT") is not None

if IS_GCP:
    from google.cloud import logging as cloud_logging
    from google.cloud.logging_v2.handlers import CloudLoggingHandler

def setup_cloud_logging(log_name: str = "fever-oracle-api") -> logging.Logger:
    """
    Set up Cloud Logging for the application.
    Falls back to standard logging if not in GCP environment.
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    
    if IS_GCP:
        # Initialize Cloud Logging client
        client = cloud_logging.Client()
        
        # Create Cloud Logging handler
        handler = CloudLoggingHandler(client, name=log_name)
        handler.setLevel(logging.INFO)
        
        # Add handler to logger
        logger.addHandler(handler)
        logger.info("Cloud Logging initialized successfully")
    else:
        # Fallback to standard console logging for local development
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.info("Using local console logging (not in GCP environment)")
    
    return logger

def log_symptom_report(logger: logging.Logger, report_id: str, location: str, severity: str):
    """Log a symptom report submission with structured data."""
    logger.info(
        "Symptom report submitted",
        extra={
            "json_fields": {
                "report_id": report_id,
                "location": location,
                "severity": severity,
                "event_type": "symptom_report"
            }
        }
    )

def log_alert_generated(logger: logging.Logger, alert_id: str, severity: str, location: str):
    """Log an alert generation with structured data."""
    logger.info(
        "Alert generated",
        extra={
            "json_fields": {
                "alert_id": alert_id,
                "severity": severity,
                "location": location,
                "event_type": "alert_generated"
            }
        }
    )

def log_prediction_made(logger: logging.Logger, prediction_value: int, confidence: float):
    """Log an AI prediction with structured data."""
    logger.info(
        "Prediction generated",
        extra={
            "json_fields": {
                "predicted_cases": prediction_value,
                "confidence": confidence,
                "event_type": "prediction_made"
            }
        }
    )

# Initialize default logger
logger = setup_cloud_logging()
