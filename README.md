# 🏃‍♂️ Jira Sprint Analyzer

A powerful Python toolkit for analyzing Jira sprint performance with AI-powered insights and automated Confluence reporting.

## ✨ Key Features

- **🎯 Sprint-by-Name Analysis**: Analyze any sprint using its exact name with intelligent search
- **📊 Team Performance Analytics**: Track completion rates and compare against team averages  
- **🧹 Backlog Hygiene Analysis**: Assess backlog health with completeness, age, and quality metrics
- **🤖 AI-Powered Insights**: Generate intelligent summaries using Google Gemini AI
- **📝 Confluence Integration**: Publish rich HTML reports with clickable ticket links
- **⚡ Multiple CLI Tools**: Choose from focused or comprehensive command interfaces
- **📈 Export & Integration**: Support for CSV, JSON, and programmatic usage

## Features

- **Sprint Analysis**: Analyze completion rates by month, recent sprints, or specific sprint names
- **Sprint-by-Name Analysis**: Analyze any sprint by its exact name with case-insensitive matching
- **Average Completion Rate**: Quick overview of team performance across last 4 sprints
- **Active Sprint Monitoring**: Track current progress of active sprints
- **Backlog Hygiene Analysis**: Comprehensive backlog health assessment with hygiene scoring
- **AI-Powered Summaries**: Generate intelligent sprint achievement summaries using Google Gemini
- **Confluence Publishing**: Automatically publish rich HTML reports with clickable ticket links
- **Team Performance Context**: Compare individual sprint performance against team averages
- **Export Support**: Export results to CSV and JSON formats
- **Multiple CLI Interfaces**: Choose from focused or comprehensive command-line tools

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd my_jira_analyzer

# Install dependencies
pip install -r requirements.txt

# Create configuration
python cli.py config --create-sample
```

### Basic Usage

```bash
# Analyze a specific sprint by name
python cli.py analyze --sprint-name "Sprint 42"

# Get team performance overview
python cli.py average

# View active sprints
python cli.py active

# Analyze backlog hygiene
python backlog_cli.py summary

# Publish to Confluence with AI insights
python publish.py confluence --sprint-name "Sprint 42" --space DEV
```

## Package Structure

```
src/
├── core/                   # Core functionality
│   ├── config.py          # Configuration management
│   ├── jira_client.py     # Jira API client
│   ├── ai_summarizer.py   # AI-powered summaries
│   └── utils.py           # Utility functions
├── analyzers/             # Analysis modules
│   ├── sprint_analyzer.py # Sprint analysis logic
│   └── backlog_hygiene_analyzer.py # Backlog hygiene analysis
├── publishers/            # Publishing modules
│   └── confluence_publisher.py # Confluence integration
└── cli/                   # Command-line interfaces
    ├── sprint_cli.py      # Focused sprint CLI
    ├── backlog_cli.py     # Backlog hygiene CLI
    ├── main_cli.py        # Comprehensive CLI
    └── publish_cli.py     # Publishing CLI
```

## Configuration

### Setup Your API Keys

1. **Copy the example configuration:**
   ```bash
   cp config.json.example config.json
   ```

2. **Edit config.json with your actual credentials:**
   ```json
   {
     "jira": {
       "url": "https://your-company.atlassian.net",
       "username": "your-email@company.com",
       "api_token": "your-actual-jira-api-token",
       "project_key": "YOUR_PROJECT_KEY"
     },
     "confluence": {
       "url": "https://your-company.atlassian.net/wiki",
       "username": "your-email@company.com",
       "api_token": "your-actual-confluence-api-token",
       "default_space": "YOUR_SPACE_KEY",
       "default_sprint_completion_parent_page": "Sprint Reviews",
       "backlog_hygiene_parent_page": "Backlog Reports"
     },
     "ai": {
       "gemini_api_key": "your-actual-gemini-api-key"
     }
   }
   ```

3. **Your config.json is automatically ignored by git** - it won't be committed to the repository.

#### Configuration Options

**Confluence Publishing:**
- `default_space`: Default Confluence space for all publishing
- `default_sprint_completion_parent_page`: Parent page for sprint completion analysis reports
- `backlog_hygiene_parent_page`: Parent page for backlog hygiene reports

If parent pages are not specified, reports will be created at the root level of the space.

### Getting API Tokens

- **Jira/Confluence**: [Create API Token](https://id.atlassian.com/manage-profile/security/api-tokens)
- **Google AI**: [Get Gemini API Key](https://aistudio.google.com/app/apikey)

## Available Commands

### Sprint Analysis (`cli.py`)

```bash
# Analyze specific sprint
python cli.py analyze --sprint-name "Sprint 42"
python cli.py analyze --sprint-name "Sprint 42" --details

# Analyze by time period
python cli.py analyze --month 6
python cli.py analyze --last-sprints 4

# Team performance overview
python cli.py average

# Active sprints
python cli.py active

# Export results
python cli.py analyze --sprint-name "Sprint 42" --export results.csv
python cli.py analyze --month 6 --export results.json

