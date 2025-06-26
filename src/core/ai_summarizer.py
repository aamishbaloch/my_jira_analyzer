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
            prompt = self._create_hygiene_insights_prompt(hygiene_data)
            
            full_prompt = """You are a senior product manager analyzing backlog health. Based on the hygiene metrics provided, write actionable insights and recommendations. Be specific about what needs attention and provide practical next steps. Focus on the most impactful improvements first. Use clear, professional language without jargon.

""" + prompt
            
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
            prompt = self._create_hygiene_recommendations_prompt(hygiene_data)
            
            # Add system context to the prompt
            full_prompt = """You are a technical project manager. Based on the backlog hygiene data, write one summary paragraph about the team's backlog health, then provide exactly 2 short-term action items the team can implement to improve their backlog management. Be concise and actionable.

""" + prompt
            
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
            prompt = f"""
Based on this {issue_type} title: "{issue_title}"

Suggest what should be included in the description to make this issue complete and actionable. Provide specific suggestions for:
1. User story or context
2. Acceptance criteria
3. Technical considerations (if applicable)

Keep suggestions concise and practical.
"""
            
            response_text = self._call_gemini_api(prompt)
            return response_text.strip() if response_text else "Add user story, acceptance criteria, and technical details."
            
        except Exception as e:
            print(f"⚠️  AI description suggestion failed: {e}")
            return "Add user story, acceptance criteria, and technical details."
    
    def analyze_issue_quality(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the quality of issue descriptions using AI.
        
        Args:
            issues (list): List of issues to analyze
            
        Returns:
            dict: Quality analysis results
        """
        if not self.api_key:
            return self._generate_fallback_quality_analysis(issues)
        
        try:
            # Analyze a sample of issues (max 10 for API efficiency)
            sample_issues = issues[:10] if len(issues) > 10 else issues
            
            prompt = self._create_quality_analysis_prompt(sample_issues)
            
            full_prompt = """Analyze these Jira issues for description quality. Rate each on clarity, completeness, and actionability. Identify common patterns of good and poor descriptions. Provide specific improvement suggestions.

""" + prompt
            
            response_text = self._call_gemini_api(full_prompt)
            
            if response_text:
                return {
                    'ai_analysis': response_text.strip(),
                    'analyzed_count': len(sample_issues),
                    'total_count': len(issues)
                }
            else:
                return self._generate_fallback_quality_analysis(issues)
            
        except Exception as e:
            print(f"⚠️  AI quality analysis failed: {e}")
            return self._generate_fallback_quality_analysis(issues)
    
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
    
    def _create_hygiene_insights_prompt(self, hygiene_data: Dict[str, Any]) -> str:
        """Create a prompt for backlog hygiene insights."""
        total_issues = hygiene_data.get('total_issues', 0)
        hygiene_score = hygiene_data.get('hygiene_score', 0)
        
        completeness = hygiene_data.get('completeness', {})
        age = hygiene_data.get('age_distribution', {})
        priority = hygiene_data.get('priority_distribution', {})
        epic = hygiene_data.get('epic_assignment', {})
        
        prompt = f"""
BACKLOG HYGIENE ANALYSIS:

Overall Score: {hygiene_score}% ({total_issues} total issues)

COMPLETENESS METRICS:
- Issues with descriptions: {completeness.get('percentages', {}).get('has_description_percentage', 0):.1f}%
- Issues with epics: {completeness.get('percentages', {}).get('has_epic_percentage', 0):.1f}%
- Issues with priorities: {completeness.get('percentages', {}).get('has_priority_percentage', 0):.1f}%
- Issues with story points: {completeness.get('percentages', {}).get('has_story_points_percentage', 0):.1f}%
- Fully complete issues: {completeness.get('percentages', {}).get('fully_complete_percentage', 0):.1f}%

AGE DISTRIBUTION:
- Average age: {age.get('average_age_days', 0)} days
- 0-7 days: {age.get('distribution', {}).get('0-7_days', 0)} issues
- 8-30 days: {age.get('distribution', {}).get('8-30_days', 0)} issues  
- 31-90 days: {age.get('distribution', {}).get('31-90_days', 0)} issues
- 91-180 days: {age.get('distribution', {}).get('91-180_days', 0)} issues
- 180+ days: {age.get('distribution', {}).get('180+_days', 0)} issues

EPIC ASSIGNMENT:
- Issues with epics: {epic.get('issues_with_epics', 0)} ({epic.get('epic_assignment_percentage', 0):.1f}%)
- Orphaned issues: {epic.get('orphaned_issues', 0)}
- Unique epics: {epic.get('unique_epics', 0)}

PRIORITY DISTRIBUTION:
- Issues without priority: {priority.get('issues_without_priority', 0)}

Based on this data, provide:
1. Key insights about backlog health
2. Top 3 priority actions to improve hygiene score
3. Specific recommendations for the most critical issues
4. Long-term suggestions for maintaining good backlog health

Be specific and actionable in your recommendations.
"""
        
        return prompt
    
    def _create_hygiene_recommendations_prompt(self, hygiene_data: Dict[str, Any]) -> str:
        """Create a prompt for generating hygiene recommendations."""
        total_issues = hygiene_data.get('total_issues', 0)
        hygiene_score = hygiene_data.get('hygiene_score', 0)
        
        completeness = hygiene_data.get('completeness', {})
        age = hygiene_data.get('age_distribution', {})
        priority = hygiene_data.get('priority_distribution', {})
        epic = hygiene_data.get('epic_assignment', {})
        
        # Extract key numbers
        missing_descriptions = completeness.get('counts', {}).get('missing_description', 0)
        missing_story_points = completeness.get('counts', {}).get('missing_story_points', 0)
        avg_age_days = age.get('average_age_days', 0)
        old_issues_180plus = age.get('distribution', {}).get('180+_days', 0)
        orphaned_issues = epic.get('orphaned_issues', 0)
        issues_without_priority = priority.get('issues_without_priority', 0)
        
        prompt = f"""
Analyze this backlog hygiene data and provide specific action items:

Total Issues: {total_issues}
Hygiene Score: {hygiene_score}%

COMPLETENESS DATA:
- Issues missing descriptions: {missing_descriptions}
- Issues missing story points: {missing_story_points}
- Issues with descriptions: {completeness.get('counts', {}).get('has_description', 0)} ({completeness.get('percentages', {}).get('has_description_percentage', 0):.1f}%)
- Issues with story points: {completeness.get('counts', {}).get('has_story_points', 0)} ({completeness.get('percentages', {}).get('has_story_points_percentage', 0):.1f}%)

AGE DATA:
- Average age: {avg_age_days} days
- Issues 180+ days old: {old_issues_180plus}
- Issues 91-180 days old: {age.get('distribution', {}).get('91-180_days', 0)}

EPIC DATA:
- Orphaned issues (no epic): {orphaned_issues}
- Epic assignment rate: {epic.get('epic_assignment_percentage', 0):.1f}%

PRIORITY DATA:
- Issues without priority: {issues_without_priority}

Write one paragraph summarizing the backlog health using these specific numbers. Then add "Action items:" followed by exactly 2 short-term improvements the team should implement. Focus on team practices and processes, not individual ticket fixes.
"""
        
        return prompt
    
    def _create_quality_analysis_prompt(self, issues: List[Dict[str, Any]]) -> str:
        """Create a prompt for issue quality analysis."""
        prompt = "ISSUE QUALITY ANALYSIS:\n\n"
        
        for i, issue in enumerate(issues, 1):
            title = issue.get('summary', 'No title')
            description = issue.get('description', 'No description')
            issue_type = issue.get('issue_type', 'Unknown')
            
            prompt += f"ISSUE {i} ({issue_type}):\n"
            prompt += f"Title: {title}\n"
            prompt += f"Description: {description[:200]}{'...' if len(description) > 200 else ''}\n\n"
        
        prompt += """
Analyze these issues for:
1. Description quality (clarity, completeness, actionability)
2. Common patterns in good vs poor descriptions  
3. Specific suggestions for improvement
4. Overall assessment of description standards

Provide actionable feedback for improving issue quality.
"""
        
        return prompt
    
    def _generate_fallback_hygiene_insights(self, hygiene_data: Dict[str, Any]) -> str:
        """Generate basic hygiene insights when AI is not available."""
        hygiene_score = hygiene_data.get('hygiene_score', 0)
        total_issues = hygiene_data.get('total_issues', 0)
        
        completeness = hygiene_data.get('completeness', {}).get('percentages', {})
        age = hygiene_data.get('age_distribution', {})
        epic = hygiene_data.get('epic_assignment', {})
        
        insights = f"**Backlog Health Summary**\n\n"
        insights += f"Your backlog hygiene score is {hygiene_score}% across {total_issues} issues. "
        
        if hygiene_score >= 80:
            insights += "This indicates excellent backlog health with good practices in place."
        elif hygiene_score >= 60:
            insights += "This indicates decent backlog health with room for improvement."
        else:
            insights += "This indicates significant hygiene issues requiring attention."
        
        # Key recommendations based on metrics
        recommendations = []
        
        if completeness.get('has_description_percentage', 0) < 80:
            recommendations.append("Improve issue descriptions for better clarity")
        
        if epic.get('epic_assignment_percentage', 0) < 70:
            recommendations.append(f"Assign {epic.get('orphaned_issues', 0)} orphaned issues to epics")
        
        if age.get('average_age_days', 0) > 90:
            recommendations.append("Review and clean up old issues to reduce backlog staleness")
        
        if recommendations:
            insights += f"\n\n**Priority Actions:**\n"
            for i, rec in enumerate(recommendations[:3], 1):
                insights += f"{i}. {rec}\n"
        
        return insights
    
    def _generate_fallback_quality_analysis(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic quality analysis when AI is not available."""
        total_issues = len(issues)
        issues_with_descriptions = sum(1 for issue in issues if issue.get('description', '').strip())
        
        quality_percentage = (issues_with_descriptions / total_issues * 100) if total_issues > 0 else 0
        
        analysis = f"**Issue Quality Analysis**\n\n"
        analysis += f"Analyzed {total_issues} issues: {issues_with_descriptions} ({quality_percentage:.1f}%) have descriptions. "
        
        if quality_percentage >= 80:
            analysis += "Description coverage is good."
        elif quality_percentage >= 60:
            analysis += "Description coverage needs improvement."
        else:
            analysis += "Description coverage is poor and requires immediate attention."
        
        return {
            'ai_analysis': analysis,
            'analyzed_count': total_issues,
            'total_count': total_issues
        }
    
    def _generate_fallback_hygiene_recommendations(self, hygiene_data: Dict[str, Any]) -> str:
        """Generate simple fallback hygiene recommendations when AI is not available."""
        total_issues = hygiene_data.get('total_issues', 0)
        hygiene_score = hygiene_data.get('hygiene_score', 0)
        
        completeness = hygiene_data.get('completeness', {})
        age = hygiene_data.get('age_distribution', {})
        epic = hygiene_data.get('epic_assignment', {})
        
        missing_story_points = completeness.get('counts', {}).get('missing_story_points', 0)
        avg_age_days = age.get('average_age_days', 0)
        orphaned_issues = epic.get('orphaned_issues', 0)
        
        # Simple summary paragraph
        summary = f"The backlog contains {total_issues} issues with a {hygiene_score}% hygiene score. "
        
        if hygiene_score >= 80:
            summary += "The backlog is well-maintained with good completeness and organization."
        elif hygiene_score >= 60:
            summary += "The backlog shows moderate hygiene with some areas needing attention."
        else:
            summary += f"The backlog needs improvement with {missing_story_points} issues missing story points, {orphaned_issues} orphaned issues, and an average age of {avg_age_days} days."
        
        # Two action items based on biggest issues
        action1 = "Schedule weekly 15-minute backlog grooming sessions"
        action2 = "Create Definition of Ready checklist for new tickets"
        
        if missing_story_points > 50:
            action1 = "Make story point estimation mandatory before sprint planning"
        if orphaned_issues > 20:
            action2 = "Assign all new tickets to epics during creation"
        if avg_age_days > 120:
            action1 = "Implement monthly backlog cleanup sessions"
        
        return f"{summary} Action items: 1) {action1}, 2) {action2}." 