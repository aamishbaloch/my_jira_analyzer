#!/usr/bin/env python3
"""
Simple script to test Jira connectivity and list available projects
"""

from src.core.jira_client import JiraClient
from src.core.config import Config

def test_jira_connection():
    try:
        print("🔍 Testing Jira connection...")
        config = Config()
        jira = JiraClient(config)
        
        # Test authentication
        current_user = jira.jira.current_user()
        print(f"✅ Authentication successful! Current user: {current_user}")
        
        # Get all projects
        projects = jira.jira.projects()
        print(f"✅ Found {len(projects)} accessible projects")
        
        if projects:
            print("\n📋 Available projects:")
            for project in projects:
                print(f"  - {project.key}: {project.name}")
        else:
            print("❌ No projects accessible - check permissions")
            
        # Test basic search without sprint field
        if projects:
            first_project = projects[0].key
            print(f"\n🔍 Testing basic search in project {first_project}...")
            try:
                issues = jira.jira.search_issues(f'project = {first_project}', maxResults=5)
                print(f"✅ Found {len(issues)} issues in {first_project}")
                
                # Check if sprint field exists
                if issues:
                    first_issue = issues[0]
                    fields = first_issue.raw['fields']
                    sprint_fields = [key for key in fields.keys() if 'sprint' in key.lower()]
                    if sprint_fields:
                        print(f"✅ Sprint fields available: {sprint_fields}")
                    else:
                        print("❌ No sprint fields found - this might be why the backlog query fails")
                        
            except Exception as e:
                print(f"❌ Search failed: {e}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Possible solutions:")
        print("1. Check if your API token is valid and updated in config.json")
        print("2. Verify your username and Jira URL are correct")
        print("3. Ensure you have proper permissions to access Jira")

if __name__ == "__main__":
    test_jira_connection() 