# Backlog Hygiene Algorithm

This document explains how the **Backlog Hygiene Score** is calculated and what each component means for your project's backlog health.

## Overview

The Backlog Hygiene Analyzer evaluates the quality and maintainability of your Jira backlog by analyzing multiple dimensions of issue health. It produces a **Hygiene Score (0-100%)** that represents the overall health of your backlog.

## 🎯 What Issues Are Analyzed

The analyzer focuses on **backlog issues** - tickets that are:
- ✅ **Not completed** (status NOT IN Done, Closed, Resolved)
- ✅ **Not in active sprints** (sprint IS EMPTY)
- ✅ **In your project** (project = YOUR_PROJECT_KEY)

**JQL Query Used:**
```sql
project = YOUR_PROJECT_KEY 
AND status NOT IN (Done, Closed, Resolved)
AND sprint IS EMPTY
ORDER BY created DESC
```

**Analysis Limit:** Up to 2,000 issues (should cover most backlogs)

## 🧮 Hygiene Score Calculation

The **Hygiene Score** is a weighted average of four key components:

### Formula
```
Hygiene Score = (Completeness × 40%) + (Age × 30%) + (Epic Assignment × 20%) + (Priority Assignment × 10%)
```

### Component Breakdown

#### 1. **Completeness Score (40% weight)**
Measures how "complete" your backlog issues are in terms of required information.

**What Makes an Issue "Complete":**
- ✅ **Description:** At least 10 characters of meaningful description
- ✅ **Epic Assignment:** Issue is linked to an epic
- ✅ **Priority:** Issue has a priority set
- ✅ **Story Points:** Issue has story points (only for Stories and Tasks)

**Calculation:**
```
Completeness Score = (Fully Complete Issues / Total Issues) × 100%
```

**Example:**
- 100 backlog issues
- 25 issues have ALL required fields
- Completeness Score = (25/100) × 100% = **25%**

#### 2. **Age Score (30% weight)**
Penalizes backlogs with very old issues that may be stale or irrelevant.

**Calculation:**
```
Age Score = max(0, 100 - (Average Age Days / 90) × 100)
```

**Baseline:** 90 days (issues older than this start getting penalized)

**Examples:**
- Average age = 45 days → Age Score = 100 - (45/90) × 100 = **50%**
- Average age = 90 days → Age Score = 100 - (90/90) × 100 = **0%**
- Average age = 180 days → Age Score = 100 - (180/90) × 100 = **-100%** → **0%** (capped at 0)

#### 3. **Epic Assignment Score (20% weight)**
Measures how well issues are organized under epics for better project structure.

**Calculation:**
```
Epic Assignment Score = (Issues with Epics / Total Issues) × 100%
```

**Example:**
- 100 backlog issues
- 60 issues are assigned to epics
- Epic Assignment Score = (60/100) × 100% = **60%**

#### 4. **Priority Assignment Score (10% weight)**
Measures how well issues are prioritized for planning purposes.

**Calculation:**
```
Priority Assignment Score = (Issues with Priority / Total Issues) × 100%
```

**Example:**
- 100 backlog issues
- 80 issues have priority set
- Priority Assignment Score = (80/100) × 100% = **80%**

## 📊 Complete Example Calculation

**Sample Backlog:**
- **Total Issues:** 100
- **Fully Complete Issues:** 25 (25%)
- **Average Age:** 120 days
- **Issues with Epics:** 60 (60%)
- **Issues with Priority:** 80 (80%)

**Step-by-Step Calculation:**

1. **Completeness Score:** 25%
2. **Age Score:** max(0, 100 - (120/90) × 100) = max(0, 100 - 133.3) = **0%**
3. **Epic Assignment Score:** 60%
4. **Priority Assignment Score:** 80%

**Final Hygiene Score:**
```
Score = (25 × 0.4) + (0 × 0.3) + (60 × 0.2) + (80 × 0.1)
Score = 10 + 0 + 12 + 8 = 30%
```

**Result:** 30% 🔴 Needs Improvement

## 📈 Score Interpretation

| Score Range | Status | Emoji | Meaning |
|-------------|--------|-------|---------|
| **80-100%** | Excellent | 🟢 | Very healthy backlog with good practices |
| **60-79%** | Good | 🟡 | Decent backlog with room for improvement |
| **0-59%** | Needs Improvement | 🔴 | Significant hygiene issues requiring attention |

## 🔍 Additional Analysis Components

