from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

# Ensure models are cached to the runtime disk (important for Hugging Face Spaces)
os.environ["HF_HOME"] = "/tmp/huggingface"

# Import your analyzer
from app.src.main import TrademarkAnalyzer

app = FastAPI(title="Trademark Descriptiveness API")

# Check that the data file exists (optional, but helpful)
data_path = "app/data/descriptive_keywords.json"
if not os.path.exists(data_path):
    print(f"Warning: Data file not found at {data_path}. Keyword overlap will be disabled.")

# Initialize analyzer
analyzer = TrademarkAnalyzer(descriptive_keywords_path=data_path)

class AnalyzeRequest(BaseModel):
    mark: str
    goods: str
    goods_class: Optional[str] = None

class AnalyzeResponse(BaseModel):
    descriptive_score: float
    generic_score: float
    reasons: list[str]
    explanation: str
    details: dict

@app.get("/")
def read_root():
    return {"message": "Trademark API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    try:
        result = analyzer.analyze(
            mark=request.mark,
            goods=request.goods,
            goods_class=request.goods_class
        )
        return AnalyzeResponse(**result)
    except Exception as e:
        # Log the error (optional)
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))