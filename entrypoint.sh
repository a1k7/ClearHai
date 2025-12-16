#!/bin/bash

# 1. Run the script that modifies Streamlit's internal HTML (the GA4 fix).
# The 'python -B' flag prevents .pyc files from being created.
python -B inject_analytics.py

# 2. Start the main Streamlit application.
streamlit run app.py
