import sys
import pathlib
from bs4 import BeautifulSoup # Dependency from inject_analytics.py
import streamlit.web.cli as stcli

# --- START: GA4 INJECTION CODE (Merged from inject_analytics.py) ---

# 1. Your unique GA4 code
GA_ID = 'G-3T6EB0F7V1'
GA_JS = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
"""

# 2. Locate Streamlit's internal index.html file
# This path is relative to the Streamlit library installation
index_path = pathlib.Path(stcli.__file__).parent.parent / "static" / "index.html"

# 3. Read the HTML and find the <head> tag
try:
    html_content = index_path.read_text()
    soup = BeautifulSoup(html_content, features="lxml")

    # 4. Inject the GA4 script right before the closing </head> tag
    # Use a check to prevent reinjection on reruns
    if not soup.find(id='ga4-injected'):
        placeholder_div = soup.new_tag("div", id='ga4-injected')
        soup.head.append(placeholder_div)

        # Inject the actual JS tag by replacing the <head> tag
        html_content_modified = str(soup).replace("</head>", f"{GA_JS}\n</head>")

        # 5. Overwrite the Streamlit index.html file
        index_path.write_text(html_content_modified)

    print(f"GA4 Tag {GA_ID} injected successfully into Streamlit index.html.")

except FileNotFoundError:
    print("Streamlit index.html file not found. GA4 injection skipped.")
except Exception as e:
    print(f"Error during GA4 injection: {e}")
# --- END: GA4 INJECTION CODE ---


# 6. Start the main Streamlit application
sys.argv = ["streamlit", "run", "app.py"]
sys.exit(stcli.main())
