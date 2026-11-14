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

COACH_SYSTEM_PROMPT = """You are Pulse AI's Elite Virtual Fitness Coach, Biomechanics Specialist, and Psychological Performance Mentor.
Your mission is to provide world-class, science-backed guidance to athletes and everyday lifters alike.

Core Competencies you must display:
1. Deep Muscle Anatomy & Joint Kinematics: Explain prime movers, synergists, stabilizer muscles, moment arms, and optimal bar paths.
2. Recovery & Supercompensation: Explain central nervous system (CNS) fatigue, systemic vs. local fatigue, optimal rest times between sets (e.g. 2.5-3 min for compounds, 60-90s for hypertrophy isolation), and sleep architecture.
3. Workout Splits: Deeply articulate PPL (Push/Pull/Legs), Upper/Lower, Arnold Split, Full-body, and customize to lifter frequency.
4. Macro Tracking & Metabolism: Detail macronutrient ratios (protein 1.6-2.2g/kg, fats 0.6-1.0g/kg, carbs to fuel glycogen), caloric deficits/surpluses, and nutrient timing.
5. Injury Prevention & Prehab: Pinpoint joint impingements, patellar tendon tracking, rotator cuff warmups, spinal neutral bracing (Valsalva maneuver), and hip mobility.
6. Mood & Sentiment Adaptive Motivation: Actively detect the user's emotional state from their phrasing (e.g., exhausted, discouraged, pumped, anxious, plateaued). Adapt your tone: if tired, offer strategic autoregulation and recovery; if unmotivated, spark discipline over fleeting motivation; if energized, channel that focus into progressive overload.

Formatting Rules:
- Use clean Markdown with bold headings, bullet points, and actionable takeaways.
- Provide practical, immediate next steps.
- Conclude with 3 dynamic, punchy actionable tips.
"""

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = Field(default_factory=list)

