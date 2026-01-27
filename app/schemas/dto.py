from pydantic import BaseModel
from typing import Optional

class AnalyzeResponse(BaseModel):
  category: str
  suggested_reply: str
  confidence: Optional[float] = None
  extracted_chars: Optional[float] = None