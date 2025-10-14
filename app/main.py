from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
import time
import uuid
import json

from app.database import get_db
from app.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ChatCompletionChoice,
)
from app.mcp_router import router as mcp_router
from app.tool_utils import execute_tool

app = FastAPI()
app.include_router(mcp_router, prefix="/api/v1")


