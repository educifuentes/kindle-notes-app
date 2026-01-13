# Kindle HTML Structure Analysis

Based on the `sample.html` file, here is the breakdown of the HTML structure and the proposed extraction logic.

## 1. Global Metadata (Book Info)
These elements appear once at the top of the body.

| Class Name | Content | Extraction Logic |
| :--- | :--- | :--- |
| `.bookTitle` | Title of the book | `soup.find(class_='bookTitle').get_text(strip=True)` |
| `.authors` | Author(s) | `soup.find(class_='authors').get_text(strip=True)` |

## 2. Content Sections
The content is a flat list of headings and divs. We need to iterate through them sequentially to handle the "current section" context.

### Section Headings (`.sectionHeading`)
- **Appears**: Spasmodically, marking chapters or major divisions.
- **Content**: Roman numerals (e.g., "I", "II") or Chapter names.
- **Logic**: When encountered, update the `current_section` variable. All subsequent notes belong to this section until a new one appears.

### Notes and Highlights Pair
Each item consists of a **Heading** followed immediately by **Text**.

#### A. Heading (`.noteHeading`)
Contains metadata about the item.
**Format variants:**
1.  **Highlight**: `Highlight (<color>) - <Book Title> > Page <N> · Location <M>`
    -   *Example*: `Highlight (yellow) - Literatura infantil > Page 5 · Location 38`
2.  **Note**: `Note - <Book Title> > Page <N> · Location <M>`
    -   *Example*: `Note - Literatura infantil > Page 10 · Location 114`

**Extraction Regex:**
-   **Type**: Starts with "Highlight" or "Note".
-   **Color**: If Highlight, captured in `span` or parentheses? *Actually, the color is text inside the parentheses `(yellow)` but also often wrapped in a span with class `highlight_<color>` inside the element.*
-   **Location**: `Location (\d+)`
-   **Page**: `Page (\d+)` (Optional)

#### B. Text (`.noteText`)
Contains the actual highlighted text or the user's written note.

## Proposed Data Model

| Field | Source | Description |
| :--- | :--- | :--- |
| `type` | `.noteHeading` | 'Highlight' or 'Note' |
| `color` | `.noteHeading` | 'yellow', 'blue', etc. (Only for Highlights) |
| `section` | `current_section` | The most recent `.sectionHeading` encountered. |
| `page` | `.noteHeading` | Page number if present. |
| `location` | `.noteHeading` | Location number. |
| `content` | `.noteText` | The text of the highlight or note. |

## Parsing Strategy
1.  Initialize `current_section = None`.
2.  Find all elements with classes `sectionHeading`, `noteHeading`, `noteText`.
3.  Iterate through them:
    -   If `sectionHeading`: Update `current_section`.
    -   If `noteHeading`: Parse metadata (Location, Page, Type). Prepare a new item.
    -   If `noteText`: Assign content to the current item.
