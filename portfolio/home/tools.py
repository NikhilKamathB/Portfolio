import os
from typing import Any, Type
from datetime import datetime
from django.conf import settings
from langchain.tools import BaseTool
from googleapiclient.discovery import build
from pydantic import BaseModel, BaseSettings, Field
from google_auth_oauthlib.flow import InstalledAppFlow


class GoogleCalendarEventSchema(BaseModel):

    time: str = Field(..., description="Time of the event in HH:MM format.")
    date: str = Field(..., description="Date of the event in MM-DD-YYYY format.")
    duration: int = Field(default=30, description="Duration of the event in minutes.")


class GoogleCalendarEventGenerator(BaseTool, BaseSettings):

    name: str = "google_calendar_event_generator"
    description: str = '''
    Use this tool when you need to generate or create a google calendar event.
    See to it that the there are three parameters time, date and duration.
    The time parameter must be in "HH:MM" format.
    The date parameter must be in "MM-DD-YYYY" format.
    The duration parameter must be a numeric value.
    If the above conditions are not met, return a text with the following message "Please check your time, date and duration format, they must be in "HH:MM", "MM-DD-YYYY" and numeric format respectively.".
    '''
    args_schema: Type[BaseModel] = GoogleCalendarEventSchema
    scopes: list = ['https://www.googleapis.com/auth/calendar']

    def _run(self, time: str, date: str, duration: int = 30):
        flow = InstalledAppFlow.from_client_secrets_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), self.scopes)
        credentials = flow.run_local_server(port=0)
        service = build('calendar', 'v3', credentials=credentials)
        time_obj = datetime.strptime(time, "%H:%M")
        date_obj = datetime.strptime(date, "%m-%d-%Y")
        event = settings.EVENT_BODY
        event['start']['dateTime'] = event['start']['dateTime'].format(start_time=(date_obj + datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute)).strftime("%Y-%m-%dT%H:%M:%S"))
        event['end']['dateTime'] = event['end']['dateTime'].format(end_time=(date_obj + datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=duration*60)).strftime("%Y-%m-%dT%H:%M:%S"))
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"

    def _arun(self, *args: Any, **kwargs: Any):
        raise NotImplementedError("This tool does not support asynchronous execution.")