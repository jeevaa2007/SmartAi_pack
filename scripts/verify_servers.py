import urllib.request
import json

def test_endpoint(url, name):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"[OK] {name} ({url}) -> Status: {resp.status}")
            return True
    except Exception as e:
        print(f"[ERR] {name} ({url}) -> Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Backend (http://127.0.0.1:8000/docs)...")
    b_ok = test_endpoint("http://127.0.0.1:8000/docs", "FastAPI Backend OpenAPI Specs")
    
    print("Testing Frontend (http://localhost:3000)...")
    f_ok = test_endpoint("http://localhost:3000", "Next.js Frontend Control Center")