### Age Distribution
Issues are categorized by age to identify staleness patterns:
- **0-7 days:** Fresh issues
- **8-30 days:** Recent issues  
- **31-90 days:** Aging issues
- **91-180 days:** Old issues ⚠️
- **180+ days:** Very old issues 🚨

### Priority Distribution
Shows how issues are distributed across priority levels:
- Critical, High, Medium, Low, None

### Epic Assignment Analysis
- **Issues with Epics:** Count and percentage
- **Orphaned Issues:** Issues without epic assignment
- **Unique Epics:** Number of different epics in backlog
- **Epic Distribution:** Which epics have the most backlog items

### Completeness Breakdown
Detailed analysis of missing information:
- **Issues with Descriptions:** Count and percentage
- **Issues with Epics:** Count and percentage  
- **Issues with Priorities:** Count and percentage
- **Issues with Story Points:** Count and percentage (Stories/Tasks only)

## 💡 AI-Powered Recommendations Engine

The analyzer uses AI to generate actionable recommendations based on your backlog's specific issues. The AI acts as a **Scrum expert and agile team coach** to provide:

### Recommendation Types
- **Backlog Health Summary:** Concise assessment of current state and impact on sprint planning
- **Action Items:** 2-3 specific, actionable recommendations for this week
- **Agile Principles:** References to transparency, definition of ready, and iterative delivery
- **Concrete Suggestions:** Time-bound, specific actions rather than vague advice

### Example AI Recommendations
```
Backlog Health: Your backlog shows significant hygiene issues with a 25.8% score, indicating it's at risk and will impact sprint planning effectiveness. Key concerns include missing descriptions, unassigned epics, and old issues.

Action Items:
1. Schedule a 45-minute backlog triage session this week to close or reclassify issues older than 90 days, following the transparency principle of Scrum.
2. Conduct a 30-minute backlog refinement session to assign the 40 orphaned issues to appropriate epics, improving your definition of ready.
3. Add story points to the top 10 prioritized issues during your next sprint planning session to enhance estimation accuracy.
```

## 🎯 Best Practices for High Hygiene Scores

### Target Metrics
- **Completeness:** >80% of issues fully complete
- **Average Age:** <60 days
- **Epic Assignment:** >80% of issues assigned to epics
- **Priority Assignment:** >90% of issues have priorities

### Workflow Recommendations
1. **Regular Grooming:** Review backlog weekly
2. **Age Management:** Archive or close issues >180 days old
3. **Information Quality:** Ensure all new issues have complete information
4. **Epic Organization:** Group related issues under meaningful epics
5. **Priority Discipline:** Assign priorities during backlog refinement

## 🔧 Technical Implementation

### Key Methods
- `analyze_full_backlog_hygiene()`: Complete analysis with all metrics
- `get_hygiene_summary()`: Quick overview with key indicators  
- `get_stale_issues(days_threshold)`: Find issues older than threshold
- `get_incomplete_issues()`: Find issues missing information

### Data Sources
- **Jira REST API:** Issue data, epic relationships, custom fields
- **Issue Fields:** Description, priority, status, creation date, story points
- **Epic Detection:** Uses JiraClient epic detection logic

### Performance
- **Query Limit:** 2,000 issues maximum
- **Display Limit:** Top 20 stale/incomplete issues shown (all analyzed)
- **Caching:** No caching - always fresh data

### File Structure
```
src/
├── gen_ai/
│   ├── hygiene_analyzer.py            # Main hygiene analysis logic
│   └── prompts/
│       └── backlog_hygiene_prompts.py # Prompt templates
├── analyzers/
│   └── backlog_hygiene_analyzer.py    # Backlog data collection
└── clients/
    └── jira_client.py                 # Epic and issue data retrieval
```

## 📋 Output Formats

### Confluence Report Structure
1. **Overall Hygiene Summary:** Score, status, and key metrics
2. **Completeness Analysis:** Field-by-field breakdown
3. **Age Distribution:** Issue age categorization
4. **Priority & Epic Analysis:** Distribution tables
5. **AI Recommendations:** Scrum expert insights and action items

### AI Processing
- **Model:** Gemini 2.5 Flash
- **Token Limit:** 4096 tokens for comprehensive analysis
- **Prompt Templates:** Dedicated templates for different analysis types
- **Fallback:** Structured recommendations when AI unavailable

This comprehensive approach ensures your backlog remains healthy, actionable, and sprint-ready while providing expert guidance for continuous improvement. 