# 🚀 Quick Start Guide: Get Your Free API Keys

Follow these steps to get free API keys for MUNEZ.AI's multi-provider system:

## 1. Groq (Primary - FASTEST) ⚡

**Free Tier**: 14,400 requests/day

1. Go to https://console.groq.com
2. Click "Sign Up" (can use Google/GitHub)
3. Once logged in, click "API Keys" in the left sidebar
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)
6. Add to `.env`: `GROQ_API_KEY=gsk_...`

**Recommended Model**: Llama 3.3 70B (already configured)

---

## 2. Together AI (Secondary) 🔥

**Free Tier**: $25 free credits (lasts months)

1. Go to https://api.together.xyz/signup
2. Sign up with email or GitHub
3. Navigate to "API Keys" section
4. Click "Create new API key"
5. Copy the key
6. Add to `.env`: `TOGETHER_API_KEY=...`

**Recommended Model**: Meta Llama 3.1 70B (already configured)

---

## 3. Hugging Face (Tertiary) 🤗

**Free Tier**: Rate-limited but unlimited

1. Go to https://huggingface.co/join
2. Create account (email or OAuth)
3. Go to https://huggingface.co/settings/tokens
4. Click "New token"
5. Name it "MUNEZ.AI" and select "Read" role
6. Copy the token (starts with `hf_...`)
7. Add to `.env`: `HUGGINGFACE_API_KEY=hf_...`

**Recommended Model**: Meta Llama 3 70B (already configured)

---

## 4. Gemini (Fallback) 🌟

**Free Tier**: 60 requests/minute

Already configured! Your current key:
```
GEMINI_API_KEY=AIzaSyCGcuiAV_cWIEPbM5zN-DMItNBLBgYA_ZM
```

If you need a new one:
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy and update `.env`

---

## ✅ Final .env File Example

```bash
# Primary Provider (Fastest - 14,400 req/day free)
GROQ_API_KEY=gsk_abc123xyz...

# Secondary Provider ($25 free credits)
TOGETHER_API_KEY=abc123xyz...

# Tertiary Provider (Free tier)
HUGGINGFACE_API_KEY=hf_abc123xyz...

# Fallback Provider (Current)
GEMINI_API_KEY=AIzaSyCGcuiAV_cWIEPbM5zN-DMItNBLBgYA_ZM
```

---

## 🎯 Minimum Requirement

**You need at least ONE API key**, but more is better for reliability:
- ✅ **Best**: All 4 providers (99.9% uptime)
- ✅ **Good**: Groq + Gemini (fast + reliable)
- ✅ **Minimum**: Just Groq OR Gemini (works but no fallback)

---

## 🧪 Test Your Setup

After adding keys, run:
```bash
uvicorn backend.main:app --reload
```

Then visit: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "providers": ["Groq", "Together AI", "Hugging Face", "Gemini"],
  "total_providers": 4
}
```

---

## 💡 Pro Tips

1. **Start with Groq**: It's the fastest and has the best free tier
2. **Add Together AI**: $25 credits last a very long time
3. **Keep Gemini**: Good fallback since you already have it
4. **Optional Hugging Face**: Add if you want maximum reliability

**Estimated time to get all keys**: 10-15 minutes 🚀
