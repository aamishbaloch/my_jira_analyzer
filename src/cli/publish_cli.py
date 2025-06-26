"""
Command-line interface for publishing analysis results to various platforms.
"""

import argparse
import sys
from datetime import datetime
from typing import Optional

from ..publishers.confluence_publisher import ConfluencePublisher
from ..configs.config import Config
from ..utils.utils import get_month_name, validate_month


class PublishCLI:
    """
    Command-line interface for publishing analysis results.
    """
    
    def __init__(self):
        self.confluence_publisher = None
        
    def run(self, args: Optional[list] = None) -> int:
        """
        Run the CLI with given arguments.
        
        Args:
            args: Command line arguments (uses sys.argv if None)
            
        Returns:
            int: Exit code
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        
        try:
            # Determine config path based on command
            config_path = 'src/configs/config.json'  # Default for backlog hygiene
            if hasattr(parsed_args, 'config'):
                config_path = parsed_args.config
            
            # Initialize components
            self.confluence_publisher = ConfluencePublisher(config_path)
            
            # Handle different commands
            if parsed_args.command == 'publish_sprint_review':
                return self._handle_confluence(parsed_args)
            elif parsed_args.command == 'publish_backlog_hygiene':
                return self._handle_backlog_hygiene(parsed_args)
            elif parsed_args.command == 'test':
                return self._handle_test(parsed_args)
            else:
                parser.print_help()
                return 1
                
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="Jira Analysis Publisher",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Publish sprint review by name
  %(prog)s publish_sprint_review --sprint-name "Sprint 42"
  
  # Publish with custom title and parent page
  %(prog)s publish_sprint_review --sprint-name "Slow Sloths (W25-W26)" --title "Custom Report Title" --parent "Sprint Reports"
  
  # Publish backlog hygiene analysis
  %(prog)s publish_backlog_hygiene
  
  # Publish backlog hygiene with custom title
  %(prog)s publish_backlog_hygiene --title "Weekly Backlog Health Check"
  

  
  # Test Confluence connection
  %(prog)s test
            """
        )
        
        parser.add_argument(
            '--config', '-c',
            default='src/configs/config.json',
            help='Configuration file path (default: src/configs/config.json)'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Sprint review command for sprint analysis
        confluence_parser = subparsers.add_parser('publish_sprint_review', help='Publish sprint review/completion analysis to Confluence')
        
        # Sprint selection (required)
        confluence_parser.add_argument(
            '--sprint-name', '-n',
            type=str,
            required=True,
            help='Sprint name to analyze and publish'
        )
        
        # Confluence-specific options (space is read from config)
        confluence_parser.add_argument(
            '--title', '-t',
            help='Page title (auto-generated if not provided)'
        )
        confluence_parser.add_argument(
            '--parent', '-p',
            help='Parent page title'
        )
        confluence_parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing page if found (default: create new or update)'
        )
        
        # Backlog hygiene command
        backlog_parser = subparsers.add_parser('publish_backlog_hygiene', help='Publish backlog hygiene analysis to Confluence')
        
        # Confluence-specific options for backlog (space and parent are read from config)
        backlog_parser.add_argument(
            '--title', '-t',
            default='Hygiene Analysis',
            help='Page title (default: "Analysis - W{week} {year}")'
        )
        
        # Test command
        subparsers.add_parser('test', help='Test Confluence connection')
        
        return parser
    
    def _handle_confluence(self, args) -> int:
        """Handle Confluence publishing command."""
        try:
            return self._publish_sprint_analysis(args)
                
        except Exception as e:
            print(f"❌ Publishing failed: {e}")
            return 1
    
    def _publish_sprint_analysis(self, args) -> int:
        """Publish single sprint analysis to Confluence."""
        print(f"🎯 Analyzing sprint: {args.sprint_name}")
        
        # Get space and parent from config
        confluence_config = self.confluence_publisher.config.get_analyzer_config('confluence')
        space_key = confluence_config.get('space')
        parent_page = args.parent or confluence_config.get('sprint_completion_parent_page')
        
        if not space_key:
            print("❌ No space configured. Please set 'space' in config.json under 'confluence' section")
            return 1
        
        # Perform sprint analysis
        results = self.confluence_publisher.sprint_analyzer.analyze_sprint_by_name(args.sprint_name)
        
        # Check if sprint was found
        if not results.get('found', False):
            print(f"❌ Sprint '{args.sprint_name}' not found: {results.get('error', 'Unknown error')}")
            return 1
        
        # Use sprint name as page title (use provided title only if specified)
        page_title = args.title or results['sprint_name']
        
        completion_rate = results.get('completion_rate', 0)
        print(f"📊 Analysis complete: {completion_rate:.1f}% completion rate")
        print(f"📝 Publishing to Confluence space '{space_key}'...")
        print(f"   📄 Page title: '{page_title}'")
        if parent_page:
            print(f"   📁 Under parent page: '{parent_page}'")
        
        # Publish to Confluence
        result = self.confluence_publisher.publish_sprint_analysis(
            analysis_results=results,
            space_key=space_key,
            page_title=page_title,
            parent_page_title=parent_page
        )
        
        print(f"✅ {result['action'].title()} Confluence page successfully!")
        print(f"   📄 Page: {result['title']}")
        print(f"   🔗 URL: {result['page_url']}")
        print(f"   📁 Space: {result['space']}")
        
        return 0
    
    def _handle_backlog_hygiene(self, args) -> int:
        """Handle backlog hygiene publishing command."""
        try:
            return self._publish_backlog_hygiene_analysis(args)
                
        except Exception as e:
            print(f"❌ Publishing failed: {e}")
            return 1
    
    def _publish_backlog_hygiene_analysis(self, args) -> int:
        """Publish backlog hygiene analysis to Confluence."""
        print("🧹 Analyzing backlog hygiene...")
        
        # Get space and parent from config
        confluence_config = self.confluence_publisher.config.get_analyzer_config('confluence')
        space_key = confluence_config.get('space')
        parent_page = confluence_config.get('backlog_hygiene_parent_page')
        
        if not space_key:
            print("❌ No space configured. Please set 'space' in config.json under 'confluence' section")
            return 1
        
        # Generate week-based title if using default
        if args.title == 'Hygiene Analysis':
            # Get current week number and year
            now = datetime.now()
            year = now.year
            week_number = now.isocalendar()[1]  # ISO week number
            page_title = f"Analysis - W{week_number:02d} {year}"
        else:
            page_title = args.title
        
        print(f"📊 Analysis in progress...")
        print(f"📝 Publishing to Confluence space '{space_key}'...")
        print(f"   📄 Page title: '{page_title}'")
        if parent_page:
            print(f"   📁 Under parent page: '{parent_page}'")
        
        # Publish to Confluence (analysis happens inside the publisher)
        result = self.confluence_publisher.publish_backlog_hygiene_analysis(
            space_key=space_key,
            page_title=page_title,
            parent_page_title=parent_page
        )
        
        # Show some key metrics from the analysis
        analysis_results = result.get('analysis_results', {})
        total_issues = analysis_results.get('total_issues', 0)
        hygiene_score = analysis_results.get('hygiene_score', 0)
        
        print(f"📊 Analysis complete:")
        print(f"   Total backlog issues: {total_issues}")
        print(f"   Hygiene score: {hygiene_score}%")
        
        print(f"✅ {result['action'].title()} Confluence page successfully!")
        print(f"   📄 Page: {result['title']}")
        print(f"   🔗 URL: {result['page_url']}")
        print(f"   📁 Space: {result['space']}")
        
        return 0
    
    def _handle_test(self, args) -> int:
        """Handle test connection command."""
        print("🔗 Testing Confluence connection...")
        
        try:
            result = self.confluence_publisher.test_connection()
            
            if result['status'] == 'success':
                print("✅ Confluence connection successful!")
                print(f"   Server: {result['confluence_url']}")
                print(f"   Message: {result['message']}")
                if 'spaces_accessible' in result:
                    print(f"   Spaces accessible: {'Yes' if result['spaces_accessible'] else 'No'}")
                return 0
            else:
                print(f"❌ Confluence connection failed: {result['error']}")
                return 1
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = PublishCLI()
    sys.exit(cli.run()) 