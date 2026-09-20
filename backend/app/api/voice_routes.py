from fastapi import APIRouter, Depends
from ..auth import current_user

router = APIRouter(prefix="/api/voice", tags=["Voice"])

@router.get("/status")
def voice_status(user=Depends(current_user)):
    return {
        "enabled": True,
        "mode": "browser_web_speech",
        "languages": ["en-IN", "ta-IN", "hi-IN"],
        "message": "AARAMBH voice input is handled by the browser Web Speech API in the prototype."
    }
