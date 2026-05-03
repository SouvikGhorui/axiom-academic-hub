from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import base64
import json
from models import User
from database import get_db

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/gmail")
async def gmail_push(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        if "message" not in body or "data" not in body["message"]:
            return {"status": "invalid payload"}
            
        data = base64.b64decode(body["message"]["data"]).decode()
        payload = json.loads(data)
        
        email = payload.get("emailAddress")
        new_hist = payload.get("historyId")
        
        if not email:
            return {"status": "ignored"}
            
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            return {"status": "ignored"}
            
        from worker import sync_user_gmail
        sync_user_gmail.delay(str(user.id), new_hist)
        
        return {"status": "queued"}
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "error"}

@router.post("/classroom")
async def classroom_push(request: Request, db: AsyncSession = Depends(get_db)):
    # Placeholder for Classroom push notifications via Pub/Sub
    # Similar structure to gmail_push, extracting user and enqueueing
    # worker.sync_user_classroom.delay(...)
    return {"status": "acknowledged"}
