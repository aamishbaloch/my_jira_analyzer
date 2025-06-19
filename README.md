# 🏃‍♂️ Jira Sprint Analyzer

A powerful Python toolkit for analyzing Jira sprint performance with AI-powered insights and automated Confluence reporting.

## ✨ Key Features

- **🎯 Sprint-by-Name Analysis**: Analyze any sprint using its exact name with intelligent search
- **📊 Team Performance Analytics**: Track completion rates and compare against team averages  
- **🤖 AI-Powered Insights**: Generate intelligent summaries using Google Gemini AI
- **📝 Confluence Integration**: Publish rich HTML reports with clickable ticket links
- **⚡ Multiple CLI Tools**: Choose from focused or comprehensive command interfaces
- **📈 Export & Integration**: Support for CSV, JSON, and programmatic usage

## Features

- **Sprint Analysis**: Analyze completion rates by month, recent sprints, or specific sprint names
- **Sprint-by-Name Analysis**: Analyze any sprint by its exact name with case-insensitive matching
- **Average Completion Rate**: Quick overview of team performance across last 4 sprints
- **Active Sprint Monitoring**: Track current progress of active sprints
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
│   └── sprint_analyzer.py # Sprint analysis logic
├── publishers/            # Publishing modules
│   └── confluence_publisher.py # Confluence integration
└── cli/                   # Command-line interfaces
    ├── sprint_cli.py      # Focused sprint CLI
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
       "space": "YOUR_SPACE_KEY"
     },
     "ai": {
       "gemini_api_key": "your-actual-gemini-api-key"
     }
   }
   ```

3. **Your config.json is automatically ignored by git** - it won't be committed to the repository.

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

### Comprehensive CLI (`main.py`)

```bash
# Sprint analysis
python main.py sprint analyze --sprint-name "Sprint 42"
python main.py sprint average
python main.py sprint active

# Publishing
python main.py publish confluence --sprint-name "Sprint 42" --space DEV

# Configuration
python main.py config --create-sample
python main.py config --test

# Project information
python main.py info
```

### Publishing (`publish.py`)

```bash
# Publish sprint analysis
python publish.py confluence --sprint-name "Sprint 42"

# Custom configuration
python publish.py confluence --sprint-name "Sprint 42" \
  --space DEV \
  --title "Custom Report Title" \
  --parent "Sprint Reports"

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

### 🤖 AI-Powered Insights
- Intelligent sprint achievement summaries
- Task categorization and theme extraction
- Professional project management language
- Fallback summaries when AI is unavailable

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