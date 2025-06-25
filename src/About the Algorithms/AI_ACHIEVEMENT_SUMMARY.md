# AI Achievement Summary - Prompt Engineering Guide

This document explains how the Jira analyzer builds AI prompts to generate meaningful sprint achievement summaries.

## Overview

The AI Achievement Summary feature transforms raw Jira ticket data into coherent, business-focused summaries that group related work by epics and highlight technical achievements across different services.

## Data Collection Process

### 1. Sprint Data Extraction
```python
# From sprint_analyzer.py
issues = self.jira_client.get_sprint_issues(sprint.id, expand_changelog=True)
```

### 2. Enhanced Task Information
For each ticket, we collect:
- **Title** (`summary`): The ticket title
- **Description** (`description`): Detailed explanation of what was done
- **Epic Context** (`epic_summary`): Parent epic for grouping related work
- **Service Names**: Extracted from titles (e.g., "UserService", "PaymentService")
- **Completion Status**: Whether completed within sprint timeline

### 3. Epic Relationship Mapping
```python
epic_info = self.jira_client.get_epic_for_issue(issue)
```
Epic information is gathered from multiple possible fields:
- `parent` field (if parent is an Epic)
- `epic` field
- `customfield_10011` (common epic link field)
- `customfield_10014` (alternative epic link field)

## Prompt Structure

### Input Format
The AI receives structured data in this format:

```
COMPLETED TASKS:
- Fix user login validation - Add proper email format validation and password strength checks (part of: User Authentication Epic)
- Update PaymentService API - Implement new refund logic with automated processing (part of: Payment Processing Epic)
- Enhance checkout flow - Add real-time validation and error messaging (part of: Checkout Experience Epic)

COMPLETED AFTER SPRINT:
- Deploy UserService updates - Deploy authentication changes to production environment (part of: User Authentication Epic)
```

### Key Elements
1. **Task Title**: Clear, concise ticket summary
2. **Description Preview**: First 100 characters of ticket description
3. **Epic Context**: `(part of: Epic Name)` for grouping
4. **Service Names**: Preserved from titles for technical context

## AI Instructions

### System Prompt
```
Write a direct paragraph summary of sprint achievements. Use both ticket titles and descriptions to understand what was actually done. Bundle tasks by their epic context into main accomplishments. Pay attention to service names in ticket titles (e.g., "UserService", "PaymentService") and include them in your summary to show which systems were worked on. Use simple, clear language. Avoid corporate jargon, flowery language, and phrases like "robust," "comprehensive," "leverage," or "outcomes."
```

### Task-Specific Instructions
```
Write a single paragraph summary of what the team achieved this sprint. Use both the ticket titles and descriptions to understand what was actually accomplished. Group tasks by their epic context and describe the main achievements. Pay special attention to service names in ticket titles and include them to show which systems were worked on (e.g., "enhanced UserService with login validation and improved PaymentService with refund processing"). Use the epic information to bundle related work together. Be direct and focus only on what was accomplished.
```

## Example Transformation

### Input Data
```
COMPLETED TASKS:
- Fix UserService login validation - Add email format validation and password strength requirements (part of: User Authentication Epic)
- Update UserService password reset - Implement secure token generation and expiration logic (part of: User Authentication Epic)
- Add PaymentService refund API - Create automated refund processing with transaction logging (part of: Payment Processing Epic)
- Enhance PaymentService error handling - Improve error messages and retry logic for failed payments (part of: Payment Processing Epic)
- Update checkout page UI - Add real-time form validation and loading states (part of: Checkout Experience Epic)
```

### Generated Summary
```
The team advanced the User Authentication Epic by enhancing UserService with email format validation, password strength requirements, and secure token-based password reset functionality. Payment Processing Epic progressed through PaymentService improvements including automated refund API implementation and enhanced error handling with retry logic. The Checkout Experience Epic was furthered with UI updates featuring real-time form validation and improved loading states.
```

## Key Features

### 1. Epic-Based Grouping
- Related tickets are bundled by their parent epic
- Provides business-level context rather than task-level details
- Shows feature progression and completion

### 2. Service Name Preservation
- Technical service names (UserService, PaymentService) are maintained
- Shows which systems were modified
- Provides architectural context

### 3. Description Context
- Ticket descriptions provide "what was actually done"
- Limited to 100 characters to maintain prompt efficiency
- Helps AI understand implementation details

### 4. Achievement Focus
- Emphasizes what was accomplished, not what was planned
- Groups individual tasks into meaningful business outcomes
- Avoids corporate jargon and focuses on concrete results

## Fallback Behavior

When AI is unavailable, the system generates structured fallback summaries:

```python
def _extract_epic_themes(self, tasks):
    # Groups tasks by epic frequency
    epic_counts = {}
    for task in tasks:
        epic_summary = task.get('epic_summary', 'No Epic')
        epic_counts[epic_summary] = epic_counts.get(epic_summary, 0) + 1
    
    # Returns epic names in order of frequency
    return formatted_epic_summary
```

## Configuration

### Epic Field Detection
The system automatically detects epic relationships from multiple field types:
```python
# Handles different Jira configurations
if hasattr(issue.fields, 'parent') and issue.fields.parent:
    if issue.fields.parent.fields.issuetype.name == 'Epic':
        epic_key = issue.fields.parent.key
elif hasattr(issue.fields, 'epic') and issue.fields.epic:
    epic_key = issue.fields.epic.key
elif hasattr(issue.fields, 'customfield_10011'):
    epic_key = getattr(issue.fields, 'customfield_10011', None)
```

### Description Length Limits
```python
# Keeps prompts manageable while preserving context
if len(task_description.strip()) > 100:
    desc_preview = task_description.strip()[:100] + "..."
```

## Best Practices

### 1. Epic Naming
- Use clear, business-focused epic names
- Avoid technical jargon in epic titles
- Examples: "User Authentication", "Payment Processing", "Checkout Experience"

### 2. Ticket Titles
- Include service names when relevant
- Be specific about what was done
- Examples: "Fix UserService login validation", "Update PaymentService API"

### 3. Ticket Descriptions
- First 100 characters are most important
- Include implementation details
- Explain what was actually accomplished

## Output Examples

### Simple Sprint
**Input**: 3 tickets across 1 epic
**Output**: "The team completed User Authentication Epic by implementing UserService login validation, password reset functionality, and session management improvements."

### Complex Sprint
**Input**: 12 tickets across 4 epics
**Output**: "The team advanced User Authentication Epic through UserService enhancements including login validation and password reset, progressed Payment Processing Epic with PaymentService refund API and error handling improvements, enhanced Checkout Experience Epic with UI validation and loading states, and completed API Integration Epic by updating external service connections and webhook processing."

## Technical Implementation

The achievement summary generation involves:

1. **Data Collection** (`sprint_analyzer.py`)
2. **Prompt Building** (`ai_summarizer.py`)
3. **AI Processing** (Gemini 2.5 Flash)
4. **Fallback Handling** (when AI unavailable)

This approach ensures consistent, meaningful summaries that provide both technical and business context for sprint accomplishments. 