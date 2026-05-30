from flask import Flask, render_template, request, jsonify, session, send_from_directory
import json, math, os, urllib.request, urllib.error
from database import get_exercises, get_yoga_poses, get_home_workouts

app = Flask(__name__)
app.secret_key = "IronBuddy-secret-2024"

# ── Exercise Data ──────────────────────────────────────────────────────────────
EXERCISES = {
    "Chest": [
        {"name": "Barbell Bench Press", "desc": "Lie flat, grip the barbell shoulder-width, lower to chest, press up explosively.", "diff": "intermediate", "muscles": "Pecs, Triceps", "equipment": "Barbell", "yt": "https://www.youtube.com/watch?v=gRVjAtPip0Y"},
        {"name": "Incline Dumbbell Press", "desc": "Targets upper chest. Set bench to 30–45°, press dumbbells from shoulder level.", "diff": "intermediate", "muscles": "Upper Pecs, Front Delts", "equipment": "Dumbbell", "yt": "https://www.youtube.com/watch?v=8iPEnn-ltC8"},
        {"name": "Chest Fly", "desc": "Isolation move for maximum pec stretch. Slight elbow bend.", "diff": "beginner", "muscles": "Pectorals", "equipment": "Dumbbell", "yt": "https://www.youtube.com/watch?v=eozdVDA78K0"},
        {"name": "Push-ups", "desc": "Zero-equipment classic. Hands shoulder-width, lower chest to floor.", "diff": "beginner", "muscles": "Pecs, Core, Triceps", "equipment": "Bodyweight", "yt": "https://www.youtube.com/watch?v=IODxDxX7oi4"},
        {"name": "Cable Crossover", "desc": "Pull the cables from high to low for lower pec activation.", "diff": "advanced", "muscles": "Lower Chest, Pectorals", "equipment": "Machine", "yt": "https://www.youtube.com/watch?v=taI4XduLpTk"},
    ],
    "Back": [
        {"name": "Pull-ups", "desc": "Overhand grip, full hang, pull until chin clears the bar cleanly.", "diff": "advanced", "muscles": "Lats, Biceps, Rhomboids", "equipment": "Bodyweight", "yt": "https://www.youtube.com/watch?v=eGo4IYlbE5g"},
        {"name": "Lat Pulldown", "desc": "Wide grip, lean slightly back, pull bar down to upper chest.", "diff": "beginner", "muscles": "Latissimus Dorsi", "equipment": "Machine", "yt": "https://www.youtube.com/watch?v=CAwf7n6Luuc"},
        {"name": "Barbell Deadlift", "desc": "Full posterior chain movement. Hip hinge, neutral spine.", "diff": "advanced", "muscles": "Hamstrings, Glutes, Erectors", "equipment": "Barbell", "yt": "https://www.youtube.com/watch?v=op9kVnSso6Q"},
        {"name": "Seated Cable Row", "desc": "Horizontal pull for mid-back thickness. Keep elbows close.", "diff": "beginner", "muscles": "Rhomboids, Mid-Traps", "equipment": "Machine", "yt": "https://www.youtube.com/watch?v=GZbfZ033f74"},
        {"name": "Dumbbell Rows", "desc": "One-arm row. Pull dumbbell to hip, squeezing lats.", "diff": "intermediate", "muscles": "Lats, Biceps", "equipment": "Dumbbell", "yt": "https://www.youtube.com/watch?v=pYcpY20QaE8"},
    ],
    "Legs": [
        {"name": "Barbell Squats", "desc": "Bar on traps, squat to parallel, drive knees out throughout.", "diff": "intermediate", "muscles": "Quads, Glutes, Hamstrings", "equipment": "Barbell", "yt": "https://www.youtube.com/watch?v=ultWZbUMPL8"},
        {"name": "Dumbbell Lunges", "desc": "Unilateral leg builder. Step forward, lower rear knee toward floor.", "diff": "beginner", "muscles": "Quads, Glutes, Hamstrings", "equipment": "Dumbbell", "yt": "https://www.youtube.com/watch?v=QOVaHwm-Q6U"},
        {"name": "Leg Press", "desc": "Machine compound for legs. Feet shoulder-width.", "diff": "beginner", "muscles": "Quads, Glutes", "equipment": "Machine", "yt": "https://www.youtube.com/watch?v=IZxyjW7MPJQ"},
        {"name": "Standing Calf Raises", "desc": "Rise fully onto toes, lower slowly for a complete stretch.", "diff": "beginner", "muscles": "Gastrocnemius, Soleus", "equipment": "Bodyweight", "yt": "https://www.youtube.com/watch?v=-M4-G8p8fmc"},
        {"name": "Leg Extensions", "desc": "Isolate the quads using the extension machine.", "diff": "beginner", "muscles": "Quadriceps", "equipment": "Machine", "yt": "https://www.youtube.com/watch?v=YyvSfVjQeL0"},
    ],
    "Shoulders": [
        {"name": "Shoulder Press", "desc": "Bar at chin, press overhead to complete extension.", "diff": "intermediate", "muscles": "All 3 Delt Heads", "equipment": "Barbell", "yt": "https://www.youtube.com/watch?v=2yjwXTZQDDI"},
        {"name": "Lateral Raises", "desc": "Side delt isolation. Raise dumbbells to shoulder height.", "diff": "beginner", "muscles": "Medial Delts", "equipment": "Dumbbell", "yt": "https://www.youtube.com/watch?v=3VcKaXpzqRo"},
        {"name": "Front Raises", "desc": "Anterior delt isolation. arms straight, lift to eye level.", "diff": "beginner", "muscles": "Anterior Delts", "equipment": "Dumbbell", "yt": "https://www.youtube.com/watch?v=sOoBQDGNOwE"},
        {"name": "Face Pulls", "desc": "Use cable machine with rope to target rear delts.", "diff": "intermediate", "muscles": "Rear Delts, Traps", "equipment": "Machine", "yt": "https://www.youtube.com/watch?v=rep-qVOkqgk"},
    ],
    "Arms": [
        {"name": "Dumbbell Bicep Curls", "desc": "Classic bicep isolation. Curl fully, squeeze hard at top.", "diff": "beginner", "muscles": "Biceps Brachii", "equipment": "Dumbbell", "yt": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo"},
        {"name": "Tricep Dips", "desc": "Bodyweight tricep builder. Shoulders down, lower until 90°.", "diff": "intermediate", "muscles": "Triceps, Chest", "equipment": "Bodyweight", "yt": "https://www.youtube.com/watch?v=0326dy_-CzM"},
        {"name": "Hammer Curls", "desc": "Neutral-grip curl targeting brachialis for thicker arms.", "diff": "beginner", "muscles": "Brachialis", "equipment": "Dumbbell", "yt": "https://www.youtube.com/watch?v=zC3nLlEvin4"},
        {"name": "Tricep Pushdowns", "desc": "Cable extension for triceps with rope or straight bar.", "diff": "beginner", "muscles": "Triceps", "equipment": "Machine", "yt": "https://www.youtube.com/watch?v=2-LAMcpzODU"},
        {"name": "Barbell Curls", "desc": "Heavy mass builder for the biceps. Strict form.", "diff": "intermediate", "muscles": "Biceps", "equipment": "Barbell", "yt": "https://www.youtube.com/watch?v=kwG2ipFRgfo"},
    ],
    "Core": [
        {"name": "Crunches", "desc": "Basic ab flexion. Lower back pressed to floor, lift shoulder blades.", "diff": "beginner", "muscles": "Upper Abs", "equipment": "Bodyweight", "yt": "https://www.youtube.com/watch?v=Xyd_fa5zoEU"},
        {"name": "Hanging Leg Raises", "desc": "Advanced lower ab movement. Hang from bar, raise legs to 90°.", "diff": "advanced", "muscles": "Lower Abs", "equipment": "Bodyweight", "yt": "https://www.youtube.com/watch?v=JB2oyawG9KI"},
        {"name": "Cable Crunches", "desc": "Weighted crunch using a cable stack. Kneel down, pull rope to head.", "diff": "intermediate", "muscles": "Abs", "equipment": "Machine", "yt": "https://www.youtube.com/watch?v=2-LAMcpzODU"},
        {"name": "Russian Twists", "desc": "Oblique rotational exercise. Use a medicine ball or dumbbell.", "diff": "intermediate", "muscles": "Obliques", "equipment": "Dumbbell", "yt": "https://www.youtube.com/watch?v=wkD8rjkodU"},
        {"name": "Plank", "desc": "Static core hold. Forearms or hands, body straight like a board.", "diff": "beginner", "muscles": "Core", "equipment": "Bodyweight", "yt": "https://www.youtube.com/watch?v=pvIjsG5Svck"},
    ],
}

# ── Yoga Data ──────────────────────────────────────────────────────────────────
YOGA = {
    "Morning Flow": [
        {"name": "Surya Namaskar (Sun Salutation)", "desc": "Energizing sequence for vitality.", "diff": "beginner", "duration": "5 min", "video": "surya-namaskar.mp4"},
        {"name": "Marjaryasana (Cat-Cow)", "desc": "Spinal flexibility and core engagement.", "diff": "beginner", "duration": "3 min", "yt": "kqnua4rHVVA"},
        {"name": "Anulom Vilom (Breathing)", "desc": "Traditional yogic breathing for clarity.", "diff": "beginner", "duration": "5 min", "video": "Anulom Vilom (Breathing).mp4"},
        {"name": "Kapalbhati (Breathing Exercise)", "desc": "Energizing skull-shining breath.", "diff": "intermediate", "duration": "5 min", "video": "Kapalbhati (Breathing Exercise).mp4"},
        {"name": "Morning Flow Sequence", "desc": "Complete AM routine to wake up.", "diff": "intermediate", "duration": "15 min", "yt": "4pKly2JojMw"},
    ],
    "Flexibility": [
        {"name": "Bhujangasana (Cobra Pose)", "desc": "Chest opener and spine strengthener.", "diff": "beginner", "duration": "3 min", "video": "Bhujangasana (Cobra Pose).mp4"},
        {"name": "Paschimottanasana (Forward Bend)", "desc": "Deep hamstring and spinal stretch.", "diff": "beginner", "duration": "3 min", "video": "Paschimottanasana (Forward Bend).mp4"},
        {"name": "Trikonasana (Triangle Pose)", "desc": "Strengthens legs and improves balance.", "diff": "beginner", "duration": "3 min", "video": "Trikonasana (Triangle Pose).mp4"},
        {"name": "Ustrasana (Camel Pose)", "desc": "Powerful backbend and heart opener.", "diff": "intermediate", "duration": "3 min", "video": "Ustrasana (Camel Pose).mp4"},
        {"name": "Flexibility Flow Sequence", "desc": "Deep stretching for full range of motion.", "diff": "intermediate", "duration": "20 min", "yt": "ypbKer1bSJE"},
    ],
    "Strength Yoga": [
        {"name": "Virabhadrasana I (Warrior 1)", "desc": "Builds leg power and stability.", "diff": "intermediate", "duration": "3 min", "video": "Virabhadrasana I (Warrior 1).mp4"},
        {"name": "Virabhadrasana II (Warrior 2)", "desc": "Enhances stamina and leg strength.", "diff": "intermediate", "duration": "3 min", "video": "Virabhadrasana II (Warrior 2).mp4"},
        {"name": "Vrikshasana (Tree Pose)", "desc": "Improves focus and single-leg balance.", "diff": "beginner", "duration": "2 min", "video": "Vrikshasana (Tree Pose).mp4"},
        {"name": "Naukasana (Boat Pose)", "desc": "Core-focused pose for abdominal strength.", "diff": "intermediate", "duration": "2 min", "video": "Naukasana (Boat Pose).mp4"},
        {"name": "Strength Flow Sequence", "desc": "Powerful flow to build lean muscle.", "diff": "advanced", "duration": "25 min", "yt": "ybMKN7oBSSs"},
    ],
    "Relaxation": [
        {"name": "Balasana (Child's Pose)", "desc": "Restorative pose to calm the mind.", "diff": "beginner", "duration": "3 min", "video": "Balasana (Child's Pose).mp4"},
        {"name": "Adho Mukha (Downward Dog)", "desc": "Full body stretch and inversion.", "diff": "beginner", "duration": "3 min", "video": "Adho Mukha (Downward Dog).mp4"},
        {"name": "Setu Bandha (Bridge Pose)", "desc": "Strengthens back and opens chest.", "diff": "beginner", "duration": "3 min", "yt": "Z4PdGxLBnfc"},
        {"name": "Shavasana (Corpse Pose)", "desc": "Total body relaxation and integration.", "diff": "beginner", "duration": "5 min", "yt": "zd4RPuZGRac"},
        {"name": "Relaxation Flow Sequence", "desc": "Gentle flow for deep peace.", "diff": "beginner", "duration": "15 min", "yt": "inpok4MKVLM"},
    ],
    "Aerial Yoga": [
        {"name": "Aerial Hammock Pose", "desc": "Fundamental aerial yoga position.", "diff": "beginner", "duration": "5 min", "yt": "bGUGOdOoZqU"},
        {"name": "Inverted Hang", "desc": "Full decompression for the spine.", "diff": "intermediate", "duration": "3 min", "yt": "FhwDSBRe8LU"},
        {"name": "Aerial Backbend", "desc": "Deep supported back extension.", "diff": "intermediate", "duration": "3 min", "yt": "UEqLtDpHiGY"},
        {"name": "Cocoon Pose (Aerial Shavasana)", "desc": "Restorative floating relaxation.", "diff": "beginner", "duration": "5 min", "yt": "9Bhj2cn_5So"},
        {"name": "Aerial Warrior", "desc": "Flying variation of warrior poses.", "diff": "intermediate", "duration": "4 min", "yt": "mOBpqSMjPR0"},
        {"name": "Aerial Pigeon Pose", "desc": "Deep hip opener with hammock support.", "diff": "intermediate", "duration": "4 min", "yt": "7Phd_kV6_pE"},
        {"name": "Aerial Forward Fold", "desc": "Inverted hamstring and back stretch.", "diff": "beginner", "duration": "3 min", "yt": "hHpUWaVuG5Q"},
        {"name": "Aerial Splits", "desc": "Advanced flexibility in the air.", "diff": "advanced", "duration": "4 min", "yt": "Q4e3_eDSBM8"},
    ],
}

# ── Home Workouts (No Equipment) ───────────────────────────────────────────────
HOME_WORKOUTS = {
    "Full Body HIIT": [
        {"name": "Jumping Jacks", "desc": "Classic cardio. Jump feet wide, arms overhead. Keep core tight. 45 seconds on.", "diff": "beginner", "reps": "45 sec", "yt": "https://www.youtube.com/watch?v=iSSAk4XCsRA"},
        {"name": "Burpees", "desc": "Full body explosive. Drop to plank, push-up, jump feet in, leap up. Intense cardio.", "diff": "intermediate", "reps": "15 reps", "yt": "https://www.youtube.com/watch?v=auQLewI-B0w"},
        {"name": "Mountain Climbers", "desc": "Core + cardio. Plank position, alternate driving knees to chest. Fast pace.", "diff": "beginner", "reps": "30 sec", "yt": "https://www.youtube.com/watch?v=zT-9L37ReW8"},
        {"name": "Jump Squats", "desc": "Explosive legs. Squat down, explode up into jump. Soft landing, immediate next rep.", "diff": "intermediate", "reps": "20 reps", "yt": "https://www.youtube.com/watch?v=72BSZupbCPk"},
        {"name": "High Knees", "desc": "Running in place. Drive knees to hip height, pump arms. Cardio blast.", "diff": "beginner", "reps": "30 sec", "yt": "https://www.youtube.com/watch?v=Z5uI6K6A1E0"},
    ],
    "Core Crusher": [
        {"name": "Crunches", "desc": "Basic ab flexion. Lower back pressed to floor, lift shoulder blades. Controlled.", "diff": "beginner", "reps": "20 reps", "yt": "https://www.youtube.com/watch?v=Xyd_fa5zoEU"},
        {"name": "Plank", "desc": "Static core hold. Forearms or hands, body straight. Squeeze glutes, breathe.", "diff": "beginner", "reps": "60 sec", "yt": "https://www.youtube.com/watch?v=pSHjTRCQxIw"},
        {"name": "Russian Twists", "desc": "Oblique exercise. Seated, lean back, twist torso side to side. Feet up for challenge.", "diff": "beginner", "reps": "30 reps", "yt": "https://www.youtube.com/watch?v=wkD8rjkodU"},
        {"name": "Leg Raises", "desc": "Lower abs. Lying on back, legs straight, lift to 90°. Control the descent.", "diff": "intermediate", "reps": "15 reps", "yt": "https://www.youtube.com/watch?v=JB2oyawG9KI"},
        {"name": "Bicycle Crunches", "desc": "Obliques + rectus abdominis. Alternate elbow to opposite knee. Slow and controlled.", "diff": "beginner", "reps": "30 reps", "yt": "https://www.youtube.com/watch?v=1919eTCo6S0"},
    ],
    "Upper Body": [
        {"name": "Push-ups", "desc": "Classic chest/triceps. Body straight, lower to ground, press back up. Many variations.", "diff": "beginner", "reps": "15 reps", "yt": "https://www.youtube.com/watch?v=IODxDxX7oi4"},
        {"name": "Diamond Push-ups", "desc": "Triceps focus. Hands form diamond under chest. Elbows tuck to sides.", "diff": "intermediate", "reps": "10 reps", "yt": "https://www.youtube.com/watch?v=J0DnG1_S92I"},
        {"name": "Tricep Dips (Chair)", "desc": "Use sturdy chair. Hands on edge, lower body, press up. Keep elbows back.", "diff": "beginner", "reps": "15 reps", "yt": "https://www.youtube.com/watch?v=0326dy_-CzM"},
        {"name": "Inchworms", "desc": "Dynamic warm-up. Walk hands to plank, walk back to feet. Core and shoulder engagement.", "diff": "beginner", "reps": "10 reps", "yt": "https://www.youtube.com/watch?v=ZY2nS6ad_Is"},
    ],
    "Lower Body": [
        {"name": "Bodyweight Squats", "desc": "Leg day staple. Feet shoulder-width, squat to parallel, drive up through heels.", "diff": "beginner", "reps": "20 reps", "yt": "https://www.youtube.com/watch?v=R1v152478fI"},
        {"name": "Lunges", "desc": "Unilateral strength. Step forward, lower until back knee nearly touches ground.", "diff": "beginner", "reps": "15 reps each", "yt": "https://www.youtube.com/watch?v=QOVaHwm-Q6U"},
        {"name": "Glute Bridges", "desc": "Posterior chain. Lie on back, lift hips, squeeze glutes at top.", "diff": "beginner", "reps": "20 reps", "yt": "https://www.youtube.com/watch?v=wPM8icqn6H8"},
        {"name": "Calf Raises", "desc": "Calf builder. Rise onto toes, hold, lower slowly. Use wall for balance.", "diff": "beginner", "reps": "20 reps", "yt": "https://www.youtube.com/watch?v=-M4-G8p8fmc"},
    ],
    "Cardio Blast": [
        {"name": "High Knees", "desc": "Cardio intensity. Drive knees up rapidly, pump arms. Keep core engaged.", "diff": "beginner", "reps": "30 sec", "yt": "https://www.youtube.com/watch?v=Z5uI6K6A1E0"},
        {"name": "Jump Rope (Imaginary)", "desc": "Cardio coordination. Mimic rope jumping, land on balls of feet.", "diff": "beginner", "reps": "45 sec", "yt": "https://www.youtube.com/watch?v=iSSAk4XCsRA"},
        {"name": "Box Jumps (No Box)", "desc": "Explosive power. Jump as high as possible, soft landing. Use ground.", "diff": "intermediate", "reps": "15 reps", "yt": "https://www.youtube.com/watch?v=72BSZupbCPk"},
        {"name": "Skaters", "desc": "Lateral cardio. Jump side to side, land on one leg, swing opposite arm back.", "diff": "intermediate", "reps": "20 reps", "yt": "https://www.youtube.com/watch?v=8K0tLzYfNIs"},
    ],
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def calc_bmi(weight, height_cm):
    if height_cm <= 0:
        return 0
    h = height_cm / 100
    return round(weight / (h * h), 1)

def bmi_status(bmi):
    if bmi < 18.5: return ("Underweight", "under")
    if bmi < 25:   return ("Normal",      "normal")
    if bmi < 30:   return ("Overweight",  "over")
    return              ("Obese",         "over")

def call_claude(prompt):
    """Call Anthropic API via urllib (no extra packages needed)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "8998ba9674b2300f90010b331fb02f0f")
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return "".join(b.get("text", "") for b in data["content"])

def generate_diet_local(age, weight, height, diet, activity_level="Moderately Active", workout_type="Mixed Training", body_fat=None, gender="Male"):
    """Generate personalized diet plan with advanced protein calculation."""
    bmi = calc_bmi(weight, height)
    
    # Calculate BMR (Mifflin-St Jeor Equation) - adjusted for gender
    if gender == "Female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    
    # Activity multipliers
    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725
    }
    
    # Determine goal and adjust calories
    if bmi < 18.5:  # Underweight - weight gain focus
        goal = "weight_gain"
        target_calories = int(bmr * activity_multipliers[activity_level] + 700)
        protein_base = 1.8  # g/kg for muscle building
    elif bmi < 22:  # Normal low end - muscle gain focus
        goal = "muscle_gain"
        target_calories = int(bmr * activity_multipliers[activity_level] + 300)
        protein_base = 2.2  # g/kg for muscle gain
    elif bmi < 25:  # Normal high end - maintenance
        goal = "maintenance"
        target_calories = int(bmr * activity_multipliers[activity_level])
        protein_base = 1.0  # g/kg for maintenance
    elif bmi < 30:  # Overweight - weight loss focus
        goal = "weight_loss"
        target_calories = int(bmr * activity_multipliers[activity_level] - 400)
        protein_base = 2.0  # g/kg for fat loss
    else:  # Obese - aggressive weight loss
        goal = "fat_loss"
        target_calories = int(bmr * activity_multipliers[activity_level] - 500)
        protein_base = 2.2  # g/kg for fat loss
    
    # Advanced protein calculation adjustments
    protein_adjustment = 0
    
    # Activity level adjustment
    if activity_level == "Very Active":
        protein_adjustment += 0.2
    elif activity_level == "Sedentary":
        protein_adjustment -= 0.1
    
    # Workout type adjustments
    if workout_type == "Weight Training":
        protein_adjustment += 0.3
    elif workout_type == "Cardio":
        protein_adjustment -= 0.1
    elif workout_type == "Bodyweight Training":
        protein_adjustment += 0.1
    
    # Body fat adjustment (if provided)
    if body_fat and body_fat > 25:
        lean_mass = weight * (1 - body_fat/100)
        protein_g = int(lean_mass * (protein_base + protein_adjustment))
    else:
        protein_g = int(weight * (protein_base + protein_adjustment))
    
    # Ensure protein ranges
    protein_ranges = {
        "weight_gain": (1.8, 2.5),
        "muscle_gain": (2.0, 2.8),
        "maintenance": (0.8, 1.5),
        "weight_loss": (1.8, 2.5),
        "fat_loss": (2.0, 2.8)
    }
    
    min_protein, max_protein = protein_ranges[goal]
    protein_g = max(min_protein * weight, min(max_protein * weight, protein_g))
    
    # Calculate macros based on goal
    if goal in ["weight_gain", "muscle_gain"]:
        protein_percent = 30
        carb_percent = 45
        fat_percent = 25
    elif goal in ["weight_loss", "fat_loss"]:
        protein_percent = 40
        carb_percent = 30
        fat_percent = 30
    else:  # maintenance
        protein_percent = 25
        carb_percent = 45
        fat_percent = 30
    
    # Calculate other macros
    protein_calories = protein_g * 4
    fat_calories = int((target_calories * fat_percent / 100))
    carb_calories = target_calories - protein_calories - fat_calories
    
    carbs_g = int(carb_calories / 4)
    fat_g = int(fat_calories / 9)
    
    # Enhanced water calculation
    base_water = weight * 0.035  # 35ml per kg
    activity_water = {
        "Sedentary": 0,
        "Lightly Active": 0.5,
        "Moderately Active": 1.0,
        "Very Active": 1.5
    }
    workout_water = {
        "Weight Training": 0.5,
        "Cardio": 1.0,
        "Mixed Training": 0.75,
        "Bodyweight Training": 0.3
    }
    
    water_liters = round(base_water + activity_water[activity_level] + workout_water[workout_type], 1)
    
    # Ensure reasonable bounds
    target_calories = max(1200, min(5000, target_calories))
    water_liters = max(2.0, min(6.0, water_liters))
    
    # Personalized meal plans based on goal and diet type
    meals_db = get_personalized_meals(goal, diet, target_calories)
    
    # Goal-specific tips
    goal_tips = {
        "weight_gain": f"Focus on calorie-dense foods. Eat every 2-3 hours. Target: {protein_g}g protein daily. Include healthy fats like nuts, avocado, and olive oil. Progressive strength training 3-4x/week.",
        "muscle_gain": f"Prioritize protein intake ({protein_g}g daily = {protein_g/weight:.1f}g/kg). Time carbs around workouts. Include compound exercises. Sleep 7-9 hours for recovery.",
        "maintenance": f"Maintain balanced macronutrients. Protein intake: {protein_g}g daily. Listen to hunger cues. Stay consistent with meal timing. Regular health checkups recommended.",
        "weight_loss": f"High protein ({protein_g}g daily) to preserve muscle mass. Focus on whole foods. Control portion sizes. Include both cardio and strength training.",
        "fat_loss": f"Very high protein intake ({protein_g}g daily = {protein_g/weight:.1f}g/kg). Minimize processed carbs and sugars. Time carbs around workouts only. Increase daily activity and NEAT."
    }
    
    return {
        "totalCalories": target_calories,
        "waterLiters": water_liters,
        "proteinG": int(protein_g),
        "carbsG": carbs_g,
        "fatG": fat_g,
        "goal": goal.replace("_", " ").title(),
        "meals": meals_db,
        "tip": goal_tips.get(goal, "Eat whole foods, stay hydrated, and maintain consistency over perfection."),
        "proteinPerKg": round(protein_g/weight, 1)
    }

def get_personalized_meals(goal, diet_type, target_calories):
    """Get personalized meals based on goal and diet type."""
    
    # Base meal templates
    base_meals = {
        "Veg": {
            "weight_gain": {
                "breakfast": {"name": "High-Calorie Oatmeal Bowl", "description": "80g rolled oats with 300ml whole milk, 25g almonds, 25g walnuts, 150g banana, 10g honey, 15g peanut butter. Calorie-dense for mass gain. (Alternative: 3 Besan Chilla = 570 kcal, 4 Moong Dal Cheela = 560 kcal)", "calories": 650},
                "morningSnack": {"name": "Protein Smoothie", "description": "200g Greek yogurt, 1 banana, 250ml milk, 30g whey protein, 20g peanut butter, 15g chia seeds. Mass gainer shake. (Options: 40g whey = 380 kcal, Add avocado = 450 kcal)", "calories": 450},
                "lunch": {"name": "Rajma Chawal with Ghee", "description": "120g kidney beans in gravy with 80g basmati rice, 10g ghee, 100g paneer cubes. High protein and carbs. (Option: 150g beans = 850 kcal, Add extra rice = 900 kcal)", "calories": 750},
                "eveningSnack": {"name": "Nut & Fruit Mix", "description": "30g almonds, 20g walnuts, 200g mango, 15g dates, 200ml full-fat milk. Energy-dense snack. (Options: 50g makhana = 350 kcal, Add avocado toast = 400 kcal)", "calories": 350},
                "dinner": {"name": "Paneer Butter Masala", "description": "150g paneer in rich gravy with 3 rotis (80g each), 100g cucumber raita, 10g butter. High protein dinner. (Option: 200g paneer = 800 kcal, Add extra roti = 850 kcal)", "calories": 700},
            },
            "muscle_gain": {
                "breakfast": {"name": "Protein Oatmeal", "description": "60g rolled oats with 250ml milk, 20g almonds, 100g banana, 30g whey protein mixed in. Protein-focused breakfast. (Alternative: 3 Moong Dal Cheela = 420 kcal, 2 Besan Chilla = 380 kcal)", "calories": 500},
                "morningSnack": {"name": "Greek Yogurt Power", "description": "200g Greek yogurt with 50g berries, 10g chia seeds, 15g almonds. High protein snack. (Options: 2 boiled eggs = 160 kcal, Protein shake = 280 kcal)", "calories": 280},
                "lunch": {"name": "Protein-Rich Rajma", "description": "120g kidney beans with 60g brown rice, 100g paneer, green salad. Balanced protein meal. (Option: 150g beans = 750 kcal, Add extra paneer = 800 kcal)", "calories": 650},
                "eveningSnack": {"name": "Sprouts & Nuts", "description": "100g sprouts chaat with 20g peanuts, 1 glass buttermilk. Protein boost. (Options: Protein shake = 220 kcal, 3 boiled eggs = 240 kcal)", "calories": 250},
                "dinner": {"name": "Paneer Tikka Special", "description": "150g grilled paneer with 2 rotis (60g each), 100g vegetables, 100g raita. Lean protein dinner. (Option: 180g paneer = 700 kcal, Add extra roti = 650 kcal)", "calories": 600},
            },
            "maintenance": {
                "breakfast": {"name": "Balanced Oatmeal", "description": "50g rolled oats with 250ml milk, 15g almonds, 15g walnuts, 100g banana, 5g honey. Balanced nutrition. (Alternative: 2 Besan Chilla = 380 kcal, 3 Moong Dal Cheela = 420 kcal)", "calories": 450},
                "morningSnack": {"name": "Greek Yogurt Berries", "description": "150g Greek yogurt with 50g berries, 5g chia seeds. Light protein snack. (Options: 200g yogurt = 270 kcal, Apple with peanut butter = 250 kcal)", "calories": 200},
                "lunch": {"name": "Rajma Chawal Standard", "description": "100g kidney beans with 60g rice, side salad. Balanced meal. (Option: 120g beans = 700 kcal, Chole with rice = 680 kcal)", "calories": 600},
                "eveningSnack": {"name": "Sprouts Chaat", "description": "80g sprouts with vegetables, lemon juice. Light evening snack. (Options: Fruit salad = 180 kcal, 15g makhana = 180 kcal)", "calories": 180},
                "dinner": {"name": "Paneer Tikka Regular", "description": "120g paneer with 2 rotis, vegetables, raita. Balanced dinner. (Option: 100g paneer = 480 kcal, Mix veg = 520 kcal)", "calories": 550},
            },
            "weight_loss": {
                "breakfast": {"name": "Light Oatmeal", "description": "40g rolled oats with water, 10g almonds, 50g berries, stevia. Low-calorie start. (Alternative: 1 Moong Dal Cheela = 140 kcal, Vegetable Upma 40g = 230 kcal)", "calories": 280},
                "morningSnack": {"name": "Protein Snack", "description": "100g Greek yogurt with 25g berries. High protein, low calorie. (Options: 1 boiled egg = 80 kcal, Apple slices = 80 kcal)", "calories": 120},
                "lunch": {"name": "Light Rajma", "description": "80g kidney beans with 40g brown rice, large salad. Protein-focused lunch. (Option: 100g beans = 450 kcal, Mix dal with roti = 420 kcal)", "calories": 400},
                "eveningSnack": {"name": "Light Sprouts", "description": "50g sprouts with cucumber, tomato, lemon. Very light snack. (Options: Green tea = 0 kcal, 1 cucumber = 45 kcal)", "calories": 80},
                "dinner": {"name": "Light Paneer", "description": "80g grilled paneer with 1 roti (40g), steamed vegetables. Light dinner. (Option: 100g paneer = 380 kcal, Mix veg without roti = 320 kcal)", "calories": 350},
            },
            "fat_loss": {
                "breakfast": {"name": "Protein Oats", "description": "30g rolled oats with water, 20g egg whites, 50g berries, cinnamon. High protein, very low carb. (Alternative: 2 egg omelette = 150 kcal, Protein shake = 180 kcal)", "calories": 220},
                "morningSnack": {"name": "Pure Protein", "description": "100g Greek yogurt unsweetened. Zero carb protein. (Options: 2 boiled eggs = 160 kcal, Green tea = 0 kcal)", "calories": 100},
                "lunch": {"name": "Protein Rajma", "description": "100g kidney beans without rice, large salad with olive oil. No carbs lunch. (Option: Grilled paneer 120g = 280 kcal, Mix dal no rice = 320 kcal)", "calories": 350},
                "eveningSnack": {"name": "Zero Carb", "description": "1 boiled egg or handful of nuts. Minimal calories. (Options: Black coffee = 0 kcal, 1 cucumber = 45 kcal)", "calories": 80},
                "dinner": {"name": "Lean Protein", "description": "100g grilled paneer with steamed vegetables only. No carbs dinner. (Option: 120g paneer = 340 kcal, Large salad = 150 kcal)", "calories": 300},
            }
        },
        "Non-Veg": {
            "weight_gain": {
                "breakfast": {"name": "Mass Gainer Eggs", "description": "4 eggs scrambled with cheese, 2 slices whole wheat bread, 250ml milk, 1 banana. High calorie breakfast. (Options: 5 eggs = 700 kcal, Add avocado toast = 650 kcal)", "calories": 650},
                "morningSnack": {"name": "Mass Gainer Shake", "description": "40g whey protein, 1 banana, 300ml whole milk, 30g peanut butter, 15g almonds. Calorie dense shake. (Options: 50g whey = 500 kcal, Add oats = 550 kcal)", "calories": 500},
                "lunch": {"name": "Chicken Rice Bulk", "description": "250g grilled chicken with 100g rice, vegetables, 10g olive oil. High protein bulk meal. (Option: 300g chicken = 900 kcal, Extra rice = 850 kcal)", "calories": 800},
                "eveningSnack": {"name": "Protein Nuts", "description": "3 boiled eggs, 30g almonds, 200ml full-fat milk. Protein and healthy fats. (Options: Chicken breast 150g = 350 kcal, Tuna sandwich = 400 kcal)", "calories": 400},
                "dinner": {"name": "Fish Rice Feast", "description": "200g salmon with 80g rice, vegetables, 15g ghee. Omega-3 rich dinner. (Option: 250g fish = 750 kcal, Add extra rice = 800 kcal)", "calories": 750},
            },
            "muscle_gain": {
                "breakfast": {"name": "Protein Eggs", "description": "4 eggs with 1 slice bread, 200ml milk, 1 banana. High protein breakfast. (Options: 3 eggs = 500 kcal, Chicken sandwich = 520 kcal)", "calories": 550},
                "morningSnack": {"name": "Protein Shake", "description": "35g whey protein, banana, 250ml milk, 15g peanut butter. Muscle building shake. (Options: 40g whey = 380 kcal, Greek yogurt 200g = 270 kcal)", "calories": 350},
                "lunch": {"name": "Chicken Rice Muscle", "description": "200g grilled chicken with 60g rice, vegetables, salad. Balanced protein meal. (Option: 250g chicken = 780 kcal, Fish curry = 620 kcal)", "calories": 650},
                "eveningSnack": {"name": "Eggs & Nuts", "description": "3 boiled eggs with 20g almonds. Protein snack. (Options: Chicken tikka 100g = 250 kcal, Protein shake = 220 kcal)", "calories": 280},
                "dinner": {"name": "Fish Protein", "description": "180g fish with 2 rotis, vegetables. Lean protein dinner. (Option: 200g fish = 600 kcal, Chicken curry = 680 kcal)", "calories": 580},
            },
            "maintenance": {
                "breakfast": {"name": "Standard Eggs", "description": "3 eggs with paratha, fresh juice. Balanced breakfast. (Options: 2 eggs = 350 kcal, Omelette toast = 450 kcal)", "calories": 500},
                "morningSnack": {"name": "Standard Shake", "description": "30g whey, banana, milk, peanut butter. Standard protein shake. (Options: 2 eggs + apple = 280 kcal, Greek yogurt = 270 kcal)", "calories": 250},
                "lunch": {"name": "Standard Chicken", "description": "200g chicken with 60g rice, vegetables. Standard lunch. (Options: 150g chicken = 520 kcal, Fish curry = 620 kcal)", "calories": 650},
                "eveningSnack": {"name": "Standard Snack", "description": "2 eggs with apple, almonds. Standard snack. (Options: 3 eggs = 300 kcal, Protein shake = 220 kcal)", "calories": 220},
                "dinner": {"name": "Standard Fish", "description": "150g fish with 2 rotis, vegetables. Standard dinner. (Options: 200g fish = 600 kcal, Chicken curry = 680 kcal)", "calories": 500},
            },
            "weight_loss": {
                "breakfast": {"name": "Light Eggs", "description": "2 egg whites + 1 whole egg with vegetables, no bread. Low calorie high protein. (Options: 3 egg omelette = 230 kcal, Protein shake = 180 kcal)", "calories": 250},
                "morningSnack": {"name": "Light Protein", "description": "1 boiled egg with apple. Light protein snack. (Options: Greek yogurt 100g = 100 kcal, Black coffee = 0 kcal)", "calories": 150},
                "lunch": {"name": "Light Chicken", "description": "150g chicken breast with large salad, no rice. Protein-focused lunch. (Options: 120g chicken = 420 kcal, Fish no rice = 380 kcal)", "calories": 450},
                "eveningSnack": {"name": "Very Light", "description": "1 boiled egg or protein shake. Minimal calories. (Options: Chicken breast 50g = 80 kcal, Green tea = 0 kcal)", "calories": 100},
                "dinner": {"name": "Light Fish", "description": "120g grilled fish with steamed vegetables only. Light dinner. (Options: 100g fish = 380 kcal, Large salad = 150 kcal)", "calories": 350},
            },
            "fat_loss": {
                "breakfast": {"name": "Keto Eggs", "description": "3 whole eggs cooked in butter, no carbs. High fat, zero carb. (Options: 4 eggs = 300 kcal, Protein shake = 180 kcal)", "calories": 280},
                "morningSnack": {"name": "Zero Carb", "description": "2 boiled eggs or handful of nuts. Zero carb snack. (Options: Black coffee = 0 kcal, Cheese cubes = 150 kcal)", "calories": 150},
                "lunch": {"name": "Keto Chicken", "description": "200g chicken with avocado, olive oil, no carbs. Keto lunch. (Options: 250g chicken = 450 kcal, Salmon no carbs = 500 kcal)", "calories": 400},
                "eveningSnack": {"name": "Fat Snack", "description": "15g almonds or cheese cubes. Fat-focused snack. (Options: Peanut butter = 180 kcal, Avocado = 200 kcal)", "calories": 120},
                "dinner": {"name": "Keto Fish", "description": "180g salmon with butter, vegetables. High fat dinner. (Options: 200g fish = 500 kcal, Steak with butter = 600 kcal)", "calories": 450},
            }
        },
        "Jain": {
            "weight_gain": {
                "breakfast": {"name": "High-Cal Poha", "description": "80g poha with 25g peanuts, 50g pomegranate, 20g cashews, 15g coconut, 10g ghee. Calorie dense. (Alternative: 3 Moong Dal Cheela = 420 kcal, Upma 80g = 500 kcal)", "calories": 600},
                "morningSnack": {"name": "Calorie Shake", "description": "200ml full-fat milk, 1 banana, 20g cashews, 10g dates, 5g honey. Mass gainer. (Options: Date milkshake = 350 kcal, Add avocado = 450 kcal)", "calories": 400},
                "lunch": {"name": "Bulk Dal Rice", "description": "120g dal tadka with 80g rice, 15g ghee, papad. High calorie lunch. (Option: 150g dal = 850 kcal, Extra rice = 800 kcal)", "calories": 750},
                "eveningSnack": {"name": "Energy Mix", "description": "30g makhana, 20g cashews, 200g mango, 15g dates. Energy dense. (Options: 50g makhana = 350 kcal, Banana chips = 250 kcal)", "calories": 350},
                "dinner": {"name": "Rich Paneer", "description": "150g paneer butter masala with 3 rotis, 10g butter. Rich dinner. (Option: 180g paneer = 750 kcal, Extra roti = 800 kcal)", "calories": 700},
            },
            "muscle_gain": {
                "breakfast": {"name": "Protein Poha", "description": "60g poha with 20g peanuts, 30g pomegranate, 15g cashews. Protein balanced. (Alternative: 2 Moong Dal Cheela = 280 kcal, Upma 60g = 380 kcal)", "calories": 450},
                "morningSnack": {"name": "Protein Shake", "description": "30g whey with banana, milk, almonds. Muscle building. (Options: Date milkshake = 250 kcal, Greek yogurt = 270 kcal)", "calories": 300},
                "lunch": {"name": "Protein Dal", "description": "100g dal with 60g rice, vegetables. Balanced protein. (Option: 120g dal = 650 kcal, Mix dal = 620 kcal)", "calories": 580},
                "eveningSnack": {"name": "Protein Nuts", "description": "20g makhana with 15g almonds, 1 glass milk. Protein snack. (Options: 2 banana chips = 180 kcal, Fruit salad = 180 kcal)", "calories": 200},
                "dinner": {"name": "Lean Paneer", "description": "120g paneer with 2 rotis, vegetables. Lean protein. (Option: 150g paneer = 600 kcal, Mix veg = 520 kcal)", "calories": 520},
            },
            "maintenance": {
                "breakfast": {"name": "Standard Poha", "description": "60g poha with 15g peanuts, 30g pomegranate, 15g cashews. Balanced. (Alternative: 2 Moong Dal Cheela = 280 kcal, Upma 60g = 380 kcal)", "calories": 420},
                "morningSnack": {"name": "Fruit Mix", "description": "Fruit bowl with 15g nuts. Light snack. (Options: Coconut water + nuts = 180 kcal, Date milkshake = 250 kcal)", "calories": 150},
                "lunch": {"name": "Standard Dal", "description": "80g dal with 60g rice, papad. Standard meal. (Option: 100g dal = 650 kcal, Rajma = 680 kcal)", "calories": 580},
                "eveningSnack": {"name": "Light Snack", "description": "30g makhana with fruit. Light evening snack. (Options: Fruit juice = 150 kcal, Banana chips = 180 kcal)", "calories": 160},
                "dinner": {"name": "Standard Paneer", "description": "120g paneer with 2 rotis, vegetables. Standard dinner. (Option: 100g paneer = 480 kcal, Veg biryani = 650 kcal)", "calories": 520},
            },
            "weight_loss": {
                "breakfast": {"name": "Light Poha", "description": "40g poha with 10g peanuts, 20g pomegranate. Low calorie. (Alternative: 1 Moong Dal Cheela = 140 kcal, Upma 40g = 250 kcal)", "calories": 300},
                "morningSnack": {"name": "Light Fruit", "description": "Fruit bowl only. Very light. (Options: Coconut water = 60 kcal, 1 banana = 100 kcal)", "calories": 100},
                "lunch": {"name": "Light Dal", "description": "60g dal with 40g rice, large salad. Light lunch. (Option: 80g dal = 500 kcal, Mix dal no rice = 420 kcal)", "calories": 400},
                "eveningSnack": {"name": "Very Light", "description": "15g makhana only. Minimal calories. (Options: Green tea = 0 kcal, 1 cucumber = 45 kcal)", "calories": 80},
                "dinner": {"name": "Light Paneer", "description": "80g paneer with 1 roti, steamed vegetables. Light dinner. (Option: 100g paneer = 480 kcal, Mix veg no roti = 320 kcal)", "calories": 350},
            },
            "fat_loss": {
                "breakfast": {"name": "Minimal Poha", "description": "30g poha with 5g peanuts only. Very low calorie. (Alternative: Protein shake = 180 kcal, 1 cheela = 140 kcal)", "calories": 200},
                "morningSnack": {"name": "Zero Cal", "description": "Green tea or black coffee. Zero calories. (Options: 1 cucumber = 45 kcal, Lemon water = 0 kcal)", "calories": 50},
                "lunch": {"name": "Protein Dal", "description": "80g dal without rice, large salad only. No carbs. (Option: 100g paneer = 280 kcal, Mix dal no rice = 320 kcal)", "calories": 300},
                "eveningSnack": {"name": "Minimal", "description": "10g makhana or lemon water. Almost zero calories. (Options: Black coffee = 0 kcal, Green tea = 0 kcal)", "calories": 50},
                "dinner": {"name": "Lean Protein", "description": "100g paneer with steamed vegetables only. No carbs. (Option: 80g paneer = 280 kcal, Large salad = 150 kcal)", "calories": 280},
            }
        }
    }
    
    return base_meals.get(diet_type, {}).get(goal, base_meals["Veg"]["maintenance"])

def generate_diet(name, gender, user_goal, age, weight, height, diet):
    """Generate personalized diet plan using local algorithm with advanced parameters."""
    # Extract activity level, workout type, and body fat from user data if available
    # Default to moderate activity and mixed training for backward compatibility
    activity_level = "Moderately Active"
    workout_type = "Mixed Training"
    body_fat = None
    
    return generate_diet_local(age, weight, height, diet, activity_level, workout_type, body_fat, gender)

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/api/user-data", methods=["POST"])
def save_user():
    d = request.json
    session["user"] = {
        "name":   d.get("name", "User"),
        "gender": d.get("gender", "Male"),
        "user_goal": d.get("user_goal", "Maintenance"),
        "age":    int(d.get("age", 25)),
        "weight": float(d.get("weight", 70)),
        "height": float(d.get("height", 170)),
        "diet":   d.get("diet", "Veg"),
    }
    session.pop("diet_plan", None)   # clear cached plan
    return jsonify({"ok": True, "user": session["user"]})

@app.route("/api/user-data", methods=["GET"])
def get_user():
    return jsonify(session.get("user"))

@app.route("/api/diet-plan", methods=["GET"])
def diet_plan():
    user = session.get("user")
    if not user:
        return jsonify({"error": "No user data"}), 400
    if "diet_plan" not in session:
        try:
            session["diet_plan"] = generate_diet(**user)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    plan = session["diet_plan"]
    bmi = calc_bmi(user["weight"], user["height"])
    label, cls = bmi_status(bmi)
    return jsonify({**plan, "bmi": bmi, "bmiLabel": label, "bmiCls": cls})

@app.route("/api/exercise-plan", methods=["GET"])
def exercise_plan():
    day = request.args.get("day", "Chest")
    exercises = get_exercises(category=day)
    return jsonify({"day": day, "exercises": exercises})

@app.route("/api/yoga-plan", methods=["GET"])
def yoga_plan():
    flow = request.args.get("flow", "Morning Flow")
    poses = get_yoga_poses(flow_category=flow)
    return jsonify({"flow": flow, "poses": poses})

@app.route('/static/videos/<filename>')
def serve_video(filename):
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'videos'),
        filename
    )

@app.route("/api/home-workout", methods=["GET"])
def home_workout():
    category = request.args.get("category", "Full Body HIIT")
    workouts = get_home_workouts(category=category)
    return jsonify({"category": category, "exercises": workouts})

@app.route("/api/calendar", methods=["GET"])
def get_calendar():
    return jsonify(session.get("calendar", []))

@app.route("/api/calendar", methods=["POST"])
def update_calendar():
    d = request.json
    cal = session.get("calendar", [])
    key = d.get("date")
    if key in cal:
        cal.remove(key)
    else:
        cal.append(key)
    session["calendar"] = cal
    return jsonify({"calendar": cal})

@app.route("/api/goal", methods=["GET"])
def get_goal():
    return jsonify({"goal": session.get("weekly_goal", 4)})

@app.route("/api/goal", methods=["POST"])
def set_goal():
    session["weekly_goal"] = int(request.json.get("goal", 4))
    return jsonify({"goal": session["weekly_goal"]})

if __name__ == "__main__":
    app.run(debug=True, port=2000)
