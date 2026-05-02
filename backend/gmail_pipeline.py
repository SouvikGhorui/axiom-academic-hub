import os
import base64
import json
import google.generativeai as genai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Ensure GEMINI_API_KEY is set in the environment for LLM extraction
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def authenticate_gmail() -> Credentials:
    """
    Handles OAuth 2.0 authentication for Gmail API.
    Reads from 'credentials.json' (downloaded from GCP Console) 
    and saves the user's session in 'token.json'.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}. Re-authenticating...")
                creds = None

        if not creds:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "Missing 'credentials.json'. Please download your OAuth 2.0 Client ID "
                    "JSON from the Google Cloud Console and place it in this directory."
                )
            
            # Spin up a local server to handle the OAuth callback
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def fetch_course_emails(creds: Credentials, max_results: int = 10) -> list:
    """
    Searches the user's Gmail inbox for syllabus or enrollment emails
    and extracts the plaintext body.
    """
    try:
        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=creds)
        
        # Query tailored for academic emails
        query = 'subject:syllabus OR "Welcome to" OR "enrolled in" OR "course registration"'
        
        print(f"Searching Gmail for query: [{query}]")
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No course-related emails found.")
            return []

        email_bodies = []
        for msg in messages:
            msg_id = msg['id']
            msg_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            
            # Extract plaintext body
            payload = msg_data.get('payload', {})
            body_data = None
            
            # Gmail payloads can be nested (multipart)
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_data = part['body'].get('data')
                        break
            else:
                body_data = payload['body'].get('data')
                
            if body_data:
                # Decode base64url encoded string
                decoded_body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                email_bodies.append(decoded_body)
                
        return email_bodies

    except HttpError as error:
        print(f"An error occurred while fetching emails: {error}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

def extract_courses(email_body: str) -> list:
    """
    Passes the email body to the Gemini LLM to extract structured course data.
    """
    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is missing. Falling back to regex (mocked).")
        return []

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an intelligent data extraction assistant. I will provide you with the text of an email.
    Your task is to extract any university courses the student is enrolled in or receiving a syllabus for.
    
    Email text:
    ---
    {email_body[:3000]} # Truncated to avoid token limits
    ---
    
    Extract the courses and respond ONLY with a JSON array of objects in this exact format:
    [
      {{"course_code": "MATH 201", "course_name": "Linear Algebra"}},
      {{"course_code": "CS 101", "course_name": "Intro to Computer Science"}}
    ]
    If no courses are found, return an empty array: []
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Clean up Markdown JSON blocks if present
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        courses = json.loads(text.strip())
        return courses
        
    except json.JSONDecodeError:
        print("LLM returned invalid JSON.")
        return []
    except Exception as e:
        print(f"LLM extraction error: {e}")
        return []

if __name__ == '__main__':
    print("--- Axiom Gmail Data Pipeline ---")
    try:
        # 1. Authenticate
        credentials = authenticate_gmail()
        print("Successfully authenticated with Google.")
        
        # 2. Fetch Emails
        emails = fetch_course_emails(credentials, max_results=3)
        print(f"Fetched {len(emails)} relevant emails.")
        
        # 3. Extract Courses
        all_extracted_courses = []
        for idx, email_text in enumerate(emails):
            print(f"Analyzing email {idx + 1}...")
            courses = extract_courses(email_text)
            if courses:
                all_extracted_courses.extend(courses)
                
        print("\n--- Final Extracted Courses ---")
        print(json.dumps(all_extracted_courses, indent=2))
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
