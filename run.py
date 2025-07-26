#!/usr/bin/env python3
"""
Entry point for OpenSuperWhisper application.
This file allows running the application from the project root directory.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from OpenSuperWhisper.main import main

if __name__ == "__main__":
    main()