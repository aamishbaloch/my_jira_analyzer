"""
Backlog hygiene analyzer for Jira projects.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from collections import Counter

from ..configs.config import Config
from ..clients.jira_client import JiraClient
from ..utils.utils import parse_jira_datetime
from ..gen_ai.hygiene_analyzer import HygieneAnalyzer


class BacklogHygieneAnalyzer:
    """
    Analyzer for backlog hygiene metrics including completeness, age, priority distribution,
    and epic assignment quality.
    """
    
    def __init__(self, config: Union[Config, str] = 'src/configs/config.json', ai_summarizer: Optional[HygieneAnalyzer] = None):
        """
        Initialize the BacklogHygieneAnalyzer with configuration.
        
        Args:
            config (Union[Config, str]): Config instance or path to configuration file
            ai_summarizer (Optional[HygieneAnalyzer]): Existing HygieneAnalyzer instance to reuse
        """
        if isinstance(config, Config):
            self.config = config
        else:
            self.config = Config(config)
        
        # Use provided HygieneAnalyzer or create a new one
        if ai_summarizer:
            self.ai_summarizer = ai_summarizer
        else:
            self.ai_summarizer = HygieneAnalyzer(self.config)
            
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
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            completeness_analysis, age_analysis, priority_analysis, epic_analysis
        )
        
        # Generate AI insights
        ai_insights = self._generate_ai_insights({
            'total_issues': len(backlog_issues),
            'hygiene_score': hygiene_score,
            'completeness': completeness_analysis,
            'age_distribution': age_analysis,
            'priority_distribution': priority_analysis,
            'epic_assignment': epic_analysis
        })
        
        # Generate AI recommendations for hygiene (concise, actionable)
        ai_recommendations = self._generate_ai_hygiene_recommendations({
            'total_issues': len(backlog_issues),
            'hygiene_score': hygiene_score,
            'completeness': completeness_analysis,
            'age_distribution': age_analysis,
            'priority_distribution': priority_analysis,
            'epic_assignment': epic_analysis
        })
        
        return {
            'total_issues': len(backlog_issues),
            'hygiene_score': hygiene_score,
            'completeness': completeness_analysis,
            'age_distribution': age_analysis,
            'priority_distribution': priority_analysis,
            'epic_assignment': epic_analysis,
            'status_distribution': status_analysis,
            'recommendations': recommendations,
            'ai_insights': ai_insights,
            'ai_recommendations': ai_recommendations,
            'analysis_timestamp': datetime.now().isoformat()
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
    
    def get_ai_enhanced_incomplete_analysis(self) -> Dict[str, Any]:
        """
        Get AI-enhanced analysis of incomplete issues with improvement suggestions.
        
        Returns:
            dict: AI-enhanced incomplete issues analysis
        """
        incomplete_result = self.get_incomplete_issues()
        incomplete_issues = incomplete_result.get('incomplete_issues', [])
        
        if not incomplete_issues:
            return incomplete_result
        
        # Get AI analysis of issue quality
        issues_for_ai = []
        for issue_data in incomplete_issues[:10]:  # Limit for API efficiency
            issues_for_ai.append({
                'summary': issue_data['summary'],
                'description': '',  # We know these are incomplete
                'issue_type': issue_data['issue_type']
            })
        
        ai_quality_analysis = self.ai_summarizer.analyze_issue_quality(issues_for_ai)
        
        # Add AI suggestions for top incomplete issues
        enhanced_issues = []
        for issue_data in incomplete_issues[:20]:  # Show top 20 with AI suggestions
            ai_suggestion = self.ai_summarizer.generate_issue_description_suggestions(
                issue_data['summary'], 
                issue_data['issue_type']
            )
            
            enhanced_issue = issue_data.copy()
            enhanced_issue['ai_improvement_suggestion'] = ai_suggestion
            enhanced_issues.append(enhanced_issue)
        
        incomplete_result['enhanced_issues'] = enhanced_issues
        incomplete_result['ai_quality_analysis'] = ai_quality_analysis
        
        return incomplete_result
    
    def get_ai_backlog_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive AI-powered backlog insights and recommendations.
        
        Returns:
            dict: AI-enhanced backlog analysis
        """
        hygiene_analysis = self.analyze_full_backlog_hygiene()
        
        # Get additional AI insights
        ai_insights = self._generate_ai_insights(hygiene_analysis)
        
        return {
            'hygiene_analysis': hygiene_analysis,
            'ai_insights': ai_insights,
            'analysis_type': 'ai_enhanced',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_ai_insights(self) -> Dict[str, Any]:
        """
        Get AI insights in a structured format for publishing.
        
        Returns:
            dict: Structured AI insights data
        """
        # Get base hygiene analysis
        hygiene_analysis = self.analyze_full_backlog_hygiene()
        
        # Generate AI insights
        ai_insights_text = self._generate_ai_insights(hygiene_analysis)
        
        # Extract structured data for better presentation
        key_findings = self._extract_key_findings(hygiene_analysis)
        recommendations = hygiene_analysis.get('recommendations', [])
        action_items = self._generate_action_items(hygiene_analysis)
        
        return {
            'total_issues': hygiene_analysis.get('total_issues', 0),
            'hygiene_score': hygiene_analysis.get('hygiene_score', 0),
            'ai_insights': ai_insights_text,
            'key_findings': key_findings,
            'recommendations': recommendations,
            'action_items': action_items,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _extract_key_findings(self, hygiene_analysis: Dict[str, Any]) -> List[str]:
        """Extract key findings from hygiene analysis."""
        findings = []
        
        # Completeness findings
        completeness = hygiene_analysis.get('completeness', {})
        percentages = completeness.get('percentages', {})
        
        if percentages.get('has_description_percentage', 0) < 70:
            findings.append(f"Only {percentages.get('has_description_percentage', 0):.1f}% of issues have meaningful descriptions")
        
        if percentages.get('has_story_points_percentage', 0) < 60:
            findings.append(f"Only {percentages.get('has_story_points_percentage', 0):.1f}% of issues have story points estimated")
        
        # Age findings
        age = hygiene_analysis.get('age_distribution', {})
        avg_age = age.get('average_age_days', 0)
        if avg_age > 90:
            findings.append(f"Average issue age is {avg_age} days - consider reviewing older items")
        
        # Epic assignment findings
        epic = hygiene_analysis.get('epic_assignment', {})
        epic_percentage = epic.get('epic_assignment_percentage', 0)
        if epic_percentage < 70:
            findings.append(f"Only {epic_percentage:.1f}% of issues are assigned to epics")
        
        # Priority findings
        priority = hygiene_analysis.get('priority_distribution', {})
        if priority.get('issues_without_priority', 0) > 0:
            findings.append(f"{priority.get('issues_without_priority', 0)} issues are missing priority assignments")
        
        return findings
    
    def _generate_action_items(self, hygiene_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate structured action items from hygiene analysis."""
        action_items = []
        
        # High priority actions
        completeness = hygiene_analysis.get('completeness', {})
        if completeness.get('counts', {}).get('missing_description', 0) > 10:
            action_items.append({
                'priority': 'High',
                'action': f"Add descriptions to {completeness.get('counts', {}).get('missing_description', 0)} issues",
                'impact': 'Improves team understanding and reduces clarification time'
            })
        
        # Medium priority actions
        epic = hygiene_analysis.get('epic_assignment', {})
        if epic.get('orphaned_issues', 0) > 5:
            action_items.append({
                'priority': 'Medium',
                'action': f"Assign {epic.get('orphaned_issues', 0)} orphaned issues to epics",
                'impact': 'Better organization and sprint planning'
            })
        
        # Age-based actions
        age = hygiene_analysis.get('age_distribution', {})
        old_issues = age.get('distribution', {}).get('180+_days', 0)
        if old_issues > 0:
            action_items.append({
                'priority': 'Medium',
                'action': f"Review and triage {old_issues} issues older than 180 days",
                'impact': 'Reduces backlog clutter and improves focus'
            })
        
        # Low priority actions
        completeness = hygiene_analysis.get('completeness', {})
        if completeness.get('counts', {}).get('missing_story_points', 0) > 0:
            action_items.append({
                'priority': 'Low',
                'action': f"Estimate story points for {completeness.get('counts', {}).get('missing_story_points', 0)} issues",
                'impact': 'Better sprint planning and velocity tracking'
            })
        
        return action_items
    
    def _generate_ai_insights(self, hygiene_data: Dict[str, Any]) -> str:
        """
        Generate AI-powered insights for backlog hygiene.
        
        Args:
            hygiene_data (dict): Hygiene analysis data
            
        Returns:
            str: AI-generated insights and recommendations
        """
        try:
            return self.ai_summarizer.generate_backlog_hygiene_insights(hygiene_data)
        except Exception as e:
            print(f"⚠️  AI insights generation failed: {e}")
            return f"AI insights unavailable. Hygiene score: {hygiene_data.get('hygiene_score', 0)}%"

    def _generate_ai_hygiene_recommendations(self, hygiene_data: Dict[str, Any]) -> str:
        """
        Generate AI-powered concise and actionable recommendations for backlog hygiene.
        
        Args:
            hygiene_data (dict): Hygiene analysis data
            
        Returns:
            str: AI-generated concise and actionable recommendations
        """
        try:
            return self.ai_summarizer.generate_ai_hygiene_recommendations(hygiene_data)
        except Exception as e:
            print(f"⚠️  AI recommendations generation failed: {e}")
            return "AI recommendations unavailable. Hygiene score: {hygiene_data.get('hygiene_score', 0)}%" 