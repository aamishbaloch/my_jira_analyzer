"""
Sprint completion analysis for Jira.
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
            dict: Active sprints information
        """
        active_sprints = self.jira_client.get_active_sprints()
        
        summary = {
            'active_sprint_count': len(active_sprints),
            'sprints': []
        }
        
        for sprint in active_sprints:
            issues = self.jira_client.get_sprint_issues(sprint.id, expand_changelog=False)
            
            sprint_info = {
                'name': sprint.name,
                'start_date': sprint.startDate,
                'end_date': sprint.endDate,
                'total_issues': len(issues),
                'done_issues': len([i for i in issues if i.fields.status.name in ['Done', 'Closed', 'Resolved']])
            }
            
            if len(issues) > 0:
                sprint_info['current_completion_rate'] = calculate_completion_percentage(
                    sprint_info['done_issues'], 
                    sprint_info['total_issues']
                )
            else:
                sprint_info['current_completion_rate'] = 0.0
            
            summary['sprints'].append(sprint_info)
        
        return summary
    
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
                'tasks_details': []
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
                'status': issue.fields.status.name,
                'done_date': done_date,
                'completed_within_sprint': completed_within
            })
        
        completion_rate = calculate_completion_percentage(completed_within_sprint, len(issues))
        
        return {
            'sprint_name': sprint.name,
            'end_date': sprint.endDate,
            'total_tasks': len(issues),
            'completed_within_sprint': completed_within_sprint,
            'completion_rate': completion_rate,
            'tasks_details': tasks_details
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