from pydantic import BaseModel
from typing import Optional
from app.domain.email_category import EmailCategory

class AnalyzeResponse(BaseModel):
  category: EmailCategory
  suggested_reply: str
  confidence: Optional[float] = None
  extracted_chars: Optional[int] = None
  content: Optional[str] = None
  reason: Optional[str] = None