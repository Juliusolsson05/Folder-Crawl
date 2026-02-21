"""
folder-crawl: A CLI tool to display folder structure and contents with gitignore-style patterns.
"""

__version__ = "0.3.0"
__author__ = "Julius Olsson"
__email__ = "julius.olsson05@gmail.com"

from .cli import main

__all__ = ["main", "__version__"]