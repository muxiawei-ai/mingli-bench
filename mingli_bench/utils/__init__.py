"""
Utility modules for Fortune Telling Benchmark.
"""

from .logger import get_logger
from .decorators import retry_on_error
from .path_utils import find_file_in_hierarchy, find_data_file

__all__ = [
    "get_logger", 
    "load_config",
    "retry_on_error", 
    "find_file_in_hierarchy",
    "find_data_file",
]


def __getattr__(name):
    if name == "load_config":
        from .config import load_config

        return load_config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
