import subprocess
import sys
import os

# 1. Run the GA4 injection script first
# We use the same python executable to ensure environment is correct
print("Running GA4 injection script...")

# We use the full path to the python executable and the script name
subprocess.run([sys.executable, "inject_analytics.py"], check=True)

print("GA4 injection successful. Starting Streamlit app...")

# 2. Start the main Streamlit application
# The 'streamlit' command is available in the environment's path
# We start the app, replacing the current process (the runner script)
os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", "app.py"])
