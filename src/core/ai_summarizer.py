"""
AI-powered sprint summary generator using Google Gemini REST API.
"""

import os
import json
from typing import Dict, List, Any, Optional
import requests

from .config import Config


class AISummarizer:
    """
    AI-powered summarizer for generating sprint achievement summaries using Google Gemini REST API.
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the AI summarizer.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config = Config(config_path)
        self.api_key = self._initialize_gemini()
        self.base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
    
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
                print("aamish")
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
            # Prepare the prompt with sprint data
            prompt = self._create_achievement_prompt(sprint_data)
            
            # Add system context to the prompt
            full_prompt = """You are a professional project manager analyzing sprint achievements. Provide concise, insightful summaries of what the development team accomplished.

""" + prompt
            
            response_text = self._call_gemini_api(full_prompt)
            
            if response_text:
                return response_text.strip()
            else:
                print("⚠️  Empty response from Gemini")
                return self._generate_fallback_summary(sprint_data)
            
        except Exception as e:
            print(f"⚠️  AI summary generation failed: {e}")
            return self._generate_fallback_summary(sprint_data)
    
    def generate_multi_sprint_summary(self, results: Dict[str, Any]) -> str:
        """
        Generate an AI summary for multiple sprints analysis.
        
        Args:
            results (dict): Multi-sprint analysis results
            
        Returns:
            str: AI-generated multi-sprint summary
        """
        if not self.api_key:
            return self._generate_fallback_multi_sprint_summary(results)
        
        try:
            prompt = self._create_multi_sprint_prompt(results)
            
            # Add system context to the prompt
            full_prompt = """You are a senior project manager analyzing multiple sprint performance. Provide strategic insights about team productivity, trends, and achievements.

