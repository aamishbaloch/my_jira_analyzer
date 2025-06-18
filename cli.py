#!/usr/bin/env python3
"""
Quick CLI script for Jira Sprint Analysis.

This provides a simple command-line interface for common sprint analysis tasks.
"""

import sys
import os

# Add src directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.jira_tools.cli.sprint_cli import main

if __name__ == "__main__":
    main() 