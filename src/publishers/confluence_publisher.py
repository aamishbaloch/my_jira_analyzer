"""
Confluence publisher for creating and updating pages with Jira analysis data.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from atlassian import Confluence

from ..core.config import Config
from ..core.utils import get_month_name, format_duration
from ..core.ai_summarizer import AISummarizer
from ..analyzers.sprint_analyzer import SprintAnalyzer


class ConfluencePublisher:
    """
    Publisher for creating and updating Confluence pages with Jira analysis data.
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the Confluence publisher.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config = Config(config_path)
        self.confluence = self._connect()
        self.ai_summarizer = AISummarizer(config_path)
        self.sprint_analyzer = SprintAnalyzer(config_path)
        
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
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
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