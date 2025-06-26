"""
Command-line interface for publishing analysis results to various platforms.
"""

import argparse
import sys
from datetime import datetime
from typing import Optional

from ..analyzers.sprint_analyzer import SprintAnalyzer
from ..publishers.confluence_publisher import ConfluencePublisher
from ..core.config import Config
from ..core.utils import get_month_name, validate_month


class PublishCLI:
    """
    Command-line interface for publishing analysis results.
    """
    
    def __init__(self):
        self.analyzer = None
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
            # Initialize components
            self.analyzer = SprintAnalyzer(parsed_args.config)
            self.confluence_publisher = ConfluencePublisher(parsed_args.config)
            
            # Handle different commands
            if parsed_args.command == 'confluence':
                return self._handle_confluence(parsed_args)
            elif parsed_args.command == 'backlog-hygiene':
                return self._handle_backlog_hygiene(parsed_args)
            elif parsed_args.command == 'ai-insights':
                return self._handle_ai_insights(parsed_args)
            elif parsed_args.command == 'test':
                return self._handle_test(parsed_args)
            elif parsed_args.command == 'spaces':
                return self._handle_spaces(parsed_args)
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
  # Publish sprint analysis by name
  %(prog)s confluence --sprint-name "Sprint 42"
  
  # Publish with custom title and parent page
  %(prog)s confluence --sprint-name "Slow Sloths (W25-W26)" --title "Custom Report Title" --parent "Sprint Reports"
  
  # Publish to specific space
  %(prog)s confluence --sprint-name "Sprint 42" --space DEV
  
  # Publish backlog hygiene analysis
  %(prog)s backlog-hygiene --space DEV
  
  # Publish backlog hygiene with custom parent
  %(prog)s backlog-hygiene --space DEV --parent "Backlog Reports" --title "Weekly Backlog Health Check"
  
  # Publish backlog hygiene with AI insights
  %(prog)s backlog-hygiene --space DEV --ai-enhanced
  
  # Publish dedicated AI insights report
  %(prog)s ai-insights --space DEV --parent "AI Reports"
  
  # Test Confluence connection
  %(prog)s test
  
  # List available spaces
  %(prog)s spaces
            """
        )
        
        parser.add_argument(
            '--config', '-c',
            default='config.json',
            help='Configuration file path (default: config.json)'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Confluence command for sprint analysis
        confluence_parser = subparsers.add_parser('confluence', help='Publish sprint analysis to Confluence')
        
        # Sprint selection (required)
        confluence_parser.add_argument(
            '--sprint-name', '-n',
            type=str,
            required=True,
            help='Sprint name to analyze and publish'
        )
        
        # Confluence-specific options
        confluence_parser.add_argument(
            '--space', '-s',
            help='Confluence space key (uses default from config if not specified)'
        )
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
        backlog_parser = subparsers.add_parser('backlog-hygiene', help='Publish backlog hygiene analysis to Confluence')
        
        # Confluence-specific options for backlog
        backlog_parser.add_argument(
            '--space', '-s',
            help='Confluence space key (uses default from config if not specified)'
        )
        backlog_parser.add_argument(
            '--title', '-t',
            default='Hygiene Analysis',
            help='Page title (default: "Analysis - W{week} {year}")'
        )
        backlog_parser.add_argument(
            '--parent', '-p',
            help='Parent page title'
        )
        backlog_parser.add_argument(
            '--ai-enhanced',
            action='store_true',
            help='Include enhanced AI insights and recommendations'
        )
        
        # AI insights command
        ai_insights_parser = subparsers.add_parser('ai-insights', help='Publish AI insights analysis to Confluence')
        
        # Confluence-specific options for AI insights
        ai_insights_parser.add_argument(
            '--space', '-s',
            help='Confluence space key (uses default from config if not specified)'
        )
        ai_insights_parser.add_argument(
            '--title', '-t',
            help='Page title (auto-generated if not provided)'
        )
        ai_insights_parser.add_argument(
            '--parent', '-p',
            help='Parent page title'
        )
        
        # Test command
        subparsers.add_parser('test', help='Test Confluence connection')
        
        # Spaces command
        subparsers.add_parser('spaces', help='List available Confluence spaces')
        
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
        
        # Get space and parent from config if not provided
        confluence_config = self.confluence_publisher.config.get_analyzer_config('confluence')
        space_key = args.space or confluence_config.get('default_space')
        parent_page = args.parent or confluence_config.get('default_sprint_completion_parent_page')
        
        if not space_key:
            print("❌ No space specified. Use --space parameter or set default_space in config.json")
            return 1
        
        # Perform sprint analysis
        results = self.analyzer.analyze_sprint_by_name(args.sprint_name)
        
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
        
        # Get space and parent from config if not provided
        confluence_config = self.confluence_publisher.config.get_analyzer_config('confluence')
        space_key = args.space or confluence_config.get('default_space')
        parent_page = args.parent or confluence_config.get('backlog_hygiene_parent_page')
        
        if not space_key:
            print("❌ No space specified. Use --space parameter or set default_space in config.json")
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
    
    def _handle_ai_insights(self, args) -> int:
        """Handle AI insights publishing command."""
        try:
            return self._publish_ai_insights_analysis(args)
                
        except Exception as e:
            print(f"❌ Publishing failed: {e}")
            return 1
    
    def _publish_ai_insights_analysis(self, args) -> int:
        """Publish AI insights analysis to Confluence."""
        print("🤖 Analyzing AI insights...")
        
        # Get space and parent from config if not provided
        confluence_config = self.confluence_publisher.config.get_analyzer_config('confluence')
        space_key = args.space or confluence_config.get('default_space')
        parent_page = args.parent or confluence_config.get('ai_insights_parent_page')
        
        if not space_key:
            print("❌ No space specified. Use --space parameter or set default_space in config.json")
            return 1
        
        # Use provided title if specified
        page_title = args.title or "AI Insights Analysis"
        
        print(f"📊 Analysis in progress...")
        print(f"📝 Publishing to Confluence space '{space_key}'...")
        print(f"   📄 Page title: '{page_title}'")
        if parent_page:
            print(f"   📁 Under parent page: '{parent_page}'")
        
        # Publish to Confluence (analysis happens inside the publisher)
        result = self.confluence_publisher.publish_ai_insights_analysis(
            space_key=space_key,
            page_title=page_title,
            parent_page_title=parent_page
        )
        
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
    
    def _handle_spaces(self, args) -> int:
        """Handle list spaces command."""
        print("📋 Listing available Confluence spaces...")
        
        try:
            result = self.confluence_publisher.list_available_spaces()
            
            if result['status'] == 'success':
                spaces = result['spaces']
                print(f"✅ Found {result['total_spaces']} accessible space(s):")
                print()
                
                if spaces:
                    print("Key        | Name                          | Type    | Status")
                    print("-" * 65)
                    for space in spaces:
                        key = space['key'][:10].ljust(10)
                        name = space['name'][:30].ljust(30)
                        space_type = space['type'][:7].ljust(7)
                        status = space['status']
                        print(f"{key} | {name} | {space_type} | {status}")
                    
                    print()
                    print("💡 Use any of these space keys with --space parameter")
                else:
                    print("❌ No spaces found or accessible")
                
                return 0
            else:
                print(f"❌ Failed to list spaces: {result['error']}")
                return 1
                
        except Exception as e:
            print(f"❌ Failed to list spaces: {e}")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = PublishCLI()
    sys.exit(cli.run()) 