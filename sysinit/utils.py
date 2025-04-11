"""
Utility functions for common filesystem operations.

This module includes lightweight helper functions used across the unit management system.

Author: Nitin Sharma
Docs Author: ChatGPT
"""

import os

# Join multiple path components into a single path
join_path = lambda *args: os.path.join(*args)

# Check if a given path exists in the filesystem
path_exists = lambda abs_path: os.path.exists(abs_path)
