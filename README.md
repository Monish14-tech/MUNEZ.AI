# MUNEZ.AI - AI Assistant

A powerful AI assistant built with FastAPI and Google Gemini.

## Features
- **Smart Chat**: Powered by Gemini Flash.
- **Modes**: Chat, Summarize, Code Explanation.
- **Modern UI**: Dark mode, glassmorphism, and animated background.

## Local Setup

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables:**
    Create a `.env` file in the root directory:
    ```
    GEMINI_API_KEY=your_api_key_here
    ```
4.  **Run the application:**
    ```bash
    uvicorn backend.main:app --reload
    ```
5.  **Open Browser:**
    Go to `http://localhost:8000`.

## Deployment

### Vercel
1.  Install Vercel CLI or connect your GitHub repo to Vercel.
2.  The included `vercel.json` will automatically configure the Python backend.
3.  **Important**: Go to Vercel Project Settings > Environment Variables and add `GEMINI_API_KEY`.

### Render / Railway
1.  Create a new Web Service.
2.  Connect your repository.
3.  **Build Command**: `pip install -r requirements.txt`
4.  **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` (Start command is also in `Procfile`).
5.  **Environment Variables**: Add `GEMINI_API_KEY` in the service settings.

## Troubleshooting
- **"Failed to fetch"**: This usually means the backend is not running or not accessible. 
    - If hosting on Vercel, ensure the `vercel.json` file is present.
    - If hosting on a static site provider (Netlify/GitHub Pages) without a Python backend, this app **will not work**. You need a server to run the Python code.
