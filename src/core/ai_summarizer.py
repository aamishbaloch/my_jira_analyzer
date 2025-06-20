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
            full_prompt = """Write a direct paragraph summary of sprint achievements. Use both ticket titles and descriptions to understand what was actually done. Bundle tasks by their epic context into main accomplishments. Pay attention to service names in ticket titles (e.g., "UserService", "PaymentService") and include them in your summary to show which systems were worked on. Use simple, clear language. Avoid corporate jargon, flowery language, and phrases like "robust," "comprehensive," "leverage," or "outcomes."

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
            full_prompt = """Write a straightforward summary of what the team built across multiple sprints. Group similar work together and include service names from ticket titles to show which systems were worked on. Use the epic context (in parentheses) to understand which tasks are related, but keep your original output format. For highlights, mention consistent delivery, successful features, or smooth processes. For lowlights, mention recurring delays, incomplete items, or blockers. Use plain English. Avoid business buzzwords, unnecessary adjectives, and corporate speak.

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
        
        prompt = f"""
Analyze this sprint and summarize what the team achieved:

Sprint: {sprint_name}
Completion Rate: {completion_rate:.1f}%

COMPLETED TASKS:
"""
        
        # Add task titles with descriptions and epic context for AI understanding
        for task in completed_tasks:
            task_summary = task.get('summary', 'No title')
            task_description = task.get('description', '')
            epic_summary = task.get('epic_summary', 'No Epic')
            
            task_line = f"- {task_summary}"
            if task_description and task_description.strip():
                # Limit description to first 100 characters for brevity
                desc_preview = task_description.strip()[:100]
                if len(task_description.strip()) > 100:
                    desc_preview += "..."
                task_line += f" - {desc_preview}"
            
            if epic_summary != 'No Epic':
                task_line += f" (part of: {epic_summary})"
            
            prompt += task_line + "\n"
        
        if late_tasks:
            prompt += f"\nCOMPLETED AFTER SPRINT:\n"
            for task in late_tasks:
                task_summary = task.get('summary', 'No title')
                task_description = task.get('description', '')
                epic_summary = task.get('epic_summary', 'No Epic')
                
                task_line = f"- {task_summary}"
                if task_description and task_description.strip():
                    # Limit description to first 100 characters for brevity
                    desc_preview = task_description.strip()[:100]
                    if len(task_description.strip()) > 100:
                        desc_preview += "..."
                    task_line += f" - {desc_preview}"
                
                if epic_summary != 'No Epic':
                    task_line += f" (part of: {epic_summary})"
                
                prompt += task_line + "\n"
        
        prompt += """

Write a single paragraph summary of what the team achieved this sprint. Use both the ticket titles and descriptions to understand what was actually accomplished. Group tasks by their epic context and describe the main achievements. Pay special attention to service names in ticket titles and include them to show which systems were worked on (e.g., "enhanced UserService with login validation and improved PaymentService with refund processing"). Use the epic information to bundle related work together. Be direct and focus only on what was accomplished.
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
        
        # Add sample of key task titles with epic context
        prompt += "\nSAMPLE COMPLETED TASKS:\n"
        task_count = 0
        for sprint in sprint_results:
            if task_count >= 10:  # Limit total tasks shown
                break
            tasks = sprint.get('tasks', [])
            completed_tasks = [t for t in tasks if t.get('completed_within_sprint', False)]
            for task in completed_tasks[:3]:  # Max 3 per sprint
                if task_count >= 10:
                    break
                task_summary = task.get('summary', 'No title')
                task_description = task.get('description', '')
                epic_summary = task.get('epic_summary', 'No Epic')
                
                task_line = f"- {task_summary}"
                if task_description and task_description.strip():
                    # Limit description to first 100 characters for brevity
                    desc_preview = task_description.strip()[:100]
                    if len(task_description.strip()) > 100:
                        desc_preview += "..."
                    task_line += f" - {desc_preview}"
                
                if epic_summary != 'No Epic':
                    task_line += f" (part of: {epic_summary})"
                
                prompt += task_line + "\n"
                task_count += 1
        
        prompt += """

Write 5 short sections:
1. **Built:** What was built across these sprints - group similar work and include service names from ticket titles
2. **Fixed:** What was fixed or improved
3. **Highlights:** What went well across these sprints
4. **Lowlights:** What challenges or issues occurred
5. **Patterns:** Any patterns you notice

