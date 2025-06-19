"""
Sprint completion rate analyzer for Jira projects.
"""

from datetime import datetime
from typing import List, Dict, Any

from ..core.config import Config
from ..core.jira_client import JiraClient
from ..core.utils import parse_jira_datetime, calculate_completion_percentage


class SprintAnalyzer:
    """
    Analyzer for Jira sprint completion rates based on actual task completion dates.
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the SprintAnalyzer with configuration.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config = Config(config_path)
        self.jira_client = JiraClient(self.config)
        
    def calculate_sprints_by_month(self, target_month: int) -> Dict[str, Any]:
        """
        Calculate completion rates for all sprints closed in a specific month.
        
        Args:
            target_month (int): Month number (1-12)
            
        Returns:
            dict: Analysis results with sprint data and statistics
        """
        sprints = self._get_closed_sprints_by_month(target_month)
        
        if not sprints:
            return {
                'analysis_type': 'month',
                'target_month': target_month,
                'sprint_results': [],
                'total_tasks': 0,
                'total_completed': 0,
                'average_completion_rate': 0,
                'best_sprint_rate': 0,
                'worst_sprint_rate': 0
            }
        
        sprint_results = []
        for sprint in sprints:
            result = self._analyze_single_sprint(sprint)
            sprint_results.append(result)
        
        return self._calculate_statistics(sprint_results, 'month', target_month)
    
    def calculate_last_x_sprints(self, sprint_count: int) -> Dict[str, Any]:
        """
        Calculate completion rates for the last X closed sprints.
        
        Args:
            sprint_count (int): Number of recent sprints to analyze
            
        Returns:
            dict: Analysis results with sprint data and statistics
        """
        all_sprints = self.jira_client.get_all_closed_sprints()
        sprints = all_sprints[:sprint_count]
        
        if not sprints:
            return {
                'analysis_type': 'last_sprints',
                'sprint_count': sprint_count,
                'sprint_results': [],
                'total_tasks': 0,
                'total_completed': 0,
                'average_completion_rate': 0,
                'best_sprint_rate': 0,
                'worst_sprint_rate': 0
            }
        
        sprint_results = []
        for sprint in sprints:
            result = self._analyze_single_sprint(sprint)
            sprint_results.append(result)
        
        return self._calculate_statistics(sprint_results, 'last_sprints', sprint_count)
    
    def get_active_sprints_summary(self) -> Dict[str, Any]:
        """
        Get summary of currently active sprints.
        
        Returns:
            dict: Active sprint summary with current progress
        """
        try:
            active_sprints = self.jira_client.get_active_sprints()
            
            sprint_summaries = []
            for sprint in active_sprints:
                # Get issues in this sprint
                jql = f'project = {self.config.get_jira_config()["project_key"]} AND sprint = {sprint.id}'
                issues = self.jira_client.jira.search_issues(jql, maxResults=1000)
                
                total_issues = len(issues)
                done_issues = len([issue for issue in issues if issue.fields.status.name.upper() == 'DONE'])
                
                current_completion_rate = (done_issues / total_issues * 100) if total_issues > 0 else 0
                
                sprint_summaries.append({
                    'name': sprint.name,
                    'id': sprint.id,
                    'start_date': sprint.startDate,
                    'end_date': sprint.endDate,
                    'total_issues': total_issues,
                    'done_issues': done_issues,
                    'current_completion_rate': current_completion_rate
                })
            
            return {
                'active_sprint_count': len(active_sprints),
                'sprints': sprint_summaries,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get active sprints summary: {str(e)}")
    
    def analyze_sprint_by_name(self, sprint_name: str) -> Dict[str, Any]:
        """
        Analyze a specific sprint by name.
        
        Args:
            sprint_name (str): Name of the sprint to analyze
            
        Returns:
            dict: Analysis results for the specified sprint
        """
        # Find the sprint by name
        sprint = self.jira_client.find_sprint_by_name(sprint_name)
        
        if not sprint:
            return {
                'analysis_type': 'sprint_by_name',
                'sprint_name': sprint_name,
                'found': False,
                'error': f'Sprint "{sprint_name}" not found'
            }
        
        # Analyze the found sprint
        result = self._analyze_single_sprint(sprint)
        result['analysis_type'] = 'sprint_by_name'
        result['found'] = True
        result['sprint_id'] = sprint.id
        result['sprint_state'] = getattr(sprint, 'state', 'unknown')
        result['start_date'] = getattr(sprint, 'startDate', None)
        
        return result
    
    def get_average_completion_rate_last_4_sprints(self) -> Dict[str, Any]:
        """
        Get the average completion rate of the last 4 closed sprints.
        This is a quick way to check recent sprint performance.
        
        Returns:
            dict: Simple result with average completion rate and basic stats
        """
        try:
            all_sprints = self.jira_client.get_all_closed_sprints()
            last_4_sprints = all_sprints[:4]
            
            if not last_4_sprints:
                return {
                    'average_completion_rate': 0,
                    'sprints_analyzed': 0,
                    'sprint_rates': [],
                    'message': 'No closed sprints found'
                }
            
            sprint_rates = []
            for sprint in last_4_sprints:
                result = self._analyze_single_sprint(sprint)
                sprint_rates.append({
                    'name': result['sprint_name'],
                    'completion_rate': result['completion_rate'],
                    'total_tasks': result['total_tasks'],
                    'completed_tasks': result['completed_within_sprint']
                })
            
            # Calculate average completion rate
            total_completion_rates = sum(sprint['completion_rate'] for sprint in sprint_rates)
            average_rate = total_completion_rates / len(sprint_rates) if sprint_rates else 0
            
            return {
                'average_completion_rate': round(average_rate, 1),
                'sprints_analyzed': len(last_4_sprints),
                'sprint_rates': sprint_rates,
                'message': f'Average completion rate across last {len(last_4_sprints)} sprints: {round(average_rate, 1)}%'
            }
            
        except Exception as e:
            return {
                'average_completion_rate': 0,
                'sprints_analyzed': 0,
                'sprint_rates': [],
                'error': f'Failed to calculate average completion rate: {str(e)}'
            }
    
    def _get_closed_sprints_by_month(self, target_month: int) -> List[Any]:
        """Get closed sprints filtered by target month."""
        all_sprints = self.jira_client.get_all_closed_sprints()
        
        # Filter sprints by target month
        filtered_sprints = []
        for sprint in all_sprints:
            end_date = parse_jira_datetime(sprint.endDate)
            if end_date.month == target_month:
                filtered_sprints.append(sprint)
        
        return filtered_sprints
    
    def _analyze_single_sprint(self, sprint: Any) -> Dict[str, Any]:
        """
        Analyze completion rate for a single sprint.
        
        Args:
            sprint: Jira sprint object
            
        Returns:
            dict: Sprint analysis results
        """
        issues = self.jira_client.get_sprint_issues(sprint.id, expand_changelog=True)
        
        if not issues:
            return {
                'sprint_name': sprint.name,
                'end_date': sprint.endDate,
                'total_tasks': 0,
                'completed_within_sprint': 0,
                'completion_rate': 0.0,
                'tasks': []
            }
        
        sprint_end = parse_jira_datetime(sprint.endDate)
        completed_within_sprint = 0
        tasks_details = []
        
        for issue in issues:
            # Find when the issue was marked as "Done"
            done_date = self._find_done_date(issue)
            
            completed_within = False
            if done_date and done_date <= sprint_end:
                completed_within_sprint += 1
                completed_within = True
            
            tasks_details.append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'current_status': issue.fields.status.name,
                'completion_date': done_date.strftime('%Y-%m-%d') if done_date else None,
                'completed_within_sprint': completed_within
            })
        
        completion_rate = calculate_completion_percentage(completed_within_sprint, len(issues))
        
        return {
            'sprint_name': sprint.name,
            'end_date': sprint.endDate,
            'total_tasks': len(issues),
            'completed_within_sprint': completed_within_sprint,
            'completion_rate': completion_rate,
            'tasks': tasks_details
        }
    
    def _find_done_date(self, issue: Any) -> datetime:
        """
        Find when an issue was marked as "Done" by analyzing the changelog.
        
        Args:
            issue: Jira issue object with changelog
            
        Returns:
            datetime or None: When the issue was marked as "Done"
        """
        if not hasattr(issue, 'changelog') or not issue.changelog:
            return None
        
        for history in issue.changelog.histories:
            for item in history.items:
                if item.field == 'status' and item.toString in ['Done', 'Closed', 'Resolved']:
                    try:
                        return parse_jira_datetime(history.created)
                    except ValueError:
                        continue
        
        return None
    
    def _calculate_statistics(self, sprint_results: List[Dict], analysis_type: str, parameter: int) -> Dict[str, Any]:
        """
        Calculate overall statistics from sprint results.
        
        Args:
            sprint_results (list): List of sprint analysis results
            analysis_type (str): 'month' or 'last_sprints'
            parameter (int): Month number or sprint count
            
        Returns:
            dict: Complete analysis results with statistics
        """
        total_tasks = sum(r['total_tasks'] for r in sprint_results)
        total_completed = sum(r['completed_within_sprint'] for r in sprint_results)
        average_completion_rate = calculate_completion_percentage(total_completed, total_tasks)
        
        best_sprint_rate = max(r['completion_rate'] for r in sprint_results) if sprint_results else 0
        worst_sprint_rate = min(r['completion_rate'] for r in sprint_results) if sprint_results else 0
        
        result = {
            'analysis_type': analysis_type,
            'sprint_results': sprint_results,
            'total_tasks': total_tasks,
            'total_completed': total_completed,
            'average_completion_rate': average_completion_rate,
            'best_sprint_rate': best_sprint_rate,
            'worst_sprint_rate': worst_sprint_rate
        }
        
        if analysis_type == 'month':
            result['target_month'] = parameter
        else:
            result['sprint_count'] = parameter
        
        return result 