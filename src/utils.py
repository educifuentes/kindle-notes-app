# ==========================================
# Imports and Constants
# ==========================================
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from .constants import (
    CLASS_BOOK_TITLE,
    CLASS_AUTHORS,
    CLASS_NOTE_HEADING,
    CLASS_NOTE_TEXT,
    CLASS_SECTION_HEADING
)

# ==========================================
# Core Parsing Logic
# ==========================================

def parse_kindle_html(html_content: str) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Parses Kindle highlights HTML file and returns a DataFrame and book metadata.

    Args:
        html_content (str): The raw HTML content from the Kindle export.

    Returns:
        Tuple[pd.DataFrame, Dict[str, str]]: A tuple containing the highlights DataFrame 
                                             and a dictionary of metadata (title, author).
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract metadata
    title_elem = soup.find(class_=CLASS_BOOK_TITLE)
    author_elem = soup.find(class_=CLASS_AUTHORS)
    
    metadata = {
        "title": title_elem.get_text(strip=True) if title_elem else "Unknown Title",
        "author": author_elem.get_text(strip=True) if author_elem else "Unknown Author"
    }
    
    # Process highlights and notes
    rows = []
    
    # State variables for tracking context while iterating
    current_section = None
    current_highlight = None
    is_note_pending = False
    
    # Store pending note metadata if a note comes before a highlight (unlikely but handled)
    pending_loc = None
    pending_page = None
    pending_sub = None
    
    # Find all relevant nodes including section headings
    # We select specific classes to filter out noise
    nodes = soup.find_all(class_=[CLASS_SECTION_HEADING, CLASS_NOTE_HEADING, CLASS_NOTE_TEXT])
    
    for node in nodes:
        text = node.get_text(strip=True)
        classes = node.get("class", [])
        
        if CLASS_SECTION_HEADING in classes:
            current_section = text
            continue

        if CLASS_NOTE_HEADING in classes:
            is_note = "Note" in text and "Highlight" not in text
            location = _extract_location(text)
            page = _extract_page(text)
            sub_section = _extract_sub_section(text)
            
            if not is_note:
                current_highlight = {
                    "location": location,
                    "page": page,
                    "section": current_section,
                    "sub_section": sub_section,
                    "highlighted_text": "",
                    "note": None,
                    "is_important": False,
                    "is_very_important": False
                }
                rows.append(current_highlight)
                is_note_pending = False
            else:
                is_note_pending = True
                pending_loc = location
                pending_page = page
                pending_sub = sub_section

        elif CLASS_NOTE_TEXT in classes:
            if is_note_pending:
                # Attach note to previous highlight or create standalone
                if current_highlight:
                    current_highlight["note"] = text
                    current_highlight.update(_classify_importance(text))
                else:
                    rows.append({
                        "location": pending_loc,
                        "page": pending_page,
                        "section": current_section,
                        "sub_section": pending_sub,
                        "highlighted_text": "",
                        "note": text,
                        **_classify_importance(text)
                    })
                is_note_pending = False
            elif current_highlight:
                current_highlight["highlighted_text"] = text
                    
    df = pd.DataFrame(rows)
    
    # Ensure all required columns exist
    # Ensure all required columns exist
    required_cols = ["location", "page", "section", "sub_section", "highlighted_text", "note", "is_very_important", "is_important"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Reorder columns to match the requirement
    df = df[required_cols]
            
    return df, metadata

# ==========================================
# Extraction Helpers
# ==========================================

def _extract_location(heading_text: str) -> str:
    """Extracts location from Kindle note heading."""
    # Example: "... - Location 123 | ..."
    match = re.search(r"Location (\d+)", heading_text)
    return match.group(1) if match else ""

def _extract_page(heading_text: str) -> str:
    """Extracts page number from Kindle note heading if available."""
    # Example: "... > Page 5 · Location 38"
    match = re.search(r"Page (\d+)", heading_text)
    return match.group(1) if match else ""

def _extract_sub_section(heading_text: str) -> str:
    """Extracts sub-section info from Kindle note heading if present."""
    # Example: "Highlight (yellow) - I. EL CERCADO > Location 33" -> "I. EL CERCADO"
    # Example: "Highlight (yellow) - Chapter 1 | Location 123" -> "Chapter 1"
    match = re.search(r"-\s*(.*?)\s*(?:>|\|)?\s*Location", heading_text)
    if match:
        return match.group(1).strip()
    return ""

# ==========================================
# Classification Helpers
# ==========================================

def _classify_importance(note_text: str) -> Dict[str, bool]:
    """
    Classifies importance based on markers in the user note.
    Rules:
    - is_very_important: if note starts with "wow iii" (case insensitive)
    - is_important: if note starts with "wow" (case insensitive)
    """
    if not note_text:
        return {"is_important": False, "is_very_important": False}
    
    note_lower = note_text.strip().lower()
    
    # Check for "wow iii" first (more specific)
    is_very = note_lower.startswith("wow iii")
    
    # Check for "wow"
    # Logic: If it starts with "wow iii", it also starts with "wow".
    # The user defined them as separate rules. 
    # Usually "Very Important" implies "Important".
    is_imp = note_lower.startswith("wow")
    
    return {
        "is_important": is_imp,
        "is_very_important": is_very
    }

# ==========================================
# Output Generation
# ==========================================

def generate_markdown(df: pd.DataFrame, metadata: Dict[str, str]) -> str:
    """
    Generates a Markdown document from the highlights DataFrame.
    """
    if df.empty:
        return f"# {metadata['title']}\n\nNo highlights found."

    lines = [
        f"# {metadata['title']}",
        f"**Author:** {metadata['author']}",
        f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        ""
    ]

    for _, row in df.iterrows():
        # Importance and Location markers
        meta_label = ""
        if row['is_very_important']:
            meta_label = "🔥 **VERY IMPORTANT** "
        elif row['is_important']:
            meta_label = "⭐ **IMPORTANT** "

        # Location, Page and Section
        loc_str = f"Loc: {row['location']}" if row['location'] else ""
        page_str = f"Page: {row['page']}" if row['page'] else ""
        
        section_parts = []
        if row['section']:
            section_parts.append(row['section'])
        if 'sub_section' in row and row['sub_section']:
            section_parts.append(row['sub_section'])
        
        section_str = f"Section: {' > '.join(section_parts)}" if section_parts else ""
        
        meta_info = " | ".join(filter(None, [loc_str, page_str, section_str]))
        
        # Formatting Highlight
        if row['highlighted_text']:
            lines.append(f"> {row['highlighted_text']}")
            if meta_info:
                lines.append(f"> *({meta_info})*")
        
        # Formatting Note
        if row['note']:
            lines.append(f"\n{meta_label}**Note:** {row['note']}")
        elif meta_label:
            lines.append(f"\n{meta_label}")

        lines.extend(["", "---", ""])
            
    return "\n".join(lines).strip()