# Test connection
python cli.py test
```

### Backlog Hygiene Analysis (`backlog_cli.py`)

```bash
# Comprehensive hygiene analysis
python backlog_cli.py hygiene

# Quick hygiene summary
python backlog_cli.py summary

# Find stale issues (default: 90+ days)
python backlog_cli.py stale

# Find stale issues with custom threshold
python backlog_cli.py stale --days 60

# Find incomplete issues
python backlog_cli.py incomplete

# Export results
python backlog_cli.py hygiene --export hygiene_report.json
```

### Comprehensive CLI (`main.py`)

```bash
# Sprint analysis
python main.py sprint analyze --sprint-name "Sprint 42"
python main.py sprint average
python main.py sprint active

# Backlog hygiene
python main.py backlog hygiene
python main.py backlog summary
python main.py backlog stale --days 60
python main.py backlog incomplete

# Publishing
python main.py publish confluence --sprint-name "Sprint 42" --space DEV
python main.py publish backlog-hygiene --space DEV --parent "Backlog Reports"

# Configuration
python main.py config --create-sample
python main.py config --test

# Project information
python main.py info
```

### Publishing (`publish.py`)

#### Sprint Analysis Publishing
```bash
# Publish sprint analysis
python publish.py confluence --sprint-name "Sprint 42"

# Custom configuration
python publish.py confluence --sprint-name "Sprint 42" \
  --space DEV \
  --title "Custom Report Title" \
  --parent "Sprint Reviews"
```

#### Backlog Hygiene Publishing
```bash
# Publish backlog hygiene analysis (automatically includes current week)
python publish.py backlog-hygiene --space DEV
# Creates: "Analysis - W26 2024" (under "Backlog Hygiene" parent page)

# With custom parent and title
python publish.py backlog-hygiene \
  --space DEV \
  --parent "Backlog Reports" \
  --title "Weekly Backlog Health Check - W26 2024"
```

#### Connection Testing
```bash
# Test connection
python publish.py test

# List available spaces
python publish.py spaces
```

## Features in Detail

### 🎯 Sprint-by-Name Analysis
- Case-insensitive sprint name matching
- Searches across active, closed, and future sprints
- Detailed task breakdown and completion metrics
- Sprint state and date information

### 📊 Team Performance Context
- Average completion rate of last 4 closed sprints
- Individual sprint performance comparison
- Best and worst performing sprint identification
- Trend analysis and insights

### 🧹 Backlog Hygiene Analysis
- **Hygiene Score (0-100%)**: Overall backlog health assessment
- **Completeness Analysis**: Track issues with descriptions, epics, priorities, and story points
- **Age Distribution**: Identify how long issues have been in backlog (0-7, 8-30, 31-90, 91-180, 180+ days)
- **Stale Issue Detection**: Find issues older than configurable threshold (default: 90 days)
- **Incomplete Issue Analysis**: Identify issues missing critical information
- **Priority Distribution**: Analyze priority assignment across backlog
- **Epic Assignment**: Track orphaned issues without epic assignments
- **Actionable Recommendations**: Get specific suggestions for backlog improvement
- **📚 [Detailed Hygiene Algorithm Guide](src/About%20the%20Algorithms/BACKLOG_HYGIENE_ALGORITHM.md)**

### 🤖 AI-Powered Insights
- Intelligent sprint achievement summaries
- Task categorization and theme extraction
- Professional project management language
- Fallback summaries when AI is unavailable
- **📚 [Detailed AI Prompt Engineering Guide](src/About the Algorithms/AI_ACHIEVEMENT_SUMMARY.md)**

### 🔗 Rich Confluence Reports
- Clickable Jira ticket links
- Professional HTML formatting
- Team performance context sections
- Visual indicators and progress bars
- Responsive design for all devices

### 📈 Export and Integration
- CSV export for spreadsheet analysis
- JSON export for programmatic use
- Multiple output formats supported
- Easy integration with other tools

## Development

### Package Structure
The codebase follows a clean, modular architecture:

- **`src/core/`**: Shared functionality (config, Jira client, utilities)
- **`src/analyzers/`**: Analysis logic and algorithms  
- **`src/publishers/`**: Output and publishing modules
- **`src/cli/`**: Command-line interfaces and user interaction

### Key Classes

- **`SprintAnalyzer`**: Core analysis engine with sprint-by-name and average completion rate features
- **`BacklogHygieneAnalyzer`**: Comprehensive backlog health assessment with hygiene scoring
- **`JiraClient`**: Jira API wrapper with enhanced sprint search capabilities
- **`ConfluencePublisher`**: Rich HTML report generation with AI integration
- **`AISummarizer`**: Google Gemini integration for intelligent insights

### Installation for Development

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Requirements

- Python 3.7+
- Jira API access
- Confluence API access (for publishing)
- Google AI API key (optional, for AI features)

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the configuration setup
2. Test API connections using `python cli.py test`
3. Review error messages for specific guidance
4. Open an issue with detailed information 