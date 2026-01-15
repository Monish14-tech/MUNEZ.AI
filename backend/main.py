from fastapi import FastAPI, HTTPException
from pathlib import Path
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Optional, Dict, Any
from groq import Groq
from huggingface_hub import InferenceClient

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    message: str
    mode: str = "chat"

SYSTEM_PROMPTS = {
    "chat": "You are a helpful AI assistant for students and developers. Answer questions clearly and concisely.",
    "summarize": "You are an expert summarizer. Provide a concise summary of the following text, capturing the main points.",
    "code_explain": "You are a coding tutor. Explain the following code step-by-step for a beginner.",
    "grammar": "You are a grammar corrector. Correct the grammar of the following text and provide a brief explanation of the changes."
}

class AIProviderClient:
    """Unified AI client with automatic fallback across multiple providers"""
    
    def __init__(self):
        # Initialize all available providers
        self.providers = []
        
        # 1. Groq (Primary - Fastest)
        if os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY") != "your_groq_api_key_here":
            try:
                self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                self.providers.append(("Groq", self._call_groq))
                logger.info("✅ Groq API initialized")
            except Exception as e:
                logger.warning(f"⚠️ Groq initialization failed: {e}")
        

        # 3. Hugging Face (Tertiary)
        if os.getenv("HUGGINGFACE_API_KEY") and os.getenv("HUGGINGFACE_API_KEY") != "your_huggingface_api_key_here":
            try:
                self.hf_client = InferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))
                self.providers.append(("Hugging Face", self._call_huggingface))
                logger.info("✅ Hugging Face API initialized")
            except Exception as e:
                logger.warning(f"⚠️ Hugging Face initialization failed: {e}")
        
        # 4. Gemini (Fallback)
        if os.getenv("GEMINI_API_KEY"):
            try:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.providers.append(("Gemini", self._call_gemini))
                logger.info("✅ Gemini API initialized")
            except Exception as e:
                logger.warning(f"⚠️ Gemini initialization failed: {e}")
        
        if not self.providers:
            logger.error("❌ No API providers configured! Please add at least one API key to .env")
    
    def _call_groq(self, prompt: str, system_instruction: str) -> str:
        """Call Groq API"""
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and powerful
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        return response.choices[0].message.content
    

    def _call_huggingface(self, prompt: str, system_instruction: str) -> str:
        """Call Hugging Face Inference API"""
        full_prompt = f"{system_instruction}\n\nUser: {prompt}\nAssistant:"
        response = self.hf_client.text_generation(
            full_prompt,
            model="meta-llama/Meta-Llama-3-70B-Instruct",
            max_new_tokens=2048,
            temperature=0.7
        )
        return response
    
    def _call_gemini(self, prompt: str, system_instruction: str) -> str:
        """Call Gemini API"""
        model = genai.GenerativeModel('gemini-flash-latest')
        full_prompt = f"System Instruction: {system_instruction}\n\nUser Message: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    
    def generate(self, prompt: str, mode: str = "chat") -> Dict[str, Any]:
        """
        Generate response with automatic fallback across providers
        Returns: {"reply": str, "provider": str}
        """
        system_instruction = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["chat"])
        
        if not self.providers:
            raise HTTPException(
                status_code=500, 
                detail="No API providers configured. Please add API keys to .env file."
            )
        
        last_error = None
        
        # Try each provider in order
        for provider_name, provider_func in self.providers:
            try:
                logger.info(f"🔄 Attempting {provider_name}...")
                response_text = provider_func(prompt, system_instruction)
                logger.info(f"✅ Success with {provider_name}")
                return {
                    "reply": response_text,
                    "provider": provider_name
                }
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a quota/rate limit error
                if any(keyword in error_msg for keyword in ['quota', 'rate limit', 'limit exceeded', '429']):
                    logger.warning(f"⚠️ {provider_name} quota exceeded, trying next provider...")
                else:
                    logger.warning(f"⚠️ {provider_name} error: {e}, trying next provider...")
                
                last_error = e
                continue
        
        # All providers failed
        raise HTTPException(
            status_code=500,
            detail=f"All API providers failed. Last error: {str(last_error)}"
        )

# Initialize the unified client
ai_client = AIProviderClient()

@app.post("/api/message")
async def chat(prompt: Prompt):
    """
    Chat endpoint with automatic multi-provider fallback
    """
    try:
        result = ai_client.generate(prompt.message, prompt.mode)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def read_root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/health")
def health_check():
    """Health check endpoint showing available providers"""
    return {
        "status": "healthy",
        "providers": [name for name, _ in ai_client.providers],
        "total_providers": len(ai_client.providers)
    }
