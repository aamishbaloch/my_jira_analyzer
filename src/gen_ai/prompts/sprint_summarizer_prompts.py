"""
Sprint analysis prompt templates for AI summarization.
"""

from typing import Dict, List, Any


class SprintSummarizerPrompts:
    """
    Prompt templates for sprint analysis and summarization.
    """
    
    @staticmethod
    def get_system_context() -> str:
        """
        Get the system context for sprint analysis.
        
        Returns:
            str: System context prompt
        """
        return """You are a technical program assistant that summarizes Jira sprint reports. Given a list of Jira tasks (including fields like title, summary, status, completion date, epic name, and epic description), generate the following:

1. Write one concise paragraph summarizing only the most meaningful achievements from the sprint. Focus on:
- What was completed that created real technical or business value.
- Use editorial judgment — do not include every task. Only mention impactful work, such as business requests, data enablement, CVA improvements, or technical enhancements.
- Group related work together to keep the summary clear and easy to read.
- Use the epic information to understand the broader context and group tasks by their strategic initiatives.
- Mention the key systems or services involved (e.g., customer-review-service, transactional communication service, dataset pipelines).
- Reference the type of work done — such as token invalidation, Kafka integration, dataset migration, CVA improvements, campaign fixes, or data snapshots.
- Clearly state the tech or business domain impacted (e.g., security, infrastructure, campaign automation, data accuracy, observability).
- Use plain, clear language without deep technical jargon.
- Do not include the highlight content in this paragraph.

2. After the paragraph, add a separate line starting with:

Highlight: [Describe the most valuable delivery. Mention which system or service was improved, what capability or benefit it unlocked, and why it matters to the platform, team, or business. Justify why this was selected as the highlight.]

Do not use markdown or rich text formatting. Output must be plain text, suitable for pasting directly into Confluence.

"""
    
    @staticmethod
    def create_achievement_prompt(sprint_data: Dict[str, Any], task_summaries: List[str], common_themes: str) -> str:
        """
        Create the main achievement prompt for sprint analysis.
        
        Args:
            sprint_data (dict): Sprint analysis data
            task_summaries (list): List of task summaries
            common_themes (str): Common themes extracted from tasks
            
        Returns:
            str: Formatted prompt for AI
        """
        sprint_name = sprint_data.get('sprint_name', 'Unknown Sprint')
        completion_rate = sprint_data.get('completion_rate', 0)
        total_tasks = sprint_data.get('total_tasks', 0)
        completed_tasks = sprint_data.get('completed_within_sprint', 0)
        
        if not task_summaries:
            return f"""Sprint: {sprint_name}
Completion Rate: {completion_rate:.1f}% ({completed_tasks}/{total_tasks} tasks)

No tasks were completed within this sprint. Provide a brief summary of the sprint status and any challenges faced."""
        
        return f"""Sprint: {sprint_name}
Completion Rate: {completion_rate:.1f}% ({completed_tasks}/{total_tasks} tasks)
Themes: {common_themes}

Completed Tasks:
{chr(10).join(task_summaries)}

Analyze these completed tasks and provide a concise, outcome-focused summary with one impactful highlight."""
    
    @staticmethod
    def get_fallback_template() -> str:
        """
        Get template for fallback summary when AI is not available.
        
        Returns:
            str: Fallback summary template
        """
        return "In {sprint_name}, the team completed {completed_tasks} out of {total_tasks} tasks, achieving a {completion_rate:.1f}% completion rate. Key areas of focus included: {themes}." 