import os
import re
from typing import List, Optional
from pydantic import BaseModel, Field

# Try to import Google GenAI
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

COACH_SYSTEM_PROMPT = """You are Pulse AI's Elite Futuristic Fitness Coach, Biomechanics Specialist, and High-Performance Motivational Mentor.
Your mission is to provide world-class, science-backed guidance to athletes, lifters, and fitness enthusiasts at every level.

Core Principles:
1. Deep Muscle Anatomy & Joint Kinematics: Explain prime movers, stabilizer muscles, moment arms, bar paths, and injury prehab.
2. High-Octane Motivation & Mental Grit: Instill fierce discipline, overcoming mental blocks, self-doubt, and physical exhaustion. Be empathetic yet relentless.
3. Indian Dietary & Lifestyle Optimization: Understand Indian dietary realities (Paneer, Soya chunks, Moong dal, Besan, Sattu, Eggs, Chicken, Indian meal timing, hydration in tropical heat).
4. Recovery & Autoregulation: Explain CNS fatigue, sleep architecture, deload weeks, and stress modulation.
5. Flexible & Universal: Answer ANY fitness, nutrition, habit, or biomechanical question with clarity, enthusiasm, and scientific precision.

Formatting Rules:
- Use clean Markdown with bold headers and crisp bullet points.
- Provide immediately actionable steps.
- Conclude with 3 dynamic, punchy actionable tips and a powerful motivational quote.
"""

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: Optional[str] = Field(default="", description="User message text")
    history: Optional[List[ChatMessage]] = Field(default_factory=list)

class ChatResponse(BaseModel):
    reply: str
    sentiment_detected: Optional[str] = "Motivated & Focused"
    actionable_tips: Optional[List[str]] = Field(default_factory=list)
    motivational_quote: Optional[str] = "Discipline is choosing between what you want now and what you want most."
    source: str = "pulse-engine"

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    if not GENAI_AVAILABLE:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Notice: Gemini client init error, falling back: {e}")
        return None

def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

async def generate_chat_response(req: ChatRequest) -> ChatResponse:
    try:
        user_msg = (req.message or "").strip()
        if not user_msg:
            return ChatResponse(
                reply=(
                    "### ⚡ Pulse AI Cyber Coach Online\n\n"
                    "I am your **Autonomous Biomechanics & Motivational Mentor**.\n\n"
                    "Ask me about:\n"
                    "* **🏋️ Squat Biomechanics & Knee Caving:** Moment arms and 95° depth.\n"
                    "* **🔥 Overcoming Laziness & Fatigue:** Autoregulation and mental grit.\n"
                    "* **🍛 Indian High-Protein Nutrition:** Paneer, soya chunks, dal, and desi eggs.\n"
                    "* **📊 Workout Splits & Progressive Overload:** PPL, Upper/Lower, and deload protocols."
                ),
                sentiment_detected="Ready to Coach",
                actionable_tips=[
                    "Ask a specific lifting form or biomechanics question.",
                    "Tell me how you are feeling today: tired, sore, or hyped.",
                    "Inquire about high-protein Indian vegetarian meal combinations."
                ],
                motivational_quote="“The secret of getting ahead is getting started.”",
                source="pulse-engine"
            )

        client = get_gemini_client()
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
                    max_output_tokens=1400
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                    config=config
                )
                reply = response.text or "I am with you. Lock in and let's achieve greatness."
                
                sentiment = detect_sentiment(user_msg)
                tips = extract_or_default_tips(user_msg)
                quote = get_motivational_quote(sentiment)

                return ChatResponse(
                    reply=reply,
                    sentiment_detected=sentiment,
                    actionable_tips=tips,
                    motivational_quote=quote,
                    source="gemini"
                )
            except Exception as e:
                print(f"Notice: Falling back to Pulse Autonomous Engine: {e}")

        # Fallback to Pulse Autonomous Kinesiology & Motivational Engine 3.0
        return generate_autonomous_response(user_msg)
    except Exception as fatal_e:
        print(f"Error in generate_chat_response (recovering gracefully): {fatal_e}")
        return generate_autonomous_response(req.message or "fitness guidance")

