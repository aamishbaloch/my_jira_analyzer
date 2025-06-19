"""
Jira Tools - Sprint Analysis Suite

A comprehensive Python package for analyzing Jira sprint completion rates 
and publishing results to various platforms with AI-powered insights.
"""

# Import main components
from .core.config import Config
from .core.jira_client import JiraClient
from .core.ai_summarizer import AISummarizer
from .analyzers.sprint_analyzer import SprintAnalyzer
from .publishers.confluence_publisher import ConfluencePublisher

__version__ = "1.0.0"

__all__ = [
    "Config",
    "JiraClient", 
    "AISummarizer",
    "SprintAnalyzer",
    "ConfluencePublisher",
] 