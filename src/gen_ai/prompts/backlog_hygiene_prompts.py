"""
Backlog hygiene analysis prompt templates for AI insights.
"""

from typing import Dict, List, Any


class BacklogHygieneRecommenderPrompt:
    """
    Prompt templates for backlog hygiene analysis and recommendations.
    """
    
    @staticmethod
    def get_insights_system_context() -> str:
        """
        Get the system context for hygiene insights.
        
        Returns:
            str: System context prompt
        """
        return """You are a Scrum expert and agile team coach. Given a backlog hygiene report that includes metrics like total issues, hygiene score, issue age distribution, epic assignment, story point coverage, and field completeness, provide the following:

1. Write a concise, direct, and clear summary of the current backlog health. Avoid long explanations. Focus on key signals such as hygiene score, issue age, missing estimates, and epic assignment. Clearly state whether the backlog is healthy, needs improvement, or is at risk.
2. Recommend 2 to 3 short-term action items the team can take this week to improve backlog quality. These actions should align with Scrum and Agile best practices such as backlog refinement, closing stale issues, assigning epics, or adding estimates.
3. Where helpful, reference Agile principles like transparency, definition of ready, or iterative delivery to justify the actions.
4. Make the suggestions specific and actionable — for example: "Schedule a 45-minute backlog triage to close or reclassify issues older than 90 days" instead of vague statements.
5. Output must be plain text only. Do not use bold, italics, or markdown formatting.

Focus on making the backlog actionable, prioritized, and sprint-ready, while reinforcing agile ways of working.

"""
    
    @staticmethod
    def get_recommendations_system_context() -> str:
        """
        Get the system context for hygiene recommendations.
        
        Returns:
            str: System context prompt
        """
        return """You are a Scrum expert and agile team coach. Given a backlog hygiene report that includes metrics like total issues, hygiene score, issue age distribution, epic assignment, story point coverage, and field completeness, provide the following:

1. Write a concise, direct, and clear summary of the current backlog health. Avoid long explanations. Focus on key signals such as hygiene score, issue age, missing estimates, and epic assignment. Clearly state whether the backlog is healthy, needs improvement, or is at risk.
2. Recommend 2 to 3 short-term action items the team can take this week to improve backlog quality. These actions should align with Scrum and Agile best practices such as backlog refinement, closing stale issues, assigning epics, or adding estimates.
3. Where helpful, reference Agile principles like transparency, definition of ready, or iterative delivery to justify the actions.
4. Make the suggestions specific and actionable — for example: "Schedule a 45-minute backlog triage to close or reclassify issues older than 90 days" instead of vague statements.
5. Output must be plain text only. Do not use bold, italics, or markdown formatting.

Focus on making the backlog actionable, prioritized, and sprint-ready, while reinforcing agile ways of working.

"""
    
    @staticmethod
    def create_hygiene_insights_prompt(hygiene_data: Dict[str, Any]) -> str:
        """
        Create the main hygiene insights prompt.
        
        Args:
            hygiene_data (dict): Hygiene analysis data
            
        Returns:
            str: Formatted prompt for AI
        """
        total_issues = hygiene_data.get('total_issues', 0)
        hygiene_score = hygiene_data.get('hygiene_score', 0)
        completeness = hygiene_data.get('completeness', {})
        age_distribution = hygiene_data.get('age_distribution', {})
        priority_distribution = hygiene_data.get('priority_distribution', {})
        epic_assignment = hygiene_data.get('epic_assignment', {})
        
        # Extract key metrics
        completeness_percentages = completeness.get('percentages', {})
        age_dist = age_distribution.get('distribution', {})
        priority_dist = priority_distribution.get('distribution', {})
        
        return f"""Backlog Hygiene Analysis Data:

Overall Metrics:
- Total Issues: {total_issues}
- Hygiene Score: {hygiene_score}%

Completeness Analysis:
- Issues with Descriptions: {completeness_percentages.get('has_description_percentage', 0):.1f}%
- Issues with Epic Assignment: {completeness_percentages.get('has_epic_percentage', 0):.1f}%
- Issues with Priority: {completeness_percentages.get('has_priority_percentage', 0):.1f}%
- Issues with Story Points: {completeness_percentages.get('has_story_points_percentage', 0):.1f}%
- Fully Complete Issues: {completeness_percentages.get('fully_complete_percentage', 0):.1f}%

Age Distribution:
- 0-7 days: {age_dist.get('0-7_days', 0)} issues
- 8-30 days: {age_dist.get('8-30_days', 0)} issues
- 31-90 days: {age_dist.get('31-90_days', 0)} issues
- 91-180 days: {age_dist.get('91-180_days', 0)} issues
- 180+ days: {age_dist.get('180+_days', 0)} issues
- Average Age: {age_distribution.get('average_age_days', 0)} days

Priority Distribution:
{chr(10).join([f"- {priority}: {count} issues" for priority, count in priority_dist.items()])}

Epic Assignment:
- Issues with Epics: {epic_assignment.get('issues_with_epics', 0)} ({epic_assignment.get('epic_assignment_percentage', 0):.1f}%)
- Orphaned Issues: {epic_assignment.get('orphaned_issues', 0)}
- Unique Epics: {epic_assignment.get('unique_epics', 0)}

Based on this data, provide insights about the backlog health and specific recommendations for improvement."""
    
    @staticmethod
    def create_hygiene_recommendations_prompt(hygiene_data: Dict[str, Any]) -> str:
        """
        Create the hygiene recommendations prompt.
        
        Args:
            hygiene_data (dict): Hygiene analysis data
            
        Returns:
            str: Formatted prompt for AI
        """
        total_issues = hygiene_data.get('total_issues', 0)
        hygiene_score = hygiene_data.get('hygiene_score', 0)
        completeness = hygiene_data.get('completeness', {})
        age_distribution = hygiene_data.get('age_distribution', {})
        
        completeness_percentages = completeness.get('percentages', {})
        age_dist = age_distribution.get('distribution', {})
        
        return f"""Backlog Hygiene Summary:
- Total Issues: {total_issues}
- Overall Hygiene Score: {hygiene_score}%
- Description Completion: {completeness_percentages.get('has_description_percentage', 0):.1f}%
- Epic Assignment: {completeness_percentages.get('has_epic_percentage', 0):.1f}%
- Old Issues (90+ days): {age_dist.get('91-180_days', 0) + age_dist.get('180+_days', 0)}

Provide a brief summary of the team's backlog health and exactly 2 actionable recommendations."""
    
    @staticmethod
    def create_issue_description_prompt(issue_title: str, issue_type: str = "Story") -> str:
        """
        Create prompt for issue description suggestions.
        
        Args:
            issue_title (str): The issue title
            issue_type (str): Type of issue (Story, Task, Bug, etc.)
            
        Returns:
            str: Formatted prompt for AI
        """
        return f"""Based on this {issue_type} title: "{issue_title}"

Suggest what should be included in the description to make this issue complete and actionable. Provide specific suggestions for:
1. User story or context
2. Acceptance criteria
3. Technical considerations (if applicable)

Keep suggestions concise and practical."""
    
    @staticmethod
    def create_quality_analysis_prompt(issues: List[Dict[str, Any]]) -> str:
        """
        Create prompt for issue quality analysis.
        
        Args:
            issues (list): List of issue dictionaries
            
        Returns:
            str: Formatted prompt for AI
        """
        if not issues:
            return "No issues to analyze."
        
        issue_summaries = []
        for i, issue in enumerate(issues[:10], 1):  # Limit to first 10 issues
            summary = issue.get('summary', 'No summary')
            description = issue.get('description', 'No description')
            epic = issue.get('epic_name', 'No epic')
            priority = issue.get('priority', 'No priority')
            
            issue_summaries.append(f"""Issue {i}:
- Summary: {summary}
- Description: {description[:200]}{'...' if len(description) > 200 else ''}
- Epic: {epic}
- Priority: {priority}""")
        
        return f"""Analyze the quality of these {len(issues)} issues:

{chr(10).join(issue_summaries)}

Provide insights about:
1. Overall issue quality
2. Common patterns or issues
3. Specific areas for improvement
4. Recommendations for better issue management"""
    
    @staticmethod
    def get_fallback_insights_template() -> str:
        """
        Get template for fallback hygiene insights.
        
        Returns:
            str: Fallback insights template
        """
        return """The backlog shows {status} hygiene with a score of {hygiene_score}%. 

Key observations:
- {description_percentage:.1f}% of issues have descriptions
- {epic_percentage:.1f}% of issues are assigned to epics
- Total backlog size: {total_issues} issues

Recommendation: {recommendation}"""
    
    @staticmethod
    def get_fallback_recommendations_template() -> str:
        """
        Get template for fallback hygiene recommendations.
        
        Returns:
            str: Fallback recommendations template
        """
        return """{summary}

Action items:
1. {action1}
2. {action2}""" 