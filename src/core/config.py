"""
Configuration management for Jira Tools.
Supports both config.json files and environment variables (.env files).
"""

import json
import os
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class Config:
    """
    Configuration manager for Jira Tools.
    Supports loading from:
    1. Environment variables (including .env files)
    2. config.json file (fallback)
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize configuration.
        
        Args:
            config_path (str): Path to the configuration file (fallback)
        """
        self.config_path = config_path
        
        # Load .env file if available
        if DOTENV_AVAILABLE:
            load_dotenv()
        
        # Load configuration from environment variables first, then config file
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables first, then JSON file."""
        config = {}
        
        # Try to load from environment variables first
        env_config = self._load_from_env()
        if self._has_required_env_vars(env_config):
            print("✅ Using configuration from environment variables")
            return env_config
        
        # Fall back to config.json
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                print(f"✅ Using configuration from {self.config_path}")
                return config
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in configuration file '{self.config_path}': {e}")
        
        # If neither source is available, raise an error
        raise FileNotFoundError(
            f"No valid configuration found. Either:\n"
            f"1. Create a .env file with required variables, or\n"
            f"2. Create {self.config_path} with your configuration\n"
            f"Required environment variables: JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT_KEY"
        )
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "jira": {
                "url": os.getenv('JIRA_URL', ''),
                "username": os.getenv('JIRA_USERNAME', ''),
                "api_token": os.getenv('JIRA_API_TOKEN', ''),
                "project_key": os.getenv('JIRA_PROJECT_KEY', '')
            },
            "confluence": {
                "url": os.getenv('CONFLUENCE_URL', ''),
                "username": os.getenv('CONFLUENCE_USERNAME', ''),
                "api_token": os.getenv('CONFLUENCE_API_TOKEN', ''),
                "space": os.getenv('CONFLUENCE_DEFAULT_SPACE', '')
            },
            "ai": {
                "gemini_api_key": os.getenv('GEMINI_API_KEY', '')
            }
        }
    
    def _has_required_env_vars(self, config: Dict[str, Any]) -> bool:
        """Check if required environment variables are present and not empty."""
        jira_config = config.get('jira', {})
        required_keys = ['url', 'username', 'api_token', 'project_key']
        
        return all(
            jira_config.get(key) and jira_config.get(key).strip()
            for key in required_keys
        )
    
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
        Get configuration for a specific analyzer or service.
        
        Args:
            analyzer_name (str): Name of the analyzer or service (e.g., 'sprint', 'confluence', 'ai')
            
        Returns:
            Dict containing analyzer/service configuration
        """
        # First check if it's a top-level service config (like 'confluence', 'jira', 'ai')
        if analyzer_name in self.config:
            return self.config[analyzer_name].copy()
        
        # Then check in the analyzers section for backward compatibility
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
            "confluence": {
                "url": "https://your-domain.atlassian.net/wiki",
                "username": "your-email@company.com",
                "api_token": "your-confluence-api-token",
                "space": "YOUR_SPACE_KEY"
            },
            "ai": {
                "gemini_api_key": "your-gemini-api-key"
            },
            "analyzers": {
                "sprint": {
                    "analysis_mode": "month",
                    "target_month": 6,
                    "last_sprints_count": 4
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
        print("\nAlternatively, create a .env file with:")
        print("JIRA_URL=https://your-domain.atlassian.net")
        print("JIRA_USERNAME=your-email@company.com")
        print("JIRA_API_TOKEN=your-api-token")
        print("JIRA_PROJECT_KEY=YOUR_PROJECT")
        print("CONFLUENCE_URL=https://your-domain.atlassian.net/wiki")
        print("CONFLUENCE_USERNAME=your-email@company.com")
        print("CONFLUENCE_API_TOKEN=your-confluence-token")
        print("CONFLUENCE_DEFAULT_SPACE=YOUR_SPACE")
        print("GEMINI_API_KEY=your-gemini-key") 