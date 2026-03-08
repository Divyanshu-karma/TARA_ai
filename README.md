# TARA AI — Trademark Application Risk Analyzer

**TARA AI** is an AI-powered trademark analysis system that evaluates trademark applications and generates a structured legal risk assessment based on USPTO TMEP guidelines.

The system analyzes trademark applications to detect:

- Likelihood of confusion with existing marks
- Descriptiveness and genericness risks
- Classification issues
- Structural validation errors
- Legal risks affecting trademark registration

TARA produces a comprehensive legal analysis and strategy recommendations to help improve the chances of trademark approval.

# TradeMark Application Frontend Workflow

- **User Uploads TradeMark Application PDF**
  - │
  - ▼
- **Frontend**
  - │
  - ▼
- **FastAPI Backend**
  - │
  - `PDFProcessor.process_pdf()`
  - │
  - ▼
- **JSON Output Generated**
  - │
  - Saved to: `TM/<serial>.json`
  - │
  - ▼
- **JSON Object goes in for future analysis**

# TARA AI – Trademark Risk Analysis System

TARA AI analyzes a USPTO trademark application and produces a structured legal risk assessment based on TMEP guidelines.

## Pipeline Flow
- **Trademark Application JSON**
  
  ↓
- **Pillar 1 — Structural Application Validation**
  
  ↓
- **Pillar 2 — Identification of Goods/Services Analysis**
  
  ↓
- **Pillar 3 — Multi-Class Legal Compliance Analysis**
  
  ↓
- Output structural validation

## Pillar 1 — TMEP §1401 Class & Structural Validation

### Code Components
- weaviate-client/
- embedding/
- services/
- pillar1_output/

### Purpose
Validates Nice Classification and application structure.

### Responsibilities
- Validate international class numbers
- Verify goods/services classification
- Check specimen availability per class
- Verify fees paid vs number of classes
- Detect misclassified goods/services

### Output-
Class Selected: int
Assessment: string
Suggested Class: int
Confidence: High | Medium | Low

## Pillar 1 Knowledge Base
Semantic + heuristic database derived from the Nice Classification system.
Contains structured descriptions of all international classes.
Database Structure:
nice_goods → Goods classes 1–34,
nice_services → Service classes 35–45.
knowledge_base/
├── nice_goods/
class_01.json
class_02.json ... till
class_34.json
├── nice_services/
class_35.json
class_36.json ... till
class_45.json

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

The system retrieves up to 1000 trademark records (10 pages × 100 records).

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
their is three similarity signals are evaluated:
1) Visual similarity — Method: Jaro-Winkler — Purpose: Textual resemblance.
2) Phonetic similarity — Method: Double Metaphone — Purpose: Sound similarity.
3) Semantic similarity — Method: Sentence-BERT — Purpose: Meaning similarity.
'these are combined into a composite score.

### 5. Conflict Ranking
All retrieved trademarks are scored and ranked.
e.g., Example output:
applied Mark: Marriott International 
conflicting Mark: MARRIOTT INTERNATIONAL'S LI YU 
Serial: 85738109 
Composite Score: 0.879 The system displays the Top-10 highest-risk conflicts.

### 6. Result Archival
All analysis results are stored as JSON for future review.
e.g., Example: `analysis_output/factor1_Marriott_20260305_101522.json`

## Running the System:
1. Install dependencies:
pip install -r requirements.txt 
Main dependencies include:
sentence-transformers, scikit-learn, jellyfish, requests, python-dotenv.
2. Configure environment variables:
Create a `.env` file with:
ATOM_API_KEY=your_api_key 
ATOM_USER_ID=your_user_id 
3. Run the analysis:
pc main.py 
Example input:
mark_text: STARBUCKS 
class : 030 
status (active/pending/dead/all): active 
Example Output:
tOP 10 HIGHEST RISK CONFLICTS...
and so on.

# Instructions for API Access

