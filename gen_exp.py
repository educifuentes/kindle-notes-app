from src.utils import parse_kindle_html, generate_markdown
from unittest.mock import patch
from datetime import datetime
import os

def main():
    with open('test/Flow-Notebook.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    fixed_now = datetime(2026, 1, 11, 12, 0, 0)
    
    with patch('src.utils.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_now
        df, meta = parse_kindle_html(html)
        markdown = generate_markdown(df, meta)
        
    with open('tests/expected_flow_notebook.md', 'w', encoding='utf-8') as f:
        f.write(markdown)

if __name__ == "__main__":
    main()
