from flask import Flask, render_template, request, jsonify, session
import json, math, os, urllib.request, urllib.error

app = Flask(__name__)
app.secret_key = "IronBuddy-secret-2024"

# ── Exercise Data ──────────────────────────────────────────────────────────────
EXERCISES = {
    "Chest": [
        {"name": "Barbell Bench Press", "desc": "Lie flat, grip the barbell shoulder-width, lower to chest, press up explosively.", "diff": "intermediate", "muscles": "Pecs, Triceps", "equipment": "Barbell", "yt": "https://youtube.com/watch?v=rT7DgCr-3pg"},
        {"name": "Incline Dumbbell Press", "desc": "Targets upper chest. Set bench to 30–45°, press dumbbells from shoulder level.", "diff": "intermediate", "muscles": "Upper Pecs, Front Delts", "equipment": "Dumbbell", "yt": "https://youtube.com/watch?v=8iPEnn-ltC8"},
        {"name": "Chest Fly", "desc": "Isolation move for maximum pec stretch. Slight elbow bend.", "diff": "beginner", "muscles": "Pectorals", "equipment": "Dumbbell", "yt": "https://youtube.com/watch?v=eozdVDA78K0"},
        {"name": "Push-ups", "desc": "Zero-equipment classic. Hands shoulder-width, lower chest to floor.", "diff": "beginner", "muscles": "Pecs, Core, Triceps", "equipment": "Bodyweight", "yt": "https://youtube.com/watch?v=IODxDxX7oi4"},
        {"name": "Cable Crossover", "desc": "Pull the cables from high to low for lower pec activation.", "diff": "advanced", "muscles": "Lower Chest, Pectorals", "equipment": "Machine", "yt": "https://youtube.com/watch?v=taI4XduLpTk"},
    ],
    "Back": [
        {"name": "Pull-ups", "desc": "Overhand grip, full hang, pull until chin clears the bar cleanly.", "diff": "advanced", "muscles": "Lats, Biceps, Rhomboids", "equipment": "Bodyweight", "yt": "https://youtube.com/watch?v=eGo4IYlbE5g"},
        {"name": "Lat Pulldown", "desc": "Wide grip, lean slightly back, pull bar down to upper chest.", "diff": "beginner", "muscles": "Latissimus Dorsi", "equipment": "Machine", "yt": "https://youtube.com/watch?v=CAwf7n6Luuc"},
        {"name": "Barbell Deadlift", "desc": "Full posterior chain movement. Hip hinge, neutral spine.", "diff": "advanced", "muscles": "Hamstrings, Glutes, Erectors", "equipment": "Barbell", "yt": "https://youtube.com/watch?v=op9kVnSso6Q"},
        {"name": "Seated Cable Row", "desc": "Horizontal pull for mid-back thickness. Keep elbows close.", "diff": "beginner", "muscles": "Rhomboids, Mid-Traps", "equipment": "Machine", "yt": "https://youtube.com/watch?v=GZbfZ033f74"},
        {"name": "Dumbbell Rows", "desc": "One-arm row. Pull dumbbell to hip, squeezing lats.", "diff": "intermediate", "muscles": "Lats, Biceps", "equipment": "Dumbbell", "yt": "https://youtube.com/watch?v=pYcpY20QaE8"},
    ],
    "Legs": [
        {"name": "Barbell Squats", "desc": "Bar on traps, squat to parallel, drive knees out throughout.", "diff": "intermediate", "muscles": "Quads, Glutes, Hamstrings", "equipment": "Barbell", "yt": "https://youtube.com/watch?v=ultWZbUMPL8"},
        {"name": "Dumbbell Lunges", "desc": "Unilateral leg builder. Step forward, lower rear knee toward floor.", "diff": "beginner", "muscles": "Quads, Glutes, Hamstrings", "equipment": "Dumbbell", "yt": "https://youtube.com/watch?v=QOVaHwm-Q6U"},
        {"name": "Leg Press", "desc": "Machine compound for legs. Feet shoulder-width.", "diff": "beginner", "muscles": "Quads, Glutes", "equipment": "Machine", "yt": "https://youtube.com/watch?v=IZxyjW7MPJQ"},
        {"name": "Standing Calf Raises", "desc": "Rise fully onto toes, lower slowly for a complete stretch.", "diff": "beginner", "muscles": "Gastrocnemius, Soleus", "equipment": "Bodyweight", "yt": "https://youtube.com/watch?v=-M4-G8p8fmc"},
        {"name": "Leg Extensions", "desc": "Isolate the quads using the extension machine.", "diff": "beginner", "muscles": "Quadriceps", "equipment": "Machine", "yt": "https://youtube.com/watch?v=YyvSfVjQeL0"},
    ],
    "Shoulders": [
        {"name": "Shoulder Press", "desc": "Bar at chin, press overhead to complete extension.", "diff": "intermediate", "muscles": "All 3 Delt Heads", "equipment": "Barbell", "yt": "https://youtube.com/watch?v=2yjwXTZQDDI"},
        {"name": "Lateral Raises", "desc": "Side delt isolation. Raise dumbbells to shoulder height.", "diff": "beginner", "muscles": "Medial Delts", "equipment": "Dumbbell", "yt": "https://youtube.com/watch?v=3VcKaXpzqRo"},
        {"name": "Front Raises", "desc": "Anterior delt isolation. arms straight, lift to eye level.", "diff": "beginner", "muscles": "Anterior Delts", "equipment": "Dumbbell", "yt": "https://youtube.com/watch?v=sOoBQDGNOwE"},
        {"name": "Face Pulls", "desc": "Use cable machine with rope to target rear delts.", "diff": "intermediate", "muscles": "Rear Delts, Traps", "equipment": "Machine", "yt": "https://youtube.com/watch?v=rep-qVOkqgk"},
    ],
    "Arms": [
        {"name": "Dumbbell Bicep Curls", "desc": "Classic bicep isolation. Curl fully, squeeze hard at top.", "diff": "beginner", "muscles": "Biceps Brachii", "equipment": "Dumbbell", "yt": "https://youtube.com/watch?v=ykJmrZ5v0Oo"},
        {"name": "Tricep Dips", "desc": "Bodyweight tricep builder. Shoulders down, lower until 90°.", "diff": "intermediate", "muscles": "Triceps, Chest", "equipment": "Bodyweight", "yt": "https://youtube.com/watch?v=0326dy_-CzM"},
        {"name": "Hammer Curls", "desc": "Neutral-grip curl targeting brachialis for thicker arms.", "diff": "beginner", "muscles": "Brachialis", "equipment": "Dumbbell", "yt": "https://youtube.com/watch?v=zC3nLlEvin4"},
        {"name": "Tricep Pushdowns", "desc": "Cable extension for triceps with rope or straight bar.", "diff": "beginner", "muscles": "Triceps", "equipment": "Machine", "yt": "https://youtube.com/watch?v=2-LAMcpzODU"},
        {"name": "Barbell Curls", "desc": "Heavy mass builder for the biceps. Strict form.", "diff": "intermediate", "muscles": "Biceps", "equipment": "Barbell", "yt": "https://youtube.com/watch?v=kwG2ipFRgfo"},
    ],
    "Core": [
        {"name": "Crunches", "desc": "Basic ab flexion. Lower back pressed to floor, lift shoulder blades.", "diff": "beginner", "muscles": "Upper Abs", "equipment": "Bodyweight", "yt": "https://youtube.com/watch?v=Xyd_fa5zoEU"},
        {"name": "Hanging Leg Raises", "desc": "Advanced lower ab movement. Hang from bar, raise legs to 90°.", "diff": "advanced", "muscles": "Lower Abs", "equipment": "Bodyweight", "yt": "https://youtube.com/watch?v=JB2oyawG9KI"},
        {"name": "Cable Crunches", "desc": "Weighted crunch using a cable stack. Kneel down, pull rope to head.", "diff": "intermediate", "muscles": "Abs", "equipment": "Machine", "yt": "https://youtube.com/watch?v=2-LAMcpzODU"},
        {"name": "Russian Twists", "desc": "Oblique rotational exercise. Use a medicine ball or dumbbell.", "diff": "intermediate", "muscles": "Obliques", "equipment": "Dumbbell", "yt": "https://youtube.com/watch?v=wkD8rjkFDU"},
        {"name": "Plank", "desc": "Static core hold. Forearms or hands, body straight like a board.", "diff": "beginner", "muscles": "Core", "equipment": "Bodyweight", "yt": "https://youtube.com/watch?v=pvIjsG5Svck"},
    ],
}

