from pydantic import BaseModel
from typing import Annotated, Union, Any, List, Dict, Optional


class PolicyTranslationRequest(BaseModel):
    kyvernoPolicy: str
    source_lang: str = "Kyverno"
    target_lang: str = "Rego"


class PolicyTranslationResponse(BaseModel):
    policy: str
    response: str = "Policy translated successfully"
    metadata: Optional[Dict[str, Any]] = None
