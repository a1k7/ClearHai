import pathlib
from bs4 import BeautifulSoup
import streamlit as st

# 1. Your unique GA4 code (from Screenshot 2.28.59 PM.jpg)
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
index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"

# 3. Read the HTML and find the <head> tag
soup = BeautifulSoup(index_path.read_text(), features="lxml")

# 4. Inject the GA4 script right before the closing </head> tag
if not soup.find(id='ga4-injected'): # Check if already injected
    # Create a placeholder <div> to prevent reinjection on rerun
    placeholder_div = soup.new_tag("div", id='ga4-injected')
    soup.head.append(placeholder_div)

    # Inject the actual JS tag by replacing the <head> tag
    html_content = str(soup).replace("</head>", f"{GA_JS}\n</head>")

    # 5. Overwrite the Streamlit index.html file
    index_path.write_text(html_content)

print(f"GA4 Tag {GA_ID} injected successfully into Streamlit index.html.")

# You must call this function before running your app
# If running locally, you must run inject_analytics.py first.
