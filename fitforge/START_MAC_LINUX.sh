#!/bin/bash
echo ""
echo " ================================"
echo "  IronBuddy - Starting App..."
echo " ================================"
echo ""
echo "[1/3] Installing Flask..."
pip install flask
echo ""
echo "[2/3] NOTE: For AI Diet Plan, set your API key:"
echo "      export ANTHROPIC_API_KEY=your_key_here"
echo ""
echo "[3/3] Starting IronBuddy server..."
echo ""
echo " Open your browser: http://localhost:5000"
echo ""
python app.py
