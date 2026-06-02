"""
IronBuddy Database Manager
Handles all database operations for exercises, users, and tracking.
"""

import sqlite3
import json
import os
from contextlib import contextmanager

# Database path - use /tmp for Vercel serverless environment
if os.environ.get('VERCEL'):
    DB_PATH = '/tmp/ironbuddy.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'ironbuddy.db')

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize the database with all required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Exercises table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                muscles TEXT NOT NULL,
                equipment TEXT NOT NULL,
                youtube_url TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Yoga poses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS yoga_poses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                duration TEXT NOT NULL,
                youtube_url TEXT,
                video_filename TEXT,
                flow_category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Home workouts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS home_workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                reps TEXT NOT NULL,
                youtube_url TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                age INTEGER NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                diet_preference TEXT NOT NULL,
                activity_level TEXT DEFAULT 'Moderately Active',
                workout_type TEXT DEFAULT 'Mixed Training',
                body_fat REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Diet plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                goal TEXT NOT NULL,
                total_calories INTEGER NOT NULL,
                protein_g INTEGER NOT NULL,
                carbs_g INTEGER NOT NULL,
                fat_g INTEGER NOT NULL,
                water_liters REAL NOT NULL,
                meals_json TEXT NOT NULL,
                tip TEXT NOT NULL,
                protein_per_kg REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Workout logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                duration_minutes INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Calendar tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, date)
            )
        ''')
        
        # Weekly goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                days_per_week INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        print("✅ Database initialized successfully!")

def populate_exercises():
    """Populate exercises table with existing data."""
    from app import EXERCISES
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM exercises')
        
        for category, exercises in EXERCISES.items():
            for exercise in exercises:
                cursor.execute('''
                    INSERT OR REPLACE INTO exercises 
                    (name, description, difficulty, muscles, equipment, youtube_url, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    exercise['name'],
                    exercise['desc'],
                    exercise['diff'],
                    exercise['muscles'],
                    exercise['equipment'],
                    exercise['yt'],
                    category
                ))
        
        print(f"✅ Populated {sum(len(ex) for ex in EXERCISES.values())} exercises!")

def populate_yoga():
    """Populate yoga_poses table with existing data."""
    from app import YOGA
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM yoga_poses')
        
        for flow_category, poses in YOGA.items():
            for pose in poses:
                cursor.execute('''
                    INSERT OR REPLACE INTO yoga_poses 
                    (name, description, difficulty, duration, youtube_url, video_filename, flow_category)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pose['name'],
                    pose['desc'],
                    pose['diff'],
                    pose['duration'],
                    pose.get('yt', ''),
                    pose.get('video', ''),
                    flow_category
                ))
        
        print(f"✅ Populated {sum(len(poses) for poses in YOGA.values())} yoga poses!")

def populate_home_workouts():
    """Populate home_workouts table with existing data."""
    from app import HOME_WORKOUTS
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM home_workouts')
        
        for category, workouts in HOME_WORKOUTS.items():
            for workout in workouts:
                cursor.execute('''
                    INSERT OR REPLACE INTO home_workouts 
                    (name, description, difficulty, reps, youtube_url, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    workout['name'],
                    workout['desc'],
                    workout['diff'],
                    workout['reps'],
                    workout['yt'],
                    category
                ))
        
        print(f"✅ Populated {sum(len(w) for w in HOME_WORKOUTS.values())} home workouts!")

def get_exercises(category=None):
    """Get exercises from database, optionally filtered by category."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT * FROM exercises WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT * FROM exercises')
        
        exercises = cursor.fetchall()
        return [
            {
                'name': row['name'],
                'desc': row['description'],
                'diff': row['difficulty'],
                'muscles': row['muscles'],
                'equipment': row['equipment'],
                'yt': row['youtube_url']
            }
            for row in exercises
        ]

def get_yoga_poses(flow_category=None):
    """Get yoga poses from database, optionally filtered by flow."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if flow_category:
            cursor.execute('SELECT * FROM yoga_poses WHERE flow_category = ?', (flow_category,))
        else:
            cursor.execute('SELECT * FROM yoga_poses')
        
        poses = cursor.fetchall()
        return [
            {
                'name': row['name'],
                'desc': row['description'],
                'diff': row['difficulty'],
                'duration': row['duration'],
                'yt': row['youtube_url'],
                'video': row['video_filename']
            }
            for row in poses
        ]

def get_home_workouts(category=None):
    """Get home workouts from database, optionally filtered by category."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT * FROM home_workouts WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT * FROM home_workouts')
        
        workouts = cursor.fetchall()
        return [
            {
                'name': row['name'],
                'desc': row['description'],
                'diff': row['difficulty'],
                'reps': row['reps'],
                'yt': row['youtube_url']
            }
            for row in workouts
        ]

def save_user(name, gender, age, weight, height, diet, activity_level="Moderately Active", workout_type="Mixed Training", body_fat=None):
    """Save or update user in database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (name, gender, age, weight, height, diet_preference, activity_level, workout_type, body_fat, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (name, gender, age, weight, height, diet, activity_level, workout_type, body_fat))
        
        user_id = cursor.lastrowid
        return user_id

def get_user(name):
    """Get user from database by name."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'name': row['name'],
                'gender': row['gender'],
                'age': row['age'],
                'weight': row['weight'],
                'height': row['height'],
                'diet': row['diet_preference'],
                'activity_level': row['activity_level'],
                'workout_type': row['workout_type'],
                'body_fat': row['body_fat']
            }
        return None

def save_diet_plan(user_id, goal, calories, protein, carbs, fat, water, meals, tip, protein_per_kg):
    """Save diet plan for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO diet_plans 
            (user_id, goal, total_calories, protein_g, carbs_g, fat_g, water_liters, meals_json, tip, protein_per_kg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, goal, calories, protein, carbs, fat, water, json.dumps(meals), tip, protein_per_kg))
        
        return cursor.lastrowid

def log_workout(user_id, exercise_name, category, date, duration=None, notes=None):
    """Log a workout for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO workout_logs 
            (user_id, exercise_name, category, date, duration_minutes, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, exercise_name, category, date, duration, notes))
        
        return cursor.lastrowid

def get_workout_logs(user_id, limit=50):
    """Get workout logs for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM workout_logs 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        return cursor.fetchall()

if __name__ == "__main__":
    # Initialize database and populate with data
    print("🗄️  Initializing IronBuddy Database...")
    init_database()
    populate_exercises()
    populate_yoga()
    populate_home_workouts()
    print("\n✨ Database setup complete!")

# Auto-initialize database for Vercel
try:
    init_database()
    populate_exercises()
    populate_yoga()
    populate_home_workouts()
except Exception as e:
    print(f"Database initialization error: {e}")
