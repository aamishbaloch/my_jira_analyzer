"""
Shared Jira client for all tools.
"""

from jira import JIRA
from typing import List, Any, Optional
from datetime import datetime

from ..configs.config import Config


class JiraClient:
    """
    Shared Jira client with common functionality.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Jira client.
        
        Args:
            config (Config): Configuration object
        """
        self.config = config
        self.jira = self._connect()
    
    def _connect(self) -> JIRA:
        """Connect to Jira using configuration credentials."""
        try:
            return JIRA(
                server=self.config.jira_url,
                basic_auth=(self.config.jira_username, self.config.jira_api_token)
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Jira: {str(e)}")
    
    def get_all_closed_sprints(self) -> List[Any]:
        """Get all closed sprints for the project."""
        # Get all boards for the project
        boards = self.jira.boards(projectKeyOrID=self.config.project_key)
        if not boards:
            raise ValueError(f"No boards found for project {self.config.project_key}")
        
        all_sprints = []
        for board in boards:
            try:
                sprints = self.jira.sprints(board.id, state='closed')
                all_sprints.extend(sprints)
            except Exception as e:
                print(f"Warning: Could not fetch sprints for board {board.name}")
                continue
        
        if not all_sprints:
            raise ValueError(f"No closed sprints found for project {self.config.project_key}")
        
        # Sort sprints by end date (most recent first)
        all_sprints.sort(key=lambda x: datetime.fromisoformat(x.endDate.replace('Z', '+00:00')), reverse=True)
        
        return all_sprints
    
    def get_active_sprints(self) -> List[Any]:
        """Get all active sprints for the project."""
        boards = self.jira.boards(projectKeyOrID=self.config.project_key)
        if not boards:
            raise ValueError(f"No boards found for project {self.config.project_key}")
        
        all_sprints = []
        for board in boards:
            try:
                sprints = self.jira.sprints(board.id, state='active')
                all_sprints.extend(sprints)
            except Exception as e:
                print(f"Warning: Could not fetch active sprints for board {board.name}")
                continue
        
        return all_sprints
    
    def find_sprint_by_name(self, sprint_name: str) -> Optional[Any]:
        """
        Find a sprint by name (searches both active and closed sprints).
        
        Args:
            sprint_name (str): Name of the sprint to find
            
        Returns:
            Sprint object if found, None otherwise
        """
        boards = self.jira.boards(projectKeyOrID=self.config.project_key)
        if not boards:
            raise ValueError(f"No boards found for project {self.config.project_key}")
        
        # Search in all sprint states
        for board in boards:
            try:
                # Check active sprints first
                active_sprints = self.jira.sprints(board.id, state='active')
                for sprint in active_sprints:
                    if sprint.name.lower() == sprint_name.lower():
                        return sprint
                
                # Then check closed sprints
                closed_sprints = self.jira.sprints(board.id, state='closed')
                for sprint in closed_sprints:
                    if sprint.name.lower() == sprint_name.lower():
                        return sprint
                
                # Finally check future sprints
                future_sprints = self.jira.sprints(board.id, state='future')
                for sprint in future_sprints:
                    if sprint.name.lower() == sprint_name.lower():
                        return sprint
                        
            except Exception as e:
                print(f"Warning: Could not fetch sprints for board {board.name}")
                continue
        
        return None
    
    def get_sprint_issues(self, sprint_id: int, expand_changelog: bool = True) -> List[Any]:
        """
        Get all issues in a sprint.
        
        Args:
            sprint_id (int): Sprint ID
            expand_changelog (bool): Whether to expand changelog
            
        Returns:
            List of Jira issues
        """
        jql = f'project = {self.config.project_key} AND sprint = {sprint_id}'
        expand = "changelog" if expand_changelog else None
        return self.jira.search_issues(jql, maxResults=1000, expand=expand)
    
    def get_epic_info(self, epic_key: str) -> dict:
        """
        Get epic information.
        
        Args:
            epic_key (str): Epic key
            
        Returns:
            Dict with epic information
        """
        try:
            if not epic_key:
                return {'key': None, 'summary': 'No Epic'}
            
            epic = self.jira.issue(epic_key)
            return {
                'key': epic.key,
                'summary': epic.fields.summary
            }
        except Exception:
            return {'key': epic_key, 'summary': 'Epic not found'}

    def get_epic_for_issue(self, issue: Any) -> dict:
        """
        Get epic information for an issue.
        
        Args:
            issue: Jira issue object
            
        Returns:
            Dict with epic information
        """
        try:
            # Try different epic field names (depends on Jira setup)
            epic_key = None
            
            # Common epic field names
            if hasattr(issue.fields, 'parent') and issue.fields.parent:
                # Issue has a parent (could be epic)
                if issue.fields.parent.fields.issuetype.name == 'Epic':
                    epic_key = issue.fields.parent.key
            elif hasattr(issue.fields, 'epic') and issue.fields.epic:
                epic_key = issue.fields.epic.key
            elif hasattr(issue.fields, 'customfield_10011'):  # Common epic link field
                epic_key = getattr(issue.fields, 'customfield_10011', None)
            elif hasattr(issue.fields, 'customfield_10014'):  # Another common epic link field
                epic_key = getattr(issue.fields, 'customfield_10014', None)
            
            return self.get_epic_info(epic_key)
            
        except Exception:
            return {'key': None, 'summary': 'No Epic'}
    
    def get_issue_with_changelog(self, issue_key: str) -> Any:
        """
        Get a specific issue with changelog.
        
        Args:
            issue_key (str): Issue key
            
        Returns:
            Jira issue with changelog
        """
        return self.jira.issue(issue_key, expand="changelog")
    
    def search_issues(self, jql: str, max_results: int = 1000, **kwargs) -> List[Any]:
        """
        Search for issues using JQL.
        
        Args:
            jql (str): JQL query
            max_results (int): Maximum results to return
            **kwargs: Additional arguments for search_issues
            
        Returns:
            List of Jira issues
        """
        return self.jira.search_issues(jql, maxResults=max_results, **kwargs)
    
    def get_project_info(self) -> dict:
        """
        Get project information.
        
        Returns:
            Dict with project information
        """
        try:
            project = self.jira.project(self.config.project_key)
            return {
                'key': project.key,
                'name': project.name,
                'description': getattr(project, 'description', 'No description'),
                'lead': getattr(project.lead, 'displayName', 'Unknown'),
                'project_type': getattr(project, 'projectTypeKey', 'Unknown')
            }
        except Exception as e:
            return {'error': f"Could not fetch project info: {e}"}
    
    def test_connection(self) -> dict:
        """
        Test the Jira connection.
        
        Returns:
            Dict with connection status
        """
        try:
            # Try to get current user info
            current_user = self.jira.current_user()
            project_info = self.get_project_info()
            
            return {
                'status': 'success',
                'user': current_user,
                'project': project_info,
                'server': self.config.jira_url
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'server': self.config.jira_url
            } 