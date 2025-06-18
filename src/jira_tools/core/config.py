"""
Configuration management for Jira Tools.
"""

import json
import os
from typing import Dict, Any, Optional


class Config:
    """
    Configuration manager for Jira Tools.
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize configuration.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file '{self.config_path}' not found. "
                "Please create it with your Jira credentials."
            )
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file '{self.config_path}': {e}")
    
    def _validate_config(self):
        """Validate that required configuration keys are present."""
        required_jira_keys = ['url', 'username', 'api_token', 'project_key']
        
        if 'jira' not in self.config:
            raise ValueError("Missing 'jira' section in configuration")
        
        jira_config = self.config['jira']
        missing_keys = [key for key in required_jira_keys if key not in jira_config]
        
        if missing_keys:
            raise ValueError(f"Missing required Jira configuration keys: {missing_keys}")
        
        # Validate that values are not empty
        empty_keys = [key for key in required_jira_keys if not jira_config[key]]
        if empty_keys:
            raise ValueError(f"Empty values for required Jira configuration keys: {empty_keys}")
    
    @property
    def jira_url(self) -> str:
        """Get Jira URL."""
        return self.config['jira']['url']
    
    @property
    def jira_username(self) -> str:
        """Get Jira username."""
        return self.config['jira']['username']
    
    @property
    def jira_api_token(self) -> str:
        """Get Jira API token."""
        return self.config['jira']['api_token']
    
    @property
    def project_key(self) -> str:
        """Get Jira project key."""
        return self.config['jira']['project_key']
    
    def get_setting(self, key: str, default: Any = None, section: str = 'settings') -> Any:
        """
        Get a setting value with optional default.
        
        Args:
            key (str): Setting key
            default: Default value if key not found
            section (str): Configuration section (default: 'settings')
            
        Returns:
            Setting value or default
        """
        return self.config.get(section, {}).get(key, default)
    
    def get_jira_config(self) -> Dict[str, str]:
        """
        Get complete Jira configuration.
        
        Returns:
            Dict containing Jira configuration
        """
        return self.config['jira'].copy()
    
    def get_analyzer_config(self, analyzer_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific analyzer.
        
        Args:
            analyzer_name (str): Name of the analyzer
            
        Returns:
            Dict containing analyzer configuration
        """
        return self.config.get('analyzers', {}).get(analyzer_name, {})
    
    @classmethod
    def create_sample_config(cls, output_path: str = 'config.json.example') -> None:
        """
        Create a sample configuration file.
        
        Args:
            output_path (str): Path where to save the sample config
        """
        sample_config = {
            "jira": {
                "url": "https://your-domain.atlassian.net",
                "username": "your-email@company.com",
                "api_token": "your-api-token-here",
                "project_key": "YOUR_PROJECT_KEY"
            },
            "analyzers": {
                "sprint": {
                    "analysis_mode": "month",
                    "target_month": 6,
                    "last_sprints_count": 4
                },
                "velocity": {
                    "lookback_sprints": 10,
                    "exclude_incomplete": True
                },
                "burndown": {
                    "active_sprint_only": True,
                    "include_scope_changes": False
                }
            },
            "export": {
                "default_format": "csv",
                "output_directory": "reports"
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        print(f"Sample configuration created at: {output_path}")
        print("Please copy it to 'config.json' and update with your credentials.") 