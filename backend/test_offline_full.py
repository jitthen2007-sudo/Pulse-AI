import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_full_offline_features():
    print("==================================================")
    print("Testing Pulse AI Full Offline Autonomous Engine...")
    print("==================================================")

    # 1. Chat scenarios
    chat_queries = [
        ("I feel totally exhausted today, what should I do?", "Fatigued / Autoregulation"),
        ("Why do my knees cave in during squats?", "Technique & Biomechanics"),
        ("What's better: PPL or Upper/Lower split?", "Program Architecture"),
        ("How long should I rest between heavy bench sets?", "Physiology & Recovery"),
        ("I feel super unmotivated and lazy to workout", "Seeking Discipline & Focus"),
        ("How much protein and carbs for a clean bulk?", "Nutritional Strategy"),
        ("Is creatine monohydrate safe and how to take it?", "Ergogenic Aids"),
    ]

    for q, expected_sentiment in chat_queries:
        res = client.post("/api/chat", json={"message": q, "history": []})
        assert res.status_code == 200
        data = res.json()
        assert data["sentiment_detected"] == expected_sentiment, f"Got {data['sentiment_detected']} for {q}"
        assert len(data["reply"]) > 100
        print(f"✓ Chat Q: '{q[:35]}...' -> Sentiment: '{data['sentiment_detected']}' [Length: {len(data['reply'])} chars]")

    # 2. Nutrition scenarios
    preferences = ["Non-Veg", "Veg", "Vegan", "Keto"]
    for pref in preferences:
        res = client.post("/api/nutrition", json={
            "weight_kg": 80,
            "height_cm": 182,
            "goal": "Fat Loss & Shred" if pref == "Keto" else "Lean Muscle Bulk",
            "preference": pref,
            "target_calories": 2400
        })
        assert res.status_code == 200
        data = res.json()
        assert data["bmi"] == 24.2
        assert len(data["grocery_list"]) == 5
        assert len(data["meal_plan"]) == 5
        print(f"✓ Nutrition ({pref}): Daily Cals {data['daily_calories']} | Protein: {data['macros']['protein_g']}g | Grocery: {data['grocery_list'][0]['name']}")

    # 3. Location & Gym scenarios
    locations = [
        ("Austin, TX", "Equinox"),
        ("London, UK", "PureGym"),
        ("Indiranagar, Bangalore", "Cult.fit"),
        ("Sydney, Australia", "Fitness First Australia"),
        ("Toronto, Canada", "GoodLife Fitness")
    ]
    for loc, expected_gym in locations:
        res = client.post("/api/routines", json={
            "location": loc,
            "goal": "Hypertrophy & Muscle Size",
            "performance_score": 85
        })
        assert res.status_code == 200
        data = res.json()
        gym_names = [g["name"] for g in data["local_gyms"]]
        assert expected_gym in gym_names, f"Expected {expected_gym} in {gym_names}"
        print(f"✓ Gym Recommender ({loc}): Identified real chains -> {gym_names}")

    print("\n🎉 ALL 16 COMPREHENSIVE OFFLINE SCENARIOS PASSED WITH 100% IDENTICAL FIDELITY!\n")

if __name__ == "__main__":
    test_full_offline_features()
