"""
Confluence publisher for creating and updating pages with Jira analysis data.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from atlassian import Confluence

from ..configs.config import Config
from ..utils.utils import get_month_name, format_duration
from ..gen_ai.ai_summarizer import AISummarizer
from ..analyzers.sprint_analyzer import SprintAnalyzer
from ..analyzers.backlog_hygiene_analyzer import BacklogHygieneAnalyzer


class ConfluencePublisher:
    """
    Publisher for creating and updating Confluence pages with Jira analysis data.
    """
    
    def __init__(self, config_path: str = 'src/configs/config.json'):
        """
        Initialize the Confluence publisher.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config = Config(config_path)
        self.confluence = self._connect()
        self.ai_summarizer = AISummarizer(self.config)
        self.sprint_analyzer = SprintAnalyzer(self.config)
        self.backlog_analyzer = BacklogHygieneAnalyzer(self.config, self.ai_summarizer)
        
    def _connect(self) -> Confluence:
        """Connect to Confluence using configuration credentials."""
        try:
            confluence_config = self.config.get_analyzer_config('confluence')
            
            # Validate required config
            required_keys = ['url', 'username', 'api_token']
            missing_keys = [key for key in required_keys if key not in confluence_config]
            if missing_keys:
                raise ValueError(f"Missing Confluence configuration keys: {missing_keys}")
            
            return Confluence(
                url=confluence_config['url'],
                username=confluence_config['username'],
                password=confluence_config['api_token']
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Confluence: {str(e)}")
    
    def publish_sprint_analysis(self, analysis_results: Dict[str, Any], 
                              space_key: str, page_title: str,
                              parent_page_title: Optional[str] = None) -> Dict[str, str]:
        """
        Publish sprint analysis results to a Confluence page.
        
        Args:
            analysis_results (dict): Results from sprint analysis
            space_key (str): Confluence space key
            page_title (str): Title for the page
            parent_page_title (str, optional): Parent page title
            
        Returns:
            dict: Information about the created/updated page
        """
        try:
            # Generate HTML content
            content = self._generate_sprint_report_html(analysis_results)
            
            # Get parent page ID if specified
            parent_id = None
            if parent_page_title:
                parent_id = self._get_page_id(space_key, parent_page_title)
            
            # Check if page already exists
            existing_page = self._get_page_id(space_key, page_title)
            
            if existing_page:
                # Update existing page
                page = self.confluence.update_page(
                    page_id=existing_page,
                    title=page_title,
                    body=content
                )
                action = "updated"
            else:
                # Create new page
                page = self.confluence.create_page(
                    space=space_key,
                    title=page_title,
                    body=content,
                    parent_id=parent_id
                )
                action = "created"
            
            base_url = self.config.get_analyzer_config('confluence').get('url', '')
            page_url = f"{base_url}/pages/viewpage.action?pageId={page['id']}"
            
            return {
                'action': action,
                'page_id': page['id'],
                'page_url': page_url,
                'title': page_title,
                'space': space_key
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to publish to Confluence: {str(e)}")
    
    def publish_backlog_hygiene_analysis(self, space_key: str, page_title: str,
                                       parent_page_title: Optional[str] = None) -> Dict[str, str]:
        """
        Publish backlog hygiene analysis results to a Confluence page.
        
        Args:
            space_key (str): Confluence space key
            page_title (str): Title for the page
            parent_page_title (str, optional): Parent page title
            
        Returns:
            dict: Information about the created/updated page
        """
        try:
            # Get backlog hygiene analysis
            analysis_results = self.backlog_analyzer.analyze_full_backlog_hygiene()
            
            # Generate HTML content
            content = self._generate_backlog_hygiene_html(analysis_results)
            
            # Get parent page ID if specified
            parent_id = None
            if parent_page_title:
                parent_id = self._get_page_id(space_key, parent_page_title)
            
            # Check if page already exists
            existing_page = self._get_page_id(space_key, page_title)
            
            if existing_page:
                # Update existing page
                page = self.confluence.update_page(
                    page_id=existing_page,
                    title=page_title,
                    body=content
                )
                action = "updated"
            else:
                # Create new page
                page = self.confluence.create_page(
                    space=space_key,
                    title=page_title,
                    body=content,
                    parent_id=parent_id
                )
                action = "created"
            
            base_url = self.config.get_analyzer_config('confluence').get('url', '')
            page_url = f"{base_url}/pages/viewpage.action?pageId={page['id']}"
            
            return {
                'action': action,
                'page_id': page['id'],
                'page_url': page_url,
                'title': page_title,
                'space': space_key,
                'analysis_results': analysis_results
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to publish backlog hygiene to Confluence: {str(e)}")
    
    def publish_ai_insights_analysis(self, space_key: str, page_title: str,
                                   parent_page_title: Optional[str] = None) -> Dict[str, str]:
        """
        Publish AI-powered insights analysis to a Confluence page.
        
        Args:
            space_key (str): Confluence space key
            page_title (str): Title for the page
            parent_page_title (str, optional): Parent page title
            
        Returns:
            dict: Information about the created/updated page
        """
        try:
            # Get AI insights from backlog analyzer
            ai_insights_results = self.backlog_analyzer.get_ai_insights()
            
            # Generate HTML content focused on AI insights
            content = self._generate_ai_insights_html(ai_insights_results)
            
            # Get parent page ID if specified
            parent_id = None
            if parent_page_title:
                parent_id = self._get_page_id(space_key, parent_page_title)
            
            # Check if page already exists
            existing_page = self._get_page_id(space_key, page_title)
            
            if existing_page:
                # Update existing page
                page = self.confluence.update_page(
                    page_id=existing_page,
                    title=page_title,
                    body=content
                )
                action = "updated"
            else:
                # Create new page
                page = self.confluence.create_page(
                    space=space_key,
                    title=page_title,
                    body=content,
                    parent_id=parent_id
                )
                action = "created"
            
            base_url = self.config.get_analyzer_config('confluence').get('url', '')
            page_url = f"{base_url}/pages/viewpage.action?pageId={page['id']}"
            
            return {
                'action': action,
                'page_id': page['id'],
                'page_url': page_url,
                'title': page_title,
                'space': space_key
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to publish AI insights to Confluence: {str(e)}")
    
    def _get_page_id(self, space_key: str, page_title: str) -> Optional[str]:
        """Get page ID by space and title."""
        try:
            page = self.confluence.get_page_by_title(space_key, page_title)
            return page['id'] if page else None
        except:
            return None
    
    def _generate_sprint_report_html(self, results: Dict[str, Any]) -> str:
        """Generate HTML content for single sprint analysis report."""
        # Header with summary
        html = f"""
        <h1>🏃 Sprint Analysis Report</h1>
        
        {self._generate_summary_section(results)}
        {self._generate_ai_achievements_section(results)}
        {self._generate_average_completion_context(results)}
        {self._generate_sprint_details_table(results)}
        """
        
        return html
    
    def _generate_summary_section(self, results: Dict[str, Any]) -> str:
        """Generate summary statistics section for single sprint."""
        # Handle sprint not found
        if not results.get('found', False):
            return f"""
            <h2>❌ Sprint Not Found</h2>
            <p><strong>Searched for:</strong> {results.get('sprint_name', 'Unknown')}</p>
            <p><strong>Error:</strong> {results.get('error', 'Sprint not found')}</p>
            """
        
        # Sprint found - show detailed information
        start_date = results.get('start_date')
        end_date = results.get('end_date')
        
        # Format dates if they exist
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            except:
                start_date = start_date
        
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            except:
                end_date = end_date
        
        return f"""
        <h2>📊 Sprint Summary</h2>
        <p><strong>Sprint:</strong> {results.get('sprint_name', 'Unknown')}</p>
        <p><strong>Sprint State:</strong> {results.get('sprint_state', 'Unknown')}</p>
        <p><strong>Start Date:</strong> {start_date or 'N/A'}</p>
        <p><strong>End Date:</strong> {end_date or 'N/A'}</p>
        
        <table class="wrapped">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td><strong>Total Tasks</strong></td>
                <td>{results.get('total_tasks', 0)}</td>
            </tr>
            <tr>
                <td><strong>Completed Within Sprint</strong></td>
                <td>{results.get('completed_within_sprint', 0)}</td>
            </tr>
            <tr>
                <td><strong>Completion Rate</strong></td>
                <td>{results.get('completion_rate', 0):.1f}%</td>
            </tr>
        </table>
        """
    
    def _generate_average_completion_context(self, results: Dict[str, Any]) -> str:
        """Generate average completion context section for single sprint."""
        if not results.get('found', False):
            return ""
        
        try:
            # Get average completion rate of last 4 sprints
            avg_results = self.sprint_analyzer.get_average_completion_rate_last_4_sprints()
            
            if 'error' in avg_results:
                return f"""
                <h2>📈 Team Performance Context</h2>
                <p><em>Unable to calculate team average: {avg_results['error']}</em></p>
                """
            
            current_sprint_rate = results.get('completion_rate', 0)
            team_average = avg_results.get('average_completion_rate', 0)
            
            # Determine performance comparison
            if current_sprint_rate > team_average:
                performance_indicator = "🟢 Above Average"
                comparison_text = f"This sprint performed {current_sprint_rate - team_average:.1f}% better than the team average."
            elif current_sprint_rate < team_average:
                performance_indicator = "🔴 Below Average"
                comparison_text = f"This sprint performed {team_average - current_sprint_rate:.1f}% below the team average."
            else:
                performance_indicator = "🟡 At Average"
                comparison_text = "This sprint performed at the team average."
            
            html = f"""
            <h2>📈 Team Performance Context</h2>
            <table class="wrapped">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td><strong>Current Sprint Rate</strong></td>
                    <td>{current_sprint_rate:.1f}%</td>
                </tr>
                <tr>
                    <td><strong>Team Average (Last 4 Sprints)</strong></td>
                    <td>{team_average}%</td>
                </tr>
                <tr>
                    <td><strong>Performance</strong></td>
                    <td>{performance_indicator}</td>
                </tr>
            </table>
            <p><strong>Analysis:</strong> {comparison_text}</p>
            """
            
            return html
            
        except Exception as e:
            return f"""
            <h2>📈 Team Performance Context</h2>
            <p><em>Unable to load team performance data: {str(e)}</em></p>
            """
    
    def _get_jira_ticket_link(self, ticket_key: str) -> str:
        """
        Generate a clickable link to a Jira ticket.
        
        Args:
            ticket_key (str): The Jira ticket key (e.g., 'PROJ-123')
            
        Returns:
            str: HTML link to the Jira ticket
        """
        if not ticket_key or ticket_key == 'N/A':
            return ticket_key
        
        try:
            jira_base_url = self.config.jira_url.rstrip('/')
            ticket_url = f"{jira_base_url}/browse/{ticket_key}"
            return f'<a href="{ticket_url}" target="_blank"><strong>{ticket_key}</strong></a>'
        except Exception:
            # Fallback to just the ticket key if URL generation fails
            return f"<strong>{ticket_key}</strong>"
    
    def _generate_sprint_details_table(self, results: Dict[str, Any]) -> str:
        """Generate task details table for single sprint."""
        if not results.get('found', False):
            return ""  # Error already shown in summary section
        
        # Show task details for single sprint
        tasks = results.get('tasks', [])
        if not tasks:
            return "<h2>📋 Task Details</h2><p>No tasks found in this sprint.</p>"
        
        html = """
        <h2>📋 Task Details</h2>
        <table class="wrapped">
            <tr>
                <th>Task Key</th>
                <th>Summary</th>
                <th>Status</th>
                <th>Completed in Sprint</th>
                <th>Done Date</th>
            </tr>
        """
        
        for task in tasks:
            completion_status = '✅' if task.get('completed_within_sprint', False) else '❌'
            done_date = task.get('completion_date', 'Not completed')
            task_key = task.get('key', 'N/A')
            
            # Generate clickable link for the ticket
            ticket_link = self._get_jira_ticket_link(task_key)
            
            html += f"""
            <tr>
                <td>{ticket_link}</td>
                <td>{task.get('summary', 'N/A')[:60]}{'...' if len(task.get('summary', '')) > 60 else ''}</td>
                <td>{task.get('current_status', 'N/A')}</td>
                <td>{completion_status}</td>
                <td>{done_date}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _generate_ai_achievements_section(self, results: Dict[str, Any]) -> str:
        """Generate AI-powered achievements summary section for single sprint."""
        if not results.get('found', False):
            return ""
        
        html = "<h2>🤖 AI Sprint Achievement Summary</h2>"
        
        try:
            # Generate AI summary for single sprint
            ai_summary = self.ai_summarizer.generate_sprint_achievement_summary(results)
            html += f"<div style='background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0;'>"
            html += f"<p>{ai_summary.replace(chr(10), '</p><p>')}</p>"
            html += "</div>"
        except Exception as e:
            html += f"<p><em>AI summary generation failed: {str(e)}</em></p>"
        
        return html
    
    def _generate_task_summary_section(self, results: Dict[str, Any]) -> str:
        """Generate task summary section showing what was accomplished in the sprint."""
        if not results.get('found', False):
            return ""
        
        tasks = results.get('tasks', [])
        
        if not tasks:
            return "<h2>📋 Task Summary</h2><p>No tasks found in this sprint.</p>"
        
        html = "<h2>📋 Task Summary</h2>"
        
        # Group tasks by completion status
        completed_tasks = [task for task in tasks if task.get('completed_within_sprint', False)]
        late_tasks = [task for task in tasks if not task.get('completed_within_sprint', False) and task.get('current_status', '').upper() == 'DONE']
        incomplete_tasks = [task for task in tasks if task.get('current_status', '').upper() != 'DONE']
        
        # Completed within sprint
        if completed_tasks:
            html += """
            <h3>✅ Completed Within Sprint</h3>
            <ul>
            """
            for task in completed_tasks:
                task_key = task.get('key', 'Unknown')
                task_title = task.get('summary', 'No title')
                ticket_link = self._get_jira_ticket_link(task_key)
                html += f"<li>{ticket_link}: {task_title}</li>"
            html += "</ul>"
        
        # Completed late
        if late_tasks:
            html += """
            <h3>⏰ Completed After Sprint</h3>
            <ul>
            """
            for task in late_tasks:
                task_key = task.get('key', 'Unknown')
                task_title = task.get('summary', 'No title')
                completion_date = task.get('completion_date', 'Unknown date')
                ticket_link = self._get_jira_ticket_link(task_key)
                html += f"<li>{ticket_link}: {task_title} <em>(completed: {completion_date})</em></li>"
            html += "</ul>"
        
        # Still incomplete
        if incomplete_tasks:
            html += """
            <h3>❌ Not Completed</h3>
            <ul>
            """
            for task in incomplete_tasks:
                task_key = task.get('key', 'Unknown')
                task_title = task.get('summary', 'No title')
                current_status = task.get('current_status', 'Unknown')
                ticket_link = self._get_jira_ticket_link(task_key)
                html += f"<li>{ticket_link}: {task_title} <em>(status: {current_status})</em></li>"
            html += "</ul>"
        
        return html
    
    def _generate_backlog_hygiene_html(self, results: Dict[str, Any]) -> str:
        """Generate HTML content for backlog hygiene analysis report."""
        html = f"""
        <h1>🧹 Backlog Hygiene Report</h1>
        
        {self._generate_hygiene_summary_section(results)}
        {self._generate_hygiene_completeness_section(results)}
        {self._generate_hygiene_age_section(results)}
        {self._generate_hygiene_priority_epic_section(results)}
        {self._generate_hygiene_ai_recommendations_section(results)}
        {self._generate_hygiene_recommendations_section(results)}
        """
        
        return html
    
    def _generate_hygiene_summary_section(self, results: Dict[str, Any]) -> str:
        """Generate hygiene summary section."""
        total_issues = results.get('total_issues', 0)
        hygiene_score = results.get('hygiene_score', 0)
        
        # Color coding for hygiene score
        if hygiene_score >= 80:
            score_emoji = "🟢"
            status = "Excellent"
            score_color = "#28a745"
        elif hygiene_score >= 60:
            score_emoji = "🟡"
            status = "Good"
            score_color = "#ffc107"
        else:
            score_emoji = "🔴"
            status = "Needs Improvement"
            score_color = "#dc3545"
        
        return f"""
        <h2>📊 Overall Hygiene Summary</h2>
        <table class="wrapped">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td><strong>Total Backlog Issues</strong></td>
                <td>{total_issues}</td>
            </tr>
            <tr>
                <td><strong>Hygiene Score</strong></td>
                <td><span style="color: {score_color}; font-weight: bold;">{hygiene_score}%</span></td>
            </tr>
            <tr>
                <td><strong>Status</strong></td>
                <td>{score_emoji} {status}</td>
            </tr>
        </table>
        """
    
    def _generate_hygiene_completeness_section(self, results: Dict[str, Any]) -> str:
        """Generate completeness analysis section."""
        completeness = results.get('completeness', {})
        counts = completeness.get('counts', {})
        percentages = completeness.get('percentages', {})
        
        return f"""
        <h2>📝 Completeness Analysis</h2>
        <table class="wrapped">
            <tr>
                <th>Field</th>
                <th>Issues with Field</th>
                <th>Percentage</th>
            </tr>
            <tr>
                <td><strong>Descriptions</strong></td>
                <td>{counts.get('has_description', 0)}</td>
                <td>{percentages.get('has_description_percentage', 0):.1f}%</td>
            </tr>
            <tr>
                <td><strong>Epic Assignment</strong></td>
                <td>{counts.get('has_epic', 0)}</td>
                <td>{percentages.get('has_epic_percentage', 0):.1f}%</td>
            </tr>
            <tr>
                <td><strong>Priority</strong></td>
                <td>{counts.get('has_priority', 0)}</td>
                <td>{percentages.get('has_priority_percentage', 0):.1f}%</td>
            </tr>
            <tr>
                <td><strong>Story Points</strong></td>
                <td>{counts.get('has_story_points', 0)}</td>
                <td>{percentages.get('has_story_points_percentage', 0):.1f}%</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td><strong>Fully Complete Issues</strong></td>
                <td><strong>{counts.get('fully_complete', 0)}</strong></td>
                <td><strong>{percentages.get('fully_complete_percentage', 0):.1f}%</strong></td>
            </tr>
        </table>
        """
    
    def _generate_hygiene_age_section(self, results: Dict[str, Any]) -> str:
        """Generate age distribution section."""
        age = results.get('age_distribution', {})
        distribution = age.get('distribution', {})
        
        return f"""
        <h2>📅 Age Distribution</h2>
        <table class="wrapped">
            <tr>
                <th>Age Range</th>
                <th>Number of Issues</th>
            </tr>
            <tr>
                <td>0-7 days</td>
                <td>{distribution.get('0-7_days', 0)}</td>
            </tr>
            <tr>
                <td>8-30 days</td>
                <td>{distribution.get('8-30_days', 0)}</td>
            </tr>
            <tr>
                <td>31-90 days</td>
                <td>{distribution.get('31-90_days', 0)}</td>
            </tr>
            <tr style="background-color: #fff3cd;">
                <td>91-180 days</td>
                <td>{distribution.get('91-180_days', 0)}</td>
            </tr>
            <tr style="background-color: #f8d7da;">
                <td>180+ days</td>
                <td>{distribution.get('180+_days', 0)}</td>
            </tr>
        </table>
        <p><strong>Average Age:</strong> {age.get('average_age_days', 0)} days</p>
        <p><strong>Median Age:</strong> {age.get('median_age_days', 0)} days</p>
        """
    
    def _generate_hygiene_priority_epic_section(self, results: Dict[str, Any]) -> str:
        """Generate priority and epic analysis section."""
        priority = results.get('priority_distribution', {})
        epic = results.get('epic_assignment', {})
        
        # Priority distribution table
        priority_html = """
        <h2>🎯 Priority Distribution</h2>
        <table class="wrapped">
            <tr>
                <th>Priority</th>
                <th>Number of Issues</th>
            </tr>
        """
        
        for priority_name, count in priority.get('distribution', {}).items():
            priority_html += f"""
            <tr>
                <td>{priority_name}</td>
                <td>{count}</td>
            </tr>
            """
        
        priority_html += "</table>"
        
        # Epic assignment summary
        epic_html = f"""
        <h2>🎭 Epic Assignment</h2>
        <table class="wrapped">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td><strong>Issues with Epics</strong></td>
                <td>{epic.get('issues_with_epics', 0)} ({epic.get('epic_assignment_percentage', 0):.1f}%)</td>
            </tr>
            <tr>
                <td><strong>Orphaned Issues</strong></td>
                <td>{epic.get('orphaned_issues', 0)}</td>
            </tr>
            <tr>
                <td><strong>Unique Epics</strong></td>
                <td>{epic.get('unique_epics', 0)}</td>
            </tr>
        </table>
        """
        
        return priority_html + epic_html
    
    def _generate_hygiene_recommendations_section(self, results: Dict[str, Any]) -> str:
        """Generate recommendations section."""
        recommendations = results.get('recommendations', [])
        
        if not recommendations:
            return """
            <h2>⚡ Quick Action Items</h2>
            <p>🎉 Great job! Your backlog hygiene looks good with no specific action items at this time.</p>
            """
        
        html = """
        <h2>⚡ Quick Action Items</h2>
        <div style='background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 10px 0;'>
        <ol>
        """
        
        for recommendation in recommendations:
            html += f"<li>{recommendation}</li>"
        
        html += """
        </ol>
        </div>
        """
        
        return html
    
    def _generate_hygiene_ai_insights_section(self, results: Dict[str, Any]) -> str:
        """Generate AI insights section for backlog hygiene."""
        ai_insights = results.get('ai_insights', '')
        
        if not ai_insights:
            return ""
        
        html = """
        <h2>🤖 AI-Powered Insights</h2>
        <div style='background-color: #e8f4fd; padding: 15px; border-left: 4px solid #0066cc; margin: 10px 0;'>
        """
        
        # Format AI insights with proper line breaks
        formatted_insights = ai_insights.replace('\n', '</p><p>')
        html += f"<p>{formatted_insights}</p>"
        
        html += """
        </div>
        """
        
        return html
    
    def _generate_ai_insights_html(self, results: Dict[str, Any]) -> str:
        """Generate HTML content specifically for AI insights analysis."""
        # Header with current timestamp
        html = f"""
        <h1>🤖 AI-Powered Backlog Insights</h1>
        
        {self._generate_ai_insights_overview_section(results)}
        {self._generate_ai_key_findings_section(results)}
        {self._generate_ai_recommendations_section(results)}
        {self._generate_ai_action_items_section(results)}
        """
        
        return html
    
    def _generate_ai_insights_overview_section(self, results: Dict[str, Any]) -> str:
        """Generate AI insights overview section."""
        total_issues = results.get('total_issues', 0)
        hygiene_score = results.get('hygiene_score', 0)
        ai_insights = results.get('ai_insights', '')
        
        return f"""
        <h2>📊 Overview</h2>
        <div style='background-color: #f8f9fa; padding: 15px; border-left: 4px solid #6c757d; margin: 10px 0;'>
            <p><strong>Total Backlog Issues:</strong> {total_issues}</p>
            <p><strong>Overall Hygiene Score:</strong> {hygiene_score}%</p>
        </div>
        
        <h3>🎯 AI Analysis Summary</h3>
        <div style='background-color: #e8f4fd; padding: 15px; border-left: 4px solid #0066cc; margin: 10px 0;'>
            <p>{ai_insights.replace(chr(10), '</p><p>') if ai_insights else 'AI insights not available'}</p>
        </div>
        """
    
    def _generate_ai_key_findings_section(self, results: Dict[str, Any]) -> str:
        """Generate AI key findings section."""
        key_findings = results.get('key_findings', [])
        
        if not key_findings:
            return """
            <h2>🔍 Key Findings</h2>
            <p>No specific key findings identified at this time.</p>
            """
        
        html = """
        <h2>🔍 Key Findings</h2>
        <div style='background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 10px 0;'>
        <ul>
        """
        
        for finding in key_findings:
            html += f"<li>{finding}</li>"
        
        html += """
        </ul>
        </div>
        """
        
        return html
    
    def _generate_ai_recommendations_section(self, results: Dict[str, Any]) -> str:
        """Generate AI recommendations section."""
        recommendations = results.get('recommendations', [])
        
        if not recommendations:
            return """
            <h2>💡 AI Recommendations</h2>
            <p>🎉 No specific recommendations at this time - your backlog looks healthy!</p>
            """
        
        html = """
        <h2>💡 AI Recommendations</h2>
        <div style='background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 10px 0;'>
        <ol>
        """
        
        for recommendation in recommendations:
            html += f"<li>{recommendation}</li>"
        
        html += """
        </ol>
        </div>
        """
        
        return html
    
    def _generate_ai_action_items_section(self, results: Dict[str, Any]) -> str:
        """Generate AI action items section."""
        action_items = results.get('action_items', [])
        
        if not action_items:
            return """
            <h2>✅ Suggested Action Items</h2>
            <p>No specific action items suggested at this time.</p>
            """
        
        html = """
        <h2>✅ Suggested Action Items</h2>
        <div style='background-color: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 10px 0;'>
        <table class="wrapped">
            <tr>
                <th>Priority</th>
                <th>Action Item</th>
                <th>Expected Impact</th>
            </tr>
        """
        
        for item in action_items:
            priority = item.get('priority', 'Medium')
            action = item.get('action', '')
            impact = item.get('impact', 'Unknown')
            
            # Color code priority
            priority_color = '#dc3545' if priority == 'High' else ('#ffc107' if priority == 'Medium' else '#28a745')
            
            html += f"""
            <tr>
                <td style="background-color: {priority_color}; color: white; font-weight: bold;">{priority}</td>
                <td>{action}</td>
                <td>{impact}</td>
            </tr>
            """
        
        html += """
        </table>
        </div>
        """
        
        return html
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Confluence connection.
        
        Returns:
            dict: Connection test results
        """
        try:
            # Try to get spaces to test connection
            spaces = self.confluence.get_all_spaces(limit=1)
            
            return {
                'status': 'success',
                'message': 'Successfully connected to Confluence',
                'spaces_accessible': len(spaces.get('results', [])) > 0,
                'confluence_url': self.config.get_analyzer_config('confluence').get('url', '')
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'confluence_url': self.config.get_analyzer_config('confluence').get('url', '')
            }
    
    def list_available_spaces(self, limit: int = 10) -> Dict[str, Any]:
        """
        List available Confluence spaces.
        
        Args:
            limit (int): Maximum number of spaces to return
            
        Returns:
            dict: Available spaces information
        """
        try:
            spaces_response = self.confluence.get_all_spaces(limit=limit)
            spaces = spaces_response.get('results', [])
            
            space_list = []
            for space in spaces:
                space_list.append({
                    'key': space.get('key', ''),
                    'name': space.get('name', ''),
                    'type': space.get('type', ''),
                    'status': space.get('status', '')
                })
            
            return {
                'status': 'success',
                'total_spaces': len(space_list),
                'spaces': space_list
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _generate_hygiene_ai_recommendations_section(self, results: Dict[str, Any]) -> str:
        """Generate AI recommendations section with summary and action items."""
        ai_recommendations = results.get('ai_recommendations', '')
        
        if not ai_recommendations:
            return ""
        
        # Split the AI recommendations into summary and action items
        if "Action items:" in ai_recommendations:
            parts = ai_recommendations.split("Action items:")
            summary = parts[0].strip()
            action_items = parts[1].strip()
        else:
            summary = ai_recommendations
            action_items = ""
        
        html = """
        <h2>🤖 AI Backlog Assessment</h2>
        <div style='background-color: #e3f2fd; padding: 20px; border-left: 5px solid #2196F3; margin: 15px 0; border-radius: 5px;'>
        """
        
        # Add summary section
        if summary:
            html += f"""
            <h4 style='margin-top: 0; color: #1565C0;'>📊 Backlog Health Summary</h4>
            <p style='line-height: 1.6; margin-bottom: 15px;'>{summary}</p>
            """
        
        # Add action items section
        if action_items:
            html += f"""
            <h4 style='color: #1565C0; margin-bottom: 10px;'>⚡ Short-term Action Items</h4>
            <div style='background-color: #ffffff; padding: 15px; border-radius: 5px; border: 1px solid #2196F3;'>
                <p style='line-height: 1.6; margin: 0; font-weight: 500;'>{action_items}</p>
            </div>
            """
        
        html += """
        </div>
        <p><em>💡 AI analysis based on current backlog patterns and team workflow optimization.</em></p>
        """
        
        return html 