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
- **Epic Description** (`epic_description`): Strategic context and goals of the epic
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
- Fix user login validation - Add proper email format validation and password strength checks (Epic: User Authentication - Improve security and user experience for authentication flows)
- Update PaymentService API - Implement new refund logic with automated processing (Epic: Payment Processing - Streamline payment operations and reduce manual intervention)
- Enhance checkout flow - Add real-time validation and error messaging (Epic: Checkout Experience - Optimize conversion rates through improved UX)
```

### Key Elements
1. **Task Title**: Clear, concise ticket summary
2. **Description Preview**: First 100 characters of ticket description
3. **Epic Context**: `(Epic: Epic Name - Epic Description)` for strategic grouping
4. **Service Names**: Preserved from titles for technical context

## AI Instructions

### System Prompt
```
You are a technical program assistant that summarizes Jira sprint reports. Given a list of Jira tasks (including fields like title, summary, status, completion date, epic name, and epic description), generate the following:

1. Write a concise, direct, and clear summary of the current backlog health. Avoid long explanations. Focus on key signals such as hygiene score, issue age, missing estimates, and epic assignment. Clearly state whether the backlog is healthy, needs improvement, or is at risk.
2. Recommend 2 to 3 short-term action items the team can take this week to improve backlog quality. These actions should align with Scrum and Agile best practices such as backlog refinement, closing stale issues, assigning epics, or adding estimates.
3. Where helpful, reference Agile principles like transparency, definition of ready, or iterative delivery to justify the actions.
4. Make the suggestions specific and actionable — for example: "Schedule a 45-minute backlog triage to close or reclassify issues older than 90 days" instead of vague statements.
5. Output must be plain text only. Do not use bold, italics, or markdown formatting.

Focus on making the backlog actionable, prioritized, and sprint-ready, while reinforcing agile ways of working.
```

### Task-Specific Instructions
```
Write one concise paragraph summarizing only the most meaningful achievements from the sprint. Focus on:
- What was completed that created real technical or business value.
- Use editorial judgment — do not include every task. Only mention impactful work, such as business requests, data enablement, CVA improvements, or technical enhancements.
- Group related work together to keep the summary clear and easy to read.
- Use the epic information to understand the broader context and group tasks by their strategic initiatives.
- Mention the key systems or services involved (e.g., customer-review-service, transactional communication service, dataset pipelines).
- Reference the type of work done — such as token invalidation, Kafka integration, dataset migration, CVA improvements, campaign fixes, or data snapshots.
- Clearly state the tech or business domain impacted (e.g., security, infrastructure, campaign automation, data accuracy, observability).
- Use plain, clear language without deep technical jargon.
- Do not include the highlight content in this paragraph.

After the paragraph, add a separate line starting with:

Highlight: [Describe the most valuable delivery. Mention which system or service was improved, what capability or benefit it unlocked, and why it matters to the platform, team, or business. Justify why this was selected as the highlight.]

Do not use markdown or rich text formatting. Output must be plain text, suitable for pasting directly into Confluence.
```

## Example Transformation

### Input Data
```
COMPLETED TASKS:
- Fix UserService login validation - Add email format validation and password strength requirements (Epic: User Authentication - Improve security and user experience for authentication flows)
- Update UserService password reset - Implement secure token generation and expiration logic (Epic: User Authentication - Improve security and user experience for authentication flows)
- Add PaymentService refund API - Create automated refund processing with transaction logging (Epic: Payment Processing - Streamline payment operations and reduce manual intervention)
- Enhance PaymentService error handling - Improve error messages and retry logic for failed payments (Epic: Payment Processing - Streamline payment operations and reduce manual intervention)
- Update checkout page UI - Add real-time form validation and loading states (Epic: Checkout Experience - Optimize conversion rates through improved UX)
```

### Generated Summary
```
This sprint significantly advanced our platform's core capabilities, particularly in critical communications and data enablement. The Transactional Communication Service (TCS) was modernized through the implementation of a Kafka publisher adaptor and the associated update of metrics and alerts, enhancing the reliability and latency of time-critical communications. We also improved data infrastructure by migrating the addons dataset to Tardis, and enabled stakeholders with crucial commercial data by providing a menu planning data snapshot and adding a 'final box delivery date' attribute to cancellation events on the Producer. Additionally, security was bolstered in the customer-review-service with new token invalidation logic, and a business-critical issue affecting VMS items in the Factor US Meal Choice module was resolved.

Highlight: The most valuable delivery was the implementation of a Kafka publisher adaptor for the Transactional Communication Service (TCS), along with updated metrics and alerts. This capability modernizes our critical communication infrastructure, improving message latency and reliability, and directly supports the deprecation of older microservice components. This foundational work significantly enhances the platform's ability to handle high-volume, time-sensitive communications efficiently.
```

## Key Features

### 1. Epic-Based Grouping with Strategic Context
- Related tickets are bundled by their parent epic
- Epic descriptions provide strategic context and business goals
- Shows feature progression and completion with business value

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

### 1. Epic Naming and Description
- Use clear, business-focused epic names
- Include strategic context in epic descriptions
- Avoid technical jargon in epic titles
- Examples: "User Authentication - Improve security and user experience for authentication flows"

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
2. **Prompt Building** (`sprint_summarizer.py` with `sprint_summarizer_prompts.py`)
3. **AI Processing** (Gemini 2.5 Flash with 4096 token limit)
4. **Fallback Handling** (when AI unavailable)

### File Structure
```
src/
├── gen_ai/
│   ├── sprint_summarizer.py          # Main sprint summarization logic
│   └── prompts/
│       └── sprint_summarizer_prompts.py  # Prompt templates
├── analyzers/
│   └── sprint_analyzer.py            # Sprint data collection
└── clients/
    └── jira_client.py                # Epic and issue data retrieval
```

This approach ensures consistent, meaningful summaries that provide both technical and business context for sprint accomplishments. 