import subprocess
import sys
import os
import streamlit.web.cli as stcli

# 1. Install necessary dependencies (BeautifulSoup)
print("Installing beautifulsoup4 dependency...")
# Use pip to install the required library for the injection script
# The 'check=True' ensures that pip installation must succeed
subprocess.run([sys.executable, "-m", "pip", "install", "beautifulsoup4"], check=True)

# 2. Run the GA4 injection script
print("Running GA4 injection script...")
# Use the Python interpreter to execute the injection script
subprocess.run([sys.executable, "inject_analytics.py"], check=True)

print("GA4 injection successful. Starting Streamlit app...")

# 3. Launch the Streamlit app using the internal CLI commands
# This is the most robust way to launch Streamlit from a Python process
sys.argv = ["streamlit", "run", "app.py"]
sys.exit(stcli.main())
