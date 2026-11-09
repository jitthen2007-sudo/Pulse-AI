import os
import json
import re
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env in backend directory or parent
backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir.parent / ".env")

# Try to import Google GenAI
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

app = FastAPI(
    title="Pulse AI API",
    description="Backend AI engine for Pulse AI fitness and form-correction platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    if not GENAI_AVAILABLE:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Notice: Running in Pulse AI Autonomous Local Mode: {e}")
        return None

def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# -------------------------------------------------------------
# Schemas
# -------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    reply: str
    sentiment_detected: Optional[str] = "Motivated"
    actionable_tips: Optional[List[str]] = []
    source: str = "gemini"

class NutritionRequest(BaseModel):
    weight_kg: float = Field(..., gt=20, lt=400, description="Weight in kilograms")
    height_cm: float = Field(..., gt=50, lt=260, description="Height in centimeters")
    goal: str = Field(..., description="E.g., Weight Loss, Muscle Gain, Maintenance, Lean Bulk")
    preference: str = Field(..., description="E.g., Veg, Non-Veg, Vegan, Keto, High Protein")
    target_calories: Optional[int] = Field(None, description="Optional target calorie goal")

class MacroBreakdown(BaseModel):
    protein_g: int
    carbs_g: int
    fats_g: int
    protein_pct: int
    carbs_pct: int
    fats_pct: int

class MealItem(BaseModel):
    title: str
    calories: int
    macros: str
    description: str

class GroceryItem(BaseModel):
    name: str
    category: str
    benefit: str
    quantity_est: str

class NutritionResponse(BaseModel):
    bmi: float
    bmi_category: str
    bmi_analysis: str
    daily_calories: int
    macros: MacroBreakdown
    strategy_summary: str
    meal_plan: Dict[str, MealItem]
    grocery_list: List[GroceryItem] # Exactly 5 items
    hydration_tip: str
    timing_tip: str
    source: str = "gemini"

class RoutineRequest(BaseModel):
    location: str = Field(..., description="User's city or locality, e.g. Austin, TX")
    goal: str = Field(..., description="E.g. Hypertrophy, Strength, Fat Loss, Athleticism")
    performance_score: int = Field(..., ge=1, le=100, description="Score between 1 and 100")

class Exercise(BaseModel):
    name: str
    sets: str
    reps: str
    rest_seconds: int
    key_cue: str

class WorkoutDay(BaseModel):
    day_title: str
    target_muscles: List[str]
    exercises: List[Exercise]

class WorkoutSplit(BaseModel):
    split_name: str
    frequency: str
    description: str
    days: List[WorkoutDay]

class DailyChallenge(BaseModel):
    title: str
    difficulty_badge: str
    description: str
    challenge_steps: List[str]
    completion_time_est: str

class LocalGym(BaseModel):
    name: str
    locality_context: str
    vibe: str
    key_amenities: List[str]
    why_recommended: str

class RoutineResponse(BaseModel):
    workout_split: WorkoutSplit
    daily_challenge: DailyChallenge
    local_gyms: List[LocalGym] # Exactly 3 real gym chains
    coach_note: str
    source: str = "gemini"

# -------------------------------------------------------------
# Module 1: Virtual Coach System Prompt
# -------------------------------------------------------------
COACH_SYSTEM_PROMPT = """You are Pulse AI's Elite Virtual Fitness Coach, Biomechanics Specialist, and Psychological Performance Mentor.
Your mission is to provide world-class, science-backed guidance to athletes and everyday lifters alike.

Core Competencies you must display:
1. Deep Muscle Anatomy & Joint Kinematics: Explain prime movers, synergists, stabilizer muscles, moment arms, and optimal bar paths.
2. Recovery & Supercompensation: Explain central nervous system (CNS) fatigue, systemic vs. local fatigue, optimal rest times between sets (e.g. 2-3 min for compounds, 60-90s for hypertrophy isolation), and sleep architecture.
3. Workout Splits: Deeply articulate PPL (Push/Pull/Legs), Upper/Lower, Arnold Split, Full-body, and customize to lifter frequency.
4. Macro Tracking & Metabolism: Detail macronutrient ratios (protein 1.6-2.2g/kg, fats 0.6-1.0g/kg, carbs to fuel glycogen), caloric deficits/surpluses, and nutrient timing.
5. Injury Prevention & Prehab: Pinpoint joint impingements, patellar tendon tracking, rotator cuff warmups, spinal neutral bracing (Valsalva maneuver), and hip mobility.
6. Mood & Sentiment Adaptive Motivation: Actively detect the user's emotional state from their phrasing (e.g., exhausted, discouraged, pumped, anxious, plateaued). Adapt your tone: if tired, offer strategic autoregulation and recovery; if unmotivated, spark discipline over fleeting motivation; if energized, channel that focus into progressive overload.

Formatting Rules:
- Use clean Markdown with bold headings, bullet points, and actionable takeaways.
- Provide practical, immediate next steps.
- Conclude with a dynamic, punchy motivational closing phrase.
"""

# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------

