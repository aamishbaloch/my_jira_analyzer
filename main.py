#!/usr/bin/env python3
"""
Main entry point for Jira Publisher.

This script provides a command-line interface for publishing Jira analysis results
to Confluence and other platforms.
"""

import sys
import os

# Add src directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.publish_cli import main

if __name__ == "__main__":
    main()
