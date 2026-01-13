from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY not found in environment variables.")
else:
    genai.configure(api_key=api_key)

class Prompt(BaseModel):
    message: str
    mode: str = "chat"

SYSTEM_PROMPTS = {
    "chat": "You are a helpful AI assistant for students and developers. Answer questions clearly and concisely.",
    "summarize": "You are an expert summarizer. Provide a concise summary of the following text, capturing the main points.",
    "code_explain": "You are a coding tutor. Explain the following code step-by-step for a beginner.",
    "grammar": "You are a grammar corrector. Correct the grammar of the following text and provide a brief explanation of the changes."
}

@app.post("/chat")
async def chat(prompt: Prompt):
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")
    
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        system_instruction = SYSTEM_PROMPTS.get(prompt.mode, SYSTEM_PROMPTS["chat"])
        full_prompt = f"System Instruction: {system_instruction}\n\nUser Message: {prompt.message}"
        
        response = model.generate_content(full_prompt)
        
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')
