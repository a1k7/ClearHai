@echo off
echo ===================================================
echo 🚀 CLEAR HAI? - ONE CLICK INSTALLER
echo ===================================================

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed! Please install Python from python.org and try again.
    pause
    exit /b
)

:: 2. Check if Ollama is installed
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Ollama not found. Opening download page...
    echo 👉 Please DOWNLOAD and INSTALL Ollama, then run this script again.
    start https://ollama.com/download
    pause
    exit /b
)

:: 3. Pull the AI Model (This handles the 4GB download)
echo 🧠 Checking for AI Model (Llama 3.2)...
ollama pull llama3.2

:: 4. Install Dependencies
echo 📦 Installing Python Libraries...
pip install -r requirements.txt

:: 5. Run the App
echo ✅ Launching App...
streamlit run app.py
pause