@app.get("/api/health")
def health_check():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    has_key = bool(api_key and api_key != "your_gemini_api_key_here")
    return {
        "status": "online",
        "service": "Pulse AI Autonomous Ecosystem",
        "gemini_configured": has_key,
        "gemini_model": get_gemini_model(),
        "genai_sdk_loaded": GENAI_AVAILABLE,
        "mode": "Gemini Live API" if has_key else "Autonomous Local Sports-Science Engine (No API Key Required)",
        "message": "All 4 modules fully operational with local biomechanics & nutrition engine."
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_coach(req: ChatRequest):
    client = get_gemini_client()
    user_msg = req.message.strip()
    
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    # Attempt live Gemini call if API key configured
    if client:
        try:
            contents = []
            for h in (req.history or [])[-6:]:
                contents.append(f"{h.role.capitalize()}: {h.content}")
            contents.append(f"User: {user_msg}")
            prompt_text = "\n\n".join(contents)
            
            model_name = get_gemini_model()
            config = types.GenerateContentConfig(
                system_instruction=COACH_SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=1200
            )
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config=config
            )
            reply = response.text or "I'm with you. What's our next target?"
            
            sentiment = "Motivated"
            lower = user_msg.lower()
            if any(w in lower for w in ["tired", "exhausted", "sore", "drained", "sleepy", "burnout"]):
                sentiment = "Fatigued / Needs Recovery"
            elif any(w in lower for w in ["pain", "hurt", "injured", "tweak", "strain", "click"]):
                sentiment = "Caution / Injury Alert"
            elif any(w in lower for w in ["hyped", "ready", "crush", "pr", "pumped", "let's go"]):
                sentiment = "High Energy / Beast Mode"
            elif any(w in lower for w in ["sad", "lazy", "demotivated", "unmotivated", "can't", "fail"]):
                sentiment = "Seeking Discipline & Focus"

            return ChatResponse(
                reply=reply,
                sentiment_detected=sentiment,
                actionable_tips=[
                    "Hydrate with 500ml water and electrolytes before your set.",
                    "Track your RPE (Rate of Perceived Exertion) to dial in intensity.",
                    "Focus on eccentric control (2-3 seconds down) for peak muscle tension."
                ],
                source="gemini"
            )
        except Exception as e:
            print(f"Notice: Falling back to Pulse Autonomous Engine: {e}")

    # =============================================================
    # HIGH-FIDELITY PULSE AUTONOMOUS KINESIOLOGY & COACHING ENGINE
    # Provides full features without any external API key
    # =============================================================
    lower = user_msg.lower()
    
    # Mood / Emotion Vector
    is_tired = any(w in lower for w in ["tired", "exhausted", "sore", "drained", "sleepy", "burnout", "no energy"])
    is_lazy = any(w in lower for w in ["lazy", "demotivated", "unmotivated", "can't get up", "struggling", "skip"])
    is_hyped = any(w in lower for w in ["hyped", "pumped", "pr", "crush", "let's go", "ready", "beast"])
    is_pain = any(w in lower for w in ["pain", "hurt", "tweak", "strain", "injured", "ache", "impinge"])

    # Topic Vectors
    is_squat = any(w in lower for w in ["squat", "knee", "depth", "valgus", "cave", "patellar", "femur"])
    is_bench = any(w in lower for w in ["bench", "chest", "shoulder", "rotator", "scapula", "pec"])
    is_deadlift = any(w in lower for w in ["deadlift", "back", "lumbar", "spine", "hinge", "hamstring"])
    is_splits = any(w in lower for w in ["split", "ppl", "push pull legs", "arnold", "upper lower", "routine", "5/3/1", "frequency"])
    is_rest = any(w in lower for w in ["rest", "recovery", "between sets", "cns", "supercompensation", "sleep", "hrv", "how long"])
    is_macros = any(w in lower for w in ["macro", "protein", "carb", "calorie", "bulk", "cut", "diet", "leucine", "tdee"])
    is_supps = any(w in lower for w in ["creatine", "supplement", "caffeine", "preworkout", "whey", "glutamine"])

    if is_squat:
        sentiment = "Technique & Biomechanics"
        reply = (
            "### 🏋️ Form Masterclass: Squat Kinematics & Depth Optimization\n\n"
            "Squats are the ultimate test of closed-chain lower body mechanics. Here is the anatomical blueprint for spotless reps:\n\n"
            "* **Acetabular Hip Clearance:** Set stance shoulder-width with toes flared **15° to 30° outward**. This creates anatomical room inside the acetabular socket, allowing the femur to drop between the hips without impingement.\n"
            "* **The 95° Depth Threshold:** In Pulse AI's Pose Coach, the depth trigger is reaching a knee joint angle **< 95°**. This guarantees your femur breaks parallel to the floor, fully recruiting the vastus medialis oblique (VMO) and gluteus maximus.\n"
            "* **Preventing Valgus Collapse (Knees Caving):** Knee cave is usually driven by weak gluteus medius or limited ankle dorsiflexion. Actively 'screw your feet into the floor' (external rotation torque) to lock your knee tracking over your second toe.\n"
            "* **Intra-Abdominal Bracing (Valsalva):** Draw air deep into your diaphragm and brace 360° against your abdominal wall before initiating the eccentric descent.\n\n"
            "**Coach's Directive:** Open our **AI Pose Coach** tab right now! It tracks your left hip-knee-ankle angle in real time at 60 FPS and gives dynamic audio depth cues."
        )
        tips = [
            "Descend with a controlled 3-second eccentric tempo.",
            "Drive your knees outward over your pinky toes on the ascent.",
            "Keep the bar centered over your midfoot at all times."
        ]

    elif is_splits:
        sentiment = "Program Architecture"
        reply = (
            "### 📊 Master Programming: Split Breakdown & Frequency Science\n\n"
            "To maximize muscle protein synthesis (which stays elevated for 36–48 hours post-training), muscle groups should ideally be hit **twice every 7 to 9 days**:\n\n"
            "* **Push / Pull / Legs (PPL - 6 Days/Week):** Best for intermediate to advanced lifters. Divides work by biomechanical movement patterns (Push = Chest/Shoulders/Triceps, Pull = Back/Rear Delts/Biceps, Legs = Quads/Hams/Calves).\n"
            "* **Upper / Lower Split (4 Days/Week):** Superior for balance and heavy compound progressive overload. Allows 72 hours of recovery between sessions, perfect for strength building.\n"
            "* **Arnold Split (Chest/Back, Shoulders/Arms, Legs):** Emphasizes antagonistic supersets and intense upper-body muscle pumps.\n"
            "* **Full Body (3 Days/Week):** The gold standard for beginner foundation and maximum systemic frequency with high neurological recovery.\n\n"
            "**Coach's Directive:** Check out our **Gym & Routines** tab to generate a custom 4-day split tailored to your exact performance score and local gym availability!"
        )
        tips = [
            "Hit each muscle group with 10–20 high-quality working sets per week.",
            "Keep 1–2 reps in reserve (RIR) on compound lifts to avoid premature CNS burnout.",
            "Schedule a planned deload week every 6–8 weeks to dissipate fatigue."
        ]

    elif is_rest:
        sentiment = "Physiology & Recovery"
        reply = (
            "### ⏱️ Rest Interval Science: Compound vs. Hypertrophy Kinetics\n\n"
            "Rest intervals directly regulate ATP-CP resynthesis and central nervous system (CNS) readiness:\n\n"
            "* **Compound Strength Lifts (Squat, Deadlift, Bench, OHP):** **2.5 to 3.5 minutes**. Phosphocreatine stores take ~3 minutes to replenish to 95% capacity. Cutting rest here cuts mechanical tension.\n"
            "* **Compound Hypertrophy Movements (Rows, Leg Press, DB Incline):** **90 to 120 seconds**. Balances metabolite clearance with high motor-unit recruitment.\n"
            "* **Isolation & Metabolite Finishers (Curls, Lateral Raises, Pushdowns):** **60 to 75 seconds**. Maximizes cell swelling, vascular occlusion, and metabolic stress.\n"
            "* **Recovery Sleep Architecture:** Human growth hormone (HGH) pulses peak during slow-wave Stage 3 & 4 NREM sleep. Prioritize 7.5 to 9 hours in a room below 20°C (68°F).\n\n"
            "**Coach's Directive:** Time your rest periods with a stopwatch. Strict rest discipline prevents junk volume."
        )
        tips = [
            "Take deep nasal breaths between sets to stimulate the parasympathetic brake.",
            "If your heart rate is still pounding above 135 bpm, wait an extra 30 seconds before lifting.",
            "Track resting heart rate upon waking as a metric for systemic recovery."
        ]

    elif is_macros:
        sentiment = "Nutritional Strategy"
        reply = (
            "### 🥗 Precision Macro Architecture & Nutrient Timing\n\n"
            "Optimizing body recomposition is a game of molecular thermodynamics and amino acid delivery:\n\n"
            "* **Protein Target:** Consume **1.8g to 2.2g of protein per kg of bodyweight** (0.8–1.0g/lb). Divide into 4 doses spaced 3–4 hours apart with at least **3g of leucine** per meal to trigger the mTOR pathway.\n"
            "* **Carbohydrate Partitioning:** Carbohydrates replenish intramuscular glycogen and spare muscle tissue. Target 40–50% of your carbs in the **peri-workout window** (pre and post-session).\n"
            "* **Essential Lipids (Fats):** Never drop below **0.6g/kg**. Fats are the biochemical precursors for testosterone, estrogen, and cell membrane fluidity.\n"
            "* **Caloric Surplus/Deficit:** For a clean bulk, aim for **+250 to +350 kcal/day** to avoid visceral fat gain; for cutting, run **-400 to -500 kcal/day** while keeping protein high.\n\n"
            "**Coach's Directive:** Head to our **AI Dietician** tab to compute your exact BMI, macro grams, and an automated 5-item grocery list!"
        )
        tips = [
            "Drink 500ml of water with a pinch of sea salt 30 minutes pre-workout.",
            "Pair post-workout fast-digesting protein with high-glycemic carbohydrates.",
            "Consistent daily protein intake matters more than acute anabolic window timing."
        ]

    elif is_bench:
        sentiment = "Joint Kinematics"
        reply = (
            "### 🛡️ Bench Press Biomechanics & Shoulder Preservation\n\n"
            "The bench press requires deliberate scapular positioning to protect the glenohumeral joint:\n\n"
            "* **Scapular Retraction & Depression:** Pinch your shoulder blades down and back 'into your back pockets' before un-racking. This stabilizes the rotator cuff against the bench.\n"
            "* **Elbow Flare Angle:** Never flare your elbows out at 90°. Tuck elbows to a **45° to 60° angle** relative to your torso. A 90° flare produces subacromial impingement on the supraspinatus tendon.\n"
            "* **Bar Path (J-Curve):** Touch the bar to your lower sternum/nipple line, then press in a slight arc backward over your shoulders.\n"
            "* **Leg Drive:** Dig your heels into the floor, pushing horizontally away from the rack to transfer ground force into your upper back.\n\n"
            "**Coach's Directive:** Always incorporate 3 sets of face pulls or cable external rotations twice a week to bulletproof your rear delts and rotator cuffs."
        )
        tips = [
            "Grip the bar tightly to stimulate muscle irradiation into the triceps and deltoids.",
            "Touch your chest gently; never bounce the barbell off your ribcage.",
            "Perform warm-up sets with a resistance band before your working weight."
        ]

    elif is_deadlift:
        sentiment = "Posterior Chain Mechanics"
        reply = (
            "### ⚡ Deadlift Kinematics: Hip Hinge vs. Squatting\n\n"
            "The deadlift is a pure hip hinge designed to load the posterior chain, not a squat:\n\n"
            "* **Barbell Proximity:** Set the barbell 1 inch from your shins, directly over mid-foot. If the bar drifts forward, the moment arm on your lumbar spine increases exponentially.\n"
            "* **Lat Engagement:** 'Protect your armpits' or 'bend the bar around your shins'. Squeezing the lats stabilizes the thoracolumbar fascia and keeps the spine rigid.\n"
            "* **Wedge & Slack:** Pull the slack out of the barbell until you hear the 'click' before pushing the floor away.\n"
            "* **Drive Through Midfoot:** Think of the pull as leg-pressing the earth downward rather than pulling with your arms.\n\n"
            "**Coach's Directive:** If your lower back rounds, drop the load by 15% and drill Romanian Deadlifts (RDLs) to build hamstring tensile strength."
        )
        tips = [
            "Never hyperextend your lower back at the top lockout; finish tall with squeezed glutes.",
            "Use mixed grip or lifting straps on top heavy sets to prevent grip fatigue from limiting posterior drive.",
            "Reset your breath and brace between every single repetition."
        ]

    elif is_supps:
        sentiment = "Ergogenic Aids"
        reply = (
            "### 💊 Evidence-Based Ergogenic Supplements\n\n"
            "Only a handful of sports supplements have decades of double-blind, peer-reviewed clinical support:\n\n"
            "* **Creatine Monohydrate (5g/day):** Saturates intramuscular phosphocreatine stores. Increases ATP regeneration, peak power output, and intracellular hydration. No loading phase necessary—take 5g daily with water.\n"
            "* **Caffeine (3–5mg per kg):** Adenosine receptor antagonist that decreases perceived exertion (RPE) and boosts motor unit firing rates. Best taken 45 minutes pre-training.\n"
            "* **Whey or Pea Protein Isolate:** Rapid source of complete branch-chain amino acids, specifically high leucine content to stimulate muscle protein synthesis.\n"
            "* **Electrolytes (Sodium & Potassium):** Crucial for neuromuscular action potentials and preventing intra-workout cramping.\n\n"
            "**Coach's Directive:** Supplements are the final 5%. Perfect your sleep, form, and progressive overload first!"
        )
        tips = [
            "Drink an extra 500ml water daily when supplementing with creatine monohydrate.",
            "Avoid caffeine within 8 hours of bedtime to safeguard Stage 3 slow-wave sleep.",
            "Focus 90% of your nutrition on single-ingredient whole foods."
        ]

    elif is_tired:
        sentiment = "Fatigued / Autoregulation"
        reply = (
            "### 🧘 Strategic Autoregulation: Respect the Nervous System\n\n"
            "I hear you—and smart athletes know that fatigue is biological feedback, not weakness:\n\n"
            "* **Autoregulate Your Session:** When your central nervous system is drained, forcing heavy maximum loads invites technique breakdown. Shift today's session to **RPE 6–7** or perform an **Active Recovery Protocol**.\n"
            "* **20-Minute Protocol:** 15 minutes of Zone 2 cardio (incline walking or cycling) followed by 90/90 hip mobility, foam rolling, and deep diaphragmatic breathing.\n"
            "* **Cellular Reload:** Down 500ml water with electrolytes and prioritize an early bedtime tonight. Sleep is when growth hormone pulses repair damaged myofibrils.\n\n"
            "**Coach's Directive:** Long-term consistency beats short-term martyrdom. Recover smartly today so you can shatter PRs tomorrow!"
        )
        tips = [
            "Drop working weights by 15-20% and focus exclusively on mind-muscle connection.",
            "Take 400mg magnesium glycinate before sleep to relax skeletal muscle tension.",
            "Take 10 slow, deep nasal breaths right now to down-regulate sympathetic stress."
        ]

    elif is_lazy:
        sentiment = "Seeking Discipline & Focus"
        reply = (
            "### ⚡ The Discipline Shift: Overcoming the Friction Point\n\n"
            "Motivation is fickle—it disappears the second work gets hard. Champions rely on **automated discipline**:\n\n"
            "* **The 5-Minute Rule:** Tell yourself: *'I am only going to do the dynamic warmup and one warm-up set.'* 95% of the battle is simply crossing the threshold and initiating movement.\n"
            "* **Action Precedes Motivation:** Dopamine is released in response to progress, not while sitting on the couch waiting for inspiration. Once the barbell moves, the brain follows.\n"
            "* **Identity Shift:** You are someone who shows up when it's inconvenient. That is the exact crucible where mental resilience is forged.\n\n"
            "**Coach's Directive:** Put on your training shoes right now. Do 10 bodyweight squats in front of Pulse AI's Pose Coach, and let momentum take over!"
        )
        tips = [
            "Start your warmup right now—don't negotiate with your internal friction.",
            "Listen to high-tempo music to activate your reticular activating system.",
            "Remember why you started this journey."
        ]

    elif is_hyped:
        sentiment = "High Energy / Beast Mode"
        reply = (
            "### 🔥 High Energy Channeling: Lock In & Execute\n\n"
            "That's the mindset! Let's channel that adrenaline into structured progressive overload:\n\n"
            "* **Target Today's Heavy Compound First:** Direct your peak neuromuscular drive into your primary movement (Squat, Bench, or Deadlift) while your ATP stores are 100% fresh.\n"
            "* **Form Precedes Weight:** Channel your aggression into **crisp, violent acceleration** on the concentric phase, while keeping the eccentric phase strictly controlled (2 seconds down).\n"
            "* **Log the Numbers:** Aim to add 1 rep or a 1.25kg plate to your top set today.\n\n"
            "**Coach's Directive:** Turn on Pulse AI's **AI Pose Coach** and see how many clean reps you can log hitting full 95° depth!"
        )
        tips = [
            "Perform 2 progressively heavier warm-up sets before your top working set.",
            "Focus on explosive intent during the lifting phase.",
            "Drink plenty of water to maintain intracellular cell volumization."
        ]

    elif is_pain:
        sentiment = "Caution / Injury Alert"
        reply = (
            "### 🛡️ Injury Prevention & Joint Prehab Protocol\n\n"
            "Pain is a red alert signal from your nervous system. Never lift through sharp, stabbing joint pain:\n\n"
            "* **The 0–3 Scale:** Mild discomfort (1-2 out of 10) during warmups is often just tight fascia, but sharp or increasing pain (3+ out of 10) means immediate cessation of that movement.\n"
            "* **Find Pain-Free Alternatives:** If flat barbell bench irritates your shoulder, swap to neutral-grip dumbbell press. If back squats irritate your knee, switch to goblet squats or reverse lunges.\n"
            "* **Tissue Temperature:** Spend 8 full minutes increasing synovial fluid in the affected joint with light banded movements.\n\n"
            "**Coach's Directive:** Longevity in the gym is the real goal. Work around pain, never through it."
        )
        tips = [
            "Apply ice for acute inflammation, or gentle heat for muscular tightness.",
            "Substitute aggravating exercises with joint-friendly dumbbell or cable variations.",
            "If pain persists longer than 72 hours, consult a licensed physical therapist."
        ]

    else:
        sentiment = "Pulse Performance Coach"
        reply = (
            f"### 🎯 Pulse AI Coach Assessment\n\n"
            f"Regarding **'{user_msg}'**:\n\n"
            "* **Kinematic Precision:** Whether lifting for hypertrophy or athletic conditioning, prioritize mechanical tension and joint stability over ego lifting.\n"
            "* **Progressive Overload Principle:** Track every session. Progress is achieved by adding a rep, increasing load by 1-2%, or slowing down your eccentric tempo to increase time under tension.\n"
            "* **Metabolic Fuel & Recovery:** Muscles are stimulated in the gym, but they are synthesized in the kitchen and built during deep Stage 4 sleep.\n\n"
            "**Coach's Directive:** Explore our tabs above—track your squat depth on **AI Pose Coach**, plan your meals on **AI Dietician**, or dial in your split on **Gym & Routines**!"
        )
        tips = [
            "Focus on full range of motion over heavier weight.",
            "Stay consistent—3 focused sessions per week beats 6 chaotic ones.",
            "Track your weekly volume to ensure steady progression."
        ]

    return ChatResponse(
        reply=reply,
        sentiment_detected=sentiment,
        actionable_tips=tips,
        source="pulse-engine"
    )

