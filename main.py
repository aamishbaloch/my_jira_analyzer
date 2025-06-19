#!/usr/bin/env python3
"""
Main entry point for Jira Tools.

This script provides a simple interface to the Jira Tools package.
For more advanced usage, use the installed CLI commands:
- jira-tools: Main CLI with all tools
- jira-sprint: Sprint analysis CLI
"""

import sys
import os

# Add src directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.main_cli import main

if __name__ == "__main__":
    main()
