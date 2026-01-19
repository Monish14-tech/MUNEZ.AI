from fastapi import FastAPI, HTTPException
from pathlib import Path
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, Any
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
    """Robust AI client with multi-key rotation and smart model fallback"""
    
    def __init__(self):
        self.groq_keys = self._get_keys("GROQ_API_KEY")
        self.hf_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # Models to try in order of preference
        self.groq_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768"
        ]
        
        # Initialize providers list for visibility (Health check)
        self.providers = []
        if self.groq_keys:
            self.providers.append(("Groq (Dynamic Rotation)", self._call_groq_with_fallback))
        if self.hf_key and self.hf_key != "your_huggingface_api_key_here":
            self.hf_client = InferenceClient(token=self.hf_key)
            self.providers.append(("Hugging Face (Backup Llama)", self._call_huggingface))

    def _get_keys(self, env_var: str) -> list:
        """Parse comma-separated keys from env"""
        val = os.getenv(env_var, "")
        if not val or val == "your_groq_api_key_here":
            return []
        return [k.strip() for k in val.split(",") if k.strip()]

    def _call_groq_with_fallback(self, prompt: str, system_instruction: str) -> str:
        """Try multiple models and multiple keys on Groq"""
        import time
        
        last_error = None
        
        # 1. Try each API key
        for key_index, api_key in enumerate(self.groq_keys):
            client = Groq(api_key=api_key)
            
            # 2. For each key, try different models
            for model_name in self.groq_models:
                retries = 2
                while retries > 0:
                    try:
                        logger.info(f"🔄 Using Groq Key #{key_index+1} with {model_name}...")
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": system_instruction},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=2048
                        )
                        return response.choices[0].message.content
                    except Exception as e:
                        error_msg = str(e).lower()
                        last_error = e
                        
                        # If Rate Limit (429), break to try next model or key
                        if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg:
                            logger.warning(f"⚠️ {model_name} quota hit on Key #{key_index+1}")
                            break # Try next model
                        
                        # If other error, retry with backoff
                        logger.warning(f"⚠️ Groq error: {e}. Retrying...")
                        time.sleep(1)
                        retries -= 1
        
        raise last_error if last_error else Exception("All Groq keys/models failed")

    def _call_huggingface(self, prompt: str, system_instruction: str) -> str:
        """Call Hugging Face API with Llama 3 70B (Last Resort)"""
        full_prompt = f"{system_instruction}\n\nUser: {prompt}\nAssistant:"
        response = self.hf_client.text_generation(
            full_prompt,
            model="meta-llama/Meta-Llama-3-70B-Instruct",
            max_new_tokens=2048,
            temperature=0.7
        )
        return response

    def generate(self, prompt: str, mode: str = "chat") -> Dict[str, Any]:
        """Generate response with automatic fallback across providers"""
        system_instruction = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["chat"])
        
        if not self.providers:
            raise HTTPException(status_code=500, detail="No API providers configured. Add keys to .env")
        
        last_error = None
        for provider_name, provider_func in self.providers:
            try:
                response_text = provider_func(prompt, system_instruction)
                return {"reply": response_text, "provider": provider_name}
            except Exception as e:
                logger.error(f"❌ {provider_name} failed: {e}")
                last_error = e
                continue
        
        raise HTTPException(status_code=500, detail=f"All providers failed: {last_error}")

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
