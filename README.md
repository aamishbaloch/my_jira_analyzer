# Jira Tools 🛠️

A comprehensive suite of Jira analysis tools for sprint completion analysis, velocity tracking, and project insights.

## 🚀 Features

### Sprint Analysis
- **Completion Rate Analysis**: Track actual task completion dates vs sprint end dates
- **Month-based Analysis**: Analyze all sprints closed in a specific month
- **Recent Sprint Analysis**: Analyze the last X closed sprints
- **Active Sprint Monitoring**: View current sprint progress
- **Detailed Task Tracking**: See which tasks were completed on time vs late

### Project Management
- **Multi-board Support**: Automatically discovers and analyzes all project boards
- **Flexible Configuration**: JSON-based configuration with validation
- **Export Capabilities**: Export results to CSV or JSON formats
- **Connection Testing**: Verify Jira connectivity and permissions

## 📦 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Configuration
```bash
# Create sample configuration file
python main.py config --create-sample

# Edit config.json with your Jira credentials
```

### 3. Test Connection
```bash
# Verify your setup works
python main.py config --test
```

### 4. Run Analysis
```bash
# Analyze sprints closed in June
python cli.py analyze --month 6

# Analyze last 4 sprints with details
python cli.py analyze --last-sprints 4 --details

# Check active sprints
python cli.py active
```

## ⚙️ Configuration

### Getting Your Jira API Token
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a name and copy the token
4. Use your email as username and the token as password

### Configuration Format (`config.json`)
```json
{
  "jira": {
    "url": "https://your-domain.atlassian.net",
    "username": "your-email@company.com",
    "api_token": "your-api-token-here",
    "project_key": "YOUR_PROJECT_KEY"
  },
  "analyzers": {
    "sprint": {
      "analysis_mode": "month",
      "target_month": 6,
      "last_sprints_count": 4
    }
  },
  "export": {
    "default_format": "csv",
    "output_directory": "reports"
  }
}
```

## 🔧 Usage

### Quick CLI (Recommended)
```bash
# Sprint analysis
python cli.py analyze --month 6                    # Analyze June sprints
python cli.py analyze --last-sprints 4 --details   # Last 4 sprints with task details
python cli.py analyze --month 6 --export june.csv  # Export June results to CSV

# Active sprints
python cli.py active                                # Show current sprint status
python cli.py active --export active.json          # Export active sprints

# Connection testing
python cli.py test                                  # Test Jira connection
```

### Main CLI (Full Features)
```bash
# Configuration management
python main.py config --create-sample              # Create sample config
python main.py config --test                       # Test configuration
python main.py config --validate                   # Validate config only

# Project information
python main.py info                                 # Show project details

# Sprint analysis
python main.py sprint analyze --month 6            # Analyze by month
python main.py sprint analyze --last-sprints 4     # Analyze recent sprints
python main.py sprint active                       # Show active sprints
```

### Python API
```python
from src.jira_tools.analyzers.sprint_analyzer import SprintAnalyzer
from src.jira_tools.core.config import Config

# Initialize analyzer
analyzer = SprintAnalyzer('config.json')

# Analyze sprints by month
results = analyzer.calculate_sprints_by_month(6)  # June
print(f"Average completion rate: {results['average_completion_rate']:.1f}%")

# Analyze recent sprints
results = analyzer.calculate_last_x_sprints(4)
for sprint in results['sprint_results']:
    print(f"{sprint['sprint_name']}: {sprint['completion_rate']:.1f}%")

# Get active sprints
active = analyzer.get_active_sprints_summary()
print(f"Active sprints: {active['active_sprint_count']}")
```

## 📊 Real Example Output

```bash
$ python cli.py analyze --month 6
🔍 Analyzing sprint completion rates...
📅 Analyzing sprints closed in June

============================================================
📊 SPRINT COMPLETION ANALYSIS RESULTS
============================================================

📈 Overall Statistics:
   Total Tasks: 87
   Completed Within Sprint: 67
   Average Completion Rate: 77.0%
   Best Sprint Rate: 88.9%
   Worst Sprint Rate: 69.2%

🏃 Sprint Details
=================

Sprint Name                | End Date   | Total Tasks | Completed | Rate (%)
----------------------------------------------------------------------------
Missing Penguin (W23-W24)  | 2025-06-16 | 9           | 8         | 88.9%   
Midnight Cats (W21-W22)    | 2025-06-02 | 13          | 9         | 69.2%   
Gracious Gazelle (W25-W26) | 2024-06-28 | 14          | 10        | 71.4%   
Uplifted Unicorn (W23-W24) | 2024-06-14 | 20          | 16        | 80.0%   
Hopeful Turtle (W21 - W22) | 2024-06-01 | 31          | 24        | 77.4%   
```

