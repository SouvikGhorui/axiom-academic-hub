from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

def get_calendar_service(refresh_token: str, client_id: str, client_secret: str):
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build('calendar', 'v3', credentials=creds)

async def check_calendar_conflicts(start_time: datetime, end_time: datetime, refresh_token: str, client_id: str, client_secret: str) -> list:
    """
    Fetches events within a given time window to check for conflicts.
    """
    service = get_calendar_service(refresh_token, client_id, client_secret)
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])

async def batch_inject_study_blocks(study_blocks_data: list, refresh_token: str, client_id: str, client_secret: str):
    """
    Injects multiple study blocks into Google Calendar using batching.
    `study_blocks_data` should be a list of dicts with 'title', 'start_time', 'end_time'.
    """
    service = get_calendar_service(refresh_token, client_id, client_secret)
    batch = service.new_batch_http_request()
    
    def callback(request_id, response, exception):
        if exception is not None:
            print(f"Error injecting block: {exception}")
        else:
            print(f"Injected block successfully: {response.get('id')}")

    for block in study_blocks_data:
        event = {
            'summary': f"Study: {block['title']}",
            'start': {'dateTime': block['start_time'].isoformat() + 'Z'},
            'end': {'dateTime': block['end_time'].isoformat() + 'Z'},
            'description': 'Automated Academic Hub Study Block'
        }
        batch.add(service.events().insert(calendarId='primary', body=event), callback=callback)
        
    batch.execute()
