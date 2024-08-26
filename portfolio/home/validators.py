from typing import Optional
from pydantic import BaseModel, Field


class TimeData(BaseModel):

    dateTime: str = Field(..., description="The date and time of the event.")
    timeZone: str = Field(..., description="The timezone of the event.")


class CalendarEvent(BaseModel):

    id: str
    status: str
    summary: Optional[str] = ""
    # start: TimeData = Field(..., description="The start time of calendar event.")
    # end: TimeData = Field(..., description="The end time of calendar event.")


class CalendarData(BaseModel):
    
    summary: Optional[str] = ""
    description: Optional[str] = ""
    timeZone: str
    nextSyncToken: Optional[str] = ""
    items: Optional[list[CalendarEvent]] = []