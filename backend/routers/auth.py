from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os
from urllib.parse import quote
import requests
from jose import jwt, JWTError
from datetime import datetime, timedelta

from database import get_db
from models import User, OAuthToken

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "dummy_client_id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "dummy_client_secret")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-for-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

from google_utils import SCOPES

@router.get("/login")
async def login():
    # Define scopes needed for Classroom, Calendar, and Gmail
    scope_str = " ".join(SCOPES)
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"response_type=code&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"scope={scope_str}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(code: str, db: AsyncSession = Depends(get_db)):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    print(f"Exchanging code for token. Redirect URI: {GOOGLE_REDIRECT_URI}")
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        print(f"Token exchange failed. Status: {response.status_code}, Body: {response.text}")
        raise HTTPException(status_code=400, detail=f"Failed to retrieve token from Google: {response.text}")
        
    print("Token retrieved successfully.")
    tokens = response.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in", 3600)
    
    # Get user info
    print("Retrieving user info from Google...")
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_response.json()
    print(f"User info retrieved: {user_info.get('email')}")
    
    # Upsert user
    print("Upserting user in database...")
    result = await db.execute(select(User).where(User.email == user_info["email"]))
    user = result.scalars().first()
    
    if not user:
        user = User(
            email=user_info["email"],
            name=user_info.get("name"),
            picture_url=user_info.get("picture")
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    if refresh_token:
        # Save token to OAuthToken table
        # In a real app we would use Fernet to encrypt this before saving
        encrypted_token = refresh_token # Plaintext for now, implement cryptography later
        
        # Check if we already have a google token
        token_result = await db.execute(
            select(OAuthToken)
            .where(OAuthToken.user_id == user.id)
            .where(OAuthToken.scope_key == "google_all")
        )
        existing_token = token_result.scalars().first()
        
        if existing_token:
            existing_token.encrypted_refresh_token = encrypted_token
            existing_token.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        else:
            new_token = OAuthToken(
                user_id=user.id,
                scope_key="google_all",
                encrypted_refresh_token=encrypted_token,
                token_expiry=datetime.utcnow() + timedelta(seconds=expires_in)
            )
            db.add(new_token)
            
        await db.commit()
        print("Token and user saved to database.")
    
    # Create Local JWT
    print("Creating local JWT...")
    to_encode = {"sub": user.email, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    
    # Redirect to the frontend with the token and user name
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    safe_name = quote(user.name or "Student")
    redirect_url = f"{frontend_url}/?token={encoded_jwt}&name={safe_name}"
    print(f"Redirecting back to frontend: {redirect_url}")
    return RedirectResponse(url=redirect_url)
