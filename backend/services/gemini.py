"""
Gemini API integration for FEVER ORACLE
Natural language processing for symptom analysis and health recommendations
"""

import os
from typing import Dict, Any, List, Optional

IS_GCP = os.getenv("GOOGLE_CLOUD_PROJECT") is not None
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

class GeminiService:
    """Gemini API client for NLP tasks."""
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model_name = "gemini-pro"
        
        if self.api_key:
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
    
    def _generate(self, prompt: str) -> Optional[str]:
        """Generate text using Gemini."""
        if not self.model:
            return None
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    def analyze_symptoms(self, symptoms: List[str], severity: str) -> Dict[str, Any]:
        """
        Analyze reported symptoms and provide insights.
        
        Args:
            symptoms: List of symptom descriptions
            severity: Severity level (mild, moderate, severe)
            
        Returns:
            Analysis results with recommendations
        """
        if not self.model:
            return self._mock_symptom_analysis(symptoms, severity)
        
        prompt = f"""
        Analyze the following health symptoms reported on a college campus:
        
        Symptoms: {', '.join(symptoms)}
        Severity Level: {severity}
        
        Provide a brief JSON response with:
        1. "likely_conditions": List of 2-3 possible conditions
        2. "risk_assessment": One of "low", "moderate", "high"
        3. "recommendation": Brief health advice (1-2 sentences)
        4. "should_seek_care": Boolean indicating if medical attention is recommended
        
        Keep the response concise and appropriate for a campus health context.
        Return only valid JSON.
        """
        
        response = self._generate(prompt)
        
        if response:
            try:
                import json
                # Clean response and parse JSON
                cleaned = response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
            except:
                pass
        
        return self._mock_symptom_analysis(symptoms, severity)
    
    def _mock_symptom_analysis(self, symptoms: List[str], severity: str) -> Dict[str, Any]:
        """Mock symptom analysis for development."""
        return {
            "likely_conditions": ["Common cold", "Seasonal flu"],
            "risk_assessment": severity if severity in ["low", "moderate", "high"] else "moderate",
            "recommendation": "Rest, stay hydrated, and monitor symptoms. If symptoms worsen, visit the campus health center.",
            "should_seek_care": severity == "severe"
        }
    
    def generate_health_tip(self, symptoms: List[str]) -> str:
        """Generate a personalized health tip based on symptoms."""
        if not self.model:
            return self._get_default_health_tip()
        
        prompt = f"""
        A student reported these symptoms: {', '.join(symptoms)}
        
        Provide ONE brief, helpful health tip (max 2 sentences) appropriate for a college student.
        Be supportive and practical. Don't diagnose.
        """
        
        response = self._generate(prompt)
        return response if response else self._get_default_health_tip()
    
    def _get_default_health_tip(self) -> str:
        """Return a default health tip."""
        import random
        tips = [
            "Stay hydrated and get plenty of rest. Your body heals best when well-rested.",
            "Consider wearing a mask in crowded areas to protect yourself and others.",
            "Wash your hands frequently and avoid touching your face.",
            "Monitor your symptoms and visit the campus health center if they worsen.",
            "Eat nutritious foods and get enough sleep to support your immune system."
        ]
        return random.choice(tips)
    
    def generate_alert_message(
        self,
        location: str,
        severity: str,
        case_count: int,
        trend: str
    ) -> Dict[str, str]:
        """
        Generate an alert message for health officials.
        
        Args:
            location: Campus location name
            severity: Alert severity
            case_count: Number of cases
            trend: Trend direction
            
        Returns:
            Dict with title and message
        """
        if not self.model:
            return {
                "title": f"Health Alert: {location}",
                "message": f"Elevated symptom reports detected in {location}. {case_count} reports with {trend} trend. Monitor closely."
            }
        
        prompt = f"""
        Generate a brief health alert for campus administrators:
        
        Location: {location}
        Severity: {severity}
        Case Count: {case_count}
        Trend: {trend}
        
        Return JSON with:
        - "title": Brief alert title (max 8 words)
        - "message": Alert details (max 2 sentences)
        
        Be professional and actionable. Return only valid JSON.
        """
        
        response = self._generate(prompt)
        
        if response:
            try:
                import json
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("\n", 1)[0]
                return json.loads(cleaned.strip())
            except:
                pass
        
        return {
            "title": f"Health Alert: {location}",
            "message": f"Elevated symptom reports detected in {location}. {case_count} reports with {trend} trend."
        }
    
    def summarize_reports(self, reports: List[Dict]) -> str:
        """Generate a summary of recent symptom reports."""
        if not self.model or not reports:
            return "No significant patterns detected in recent reports."
        
        # Extract key info from reports
        symptoms_list = []
        locations = set()
        for report in reports[:20]:  # Limit to 20 reports
            symptoms_list.extend(report.get("symptoms", []))
            locations.add(report.get("location", "Unknown"))
        
        prompt = f"""
        Summarize these campus health reports briefly:
        
        Locations affected: {', '.join(locations)}
        Symptoms reported: {', '.join(set(symptoms_list))}
        Total reports: {len(reports)}
        
        Provide a 2-3 sentence summary for health officials.
        Focus on patterns and actionable insights.
        """
        
        response = self._generate(prompt)
        return response if response else "Unable to generate summary."


# Initialize Gemini service
gemini = GeminiService()
