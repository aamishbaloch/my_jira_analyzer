#!/usr/bin/env python3
"""
Quick CLI script for Backlog Hygiene Analysis.

This provides a simple command-line interface for backlog hygiene analysis tasks.
"""

import sys
import os

# Add src directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.backlog_cli import main

if __name__ == "__main__":
    main() 