# -------------------------------------------------------------
# Module 2: AI Dietician & Nutritionist Endpoint
# -------------------------------------------------------------

@app.post("/api/nutrition", response_model=NutritionResponse)
async def generate_diet_plan(req: NutritionRequest):
    # Calculate exact BMI
    height_m = req.height_cm / 100.0
    bmi = round(req.weight_kg / (height_m * height_m), 1)
    
    if bmi < 18.5:
        bmi_cat = "Underweight"
        bmi_note = f"Your BMI of {bmi} indicates a caloric surplus is optimal to build lean myofibrillar muscle and balance hormonal health."
    elif bmi < 25.0:
        bmi_cat = "Normal Weight"
        bmi_note = f"Your BMI of {bmi} is in the optimal metabolic zone. Ideal for lean bulking, athletic performance, or body recomposition."
    elif bmi < 30.0:
        bmi_cat = "Overweight"
        bmi_note = f"Your BMI of {bmi} suggests a slight caloric deficit paired with high-protein resistance training will efficiently shred fat while preserving muscle."
    else:
        bmi_cat = "Obese"
        bmi_note = f"Your BMI of {bmi} benefits from a structured, sustainable caloric deficit with low-glycemic foods and daily non-exercise physical activity (NEAT)."

    # Mifflin-St Jeor Energy Estimation
    bmr_est = 10 * req.weight_kg + 6.25 * req.height_cm - 5 * 28 + 5
    tdee_est = int(bmr_est * 1.45) # moderately active baseline
    
    target_cals = req.target_calories
    if not target_cals or target_cals <= 0:
        if "loss" in req.goal.lower() or "shred" in req.goal.lower() or "cut" in req.goal.lower():
            target_cals = max(1350, tdee_est - 450)
        elif "bulk" in req.goal.lower() or "gain" in req.goal.lower():
            target_cals = tdee_est + 350
        elif "strength" in req.goal.lower():
            target_cals = tdee_est + 200
        else:
            target_cals = tdee_est

    # Try live Gemini call if configured
    client = get_gemini_client()
    if client:
        try:
            prompt = f"""You are Pulse AI's Clinical Dietician and Sports Nutrition Scientist.
Generate a structured, scientifically balanced nutrition strategy for a client with:
- Weight: {req.weight_kg} kg
- Height: {req.height_cm} cm
- BMI: {bmi} ({bmi_cat})
- Goal: {req.goal}
- Dietary Preference: {req.preference}
- Target Daily Calories: {target_cals} kcal

You MUST respond strictly with a valid JSON object matching this exact schema:
{{
  "bmi_analysis": "2 sentence expert analysis tailored to their stats and goal",
  "daily_calories": {target_cals},
  "macros": {{
    "protein_g": 160,
    "carbs_g": 210,
    "fats_g": 55,
    "protein_pct": 30,
    "carbs_pct": 45,
    "fats_pct": 25
  }},
  "strategy_summary": "Comprehensive 2-3 sentence overview of why this meal strategy works for their goal",
  "meal_plan": {{
    "breakfast": {{
      "title": "Recipe name",
      "calories": 450,
      "macros": "35g P | 45g C | 12g F",
      "description": "Details of ingredients and prep"
    }},
    "lunch": {{
      "title": "Recipe name",
      "calories": 650,
      "macros": "45g P | 65g C | 18g F",
      "description": "Details of ingredients and prep"
    }},
    "snack": {{
      "title": "Recipe name",
      "calories": 250,
      "macros": "20g P | 25g C | 7g F",
      "description": "Details of ingredients and prep"
    }},
    "dinner": {{
      "title": "Recipe name",
      "calories": 550,
      "macros": "40g P | 50g C | 15g F",
      "description": "Details of ingredients and prep"
    }},
    "pre_post_workout": {{
      "title": "Pre/Post Workout Fuel",
      "calories": 200,
      "macros": "25g P | 22g C | 2g F",
      "description": "Nutrient timing details"
    }}
  }},
  "grocery_list": [
    {{
      "name": "Item 1",
      "category": "Protein / Plant Protein",
      "benefit": "Why this item is essential for their goal",
      "quantity_est": "e.g. 1 kg / 1 dozen"
    }},
    {{
      "name": "Item 2",
      "category": "Complex Carbohydrates",
      "benefit": "Why this item is essential",
      "quantity_est": "e.g. 500g"
    }},
    {{
      "name": "Item 3",
      "category": "Healthy Lipids",
      "benefit": "Why this item is essential",
      "quantity_est": "e.g. 1 kg"
    }},
    {{
      "name": "Item 4",
      "category": "Cruciferous Produce",
      "benefit": "Why this item is essential",
      "quantity_est": "e.g. 250g"
    }},
    {{
      "name": "Item 5",
      "category": "Superfood / Micronutrient",
      "benefit": "Why this item is essential",
      "quantity_est": "e.g. 1 bunch"
    }}
  ],
  "hydration_tip": "Specific daily fluid recommendation in liters with electrolyte guidance",
  "timing_tip": "Nutrient timing advice around training windows"
}}
Return ONLY valid JSON."""

            model_name = get_gemini_model()
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4
            )
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            raw = resp.text.strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```[a-z]*\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
            
            return NutritionResponse(
                bmi=bmi,
                bmi_category=bmi_cat,
                bmi_analysis=data.get("bmi_analysis", bmi_note),
                daily_calories=data.get("daily_calories", target_cals),
                macros=MacroBreakdown(**data["macros"]),
                strategy_summary=data.get("strategy_summary", "Customized fuel plan optimized for your metabolic demands."),
                meal_plan={k: MealItem(**v) for k, v in data.get("meal_plan", {}).items()},
                grocery_list=[GroceryItem(**item) for item in data.get("grocery_list", [])[:5]],
                hydration_tip=data.get("hydration_tip", f"Target at least {round(req.weight_kg * 0.04, 1)}L water daily."),
                timing_tip=data.get("timing_tip", "Consume high glycemic carbs + whey/plant protein within 60 minutes post-training."),
                source="gemini"
            )
        except Exception as e:
            print(f"Notice: Falling back to Pulse Autonomous Nutrition Engine: {e}")

    # =============================================================
    # HIGH-FIDELITY PULSE AUTONOMOUS NUTRITION ENGINE
    # Fully dynamic, handles Veg, Non-Veg, Vegan, Keto, Bulk, Cut
    # =============================================================
    pref_lower = req.preference.lower()
    is_keto = "keto" in pref_lower
    is_vegan = "vegan" in pref_lower
    is_veg = "veg" in pref_lower and not is_vegan and "non" not in pref_lower
    
    if is_keto:
        # Keto: 70% fat, 25% protein, 5% carbs
        protein_g = int(req.weight_kg * 1.8)
        carbs_g = 30
        fat_cals = target_cals - (protein_g * 4) - (carbs_g * 4)
        fat_g = max(40, int(fat_cals / 9))
    elif "loss" in req.goal.lower() or "shred" in req.goal.lower():
        # Fat Loss: High protein (2.2g/kg), moderate fat (25%), balance in carbs
        protein_g = int(req.weight_kg * 2.2)
        fat_g = int((target_cals * 0.25) / 9)
        carbs_g = max(40, int((target_cals - (protein_g * 4) - (fat_g * 9)) / 4))
    else:
        # Hypertrophy / Bulk / Performance: 2.0g/kg protein, 25% fat, high carbs
        protein_g = int(req.weight_kg * 2.0)
        fat_g = int((target_cals * 0.25) / 9)
        carbs_g = max(50, int((target_cals - (protein_g * 4) - (fat_g * 9)) / 4))

    total_macro_cals = (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)
    p_pct = int((protein_g * 4 / total_macro_cals) * 100)
    c_pct = int((carbs_g * 4 / total_macro_cals) * 100)
    f_pct = max(5, 100 - p_pct - c_pct)

    # Dynamic Meal Plan & 5-Item Grocery Generation based on Preference
    if is_keto:
        meals = {
            "breakfast": MealItem(
                title="Avocado, Spinach & Pasture Egg Omelette",
                calories=int(target_cals * 0.28),
                macros=f"{int(protein_g * 0.25)}g P | 4g C | {int(fat_g * 0.32)}g F",
                description="3 large pasture-raised eggs whisked with grass-fed butter, baby spinach, cheddar, and half a sliced hass avocado."
            ),
            "lunch": MealItem(
                title="Keto Salmon Salad with MCT Olive Oil Vinaigrette",
                calories=int(target_cals * 0.32),
                macros=f"{int(protein_g * 0.35)}g P | 6g C | {int(fat_g * 0.35)}g F",
                description="Pan-seared Atlantic salmon fillet on a bed of mixed arugula, cucumbers, walnuts, and extra virgin olive oil."
            ),
            "snack": MealItem(
                title="Macadamia Nuts & Sea Salt Dark Chocolate (90%)",
                calories=int(target_cals * 0.12),
                macros=f"{int(protein_g * 0.08)}g P | 3g C | {int(fat_g * 0.15)}g F",
                description="Raw macadamia nuts providing heart-healthy monounsaturated fats and essential minerals."
            ),
            "dinner": MealItem(
                title="Grass-Fed Ribeye with Roasted Garlic Asparagus",
                calories=int(target_cals * 0.28),
                macros=f"{int(protein_g * 0.32)}g P | 5g C | {int(fat_g * 0.28)}g F",
                description="Seared ribeye steak basted in rosemary herb butter alongside charred asparagus spears."
            ),
            "pre_post_workout": MealItem(
                title="BHB Ketones & Whey/Collagen Peptide Shake",
                calories=160,
                macros=f"{int(protein_g * 0.15)}g P | 2g C | 4g F",
                description="Zero-sugar cold-filtered isolate blended with unsweetened almond milk and MCT oil powder."
            )
        }
        groceries = [
            GroceryItem(name="Wild Atlantic Salmon Fillets", category="Omega-3 Protein", benefit="Zero-carb complete protein packed with anti-inflammatory EPA and DHA", quantity_est="800g (4 fillets)"),
            GroceryItem(name="Hass Avocados", category="Monounsaturated Fat", benefit="Potassium-dense healthy lipids to prevent keto-adaptation cramping", quantity_est="1 bag (5 avocados)"),
            GroceryItem(name="Pasture-Raised Large Eggs", category="Whole Food Protein", benefit="Choline and lutein rich with perfect 1:1 protein to healthy fat ratio", quantity_est="2 dozen"),
            GroceryItem(name="Raw Macadamia Nuts", category="Healthy Lipids", benefit="Highest monounsaturated fat concentration of any nut, keeping blood sugar flat", quantity_est="400g pack"),
            GroceryItem(name="Fresh Asparagus & Baby Spinach", category="Low-Carb Greens", benefit="Sulforaphane and magnesium without kicking you out of ketosis", quantity_est="1 kg bundle")
        ]

    elif is_vegan:
        meals = {
            "breakfast": MealItem(
                title="Hemp & Chia Seed Oatmeal with Plant Isolate",
                calories=int(target_cals * 0.25),
                macros=f"{int(protein_g * 0.25)}g P | {int(carbs_g * 0.35)}g C | {int(fat_g * 0.2)}g F",
                description="Sprouted rolled oats in almond milk, mixed with 1 scoop pea/rice protein isolate, chia seeds, and fresh blueberries."
            ),
            "lunch": MealItem(
                title="Smoked Tempeh & Tri-Color Quinoa Bowl",
                calories=int(target_cals * 0.35),
                macros=f"{int(protein_g * 0.35)}g P | {int(carbs_g * 0.35)}g C | {int(fat_g * 0.35)}g F",
                description="Fermented organic tempeh cubes pan-seared with coconut aminos, served over quinoa with steamed broccoli and tahini."
            ),
            "snack": MealItem(
                title="Edamame Pods with Sea Salt & Roasted Almonds",
                calories=int(target_cals * 0.12),
                macros=f"{int(protein_g * 0.12)}g P | {int(carbs_g * 0.1)}g C | {int(fat_g * 0.2)}g F",
                description="Whole steamed edamame providing complete plant amino acids and fiber."
            ),
            "dinner": MealItem(
                title="Red Lentil & Chickpea Coconut Curry with Brown Rice",
                calories=int(target_cals * 0.28),
                macros=f"{int(protein_g * 0.28)}g P | {int(carbs_g * 0.2)}g C | {int(fat_g * 0.25)}g F",
                description="Slow-simmered lentils, chickpeas, turmeric, cumin, and spinach with aromatic brown basmati rice."
            ),
            "pre_post_workout": MealItem(
                title="Organic Pea & Pumpkin Seed Protein Shake",
                calories=180,
                macros=f"{int(protein_g * 0.15)}g P | 20g C | 2g F",
                description="Fast-digesting plant protein isolate with ripe banana for rapid muscle glycogen resynthesis."
            )
        }
        groceries = [
            GroceryItem(name="Organic Fermented Tempeh", category="Complete Plant Protein", benefit="Prebiotic-rich fermented whole soybean with 40g complete protein per block", quantity_est="3 blocks (750g)"),
            GroceryItem(name="Tri-Color Sprouted Quinoa", category="Complex Carbs", benefit="Contains all 9 essential amino acids plus slow-burning sustained energy", quantity_est="1 kg bag"),
            GroceryItem(name="Shelled Hemp Hearts", category="Essential Omegas", benefit="Optimal 3:1 balance of Omega-6 to Omega-3 for joint recovery", quantity_est="400g pouch"),
            GroceryItem(name="Red Lentils & Chickpeas", category="Legumes & Fiber", benefit="High folate and iron to support oxygen transport during training", quantity_est="1 kg bag"),
            GroceryItem(name="Baby Kale & Spinach Medley", category="Micronutrient Produce", benefit="Bioavailable plant nitrates to elevate nitric oxide and blood flow", quantity_est="2 tubs (600g)")
        ]

    elif is_veg:
        meals = {
            "breakfast": MealItem(
                title="Cottage Cheese / Paneer & Sprouted Grain Bowl",
                calories=int(target_cals * 0.25),
                macros=f"{int(protein_g * 0.25)}g P | {int(carbs_g * 0.35)}g C | {int(fat_g * 0.2)}g F",
                description="Low-fat cottage cheese / fresh paneer paired with steel-cut oats, raw honey, walnuts, and strawberries."
            ),
            "lunch": MealItem(
                title="Mediterranean Tofu & Quinoa Power Bowl",
                calories=int(target_cals * 0.35),
                macros=f"{int(protein_g * 0.35)}g P | {int(carbs_g * 0.35)}g C | {int(fat_g * 0.35)}g F",
                description="Pan-seared extra-firm organic tofu, tri-color quinoa, roasted chickpeas, cucumbers, and tahini dressing."
            ),
            "snack": MealItem(
                title="Greek Yogurt (0% fat) with Crushed Walnuts",
                calories=int(target_cals * 0.12),
                macros=f"{int(protein_g * 0.12)}g P | {int(carbs_g * 0.1)}g C | {int(fat_g * 0.2)}g F",
                description="Strained Greek yogurt offering 20g slow-digesting casein protein to suppress catabolism."
            ),
            "dinner": MealItem(
                title="Spiced Yellow Dal Tadka with Brown Basmati & Greens",
                calories=int(target_cals * 0.28),
                macros=f"{int(protein_g * 0.28)}g P | {int(carbs_g * 0.2)}g C | {int(fat_g * 0.25)}g F",
                description="Protein-rich yellow and red lentils tempered with cumin, turmeric, garlic, served with brown rice."
            ),
            "pre_post_workout": MealItem(
                title="Whey / Plant Isolate with Crisp Rice Cakes",
                calories=190,
                macros=f"{int(protein_g * 0.15)}g P | 22g C | 1g F",
                description="Rapidly absorbed whey isolate providing 3g leucine to initiate muscle protein synthesis immediately."
            )
        }
        groceries = [
            GroceryItem(name="Extra-Firm Organic Tofu", category="Plant Protein", benefit="Complete amino acid profile providing 48g of bioavailable protein per pack", quantity_est="2 blocks (800g)"),
            GroceryItem(name="Greek Yogurt (Plain Strained)", category="Dairy Protein", benefit="Slow-digesting casein protein that feeds amino acids into the bloodstream over hours", quantity_est="2 tubs (1 kg)"),
            GroceryItem(name="Tri-Color Quinoa", category="Complex Carbs", benefit="Low-glycemic complex carbohydrate loaded with magnesium to prevent muscle fatigue", quantity_est="1 kg bag"),
            GroceryItem(name="Raw Walnuts & Chia Seeds", category="Healthy Lipids", benefit="Rich in ALA Omega-3 fatty acids for joint and tendon lubrication", quantity_est="350g pack"),
            GroceryItem(name="Fresh Broccoli & Baby Spinach", category="Micronutrients", benefit="High in bioavailable nitrates to boost nitric oxide and workout pump", quantity_est="1 kg")
        ]

    else:
        # Non-Veg High-Performance
        meals = {
            "breakfast": MealItem(
                title="Omega-3 Egg Scramble & Sourdough Avocado Toast",
                calories=int(target_cals * 0.26),
                macros=f"{int(protein_g * 0.26)}g P | {int(carbs_g * 0.25)}g C | {int(fat_g * 0.3)}g F",
                description="3 whole pasture-raised eggs scrambled with 2 egg whites, baby spinach, on sourdough toast with avocado."
            ),
            "lunch": MealItem(
                title="Rosemary Grilled Chicken Breast & Sweet Potato Wedges",
                calories=int(target_cals * 0.35),
                macros=f"{int(protein_g * 0.38)}g P | {int(carbs_g * 0.35)}g C | {int(fat_g * 0.25)}g F",
                description="220g grilled herb chicken breast, oven-roasted cinnamon sweet potato wedges, and steamed garlic broccoli."
            ),
            "snack": MealItem(
                title="Icelandic Skyr with Berries & Raw Almonds",
                calories=int(target_cals * 0.12),
                macros=f"{int(protein_g * 0.14)}g P | {int(carbs_g * 0.12)}g C | {int(fat_g * 0.15)}g F",
                description="High-density Skyr delivering 22g protein with antioxidant-rich blackberries."
            ),
            "dinner": MealItem(
                title="Wild Pan-Seared Salmon & Jasmine Rice Bowl",
                calories=int(target_cals * 0.27),
                macros=f"{int(protein_g * 0.22)}g P | {int(carbs_g * 0.28)}g C | {int(fat_g * 0.3)}g F",
                description="Wild Atlantic salmon fillet rich in EPA/DHA, fragrant jasmine rice, and charred asparagus spears with lemon."
            ),
            "pre_post_workout": MealItem(
                title="Cold-Filtered Whey Isolate & Banana Reload",
                calories=190,
                macros=f"{int(protein_g * 0.15)}g P | 24g C | 1g F",
                description="Ultra-clean whey isolate with high-glycemic fruit to rapidly reload intramuscular glycogen."
            )
        }
        groceries = [
            GroceryItem(name="Boneless Skinless Chicken Breast", category="Lean Protein", benefit="Complete ultra-lean amino acid source to repair microtears in muscle fibers", quantity_est="1.5 kg"),
            GroceryItem(name="Wild-Caught Salmon Fillets", category="Omega-3 Protein", benefit="High EPA/DHA fatty acids combat exercise-induced inflammation and protect joints", quantity_est="4 fillets (600g)"),
            GroceryItem(name="Organic Sweet Potatoes", category="Complex Carbs", benefit="Low-glycemic complex starch rich in potassium to prevent intra-workout cramps", quantity_est="2 kg bag"),
            GroceryItem(name="Pasture-Raised Large Eggs", category="Whole Food Protein", benefit="Choline-packed yolks optimize neuromuscular transmission and cell structure", quantity_est="2 dozen"),
            GroceryItem(name="Fresh Broccoli Crowns & Asparagus", category="Cruciferous Greens", benefit="Sulforaphane and indole-3-carbinol for optimal hormonal balance", quantity_est="1 kg")
        ]

    return NutritionResponse(
        bmi=bmi,
        bmi_category=bmi_cat,
        bmi_analysis=bmi_note,
        daily_calories=target_cals,
        macros=MacroBreakdown(
            protein_g=protein_g,
            carbs_g=carbs_g,
            fats_g=fat_g,
            protein_pct=p_pct,
            carbs_pct=c_pct,
            fats_pct=f_pct
        ),
        strategy_summary=f"Scientifically calibrated for {req.goal} with a {req.preference} protocol. Evenly spaces leucine-rich boluses to keep muscle protein synthesis elevated 24/7.",
        meal_plan=meals,
        grocery_list=groceries,
        hydration_tip=f"Consume a baseline of {round(req.weight_kg * 0.04, 1)} Liters of water daily, adding 500ml per 45 minutes of heavy resistance training.",
        timing_tip="Consume your primary carbohydrate allotment within 90 minutes before and immediately after your heaviest resistance training.",
        source="pulse-engine"
    )

# -------------------------------------------------------------
# Module 3: Smart Gym & Routine Recommender Endpoint
# -------------------------------------------------------------

@app.post("/api/routines", response_model=RoutineResponse)
async def recommend_routines(req: RoutineRequest):
    client = get_gemini_client()
    score = req.performance_score
    
    if score < 35:
        tier = "Foundation / Beginner"
    elif score < 75:
        tier = "Intermediate / Progressive Overload"
    else:
        tier = "Advanced / High Performance Elite"

    # Try live Gemini call if configured
    if client:
        try:
            prompt = f"""You are Pulse AI's Master Strength & Conditioning Coach and Local Fitness Concierge.
Generate a tailored training routine, daily challenge, and identify 3 REAL gym chains in the specified location.

Parameters:
- Location: {req.location}
- User Goal: {req.goal}
- Performance Score: {score}/100 ({tier})

Respond strictly with a valid JSON object matching this schema:
{{
  "workout_split": {{
    "split_name": "e.g. 4-Day Push-Pull-Legs Upper Hybrid",
    "frequency": "e.g. 4 days/week (Upper, Lower, Push, Pull)",
    "description": "Comprehensive explanation of how this split maximizes their {req.goal} based on score {score}",
    "days": [
      {{
        "day_title": "Day 1: Upper Body Power & Lat Width",
        "target_muscles": ["Chest", "Upper Back", "Deltoids", "Triceps"],
        "exercises": [
          {{
            "name": "Barbell Bench Press or Dumbbell Press",
            "sets": "3-4",
            "reps": "6-8",
            "rest_seconds": 120,
            "key_cue": "Retract scapulae, touch lower sternum, flare elbows at 45 degrees"
          }},
          {{
            "name": "Chest-Supported T-Bar Row",
            "sets": "3",
            "reps": "8-10",
            "rest_seconds": 90,
            "key_cue": "Pull with elbows, pause 1s at peak contraction"
          }},
          {{
            "name": "Incline Dumbbell Fly-Press Hybrid",
            "sets": "3",
            "reps": "10-12",
            "rest_seconds": 60,
            "key_cue": "Feel deep pectoralis stretch at the bottom"
          }}
        ]
      }},
      {{
        "day_title": "Day 2: Lower Body Quad & Posterior Chain",
        "target_muscles": ["Quadriceps", "Hamstrings", "Glutes", "Calves"],
        "exercises": [
          {{
            "name": "Barbell Back Squat",
            "sets": "3-4",
            "reps": "6-8",
            "rest_seconds": 150,
            "key_cue": "Break at hips and knees simultaneously, hit 95 degree depth"
          }},
          {{
            "name": "Romanian Deadlift (RDL)",
            "sets": "3",
            "reps": "8-10",
            "rest_seconds": 90,
            "key_cue": "Push hips back to wall, maintain neutral lumbar spine"
          }},
          {{
            "name": "Walking Dumbbell Lunges",
            "sets": "3",
            "reps": "12 steps/leg",
            "rest_seconds": 60,
            "key_cue": "Upright torso, 90 degree front knee angle"
          }}
        ]
      }},
      {{
        "day_title": "Day 3: Hypertrophy & Weak Point Synergy",
        "target_muscles": ["Shoulders", "Biceps", "Triceps", "Core"],
        "exercises": [
          {{
            "name": "Overhead Dumbbell Shoulder Press",
            "sets": "3",
            "reps": "8-10",
            "rest_seconds": 90,
            "key_cue": "Lock out overhead with bicep next to ears"
          }},
          {{
            "name": "Cable Lateral Raise",
            "sets": "4",
            "reps": "12-15",
            "rest_seconds": 45,
            "key_cue": "Lead with elbows for targeted lateral deltoid activation"
          }},
          {{
            "name": "Hanging Leg Raises",
            "sets": "3",
            "reps": "12-15",
            "rest_seconds": 60,
            "key_cue": "Posterior pelvic tilt at the top to fire rectus abdominis"
          }}
        ]
      }}
    ]
  }},
  "daily_challenge": {{
    "title": "Custom Challenge Name matching performance score {score}",
    "difficulty_badge": "{tier}",
    "description": "Engaging description of today's fitness benchmark",
    "challenge_steps": [
      "Step 1 detail",
      "Step 2 detail",
      "Step 3 detail"
    ],
    "completion_time_est": "e.g. 10-12 minutes"
  }},
  "local_gyms": [
    {{
      "name": "Real Gym Chain Name in or near {req.location}",
      "locality_context": "Exact presence or branches known in {req.location}",
      "vibe": "e.g. High-energy functional training / Iron Paradise",
      "key_amenities": ["Olympic Barbells", "Sauna & Ice Bath", "Turf Sprint Track"],
      "why_recommended": "Why this specific facility excels for {req.goal}"
    }},
    {{
      "name": "Second Real Gym Chain in {req.location}",
      "locality_context": "Branch info in {req.location}",
      "vibe": "e.g. Premium wellness & state-of-the-art strength machines",
      "key_amenities": ["Hammer Strength Line", "HydroMassage", "Steam Room"],
      "why_recommended": "Why it suits their score and training style"
    }},
    {{
      "name": "Third Real Gym Chain in {req.location}",
      "locality_context": "Branch info in {req.location}",
      "vibe": "e.g. 24/7 accessible athletic club",
      "key_amenities": ["Squat Racks", "Kettlebells", "Private Showers"],
      "why_recommended": "Why it provides great value and consistency"
    }}
  ],
  "coach_note": "A powerful 2-sentence piece of guidance connecting their score to long-term gains"
}}
Return ONLY valid JSON."""

            model_name = get_gemini_model()
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4
            )
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            raw = resp.text.strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```[a-z]*\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
            
            return RoutineResponse(
                workout_split=WorkoutSplit(**data["workout_split"]),
                daily_challenge=DailyChallenge(**data["daily_challenge"]),
                local_gyms=[LocalGym(**g) for g in data.get("local_gyms", [])[:3]],
                coach_note=data.get("coach_note", "Consistency triumphs over intensity. Show up and execute."),
                source="gemini"
            )
        except Exception as e:
            print(f"Notice: Falling back to Pulse Autonomous Routine Engine: {e}")

    # =============================================================
    # HIGH-FIDELITY PULSE AUTONOMOUS ROUTINE & LOCAL GYM ENGINE
    # Geo-aware real gym mapping across US, UK, India, Canada, AUS
    # =============================================================
    loc = req.location.strip() or "Metropolitan Area"
    loc_lower = loc.lower()
    
    # 1. Hyperlocal Gym Database Matching
    if any(c in loc_lower for c in ["india", "bangalore", "mumbai", "delhi", "hyderabad", "pune", "chennai", "kolkata", "gurgaon", "noida", "indiranagar", "koramangala"]):
        gym1 = LocalGym(
            name="Cult.fit",
            locality_context=f"Flagship centers conveniently situated across {loc}",
            vibe="Modern High-Intensity Functional & Strength Training",
            key_amenities=["HRX Training Zone", "Boxing Rings", "S&C Conditioning Turf", "In-house Physiotherapists"],
            why_recommended=f"Ideal for your {req.goal} with guided group strength classes and dedicated open gym turf."
        )
        gym2 = LocalGym(
            name="Gold's Gym India",
            locality_context=f"Established premier strength franchises serving {loc}",
            vibe="Old-School Heavy Iron & Serious Hypertrophy",
            key_amenities=["Eleiko Olympic Barbells", "Dumbbells up to 60kg", "Steam & Sauna", "Cardio Deck"],
            why_recommended="Unrivaled equipment depth for progressive overload and heavy compound movements."
        )
        gym3 = LocalGym(
            name="Anytime Fitness",
            locality_context=f"24/7 neighborhood locations throughout {loc}",
            vibe="Clean, Uncrowded 24/7 Community Strength Hub",
            key_amenities=["24/7 Keycard Access", "Power Cages & Bumper Plates", "Functional Cable Crosses"],
            why_recommended="Zero-friction scheduling—train at whatever hour your peak physical energy strikes."
        )
    elif any(c in loc_lower for c in ["uk", "london", "manchester", "birmingham", "edinburgh", "glasgow", "bristol", "leeds"]):
        gym1 = LocalGym(
            name="PureGym",
            locality_context=f"Widespread 24/7 high-spec clubs in {loc}",
            vibe="High-Value Modern Functional & Strength Hub",
            key_amenities=["Multiple Olympic Lifting Platforms", "50kg+ Dumbbell Racks", "Functional Rig Zones"],
            why_recommended="Exceptional equipment availability without contracts, perfect for progressive overload."
        )
        gym2 = LocalGym(
            name="Third Space",
            locality_context=f"Iconic luxury athletic sanctuaries in {loc}",
            vibe="Elite Performance & Biophilic Recovery Sanctuary",
            key_amenities=["Hypoxic Altitude Chambers", "Olympic Rig & Sled Tracks", "Cryotherapy & Hydro Pools"],
            why_recommended="State-of-the-art sports science facilities tailored for serious athletes."
        )
        gym3 = LocalGym(
            name="The Gym Group",
            locality_context=f"Centrally located facilities across {loc}",
            vibe="Accessible, 24/7 Clean Strength Floor",
            key_amenities=["24/7 Secure Access", "Weightlifting Platforms", "Free Weight Area"],
            why_recommended="Reliable setup with plenty of squat racks to dial in your form."
        )
    elif any(c in loc_lower for c in ["canada", "toronto", "vancouver", "montreal", "calgary", "ottawa", "edmonton"]):
        gym1 = LocalGym(
            name="GoodLife Fitness",
            locality_context=f"Flagship and express locations throughout {loc}",
            vibe="Comprehensive Multi-Level Athletic Health Club",
            key_amenities=["Hammer Strength Iso-Lateral Machines", "Olympic Platforms", "Hot Yoga Studios", "Sauna"],
            why_recommended=f"Complete equipment variety to support your {req.goal} with plenty of power cages."
        )
        gym2 = LocalGym(
            name="Club 16 Trevor Linden / Movati",
            locality_context=f"Premier regional fitness centers in {loc}",
            vibe="High-Energy Community Strength & Functional Zone",
            key_amenities=["Functional Turf Agility Area", "Free Weights to 120 lbs", "HydroMassage Lounges"],
            why_recommended="Spacious barbell areas designed for progressive overload and form tracking."
        )
        gym3 = LocalGym(
            name="Anytime Fitness Canada",
            locality_context=f"24/7 neighborhood access clubs in {loc}",
            vibe="Accessible, 24/7 Keycard Strength Sanctuary",
            key_amenities=["Round-the-Clock Access", "Squat Racks", "Olympic Bumper Plates"],
            why_recommended="Guarantees you never miss a training split day regardless of your schedule."
        )
    elif any(c in loc_lower for c in ["australia", "sydney", "melbourne", "brisbane", "perth", "adelaide"]):
        gym1 = LocalGym(
            name="Fitness First Australia",
            locality_context=f"Titanium and Platinum clubs across {loc}",
            vibe="High-Performance Athletic Club & Strength Floor",
            key_amenities=["Olympic Lifting Platforms", "Freemotion Cables", "Steam & Recovery Suites"],
            why_recommended=f"Top-tier strength facilities engineered for serious {req.goal} progression."
        )
        gym2 = LocalGym(
            name="Virgin Active Australia",
            locality_context=f"Premium athletic sanctuaries serving {loc}",
            vibe="Luxury Wellness, Strength & Biomechanics Hub",
            key_amenities=["Reformer Pilates", "Grid Functional Training", "25m Lap Pools", "Ice Baths"],
            why_recommended="Unmatched recovery facilities that accelerate supercompensation between heavy sessions."
        )
        gym3 = LocalGym(
            name="Anytime Fitness AU",
            locality_context=f"Convenient neighborhood clubs throughout {loc}",
            vibe="24/7 Uncrowded Barbell & Dumbbell Facility",
            key_amenities=["24/7 Biometric Entry", "Eleiko Bars", "Bumper Plates"],
            why_recommended="Reliable squat and deadlift bays available 365 days a year."
        )
    else:
        # Default United States / Global
        gym1 = LocalGym(
            name="Equinox",
            locality_context=f"Premier athletic sanctuaries in and around {loc}",
            vibe="High-End Athletic Performance & Elite Recovery",
            key_amenities=["Precision Olympic Platforms", "Eucalyptus Steam Rooms", "Cold Plunges & Spa"],
            why_recommended=f"Unmatched equipment standards and recovery amenities that accelerate {req.goal}."
        )
        gym2 = LocalGym(
            name="Gold's Gym",
            locality_context=f"Legendary bodybuilding and strength centers serving {loc}",
            vibe="The Mecca of Raw Iron & Muscle Hypertrophy",
            key_amenities=["Calibrated Steel Plates", "Monolifts & Deadlift Deadening Mats", "Heavy Dumbbells to 150 lbs"],
            why_recommended="The ultimate environment to surround yourself with serious lifters pushing progressive overload."
        )
        gym3 = LocalGym(
            name="Lifetime Fitness / LA Fitness",
            locality_context=f"High-accessibility clubs throughout {loc}",
            vibe="Comprehensive 24/7 Family & Functional Athletic Club",
            key_amenities=["Multi-Bay Squat Racks", "Turf Agility Lanes", "Lap Pools & Recovery Saunas"],
            why_recommended="Round-the-clock availability ensures you never miss a training split session."
        )

    # 2. Daily Challenge scaled to Performance Score
    if score < 35:
        challenge = DailyChallenge(
            title="The Foundation Catalyst",
            difficulty_badge="Level 1: Foundation",
            description="Build joint stability, tendon tensile strength, and neurological motor patterns.",
            challenge_steps=[
                "3 rounds: 12 Bodyweight Squats (hitting 95° depth with 2s pause at bottom)",
                "3 rounds: 30-second Plank with active glute and lat contraction",
                "3 rounds: 10 Incline Push-ups focusing on full scapular protraction at top",
                "Cool-down: 3 minutes of Couch Stretch for hip flexor mobility"
            ],
            completion_time_est="10-12 minutes"
        )
    elif score < 75:
        challenge = DailyChallenge(
            title="The Hypertrophy Furnace",
            difficulty_badge="Level 2: Progressive Athlete",
            description="Test your lactate threshold and muscular stamina under continuous tension.",
            challenge_steps=[
                "Accumulate 50 Deep Squats in under 4 minutes using Pulse AI's Pose Coach",
                "EMOM for 6 minutes: 12 Push-ups + 6 Burpees",
                "3 sets of 45-second Wall Sits holding a 90° knee angle",
                "Finisher: 2-minute Hollow Body Hold"
            ],
            completion_time_est="14-16 minutes"
        )
    else:
        challenge = DailyChallenge(
            title="The Spartan Crucible 100",
            difficulty_badge="Level 3: Elite Conditioning",
            description="Elite-tier anaerobic endurance challenge designed to push VO2 max and mental fortitude.",
            challenge_steps=[
                "100 Squats below 95° angle logged via AI Pose Coach in under 5 minutes",
                "50 Hand-Release Push-ups with strict core bracing",
                "5 rounds: 20 Jumping Lunges + 15 V-Ups with zero rest between movements",
                "Finisher: 3-minute continuous Plank"
            ],
            completion_time_est="18-20 minutes"
        )

    # 3. Customized Split tailored to Goal
    if "strength" in req.goal.lower():
        split_days = [
            WorkoutDay(
                day_title="Day 1: Heavy Squat & Posterior Drive",
                target_muscles=["Quadriceps", "Gluteus Maximus", "Adductors", "Core"],
                exercises=[
                    Exercise(name="Barbell Back Squat", sets="5", reps="3-5", rest_seconds=180, key_cue="Brace 360°, break hips and knees together, break 95° parallel"),
                    Exercise(name="Romanian Deadlift (RDL)", sets="4", reps="6-8", rest_seconds=120, key_cue="Hips travel straight back, lats engaged to pin bar to shins"),
                    Exercise(name="Bulgarian Split Squat", sets="3", reps="8 / leg", rest_seconds=90, key_cue="Drive through front heel, maintain vertical shin angle")
                ]
            ),
            WorkoutDay(
                day_title="Day 2: Competition Bench & Upper Power",
                target_muscles=["Pectoralis Major", "Triceps", "Anterior Delts", "Lats"],
                exercises=[
                    Exercise(name="Barbell Flat Bench Press", sets="5", reps="3-5", rest_seconds=180, key_cue="Retract scapulae into bench, touch lower sternum, push J-curve"),
                    Exercise(name="Weighted Pull-ups / Heavy Lat Pulldown", sets="4", reps="6-8", rest_seconds=120, key_cue="Depress scapulae first, drive elbows into back pockets"),
                    Exercise(name="Overhead Barbell Press (OHP)", sets="3", reps="6-8", rest_seconds=120, key_cue="Glutes locked, head pushes through the window at lockout")
                ]
            ),
            WorkoutDay(
                day_title="Day 3: Conventional Deadlift & Accessory",
                target_muscles=["Erector Spinae", "Hamstrings", "Lats", "Traps"],
                exercises=[
                    Exercise(name="Barbell Deadlift (Floor)", sets="4", reps="3-5", rest_seconds=210, key_cue="Pull slack out of bar, wedge hips, push floor away"),
                    Exercise(name="Chest-Supported T-Bar Row", sets="4", reps="8-10", rest_seconds=90, key_cue="Hold 1s peak contraction against pad, full eccentric stretch"),
                    Exercise(name="Standing Cable Woodchoppers", sets="3", reps="12 / side", rest_seconds=60, key_cue="Rotational power driven by hips and core bracing")
                ]
            )
        ]
    elif "athletic" in req.goal.lower() or "conditioning" in req.goal.lower():
        split_days = [
            WorkoutDay(
                day_title="Day 1: Explosive Power & Triple Extension",
                target_muscles=["Glutes", "Hamstrings", "Shoulders", "Cardiovascular"],
                exercises=[
                    Exercise(name="Kettlebell Swings (Hardstyle)", sets="4", reps="15-20", rest_seconds=60, key_cue="Violent hip snap, plank at top, don't squat the swing"),
                    Exercise(name="Goblet Squats with 3s Pause", sets="4", reps="10-12", rest_seconds=75, key_cue="Sink to 90° angle, pause without losing lumbar tension"),
                    Exercise(name="Plyometric Push-ups / Med Ball Slams", sets="4", reps="8-10", rest_seconds=60, key_cue="Explode through hands, land with soft elbows")
                ]
            ),
            WorkoutDay(
                day_title="Day 2: Multi-Planar Mobility & Core Rotational Power",
                target_muscles=["Adductors", "Obliques", "Upper Back", "Rotator Cuff"],
                exercises=[
                    Exercise(name="Cossack Squats / Lateral Lunges", sets="3", reps="8 / side", rest_seconds=60, key_cue="Keep trailing foot grounded, sink deep into hip crease"),
                    Exercise(name="Single-Arm Dumbbell Snatch", sets="4", reps="6 / arm", rest_seconds=90, key_cue="High pull with elbow leading, punch ceiling at lockout"),
                    Exercise(name="Farmer's Walks (Heavy Dumbbells)", sets="4", reps="40 meters", rest_seconds=60, key_cue="Tall posture, ribcage pinned down, short rapid steps")
                ]
            ),
            WorkoutDay(
                day_title="Day 3: Anaerobic Lactate Capacity & Sprint Intervals",
                target_muscles=["Total Body VO2 Max", "Calves", "Quads"],
                exercises=[
                    Exercise(name="Trap Bar Deadlift (High Handles)", sets="4", reps="8-10", rest_seconds=90, key_cue="Upright torso, rapid explosive drive"),
                    Exercise(name="Assault Bike / Rower Sprints", sets="6", reps="20s on / 40s off", rest_seconds=40, key_cue="All-out maximum wattage output"),
                    Exercise(name="Hanging Toes-to-Bar", sets="3", reps="10-12", rest_seconds=60, key_cue="Kip rhythmically, active shoulder depression")
                ]
            )
        ]
    else:
        # Hypertrophy / Muscle Building Default
        split_days = [
            WorkoutDay(
                day_title="Day 1: Upper Body Horizontal Force & Lat Spread",
                target_muscles=["Pectoralis Major", "Latissimus Dorsi", "Anterior Deltoids", "Triceps"],
                exercises=[
                    Exercise(name="Barbell / Dumbbell Flat Press", sets="4", reps="6-8", rest_seconds=120, key_cue="Drive through mid-foot, touch sternum, retract scapulae"),
                    Exercise(name="Chest-Supported Neutral Dumbbell Row", sets="4", reps="8-10", rest_seconds=90, key_cue="Lead with elbows, squeeze rhomboids for 1 full second"),
                    Exercise(name="Incline Cable Flys", sets="3", reps="12-15", rest_seconds=60, key_cue="Keep elbows soft, achieve deep fascial stretch at bottom"),
                    Exercise(name="Triceps Rope Pushdowns", sets="3", reps="12-15", rest_seconds=45, key_cue="Flare ropes at bottom, pin elbows strictly to your ribcage")
                ]
            ),
            WorkoutDay(
                day_title="Day 2: Lower Body Knee-Dominant & Glute Drive",
                target_muscles=["Quadriceps", "Gluteus Maximus", "Adductors", "Calves"],
                exercises=[
                    Exercise(name="Barbell Back Squat / Goblet Squat", sets="4", reps="6-8", rest_seconds=150, key_cue="Break at hips, descend until femur is sub-parallel (angle < 95°)"),
                    Exercise(name="Romanian Deadlifts (RDL)", sets="3", reps="8-10", rest_seconds=90, key_cue="Hinge at hips, keep bar skimming shins, feel intense hamstring tension"),
                    Exercise(name="Bulgarian Split Squats", sets="3", reps="10 / leg", rest_seconds=75, key_cue="Slight forward torso lean to target glute-ham tie-in"),
                    Exercise(name="Standing Calf Raises", sets="4", reps="15-20", rest_seconds=45, key_cue="Full 2-second pause in deep dorsiflexion stretch")
                ]
            ),
            WorkoutDay(
                day_title="Day 3: Overhead Power & Vertical Pull",
                target_muscles=["Lateral Deltoids", "Upper Trapezius", "Biceps", "Core"],
                exercises=[
                    Exercise(name="Standing Overhead Barbell / Dumbbell Press", sets="4", reps="6-8", rest_seconds=120, key_cue="Glutes locked, head pushes through the window at lockout"),
                    Exercise(name="Weighted Pull-ups / Lat Pulldowns", sets="4", reps="8-10", rest_seconds=90, key_cue="Depress shoulders before initiating pull; chest touches bar"),
                    Exercise(name="Leaning Cable Lateral Raises", sets="4", reps="12-15", rest_seconds=60, key_cue="Maintain constant tension through side deltoid path"),
                    Exercise(name="Incline Dumbbell Bicep Curls", sets="3", reps="10-12", rest_seconds=60, key_cue="Emphasize long head bicep stretch behind the torso")
                ]
            )
        ]

    split = WorkoutSplit(
        split_name=f"Pulse Optimized {req.goal} Split ({tier})",
        frequency="4-5 days per week with active recovery intervals",
        description=f"Engineered specifically for {req.goal} at performance rating {score}/100. Leverages compound lifts as primary neural drivers followed by high-metabolic accessory work.",
        days=split_days
    )

    return RoutineResponse(
        workout_split=split,
        daily_challenge=challenge,
        local_gyms=[gym1, gym2, gym3],
        coach_note=f"At a score of {score}/100, your physical capacity is primed for systematic progressive overload. Log every lift and verify deep squat depth on our AI Pose Coach.",
        source="pulse-engine"
    )

# Entry point for direct execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"🚀 Starting Pulse AI server on http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