class ChatResponse(BaseModel):
    reply: str
    sentiment_detected: Optional[str] = "Motivated"
    actionable_tips: Optional[List[str]] = Field(default_factory=list)
    source: str = "gemini"

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
    user_msg = req.message.strip()
    if not user_msg:
        raise ValueError("Message cannot be empty")

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
                sentiment = "Fatigued / Autoregulation Needed"
            elif any(w in lower for w in ["pain", "hurt", "injured", "tweak", "strain", "click"]):
                sentiment = "Caution / Injury Alert"
            elif any(w in lower for w in ["hyped", "ready", "crush", "pr", "pumped", "let's go"]):
                sentiment = "High Neuromuscular Arousal"
            elif any(w in lower for w in ["lazy", "demotivated", "unmotivated", "can't", "fail"]):
                sentiment = "Seeking Discipline & Activation"

            return ChatResponse(
                reply=reply,
                sentiment_detected=sentiment,
                actionable_tips=[
                    "Hydrate with 500ml water and electrolytes before your set.",
                    "Focus on eccentric control (2-3 seconds down) for peak muscle tension.",
                    "Track every set and target a 1-2% progressive overload week over week."
                ],
                source="gemini"
            )
        except Exception as e:
            print(f"Notice: Falling back to Pulse Autonomous Engine: {e}")

    # Pulse Autonomous Kinesiology & Coaching Engine
    lower = user_msg.lower()
    sentiment = "Performance Mindset"
    if any(w in lower for w in ["tired", "exhausted", "sore", "drained", "sleepy", "burnout", "no energy", "fatigued"]):
        sentiment = "Fatigued / Autoregulation Needed"
    elif any(w in lower for w in ["lazy", "demotivated", "unmotivated", "can't get up", "struggling", "skip", "slack"]):
        sentiment = "Seeking Discipline & Activation"
    elif any(w in lower for w in ["hyped", "pumped", "pr", "crush", "let's go", "ready", "beast", "fire", "unstoppable"]):
        sentiment = "High Neuromuscular Arousal"
    elif any(w in lower for w in ["pain", "hurt", "tweak", "strain", "injured", "ache", "impinge"]):
        sentiment = "Injury Prehab & Joint Care"
    elif any(w in lower for w in ["stress", "anxious", "overwhelmed", "hectic", "pressure", "nervous"]):
        sentiment = "Stress Modulation & CNS Calm"
    elif any(w in lower for w in ["stuck", "plateau", "no progress", "weak", "frustrated", "not growing"]):
        sentiment = "Plateau Breakthrough Strategy"

    tips = [
        "Focus on a controlled 2-3 second eccentric tempo for maximum mechanical tension.",
        "Hydrate with 500ml water and electrolytes 30 minutes before your workout.",
        "Log your working sets and target a 1-2% progressive overload week over week."
    ]

    if any(w in lower for w in ["squat", "knee", "depth", "valgus", "patellar", "vmo", "femur", "quad", "hack squat"]):
        sentiment = "Squat Biomechanics & Kinematics" if "Performance" in sentiment else sentiment
        reply = (
            "### 🏋️ Form Masterclass: Squat Kinematics & Depth Optimization\n\n"
            "Squats are the gold-standard closed-kinetic-chain movement for lower body hypertrophy. Achieving clean, injury-free depth requires understanding your hip and ankle anatomy:\n\n"
            "* **Acetabular Hip Clearance:** Set stance slightly wider than shoulder-width with toes flared **15° to 30° outward**. This matches your femur's angle to your acetabular hip socket, allowing your pelvis to descend freely between your femurs without femoroacetabular impingement.\n"
            "* **The 95° Knee Angle Threshold:** In Pulse AI's Pose Coach, the depth benchmark is breaking a knee angle **< 95°**. This guarantees your inguinal hip crease dips lower than the top of your patella, maximizing recruitment of the vastus medialis oblique (VMO) and gluteus maximus.\n"
            "* **Preventing Valgus Collapse (Knees Caving):** Knee cave occurs when the adductor magnus overpowers a weak gluteus medius or when ankle dorsiflexion is restricted. Cue yourself to **\"spread the floor apart\"** with your feet to engage the hip external rotators.\n"
            "* **Intra-Abdominal Bracing (Valsalva):** Inhale deeply into your lower abdomen (not your chest) and expand your obliques 360° against your core before initiating the eccentric descent.\n\n"
            "**Coach's Directive:** Switch over to our **AI Pose Coach** tab! It uses computer vision to track your left hip, knee, and ankle angles in real time at 60 FPS with immediate audio depth cues."
        )
        tips = [
            "Descend with a steady 3-second eccentric tempo; avoid bouncing at the bottom.",
            "Actively drive your knees outward in line with your second toe throughout the ascent.",
            "Keep your tripod foot contact (heel, big toe, pinky toe) glued to the floor."
        ]
    elif any(w in lower for w in ["bench", "chest", "pec", "scapula", "rotator cuff", "incline", "pushup", "fly"]):
        sentiment = "Pectoral Mechanics & Shoulder Preservation" if "Performance" in sentiment else sentiment
        reply = (
            "### 🛡️ Bench Press Biomechanics & Shoulder Preservation\n\n"
            "The barbell bench press produces massive pectoral mechanical tension, but incorrect shoulder mechanics can place high shear stress on the anterior capsule:\n\n"
            "* **Scapular Retraction & Depression:** Before un-racking, pinch your shoulder blades back and down \"into your back pockets.\" Maintain this tightness through every rep so your ribcage creates a stable base and protects the rotator cuff.\n"
            "* **Elbow Flare Angle:** Never flare your elbows perpendicular to your torso at 90°. Tuck your elbows to a **45° to 60° angle** relative to your ribs. A 90° flare compresses the supraspinatus tendon beneath the acromion process.\n"
            "* **The Natural J-Curve Bar Path:** Touch the bar lightly at your lower sternum/nipple line, then press upward and slightly back toward your eyes so the bar finishes directly stacked above your shoulder joints.\n"
            "* **Leg Drive Integration:** Plant your heels firmly on the floor and drive backward into the bench. This transfers ground reaction force across your thoracic spine to lock your stability.\n\n"
            "**Coach's Directive:** Pair heavy pressing with 3 sets of cable face pulls or band pull-aparts twice weekly to keep your rotator cuff healthy and preserve joint balance."
        )
        tips = [
            "Retract and depress your scapulae before lifting the barbell off the rack.",
            "Keep wrists stacked vertically directly over your elbows to avoid wrist hyperextension.",
            "Lower the bar with a 2-second eccentric cadence, pausing briefly on the chest."
        ]
    elif any(w in lower for w in ["deadlift", "hinge", "lumbar", "back pain", "spine", "hamstring", "glute", "rdl"]):
        sentiment = "Posterior Chain & Spinal Alignment" if "Performance" in sentiment else sentiment
        reply = (
            "### 🏗️ Deadlift Kinematics: Hip Hinging & Spinal Neutrality\n\n"
            "The deadlift is a pure hip hinge, not a squat with a bar in your hands. Mastering the starting position eliminates lower back strain:\n\n"
            "* **Wedge and Pull the Slack:** Do not jerk the bar off the floor. Grip the bar, pull your hips down and forward, and pull up until you hear the barbell \"click\" against the plates. Your lats should feel like you are squeezing oranges in your armpits.\n"
            "* **Push the Floor Away:** Think of the initial pull as a leg press against the ground rather than pulling with your arms or lower back. The barbell should stay in continuous contact with your shins.\n"
            "* **Neutral Cervical & Lumbar Spine:** Keep your eyes focused 6–8 feet in front of you on the ground. Avoid cranking your neck up or hyperextending your lumbar spine at the top lockout.\n"
            "* **Romanian Deadlifts (RDLs) for Hypertrophy:** Initiate by pushing your hips straight back toward the wall behind you with soft knees until you feel a deep hamstring stretch, then drive hips forward.\n\n"
            "**Coach's Directive:** If you experience lower back fatigue, swap conventional pulls for trap bar deadlifts or RDLs to reduce shear forces on the lumbar spine."
        )
        tips = [
            "Lock your lats tightly before the barbell leaves the floor.",
            "Keep the bar path completely vertical and dragging against your shins.",
            "Squeeze your glutes to finish the lockout without hyperextending your lower back."
        ]
    elif any(w in lower for w in ["creatine", "supplement", "caffeine", "preworkout", "whey", "bcaa", "glutamine"]):
        sentiment = "Supplement Science & Efficacy" if "Performance" in sentiment else sentiment
        reply = (
            "### 💊 Evidence-Based Supplementation: What Actually Works\n\n"
            "90% of sports supplements are marketing hype. Here is the peer-reviewed evidence on what moves the needle:\n\n"
            "* **Creatine Monohydrate (Tier 1 - Essential):** The most researched ergogenic aid in history. Take **3g to 5g daily** at any time of day. It saturates phosphocreatine stores, increasing cellular hydration, power output, and lean mass over time. No loading phase or cycling required.\n"
            "* **Caffeine Anhydrous (Tier 1 - Acute Performance):** Ingest **3–5 mg/kg** of bodyweight 45–60 minutes pre-workout. Blocks adenosine receptors in the brain to reduce perceived exertion and enhance motor unit recruitment. Avoid within 6–8 hours of bedtime.\n"
            "* **Whey / Plant Protein Isolate (Tier 1 - Convenience):** Convenient, high-bioavailability protein source to help hit your daily protein targets without excess fats or carbs.\n"
            "* **Electrolytes (Sodium, Potassium, Magnesium):** A pinch of sodium (300-500mg) in your pre-workout water enhances muscular pump and prevents cramping during heavy sessions.\n"
            "* **BCAAs vs EAAs:** If your daily protein intake is sufficient, isolated BCAAs are unnecessary. Whole protein or essential amino acids (EAAs) are vastly superior."
        )
        tips = [
            "Take 5g of creatine monohydrate daily with water or your post-workout meal.",
            "Cut off caffeine intake at least 8 hours before sleeping to protect sleep architecture.",
            "Rely on whole nutrient-dense foods for 80%+ of your daily micronutrients."
        ]
    elif any(w in lower for w in ["split", "ppl", "push pull legs", "arnold", "upper lower", "bro split", "full body", "routine"]):
        sentiment = "Training Architecture & Split Design" if "Performance" in sentiment else sentiment
        reply = (
            "### 📊 Master Programming: Workout Splits & Frequency Science\n\n"
            "Muscle protein synthesis remains elevated for approximately 36 to 48 hours post-workout. To maximize hypertrophy, each muscle group should be stimulated **twice every 7 to 9 days**:\n\n"
            "* **Push / Pull / Legs (PPL - 6 Days/Week):** The gold standard for intermediate and advanced lifters. Organizes exercises by movement pattern to prevent overlapping joint fatigue.\n"
            "* **Upper / Lower Split (4 Days/Week):** Best for balanced strength and hypertrophy. Allows 72 hours of complete recovery between upper sessions, ideal for heavy progressive overload.\n"
            "* **Full Body (3 Days/Week):** Superb for foundation building, busy schedules, and maximum systemic motor unit recruitment with high neurological recovery.\n"
            "* **Arnold Split (Chest/Back, Shoulders/Arms, Legs):** Exceptional for upper-body prioritization and intense antagonistic superset pumps.\n\n"
            "**Coach's Directive:** Open our **Gym & Routines** tab! Enter your current fitness score (1–100) and city to generate a calibrated split with tailored daily challenges."
        )
        tips = [
            "Target 10 to 20 hard working sets per muscle group per week.",
            "Keep compound movements between 1–2 Reps in Reserve (RIR) to preserve the nervous system.",
            "Schedule a planned deload every 6 to 8 weeks where volume is halved."
        ]
    elif any(w in lower for w in ["macro", "protein", "carb", "calorie", "bulk", "diet", "leucine", "deficit", "surplus"]):
        sentiment = "Metabolic Precision & Macronutrients" if "Performance" in sentiment else sentiment
        reply = (
            "### 🥗 Precision Nutrition: Macronutrient Engineering & Energy Balance\n\n"
            "Body recomposition is governed by thermodynamics, nitrogen balance, and nutrient timing:\n\n"
            "* **Protein Calibration:** Consume **1.8g to 2.2g of protein per kg of bodyweight** (0.8–1.0g/lb). Divide into 3–5 meals spaced 3–4 hours apart, ensuring each meal provides at least **3g of leucine** to trigger the mTOR pathway.\n"
            "* **Carbohydrate Partitioning:** Carbohydrates are protein-sparing and replenish intramuscular glycogen stores. Consume 40–50% of your daily carbs in the peri-workout window (pre- and post-training).\n"
            "* **Essential Fats:** Never drop below **0.6g/kg** of bodyweight. Dietary fats are essential precursors for testosterone, cortisol regulation, and cell membrane fluidity.\n"
            "* **Energy Balance:**\n"
            "  * **Lean Bulk:** +250 to +350 kcal/day above maintenance (~1-1.5% bodyweight gain per month).\n"
            "  * **Fat Loss / Shred:** -400 to -500 kcal/day deficit while keeping protein high to prevent catabolism.\n\n"
            "**Coach's Directive:** Visit our **AI Dietician** tab! Input your weight, height, and goal to get an automated macro breakdown and a custom 5-item grocery list."
        )
        tips = [
            "Prioritize high-leucine complete protein sources like eggs, chicken, fish, whey, or tofu/tempeh.",
            "Drink at least 35-40ml of water per kg of bodyweight daily.",
            "Weigh yourself every morning under identical conditions and track the 7-day rolling average."
        ]
    elif any(w in lower for w in ["bicep", "tricep", "arm", "curl", "pushdown", "dip", "forearm"]):
        sentiment = "Arm Hypertrophy & Joint Angles" if "Performance" in sentiment else sentiment
        reply = (
            "### 💪 Arm Hypertrophy: Muscle Head Isolation & Moment Arms\n\n"
            "Building impressive arms requires targeting specific muscle heads through varied joint angles:\n\n"
            "* **Triceps (60% of Upper Arm Mass):**\n"
            "  * **Long Head:** Crosses the shoulder joint. It is only fully stretched when your arms are elevated overhead (e.g., Overhead Cable Extensions, French Press).\n"
            "  * **Lateral & Medial Heads:** Highly active during standard pushdowns, dips, and close-grip bench press.\n"
            "* **Biceps (Two Heads + Brachialis):**\n"
            "  * **Long Head (Outer Peak):** Best stimulated when elbows are behind the torso (e.g., Incline Dumbbell Curls).\n"
            "  * **Short Head (Inner Thickness):** Best stimulated when elbows are in front of the torso (e.g., Preacher Curls).\n"
            "  * **Brachialis:** Lies beneath the biceps. Developing it pushes the biceps upward, adding width. Hammer curls target the brachialis.\n\n"
            "**Coach's Directive:** Treat arms with the same progressive overload rigor as squats and bench. Use controlled 2-second negatives and avoid swinging your shoulders."
        )
        tips = [
            "Include at least one overhead triceps extension movement to target the long head.",
            "Perform hammer curls with neutral grip to build the underlying brachialis.",
            "Lock your upper arms in place; do not let your front deltoids take over the curl."
        ]
    elif any(w in lower for w in ["tired", "exhausted", "burnout", "drained"]):
        sentiment = "Fatigued / Autoregulation Needed"
        reply = (
            "### 🧘 Strategic Autoregulation: Respect the Central Nervous System\n\n"
            "Fatigue is biological biofeedback. Champions manage fatigue through intelligent autoregulation:\n\n"
            "* **Autoregulate with RPE:** Drop working loads by 10–15% and cap all sets at **RPE 7** (leaving 3 solid reps in reserve).\n"
            "* **The 20-Minute Blood-Flow Routine:** Do 15 minutes of low-intensity incline walking followed by light mobility work.\n"
            "* **Cellular Rehydration:** Down 500ml cold water with a pinch of sea salt to prevent power loss.\n"
            "* **Prioritize Sleep:** Tonight, get to bed 45 minutes earlier to maximize growth hormone pulses.\n\n"
            "**Coach's Directive:** The athlete who knows when to pull back avoids plateaus and injuries."
        )
        tips = [
            "Drop weight by 10-15% and focus on crisp form when tired.",
            "Drink 500ml of water with electrolytes before stepping onto the gym floor.",
            "Aim for an extra 45 minutes of sleep tonight to accelerate central nervous recovery."
        ]
    elif any(w in lower for w in ["lazy", "demotivated", "skip", "can't get up", "struggling"]):
        sentiment = "Seeking Discipline & Activation"
        reply = (
            "### ⚡ Overcoming the Friction Point: Action Precedes Motivation\n\n"
            "Motivation is an emotion—it is unreliable and disappears when work is demanding. Real progress is built on **automated discipline**:\n\n"
            "* **The 5-Minute Commitment Rule:** Tell yourself: *\"I am only going to do the dynamic warm-up and hit one warm-up set.\"* 95% of resistance is crossing the threshold.\n"
            "* **Action Precedes Motivation:** Dopamine is released in response to forward progress, not while waiting on the couch. Move the body, and the mind will follow.\n"
            "* **Identity-Based Training:** You are an athlete who executes regardless of mood.\n\n"
            "**Coach's Directive:** Lace up your shoes right now. Open our **AI Pose Coach** tab, turn on your camera, and knock out 10 bodyweight squats!"
        )
        tips = [
            "Apply the 5-minute rule: start your warm-up and let momentum carry you.",
            "Put on your training shoes immediately to reduce cognitive friction.",
            "Focus on the feeling of accomplishment you will have once the session is completed."
        ]
    else:
        sentiment = "Pulse Master Coach"
        reply = (
            f"### 🎯 Pulse AI Master Coaching Assessment\n\n"
            f"Regarding **\"{user_msg}\"**:\n\n"
            "* **Biomechanical & Movement Efficiency:** Always prioritize joint alignment and mechanical tension over arbitrary poundages. Lifting with full active range of motion stimulates significantly greater hypertrophy than partial reps.\n"
            "* **Progressive Overload Principle:** Progression is achieved by adding 1-2 reps, increasing load by 1-2%, or slowing down your eccentric tempo to increase time under tension.\n"
            "* **Metabolic Recovery & Fueling:** Training provides the stimulus, but recovery delivers the adaptation. Ensure you hit your daily protein targets (1.8–2.2g/kg), maintain adequate hydration, and prioritize 7.5+ hours of sleep.\n\n"
            "**Coach's Directive:** Explore Pulse AI's core toolset!\n"
            "* Verify your squat form on **AI Pose Coach**\n"
            "* Calibrate your macros and meals on **AI Dietician**\n"
            "* Customize your training split on **Gym & Routines**"
        )

    return ChatResponse(
        reply=reply,
        sentiment_detected=sentiment,
        actionable_tips=tips,
        source="pulse-engine"
    )
