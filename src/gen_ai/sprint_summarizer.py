"""
AI-powered sprint summary generator using Google Gemini REST API.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
import requests

from ..configs.config import Config
from .prompts.sprint_summarizer_prompts import SprintSummarizerPrompts


class SprintSummarizer:
    """
    AI-powered summarizer for generating sprint achievement summaries using Google Gemini REST API.
    """
    
    def __init__(self, config: Union[Config, str] = 'src/configs/config.json'):
        """
        Initialize the Sprint Summarizer.
        
        Args:
            config (Union[Config, str]): Config instance or path to configuration file
        """
        if isinstance(config, Config):
            self.config = config
        else:
            self.config = Config(config)
        self.api_key = self._initialize_gemini()
        self.base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
        self.prompts = SprintSummarizerPrompts()
    
    def _initialize_gemini(self) -> Optional[str]:
        """Initialize Gemini API key if available."""
        try:
            ai_config = self.config.get_analyzer_config('ai')
            api_key = ai_config.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                print("⚠️  No Gemini API key found. AI summaries will be disabled.")
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
    
    def generate_sprint_achievement_summary(self, sprint_data: Dict[str, Any]) -> str:
        """
        Generate an AI-powered summary of sprint achievements.
        
        Args:
            sprint_data (dict): Sprint analysis data
            
        Returns:
            str: AI-generated achievement summary
        """
        if not self.api_key:
            return self._generate_fallback_summary(sprint_data)
        
        try:
            # Prepare task summaries and themes
            tasks = sprint_data.get('tasks', [])
            completed_tasks_data = [task for task in tasks if task.get('completed_within_sprint', False)]
            
            task_summaries = []
            for task in completed_tasks_data[:10]:  # Limit to first 10
                summary = task.get('summary', 'Unknown')
                key = task.get('key', 'N/A')
                epic_summary = task.get('epic_summary', 'No Epic')
                epic_description = task.get('epic_description', '')
                
                # Create a more detailed task summary with epic context
                task_info = f"{key}: {summary}"
                if epic_summary and epic_summary != 'No Epic':
                    task_info += f" (Epic: {epic_summary}"
                    if epic_description and epic_description != 'No description':
                        # Truncate epic description to avoid too long summaries
                        short_desc = epic_description[:100] + '...' if len(epic_description) > 100 else epic_description
                        task_info += f" - {short_desc}"
                    task_info += ")"
                
                task_summaries.append(task_info)
            
            common_themes = self._extract_common_themes(completed_tasks_data)
            
            # Create prompt using the new prompt system
            prompt = self.prompts.create_achievement_prompt(sprint_data, task_summaries, common_themes)
            
            # Debug: Print prompt length
            print(f"🔍 Prompt length: {len(prompt)} characters")
            
            # Add system context to the prompt
            full_prompt = self.prompts.get_system_context() + prompt
            
            print(f"🔍 Full prompt length: {len(full_prompt)} characters")
            
            response_text = self._call_gemini_api(full_prompt)
            
            if response_text:
                print(f"🔍 AI Response: '{response_text}'")
                return response_text.strip()
            else:
                print("⚠️  Empty response from Gemini")
                return self._generate_fallback_summary(sprint_data)
            
        except Exception as e:
            print(f"⚠️  AI summary generation failed: {e}")
            return self._generate_fallback_summary(sprint_data)
    
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
                
                # Debug: Print the response structure
                print(f"🔍 Gemini response keys: {list(result.keys())}")
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']
                    print(f"🔍 Content keys: {list(content.keys())}")
                    
                    if 'parts' in content and len(content['parts']) > 0:
                        text = content['parts'][0]['text']
                        print(f"🔍 Extracted text length: {len(text)}")
                        return text
                    else:
                        print(f"⚠️  No parts found in content: {content}")
                else:
                    print(f"⚠️  No candidates found in response: {result}")
                    
                # Check for error information
                if 'error' in result:
                    print(f"⚠️  Gemini API error: {result['error']}")
                if 'promptFeedback' in result:
                    print(f"⚠️  Prompt feedback: {result['promptFeedback']}")
                    
            else:
                print(f"⚠️  Gemini API returned status code: {response.status_code}")
                print(f"⚠️  Response text: {response.text}")
            
            return None
            
        except Exception as e:
            print(f"⚠️  API call failed: {e}")
            return None
    
    def _generate_fallback_summary(self, sprint_data: Dict[str, Any]) -> str:
        """Generate fallback summary when AI is not available."""
        sprint_name = sprint_data.get('sprint_name', 'Unknown Sprint')
        completion_rate = sprint_data.get('completion_rate', 0)
        total_tasks = sprint_data.get('total_tasks', 0)
        completed_tasks = sprint_data.get('completed_within_sprint', 0)
        
        tasks = sprint_data.get('tasks', [])
        completed_tasks_data = [task for task in tasks if task.get('completed_within_sprint', False)]
        
        if not completed_tasks_data:
            return f"In {sprint_name}, no tasks were completed within the sprint timeframe. The team achieved a {completion_rate:.1f}% completion rate with {completed_tasks} out of {total_tasks} tasks completed."
        
        # Extract common themes from completed tasks
        themes = self._extract_common_themes(completed_tasks_data)
        
        return f"In {sprint_name}, the team completed {completed_tasks} out of {total_tasks} tasks, achieving a {completion_rate:.1f}% completion rate. Key areas of focus included: {themes}."
    
    def _extract_epic_themes(self, tasks: List[Dict[str, Any]]) -> str:
        """Extract common epic themes from tasks."""
        epics = {}
        for task in tasks:
            epic = task.get('epic_name', 'No Epic')
            if epic not in epics:
                epics[epic] = 0
            epics[epic] += 1
        
        if not epics:
            return "No epic assignments found"
        
        # Sort by count and take top 3
        sorted_epics = sorted(epics.items(), key=lambda x: x[1], reverse=True)[:3]
        return ", ".join([f"{epic} ({count} tasks)" for epic, count in sorted_epics])
    
    def _extract_common_themes(self, tasks: List[Dict[str, Any]]) -> str:
        """Extract common themes from task summaries."""
        if not tasks:
            return "No tasks to analyze"
        
        # Extract keywords from task summaries
        keywords = []
        for task in tasks:
            summary = task.get('summary', '').lower()
            # Add common technical terms
            if any(term in summary for term in ['api', 'service', 'database', 'ui', 'frontend', 'backend']):
                if 'api' in summary:
                    keywords.append('API')
                if 'service' in summary:
                    keywords.append('Service')
                if 'database' in summary:
                    keywords.append('Database')
                if 'ui' in summary or 'frontend' in summary:
                    keywords.append('UI/Frontend')
                if 'backend' in summary:
                    keywords.append('Backend')
        
        if not keywords:
            return "General development tasks"
        
        # Count and return most common themes
        from collections import Counter
        keyword_counts = Counter(keywords)
        top_keywords = [keyword for keyword, count in keyword_counts.most_common(3)]
        return ", ".join(top_keywords) 