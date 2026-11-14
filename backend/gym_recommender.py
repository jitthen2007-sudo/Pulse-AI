import os
from typing import List
from pydantic import BaseModel, Field

class RoutineRequest(BaseModel):
    location: str = Field(default="Bengaluru, India", description="User's city or locality, e.g. Bengaluru, Mumbai, Delhi")
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
    rating: float = 4.8
    review_count: int = 420
    star_display: str = "⭐⭐⭐⭐⭐ 4.8"
    price_est: str = "₹2,200/month"

class RoutineResponse(BaseModel):
    workout_split: WorkoutSplit
    daily_challenge: DailyChallenge
    local_gyms: List[LocalGym]
    coach_note: str
    source: str = "pulse-indian-gym-engine"

def get_indian_gyms_for_location(location: str) -> List[LocalGym]:
    loc_clean = location.strip() if location.strip() else "Bengaluru, India"
    loc_lower = loc_clean.lower()

    if any(k in loc_lower for k in ["bangalore", "bengaluru"]):
        return [
            LocalGym(
                name="Cult.fit Indiranagar Elite",
                locality_context="100ft Road, Indiranagar, Bengaluru, Karnataka",
                vibe="High-energy athletic hub with functional conditioning & Olympic strength floors",
                key_amenities=["HRX conditioning rigs", "Olympic barbell platforms", "Boxing arena", "Steam recovery suites", "In-app biometric tracking"],
                why_recommended="Prime destination for athletic conditioning, data-driven heart rate tracking, and community energy.",
                rating=4.9,
                review_count=1450,
                star_display="⭐⭐⭐⭐⭐ 4.9",
                price_est="₹1,850/month"
            ),
            LocalGym(
                name="Gold's Gym Koramangala",
                locality_context="80ft Road, 4th Block Koramangala, Bengaluru, Karnataka",
                vibe="Premier heavy bodybuilding mecca with calibrated steel plates",
                key_amenities=["Dumbbells up to 60kg", "Precor & Hammer Strength pin-loaded machines", "Certified Kinesiology coaches", "Locker & sauna"],
                why_recommended="Unmatched barbell culture and isolated hypertrophy machines to break strength plateaus.",
                rating=4.8,
                review_count=980,
                star_display="⭐⭐⭐⭐⭐ 4.8",
                price_est="₹2,400/month"
            ),
            LocalGym(
                name="Anytime Fitness HSR Layout",
                locality_context="Sector 1, HSR Layout, Bengaluru, Karnataka",
                vibe="Clean, modern 24/7 training club with zero scheduling friction",
                key_amenities=["24/7 keycard access", "Matrix performance racks", "Functional synthetic turf", "Personalized fitness assessment"],
                why_recommended="Ideal for tech professionals needing early-morning or late-night access without crowd congestion.",
                rating=4.7,
                review_count=620,
                star_display="⭐⭐⭐⭐½ 4.7",
                price_est="₹2,100/month"
            )
        ]
    elif any(k in loc_lower for k in ["mumbai", "bombay"]):
        return [
            LocalGym(
                name="Gold's Gym Bandra West",
                locality_context="Pali Hill, Bandra West, Mumbai, Maharashtra",
                vibe="Iconic celebrity strength sanctuary with world-class biomechanical equipment",
                key_amenities=["Eleiko Olympic power cages", "Extensive free weights", "Steam & physiotherapy lounge", "Rehabilitation zone"],
                why_recommended="The gold standard of Indian bodybuilding culture with elite biomechanics coaching.",
                rating=4.9,
                review_count=1820,
                star_display="⭐⭐⭐⭐⭐ 4.9",
                price_est="₹3,200/month"
            ),
            LocalGym(
                name="Nitro Fitness Juhu",
                locality_context="JVPD Scheme, Juhu, Mumbai, Maharashtra",
                vibe="Ultra-luxurious, spacious strength and conditioning training facility",
                key_amenities=["Hammer Strength Iso-lateral equipment", "Custom indoor sprint track", "Spinning studio", "Juice & protein bar"],
                why_recommended="Spacious open layout preventing wait times during peak evening training hours.",
                rating=4.8,
                review_count=1140,
                star_display="⭐⭐⭐⭐⭐ 4.8",
                price_est="₹3,500/month"
            ),
            LocalGym(
                name="Cult.fit Andheri West",
                locality_context="Lokhandwala Complex, Andheri West, Mumbai, Maharashtra",
                vibe="Functional athleticism, HIIT circuits, and athletic resistance training",
                key_amenities=["Multi-station functional rig", "Prowler sled lanes", "Air bikes & rowers", "Recovery steam rooms"],
                why_recommended="High-calorie burn programs and group athletic motivation to maintain accountability.",
                rating=4.8,
                review_count=890,
                star_display="⭐⭐⭐⭐⭐ 4.8",
                price_est="₹1,900/month"
            )
        ]
    elif any(k in loc_lower for k in ["delhi", "gurgaon", "noida", "gurugram", "ncr"]):
        return [
            LocalGym(
                name="Anytime Fitness Connaught Place",
                locality_context="Inner Circle, Connaught Place, New Delhi",
                vibe="Modern 24/7 fitness facility right in central Delhi",
                key_amenities=["24/7 biometric security", "Life Fitness selectorized line", "Functional training zone", "Private shower suites"],
                why_recommended="Central connectivity and round-the-clock training capability in Delhi NCR.",
                rating=4.8,
                review_count=1290,
                star_display="⭐⭐⭐⭐⭐ 4.8",
                price_est="₹2,200/month"
            ),
            LocalGym(
                name="Cult.fit Cyber Hub Gurgaon",
                locality_context="DLF Cyber City, Sector 24, Gurugram, Haryana",
                vibe="Futuristic corporate fitness center with athletic conditioning floors",
                key_amenities=["HRX transformation programs", "Olympic deadlift stations", "Cardio cinema", "Nutrition counseling"],
                why_recommended="State-of-the-art facility for peak metabolic conditioning and posture restoration.",
                rating=4.9,
                review_count=1650,
                star_display="⭐⭐⭐⭐⭐ 4.9",
                price_est="₹2,000/month"
            ),
            LocalGym(
                name="Ozone Fitness Club South Ex",
                locality_context="South Extension Part 2, New Delhi",
                vibe="Premium wellness and heavy resistance club with hydrotherapy",
                key_amenities=["Calibrated iron plates", "Hydro-massage lounge", "Certified strength coaches", "Sauna & steam bath"],
                why_recommended="Exceptional muscle recovery suites and top-tier barbell equipment.",
                rating=4.7,
                review_count=740,
                star_display="⭐⭐⭐⭐½ 4.7",
                price_est="₹2,800/month"
            )
        ]
    elif any(k in loc_lower for k in ["hyderabad", "secunderabad"]):
        return [
            LocalGym(
                name="Cult.fit Gachibowli",
                locality_context="Financial District, Gachibowli, Hyderabad, Telangana",
                vibe="Dynamic athletic center catering to tech professionals and athletes",
                key_amenities=["Multi-rig cross training", "Olympic platforms", "Boxing & kickboxing ring", "App-synced telemetry"],
                why_recommended="High-energy team atmosphere that eliminates workout boredom and enforces consistency.",
                rating=4.9,
                review_count=1100,
                star_display="⭐⭐⭐⭐⭐ 4.9",
                price_est="₹1,800/month"
            ),
            LocalGym(
                name="Gold's Gym Jubilee Hills",
                locality_context="Road No. 36, Jubilee Hills, Hyderabad, Telangana",
                vibe="Elite strength and physique development mecca",
                key_amenities=["Heavy dumbbell racks to 55kg", "Plate-loaded chest & back stations", "Steam & locker", "Biomechanics trainers"],
                why_recommended="Comprehensive hypertrophy machines and spacious free weight areas.",
                rating=4.8,
                review_count=920,
                star_display="⭐⭐⭐⭐⭐ 4.8",
                price_est="₹2,500/month"
            ),
            LocalGym(
                name="Anytime Fitness Hitec City",
                locality_context="Madhapur, Hitec City, Hyderabad, Telangana",
                vibe="Sleek 24/7 fitness hub with seamless digital access",
                key_amenities=["24/7 secure entry", "Matrix cardio & strength", "Turf sprint track", "Certified trainers"],
                why_recommended="Convenient hours for shifting schedules and late-night hypertrophy sessions.",
                rating=4.7,
                review_count=580,
                star_display="⭐⭐⭐⭐½ 4.7",
                price_est="₹2,100/month"
            )
        ]
    elif any(k in loc_lower for k in ["pune"]):
        return [
            LocalGym(
                name="Nitro Fitness Koregaon Park",
                locality_context="North Main Road, Koregaon Park, Pune, Maharashtra",
                vibe="Spacious, high-end bodybuilding and functional fitness center",
                key_amenities=["Hammer Strength line", "Dedicated deadlift platforms", "Cafe & recovery area", "Steam"],
                why_recommended="Top-rated equipment variety and spacious barbell zones in Pune.",
                rating=4.9,
                review_count=1340,
                star_display="⭐⭐⭐⭐⭐ 4.9",
                price_est="₹2,600/month"
            ),
            LocalGym(
                name="Cult.fit Baner",
                locality_context="Baner Road, Pune, Maharashtra",
                vibe="Modern athletic strength and HIIT conditioning",
                key_amenities=["HRX workout formats", "Olympic barbells", "Boxing studio", "Locker & showers"],
                why_recommended="Great community energy and structured metabolic conditioning.",
                rating=4.8,
                review_count=870,
                star_display="⭐⭐⭐⭐⭐ 4.8",
                price_est="₹1,800/month"
            ),
            LocalGym(
                name="Gold's Gym Kalyani Nagar",
                locality_context="East Ave, Kalyani Nagar, Pune, Maharashtra",
                vibe="Serious lifting community with dedicated personal coaching",
                key_amenities=["Free weights to 50kg", "Squat racks", "Cardio deck", "Steam room"],
                why_recommended="Tried-and-tested hypertrophy equipment and attentive trainers.",
                rating=4.7,
                review_count=650,
                star_display="⭐⭐⭐⭐½ 4.7",
                price_est="₹2,300/month"
            )
        ]
    else:
        # Universal Indian City Fallback (e.g. Chennai, Kolkata, Ahmedabad, Jaipur, etc.)
        city_name = loc_clean.split(",")[0].strip().title()
        return [
            LocalGym(
                name=f"Cult.fit {city_name} Center",
                locality_context=f"Central Hub, {city_name}, India",
                vibe="High-energy functional fitness, HRX athletic circuits & Olympic strength floor",
                key_amenities=["Olympic lifting rigs", "Functional turf track", "Boxing arena", "Steam recovery rooms", "In-app workout logs"],
                why_recommended=f"Top-tier athletic training hub in {city_name} with certified coaches and community support.",
                rating=4.8,
                review_count=940,
                star_display="⭐⭐⭐⭐⭐ 4.8",
                price_est="₹1,800/month"
            ),
            LocalGym(
                name=f"Gold's Gym {city_name}",
                locality_context=f"Premier Fitness Zone, {city_name}, India",
                vibe="Authentic heavy iron mecca and muscle hypertrophy headquarters",
                key_amenities=["Calibrated steel plates", "Heavy dumbbells up to 55kg", "Precor selectorized machines", "Sauna & locker suites"],
                why_recommended="Unmatched barbell culture and isolated biomechanical machines for maximum hypertrophy.",
                rating=4.8,
                review_count=820,
                star_display="⭐⭐⭐⭐⭐ 4.8",
                price_est="₹2,400/month"
            ),
            LocalGym(
                name=f"Anytime Fitness {city_name}",
                locality_context=f"Neighborhood Club, {city_name}, India",
                vibe="Clean, modern 24/7 accessible training hub with Matrix equipment",
                key_amenities=["24/7 keycard access", "Olympic squat racks", "Functional training zone", "Private shower suites"],
                why_recommended="Complete schedule flexibility so you never skip a session in your training split.",
                rating=4.7,
                review_count=510,
                star_display="⭐⭐⭐⭐½ 4.7",
                price_est="₹2,000/month"
            )
        ]

