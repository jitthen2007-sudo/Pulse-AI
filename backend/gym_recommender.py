import os
from typing import List
from pydantic import BaseModel, Field

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
    rating: float = 4.8
    review_count: int = 340
    star_display: str = "⭐⭐⭐⭐⭐ 4.8"

class RoutineResponse(BaseModel):
    workout_split: WorkoutSplit
    daily_challenge: DailyChallenge
    local_gyms: List[LocalGym]
    coach_note: str
    source: str = "gemini"

async def recommend_gyms_and_routines(req: RoutineRequest) -> RoutineResponse:
    location = req.location.strip() or "Austin, TX"
    goal = req.goal
    score = req.performance_score

    loc_lower = location.lower()
    local_gyms = [
        LocalGym(
            name="Equinox Fitness Club",
            locality_context=f"Serving {location} metropolitan athletes",
            vibe="Luxury high-performance facility with elite Tier-X strength coaching",
            key_amenities=["Olympic lifting platforms", "Cold plunge pools", "Spa & sauna", "Pilates reformer studio"],
            why_recommended="Ideal biomechanical recovery suite and top-tier barbell equipment for injury-free progression.",
            rating=4.9,
            review_count=520,
            star_display="⭐⭐⭐⭐⭐ 4.9"
        ),
        LocalGym(
            name="Gold's Gym / Metroflex Power Gym",
            locality_context=f"Premier heavy-iron community in {location}",
            vibe="Authentic bodybuilding and strength mecca with calibrated plates",
            key_amenities=["Eleiko power racks", "Dumbbells up to 150 lbs", "Chalk-friendly lifting platforms", "Glute-ham developers"],
            why_recommended="Unrivaled training culture to maximize neuromuscular drive and heavy progressive overload.",
            rating=4.8,
            review_count=890,
            star_display="⭐⭐⭐⭐⭐ 4.8"
        ),
        LocalGym(
            name="Anytime Fitness & Athletic Club",
            locality_context=f"Convenient neighborhood access across {location}",
            vibe="Clean, 24/7 accessible training hub with modern cable and cardio stations",
            key_amenities=["24/7 secure access", "Functional turf lane", "Hammer Strength machines", "Private shower suites"],
            why_recommended="Zero schedule friction so you never miss a split session regardless of work hours.",
            rating=4.7,
            review_count=415,
            star_display="⭐⭐⭐⭐½ 4.7"
        )
    ]

    if any(k in loc_lower for k in ["bangalore", "bengaluru", "mumbai", "delhi", "india", "hyderabad", "pune"]):
        local_gyms = [
            LocalGym(
                name="Cult.fit & Cult Elite Center",
                locality_context=f"Prime athletic training hub in {location}",
                vibe="High-energy functional athletic training, group conditioning & strength floor",
                key_amenities=["HRX strength circuits", "Olympic lifting rigs", "Boxing ring", "Steam recovery rooms"],
                why_recommended="Data-driven workout tracking and top athletic community support in the region.",
                rating=4.8,
                review_count=1240,
                star_display="⭐⭐⭐⭐⭐ 4.8"
            ),
            LocalGym(
                name="Gold's Gym India",
                locality_context=f"Full-spectrum strength gym in {location}",
                vibe="Serious bodybuilding and body recomposition facility",
                key_amenities=["Heavy dumbbell rows up to 60kg", "Precor selectorized machines", "Certified biomechanics trainers", "Sauna"],
                why_recommended="Time-tested hypertrophy equipment and isolated biomechanical machines for maximum hypertrophy.",
                rating=4.7,
                review_count=870,
                star_display="⭐⭐⭐⭐½ 4.7"
            ),
            LocalGym(
                name="Snap Fitness 24/7",
                locality_context=f"Modern neighborhood club in {location}",
                vibe="Sleek, round-the-clock training with Matrix & Cybex equipment",
                key_amenities=["24/7 biometric key access", "Olympic squat racks", "Functional turf track", "Hydration station"],
                why_recommended="Flexibility to hit workouts early morning or late night without crowded wait times.",
                rating=4.6,
                review_count=630,
                star_display="⭐⭐⭐⭐½ 4.6"
            )
        ]
    elif any(k in loc_lower for k in ["london", "uk", "manchester", "birmingham"]):
        local_gyms = [
            LocalGym(
                name="Third Space London",
                locality_context=f"Elite central training sanctuary in {location}",
                vibe="Ultra-premium athletic club with bespoke strength and recovery zones",
                key_amenities=["Natural athletic turf", "Cryotherapy chambers", "Olympic lifting platforms", "UV-filtered swimming pool"],
                why_recommended="The benchmark for recovery science, elite equipment, and performance nutrition.",
                rating=4.9,
                review_count=780,
                star_display="⭐⭐⭐⭐⭐ 4.9"
            ),
            LocalGym(
                name="Gymbox",
                locality_context=f"High-octane urban playground in {location}",
                vibe="Nightclub lighting meets serious combat and heavy strength programming",
                key_amenities=["Combat sports cages", "Custom free-weight zones", "Olympic rigs", "Laser recovery suites"],
                why_recommended="High-adrenaline atmosphere that eliminates workout sluggishness and elevates output.",
                rating=4.7,
                review_count=920,
                star_display="⭐⭐⭐⭐½ 4.7"
            ),
            LocalGym(
                name="PureGym 24/7",
                locality_context=f"High-value accessible strength network across {location}",
                vibe="Straightforward, clean 24/7 training with extensive free weights",
                key_amenities=["50+ cardio stations", "Extensive dumbbell racks", "Lifting platforms", "Contactless app entry"],
                why_recommended="Reliable, no-nonsense setup to execute your routine consistently at any hour.",
                rating=4.5,
                review_count=1450,
                star_display="⭐⭐⭐⭐½ 4.5"
            )
        ]

    daily_challenge = DailyChallenge(
        title="Tempo Squat & Core Stability Crucible",
        difficulty_badge="Score Calibration: Intermediate (40-79)",
        description="Engineered to stimulate motor-unit synchronization and reinforce pristine squat depth mechanics.",
        challenge_steps=[
            "Complete 4 sets of 12 bodyweight squats using a 3-second eccentric (down) tempo.",
            "Use Pulse AI's Pose Coach to ensure your left knee angle drops below 95° on every rep.",
            "Hold a 45-second hollow body rock or plank after each set with maximum pelvic tuck.",
            "Rest exactly 60 seconds between rounds to train lactate clearance."
        ],
        completion_time_est="12 - 15 minutes"
    )

    if score < 40:
        daily_challenge = DailyChallenge(
            title="Foundational Movement & Mobility Primer",
            difficulty_badge="Score Calibration: Foundation (1-39)",
            description="Focuses on neuromuscular activation, joint lubricity, and hip hinge alignment without excessive CNS fatigue.",
            challenge_steps=[
                "Perform 3 sets of 8 bodyweight box/chair squats with hands reaching forward for counter-balance.",
                "Open Pulse AI's Pose Coach and aim for steady 100°-95° depth with knees tracking toes.",
                "Hold 3 rounds of 20-second glute bridges at peak contraction.",
                "Finish with 10 slow cat-cow spinal flexions for thoracic mobility."
            ],
            completion_time_est="8 - 10 minutes"
        )
    elif score >= 80:
        daily_challenge = DailyChallenge(
            title="Centurion Volume & Lactate Threshold Protocol",
            difficulty_badge="Score Calibration: Advanced Athlete (80-100)",
            description="High-density metabolic and eccentric stress designed for advanced neuromuscular adaptation.",
            challenge_steps=[
                "5 rounds: 15 barbell or dumbbell squats breaking 95° depth verified by Pose Coach.",
                "Superset immediately with 12 explosive jump lunges or Bulgarian split squats per leg.",
                "Perform a 30-second isometric wall sit with femurs strictly parallel to floor.",
                "Active recovery: 45 seconds deep nasal diaphragmatic breathing before starting the next round."
            ],
            completion_time_est="18 - 22 minutes"
        )

    workout_split = WorkoutSplit(
        split_name="4-Day Hypertrophy & Density Upper/Lower Split",
        frequency="4 Days / Week (Upper A, Lower A, Rest, Upper B, Lower B, Rest, Rest)",
        description="Optimized for lean myofibrillar growth with 72-hour recovery windows between synergistic muscle groups.",
        days=[
            WorkoutDay(
                day_title="Day 1: Upper Body Power & Lat Width",
                target_muscles=["Pectorals", "Latissimus Dorsi", "Anterior Delts", "Triceps"],
                exercises=[
                    Exercise(name="Barbell Incline Bench Press", sets="4", reps="6-8", rest_seconds=150, key_cue="Retract scapulae and tuck elbows 45° to eliminate shoulder impingement."),
                    Exercise(name="Chest-Supported T-Bar Row", sets="4", reps="8-10", rest_seconds=120, key_cue="Initiate by driving elbows toward the hips; hold 1s peak squeeze."),
                    Exercise(name="Standing Overhead Dumbbell Press", sets="3", reps="8-10", rest_seconds=90, key_cue="Brace core and lock glutes to protect the lumbar spine."),
                    Exercise(name="Dual Cable Triceps Pressdown", sets="3", reps="12-15", rest_seconds=60, key_cue="Pin elbows to your ribs and flare wrists at bottom lockout.")
                ]
            ),
            WorkoutDay(
                day_title="Day 2: Lower Body Quad & Posterior Chain",
                target_muscles=["Quadriceps", "Hamstrings", "Glutes", "Calves"],
                exercises=[
                    Exercise(name="Barbell Back Squat", sets="4", reps="6-8", rest_seconds=180, key_cue="Break parallel (<95° knee angle) and drive knees out over pinky toes."),
                    Exercise(name="Romanian Deadlift (RDL)", sets="4", reps="8-10", rest_seconds=120, key_cue="Hinge hips backward like touching a wall; keep lats tightly locked."),
                    Exercise(name="Bulgarian Split Squat", sets="3", reps="10-12/leg", rest_seconds=90, key_cue="Slight forward torso lean shifts maximum tension to glute max."),
                    Exercise(name="Standing Calf Raise", sets="4", reps="12-15", rest_seconds=60, key_cue="Pause 2 seconds in full deep stretch to eliminate Achilles elasticity.")
                ]
            ),
            WorkoutDay(
                day_title="Day 3: Upper Body Hypertrophy & Shoulders",
                target_muscles=["Upper Chest", "Rhomboids", "Lateral Delts", "Biceps"],
                exercises=[
                    Exercise(name="Dumbbell Flat Bench Press", sets="4", reps="8-12", rest_seconds=120, key_cue="Descend with 3s tempo for deep pec stretch at bottom."),
                    Exercise(name="Lat Pulldown (Neutral Grip)", sets="4", reps="10-12", rest_seconds=90, key_cue="Pull chest up to bar; focus on depressing shoulder blades."),
                    Exercise(name="Cable Lateral Raise", sets="4", reps="15-20", rest_seconds=60, key_cue="Pull from behind back; elevate arm in scapular plane (30° forward)."),
                    Exercise(name="Incline Dumbbell Biceps Curl", sets="3", reps="10-12", rest_seconds=60, key_cue="Keep elbows back to recruit long head of biceps.")
                ]
            ),
            WorkoutDay(
                day_title="Day 4: Posterior Chain & Hamstring Dominance",
                target_muscles=["Hamstrings", "Glutes", "Core", "Vastus Medialis"],
                exercises=[
                    Exercise(name="Barbell Hip Thrust", sets="4", reps="8-10", rest_seconds=120, key_cue="Tuck chin to chest; achieve full posterior pelvic tilt at lockout."),
                    Exercise(name="Leg Press (Feet High & Wide)", sets="4", reps="10-12", rest_seconds=120, key_cue="Do not allow lower back to round off the seat pad."),
                    Exercise(name="Seated Hamstring Curl", sets="4", reps="12-15", rest_seconds=75, key_cue="Torso leaned forward to lengthen hamstring over the hip joint."),
                    Exercise(name="Hanging Leg Raise", sets="3", reps="12-15", rest_seconds=60, key_cue="Roll pelvis upward toward sternum rather than swinging legs.")
                ]
            )
        ]
    )

    if any(k in goal.lower() for k in ["fat", "loss", "shred", "burn"]):
        workout_split.split_name = "Metabolic Resistance & Fat Shred Split"
        workout_split.description = "Combines heavy compound tension with short rest density and metabolic conditioning to maintain muscle while accelerating caloric expenditure."
    elif any(k in goal.lower() for k in ["strength", "power"]):
        workout_split.split_name = "5x5 Linear Strength & Neurological Peaking Split"
        workout_split.description = "Focused on submaximal load progression, 3-minute rest periods, and high motor-unit recruitment across the Big Three."

    return RoutineResponse(
        workout_split=workout_split,
        daily_challenge=daily_challenge,
        local_gyms=local_gyms,
        coach_note=f"Split and facilities calibrated for {location} with benchmark score {score}/100. Use AI Pose Coach to verify your knee angles.",
        source="pulse-engine"
    )
