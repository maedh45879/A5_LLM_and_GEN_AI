from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    message: str = "Service healthy"


class VoiceRequest(BaseModel):
    audio_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded audio payload (wav/pcm). Optional for text-only testing.",
    )
    text: Optional[str] = Field(
        default=None, description="Fallback text input when audio is unavailable."
    )


class VoiceResponse(BaseModel):
    text: str
    audio_base64: Optional[str] = None
    intent: Optional[str] = None


class ReservationRequest(BaseModel):
    name: str
    date: str = Field(description="Date in YYYY-MM-DD format")
    time: str = Field(description="Time in HH:MM format")
    guests: int
    special_requests: Optional[str] = None


class ReservationResponse(BaseModel):
    confirmed: bool
    reference: str
    message: str


class OrderItem(BaseModel):
    item: str
    quantity: int = Field(default=1, ge=1)
    notes: Optional[str] = None


class OrderRequest(BaseModel):
    table: Optional[str] = None
    items: List[OrderItem]


class OrderResponse(BaseModel):
    confirmed: bool
    summary: str
    total_items: int
    message: str


class MenuQuery(BaseModel):
    question: str


class MenuAnswer(BaseModel):
    answer: str
    sources: List[str] = []


class GeneralInfoRequest(BaseModel):
    question: str


class GeneralInfoResponse(BaseModel):
    answer: str