""" + prompt
            
            response_text = self._call_gemini_api(full_prompt)
            
            if response_text:
                return response_text.strip()
            else:
                print("⚠️  Empty response from Gemini")
                return self._generate_fallback_multi_sprint_summary(results)
            
        except Exception as e:
            print(f"⚠️  AI multi-sprint summary generation failed: {e}")
            return self._generate_fallback_multi_sprint_summary(results)
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Call Gemini API with the given prompt."""
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
                    "maxOutputTokens": 8192,
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    content = data['candidates'][0].get('content', {})
                    parts = content.get('parts', [])
                    if parts and 'text' in parts[0]:
                        return parts[0]['text']
            else:
                print(f"⚠️  Gemini API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"⚠️  Error calling Gemini API: {e}")
            
        return None
    
    def _create_achievement_prompt(self, sprint_data: Dict[str, Any]) -> str:
        """Create a prompt for single sprint achievement summary."""
        sprint_name = sprint_data.get('sprint_name', 'Unknown Sprint')
        tasks = sprint_data.get('tasks', [])
        completion_rate = sprint_data.get('completion_rate', 0)
        
        # Categorize tasks
        completed_tasks = [t for t in tasks if t.get('completed_within_sprint', False)]
        late_tasks = [t for t in tasks if not t.get('completed_within_sprint', False) and t.get('current_status', '').upper() == 'DONE']
        incomplete_tasks = [t for t in tasks if t.get('current_status', '').upper() != 'DONE']
        
        prompt = f"""
Analyze this sprint and provide a professional summary of achievements:

Sprint: {sprint_name}
Completion Rate: {completion_rate:.1f}%
Total Tasks: {len(tasks)}

COMPLETED ON TIME ({len(completed_tasks)} tasks):
"""
        
        for task in completed_tasks[:10]:  # Limit to first 10 tasks
            prompt += f"- {task.get('key', 'N/A')}: {task.get('summary', 'No title')}\n"
        
        if late_tasks:
            prompt += f"\nCOMPLETED LATE ({len(late_tasks)} tasks):\n"
            for task in late_tasks[:5]:  # Limit to first 5 late tasks
                prompt += f"- {task.get('key', 'N/A')}: {task.get('summary', 'No title')}\n"
        
        if incomplete_tasks:
            prompt += f"\nINCOMPLETE ({len(incomplete_tasks)} tasks):\n"
            for task in incomplete_tasks[:5]:  # Limit to first 5 incomplete tasks
                prompt += f"- {task.get('key', 'N/A')}: {task.get('summary', 'No title')}\n"
        
        prompt += """

Please provide a concise 2-3 paragraph summary covering:
1. Key achievements and deliverables completed
2. Overall sprint performance assessment
3. Notable patterns or insights (if any)

Keep it professional and focus on value delivered to the business.
"""
        
        return prompt
    
    def _create_multi_sprint_prompt(self, results: Dict[str, Any]) -> str:
        """Create a prompt for multi-sprint summary."""
        sprint_results = results.get('sprint_results', [])
        avg_completion = results.get('average_completion_rate', 0)
        total_tasks = results.get('total_tasks', 0)
        total_completed = results.get('total_completed', 0)
        
        prompt = f"""
Analyze this multi-sprint performance and provide strategic insights:

Analysis Period: {results.get('analysis_type', 'Unknown')}
Total Sprints: {len(sprint_results)}
Overall Completion Rate: {avg_completion:.1f}%
Total Tasks Analyzed: {total_tasks}
Tasks Completed On Time: {total_completed}

SPRINT PERFORMANCE:
"""
        
        for sprint in sprint_results:
            prompt += f"- {sprint.get('sprint_name', 'Unknown')}: {sprint.get('completion_rate', 0):.1f}% ({sprint.get('completed_within_sprint', 0)}/{sprint.get('total_tasks', 0)} tasks)\n"
        
        # Add sample of key achievements
        prompt += "\nKEY DELIVERABLES ACROSS SPRINTS:\n"
        task_count = 0
        for sprint in sprint_results:
            if task_count >= 15:  # Limit total tasks shown
                break
            tasks = sprint.get('tasks', [])
            completed_tasks = [t for t in tasks if t.get('completed_within_sprint', False)]
            for task in completed_tasks[:5]:  # Max 5 per sprint
                if task_count >= 15:
                    break
                prompt += f"- {task.get('key', 'N/A')}: {task.get('summary', 'No title')}\n"
                task_count += 1
        
        prompt += """

Please provide a strategic 3-4 paragraph analysis covering:
1. Overall team performance and productivity trends
2. Key business value delivered across these sprints
3. Performance consistency and any notable patterns
4. High-level recommendations for improvement (if applicable)

Focus on executive-level insights and business impact.
"""
        
        return prompt
    
    def _generate_fallback_summary(self, sprint_data: Dict[str, Any]) -> str:
        """Generate a basic summary when AI is not available."""
        sprint_name = sprint_data.get('sprint_name', 'Unknown Sprint')
        tasks = sprint_data.get('tasks', [])
        completion_rate = sprint_data.get('completion_rate', 0)
        
        completed_tasks = [t for t in tasks if t.get('completed_within_sprint', False)]
        
        summary = f"**Sprint {sprint_name} Summary**\n\n"
        summary += f"The team achieved a {completion_rate:.1f}% completion rate, successfully delivering {len(completed_tasks)} out of {len(tasks)} planned tasks. "
        
        if completion_rate >= 80:
            summary += "This represents excellent sprint execution with strong team performance."
        elif completion_rate >= 70:
            summary += "This shows solid sprint performance with room for minor improvements."
        else:
            summary += "This indicates challenges in sprint execution that may require attention."
        
        if completed_tasks:
            summary += f"\n\nKey deliverables completed include tasks focused on {self._extract_common_themes(completed_tasks)}."
        
        return summary
    
    def _generate_fallback_multi_sprint_summary(self, results: Dict[str, Any]) -> str:
        """Generate a basic multi-sprint summary when AI is not available."""
        sprint_results = results.get('sprint_results', [])
        avg_completion = results.get('average_completion_rate', 0)
        
        summary = f"**Multi-Sprint Performance Analysis**\n\n"
        summary += f"Across {len(sprint_results)} sprints, the team maintained an average completion rate of {avg_completion:.1f}%. "
        
        if avg_completion >= 80:
            summary += "This demonstrates consistently high performance and reliable delivery."
        elif avg_completion >= 70:
            summary += "This shows generally good performance with opportunities for optimization."
        else:
            summary += "This suggests systematic challenges that require strategic attention."
        
        # Calculate consistency
        if sprint_results:
            rates = [s.get('completion_rate', 0) for s in sprint_results]
            variation = max(rates) - min(rates)
            if variation < 15:
                summary += " The team shows excellent consistency in delivery."
            elif variation < 30:
                summary += " Performance varies moderately between sprints."
            else:
                summary += " There's significant variation in sprint performance."
        
        return summary
    
    def _extract_common_themes(self, tasks: List[Dict[str, Any]]) -> str:
        """Extract common themes from task titles."""
        if not tasks:
            return "various development activities"
        
        # Simple keyword extraction
        keywords = []
        for task in tasks:
            title = task.get('summary', '').lower()
            if 'user' in title or 'login' in title or 'auth' in title:
                keywords.append('user authentication')
            elif 'api' in title or 'endpoint' in title:
                keywords.append('API development')
            elif 'ui' in title or 'interface' in title or 'frontend' in title:
                keywords.append('user interface')
            elif 'bug' in title or 'fix' in title:
                keywords.append('bug fixes')
            elif 'test' in title:
                keywords.append('testing')
            else:
                keywords.append('feature development')
        
        # Return most common themes
        unique_keywords = list(set(keywords))
        if len(unique_keywords) <= 2:
            return ' and '.join(unique_keywords)
        else:
            return ', '.join(unique_keywords[:2]) + ', and other improvements' 