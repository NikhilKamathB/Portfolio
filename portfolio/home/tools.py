import os
import copy
import json
import datetime
from typing import Any, Optional
from django.conf import settings
from langchain.tools import BaseTool
from googleapiclient.discovery import build
from pydantic import BaseModel, Field
from google_auth_oauthlib.flow import InstalledAppFlow

class GoogleCalendarEventSchema(BaseModel):

    period: dict = Field(..., description="Period of the event information as dict.")


class GoogleCalendarEventGeneratorTool(BaseTool):
    
    """
        Tool to create a google calendar event.
    """

    name: str = "google_calendar_event_generator_tool"
    description: str = settings.LANGCHAIN_GOOGLE_CALENDAR_EVENT_SCHEMA_TOOL_DESC
    args_schema: Optional[GoogleCalendarEventSchema] = GoogleCalendarEventSchema
    scopes: list = ['https://www.googleapis.com/auth/calendar']

    def __init__(self):
        super().__init__()
        self.return_direct = True

    def _run(self, period:str):
        period = json.loads(period)
        if not period.get("date", None):
            date = (datetime.datetime.now() + datetime.timedelta(days=settings.DEFAULT_EVENT_DELTA_DAYS)).strftime("%m-%d-%Y")
        else:
            date = period.get("date")
        if not period.get("time", None):
            time = settings.DEFAULT_EVENT_TIME
        else:
            time = period.get("time")
        flow = InstalledAppFlow.from_client_secrets_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), self.scopes)
        credentials = flow.run_local_server(port=0)
        service = build('calendar', 'v3', credentials=credentials)
        date_obj = datetime.datetime.strptime(date, "%m-%d-%Y")
        time_obj = datetime.datetime.strptime(time, "%H:%M")
        event = copy.deepcopy(settings.EVENT_BODY)
        event['start']['dateTime'] = event['start']['dateTime'].format(start_time=(date_obj + datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute)).strftime("%Y-%m-%dT%H:%M:%S"))
        event['end']['dateTime'] = event['end']['dateTime'].format(end_time=(date_obj + datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=period.get("duration", 60)*60)).strftime("%Y-%m-%dT%H:%M:%S"))
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"

    def _arun(self, *args: Any, **kwargs: Any):
        raise NotImplementedError("This tool does not support asynchronous execution.")