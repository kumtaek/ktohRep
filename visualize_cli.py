#!/usr/bin/env python3
"""
Command line interface for Source Analyzer Visualization
Usage: python visualize_cli.py <command> [options]
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import CLI from visualize module
from visualize.cli import main

if __name__ == '__main__':
    exit(main())