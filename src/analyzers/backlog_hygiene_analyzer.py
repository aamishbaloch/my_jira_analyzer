"""
Backlog hygiene analyzer for Jira projects.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter

from ..core.config import Config
from ..core.jira_client import JiraClient
from ..core.utils import parse_jira_datetime


class BacklogHygieneAnalyzer:
    """
    Analyzer for backlog hygiene metrics including completeness, age, priority distribution,
    and epic assignment quality.
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the BacklogHygieneAnalyzer with configuration.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config = Config(config_path)
        self.jira_client = JiraClient(self.config)
        
    def analyze_full_backlog_hygiene(self) -> Dict[str, Any]:
        """
        Perform comprehensive backlog hygiene analysis.
        
        Returns:
            dict: Complete hygiene analysis results
        """
        backlog_issues = self._get_backlog_issues()
        
        if not backlog_issues:
            return {
                'total_issues': 0,
                'message': 'No backlog issues found',
                'hygiene_score': 0,
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        # Analyze different aspects of hygiene
        completeness_analysis = self._analyze_completeness(backlog_issues)
        age_analysis = self._analyze_age_distribution(backlog_issues)
        priority_analysis = self._analyze_priority_distribution(backlog_issues)
        epic_analysis = self._analyze_epic_assignment(backlog_issues)
        status_analysis = self._analyze_status_distribution(backlog_issues)
        
        # Calculate overall hygiene score
        hygiene_score = self._calculate_hygiene_score(
            completeness_analysis, age_analysis, priority_analysis, epic_analysis
        )
        
        return {
            'total_issues': len(backlog_issues),
            'hygiene_score': hygiene_score,
            'completeness': completeness_analysis,
            'age_distribution': age_analysis,
            'priority_distribution': priority_analysis,
            'epic_assignment': epic_analysis,
            'status_distribution': status_analysis,
            'analysis_timestamp': datetime.now().isoformat(),
            'recommendations': self._generate_recommendations(
                completeness_analysis, age_analysis, priority_analysis, epic_analysis
            )
        }
    
    def get_hygiene_summary(self) -> Dict[str, Any]:
        """
        Get a quick summary of backlog hygiene.
        
        Returns:
            dict: Brief hygiene summary with key metrics
        """
        try:
            backlog_issues = self._get_backlog_issues()
            
            if not backlog_issues:
                return {
                    'hygiene_score': 0,
                    'total_issues': 0,
                    'issues_with_descriptions': 0,
                    'issues_with_epics': 0,
                    'average_age_days': 0,
                    'message': 'No backlog issues found'
                }
            
            # Quick calculations
            issues_with_descriptions = sum(1 for issue in backlog_issues 
                                         if self._has_meaningful_description(issue))
            issues_with_epics = sum(1 for issue in backlog_issues 
                                  if self._has_epic_assignment(issue))
            
            # Calculate average age
            total_age_days = 0
            for issue in backlog_issues:
                age_days = self._calculate_issue_age_days(issue)
                total_age_days += age_days
            
            average_age = total_age_days / len(backlog_issues) if backlog_issues else 0
            
            # Quick hygiene score calculation
            description_score = (issues_with_descriptions / len(backlog_issues)) * 100
            epic_score = (issues_with_epics / len(backlog_issues)) * 100
            age_score = max(0, 100 - (average_age / 90) * 100)  # Penalty for old issues
            
            hygiene_score = (description_score + epic_score + age_score) / 3
            
            return {
                'hygiene_score': round(hygiene_score, 1),
                'total_issues': len(backlog_issues),
                'issues_with_descriptions': issues_with_descriptions,
                'issues_with_epics': issues_with_epics,
                'average_age_days': round(average_age, 1),
                'description_percentage': round(description_score, 1),
                'epic_assignment_percentage': round(epic_score, 1),
                'message': f'Backlog hygiene score: {round(hygiene_score, 1)}% ({len(backlog_issues)} issues analyzed)'
            }
            
        except Exception as e:
            return {
                'hygiene_score': 0,
                'total_issues': 0,
                'issues_with_descriptions': 0,
                'issues_with_epics': 0,
                'average_age_days': 0,
                'error': f'Failed to analyze backlog hygiene: {str(e)}'
            }
    
    def get_stale_issues(self, days_threshold: int = 90) -> Dict[str, Any]:
        """
        Get issues that have been in backlog for too long.
        
        Args:
            days_threshold (int): Number of days to consider as stale (default: 90)
            
        Returns:
            dict: Analysis of stale issues
        """
        backlog_issues = self._get_backlog_issues()
        
        if not backlog_issues:
            return {
                'stale_issues': [],
                'stale_count': 0,
                'total_issues': 0,
                'staleness_percentage': 0,
                'days_threshold': days_threshold
            }
        
        stale_issues = []
        for issue in backlog_issues:
            age_days = self._calculate_issue_age_days(issue)
            if age_days >= days_threshold:
                epic_info = self.jira_client.get_epic_for_issue(issue)
                stale_issues.append({
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'age_days': age_days,
                    'created_date': issue.fields.created,
                    'status': issue.fields.status.name,
                    'priority': getattr(issue.fields.priority, 'name', 'None') if issue.fields.priority else 'None',
                    'epic_key': epic_info['key'],
                    'epic_summary': epic_info['summary']
                })
        
        # Sort by age (oldest first)
        stale_issues.sort(key=lambda x: x['age_days'], reverse=True)
        
        staleness_percentage = (len(stale_issues) / len(backlog_issues)) * 100
        
        return {
            'stale_issues': stale_issues,
            'stale_count': len(stale_issues),
            'total_issues': len(backlog_issues),
            'staleness_percentage': round(staleness_percentage, 1),
            'days_threshold': days_threshold,
            'oldest_issue_age': stale_issues[0]['age_days'] if stale_issues else 0
        }
    
    def get_incomplete_issues(self) -> Dict[str, Any]:
        """
        Get issues that are missing important information.
        
        Returns:
            dict: Analysis of incomplete issues
        """
        backlog_issues = self._get_backlog_issues()
        
        if not backlog_issues:
            return {
                'incomplete_issues': [],
                'incomplete_count': 0,
                'total_issues': 0,
                'completion_percentage': 100
            }
        
        incomplete_issues = []
        for issue in backlog_issues:
            missing_fields = []
            
            # Check for missing description
            if not self._has_meaningful_description(issue):
                missing_fields.append('description')
            
            # Check for missing epic
            if not self._has_epic_assignment(issue):
                missing_fields.append('epic')
            
            # Check for missing priority
            if not issue.fields.priority:
                missing_fields.append('priority')
            
            # Check for missing story points (if applicable)
            story_points = self._get_story_points(issue)
            if story_points is None and issue.fields.issuetype.name in ['Story', 'Task']:
                missing_fields.append('story_points')
            
            if missing_fields:
                incomplete_issues.append({
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'missing_fields': missing_fields,
                    'missing_count': len(missing_fields),
                    'issue_type': issue.fields.issuetype.name,
                    'created_date': issue.fields.created,
                    'age_days': self._calculate_issue_age_days(issue)
                })
        
        # Sort by number of missing fields (most incomplete first)
        incomplete_issues.sort(key=lambda x: x['missing_count'], reverse=True)
        
        completion_percentage = ((len(backlog_issues) - len(incomplete_issues)) / len(backlog_issues)) * 100
        
        return {
            'incomplete_issues': incomplete_issues,
            'incomplete_count': len(incomplete_issues),
            'total_issues': len(backlog_issues),
            'completion_percentage': round(completion_percentage, 1),
            'most_common_missing_fields': self._get_most_common_missing_fields(incomplete_issues)
        }
    
    def _get_backlog_issues(self) -> List[Any]:
        """Get all backlog issues (not in active sprints or done)."""
        # JQL to get backlog issues - not in active sprints and not done
        jql = f"""
        project = {self.config.project_key} 
        AND status NOT IN (Done, Closed, Resolved)
        AND sprint IS EMPTY
        ORDER BY created DESC
        """
        
        return self.jira_client.search_issues(jql.strip(), max_results=2000)
    
    def _analyze_completeness(self, issues: List[Any]) -> Dict[str, Any]:
        """Analyze completeness of issue information."""
        total_issues = len(issues)
        
        metrics = {
            'has_description': 0,
            'has_epic': 0,
            'has_priority': 0,
            'has_story_points': 0,
            'fully_complete': 0
        }
        
        for issue in issues:
            if self._has_meaningful_description(issue):
                metrics['has_description'] += 1
            
            if self._has_epic_assignment(issue):
                metrics['has_epic'] += 1
            
            if issue.fields.priority:
                metrics['has_priority'] += 1
            
            story_points = self._get_story_points(issue)
            if story_points is not None:
                metrics['has_story_points'] += 1
            
            # Check if fully complete (all required fields present)
            is_complete = all([
                self._has_meaningful_description(issue),
                self._has_epic_assignment(issue),
                issue.fields.priority,
                story_points is not None if issue.fields.issuetype.name in ['Story', 'Task'] else True
            ])
            
            if is_complete:
                metrics['fully_complete'] += 1
        
        # Convert to percentages
        percentages = {}
        for key, value in metrics.items():
            percentages[f'{key}_percentage'] = (value / total_issues * 100) if total_issues > 0 else 0
        
        return {
            'counts': metrics,
            'percentages': percentages,
            'total_issues': total_issues
        }
    
    def _analyze_age_distribution(self, issues: List[Any]) -> Dict[str, Any]:
        """Analyze age distribution of backlog issues."""
        age_buckets = {
            '0-7_days': 0,
            '8-30_days': 0,
            '31-90_days': 0,
            '91-180_days': 0,
            '180+_days': 0
        }
        
        ages = []
        for issue in issues:
            age_days = self._calculate_issue_age_days(issue)
            ages.append(age_days)
            
            if age_days <= 7:
                age_buckets['0-7_days'] += 1
            elif age_days <= 30:
                age_buckets['8-30_days'] += 1
            elif age_days <= 90:
                age_buckets['31-90_days'] += 1
            elif age_days <= 180:
                age_buckets['91-180_days'] += 1
            else:
                age_buckets['180+_days'] += 1
        
        average_age = sum(ages) / len(ages) if ages else 0
        median_age = sorted(ages)[len(ages) // 2] if ages else 0
        
        return {
            'distribution': age_buckets,
            'average_age_days': round(average_age, 1),
            'median_age_days': median_age,
            'oldest_issue_days': max(ages) if ages else 0,
            'newest_issue_days': min(ages) if ages else 0
        }
    
    def _analyze_priority_distribution(self, issues: List[Any]) -> Dict[str, Any]:
        """Analyze priority distribution of backlog issues."""
        priorities = []
        for issue in issues:
            priority = getattr(issue.fields.priority, 'name', 'None') if issue.fields.priority else 'None'
            priorities.append(priority)
        
        priority_counts = Counter(priorities)
        
        return {
            'distribution': dict(priority_counts),
            'total_issues': len(issues),
            'issues_without_priority': priority_counts.get('None', 0),
            'most_common_priority': priority_counts.most_common(1)[0] if priority_counts else ('None', 0)
        }
    
    def _analyze_epic_assignment(self, issues: List[Any]) -> Dict[str, Any]:
        """Analyze epic assignment quality."""
        epic_assignments = []
        issues_with_epics = 0
        
        for issue in issues:
            epic_info = self.jira_client.get_epic_for_issue(issue)
            has_epic = epic_info['key'] is not None
            
            if has_epic:
                issues_with_epics += 1
                epic_assignments.append(epic_info['key'])
        
        epic_distribution = Counter(epic_assignments)
        
        return {
            'issues_with_epics': issues_with_epics,
            'issues_without_epics': len(issues) - issues_with_epics,
            'epic_assignment_percentage': (issues_with_epics / len(issues) * 100) if issues else 0,
            'unique_epics': len(epic_distribution),
            'epic_distribution': dict(epic_distribution.most_common(10)),  # Top 10 epics
            'orphaned_issues': len(issues) - issues_with_epics
        }
    
    def _analyze_status_distribution(self, issues: List[Any]) -> Dict[str, Any]:
        """Analyze status distribution of backlog issues."""
        statuses = [issue.fields.status.name for issue in issues]
        status_counts = Counter(statuses)
        
        return {
            'distribution': dict(status_counts),
            'total_issues': len(issues),
            'unique_statuses': len(status_counts),
            'most_common_status': status_counts.most_common(1)[0] if status_counts else ('None', 0)
        }
    
    def _calculate_hygiene_score(self, completeness: Dict, age: Dict, 
                               priority: Dict, epic: Dict) -> float:
        """Calculate overall hygiene score (0-100)."""
        # Completeness score (40% weight)
        completeness_score = completeness['percentages']['fully_complete_percentage']
        
        # Age score (30% weight) - penalty for old issues
        avg_age = age['average_age_days']
        age_score = max(0, 100 - (avg_age / 90) * 100)  # 90 days as baseline
        
        # Epic assignment score (20% weight)
        epic_score = epic['epic_assignment_percentage']
        
        # Priority assignment score (10% weight)
        priority_without = priority['issues_without_priority']
        priority_total = priority['total_issues']
        priority_score = ((priority_total - priority_without) / priority_total * 100) if priority_total > 0 else 0
        
        # Weighted average
        overall_score = (
            completeness_score * 0.4 +
            age_score * 0.3 +
            epic_score * 0.2 +
            priority_score * 0.1
        )
        
        return round(overall_score, 1)
    
    def _generate_recommendations(self, completeness: Dict, age: Dict, 
                                priority: Dict, epic: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Completeness recommendations
        if completeness['percentages']['has_description_percentage'] < 80:
            recommendations.append(
                f"Add meaningful descriptions to issues missing descriptions"
            )
        
        if epic['epic_assignment_percentage'] < 70:
            recommendations.append(
                f"Assign {epic['orphaned_issues']} orphaned issues to appropriate epics"
            )
        
        # Age recommendations
        if age['average_age_days'] > 60:
            recommendations.append(
                f"Review and prioritize old issues (average age: {age['average_age_days']} days)"
            )
        
        # Priority recommendations
        if priority['issues_without_priority'] > 0:
            recommendations.append(
                f"Set priorities for {priority['issues_without_priority']} issues without priority"
            )
        
        # Story points recommendations
        if completeness['percentages']['has_story_points_percentage'] < 60:
            recommendations.append(
                "Estimate story points for unestimated stories and tasks"
            )
        
        return recommendations
    
    def _has_meaningful_description(self, issue: Any) -> bool:
        """Check if issue has a meaningful description."""
        description = getattr(issue.fields, 'description', '') or ''
        return len(description.strip()) > 10  # At least 10 characters
    
    def _has_epic_assignment(self, issue: Any) -> bool:
        """Check if issue is assigned to an epic."""
        epic_info = self.jira_client.get_epic_for_issue(issue)
        return epic_info['key'] is not None
    
    def _get_story_points(self, issue: Any) -> Optional[float]:
        """Get story points for an issue."""
        # Common story points field names
        story_points_fields = ['customfield_10016', 'customfield_10002', 'storyPoints']
        
        for field_name in story_points_fields:
            if hasattr(issue.fields, field_name):
                points = getattr(issue.fields, field_name)
                if points is not None:
                    return float(points)
        
        return None
    
    def _calculate_issue_age_days(self, issue: Any) -> int:
        """Calculate age of issue in days."""
        created_date = parse_jira_datetime(issue.fields.created)
        return (datetime.now(created_date.tzinfo) - created_date).days
    
    def _get_most_common_missing_fields(self, incomplete_issues: List[Dict]) -> List[Dict]:
        """Get most common missing fields across incomplete issues."""
        all_missing = []
        for issue in incomplete_issues:
            all_missing.extend(issue['missing_fields'])
        
        missing_counts = Counter(all_missing)
        
        return [
            {'field': field, 'count': count, 'percentage': round(count / len(incomplete_issues) * 100, 1)}
            for field, count in missing_counts.most_common()
        ] 