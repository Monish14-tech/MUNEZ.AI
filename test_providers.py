"""
Test script for multi-provider AI fallback system
Run this to verify all providers are working correctly
"""
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_api_keys():
    """Check which API keys are configured"""
    print("🔍 Checking API Keys Configuration...\n")
    
    providers = {
        "Groq": os.getenv("GROQ_API_KEY"),
        "Hugging Face": os.getenv("HUGGINGFACE_API_KEY"),
        "Gemini": os.getenv("GEMINI_API_KEY")
    }
    
    configured = []
    missing = []
    
    for name, key in providers.items():
        if key and key not in ["your_groq_api_key_here", "your_together_api_key_here", "your_huggingface_api_key_here"]:
            configured.append(name)
            # Show partial key for security
            masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            print(f"✅ {name}: {masked_key}")
        else:
            missing.append(name)
            print(f"❌ {name}: Not configured")
    
    print(f"\n📊 Summary: {len(configured)}/3 providers configured")
    
    if len(configured) == 0:
        print("\n⚠️  WARNING: No API providers configured!")
        print("   Add at least one API key to .env file")
        return False
    elif len(configured) < 3:
        print(f"\n💡 TIP: Add {3 - len(configured)} more provider(s) for better reliability")
        print(f"   Missing: {', '.join(missing)}")
    else:
        print("\n🎉 Perfect! All providers configured for maximum reliability!")
    
    return True

def test_individual_providers():
    """Test each provider individually"""
    print("\n\n🧪 Testing Individual Providers...\n")
    
    test_prompt = "Say 'Hello from' followed by your model name in 5 words or less."
    
    # Test Groq
    if os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY") != "your_groq_api_key_here":
        try:
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=50
            )
            print(f"✅ Groq: {response.choices[0].message.content.strip()}")
        except Exception as e:
            print(f"❌ Groq: {str(e)[:100]}")
    

    # Test Hugging Face
    if os.getenv("HUGGINGFACE_API_KEY") and os.getenv("HUGGINGFACE_API_KEY") != "your_huggingface_api_key_here":
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))
            response = client.text_generation(
                test_prompt,
                model="meta-llama/Meta-Llama-3-70B-Instruct",
                max_new_tokens=50
            )
            print(f"✅ Hugging Face: {response.strip()}")
        except Exception as e:
            print(f"❌ Hugging Face: {str(e)[:100]}")
    
    # Test Gemini
    if os.getenv("GEMINI_API_KEY"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(test_prompt)
            print(f"✅ Gemini: {response.text.strip()}")
        except Exception as e:
            print(f"❌ Gemini: {str(e)[:100]}")

def test_backend_health():
    """Test if backend is running and check health endpoint"""
    print("\n\n🏥 Testing Backend Health...\n")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running!")
            print(f"   Status: {data.get('status')}")
            print(f"   Active Providers: {', '.join(data.get('providers', []))}")
            print(f"   Total: {data.get('total_providers')}/4")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running")
        print("   Start it with: uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  MUNEZ.AI - Multi-Provider Fallback System Test")
    print("=" * 60)
    
    # Step 1: Check API keys
    keys_ok = test_api_keys()
    
    if not keys_ok:
        print("\n❌ Test failed: No API keys configured")
        print("\n📖 See API_KEYS_GUIDE.md for setup instructions")
        exit(1)
    
    # Step 2: Test individual providers
    test_individual_providers()
    
    # Step 3: Test backend health
    backend_ok = test_backend_health()
    
    print("\n" + "=" * 60)
    if backend_ok:
        print("✅ All tests passed! System is ready to use.")
        print("\n🚀 Try it at: http://localhost:8000")
    else:
        print("⚠️  Backend not running. Start it to complete testing.")
        print("\n   Run: uvicorn backend.main:app --reload")
    print("=" * 60)
