# Trademark Conflict Analysis Module

*(Autonomous USPTO Examiner System)*

This module performs automated trademark conflict detection using DuPont Factor-1 (Similarity of the Marks). It retrieves trademarks from the Atom Trademark API, processes them, and computes semantic, phonetic, and visual similarity scores to identify potential conflicts.

## Module Workflow:

- **Trademark Text** (from given Trademark Application)
  - ↓
- **Atom API Search**
  - ↓
- **First 300 trademarks returned**
  - ↓
- **JSON saved** → `search_data/`
  - ↓
- **extract_pairs.py**
  - ↓
- **(trademark_name, serial_number)**
  - ↓
- **factor1.py**
  - ↓
- **DuPont Factor-1 Similarity Score**

## Module Capabilities

This module performs the following operations:

### 1. Trademark Retrieval
Queries the Atom Trademark Search API using:
- Trademark keyword
- International class (optional)
- Filing status (active / pending / dead)

The system retrieves up to 300 trademark records (3 pages × 100 records).

### 2. Data Storage
API responses are saved locally for:
- debugging
- reproducibility
- further analysis

Location: `search_data/`
Example file: `search_STARBUCKS_20260304_125526.json`

### 3. Trademark Parsing
The parser (`extract_pairs.py`) extracts:
- `(trademark_name, serial_number)` from each trademark record.
It also handles edge cases:
- Missing trademark_name,
- Missing serial_number,
- Nested JSON structures.

### 4. Similarity Analysis (DuPont Factor-1)
The module computes similarity between:
a) Applied Mark (user input) vs b) Conflicting Mark (retrieved trademark)
their three similarity signals are evaluated:
d) Visual similarity — Method: Jaro-Winkler — Purpose: Textual resemblance.
e) Phonetic similarity — Method: Double Metaphone — Purpose: Sound similarity.
f) Semantic similarity — Method: Sentence-BERT — Purpose: Meaning similarity.
'these are combined into a composite score.

### 5. Conflict Ranking
All retrieved trademarks are scored and ranked.
e.g., Example output:
applied Mark: Marriott International 
dconflicting Mark: MARRIOTT INTERNATIONAL'S LI YU 
sSerial: 85738109 
tComposite Score: 0.879 The system displays the Top-10 highest-risk conflicts.

### 6. Result Archival
All analysis results are stored as JSON for future review.
e.g., Example: `analysis_output/factor1_Marriott_20260305_101522.json`

## Running the System:
1. Install dependencies:
pip install -r requirements.txt 
tMain dependencies include:
sentence-transformers, scikit-learn, jellyfish, requests, python-dotenv.
2. Configure environment variables:
cCreate a `.env` file with:
atm_api_key=your_api_key 
atm_user_id=your_user_id 
c3. Run the analysis:
pc main.py 
eExample input:
dmark_text: STARBUCKS 
dclass : 030 
dstatus (active/pending/dead/all): active 
eExample Output:
tOP 10 HIGHEST RISK CONFLICTS...
and so on.
