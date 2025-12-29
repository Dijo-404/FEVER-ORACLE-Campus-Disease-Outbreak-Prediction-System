"""
Vertex AI integration for FEVER ORACLE
ML model training and prediction for outbreak forecasting
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime

IS_GCP = os.getenv("GOOGLE_CLOUD_PROJECT") is not None
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "fever-oracle")
LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
ENDPOINT_ID = os.getenv("VERTEX_AI_ENDPOINT_ID")

if IS_GCP:
    from google.cloud import aiplatform
    from google.cloud.aiplatform import Model, Endpoint

class VertexAIService:
    """Vertex AI client for ML predictions and model management."""
    
    def __init__(self):
        self.project_id = PROJECT_ID
        self.location = LOCATION
        self.endpoint_id = ENDPOINT_ID
        self.is_gcp = IS_GCP
        
        if self.is_gcp:
            aiplatform.init(project=self.project_id, location=self.location)
    
    def predict(self, instances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Make predictions using the deployed model.
        
        Args:
            instances: List of input instances for prediction
            
        Returns:
            List of predictions
        """
        if not self.is_gcp or not self.endpoint_id:
            # Return mock predictions for local development
            return self._mock_predictions(instances)
        
        try:
            endpoint = Endpoint(
                endpoint_name=f"projects/{self.project_id}/locations/{self.location}/endpoints/{self.endpoint_id}"
            )
            
            response = endpoint.predict(instances=instances)
            return response.predictions
        except Exception as e:
            print(f"Vertex AI prediction error: {e}")
            return self._mock_predictions(instances)
    
    def _mock_predictions(self, instances: List[Dict]) -> List[Dict]:
        """Generate mock predictions for development."""
        import random
        predictions = []
        
        for instance in instances:
            base_value = instance.get("current_cases", 20)
            predictions.append({
                "predicted_cases": base_value + random.randint(-5, 15),
                "confidence": round(random.uniform(0.75, 0.95), 2),
                "risk_level": random.choice(["low", "moderate", "high"]),
                "trend": random.choice(["increasing", "stable", "decreasing"])
            })
        
        return predictions
    
    def predict_outbreak(
        self,
        location: str,
        current_cases: int,
        historical_data: List[int],
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        Predict outbreak for a specific location.
        
        Args:
            location: Campus location ID
            current_cases: Current number of cases
            historical_data: List of historical case counts
            days_ahead: Number of days to predict
            
        Returns:
            Prediction results
        """
        instance = {
            "location": location,
            "current_cases": current_cases,
            "historical_cases": historical_data,
            "days_ahead": days_ahead
        }
        
        predictions = self.predict([instance])
        
        if predictions:
            return {
                "location": location,
                "prediction": predictions[0],
                "generated_at": datetime.utcnow().isoformat()
            }
        
        return {"error": "Failed to generate prediction"}
    
    def batch_predict(
        self,
        locations: List[str],
        location_data: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Generate predictions for multiple locations.
        
        Args:
            locations: List of location IDs
            location_data: Dict mapping location to its data
            
        Returns:
            Dict mapping location to prediction
        """
        instances = []
        for loc in locations:
            data = location_data.get(loc, {})
            instances.append({
                "location": loc,
                "current_cases": data.get("current_cases", 0),
                "historical_cases": data.get("historical_cases", []),
                "days_ahead": 7
            })
        
        predictions = self.predict(instances)
        
        results = {}
        for i, loc in enumerate(locations):
            if i < len(predictions):
                results[loc] = predictions[i]
        
        return results
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a deployed model."""
        if not self.is_gcp:
            return {
                "name": model_name,
                "version": "v1.0-mock",
                "status": "local"
            }
        
        try:
            models = Model.list(
                filter=f'display_name="{model_name}"',
                order_by="create_time desc"
            )
            
            if models:
                model = models[0]
                return {
                    "name": model.display_name,
                    "resource_name": model.resource_name,
                    "create_time": str(model.create_time),
                    "version": model.version_id
                }
        except Exception as e:
            print(f"Error getting model info: {e}")
        
        return None


# Initialize Vertex AI service
vertex_ai = VertexAIService()
