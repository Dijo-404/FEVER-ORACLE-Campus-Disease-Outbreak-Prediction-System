"""
Cloud Pub/Sub integration for FEVER ORACLE
Real-time messaging for symptom reports and alerts
"""

import os
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime

IS_GCP = os.getenv("GOOGLE_CLOUD_PROJECT") is not None
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "fever-oracle")

# Topic names
TOPIC_SYMPTOM_REPORTS = os.getenv("PUBSUB_TOPIC_REPORTS", "symptom-reports")
TOPIC_ALERTS = os.getenv("PUBSUB_TOPIC_ALERTS", "alerts")
TOPIC_PREDICTIONS = os.getenv("PUBSUB_TOPIC_PREDICTIONS", "predictions")

if IS_GCP:
    from google.cloud import pubsub_v1
    from google.api_core import retry

class PubSubService:
    """Cloud Pub/Sub client for real-time messaging."""
    
    def __init__(self):
        self.project_id = PROJECT_ID
        self.is_gcp = IS_GCP
        
        if self.is_gcp:
            self.publisher = pubsub_v1.PublisherClient()
            self.subscriber = pubsub_v1.SubscriberClient()
    
    def _get_topic_path(self, topic_name: str) -> str:
        """Get full topic path."""
        if self.is_gcp:
            return self.publisher.topic_path(self.project_id, topic_name)
        return f"projects/{self.project_id}/topics/{topic_name}"
    
    def _get_subscription_path(self, subscription_name: str) -> str:
        """Get full subscription path."""
        if self.is_gcp:
            return self.subscriber.subscription_path(self.project_id, subscription_name)
        return f"projects/{self.project_id}/subscriptions/{subscription_name}"
    
    def publish(self, topic_name: str, data: Dict[str, Any], **attributes) -> str:
        """
        Publish a message to a topic.
        
        Args:
            topic_name: Name of the Pub/Sub topic
            data: Message data as dictionary
            **attributes: Additional message attributes
            
        Returns:
            Message ID
        """
        if not self.is_gcp:
            print(f"[LOCAL] Would publish to {topic_name}: {data}")
            return "local-message-id"
        
        topic_path = self._get_topic_path(topic_name)
        message_data = json.dumps(data).encode("utf-8")
        
        future = self.publisher.publish(
            topic_path,
            message_data,
            **{k: str(v) for k, v in attributes.items()}
        )
        
        return future.result()
    
    def publish_symptom_report(self, report: Dict[str, Any]) -> str:
        """Publish a symptom report to the reports topic."""
        return self.publish(
            TOPIC_SYMPTOM_REPORTS,
            {
                "type": "symptom_report",
                "data": report,
                "timestamp": datetime.utcnow().isoformat()
            },
            event_type="symptom_report",
            location=report.get("location", "unknown")
        )
    
    def publish_alert(self, alert: Dict[str, Any]) -> str:
        """Publish an alert to the alerts topic."""
        return self.publish(
            TOPIC_ALERTS,
            {
                "type": "alert",
                "data": alert,
                "timestamp": datetime.utcnow().isoformat()
            },
            event_type="alert",
            severity=alert.get("severity", "info")
        )
    
    def publish_prediction(self, prediction: Dict[str, Any]) -> str:
        """Publish a prediction to the predictions topic."""
        return self.publish(
            TOPIC_PREDICTIONS,
            {
                "type": "prediction",
                "data": prediction,
                "timestamp": datetime.utcnow().isoformat()
            },
            event_type="prediction"
        )
    
    def subscribe(
        self,
        subscription_name: str,
        callback: Callable,
        timeout: Optional[float] = None
    ):
        """
        Subscribe to messages from a subscription.
        
        Args:
            subscription_name: Name of the subscription
            callback: Function to call for each message
            timeout: Optional timeout in seconds
        """
        if not self.is_gcp:
            print(f"[LOCAL] Would subscribe to {subscription_name}")
            return
        
        subscription_path = self._get_subscription_path(subscription_name)
        
        def wrapped_callback(message):
            try:
                data = json.loads(message.data.decode("utf-8"))
                callback(data, message.attributes)
                message.ack()
            except Exception as e:
                print(f"Error processing message: {e}")
                message.nack()
        
        streaming_pull_future = self.subscriber.subscribe(
            subscription_path,
            callback=wrapped_callback
        )
        
        if timeout:
            try:
                streaming_pull_future.result(timeout=timeout)
            except Exception:
                streaming_pull_future.cancel()


# Initialize Pub/Sub service
pubsub_service = PubSubService()
