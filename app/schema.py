from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class AgentTrace(BaseModel):
    # Allowed intents including profile_summary for personal introductions
    intent: Literal[
        "profile_summary",
        "project_summary",
        "reading_suggestion",
        "job_fit",
        "refusal",
        "clarification",
        "external_api_query",
        "out_of_scope"
    ]
    fields_read: List[str] = Field(default_factory=list)
    capability: Literal[
        "answer_from_record",
        "answer_from_external_api",
        "refuse_unauthorized_fact",
        "ask_clarification",
        "out_of_scope_rejection"
    ]
    external_service_used: Optional[str] = None
    missing_facts: List[str] = Field(default_factory=list)
    creativity_meta: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    # Visitor query payload
    message: str = Field(..., max_length=1000)

class ChatResponse(BaseModel):
    # Structured response with conversational output and explainability trace
    answer: str
    trace: AgentTrace