# ── Yoga Data ──────────────────────────────────────────────────────────────────
YOGA = {
    "Morning Flow": [
        {"name": "Sun Salutation A", "desc": "Energizing sequence linking breath with movement. 5 rounds to awaken body and mind.", "diff": "beginner", "duration": "5 min", "yt": "https://youtube.com/watch?v=8MvQ2RzX2jU"},
        {"name": "Cat-Cow Pose", "desc": "Spinal flexion and extension. Inhale arch back, exhale round spine. Flow with breath.", "diff": "beginner", "duration": "2 min", "yt": "https://youtube.com/watch?v=kqnua4rHVVA"},
        {"name": "Downward Dog", "desc": "Inverted V-shape. Press heels toward ground, chest toward thighs. Hold and breathe.", "diff": "beginner", "duration": "3 min", "yt": "https://youtube.com/watch?v=j97ssG5k7iE"},
        {"name": "Child's Pose", "desc": "Restorative pose. Knees wide, forehead on mat, arms extended. Deep belly breathing.", "diff": "beginner", "duration": "2 min", "yt": "https://youtube.com/watch?v=qYvXsFrwTkw"},
    ],
    "Flexibility": [
        {"name": "Pigeon Pose", "desc": "Deep hip opener. Front knee at 90°, extend back leg, fold forward over front shin.", "diff": "intermediate", "duration": "3 min", "yt": "https://youtube.com/watch?v=Flm3ZW5SrY8"},
        {"name": "Seated Forward Fold", "desc": "Hamstring stretch. Sit with legs straight, hinge at hips, reach for toes.", "diff": "beginner", "duration": "3 min", "yt": "https://youtube.com/watch?v=iSOMx8jU7iY"},
        {"name": "Butterfly Pose", "desc": "Groin and inner thigh stretch. Soles of feet together, knees fall open. Breathe deeply.", "diff": "beginner", "duration": "3 min", "yt": "https://youtube.com/watch?v=YbR9EjfMxXU"},
        {"name": "Bridge Pose", "desc": "Backbend. Feet hip-width, lift hips to sky, interlace hands under back.", "diff": "beginner", "duration": "2 min", "yt": "https://youtube.com/watch?v=5lK3LqK9dG8"},
    ],
    "Strength Yoga": [
        {"name": "Warrior I", "desc": "Power pose. Front knee bent 90°, back leg straight, arms reaching overhead. Strong foundation.", "diff": "intermediate", "duration": "2 min", "yt": "https://youtube.com/watch?v=NQhrfydG5OQ"},
        {"name": "Warrior II", "desc": "Open-hip warrior. Arms parallel to floor, gaze over front hand. Build leg strength.", "diff": "intermediate", "duration": "2 min", "yt": "https://youtube.com/watch?v=xlCEq5q1Xg4"},
        {"name": "Plank", "desc": "Core stability. Shoulders over wrists, body in straight line. Hold with steady breath.", "diff": "intermediate", "duration": "2 min", "yt": "https://youtube.com/watch?v=pvIjsG5Svck"},
        {"name": "Chair Pose", "desc": "Leg burner. Sit back into imaginary chair, arms reaching up. Thighs parallel to floor.", "diff": "intermediate", "duration": "2 min", "yt": "https://youtube.com/watch?v=_2i4EP1qK40"},
    ],
    "Relaxation": [
        {"name": "Legs Up Wall", "desc": "Restorative inversion. Legs vertical against wall, hips supported. Calms nervous system.", "diff": "beginner", "duration": "5 min", "yt": "https://youtube.com/watch?v=EqTjvOqPqD0"},
        {"name": "Supine Twist", "desc": "Spinal twist. Knees to one side, arms in T-shape. Releases lower back tension.", "diff": "beginner", "duration": "3 min", "yt": "https://youtube.com/watch?v=hiia0f_5z4A"},
        {"name": "Savasana", "desc": "Final relaxation. Lie flat on back, arms by sides. Complete surrender. Essential practice.", "diff": "beginner", "duration": "5 min", "yt": "https://youtube.com/watch?v=8GPKocOY57Y"},
    ],
}

