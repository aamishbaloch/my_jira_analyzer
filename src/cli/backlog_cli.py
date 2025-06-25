"""
Command-line interface for backlog hygiene analysis.
"""

import argparse
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime

from ..analyzers.backlog_hygiene_analyzer import BacklogHygieneAnalyzer
from ..core.utils import export_to_csv, export_to_json


class BacklogCLI:
    """
    Command-line interface for backlog hygiene analysis.
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
            self.analyzer = BacklogHygieneAnalyzer(parsed_args.config)
            
            # Handle different commands
            if parsed_args.command == 'hygiene':
                return self._handle_hygiene(parsed_args)
            elif parsed_args.command == 'summary':
                return self._handle_summary(parsed_args)
            elif parsed_args.command == 'stale':
                return self._handle_stale(parsed_args)
            elif parsed_args.command == 'incomplete':
                return self._handle_incomplete(parsed_args)
            else:
                parser.print_help()
                return 1
                
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="Jira Backlog Hygiene Analysis Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Get comprehensive hygiene analysis
  %(prog)s hygiene
  
  # Get quick hygiene summary
  %(prog)s summary
  
  # Find stale issues (older than 90 days)
  %(prog)s stale
  
  # Find stale issues with custom threshold
  %(prog)s stale --days 60
  
  # Find incomplete issues
  %(prog)s incomplete
  
  # Export results to JSON
  %(prog)s hygiene --export results.json
            """
        )
        
        parser.add_argument(
            '--config', '-c',
            default='config.json',
            help='Configuration file path (default: config.json)'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Hygiene command (comprehensive analysis)
        hygiene_parser = subparsers.add_parser('hygiene', help='Comprehensive backlog hygiene analysis')
        hygiene_parser.add_argument(
            '--export', '-e',
            help='Export results to file (JSON format)'
        )
        
        # Summary command (quick overview)
        summary_parser = subparsers.add_parser('summary', help='Quick backlog hygiene summary')
        summary_parser.add_argument(
            '--export', '-e',
            help='Export results to file (JSON format)'
        )
        
        # Stale issues command
        stale_parser = subparsers.add_parser('stale', help='Find stale issues in backlog')
        stale_parser.add_argument(
            '--days', '-d',
            type=int,
            default=90,
            help='Days threshold for stale issues (default: 90)'
        )
        stale_parser.add_argument(
            '--export', '-e',
            help='Export results to file (JSON format)'
        )
        
        # Incomplete issues command
        incomplete_parser = subparsers.add_parser('incomplete', help='Find incomplete issues')
        incomplete_parser.add_argument(
            '--export', '-e',
            help='Export results to file (JSON format)'
        )
        
        return parser
    
    def _handle_hygiene(self, args) -> int:
        """Handle comprehensive hygiene analysis command."""
        print("🔍 Analyzing backlog hygiene...")
        
        try:
            results = self.analyzer.analyze_full_backlog_hygiene()
            self._display_hygiene_analysis(results)
            
            if args.export:
                self._export_results(results, args.export)
            
            return 0
            
        except Exception as e:
            print(f"❌ Hygiene analysis failed: {e}")
            return 1
    
    def _handle_summary(self, args) -> int:
        """Handle hygiene summary command."""
        print("📊 Getting backlog hygiene summary...")
        
        try:
            results = self.analyzer.get_hygiene_summary()
            self._display_hygiene_summary(results)
            
            if args.export:
                self._export_results(results, args.export)
            
            return 0
            
        except Exception as e:
            print(f"❌ Failed to get hygiene summary: {e}")
            return 1
    
    def _handle_stale(self, args) -> int:
        """Handle stale issues command."""
        print(f"🕰️  Finding stale issues (older than {args.days} days)...")
        
        try:
            results = self.analyzer.get_stale_issues(args.days)
            self._display_stale_issues(results)
            
            if args.export:
                self._export_results(results, args.export)
            
            return 0
            
        except Exception as e:
            print(f"❌ Failed to analyze stale issues: {e}")
            return 1
    
    def _handle_incomplete(self, args) -> int:
        """Handle incomplete issues command."""
        print("📝 Finding incomplete issues...")
        
        try:
            results = self.analyzer.get_incomplete_issues()
            self._display_incomplete_issues(results)
            
            if args.export:
                self._export_results(results, args.export)
            
            return 0
            
        except Exception as e:
            print(f"❌ Failed to analyze incomplete issues: {e}")
            return 1
    
    def _export_results(self, results: dict, filename: str):
        """Export results to file."""
        try:
            export_to_json(results, filename)
            print(f"✅ Results exported to {filename}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def _display_hygiene_analysis(self, result: Dict[str, Any]):
        """Display comprehensive hygiene analysis in table format."""
        print("\n" + "="*80)
        print("BACKLOG HYGIENE ANALYSIS")
        print("="*80)
        
        # Overall metrics
        print(f"\n📊 OVERALL METRICS")
        print(f"   Total Issues: {result['total_issues']}")
        print(f"   Hygiene Score: {result['hygiene_score']}%")
        
        # Color coding for hygiene score
        if result['hygiene_score'] >= 80:
            score_emoji = "🟢"
        elif result['hygiene_score'] >= 60:
            score_emoji = "🟡"
        else:
            score_emoji = "🔴"
        
        print(f"   Status: {score_emoji} {'Excellent' if result['hygiene_score'] >= 80 else 'Good' if result['hygiene_score'] >= 60 else 'Needs Improvement'}")
        
        # Completeness analysis
        completeness = result['completeness']
        print(f"\n📝 COMPLETENESS ANALYSIS")
        print(f"   Issues with descriptions: {completeness['counts']['has_description']} ({completeness['percentages']['has_description_percentage']:.1f}%)")
        print(f"   Issues with epics: {completeness['counts']['has_epic']} ({completeness['percentages']['has_epic_percentage']:.1f}%)")
        print(f"   Issues with priorities: {completeness['counts']['has_priority']} ({completeness['percentages']['has_priority_percentage']:.1f}%)")
        print(f"   Issues with story points: {completeness['counts']['has_story_points']} ({completeness['percentages']['has_story_points_percentage']:.1f}%)")
        print(f"   Fully complete issues: {completeness['counts']['fully_complete']} ({completeness['percentages']['fully_complete_percentage']:.1f}%)")
        
        # Age analysis
        age = result['age_distribution']
        print(f"\n📅 AGE DISTRIBUTION")
        print(f"   Average age: {age['average_age_days']} days")
        print(f"   Median age: {age['median_age_days']} days")
        print(f"   0-7 days: {age['distribution']['0-7_days']} issues")
        print(f"   8-30 days: {age['distribution']['8-30_days']} issues")
        print(f"   31-90 days: {age['distribution']['31-90_days']} issues")
        print(f"   91-180 days: {age['distribution']['91-180_days']} issues")
        print(f"   180+ days: {age['distribution']['180+_days']} issues")
        
        # Priority analysis
        priority = result['priority_distribution']
        print(f"\n🎯 PRIORITY DISTRIBUTION")
        for priority_name, count in priority['distribution'].items():
            print(f"   {priority_name}: {count} issues")
        
        # Epic analysis
        epic = result['epic_assignment']
        print(f"\n🎭 EPIC ASSIGNMENT")
        print(f"   Issues with epics: {epic['issues_with_epics']} ({epic['epic_assignment_percentage']:.1f}%)")
        print(f"   Orphaned issues: {epic['orphaned_issues']}")
        print(f"   Unique epics: {epic['unique_epics']}")
        
        # Recommendations
        if result['recommendations']:
            print(f"\n💡 RECOMMENDATIONS")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print(f"\nAnalysis completed at: {result['analysis_timestamp']}")

    def _display_hygiene_summary(self, result: Dict[str, Any]):
        """Display hygiene summary in table format."""
        print("\n" + "="*60)
        print("BACKLOG HYGIENE SUMMARY")
        print("="*60)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Color coding for hygiene score
        score = result['hygiene_score']
        if score >= 80:
            score_emoji = "🟢"
            status = "Excellent"
        elif score >= 60:
            score_emoji = "🟡"
            status = "Good"
        else:
            score_emoji = "🔴"
            status = "Needs Improvement"
        
        print(f"\n{score_emoji} Hygiene Score: {score}% ({status})")
        print(f"📦 Total Issues: {result['total_issues']}")
        print(f"📝 Issues with Descriptions: {result['issues_with_descriptions']} ({result['description_percentage']:.1f}%)")
        print(f"🎭 Issues with Epics: {result['issues_with_epics']} ({result['epic_assignment_percentage']:.1f}%)")
        print(f"📅 Average Age: {result['average_age_days']} days")
        
        print(f"\n{result['message']}")

    def _display_stale_issues(self, result: Dict[str, Any]):
        """Display stale issues in table format."""
        print("\n" + "="*80)
        print("STALE BACKLOG ISSUES")
        print("="*80)
        
        print(f"\nThreshold: {result['days_threshold']} days")
        print(f"Stale Issues: {result['stale_count']} out of {result['total_issues']} ({result['staleness_percentage']:.1f}%)")
        
        if result['stale_issues']:
            print(f"Oldest Issue: {result['oldest_issue_age']} days old")
            
            print(f"\n{'Key':<12} {'Age':<6} {'Priority':<10} {'Epic':<15} {'Summary'}")
            print("-" * 80)
            
            for issue in result['stale_issues'][:20]:  # Show top 20
                epic_key = issue['epic_key'] or 'No Epic'
                summary = issue['summary'][:30] + "..." if len(issue['summary']) > 30 else issue['summary']
                
                print(f"{issue['key']:<12} {issue['age_days']:<6} {issue['priority']:<10} {epic_key:<15} {summary}")
            
            if len(result['stale_issues']) > 20:
                print(f"\n... and {len(result['stale_issues']) - 20} more stale issues")
        else:
            print("\n🎉 No stale issues found!")

    def _display_incomplete_issues(self, result: Dict[str, Any]):
        """Display incomplete issues in table format."""
        print("\n" + "="*80)
        print("INCOMPLETE BACKLOG ISSUES")
        print("="*80)
        
        print(f"\nIncomplete Issues: {result['incomplete_count']} out of {result['total_issues']}")
        print(f"Completion Rate: {result['completion_percentage']:.1f}%")
        
        if result['most_common_missing_fields']:
            print(f"\nMost Common Missing Fields:")
            for field_info in result['most_common_missing_fields']:
                print(f"   {field_info['field']}: {field_info['count']} issues ({field_info['percentage']:.1f}%)")
        
        if result['incomplete_issues']:
            print(f"\n{'Key':<12} {'Missing':<6} {'Type':<8} {'Age':<6} {'Missing Fields'}")
            print("-" * 80)
            
            for issue in result['incomplete_issues'][:20]:  # Show top 20
                missing_fields = ', '.join(issue['missing_fields'])
                if len(missing_fields) > 25:
                    missing_fields = missing_fields[:22] + "..."
                
                print(f"{issue['key']:<12} {issue['missing_count']:<6} {issue['issue_type']:<8} {issue['age_days']:<6} {missing_fields}")
            
            if len(result['incomplete_issues']) > 20:
                print(f"\n... and {len(result['incomplete_issues']) - 20} more incomplete issues")
        else:
            print("\n🎉 All issues are complete!")


def main():
    """Main entry point for backlog CLI."""
    cli = BacklogCLI()
    sys.exit(cli.run()) 