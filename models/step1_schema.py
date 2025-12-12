from pydantic import BaseModel
from typing import List, Optional

class Step1OCRResponse(BaseModel):
    raw_tokens: List[str]
    currency_hint: Optional[str] = None
    confidence: float

class GuardrailResponse(BaseModel):
    status: str
    reason: str