# ── Home Workouts (No Equipment) ───────────────────────────────────────────────
HOME_WORKOUTS = {
    "Full Body HIIT": [
        {"name": "Jumping Jacks", "desc": "Classic cardio. Jump feet wide, arms overhead. Keep core tight. 45 seconds on.", "diff": "beginner", "reps": "45 sec", "yt": "https://youtube.com/watch?v=iSSAk4XCsRA"},
        {"name": "Burpees", "desc": "Full body explosive. Drop to plank, push-up, jump feet in, leap up. Intense cardio.", "diff": "intermediate", "reps": "15 reps", "yt": "https://youtube.com/watch?v=auBLPXO8Fww"},
        {"name": "Mountain Climbers", "desc": "Core + cardio. Plank position, alternate driving knees to chest. Fast pace.", "diff": "beginner", "reps": "30 sec", "yt": "https://youtube.com/watch?v=nmwgirgXLYM"},
        {"name": "Jump Squats", "desc": "Explosive legs. Squat down, explode up into jump. Soft landing, immediate next rep.", "diff": "intermediate", "reps": "20 reps", "yt": "https://youtube.com/watch?v=Azl5tkCzDcc"},
        {"name": "High Knees", "desc": "Running in place. Drive knees to hip height, pump arms. Cardio blast.", "diff": "beginner", "reps": "30 sec", "yt": "https://youtube.com/watch?v=8opcQdC-V-U"},
    ],
    "Core Crusher": [
        {"name": "Crunches", "desc": "Basic ab flexion. Lower back pressed to floor, lift shoulder blades. Controlled.", "diff": "beginner", "reps": "20 reps", "yt": "https://youtube.com/watch?v=Xyd_fa5zoEU"},
        {"name": "Plank", "desc": "Static core hold. Forearms or hands, body straight. Squeeze glutes, breathe.", "diff": "beginner", "reps": "60 sec", "yt": "https://youtube.com/watch?v=pvIjsG5Svck"},
        {"name": "Russian Twists", "desc": "Oblique exercise. Seated, lean back, twist torso side to side. Feet up for challenge.", "diff": "beginner", "reps": "30 reps", "yt": "https://youtube.com/watch?v=wkD8rjkFDU"},
        {"name": "Leg Raises", "desc": "Lower abs. Lying on back, legs straight, lift to 90°. Control the descent.", "diff": "intermediate", "reps": "15 reps", "yt": "https://youtube.com/watch?v=JB2oyawG9KI"},
        {"name": "Bicycle Crunches", "desc": "Obliques + rectus abdominis. Alternate elbow to opposite knee. Slow and controlled.", "diff": "beginner", "reps": "30 reps", "yt": "https://youtube.com/watch?v=9FGilxCbdz8"},
    ],
    "Upper Body": [
        {"name": "Push-ups", "desc": "Classic chest/triceps. Body straight, lower to ground, press back up. Many variations.", "diff": "beginner", "reps": "15 reps", "yt": "https://youtube.com/watch?v=IODxDxX7oi4"},
        {"name": "Diamond Push-ups", "desc": "Triceps focus. Hands form diamond under chest. Elbows tuck to sides.", "diff": "intermediate", "reps": "10 reps", "yt": "https://youtube.com/watch?v=J0DnG1_S92g"},
        {"name": "Tricep Dips (Chair)", "desc": "Use sturdy chair. Hands on edge, lower body, press up. Keep elbows back.", "diff": "beginner", "reps": "15 reps", "yt": "https://youtube.com/watch?v=6kALZikXxLc"},
        {"name": "Inchworms", "desc": "Dynamic warm-up. Walk hands to plank, walk back to feet. Core and shoulder engagement.", "diff": "beginner", "reps": "10 reps", "yt": "https://youtube.com/watch?v=V5x9HnGfB9A"},
    ],
    "Lower Body": [
        {"name": "Air Squats", "desc": "Bodyweight squats. Feet shoulder-width, hips back and down. Keep chest up.", "diff": "beginner", "reps": "25 reps", "yt": "https://youtube.com/watch?v=C_VtOYc6j5c"},
        {"name": "Lunges", "desc": "Split squat. Step forward, drop back knee toward floor. Alternate legs.", "diff": "beginner", "reps": "20 reps", "yt": "https://youtube.com/watch?v=L8fvyBHUPew"},
        {"name": "Glute Bridges", "desc": "Hip thrust on floor. Lift hips, squeeze glutes at top. No arching back.", "diff": "beginner", "reps": "20 reps", "yt": "https://youtube.com/watch?v=QQI8bP4jnjk"},
        {"name": "Calf Raises", "desc": "Rise onto toes, lower slowly. Do on step for extra range. Hold wall for balance.", "diff": "beginner", "reps": "30 reps", "yt": "https://youtube.com/watch?v=gwLzBJYoWlI"},
        {"name": "Wall Sit", "desc": "Static leg burner. Back against wall, knees at 90°. Hold and embrace the burn.", "diff": "beginner", "reps": "45 sec", "yt": "https://youtube.com/watch?v=-cdph8hv0O0"},
    ],
    "Cardio Blast": [
        {"name": "Butt Kicks", "desc": "Running in place, heels touch glutes. Pump arms, quick feet.", "diff": "beginner", "reps": "45 sec", "yt": "https://youtube.com/watch?v=8opcQdC-V-U"},
        {"name": "Skaters", "desc": "Lateral bounds. Leap side to side, touching floor. Like speed skater motion.", "diff": "beginner", "reps": "30 sec", "yt": "https://youtube.com/watch?v=1C7v29PCZyw"},
        {"name": "Star Jumps", "desc": "Explosive X-jumps. Jump spreading arms and legs wide. Land softly.", "diff": "intermediate", "reps": "20 reps", "yt": "https://youtube.com/watch?v=1C7v29PCZyw"},
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

def generate_diet_local(name, gender, user_goal, age, weight, height, diet):
    """Generate personalized diet plan locally without AI API."""
    bmi = calc_bmi(weight, height)
    
    # Calculate BMR (Mifflin-St Jeor Equation)
    if gender == "Female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    
    tdee = bmr * 1.3 # moderately active assumption
    
    # Determine goal and adjust calories based on user_goal
    if user_goal == "Weight Loss":
        goal = "weight_loss" if bmi < 30 else "fat_loss"
        target_calories = int(tdee - 500)
        protein_percent = 40
        carb_percent = 30
        fat_percent = 30
    elif user_goal == "Muscle Gain":
        goal = "muscle_gain" if bmi < 25 else "weight_gain"
        target_calories = int(tdee + 300)
        protein_percent = 35
        carb_percent = 40
        fat_percent = 25
    else:
        goal = "maintenance"
        target_calories = int(tdee)
        protein_percent = 30
        carb_percent = 40
        fat_percent = 30

    # Ensure reasonable bounds
    target_calories = max(1200, min(4000, target_calories))
    
    # Calculate macros based on goal
    protein_g = int((target_calories * protein_percent / 100) / 4)
    carbs_g = int((target_calories * carb_percent / 100) / 4)
    fat_g = int((target_calories * fat_percent / 100) / 9)
    water_liters = round(weight * 0.035, 1)  # ~35ml per kg
    
    # Personalized meal plans based on goal and diet type
    meals_db = get_personalized_meals(goal, diet, target_calories)
    
    # Goal-specific tips
    goal_tips = {
        "weight_gain": "Focus on calorie-dense foods. Eat every 2-3 hours. Include healthy fats like nuts, avocado, and olive oil. Progressive strength training 3-4x/week.",
        "muscle_gain": "Prioritize protein intake (1.6-2g per kg body weight). Time carbs around workouts. Include compound exercises. Sleep 7-9 hours for recovery.",
        "maintenance": "Maintain balanced macronutrients. Listen to hunger cues. Stay consistent with meal timing. Regular health checkups recommended.",
        "weight_loss": "High protein to preserve muscle mass. Focus on whole foods. Control portion sizes. Include both cardio and strength training.",
        "fat_loss": "Very high protein intake. Minimize processed carbs and sugars. Time carbs around workouts only. Increase daily activity and NEAT."
    }
    
    return {
        "totalCalories": target_calories,
        "waterLiters": water_liters,
        "proteinG": protein_g,
        "carbsG": carbs_g,
        "fatG": fat_g,
        "goal": user_goal,
        "meals": meals_db,
        "tip": f"Hey {name}, " + goal_tips.get(goal, "Eat whole foods, stay hydrated, and maintain consistency over perfection.")
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
    bmi = calc_bmi(weight, height)
    rules = {
        "Veg":     "STRICTLY vegetarian. No meat, fish, or eggs. Include dairy and plant proteins.",
        "Non-Veg": "Can include chicken, fish, eggs, and dairy.",
        "Jain":    "STRICTLY Jain. NO onion, garlic, potato, or any root vegetables. No meat, fish, eggs. Use lentils, beans, dairy, above-ground vegetables only.",
    }
    prompt = f"""You are a certified nutritionist. Generate a personalized daily diet plan in JSON format.

User: {name}, Gender: {gender}, Goal: {user_goal}, Age: {age}yr, Weight: {weight}kg, Height: {height}cm, BMI: {bmi}, Diet: {diet}
Rules: {rules[diet]}

Respond ONLY with valid JSON (no markdown):
{{
  "totalCalories": number,
  "waterLiters": number,
  "proteinG": number,
  "carbsG": number,
  "fatG": number,
  "meals": {{
    "breakfast":    {{"name":"","description":"","calories":0}},
    "morningSnack": {{"name":"","description":"","calories":0}},
    "lunch":        {{"name":"","description":"","calories":0}},
    "eveningSnack": {{"name":"","description":"","calories":0}},
    "dinner":       {{"name":"","description":"","calories":0}}
  }},
  "tip": "one personalized tip"
}}"""
    try:
        raw = call_claude(prompt)
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(raw)
    except Exception:
        # Fallback to local generator if API fails
        return generate_diet_local(name, gender, user_goal, age, weight, height, diet)

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
    return jsonify({"day": day, "exercises": EXERCISES.get(day, [])})

@app.route("/api/yoga-plan", methods=["GET"])
def yoga_plan():
    flow = request.args.get("flow", "Morning Flow")
    return jsonify({"flow": flow, "poses": YOGA.get(flow, [])})

@app.route("/api/home-workout", methods=["GET"])
def home_workout():
    category = request.args.get("category", "Full Body HIIT")
    return jsonify({"category": category, "exercises": HOME_WORKOUTS.get(category, [])})

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
