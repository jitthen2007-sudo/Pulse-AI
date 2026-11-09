import sys
from pathlib import Path

# Add backend directory to path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    print("Testing /api/health...")
    response = client.get("/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "online"
    print("✓ Healthcheck passed:", data["status"], "| Model:", data.get("gemini_model"))

def test_virtual_coach_chat():
    print("Testing Module 1: POST /api/chat...")
    payload = {
        "message": "I feel super tired today. What should I do for my workout, and what causes my knees to cave during squats?",
        "history": []
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "reply" in data
    assert "sentiment_detected" in data
    print("✓ Chatbot passed:", data["sentiment_detected"], "| Reply length:", len(data["reply"]))

def test_dietician_nutrition():
    print("Testing Module 2: POST /api/nutrition...")
    payload = {
        "weight_kg": 75,
        "height_cm": 180,
        "goal": "Lean Muscle Bulk",
        "preference": "Veg",
        "target_calories": 2600
    }
    response = client.post("/api/nutrition", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["bmi"] == 23.1
    assert data["bmi_category"] == "Normal Weight"
    assert "macros" in data
    assert len(data["grocery_list"]) == 5, f"Expected 5 grocery items, got {len(data['grocery_list'])}"
    print("✓ Nutrition passed: BMI:", data["bmi"], "| Groceries:", [g["name"] for g in data["grocery_list"]])

def test_routines_and_gyms():
    print("Testing Module 3: POST /api/routines...")
    payload = {
        "location": "Austin, TX",
        "goal": "Hypertrophy",
        "performance_score": 75
    }
    response = client.post("/api/routines", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "workout_split" in data
    assert "daily_challenge" in data
    assert len(data["local_gyms"]) == 3, f"Expected 3 gym chains, got {len(data['local_gyms'])}"
    print("✓ Routines passed: Challenge:", data["daily_challenge"]["title"], "| Gyms:", [g["name"] for g in data["local_gyms"]])

if __name__ == "__main__":
    print("\n--- RUNNING PULSE AI BACKEND TEST SUITE ---")
    test_health()
    test_virtual_coach_chat()
    test_dietician_nutrition()
    test_routines_and_gyms()
    print("\n🎉 ALL BACKEND MODULE TESTS PASSED PERFECTLY!\n")