## 🏗️ Project Structure

```
my_jira_analyzer/
├── src/jira_tools/              # Main package
│   ├── __init__.py
│   ├── core/                    # Core functionality
│   │   ├── config.py           # Configuration management
│   │   ├── jira_client.py      # Shared Jira client
│   │   └── utils.py            # Utility functions
│   ├── analyzers/              # Analysis modules
│   │   └── sprint_analyzer.py  # Sprint completion analysis
│   └── cli/                    # Command-line interfaces
│       ├── main_cli.py         # Main CLI entry point
│       └── sprint_cli.py       # Sprint-specific CLI
├── main.py                     # Full-featured CLI
├── cli.py                      # Quick sprint analysis CLI
├── setup.py                    # Package installation
├── config.json                 # Your Jira configuration
└── requirements.txt            # Dependencies
```

## 🎯 Key Metrics Explained

### Completion Rate Analysis
- **Within Sprint**: Task marked as "Done" before or on sprint end date ✅
- **After Sprint**: Task marked as "Done" after sprint end date ❌
- **Not Completed**: Task never marked as "Done" ❌

### Status Recognition
The tool recognizes these Jira statuses as "completed":
- Done
- Closed  
- Resolved

### Analysis Modes
- **Month-based**: `--month 6` analyzes all sprints that ended in June
- **Recent sprints**: `--last-sprints 4` analyzes the 4 most recently closed sprints
- **Active monitoring**: Shows current progress of active sprints

## 🛠️ Advanced Usage

### Export Options
```bash
# Export to CSV
python cli.py analyze --month 6 --export june_sprints.csv

# Export to JSON  
python cli.py analyze --last-sprints 4 --export recent_sprints.json

# Export active sprints
python cli.py active --export active_status.csv
```

### Detailed Task Analysis
```bash
# Show individual task completion status
python cli.py analyze --month 6 --details

# This shows for each task:
# - Task key (e.g., CBB-123)
# - Current status
# - Whether completed within sprint timeframe
# - Actual completion date
```

### Package Installation (Optional)
```bash
# Install as a package for system-wide access
pip install -e .

# Note: Console scripts may not work in all environments
# Use the python scripts instead for reliability
```

## 🔍 Understanding Your Results

### Good Completion Rates
- **80%+**: Excellent sprint planning and execution
- **70-79%**: Good performance with room for improvement
- **60-69%**: Needs attention - consider sprint planning review

### Common Issues
- **Low completion rates**: May indicate over-commitment or scope creep
- **High variation**: Inconsistent sprint planning or external dependencies
- **Tasks completed late**: Could indicate poor estimation or blockers

## 🆘 Troubleshooting

### Connection Issues
```bash
# Test your connection
python main.py config --test

# Get detailed project info
python main.py info
```

### Common Problems

**"No closed sprints found"**
- Verify your project key is correct
- Check that sprints exist in the specified timeframe
- Ensure you have access to the project boards

**"The board does not support sprints"**
- Some boards (like Kanban or Epic boards) don't have sprints
- The tool will skip these and analyze sprint-enabled boards only

**"Configuration file not found"**
```bash
# Create the config file
python main.py config --create-sample
# Then edit config.json with your credentials
```

**Permission Errors**
- Verify your API token has project access
- Check that your user account can view the project
- Ensure the project key is correct

### Getting Help
```bash
# Show all available commands
python main.py --help
python cli.py --help

# Test your setup step by step
python main.py config --test    # Test credentials
python main.py info             # Check project access
python cli.py active            # Verify sprint access
```

## 🚀 Next Steps

### Adding New Analysis Types
The modular structure makes it easy to add:
- **Velocity Analysis**: Track story points over time
- **Burndown Charts**: Sprint progress visualization  
- **Epic Analysis**: Cross-sprint epic tracking
- **Team Performance**: Individual contributor metrics

### Integration Options
- Export data to BI tools (Tableau, Power BI)
- Integrate with CI/CD pipelines
- Create automated reports
- Build dashboards with the Python API

## 📄 License

MIT License - see LICENSE file for details.

---

**💡 Pro Tip**: Start with `python cli.py analyze --month [current_month]` to get a quick overview of your team's recent performance! 