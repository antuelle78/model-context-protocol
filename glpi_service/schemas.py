from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class TicketBase(BaseModel):
    number: str
    short_description: str
    assignment_group: str
    priority: str
    state: str
    sys_updated_on: str

class TicketCreate(TicketBase):
    pass

class TicketUpdate(TicketBase):
    pass

class Ticket(TicketBase):
    id: int

    model_config = {"from_attributes": True}

# New schemas for ticket creation
class TicketCreateRequest(BaseModel):
    short_description: str
    assignment_group: str
    priority: str

class TicketCreationResponse(BaseModel):
    number: str
    short_description: str
    assignment_group: str
    priority: str
    state: str
    sys_updated_on: str

# User schemas
class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}

# OpenAI compatible schemas
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: str
    stream: bool = False

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

# Tool argument schemas
class GenerateOpenTicketsByPriorityReportArgs(BaseModel):
    priority: str

class GenerateTicketsByAssignmentGroupReportArgs(BaseModel):
    group: str

class CreateNewTicketArgs(BaseModel):
    short_description: str
    assignment_group: str
    priority: str

class GetGlpiFullAssetDumpArgs(BaseModel):
    itemtype: str
