"""
Main command-line interface for Jira Tools.
"""

import argparse
import sys
from typing import Optional

from .sprint_cli import SprintCLI
from .publish_cli import PublishCLI
from ..core.config import Config


class MainCLI:
    """
    Main command-line interface for all Jira tools.
    """
    
    def run(self, args: Optional[list] = None) -> int:
        """
        Run the main CLI with given arguments.
        
        Args:
            args: Command line arguments (uses sys.argv if None)
            
        Returns:
            int: Exit code
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        
        try:
            # Handle different tools
            if parsed_args.tool == 'sprint':
                sprint_cli = SprintCLI()
                # Pass the remaining args to the sprint CLI
                sprint_args = self._build_sprint_args(parsed_args)
                return sprint_cli.run(sprint_args)
            elif parsed_args.tool == 'publish':
                publish_cli = PublishCLI()
                # Pass the remaining args to the publish CLI
                publish_args = self._build_publish_args(parsed_args)
                return publish_cli.run(publish_args)
            elif parsed_args.tool == 'config':
                return self._handle_config(parsed_args)
            elif parsed_args.tool == 'info':
                return self._handle_info(parsed_args)
            else:
                parser.print_help()
                return 1
                
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create main argument parser."""
        parser = argparse.ArgumentParser(
            description="Jira Tools - Comprehensive Jira Analysis Suite",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Available Tools:
  sprint    Sprint completion analysis
  publish   Publish results to Confluence, Slack, etc.
  config    Configuration management
  info      Project and connection information

Examples:
  # Sprint analysis
  %(prog)s sprint analyze --month 6
  %(prog)s sprint analyze --last-sprints 4 --details
  %(prog)s sprint analyze --sprint-name "Sprint 42"
  %(prog)s sprint active
  
  # Publishing
  %(prog)s publish confluence --month 6 --space TEAM
  %(prog)s publish confluence --active --space DEV
  
  # Configuration
  %(prog)s config --create-sample
  %(prog)s config --test
  
  # Project info
  %(prog)s info
            """
        )
        
        parser.add_argument(
            '--version', '-v',
            action='version',
            version='Jira Tools 1.0.0'
        )
        
        parser.add_argument(
            '--config', '-c',
            default='config.json',
            help='Configuration file path (default: config.json)'
        )
        
        subparsers = parser.add_subparsers(dest='tool', help='Available tools')
        
        # Sprint tool
        sprint_parser = subparsers.add_parser('sprint', help='Sprint analysis tools')
        sprint_subparsers = sprint_parser.add_subparsers(dest='sprint_command')
        
        # Sprint analyze
        analyze_parser = sprint_subparsers.add_parser('analyze', help='Analyze sprint completion rates')
        analyze_group = analyze_parser.add_mutually_exclusive_group(required=True)
        analyze_group.add_argument('--month', '-m', type=int, choices=range(1, 13))
        analyze_group.add_argument('--last-sprints', '-l', type=int)
        analyze_group.add_argument('--sprint-name', '-n', type=str, help='Analyze specific sprint by name')
        analyze_parser.add_argument('--export', '-e', help='Export results to file')
        analyze_parser.add_argument('--details', '-d', action='store_true')
        
        # Sprint active
        active_parser = sprint_subparsers.add_parser('active', help='Show active sprints')
        active_parser.add_argument('--export', '-e', help='Export results to file')
        
        # Sprint average
        sprint_subparsers.add_parser('average', help='Get average completion rate of last 4 sprints')
        
        # Sprint test
        sprint_subparsers.add_parser('test', help='Test Jira connection')
        
        # Publish tool
        publish_parser = subparsers.add_parser('publish', help='Publish analysis results')
        publish_subparsers = publish_parser.add_subparsers(dest='publish_command')
        
        # Publish confluence
        confluence_parser = publish_subparsers.add_parser('confluence', help='Publish to Confluence')
        confluence_parser.add_argument('--sprint-name', '-n', type=str, required=True, help='Sprint name to analyze and publish')
        confluence_parser.add_argument('--space', '-s', required=True, help='Confluence space key')
        confluence_parser.add_argument('--title', '-t', help='Page title')
        confluence_parser.add_argument('--parent', '-p', help='Parent page title')
        
        # Publish test
        publish_subparsers.add_parser('test', help='Test publishing connections')
        
        # Config tool
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_group = config_parser.add_mutually_exclusive_group(required=True)
        config_group.add_argument('--create-sample', action='store_true', help='Create sample config')
        config_group.add_argument('--test', action='store_true', help='Test configuration')
        config_group.add_argument('--validate', action='store_true', help='Validate configuration')
        
        # Info tool
        subparsers.add_parser('info', help='Show project and connection information')
        
        return parser
    
    def _build_sprint_args(self, parsed_args) -> list:
        """Build arguments for sprint CLI."""
        args = ['--config', parsed_args.config]
        
        if hasattr(parsed_args, 'sprint_command') and parsed_args.sprint_command:
            args.append(parsed_args.sprint_command)
            
            if parsed_args.sprint_command == 'analyze':
                if hasattr(parsed_args, 'month') and parsed_args.month:
                    args.extend(['--month', str(parsed_args.month)])
                elif hasattr(parsed_args, 'last_sprints') and parsed_args.last_sprints:
                    args.extend(['--last-sprints', str(parsed_args.last_sprints)])
                elif hasattr(parsed_args, 'sprint_name') and parsed_args.sprint_name:
                    args.extend(['--sprint-name', parsed_args.sprint_name])
                
                if hasattr(parsed_args, 'export') and parsed_args.export:
                    args.extend(['--export', parsed_args.export])
                
                if hasattr(parsed_args, 'details') and parsed_args.details:
                    args.append('--details')
            
            elif parsed_args.sprint_command == 'active':
                if hasattr(parsed_args, 'export') and parsed_args.export:
                    args.extend(['--export', parsed_args.export])
        
        return args
    
    def _build_publish_args(self, parsed_args) -> list:
        """Build arguments for publish CLI."""
        args = ['--config', parsed_args.config]
        
        if hasattr(parsed_args, 'publish_command') and parsed_args.publish_command:
            args.append(parsed_args.publish_command)
            
            if parsed_args.publish_command == 'confluence':
                if hasattr(parsed_args, 'sprint_name') and parsed_args.sprint_name:
                    args.extend(['--sprint-name', parsed_args.sprint_name])
                
                if hasattr(parsed_args, 'space') and parsed_args.space:
                    args.extend(['--space', parsed_args.space])
                
                if hasattr(parsed_args, 'title') and parsed_args.title:
                    args.extend(['--title', parsed_args.title])
                
                if hasattr(parsed_args, 'parent') and parsed_args.parent:
                    args.extend(['--parent', parsed_args.parent])
        
        return args
    
    def _handle_config(self, args) -> int:
        """Handle config commands."""
        try:
            if args.create_sample:
                Config.create_sample_config()
                print("✅ Sample configuration created successfully!")
                return 0
            elif args.test or args.validate:
                config = Config(args.config)
                print("✅ Configuration is valid!")
                
                if args.test:
                    # Test actual connection
                    from ..core.jira_client import JiraClient
                    client = JiraClient(config)
                    result = client.test_connection()
                    
                    if result['status'] == 'success':
                        print("✅ Jira connection test successful!")
                        return 0
                    else:
                        print(f"❌ Jira connection failed: {result['error']}")
                        return 1
                
                return 0
                
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return 1
    
    def _handle_info(self, args) -> int:
        """Handle info command."""
        try:
            from ..core.jira_client import JiraClient
            
            config = Config(args.config)
            client = JiraClient(config)
            
            print("\n" + "="*50)
            print("📋 JIRA PROJECT INFORMATION")
            print("="*50)
            
            # Test connection and get info
            result = client.test_connection()
            
            if result['status'] == 'success':
                print(f"\n🔗 Connection Status: ✅ Connected")
                print(f"   Server: {result['server']}")
                print(f"   User: {result['user']}")
                
                project_info = result['project']
                if 'error' not in project_info:
                    print(f"\n📊 Project Details:")
                    print(f"   Name: {project_info['name']}")
                    print(f"   Key: {project_info['key']}")
                    print(f"   Lead: {project_info['lead']}")
                    print(f"   Type: {project_info['project_type']}")
                    
                    if project_info.get('description'):
                        print(f"   Description: {project_info['description']}")
                
                # Get sprint summary
                try:
                    closed_sprints = client.get_all_closed_sprints()
                    active_sprints = client.get_active_sprints()
                    
                    print(f"\n🏃 Sprint Summary:")
                    print(f"   Total Closed Sprints: {len(closed_sprints)}")
                    print(f"   Active Sprints: {len(active_sprints)}")
                    
                    if closed_sprints:
                        latest_sprint = closed_sprints[0]
                        print(f"   Latest Closed Sprint: {latest_sprint.name}")
                        print(f"   Latest End Date: {latest_sprint.endDate}")
                        
                except Exception as e:
                    print(f"   Sprint info unavailable: {e}")
                
                return 0
            else:
                print(f"\n🔗 Connection Status: ❌ Failed")
                print(f"   Error: {result['error']}")
                return 1
                
        except Exception as e:
            print(f"❌ Failed to get project info: {e}")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = MainCLI()
    sys.exit(cli.run()) 