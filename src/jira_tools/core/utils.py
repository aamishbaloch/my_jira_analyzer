"""
Utility functions shared across all Jira tools.
"""

import csv
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


def parse_jira_datetime(date_string: str) -> datetime:
    """
    Parse Jira datetime string with multiple format support.
    
    Args:
        date_string (str): Jira datetime string
        
    Returns:
        datetime object
    """
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z", 
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ"
    ]
    
    for fmt in formats:
        try:
            if date_string.endswith('Z'):
                date_string = date_string.replace('Z', '+00:00')
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    # If all formats fail, try ISO format
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError(f"Unable to parse datetime: {date_string}")


def export_to_csv(data: List[Dict[str, Any]], filename: str, fieldnames: Optional[List[str]] = None) -> None:
    """
    Export data to CSV file.
    
    Args:
        data (List[Dict]): Data to export
        filename (str): Output filename
        fieldnames (List[str], optional): Field names for CSV header
    """
    if not data:
        print("No data to export")
        return
    
    if fieldnames is None:
        fieldnames = list(data[0].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Data exported to: {filename}")


def export_to_json(data: Any, filename: str, indent: int = 2) -> None:
    """
    Export data to JSON file.
    
    Args:
        data: Data to export
        filename (str): Output filename
        indent (int): JSON indentation
    """
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=indent, default=str)
    
    print(f"Data exported to: {filename}")


def calculate_completion_percentage(completed: int, total: int) -> float:
    """
    Calculate completion percentage.
    
    Args:
        completed (int): Number of completed items
        total (int): Total number of items
        
    Returns:
        float: Completion percentage
    """
    if total == 0:
        return 0.0
    return (completed / total) * 100


def format_duration(start_date: datetime, end_date: datetime) -> str:
    """
    Format duration between two dates.
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
        
    Returns:
        str: Formatted duration
    """
    duration = end_date - start_date
    days = duration.days
    
    if days == 0:
        hours = duration.seconds // 3600
        return f"{hours} hours"
    elif days == 1:
        return "1 day"
    else:
        return f"{days} days"


def get_month_name(month_number: int) -> str:
    """
    Get month name from number.
    
    Args:
        month_number (int): Month number (1-12)
        
    Returns:
        str: Month name
    """
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    if 1 <= month_number <= 12:
        return months[month_number - 1]
    else:
        return f"Month {month_number}"


def print_table(headers: List[str], rows: List[List[str]], title: Optional[str] = None) -> None:
    """
    Print a formatted table.
    
    Args:
        headers (List[str]): Table headers
        rows (List[List[str]]): Table rows
        title (str, optional): Table title
    """
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    
    if not rows:
        print("No data to display")
        return
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_row = " | ".join(header.ljust(width) for header, width in zip(headers, col_widths))
    print(f"\n{header_row}")
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        row_str = " | ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths))
        print(row_str)
    
    print()


def validate_month(month: int) -> bool:
    """
    Validate month number.
    
    Args:
        month (int): Month number
        
    Returns:
        bool: True if valid month
    """
    return 1 <= month <= 12


def create_summary_stats(data: List[Dict[str, Any]], metric_key: str) -> Dict[str, float]:
    """
    Create summary statistics for a metric.
    
    Args:
        data (List[Dict]): Data containing the metric
        metric_key (str): Key for the metric to analyze
        
    Returns:
        Dict with summary statistics
    """
    if not data:
        return {}
    
    values = [item.get(metric_key, 0) for item in data if isinstance(item.get(metric_key), (int, float))]
    
    if not values:
        return {}
    
    return {
        'count': len(values),
        'min': min(values),
        'max': max(values),
        'average': sum(values) / len(values),
        'total': sum(values)
    } 