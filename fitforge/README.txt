
 ⚡ FITFORGE - FITNESS WEB APP
================================

HOW TO RUN
----------

WINDOWS:
  Double-click  →  START_WINDOWS.bat

MAC / LINUX:
  Open terminal in this folder and run:
  chmod +x START_MAC_LINUX.sh
  ./START_MAC_LINUX.sh

MANUAL (any OS):
  1. pip install flask
  2. python app.py
  3. Open browser → http://localhost:5000


FOR AI DIET PLAN FEATURE
-------------------------
Set your Anthropic API key before running:

  Windows:   set ANTHROPIC_API_KEY=your_key_here
  Mac/Linux: export ANTHROPIC_API_KEY=your_key_here

Get a free API key at: https://console.anthropic.com


FILE STRUCTURE
--------------
IronBuddy/
├── app.py                  ← Flask backend
├── requirements.txt        ← Dependencies
├── START_WINDOWS.bat       ← Windows launcher
├── START_MAC_LINUX.sh      ← Mac/Linux launcher
├── templates/
│   └── index.html          ← Main HTML page
└── static/
    ├── css/
    │   └── style.css       ← All styles
    └── js/
        └── app.js          ← All JavaScript


FEATURES
--------
  ✅ Onboarding form (age, weight, height, diet)
  ✅ AI-powered diet plan (Veg / Non-Veg / Jain)
  ✅ BMI calculator with status
  ✅ Macro breakdown (protein, carbs, fat, water)
  ✅ Water intake tracker
  ✅ 5 workout splits with YouTube links
  ✅ Rest timer
  ✅ Monthly calendar tracker
  ✅ Streak counter
  ✅ Weekly goal tracker
  ✅ Profile page
  ✅ Mobile responsive + dark mode

