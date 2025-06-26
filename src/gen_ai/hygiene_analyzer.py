"""
AI-powered backlog hygiene analyzer using Google Gemini REST API.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
import requests

from ..configs.config import Config
from .prompts.backlog_hygiene_prompts import BacklogHygieneRecommenderPrompt


class HygieneAnalyzer:
    """
    AI-powered analyzer for generating backlog hygiene insights and recommendations using Google Gemini REST API.
    """
    
    def __init__(self, config: Union[Config, str] = 'src/configs/config.json'):
        """
        Initialize the Hygiene Analyzer.
        
        Args:
            config (Union[Config, str]): Config instance or path to configuration file
        """
        if isinstance(config, Config):
            self.config = config
        else:
            self.config = Config(config)
        self.api_key = self._initialize_gemini()
        self.base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
        self.prompts = BacklogHygieneRecommenderPrompt()
    
    def _initialize_gemini(self) -> Optional[str]:
        """Initialize Gemini API key if available."""
        try:
            ai_config = self.config.get_analyzer_config('ai')
            api_key = ai_config.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                print("⚠️  No Gemini API key found. AI insights will be disabled.")
                print("   Add 'gemini_api_key' to config.json or set GEMINI_API_KEY environment variable.")
                print("   Get your free API key at: https://aistudio.google.com/app/apikey")
                return None
            
            # Test the connection with a simple request
            test_success = self._test_gemini_connection(api_key)
            if test_success:
                print("✅ Gemini AI initialized successfully")
                return api_key
            else:
                print("⚠️  Failed to connect to Gemini")
                return None
                
        except Exception as e:
            print(f"⚠️  Failed to initialize Gemini: {e}")
            return None
    
    def _test_gemini_connection(self, api_key: str) -> bool:
        """Test Gemini API connection."""
        try:
            # Use the base URL directly since self.base_url isn't set yet
            base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
            url = f"{base_url}?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": "Hello"}]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def generate_backlog_hygiene_insights(self, hygiene_data: Dict[str, Any]) -> str:
        """
        Generate AI-powered insights and recommendations for backlog hygiene.
        
        Args:
            hygiene_data (dict): Backlog hygiene analysis data
            
        Returns:
            str: AI-generated hygiene insights and recommendations
        """
        if not self.api_key:
            return self._generate_fallback_hygiene_insights(hygiene_data)
        
        try:
            prompt = self.prompts.create_hygiene_insights_prompt(hygiene_data)
            
            full_prompt = self.prompts.get_insights_system_context() + prompt
            
            response_text = self._call_gemini_api(full_prompt)
            
            if response_text:
                return response_text.strip()
            else:
                print("⚠️  Empty response from Gemini for hygiene insights")
                return self._generate_fallback_hygiene_insights(hygiene_data)
            
        except Exception as e:
            print(f"⚠️  AI hygiene insights generation failed: {e}")
            return self._generate_fallback_hygiene_insights(hygiene_data)
    
    def generate_ai_hygiene_recommendations(self, hygiene_data: Dict[str, Any]) -> str:
        """
        Generate AI-powered concise and actionable recommendations for backlog hygiene.
        
        Args:
            hygiene_data (dict): Hygiene analysis data
            
        Returns:
            str: AI-generated concise and actionable recommendations
        """
        if not self.api_key:
            return self._generate_fallback_hygiene_recommendations(hygiene_data)
        
        try:
            prompt = self.prompts.create_hygiene_recommendations_prompt(hygiene_data)
            
            # Add system context to the prompt
            full_prompt = self.prompts.get_recommendations_system_context() + prompt
            
            response_text = self._call_gemini_api(full_prompt)
            
            if response_text:
                return response_text.strip()
            else:
                print("⚠️  Empty response from Gemini")
                return self._generate_fallback_hygiene_recommendations(hygiene_data)
            
        except Exception as e:
            print(f"⚠️  AI hygiene recommendations generation failed: {e}")
            return self._generate_fallback_hygiene_recommendations(hygiene_data)
    
    def generate_issue_description_suggestions(self, issue_title: str, issue_type: str = "Story") -> str:
        """
        Generate AI suggestions for improving issue descriptions.
        
        Args:
            issue_title (str): The issue title
            issue_type (str): Type of issue (Story, Task, Bug, etc.)
            
        Returns:
            str: AI-generated description suggestions
        """
        if not self.api_key:
            return f"Consider adding: user story, acceptance criteria, and technical details for this {issue_type.lower()}."
        
        try:
            prompt = self.prompts.create_issue_description_prompt(issue_title, issue_type)
            
            response_text = self._call_gemini_api(prompt)
            
            if response_text:
                return response_text.strip()
            else:
                return f"Consider adding: user story, acceptance criteria, and technical details for this {issue_type.lower()}."
            
        except Exception as e:
            print(f"⚠️  AI description suggestions generation failed: {e}")
            return f"Consider adding: user story, acceptance criteria, and technical details for this {issue_type.lower()}."
    
    def analyze_issue_quality(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the quality of a list of issues and provide AI insights.
        
        Args:
            issues (list): List of issue dictionaries
            
        Returns:
            dict: Quality analysis results with AI insights
        """
        if not self.api_key:
            return self._generate_fallback_quality_analysis(issues)
        
        try:
            prompt = self.prompts.create_quality_analysis_prompt(issues)
            
            full_prompt = """You are a senior product manager reviewing issue quality. Analyze the provided issues and provide insights about their completeness, clarity, and actionability. Focus on common patterns and areas for improvement.

""" + prompt
            
            response_text = self._call_gemini_api(full_prompt)
            
            if response_text:
                return {
                    'ai_insights': response_text.strip(),
                    'total_issues_analyzed': len(issues),
                    'analysis_timestamp': '2024-01-01T00:00:00'  # Placeholder
                }
            else:
                return self._generate_fallback_quality_analysis(issues)
            
        except Exception as e:
            print(f"⚠️  AI quality analysis failed: {e}")
            return self._generate_fallback_quality_analysis(issues)
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Make API call to Gemini."""
        try:
            url = f"{self.base_url}?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 4096,
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']
                    if 'parts' in content and len(content['parts']) > 0:
                        return content['parts'][0]['text']
            
            print(f"⚠️  Unexpected response from Gemini: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"⚠️  API call failed: {e}")
            return None
    
    def _generate_fallback_hygiene_insights(self, hygiene_data: Dict[str, Any]) -> str:
        """Generate fallback hygiene insights when AI is not available."""
        total_issues = hygiene_data.get('total_issues', 0)
        hygiene_score = hygiene_data.get('hygiene_score', 0)
        completeness = hygiene_data.get('completeness', {})
        
        completeness_percentages = completeness.get('percentages', {})
        description_percentage = completeness_percentages.get('has_description_percentage', 0)
        epic_percentage = completeness_percentages.get('has_epic_percentage', 0)
        
        if hygiene_score >= 80:
            status = "excellent"
            recommendation = "Continue maintaining high standards."
        elif hygiene_score >= 60:
            status = "good"
            recommendation = "Focus on improving descriptions and epic assignments."
        else:
            status = "needs improvement"
            recommendation = "Prioritize adding descriptions and organizing issues into epics."
        
        return f"""The backlog shows {status} hygiene with a score of {hygiene_score}%. 
        
