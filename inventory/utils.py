import os
import shutil
from datetime import datetime
from django.conf import settings


def backup_to_google_drive():
    """
    Backup database to Google Drive
    Note: This requires Google Drive API credentials to be set up.
    For now, we'll create a local backup that can be manually uploaded.
    """
    try:
        # Create backups directory
        backup_dir = settings.BASE_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup database
        db_path = settings.DATABASES['default']['NAME']
        backup_file = backup_dir / f'db_backup_{timestamp}.sqlite3'
        
        shutil.copy2(db_path, backup_file)
        
        return f"Backup created: {backup_file.name}"
        
    except Exception as e:
        raise Exception(f"Backup failed: {str(e)}")


def setup_google_drive():
    """
    Set up Google Drive API credentials
    This function should be called once to authenticate with Google Drive
    """
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = None
    
    token_path = settings.BASE_DIR / 'token.pickle'
    
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_DRIVE_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)


def upload_to_google_drive(file_path):
    """
    Upload a file to Google Drive
    """
    try:
        from googleapiclient.http import MediaFileUpload
        
        service = setup_google_drive()
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'mimeType': 'application/octet-stream'
        }
        
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return f"File uploaded to Google Drive with ID: {file.get('id')}"
        
    except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")
