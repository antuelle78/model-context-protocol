from pydantic import BaseModel, EmailStr, Field
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

# Schemas for ServiceNow tool arguments
class GetReportOpenByPriorityArgs(BaseModel):
    priority: str = Field(..., description="The priority of the tickets to include in the report.")

class GetReportByAssignmentGroupArgs(BaseModel):
    assignment_group: str = Field(..., description="The assignment group to filter the report by.")

class CreateNewTicketServiceNowArgs(BaseModel):
    short_description: str = Field(..., description="A short description of the ticket.")
    assignment_group: str = Field(..., description="The group to assign the ticket to.")
    priority: str = Field(..., description="The priority of the ticket.")

# Schemas for GLPI tool arguments
class GetGlpiFullAssetDumpArgs(BaseModel):
    itemtype: str = Field(..., description="The type of asset to dump (e.g., 'Computer', 'Monitor').")

# Microservice Tool Input Schemas
class ServiceNowToolInput(BaseModel):
    servicenow_base_url: Optional[str] = Field(None, description="Base URL for the ServiceNow API.")
    servicenow_username: Optional[str] = Field(None, description="Username for ServiceNow API authentication.")
    servicenow_password: Optional[str] = Field(None, description="Password for ServiceNow API authentication.")

class GLPIToolInput(BaseModel):
    glpi_base_url: Optional[str] = Field(None, description="Base URL for the GLPI API.")
    glpi_app_token: Optional[str] = Field(None, description="Application token for GLPI API authentication.")
    glpi_access_token: Optional[str] = Field(None, description="Access token for GLPI API authentication.")

class FetchAllTicketsInput(BaseModel):
    service_name: str = Field(..., description="The name of the service to fetch tickets from (e.g., 'glpi', 'servicenow').")
    servicenow_base_url: Optional[str] = Field(None, description="Base URL for the ServiceNow API.")
    servicenow_username: Optional[str] = Field(None, description="Username for ServiceNow API authentication.")
    servicenow_password: Optional[str] = Field(None, description="Password for ServiceNow API authentication.")
    glpi_base_url: Optional[str] = Field(None, description="Base URL for the GLPI API.")
    glpi_app_token: Optional[str] = Field(None, description="Application token for GLPI API authentication.")
    glpi_access_token: Optional[str] = Field(None, description="Access token for GLPI API authentication.")