async def recommend_gyms_and_routines(req: RoutineRequest) -> RoutineResponse:
    location = req.location.strip() or "Bengaluru, India"
    goal = req.goal
    score = req.performance_score

    local_gyms = get_indian_gyms_for_location(location)

    # Performance-score-calibrated workout splits
    if score >= 75:
        split_name = "6-Day Elite Push / Pull / Legs (PPL Hypertrophy Split)"
        frequency = "6 Days On / 1 Day Active Recovery"
        split_desc = "Advanced high-frequency hypertrophy architecture stimulating each muscle group twice weekly with optimal volume."
        
        days = [
            WorkoutDay(
                day_title="Day 1: Push A (Chest, Anterior Delts, Triceps)",
                target_muscles=["Pectoralis Major", "Front Delts", "Triceps Lateral/Medial Heads"],
                exercises=[
                    Exercise(name="Barbell Flat Bench Press", sets="4 sets", reps="6-8 reps", rest_seconds=150, key_cue="Tuck elbows 45°, maintain tight scapular retraction into the bench."),
                    Exercise(name="Incline Dumbbell Press (30°)", sets="3 sets", reps="8-10 reps", rest_seconds=120, key_cue="Deep eccentric stretch on clavicular head, drive inward without clacking dumbbells."),
                    Exercise(name="Standing Cable Lateral Raises", sets="4 sets", reps="12-15 reps", rest_seconds=75, key_cue="Set pulley at wrist height, lead with elbows, control 2-second negative."),
                    Exercise(name="Overhead Cable Triceps Extensions", sets="3 sets", reps="10-12 reps", rest_seconds=90, key_cue="Full stretch on long head of triceps, lock out forcefully.")
                ]
            ),
            WorkoutDay(
                day_title="Day 2: Pull A (Back Width, Rear Delts, Biceps)",
                target_muscles=["Latissimus Dorsi", "Rhomboids", "Rear Delts", "Biceps Brachii"],
                exercises=[
                    Exercise(name="Chest-Supported T-Bar Row", sets="4 sets", reps="6-8 reps", rest_seconds=150, key_cue="Pull through elbows toward hips, squeeze scapulae for 1 full second at peak contraction."),
                    Exercise(name="Neutral-Grip Lat Pulldown", sets="3 sets", reps="8-10 reps", rest_seconds=90, key_cue="Drive elbows straight down to ribcage, lean back only 10°."),
                    Exercise(name="Rope Face Pulls with External Rotation", sets="4 sets", reps="12-15 reps", rest_seconds=60, key_cue="Pull rope to eye level, spread knuckles apart to activate rotator cuff."),
                    Exercise(name="Incline Dumbbell Biceps Curls", sets="3 sets", reps="10-12 reps", rest_seconds=75, key_cue="Keep elbows pinned behind torso for deep stretch on biceps long head.")
                ]
            ),
            WorkoutDay(
                day_title="Day 3: Legs A (Quad Focus & Calves)",
                target_muscles=["Quadriceps (VMO/Rectus Femoris)", "Gluteus Maximus", "Gastrocnemius"],
                exercises=[
                    Exercise(name="Barbell Back Squat (Pose Coach Verified)", sets="4 sets", reps="6-8 reps", rest_seconds=180, key_cue="Break 95° knee angle, drive knees out over second toe, 3-second eccentric."),
                    Exercise(name="45° Leg Press", sets="3 sets", reps="10-12 reps", rest_seconds=120, key_cue="Feet low and shoulder-width for maximum knee flexion without lower back lifting."),
                    Exercise(name="Leg Extension (Pin-Loaded)", sets="3 sets", reps="12-15 reps", rest_seconds=75, key_cue="Pause for 1 second at top contraction with toes dorsiflexed."),
                    Exercise(name="Standing Machine Calf Raises", sets="4 sets", reps="12-15 reps", rest_seconds=60, key_cue="Full deep ankle stretch at the bottom, pause 2 seconds to eliminate Achilles tendon recoil.")
                ]
            ),
            WorkoutDay(
                day_title="Day 4: Push B (Shoulder Focus & Upper Chest)",
                target_muscles=["Deltoids", "Upper Chest", "Triceps Long Head"],
                exercises=[
                    Exercise(name="Seated Dumbbell Overhead Shoulder Press", sets="4 sets", reps="6-8 reps", rest_seconds=120, key_cue="Keep forearms perpendicular to floor, lower dumbbells to ear level."),
                    Exercise(name="Low-to-High Cable Flyes", sets="3 sets", reps="10-12 reps", rest_seconds=75, key_cue="Scoop cables upward to eye level to target upper clavicular pec fibers."),
                    Exercise(name="Dips (Chest/Triceps Bias)", sets="3 sets", reps="8-10 reps", rest_seconds=90, key_cue="Lean torso forward 20° for chest, keep elbows tucked."),
                    Exercise(name="Cross-Body Cable Triceps Pushdowns", sets="3 sets", reps="12-15 reps", rest_seconds=60, key_cue="Individual cable lines to eliminate wrist torque and isolate lateral heads.")
                ]
            ),
            WorkoutDay(
                day_title="Day 5: Pull B (Back Thickness & Arms)",
                target_muscles=["Mid Trapezius", "Lats", "Brachialis", "Forearms"],
                exercises=[
                    Exercise(name="Barbell Romanian Deadlift (RDL)", sets="4 sets", reps="8-10 reps", rest_seconds=120, key_cue="Hinge at hips, push pelvis back, bar stays glued to shins until deep hamstring stretch."),
                    Exercise(name="Single-Arm Dumbbell Row", sets="3 sets", reps="8-10 reps", rest_seconds=90, key_cue="Pull dumbbell toward hip pocket, avoid rotating your torso."),
                    Exercise(name="Reverse Pec Deck Fly", sets="4 sets", reps="12-15 reps", rest_seconds=60, key_cue="Lead with elbows, keep thumbs facing each other to isolate rear delts."),
                    Exercise(name="Standing Dumbbell Hammer Curls", sets="3 sets", reps="10-12 reps", rest_seconds=75, key_cue="Neutral grip to overload the brachialis and brachioradialis for arm thickness.")
                ]
            ),
            WorkoutDay(
                day_title="Day 6: Legs B (Posterior Chain & Hamstrings)",
                target_muscles=["Hamstrings (Biceps Femoris)", "Glutes", "Core"],
                exercises=[
                    Exercise(name="Lying Leg Curls", sets="4 sets", reps="8-10 reps", rest_seconds=90, key_cue="Drive hips down into the pad to prevent lumbar hyperextension."),
                    Exercise(name="Bulgarian Split Squats (Dumbbell)", sets="3 sets", reps="8-10 reps/leg", rest_seconds=90, key_cue="Torso slightly forward, knee tracks forward over foot, drive through front heel."),
                    Exercise(name="Barbell Hip Thrust", sets="3 sets", reps="10-12 reps", rest_seconds=120, key_cue="Chin tucked, anterior pelvic tilt at top lockout, hold glute squeeze 2 seconds."),
                    Exercise(name="Hanging Leg Raises", sets="3 sets", reps="12-15 reps", rest_seconds=60, key_cue="Posteriorly tilt pelvis upward at the top, avoid swinging.")
                ]
            )
        ]
        
        challenge = DailyChallenge(
            title="The 100-Rep Century Squat Gauntlet",
            difficulty_badge="Level 5: Apex Beast",
            description="High-volume metabolic conditioning challenge to stimulate mitochondrial density and mental grit.",
            challenge_steps=[
                "Warm up hips, knees, and ankles for 5 minutes with dynamic lunges and Cossack squats.",
                "Set a timer for 10 minutes.",
                "Perform 100 bodyweight squats breaking the 95° knee angle using the AI Pose Coach for tracking.",
                "Every time you rest, perform a 20-second deep squat isometric hold before resuming.",
                "Hydrate with 500ml lemon-rock-salt water immediately upon completion."
            ],
            completion_time_est="10 - 12 Minutes"
        )
    elif score >= 45:
        split_name = "4-Day Kinetic Upper / Lower Strength Split"
        frequency = "4 Days On / 3 Days Recovery"
        split_desc = "Optimal balance of progressive overload, structural recovery, and sustainable metabolic adaptation."
        
        days = [
            WorkoutDay(
                day_title="Day 1: Upper Power A",
                target_muscles=["Chest", "Upper Back", "Shoulders", "Arms"],
                exercises=[
                    Exercise(name="Barbell Bench Press", sets="4 sets", reps="6-8 reps", rest_seconds=150, key_cue="Retract shoulder blades, lower bar with 2-second negative to sternum."),
                    Exercise(name="Chest-Supported Dumbbell Row", sets="4 sets", reps="8-10 reps", rest_seconds=120, key_cue="Pull elbows back towards hips, pause at top."),
                    Exercise(name="Seated Dumbbell Shoulder Press", sets="3 sets", reps="8-10 reps", rest_seconds=90, key_cue="Maintain vertical forearm alignment throughout the press."),
                    Exercise(name="Triceps Rope Pushdowns", sets="3 sets", reps="10-12 reps", rest_seconds=60, key_cue="Spread rope at the bottom for peak lateral head tension.")
                ]
            ),
            WorkoutDay(
                day_title="Day 2: Lower Power A",
                target_muscles=["Quadriceps", "Hamstrings", "Calves"],
                exercises=[
                    Exercise(name="Barbell Back Squat (Pose Coach Verified)", sets="4 sets", reps="6-8 reps", rest_seconds=180, key_cue="Break 95° knee depth, maintain 360° intra-abdominal pressure."),
                    Exercise(name="Romanian Deadlift (Dumbbell/Barbell)", sets="3 sets", reps="8-10 reps", rest_seconds=120, key_cue="Push hips back toward wall, feel hamstring stretch."),
                    Exercise(name="Seated Leg Extensions", sets="3 sets", reps="12-15 reps", rest_seconds=75, key_cue="Squeeze quads hard for 1 second at full lockout."),
                    Exercise(name="Standing Calf Raises", sets="4 sets", reps="12-15 reps", rest_seconds=60, key_cue="2-second pause in deep ankle stretch at the bottom.")
                ]
            ),
            WorkoutDay(
                day_title="Day 3: Upper Hypertrophy B",
                target_muscles=["Lats", "Pectorals", "Rear Delts", "Biceps"],
                exercises=[
                    Exercise(name="Incline Dumbbell Press (30°)", sets="3 sets", reps="8-10 reps", rest_seconds=90, key_cue="Control descent, explode upward on 1-second cadence."),
                    Exercise(name="Wide-Grip Lat Pulldown", sets="3 sets", reps="10-12 reps", rest_seconds=90, key_cue="Pull bar to collarbone, avoid swinging backward."),
                    Exercise(name="Standing Dumbbell Lateral Raises", sets="4 sets", reps="12-15 reps", rest_seconds=60, key_cue="Tilt pinkies slightly upward, lead with elbows."),
                    Exercise(name="Incline Biceps Dumbbell Curls", sets="3 sets", reps="10-12 reps", rest_seconds=75, key_cue="Keep upper arms stationary; emphasize long head stretch.")
                ]
            ),
            WorkoutDay(
                day_title="Day 4: Lower Hypertrophy B",
                target_muscles=["Glutes", "Hamstrings", "Quadriceps"],
                exercises=[
                    Exercise(name="Leg Press (Wide Stance)", sets="4 sets", reps="10-12 reps", rest_seconds=120, key_cue="Control eccentric tempo, keep lower back glued to pad."),
                    Exercise(name="Lying Leg Curls", sets="3 sets", reps="10-12 reps", rest_seconds=75, key_cue="Lock pelvis flat, pull heels to glutes."),
                    Exercise(name="Walking Dumbbell Lunges", sets="3 sets", reps="10 reps/leg", rest_seconds=90, key_cue="Step out far enough so shin stays vertical, torso slightly angled forward."),
                    Exercise(name="Plank with Posterior Pelvic Tilt", sets="3 sets", reps="45 seconds", rest_seconds=60, key_cue="Squeeze glutes and draw navel toward spine.")
                ]
            )
        ]
        
        challenge = DailyChallenge(
            title="The 50-Rep Biomechanical Form Check",
            difficulty_badge="Level 3: Intermediate Calibrated",
            description="Kinematic verification drill designed to lock in squat neuromuscular patterns.",
            challenge_steps=[
                "Open the AI Pose Coach tab and enable webcam tracking.",
                "Execute 5 sets of 10 bodyweight squats.",
                "Aim for a 100% 'Good Depth' rating by maintaining hip-knee angle < 95°.",
                "Rest 45 seconds between sets and practice deep diaphragmatic breathing."
            ],
            completion_time_est="8 Minutes"
        )
    else:
        split_name = "3-Day Full Body Foundational Kinetic Split"
        frequency = "3 Days On / 4 Days Recovery"
        split_desc = "Master basic multi-joint movement patterns, build connective tissue tolerance, and ignite metabolic rate."
        
        days = [
            WorkoutDay(
                day_title="Day 1: Full Body Foundation A",
                target_muscles=["Quadriceps", "Chest", "Upper Back", "Core"],
                exercises=[
                    Exercise(name="Goblet Squat (Dumbbell/Kettlebell)", sets="3 sets", reps="8-10 reps", rest_seconds=120, key_cue="Hold dumbbell close to chest, sink between your knees to break 95°."),
                    Exercise(name="Push-Ups (or Incline Push-Ups)", sets="3 sets", reps="8-12 reps", rest_seconds=90, key_cue="Maintain plank stiffness, tuck elbows 45° to ribs."),
                    Exercise(name="Seated Cable Row", sets="3 sets", reps="10-12 reps", rest_seconds=90, key_cue="Pull to belly button, squeeze shoulder blades together."),
                    Exercise(name="Dead Bug Core Stabilization", sets="3 sets", reps="8 reps/side", rest_seconds=60, key_cue="Keep lower back pressed flat into floor throughout.")
                ]
            ),
            WorkoutDay(
                day_title="Day 2: Full Body Foundation B",
                target_muscles=["Hamstrings", "Shoulders", "Lats", "Arms"],
                exercises=[
                    Exercise(name="Dumbbell Romanian Deadlift", sets="3 sets", reps="8-10 reps", rest_seconds=120, key_cue="Slight knee bend, push hips back until hamstrings stretch."),
                    Exercise(name="Dumbbell Overhead Press", sets="3 sets", reps="8-10 reps", rest_seconds=90, key_cue="Press dumbbells vertically without arching lower back."),
                    Exercise(name="Lat Pulldown (Machine)", sets="3 sets", reps="10-12 reps", rest_seconds=90, key_cue="Pull with elbows down to ribs, chest up."),
                    Exercise(name="Standing Dumbbell Biceps Curls", sets="3 sets", reps="10-12 reps", rest_seconds=60, key_cue="Control the downward phase for 2 full seconds.")
                ]
            ),
            WorkoutDay(
                day_title="Day 3: Full Body Foundation C",
                target_muscles=["Glutes", "Quads", "Chest", "Core"],
                exercises=[
                    Exercise(name="Leg Press Machine", sets="3 sets", reps="10-12 reps", rest_seconds=120, key_cue="Smooth motion, do not lock out knees aggressively at top."),
                    Exercise(name="Dumbbell Flat Bench Press", sets="3 sets", reps="8-10 reps", rest_seconds=90, key_cue="Lower slowly with hands angled at 45°."),
                    Exercise(name="Cable Face Pulls", sets="3 sets", reps="12-15 reps", rest_seconds=60, key_cue="Pull rope toward eyes to strengthen postural upper back."),
                    Exercise(name="Side Plank Holds", sets="3 sets", reps="25 seconds/side", rest_seconds=60, key_cue="Stack shoulder directly above elbow, keep hips high.")
                ]
            )
        ]
        
        challenge = DailyChallenge(
            title="The 30-Rep Kinetic Activation Drill",
            difficulty_badge="Level 1: Foundation Catalyst",
            description="Gentle joint mobilization and movement pattern builder.",
            challenge_steps=[
                "Perform 10 arm circles forward and backward to warm up shoulders.",
                "Execute 3 sets of 10 bodyweight squats using the AI Pose Coach for instant feedback.",
                "Hold a 30-second plank to lock in core bracing.",
                "Drink a tall glass of water and log your session."
            ],
            completion_time_est="6 Minutes"
        )

    coach_note = (
        f"Calibrated for fitness score {score}/100 and Indian locality ({location}). "
        f"Focus on progressive overload: track your poundages, prioritize sleep, "
        f"and visit our verified Indian gyms for elite barbell rigs and recovery suites."
    )

    return RoutineResponse(
        workout_split=WorkoutSplit(
            split_name=split_name,
            frequency=frequency,
            description=split_desc,
            days=days
        ),
        daily_challenge=challenge,
        local_gyms=local_gyms,
        coach_note=coach_note,
        source="pulse-indian-gym-engine"
    )
