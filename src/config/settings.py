"""
Configuration settings for the analytics platform
"""
import os
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Database configuration
DB_PATH = DATA_DIR / "nassau_candy.db"

# Analysis parameters
PARETO_THRESHOLD = 0.8  # 80% for Pareto analysis
HIGH_MARGIN_THRESHOLD = 0.30  # 30% gross margin
LOW_MARGIN_THRESHOLD = 0.10  # 10% gross margin

# Division categories
DIVISIONS = ["Chocolate", "Sugar", "Other"]

# Visualization settings
CHART_HEIGHT = 500
CHART_WIDTH = 800
COLOR_SCHEME = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff9800",
    "info": "#17a2b8"
}

# Dashboard configuration
PAGE_TITLE = "Nassau Candy Analytics"
PAGE_ICON = "🍬"
LAYOUT = "wide"
