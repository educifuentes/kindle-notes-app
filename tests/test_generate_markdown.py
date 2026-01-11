import pytest
import pandas as pd
from src.utils import parse_kindle_html, generate_markdown
from unittest.mock import patch
from datetime import datetime

@pytest.fixture
def sample_html():
    with open("test/Flow-Notebook.html", "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def expected_markdown():
    with open("tests/expected_flow_notebook.md", "r", encoding="utf-8") as f:
        return f.read()

def test_generate_markdown_matches_expected(sample_html, expected_markdown):
    # Mock datetime.now() to return a fixed date for determinism
    fixed_now = datetime(2026, 1, 11, 12, 0, 0)
    
    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        # Also need to mock strftime if it's called on the returned object
        # but in utils.py it's datetime.now().strftime(...)
        
        df, metadata = parse_kindle_html(sample_html)
        actual_markdown = generate_markdown(df, metadata)
        
        # Ensure we compare line by line to make debugging easier if it fails
        actual_lines = actual_markdown.splitlines()
        expected_lines = expected_markdown.splitlines()
        
        assert len(actual_lines) == len(expected_lines)
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            assert actual == expected, f"Mismatch at line {i+1}: expected '{expected}', got '{actual}'"
