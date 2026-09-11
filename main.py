import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import edge_tts

app = FastAPI(title="Edge TTS Microservice")

# App မှ တိုက်ရိုက်ခေါ်ယူနိုင်ရန် CORS အပြည့်အဝ ဖွင့်ပေးထားပါသည်
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice: str = "my-MM-ThihaNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Edge TTS Microservice",
        "endpoints": ["/api/edge-tts", "/edge-tts", "/tts"]
    }

@app.post("/api/edge-tts")
@app.post("/edge-tts")
@app.post("/tts")
async def generate_speech(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        communicate = edge_tts.Communicate(
            text=req.text,
            voice=req.voice,
            rate=req.rate,
            pitch=req.pitch
        )
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as err:
        print(f"TTS Error: {err}")
        raise HTTPException(status_code=500, detail=str(err))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
