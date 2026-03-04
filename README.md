Trademark Conflict Analysis Module: folder name: conflict_check
(Autonomous USPTO Examiner System)

This module performs automated trademark conflict detection using DuPont Factor-1 (Similarity of the Marks).
It retrieves trademarks from the Atom Trademark API, processes them, and computes semantic, phonetic, and visual similarity scores to identify potential conflicts.

1. ✅ Using uv (Recommended Modern Way)
uv init
uv add -r requirements.txt
uv sync

2. Verify .env Configuration

Your .env file should contain:

ATOM_API_KEY=your_api_key
ATOM_USER_ID=your_user_id
3. Run the System
    Execute: python main.py
4. Provide Input
Example:
mark_text: STARBUCKS
class : 030
status (active/pending/dead/all): active

What Happens Internally
The system runs this pipeline:

User Input
   ↓
Atom API search
   ↓
300 trademarks fetched
   ↓
JSON saved → search_data/
   ↓
extract_pairs.py parses pairs
   ↓
factor1.py computes similarity
   ↓
Top 10 conflicts printed
   ↓
Full analysis saved → analysis_output/

Example Terminal Output
Searching 'STARBUCKS'

Using JSON file:
search_STARBUCKS_20260304_125526.json

Running DuPont Factor-1 similarity analysis...

TOP 10 HIGHEST RISK CONFLICTS
Applied Mark: STARBUCKS
Conflicting Mark: STARBUCKS COFFEE
Serial: 85723897
Composite Score: 0.93
-------------------------