def detect_sentiment(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["tired", "exhausted", "sore", "drained", "sleepy", "burnout", "no energy", "heavy", "fatigued"]):
        return "Fatigued / Autoregulation Needed"
    if any(w in lower for w in ["lazy", "demotivated", "unmotivated", "can't get up", "struggling", "skip", "quit", "slack"]):
        return "Seeking Discipline & Mental Spark"
    if any(w in lower for w in ["hyped", "pumped", "pr", "crush", "let's go", "ready", "beast", "fire", "unstoppable", "energy"]):
        return "Peak Neuromuscular Drive"
    if any(w in lower for w in ["pain", "hurt", "tweak", "strain", "injured", "ache", "impinge", "pop"]):
        return "Injury Alert & Joint Care"
    if any(w in lower for w in ["stuck", "plateau", "no progress", "weak", "frustrated", "not growing", "fail"]):
        return "Plateau Breakthrough Protocol"
    if any(w in lower for w in ["stress", "anxious", "overwhelmed", "hectic", "pressure", "nervous"]):
        return "CNS Stress Modulation"
    return "High Performance Focus"

def get_motivational_quote(sentiment: str) -> str:
    quotes = {
        "Seeking Discipline & Mental Spark": "“Motivation gets you started; discipline keeps you growing. Show up today, especially when you don't feel like it.”",
        "Fatigued / Autoregulation Needed": "“Recovery is not a sign of weakness; it is the forge where your muscles rebuild stronger than yesterday.”",
        "Peak Neuromuscular Drive": "“Channel this fire. Every rep with pristine form is an investment in the unstoppable version of you.”",
        "Injury Alert & Joint Care": "“Longevity is the ultimate victory in fitness. Protect the joints today so you can lift heavy for decades to come.”",
        "Plateau Breakthrough Protocol": "“The resistance you face in the gym and the resistance you face in life can only build a stronger character.”",
        "CNS Stress Modulation": "“Control the breath, ground your feet, and let the barbell be your sanctuary of clarity.”",
        "High Performance Focus": "“Consistency eats talent for breakfast. Execute your routine relentlessly day after day.”"
    }
    return quotes.get(sentiment, "“Small daily disciplines compounded over time yield miraculous physical transformations.”")

def extract_or_default_tips(text: str) -> List[str]:
    lower = text.lower()
    if any(w in lower for w in ["squat", "leg", "knee", "depth"]):
        return [
            "Drive your knees outward over your second toe to create room for deep hip descent.",
            "Maintain 360° intra-abdominal pressure (Valsalva brace) before descending.",
            "Explode through mid-foot and heel while keeping your chest proud."
        ]
    if any(w in lower for w in ["diet", "food", "protein", "paneer", "soya", "egg"]):
        return [
            "Spread your protein intake across 4 distinct meals to maximize muscle protein synthesis.",
            "Drink 3.5L to 4.5L of water daily, adding lemon & rock salt for electrolyte balance.",
            "Weigh yourself once weekly under identical conditions to gauge real trends."
        ]
    return [
        "Focus on controlled 2-3 second eccentric cadence on every working rep.",
        "Hydrate with 500ml of water and electrolytes 30 minutes prior to training.",
        "Track every single set and aim for a 1-2% progressive overload each week."
    ]

