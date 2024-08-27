from typing import Optional
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    success: bool
    message: str
    description: str

    
class TimeData(BaseModel):

    dateTime: str
    timeZone: str


class CalendarEvent(BaseModel):

    id: str
    status: str
    summary: Optional[str] = ""
    start: Optional[TimeData] = None
    end: Optional[TimeData] = None


class CalendarData(BaseModel):
    
    summary: Optional[str] = ""
    description: Optional[str] = ""
    timeZone: str
    nextSyncToken: Optional[str] = ""
    items: Optional[list[CalendarEvent]] = []