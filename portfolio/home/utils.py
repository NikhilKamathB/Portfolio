from datetime import datetime
from django.conf import settings
from django.utils import timezone
from collections import defaultdict
from django.core.mail import send_mail
from typing import List, DefaultDict, Tuple
from calendar import HTMLCalendar, month_name
from dateutil.relativedelta import relativedelta
from home.validators import CalendarData, CalendarEvent


def send_email_utils(email: str, message: str) -> None:
    """
    Send an email.
    """
    subject = settings.DEFAULT_EMAIL_SUBJECT
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email, settings.DEFAULT_NIKHIL_EMAIL])

def get_months_years() -> List[Tuple[int, int]]:
    """
    Get a list of months and years for the next settings.QUERY_DAYS
    """
    time = []
    now = timezone.now()
    end_data = now + timezone.timedelta(days=settings.QUERY_DAYS)
    current_date = now
    while current_date <= end_data:
        time.append((current_date.month, current_date.year))
        current_date += relativedelta(months=1)
    return time


class Calendar(HTMLCalendar):
    
    """
    Custom calendar class.
    """
    
    def __init__(self, year: int = None, month: int = None, firstweekday: int = 0, show_event_summary: bool = False, calendar_data: List[CalendarData] = None) -> None:
        super().__init__(firstweekday)
        self.year = year
        self.month = month
        self.show_event_summary = show_event_summary
        self.events = self._map_events_to_days(calendar_data)
    
    def _map_events_to_days(self, calendar_data: List[CalendarData]) -> DefaultDict[str, List[CalendarEvent]]:
        events = []
        for account in calendar_data:
            if account.items: 
                events.extend(account.items)
        mapped_events = defaultdict(list)
        for event in events:
            start_date = event.start
            if start_date:
                mapped_events[start_date.dateTime].append(event)
        return mapped_events
    
    def formatday(self, day: int, events: List[CalendarEvent]) -> str:
        if day != 0:
            d = ""
            for idx, event in enumerate(events):
                start_time = datetime.fromisoformat(event.start.dateTime)
                start_time = start_time.astimezone(timezone.get_current_timezone())
                end_time = datetime.fromisoformat(event.end.dateTime)
                end_time = end_time.astimezone(timezone.get_current_timezone())
                time_info = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
                event_title = event.summary if self.show_event_summary else f"Event {idx + 1}"
                d += f"<li>{event_title} - {time_info}</li>"
            now = datetime.now()
            if now.day == day and now.month == self.month and now.year == self.year:
                day_span = f"<span><div class='today'>{day}</div></span>"
            else:
                day_span = f"<span>{day}</span>"
            return f"<td><div class='day'>{day_span}<ul>{d}</ul></div></td>"
        return "<td style='border: none;'></td>"

    def formatweek(self, theweek: List[Tuple[int, int]], events: List[CalendarEvent]) -> str:
        """
        Return a complete week as a table row.
        """
        week = ""
        for d, weekday in theweek:    
            day_events = []
            for event in events:
                start_date_iso = datetime.fromisoformat(event.start.dateTime)
                if start_date_iso.day == d:
                    day_events.append(event)
            week += self.formatday(d, day_events)
        return f"<tr>{week}</tr>"

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr><th colspan="7" class="%s"><div class="mb-4">%s</div></th></tr>' % (
            self.cssclass_month_head, s)

    def formatmonth(self, theyear: int, themonth: int, withyear: bool = True) -> str:
        """
        Return a formatted month as a table.
        """
        # Get events for the month
        events = []
        for date in self.events.keys():
            date_iso = datetime.fromisoformat(date)
            if date_iso.year == theyear and date_iso.month == themonth:
                events.extend(self.events[date])
        events.sort(key=lambda x: datetime.fromisoformat(x.start.dateTime))
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="%s">' % (
            self.cssclass_month))
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, events))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)