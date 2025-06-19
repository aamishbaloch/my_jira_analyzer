"""
Command-line interface for sprint analysis.
"""

import argparse
import sys
from datetime import datetime
from typing import Optional

from ..analyzers.sprint_analyzer import SprintAnalyzer
from ..core.config import Config
from ..core.utils import (
    export_to_csv, export_to_json, print_table, 
    get_month_name, validate_month
)


class SprintCLI:
    """
    Command-line interface for sprint analysis.
    """
    
    def __init__(self):
        self.analyzer = None
        
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
            # Initialize analyzer with config
            self.analyzer = SprintAnalyzer(parsed_args.config)
            
            # Handle different commands
            if parsed_args.command == 'analyze':
                return self._handle_analyze(parsed_args)
            elif parsed_args.command == 'active':
                return self._handle_active(parsed_args)
            elif parsed_args.command == 'test':
                return self._handle_test(parsed_args)
            elif parsed_args.command == 'config':
                return self._handle_config(parsed_args)
            elif parsed_args.command == 'average':
                return self._handle_average(parsed_args)
            else:
                parser.print_help()
                return 1
                
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="Jira Sprint Analysis Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Analyze last 4 sprints
  %(prog)s analyze --last-sprints 4
  
  # Analyze sprints closed in June
  %(prog)s analyze --month 6
  
  # Analyze a specific sprint by name
  %(prog)s analyze --sprint-name "Sprint 42"
  
  # Export results to CSV
  %(prog)s analyze --month 6 --export results.csv
  
  # View active sprints
  %(prog)s active
  
  # Get average completion rate of last 4 sprints  
  %(prog)s average
  
  # Test connection
  %(prog)s test
  
  # Create sample config
  %(prog)s config --create-sample
            """
        )
        
        parser.add_argument(
            '--config', '-c',
            default='config.json',
            help='Configuration file path (default: config.json)'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze sprint completion rates')
        analyze_group = analyze_parser.add_mutually_exclusive_group(required=True)
        analyze_group.add_argument(
            '--month', '-m',
            type=int,
            choices=range(1, 13),
            help='Analyze sprints closed in specific month (1-12)'
        )
        analyze_group.add_argument(
            '--last-sprints', '-l',
            type=int,
            help='Analyze last X closed sprints'
        )
        analyze_group.add_argument(
            '--sprint-name', '-n',
            type=str,
            help='Analyze a specific sprint by name'
        )
        analyze_parser.add_argument(
            '--export', '-e',
            help='Export results to file (CSV or JSON based on extension)'
        )
        analyze_parser.add_argument(
            '--details', '-d',
            action='store_true',
            help='Show detailed task information'
        )
        
        # Active sprints command
        active_parser = subparsers.add_parser('active', help='Show active sprints summary')
        active_parser.add_argument(
            '--export', '-e',
            help='Export results to file'
        )
        
        # Average completion rate command
        subparsers.add_parser('average', help='Get average completion rate of last 4 closed sprints')
        
        # Test command
        subparsers.add_parser('test', help='Test Jira connection')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_parser.add_argument(
            '--create-sample',
            action='store_true',
            help='Create sample configuration file'
        )
        
        return parser
    
    def _handle_analyze(self, args) -> int:
        """Handle analyze command."""
        print("🔍 Analyzing sprint completion rates...")
        
        try:
            # Perform analysis
            if args.month:
                print(f"📅 Analyzing sprints closed in {get_month_name(args.month)}")
                results = self.analyzer.calculate_sprints_by_month(args.month)
            elif args.sprint_name:
                print(f"🎯 Analyzing sprint: {args.sprint_name}")
                results = self.analyzer.analyze_sprint_by_name(args.sprint_name)
            else:
                print(f"📈 Analyzing last {args.last_sprints} closed sprints")
                results = self.analyzer.calculate_last_x_sprints(args.last_sprints)
            
            # Display results
            self._display_analysis_results(results, args.details)
            
            # Export if requested
            if args.export:
                self._export_results(results, args.export)
            
            return 0
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return 1
    
    def _handle_active(self, args) -> int:
        """Handle active sprints command."""
        print("🏃 Getting active sprints summary...")
        
        try:
            results = self.analyzer.get_active_sprints_summary()
            self._display_active_sprints(results)
            
            if args.export:
                self._export_results(results, args.export)
            
            return 0
            
        except Exception as e:
            print(f"❌ Failed to get active sprints: {e}")
            return 1
    
    def _handle_test(self, args) -> int:
        """Handle test connection command."""
        print("🔗 Testing Jira connection...")
        
        try:
            result = self.analyzer.jira_client.test_connection()
            
            if result['status'] == 'success':
                print("✅ Connection successful!")
                print(f"   Server: {result['server']}")
                print(f"   User: {result['user']}")
                
                project_info = result['project']
                if 'error' not in project_info:
                    print(f"   Project: {project_info['name']} ({project_info['key']})")
                    print(f"   Lead: {project_info['lead']}")
                else:
                    print(f"   Project: {project_info['error']}")
                
                return 0
            else:
                print(f"❌ Connection failed: {result['error']}")
                return 1
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return 1
    
    def _handle_config(self, args) -> int:
        """Handle config command."""
        if args.create_sample:
            try:
                Config.create_sample_config()
                return 0
            except Exception as e:
                print(f"❌ Failed to create sample config: {e}")
                return 1
        else:
            print("Use --create-sample to create a sample configuration file")
            return 1
    
    def _handle_average(self, args) -> int:
        """Handle average command."""
        print("📈 Getting average completion rate of last 4 sprints...")
        
        try:
            results = self.analyzer.get_average_completion_rate_last_4_sprints()
            self._display_average_completion_rate(results)
            
            return 0
            
        except Exception as e:
            print(f"❌ Failed to get average completion rate: {e}")
            return 1
    
    def _display_analysis_results(self, results: dict, show_details: bool = False):
        """Display analysis results in a formatted way."""
        print("\n" + "="*60)
        print("📊 SPRINT COMPLETION ANALYSIS RESULTS")
        print("="*60)
        
        # Handle sprint-by-name results (single sprint)
        if results.get('analysis_type') == 'sprint_by_name':
            if not results.get('found'):
                print(f"\n❌ {results.get('error', 'Sprint not found')}")
                return
            
            print(f"\n🎯 Sprint: {results['sprint_name']}")
            print(f"   ID: {results.get('sprint_id', 'N/A')}")
            print(f"   State: {results.get('sprint_state', 'unknown')}")
            print(f"   Start Date: {results.get('start_date', 'N/A')}")
            print(f"   End Date: {results.get('end_date', 'N/A')}")
            print(f"   Total Tasks: {results['total_tasks']}")
            print(f"   Completed Within Sprint: {results['completed_within_sprint']}")
            print(f"   Completion Rate: {results['completion_rate']:.1f}%")
            
            # Show task details if requested
            if show_details:
                self._display_sprint_task_details(results)
                
            return
        
        # Summary statistics (for multiple sprints)
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Tasks: {results['total_tasks']}")
        print(f"   Completed Within Sprint: {results['total_completed']}")
        print(f"   Average Completion Rate: {results['average_completion_rate']:.1f}%")
        print(f"   Best Sprint Rate: {results['best_sprint_rate']:.1f}%")
        print(f"   Worst Sprint Rate: {results['worst_sprint_rate']:.1f}%")
        
        # Sprint details table
        if results['sprint_results']:
            headers = ['Sprint Name', 'End Date', 'Total Tasks', 'Completed', 'Rate (%)']
            rows = []
            
            for sprint in results['sprint_results']:
                end_date = datetime.fromisoformat(sprint['end_date'].replace('Z', '+00:00'))
                rows.append([
                    sprint['sprint_name'][:30] + ('...' if len(sprint['sprint_name']) > 30 else ''),
                    end_date.strftime('%Y-%m-%d'),
                    str(sprint['total_tasks']),
                    str(sprint['completed_within_sprint']),
                    f"{sprint['completion_rate']:.1f}%"
                ])
            
            print_table(headers, rows, "\n🏃 Sprint Details")
            
            # Show task details if requested
            if show_details:
                for sprint in results['sprint_results']:
                    self._display_sprint_task_details(sprint)
    
    def _display_sprint_task_details(self, sprint_result: dict):
        """Display detailed task information for a sprint."""
        print(f"\n📋 Task Details for: {sprint_result['sprint_name']}")
        print("-" * 50)
        
        # Handle both formats: tasks_details (multiple sprints) and tasks (single sprint)
        task_list = sprint_result.get('tasks_details') or sprint_result.get('tasks', [])
        
        if not task_list:
            print("No tasks found in this sprint")
            return
        
        headers = ['Task Key', 'Summary', 'Status', 'Completed in Sprint', 'Done Date']
        rows = []
        
        for task in task_list:
            # Handle different field names between formats
            task_key = task.get('key', 'N/A')
            task_summary = task.get('summary', 'N/A')[:40] + ('...' if len(task.get('summary', '')) > 40 else '')
            task_status = task.get('current_status') or task.get('status', 'N/A')
            completed_within = task.get('completed_within_sprint', False)
            
            # Handle date field variations
            done_date_str = 'Not completed'
            completion_date = task.get('completion_date') or task.get('done_date')
            if completion_date:
                if isinstance(completion_date, str):
                    done_date_str = completion_date
                else:
                    done_date_str = completion_date.strftime('%Y-%m-%d')
            
            rows.append([
                task_key,
                task_summary,
                task_status,
                '✅' if completed_within else '❌',
                done_date_str
            ])
        
        print_table(headers, rows)
    
    def _display_active_sprints(self, results: dict):
        """Display active sprints information."""
        print("\n" + "="*50)
        print("🏃 ACTIVE SPRINTS SUMMARY")
        print("="*50)
        
        print(f"\nActive Sprint Count: {results['active_sprint_count']}")
        
        if results['sprints']:
            headers = ['Sprint Name', 'Start Date', 'End Date', 'Total Issues', 'Done', 'Current Rate (%)']
            rows = []
            
            for sprint in results['sprints']:
                start_date = datetime.fromisoformat(sprint['start_date'].replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(sprint['end_date'].replace('Z', '+00:00'))
                
                rows.append([
                    sprint['name'][:25] + ('...' if len(sprint['name']) > 25 else ''),
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d'),
                    str(sprint['total_issues']),
                    str(sprint['done_issues']),
                    f"{sprint['current_completion_rate']:.1f}%"
                ])
            
            print_table(headers, rows)
        else:
            print("No active sprints found")
    
    def _export_results(self, results: dict, filename: str):
        """Export results to file."""
        try:
            if filename.lower().endswith('.csv'):
                # Flatten sprint results for CSV export
                if 'sprint_results' in results:
                    csv_data = []
                    for sprint in results['sprint_results']:
                        csv_data.append({
                            'sprint_name': sprint['sprint_name'],
                            'end_date': sprint['end_date'],
                            'total_tasks': sprint['total_tasks'],
                            'completed_within_sprint': sprint['completed_within_sprint'],
                            'completion_rate': sprint['completion_rate']
                        })
                    export_to_csv(csv_data, filename)
                else:
                    # For active sprints
                    export_to_csv(results.get('sprints', []), filename)
            else:
                # Export as JSON
                export_to_json(results, filename)
                
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def _display_average_completion_rate(self, results: dict):
        """Display average completion rate results."""
        print("\n" + "="*50)
        print("📈 AVERAGE COMPLETION RATE - LAST 4 SPRINTS")
        print("="*50)
        
        if 'error' in results:
            print(f"\n❌ {results['error']}")
            return
        
        print(f"\n{results['message']}")
        
        if results['sprint_rates']:
            print(f"\n📊 Individual Sprint Rates:")
            
            headers = ['Sprint Name', 'Total Tasks', 'Completed', 'Rate (%)']
            rows = []
            
            for sprint in results['sprint_rates']:
                rows.append([
                    sprint['name'][:35] + ('...' if len(sprint['name']) > 35 else ''),
                    str(sprint['total_tasks']),
                    str(sprint['completed_tasks']),
                    f"{sprint['completion_rate']:.1f}%"
                ])
            
            print_table(headers, rows)
            
            print(f"\n🎯 Key Metrics:")
            print(f"   • Sprints Analyzed: {results['sprints_analyzed']}")
            print(f"   • Average Completion Rate: {results['average_completion_rate']}%")
            
            if results['sprint_rates']:
                best_sprint = max(results['sprint_rates'], key=lambda x: x['completion_rate'])
                worst_sprint = min(results['sprint_rates'], key=lambda x: x['completion_rate'])
                
                print(f"   • Best Sprint: {best_sprint['name']} ({best_sprint['completion_rate']:.1f}%)")
                print(f"   • Worst Sprint: {worst_sprint['name']} ({worst_sprint['completion_rate']:.1f}%)")
        else:
            print(f"\nNo sprint data available for analysis.")


def main():
    """Main entry point for the CLI."""
    cli = SprintCLI()
    sys.exit(cli.run()) 