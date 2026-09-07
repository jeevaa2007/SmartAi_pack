import os
import sys
import json
from fastapi.testclient import TestClient

# Ensure root directory in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

os.environ["DATABASE_URL"] = "postgresql://smartpack_user:smartpack_password@localhost:5432/smartpack_db"

from src.main import app
from src.database.connection import SessionLocal
from src.models.user import User
from src.security.jwt import create_access_token

def verify_dashboard():
    print("=== SMARTPACK AI DASHBOARD LIVE VERIFICATION ===")
    client = TestClient(app)
    db = SessionLocal()
    
    try:
        admin_user = db.query(User).filter_by(email="admin@smartpack.ai").first()
        if not admin_user:
            # Fallback to any user
            admin_user = db.query(User).first()
            
        assert admin_user is not None, "Admin user must exist in database!"
        print(f"[OK] Found Admin User: {admin_user.full_name} ({admin_user.email})")

        token = create_access_token(admin_user.id, role="ADMIN")
        headers = {"Authorization": f"Bearer {token}"}

        print("[INFO] Requesting GET /api/v1/dashboard/stats...")
        res = client.get("/api/v1/dashboard/stats", headers=headers)
        assert res.status_code == 200, f"Expected status 200, got {res.status_code}"
        
        body = res.json()
        assert body["success"] is True, "APIResponse success must be True"
        
        data = body["data"]
        print("\n--- LIVE DASHBOARD KPI METRICS ---")
        print(f"Total Orders:             {data['total_orders']}")
        print(f"Verified Orders:          {data['verified_orders']}")
        print(f"Overall Pass Rate:        {data['pass_rate']}%")
        print(f"Average Packing Score:    {data['avg_packing_score']}")
        print(f"Warning Count:            {data['warning_count']}")
        print(f"Failure Count:            {data['failure_count']}")
        print(f"Pass Count (Breakdown):   {data['outcome_breakdown']['pass_count']}")
        print(f"Warning Count (Breakdown):{data['outcome_breakdown']['warning_count']}")
        print(f"Fail Count (Breakdown):   {data['outcome_breakdown']['fail_count']}")
        print(f"Recent Orders Count:      {len(data['recent_orders'])}")
        print(f"Recent Verifications:     {len(data['recent_verifications'])}")

        print("\n[OK] Dashboard Verification Completed Successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    verify_dashboard()
