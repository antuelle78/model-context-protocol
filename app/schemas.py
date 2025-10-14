from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

# OpenAI compatible schemas
class ChatMessage(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: str
    stream: bool = False
    tool_calls: Optional[List[Dict[str, Any]]] = None

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]

class GetStockPriceArgs(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol, e.g., 'AAPL' for Apple.")