def generate_autonomous_response(user_msg: str) -> ChatResponse:
    lower = user_msg.lower()
    sentiment = detect_sentiment(user_msg)
    quote = get_motivational_quote(sentiment)

    # 1. Motivation / Mindset / Feeling Lazy / Skipping Gym
    if any(w in lower for w in ["lazy", "demotivated", "unmotivated", "can't get up", "struggling", "skip", "quit", "give up", "hard", "discipline", "mindset", "motivat"]):
        reply = (
            "### ⚡ Master Mindset: Action Precedes Motivation\n\n"
            "Here is the fundamental neurobiology of training: **Motivation is a fickle emotion, but Discipline is an unbreakable habit.** "
            "You do not wait to feel like working out to train; you take action, and the dopamine cascade follows your movement.\n\n"
            "* **The 5-Minute Activation Trigger:** Don't negotiate with your brain about an entire 60-minute brutal session. Tell yourself: *\"I will put on my shoes, do 5 minutes of dynamic warm-up, and hit one light set.\"* In 95% of cases, crossing that friction threshold unleashes momentum.\n"
            "* **The Identity Shift:** Amateurs train when conditions are perfect. Champions train because execution is part of their identity. The sessions where you show up tired and reluctant are the ones that fundamentally forge mental grit.\n"
            "* **Compound Momentum:** A workout completed at 70% intensity is infinitely superior to the workout you skipped on the couch. Every single rep counts toward your long-term transformation.\n\n"
            "**Coach's Directive:** Stand up right now. Take 3 deep diaphragmatic breaths, drink a glass of water, and move your body. You will NEVER regret finishing a workout!"
        )
        tips = [
            "Apply the 5-Minute Rule: put on training gear and just start with joint rotations.",
            "Visualize the post-workout endorphin rush and sense of pride you will feel in 45 minutes.",
            "Treat your workout like an immovable meeting with your future, strongest self."
        ]

    # 2. Fatigue / Exhaustion / Burnout / Low Energy
    elif any(w in lower for w in ["tired", "exhausted", "burnout", "drained", "sleepy", "no energy", "heavy", "fatigued", "sore"]):
        reply = (
            "### 🧘 Strategic Autoregulation: Respecting CNS & Muscular Biofeedback\n\n"
            "Fatigue is not failure—it is critical biological data signaling that your central nervous system (CNS) and muscle tissue are demanding recovery resources:\n\n"
            "* **Autoregulate with RPE (Rating of Perceived Exertion):** Today is not the day to hunt for a 1-Rep Max. Drop your working loads by 15-20%, cap your sets at **RPE 6.5–7** (leaving 3-4 clean reps in reserve), and prioritize absolute technical perfection.\n"
            "* **The 15-Minute Blood-Flow Flush:** If heavy weights feel impossible, do 15 minutes of brisk incline walking or light cycling followed by deep hip and thoracic mobility drills. This flushes metabolic waste and accelerates muscular supercompensation.\n"
            "* **Electrolyte & Glycogen Rescue:** Fatigue is often disguised dehydration. Down 500ml water mixed with a pinch of pink Himalayan rock salt and lemon juice to restore cellular osmolarity.\n"
            "* **Sleep Protocol:** Tonight, initiate a blue-light fast 45 minutes before bed and target 8 hours of deep slow-wave sleep to surge natural Growth Hormone (GH).\n\n"
            "**Coach's Directive:** Listen to your physiology. An athlete who autoregulates intelligently never hits a catastrophic burnout wall."
        )
        tips = [
            "Downscale intensity by 15% today and prioritize mind-muscle connection over heavy loads.",
            "Drink 500ml cold water with pink salt and fresh lemon for immediate cellular hydration.",
            "Aim to get in bed 30-45 minutes earlier tonight to replenish central nervous energy."
        ]

    # 3. Indian Diet / Vegetarian Protein / Indian Meals
    elif any(w in lower for w in ["indian", "paneer", "soya", "roti", "dal", "sattu", "besan", "rice", "curd", "dahi", "veg", "vegetarian", "khichdi", "chana", "rajma"]):
        reply = (
            "### 🍛 Indian Fitness Nutrition: Complete High-Protein Mastery\n\n"
            "A major myth is that an authentic Indian diet cannot build elite muscle or shred fat. By engineering your traditional meals, you can hit 120g–160g+ of high-bioavailability protein effortlessly:\n\n"
            "* **The Indian Vegetarian Super-Combos (Complete Amino Acids):**\n"
            "  * **Low-Fat / Malai Paneer (150-200g):** Delivers ~28-36g of slow-digesting casein protein, ideal for sustained nitrogen retention.\n"
            "  * **Soya Chunks (50g dry):** A powerhouse delivering **26g of pure protein** with zero cholesterol. Soak in warm salted water, squeeze thoroughly, and saute with masala.\n"
            "  * **Dal + Roti / Rice Synergy:** Pulses (rich in lysine) paired with whole grains (rich in methionine) form a complete essential amino acid profile.\n"
            "  * **Sattu (Roasted Chana Flour):** Mix 40g sattu in chilled water with roasted jeera, rock salt, and lemon for a 10g natural protein energizer.\n"
            "* **For Indian Non-Vegetarians:**\n"
            "  * 4 Egg whites + 2 whole eggs bhurji with 2 multigrain phulkas = ~30g high-BV protein.\n"
            "  * Tandoori / Grilled Chicken Breast (150g) seasoned with turmeric, ginger-garlic, and hung curd = ~45g lean protein.\n"
            "* **Tropical Hydration:** Indian temperatures demand 3.5L to 4.5L of water daily. Use nimbu paani (lemon water with rock salt) to balance sodium-potassium pumps.\n\n"
            "**Coach's Directive:** Check our **AI Dietician** tab! It is custom-built with complete Indian vegetarian and non-vegetarian meal plans and 5-item local grocery lists."
        )
        tips = [
            "Combine lentils with whole grains or paneer/dahi to ensure a complete amino acid profile.",
            "Incorporate 40-50g of soya chunks daily for the highest protein-to-cost ratio in India.",
            "Drink a glass of warm turmeric milk with a pinch of black pepper at bedtime for recovery."
        ]

    # 4. Squat / Pose Coach / Biomechanics / Knee Cave
    elif any(w in lower for w in ["squat", "knee", "depth", "pose", "camera", "form", "patellar", "hip", "ankle"]):
        reply = (
            "### 🏋️ Squat Biomechanics & Kinematic Optimization\n\n"
            "The squat is the king of closed-kinetic-chain lower body movements. Executing safe, explosive depth is governed by precise joint angles:\n\n"
            "* **Acetabular Hip Clearance:** Position your feet slightly wider than shoulder-width with toes flared **15° to 30° outward**. This aligns your femur with your hip socket, allowing the pelvis to descend smoothly between your thighs.\n"
            "* **The 95° Knee Angle Benchmark:** In Pulse AI's Pose Coach, depth is registered when your hip-knee-ankle angle breaks **< 95°**. This guarantees your hip crease dips below the top of the patella, activating the vastus medialis (VMO) and glute max.\n"
            "* **Eliminating Knee Cave (Valgus Collapse):** Knee cave happens when your adductors overpower weak gluteus medius stabilizers. Cue yourself to **\"rip the floor apart\"** with your feet throughout both descent and ascent.\n"
            "* **Valsalva Intra-Abdominal Brace:** Inhale 360° into your stomach and obliques before breaking at the hips. Keep your torso rigid like a concrete pillar.\n\n"
            "**Coach's Directive:** Open the **AI Pose Coach** tab right now! Our client-side MediaPipe computer vision tracks your joint landmarks at 60 FPS with live audio feedback."
        )
        tips = [
            "Descend on a controlled 3-second negative; never bounce recklessly at the bottom.",
            "Screw your feet into the floor to activate your hip external rotators.",
            "Maintain full tripod foot contact: big toe, pinky toe, and heel anchored."
        ]

    # 5. Bench Press / Chest / Shoulder Preservation
    elif any(w in lower for w in ["bench", "chest", "pec", "scapula", "shoulder", "incline", "pushup", "dip"]):
        reply = (
            "### 🛡️ Bench Press Biomechanics & Shoulder Longevity\n\n"
            "To build an armor-plated chest without tearing up your rotator cuffs, master these kinematic principles:\n\n"
            "* **Scapular Retraction & Depression:** Before un-racking, pinch your shoulder blades together and pull them down toward your back pockets. This creates a stable thoracic shelf and protects your anterior shoulder capsule.\n"
            "* **The 45° to 60° Elbow Tuck:** Avoid flaring your elbows perpendicular at 90°. Flaring compresses the supraspinatus tendon. Tuck your elbows at a **45° to 60° angle** relative to your ribs.\n"
            "* **J-Curve Bar Path:** The bar shouldn't travel straight up and down. Lower it under control to your lower sternum/nipple line, then press upward and slightly backward over your shoulder joints.\n"
            "* **Leg Drive Integration:** Plant your heels firmly, driving backwards into the bench to stabilize your pelvis and thoracic arch."
        )
        tips = [
            "Lock your shoulder blades tight into the bench before taking the bar out.",
            "Stack your wrists vertically above your elbows to avoid wrist joint strain.",
            "Do 3 sets of face-pulls twice a week to maintain anterior-posterior shoulder balance."
        ]

    # 6. Deadlift / Back / Spine / Posture
    elif any(w in lower for w in ["deadlift", "back", "spine", "lumbar", "hinge", "hamstring", "lats", "posture"]):
        reply = (
            "### 🏗️ Deadlift & Posterior Chain: Master the Hip Hinge\n\n"
            "A deadlift is not a squat with a bar in your hands—it is a pure hip hinge designed to build an unbreakable back and posterior chain:\n\n"
            "* **Pull the Slack Out of the Bar:** Never jerk the bar off the floor. Set your grip, wedge your hips into position, and pull up on the barbell until you hear the collar click against the plates. Squeeze your armpits like holding oranges.\n"
            "* **Push the Earth Away:** Initiate the lift by driving your feet through the floor (like a leg press) rather than pulling with your lower back. The bar must graze your shins.\n"
            "* **Neutral Cervical & Lumbar Alignment:** Pick a spot on the floor 6-8 feet ahead of you. Don't crane your neck up at the ceiling or hyperextend your lumbar spine at lockout.\n"
            "* **Glute Engagement at Lockout:** Stand tall by violently squeezing your glutes forward into the bar, not by leaning backward."
        )
        tips = [
            "Keep the barbell in continuous contact with your shins and thighs throughout the pull.",
            "Engage your lats to prevent spinal flexion under heavy working loads.",
            "If lower back fatigue arises, swap to Trap Bar Deadlifts or Romanian Deadlifts (RDLs)."
        ]

    # 7. Gym Splits & Routines
    elif any(w in lower for w in ["split", "routine", "ppl", "push pull legs", "arnold", "upper lower", "workout plan", "frequency"]):
        reply = (
            "### 📊 Hypertrophy Architecture: Optimal Training Splits\n\n"
            "Muscle Protein Synthesis (MPS) stays elevated for approximately 36 to 48 hours following a resistance session. To maximize growth, stimulate each muscle group **twice every 7 to 9 days**:\n\n"
            "* **Push / Pull / Legs (PPL - 6 Days/Week):** Gold standard for intermediate-to-advanced athletes. Groups synergist muscles to eliminate joint overlap.\n"
            "* **Upper / Lower Split (4 Days/Week):** The best split for busy schedules, balanced strength progression, and joint longevity.\n"
            "* **Full Body (3 Days/Week):** Incredible for natural lifters, beginners, and high-frequency neuromuscular efficiency.\n"
            "* **Arnold Split (Chest/Back, Shoulders/Arms, Legs):** Superior for upper body aesthetics and agonizing antagonistic superset pumps.\n\n"
            "**Coach's Directive:** Head to our **Gym & Routines** tab! Enter your fitness score to generate a calibrated split with local Indian gym recommendations."
        )
        tips = [
            "Target 10 to 20 hard working sets per muscle group per week.",
            "Keep your heavy compound movements at 1-2 Reps in Reserve (RIR).",
            "Take a planned deload week every 6-8 weeks to allow tendons and CNS to resensitize."
        ]

    # 8. Supplements (Creatine, Whey, Ashwagandha)
    elif any(w in lower for w in ["creatine", "whey", "supplement", "ashwagandha", "caffeine", "preworkout", "vitamin"]):
        reply = (
            "### 💊 Evidence-Based Ergogenics: The Proven Stack\n\n"
            "Strip away the marketing fluff. Here is what peer-reviewed sports science actually validates:\n\n"
            "* **Creatine Monohydrate (5g/day):** The most researched supplement in human history. Saturates cellular phosphocreatine reserves to boost power output, anaerobic capacity, and intracellular hydration. Take it daily at any time. No loading phase necessary.\n"
            "* **Whey Protein Isolate / Concentrate:** Rapidly digesting complete protein providing ~2.7g leucine per scoop to stimulate muscle protein synthesis.\n"
            "* **Caffeine (3–5 mg/kg):** Take 45 minutes pre-workout to block adenosine receptors, amplify motor unit recruitment, and blunt perceived exertion.\n"
            "* **Ashwagandha (KSM-66, 300-600mg):** Proven in clinical trials to lower serum cortisol, improve sleep quality, and support natural testosterone recovery.\n"
            "* **Electrolytes (Sodium & Potassium):** A pinch of rock salt in your pre-workout water enhances muscular contractions and pumps."
        )
        tips = [
            "Take 5g of creatine monohydrate consistently every single day, with or without workout.",
            "Cut off caffeine consumption at least 8 hours before sleeping to protect REM sleep.",
            "Remember: supplements account for only 5% of results; whole nutrition and hard training drive 95%."
        ]

    # 9. Fat Loss / Cutting / Belly Fat
    elif any(w in lower for w in ["fat loss", "cut", "shred", "belly fat", "weight loss", "calorie deficit", "cardio", "lean"]):
        reply = (
            "### 🔥 Scientific Fat Loss & Metabolic Preservation\n\n"
            "Spot reduction of fat is biologically impossible; fat is mobilized systemically when you sustain an energy deficit while preserving lean muscle mass:\n\n"
            "* **The Moderate Caloric Deficit:** Aim for a 350-500 kcal deficit below your maintenance TDEE. Aggressive crash diets burn valuable muscle tissue and crash your thyroid/metabolism.\n"
            "* **High Protein Shield (2.0–2.2g per kg bodyweight):** In a deficit, protein has the highest thermic effect of food (TEF) and signals your body to burn stored adipose tissue instead of muscle.\n"
            "* **Heavy Resistance Training:** Keep lifting heavy! Lifting signals your body that muscle tissue is essential for survival, forcing it to liberate fat reserves for fuel.\n"
            "* **Daily Step Goal (NEAT):** Non-Exercise Activity Thermogenesis (8,000–12,000 daily steps) burns more total weekly calories than grueling cardio sessions without spiking your appetite."
        )
        tips = [
            "Track daily protein intake first; hitting your protein target prevents muscle wasting in a cut.",
            "Hit 10,000 daily steps consistently to elevate your baseline caloric expenditure.",
            "Weigh yourself daily in the morning after using the restroom and track your weekly average."
        ]

    # 10. Universal High-Intelligence Synthesizer for ANY Question
    else:
        # Dynamically tailor response to user query
        keywords = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', lower) if w not in ["the", "and", "for", "with", "about", "what", "how", "can", "you", "tell"]]
        topic_str = ", ".join(keywords[:3]) if keywords else "your fitness evolution"
        
        reply = (
            f"### 🎯 Pulse AI Tactical Coaching Directive: Focus on {user_msg.strip().capitalize()}\n\n"
            f"Regarding **\"{user_msg}\"**, let us break this down with sports-science rigor and an elite performance mindset:\n\n"
            "* **Kinematic & Biomechanical Integrity:** Every physical adaptation begins with movement efficiency. Ensure your joints move through a full active range of motion under continuous mechanical tension rather than relying on momentum.\n"
            "* **Progressive Overload Blueprint:** Real progress requires demanding more from your physiology week over week. Progress can be adding a rep, increasing load by 1-2%, slowing down your eccentric tempo (3-second negatives), or cutting rest times.\n"
            "* **Nutritional Fueling & Tropical Hydration:** If you are training in India or warm conditions, prioritize 3.5L+ of water with minerals, hit 1.8–2.2g protein per kg of bodyweight, and balance whole food carbohydrates for glycogen replenishment.\n"
            "* **Neuro-Muscular Recovery:** The workout provides the biological stimulus, but your adaptation happens while sleeping and recovering. Give your nervous system 48 hours of recovery between working the same muscle groups.\n\n"
            "**Coach's Directive:** Pulse AI is equipped with specialized tools to assist you:\n"
            "* **AI Pose Coach:** Calibrate real-time squat depth and form with computer vision.\n"
            "* **AI Dietician:** Generate custom Indian vegetarian/non-vegetarian macro blueprints.\n"
            "* **Gym & Routines:** Discover premier Indian gyms and tailor-made workout splits."
        )
        tips = [
            "Log your training numbers so you have measurable data to progressively overload.",
            "Master your form with controlled tempo before increasing the weight on the bar.",
            "Remember that discipline and daily consistency outshine sporadic intensity every time."
        ]

    return ChatResponse(
        reply=reply,
        sentiment_detected=sentiment,
        actionable_tips=tips,
        motivational_quote=quote,
        source="pulse-autonomous-engine"
    )
