"""Test package initialization."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_import():
    """Test that all modules can be imported."""
    from scripts import TrendingFetcher, NotePublisher, StatsFetcher
    
    assert TrendingFetcher is not None
    assert NotePublisher is not None
    assert StatsFetcher is not None


def test_version():
    """Test that version is defined."""
    from scripts import __version__
    
    assert isinstance(__version__, str)
    assert __version__ == "1.0.0"
