# MUNEZ.AI - AI Assistant

A powerful AI assistant with **multi-provider fallback** for unlimited usage.

## Features
- **Multi-Provider Fallback**: Groq → Together AI → Hugging Face → Gemini
- **Unlimited Requests**: No quota limits with automatic provider switching
- **Ultra-Fast**: Primary provider (Groq) delivers responses in milliseconds
- **Smart Chat**: Multiple AI modes (Chat, Summarize, Code Explanation)
- **Modern UI**: Dark mode, glassmorphism, and animated background
- **99.9% Uptime**: Automatic failover ensures service availability

## Local Setup

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Get Free API Keys:**
    - **Groq** (Primary - Fastest): https://console.groq.com
    - **Together AI** (Secondary): https://api.together.xyz/signup
    - **Hugging Face** (Tertiary): https://huggingface.co/settings/tokens
    - **Gemini** (Fallback): https://makersuite.google.com/app/apikey
    
    All services offer generous free tiers!

4.  **Environment Variables:**
    Update the `.env` file with your API keys:
    ```bash
    # At least ONE key is required, but more = better reliability
    GROQ_API_KEY=your_groq_key_here
    TOGETHER_API_KEY=your_together_key_here
    HUGGINGFACE_API_KEY=your_hf_key_here
    GEMINI_API_KEY=your_gemini_key_here
    ```
5.  **Run the application:**
    ```bash
    uvicorn backend.main:app --reload
    ```
6.  **Open Browser:**
    Go to `http://localhost:8000`.

7.  **Check Health:**
    Visit `http://localhost:8000/health` to see active providers.

## How It Works

The app automatically tries providers in this order:
1. **Groq** (14,400 req/day free) - Fastest responses
2. **Together AI** ($25 free credits) - Diverse models
3. **Hugging Face** (Free tier) - Reliable fallback
4. **Gemini** (Free tier) - Final fallback

If one provider hits quota limits, it instantly switches to the next!

## Deployment

### Vercel
1.  Install Vercel CLI or connect your GitHub repo to Vercel.
2.  The included `vercel.json` will automatically configure the Python backend.
3.  **Important**: Add ALL your API keys as environment variables in Vercel Project Settings.

### Render / Railway
1.  Create a new Web Service.
2.  Connect your repository.
3.  **Build Command**: `pip install -r requirements.txt`
4.  **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables**: Add all your API keys in the service settings.

## Troubleshooting

- **"No API providers configured"**: Add at least one API key to `.env`
- **"All API providers failed"**: Check your API keys are valid
- **Slow responses**: Primary provider (Groq) may be down, check `/health` endpoint
- **"Failed to fetch"**: Backend is not running or not accessible
    - Ensure `uvicorn` is running locally
    - For deployment, verify the backend service is active

## API Provider Comparison

| Provider | Free Tier | Speed | Best For |
|----------|-----------|-------|----------|
| Groq | 14,400 req/day | ⚡⚡⚡⚡⚡ | Primary use |
| Together AI | $25 credits | ⚡⚡⚡⚡ | Backup |
| Hugging Face | Rate-limited | ⚡⚡⚡ | Fallback |
| Gemini | 60 req/min | ⚡⚡⚡⚡ | Final fallback |