**Link of website:** https://www.atom.com/dashboard/seller/api-access

**Steps to access the API:**

1. Visit the website and sign up.
2. After signing up, follow these steps:
   - Click on **Create New Key**.
   - Select **Trademark API**.
   - Copy the generated key.
3. In your User Dashboard (top-right corner), find **My ID** and copy the number.

**Set the following environment variables:**

- `ATOM_API_KEY` = *key generated from website*
- `ATOM_USER_ID` = *My ID*

# Trademark Descriptiveness Analyzer

This module assesses whether a proposed trademark is descriptive or generic for the associated goods/services. It is built using state‑of‑the‑art NLP techniques (spaCy, sentence‑transformers, cross‑encoders) and a rule‑based heuristic to produce interpretable risk scores.

## 🧠 Concept
The system combines three complementary approaches:

- **Linguistic analysis** – part‑of‑speech tagging, dictionary checks, n‑gram overlap with the goods.
- **Semantic similarity** – sentence‑transformer embeddings compare the mark to known descriptive terms for the class.
- **Contextual similarity** – a cross‑encoder evaluates how well the mark describes the goods.

## 🔄 Data Flow
1. **Module's input** – JSON containing:
   - Trademark text
   - Description of goods/services
   - Applied class 
2. `TrademarkAnalyzer` (`app/src/main.py`) initializes sub-modules and passes the input.
3. **LinguisticAnalyzer** extracts features from the mark (POS, dictionary ratio, n‑gram overlap, etc.).
4. **EmbeddingSimilarity** computes:
   - Maximum similarity between the mark and descriptive terms for the given class.
   - Similarity between the mark and segments of the goods description.
5. **CrossEncoderSimilarity** computes deep contextual similarity between mark and goods.
6. **DescriptivenessHeuristic** combines all signals using a weighted ensemble to produce final scores and an explanation.

## 🧩 Module Details
### linguistic.py
- **Purpose:** Extract interpretable linguistic features.
- **Key methods:**
  - `pos_tags()` – spaCy POS tagging.
  - `dependency_relations()` – adjective-noun relations.
  - `is_dictionary_word()` – WordNet lookup.
  - `ngram_overlap_with_goods()` – exact n-gram matches.
  - `descriptive_keyword_overlap()` – lemma-based overlap with class-specific terms (from JSON).
- **Output:** Dictionary with POS counts, dictionary word ratio, overlap scores, etc.

### embeddings.py
- **Purpose:** Semantic similarity using sentence-transformers.
- **Key methods:**
  - `max_similarity_to_terms()` – Best match between mark and any class-specific descriptor.
  - `similarity_to_goods_segments()` – Best match between mark and sentences in goods description.
- **Model:** all-MiniLM-L6-v2 (lightweight, good performance).
- Lazy loading: model is downloaded only on first use.

### cross_encoder.py
- **Purpose:** Deep contextual similarity between mark and goods.
- **Key methods:**
  - `similarity()` – Splits goods into sentences, computes cross-encoder scores, returns maximum score.
- Automatic cache clearing if model files are corrupted, with fallback models:
  - primary: `cross-encoder/stsb-roberta-large`
  - fallback: `stsb-distilroberta-base`, `ms-marco-MiniLM-L-6-v2`

### heuristics.py
- **Purpose:** Combine scores from modules into final risk scores and generate explanations.
- Weights (configurable):
  - Linguistic: 0.25
  - Embedding (max term): 0.25
  - Embedding (goods): 0.20
  - Cross‑encoder: 0.30
- Also computes a *genericness* score based on dictionary word ratio and cross‑encoder similarity.

## main.py (`src/`)
describes the process orchestrator:
descriptive terms loaded from JSON based on *goods_class*, calls sub-modules, then uses heuristics.assess().

## Response Format:
a) Descriptive Score — higher means more descriptive (0–1)
b) Generic Score — higher means more generic (0–1)
c) Reasons — list of human-readable flags.
