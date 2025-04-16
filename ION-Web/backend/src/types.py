from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

class User(BaseModel):
    """User model representing a user in the database"""
    email: EmailStr
    user_id: UUID
    traces: Dict[str, dict] = Field(default_factory=dict)
    messages: Dict[str, dict] = Field(default_factory=dict)

class ChatMessage(BaseModel):
    """Model for individual chat messages"""
    role: str = Field(..., description="Role of the message sender (user/assistant/tool)")
    content: Optional[str] = Field(None, description="Content of the message")
    tool_calls: Optional[List[dict]] = Field(None, description="Tool calls made in the message")
    tool_call_id: Optional[str] = Field(None, description="ID of the tool call this message responds to")

class ChatHistory(BaseModel):
    """Model for chat history"""
    id: str
    messages: List[ChatMessage]

class TraceMetadata(BaseModel):
    """Model for trace metadata"""
    trace_name: str
    trace_description: str
    upload_date: datetime
    status: str = Field(default="not_started", description="Status of trace analysis")
    model: Optional[str] = Field(None, description="Model used for analysis")

class TraceSource(BaseModel):
    """Model for trace sources/citations"""
    file: str
    id: int

class TraceDiagnosis(BaseModel):
    """Model for trace diagnosis"""
    content: str
    sources: List[TraceSource]

class APIResponse(BaseModel):
    """Generic API response model"""
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[dict] = None
    status_code: int

class UploadTraceResponse(BaseModel):
    """Response model for trace upload"""
    message: str
    trace_name: str

class UserResponse(BaseModel):
    """Response model for user operations"""
    user_id: UUID
    message: str