Key observations:
- {description_percentage:.1f}% of issues have descriptions
- {epic_percentage:.1f}% of issues are assigned to epics
- Total backlog size: {total_issues} issues

Recommendation: {recommendation}"""
    
    def _generate_fallback_quality_analysis(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback quality analysis when AI is not available."""
        return {
            'ai_insights': f"Analyzed {len(issues)} issues. Consider reviewing descriptions, epic assignments, and priority levels for better issue quality.",
            'total_issues_analyzed': len(issues),
            'analysis_timestamp': '2024-01-01T00:00:00'  # Placeholder
        }
    
    def _generate_fallback_hygiene_recommendations(self, hygiene_data: Dict[str, Any]) -> str:
        """Generate fallback hygiene recommendations when AI is not available."""
        total_issues = hygiene_data.get('total_issues', 0)
        hygiene_score = hygiene_data.get('hygiene_score', 0)
        
        if hygiene_score >= 70:
            summary = f"The backlog is in good health with {hygiene_score}% hygiene score."
            action1 = "Review and update any outdated issues"
            action2 = "Ensure new issues follow the established template"
        else:
            summary = f"The backlog needs attention with {hygiene_score}% hygiene score."
            action1 = "Add descriptions to issues missing them"
            action2 = "Organize issues into appropriate epics"
        
        return f"""{summary}

Action items:
1. {action1}
2. {action2}""" 