#!/usr/bin/env python3
"""Setup script for Jira Tools package."""

from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="jira-tools",
    version="1.0.0",
    description="A comprehensive Python package for analyzing Jira sprint completion rates and publishing results",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/jira-tools",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=requirements,
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'jira-tools=cli.main_cli:main',
            'jira-sprint=cli.sprint_cli:main',
            'jira-publish=cli.publish_cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Groupware",
    ],
    keywords="jira, sprint, analysis, confluence, reporting, agile",
    include_package_data=True,
    zip_safe=False,
) 