Use the epic context in parentheses to understand which tasks belong together. Pay attention to service names in ticket titles to show which systems were worked on. Keep it simple and direct.
"""
        
        return prompt
    
    def _generate_fallback_summary(self, sprint_data: Dict[str, Any]) -> str:
        """Generate a basic summary when AI is not available."""
        sprint_name = sprint_data.get('sprint_name', 'Unknown Sprint')
        tasks = sprint_data.get('tasks', [])
        completion_rate = sprint_data.get('completion_rate', 0)
        
        completed_tasks = [t for t in tasks if t.get('completed_within_sprint', False)]
        late_tasks = [t for t in tasks if not t.get('completed_within_sprint', False) and t.get('current_status', '').upper() == 'DONE']
        incomplete_tasks = [t for t in tasks if t.get('current_status', '').upper() != 'DONE']
        
        summary = f"**Sprint {sprint_name} Achievement Summary**\n\n"
        
        if completed_tasks:
            epic_summary = self._extract_epic_themes(completed_tasks)
            summary += f"The team completed {len(completed_tasks)} tasks across {epic_summary}, achieving a {completion_rate:.1f}% completion rate."
            
            if late_tasks:
                summary += f" An additional {len(late_tasks)} tasks were completed after the sprint deadline."
            
            if incomplete_tasks:
                summary += f" {len(incomplete_tasks)} tasks remain incomplete."
        else:
            summary += f"The team achieved a {completion_rate:.1f}% completion rate with no tasks completed within the sprint timeline."
        
        return summary
    
    def _generate_fallback_multi_sprint_summary(self, results: Dict[str, Any]) -> str:
        """Generate a basic multi-sprint summary when AI is not available."""
        sprint_results = results.get('sprint_results', [])
        avg_completion = results.get('average_completion_rate', 0)
        total_tasks = results.get('total_tasks', 0)
        total_completed = results.get('total_completed', 0)
        
        summary = f"**Multi-Sprint Performance Metrics**\n\n"
        summary += f"Across {len(sprint_results)} sprints: average completion rate of {avg_completion:.1f}% ({total_completed}/{total_tasks} total tasks completed within sprint timelines). "
        
        # Performance against benchmark
        if avg_completion >= 80:
            summary += f"Team performance is {avg_completion - 80:.1f} percentage points above the 80% target benchmark."
        elif avg_completion >= 70:
            summary += f"Team performance is {80 - avg_completion:.1f} percentage points below the 80% target benchmark."
        else:
            summary += f"Team performance is {80 - avg_completion:.1f} percentage points below target, indicating systematic capacity or planning issues."
        
        # Calculate consistency with specific metrics
        if sprint_results:
            rates = [s.get('completion_rate', 0) for s in sprint_results]
            variation = max(rates) - min(rates)
            highest_rate = max(rates)
            lowest_rate = min(rates)
            
            summary += f"\n\nPerformance consistency: {variation:.1f}% variance (range: {lowest_rate:.1f}% to {highest_rate:.1f}%). "
            
            if variation < 15:
                summary += f"Variance under 15% indicates consistent delivery patterns."
            elif variation < 30:
                summary += f"Variance of {variation:.1f}% suggests moderate inconsistency in sprint execution."
            else:
                summary += f"Variance of {variation:.1f}% indicates significant inconsistency requiring process improvements."
        
        return summary
    
    def _extract_epic_themes(self, tasks: List[Dict[str, Any]]) -> str:
        """Extract themes from epic summaries."""
        if not tasks:
            return "various development activities"
        
        # Group by epic
        epic_counts = {}
        for task in tasks:
            epic_summary = task.get('epic_summary', 'No Epic')
            epic_counts[epic_summary] = epic_counts.get(epic_summary, 0) + 1
        
        # Sort by frequency
        sorted_epics = sorted(epic_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return epic names
        if len(sorted_epics) == 1:
            return sorted_epics[0][0]
        elif len(sorted_epics) == 2:
            return f"{sorted_epics[0][0]} and {sorted_epics[1][0]}"
        else:
            return f"{sorted_epics[0][0]}, {sorted_epics[1][0]}, and {len(sorted_epics) - 2} other epics"

    def _extract_common_themes(self, tasks: List[Dict[str, Any]]) -> str:
        """Extract common themes from task titles (fallback method)."""
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