# 📝 Jira Publisher

A focused Python tool for publishing Jira analysis results to Confluence with AI-powered insights.

## ✨ Key Features

- **📝 Confluence Publishing**: Publish sprint analysis and backlog hygiene reports to Confluence
- **🤖 AI-Powered Insights**: Generate intelligent summaries and recommendations using Google Gemini AI
- **🎯 Sprint Analysis Publishing**: Create rich HTML reports for sprint completion analysis
- **🧹 Backlog Hygiene Publishing**: Publish comprehensive backlog health assessments
- **🔗 Rich HTML Reports**: Generate reports with clickable Jira ticket links
- **⚙️ Flexible Configuration**: Support for multiple projects and spaces

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
# Publish sprint analysis to Confluence
python main.py confluence --sprint-name "Sprint 42"

# Publish backlog hygiene analysis
python main.py backlog-hygiene

# Publish backlog hygiene with AI insights
python main.py backlog-hygiene --ai-enhanced

# Publish dedicated AI insights report  
python main.py ai-insights

# Test Confluence connection
python main.py test

# List available Confluence spaces (for reference)
python main.py spaces
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
└── cli/                   # Command-line interface
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
       "space": "YOUR_SPACE_KEY",
               "sprint_completion_parent_page": "Sprint Reviews",
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
- `space`: Confluence space for all publishing
- `sprint_completion_parent_page`: Parent page for sprint completion analysis reports
- `backlog_hygiene_parent_page`: Parent page for backlog hygiene reports

If parent pages are not specified, reports will be created at the root level of the space.

### Getting API Tokens

- **Jira/Confluence**: [Create API Token](https://id.atlassian.com/manage-profile/security/api-tokens)
- **Google AI**: [Get Gemini API Key](https://aistudio.google.com/app/apikey)

## Available Commands

All commands are publishing-focused and generate Confluence reports with rich HTML formatting and AI insights:

### Sprint Analysis Publishing
```bash
# Publish sprint analysis to Confluence
python main.py confluence --sprint-name "Sprint 42"

# Custom configuration
python main.py confluence --sprint-name "Sprint 42" \
  --title "Custom Report Title" \
  --parent "Sprint Reviews"
```

### Backlog Hygiene Publishing
```bash
# Publish backlog hygiene analysis (automatically includes current week)
python main.py backlog-hygiene
# Creates: "Analysis - W26 2024" (under default parent page)

# With AI-enhanced insights
python main.py backlog-hygiene --ai-enhanced

# With custom parent and title
python main.py backlog-hygiene \
  --parent "Backlog Reports" \
  --title "Weekly Backlog Health Check"
```

### AI Insights Publishing
```bash
# Publish dedicated AI insights report
python main.py ai-insights

# With custom configuration
python main.py ai-insights \
  --title "AI Backlog Insights" \
  --parent "AI Reports"
```

### Utility Commands
```bash
# Test Confluence connection
python main.py test

# List available Confluence spaces (for reference)
python main.py spaces
```

### Command Options
- `--title, -t`: Custom page title (auto-generated if not provided)  
- `--parent, -p`: Parent page title for organizing reports
- `--ai-enhanced`: Include enhanced AI insights in backlog hygiene reports
- `--config, -c`: Path to configuration file (default: config.json)

**Note**: The Confluence space is automatically read from `space` in your config.json file.

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
- **📚 [Detailed Hygiene Algorithm Guide](documentation/BACKLOG_HYGIENE_ALGORITHM.md)**

### 🤖 AI-Powered Insights
- Intelligent sprint achievement summaries
- Task categorization and theme extraction
- Professional project management language
- Fallback summaries when AI is unavailable
- **📚 [Detailed AI Prompt Engineering Guide](documentation/AI_ACHIEVEMENT_SUMMARY.md)**

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