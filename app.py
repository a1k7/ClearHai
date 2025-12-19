import streamlit as st
import os
import uuid
from groq import Groq

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Pocket Lawyer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS STYLING ---
st.markdown("""
<style>
    /* 1. Main Background */
    .stApp {
        background-color: #131314;
        color: #E3E3E3;
    }

    /* 2. Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1E1F20;
    }

    /* 3. TEXT STYLES */
    .welcome-text {
        background: linear-gradient(90deg, #4b90ff, #ff5546);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    
    .sub-text {
        color: #5f6368;
        font-size: 1.5rem;
        font-weight: 500;
        margin-top: -10px;
        margin-bottom: 40px;
    }

    .gemini-header {
        background: linear-gradient(90deg, #4b90ff, #ff5546);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 5px;
    }

    /* 4. Suggestion Cards */
    .stButton button {
        background-color: #1E1F20 !important;
        border: 1px solid #333 !important;
        color: #E3E3E3 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        text-align: left !important;
        height: 100px !important;
    }
    .stButton button:hover {
        background-color: #2D2E30 !important;
        border-color: #4b90ff !important;
    }

    /* 5. Chat Input (Floating) */
    .stChatInput {
        position: fixed;
        bottom: 30px;
        width: 70%;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
    }
    
    .stChatInput > div > div {
        background-color: #1E1F20 !important;
        border: none !important;
        border-radius: 25px;
        color: white !important;
    }

    /* 6. Visibility Controls */
    [data-testid="stToolbar"], [data-testid="stDecoration"], footer {display: none !important;}
    [data-testid="stHeader"] {background: transparent !important; visibility: visible !important;}
    
    [data-testid="stSidebarCollapsedControl"] {
        color: white !important;
        background-color: rgba(255,255,255,0.1);
        border-radius: 5px;
        display: block !important;
        visibility: visible !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC ENGINE (UPDATED WITH SECTION 154 & 119 RULES) ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"])

# >>> UPDATED KNOWLEDGE BASE <<<
KNOWLEDGE_BASE = """
[ROLE]
- You are 'Clear Hai', an expert Indian Legal Consultant.
- JURISDICTION: INDIA ONLY.

[TOPIC: RENT AGREEMENTS & LEASES]
- **Core Myth Buster:** There is NO legal rule mandating an 11-month period.
  - *Reality:* People choose 11 months to avoid "Mandatory Registration" under Section 17 of the Registration Act, 1908 (required only for leases of 12 months or more).
- **Registration Rule:** - < 12 Months: Notarized is enough (Optional Registration).
  - 12+ Months: MUST be Registered at Sub-Registrar office.
- **Applicable Laws (State Specific):**
  - NEVER cite a "Central Rent Control Act". Rent is a STATE subject.
  - Maharashtra: Maharashtra Rent Control Act, 1999.
  - Delhi: Delhi Rent Control Act, 1958.
  - **Model Tenancy Act 2021:** This is ADVISORY only. It is NOT law unless the specific state has notified it.
- **Security Deposit:** - No central limit. Depends on State Act or Contract. 
  - (e.g., Model Act suggests 2 months, but this is not binding in all states yet).
[CRITICAL LEGAL RULES]
1. **Loan Default & Criminal Law (BNS vs NI Act)**:
   - **CORE RULE**: Loan default is CIVIL, not CRIMINAL. Police cannot arrest you for simple non-payment.
   - **BNS Clarification**: 
     - **BNS Section 138** = Abduction (Kidnapping). 
     - **NI Act Section 138** = Cheque Bounce.
     - *Warning*: If an agent cites "BNS 138" for a loan, they are using intimidation tactics. Clarify this distinction to the user immediately.
   - **Remedy**: File complaint on **RBI CMS Portal** (cms.rbi.org.in) for harassment. Do not suggest Banking Ombudsman for criminal threats.
   - **Bail**: If a Cheque Bounce case (NI Act 138) is filed, it is bailable.

2. **Tax Demand (Section 143(1))**:
   - Primary Remedy: Rectification u/s 154.
   - Secondary: Condonation u/s 119(2)(b).

3. **Property Disputes**:
   - Never advise suing for black money. 
   - Use "Cancellation of Sale Deed" for fraud/wrong description cases.
[TOPIC: RECOVERY AGENT HARASSMENT]
- Violation: Refusing to identify the Agency/Bank violates RBI 'Fair Practices Code'.
- Complaint Forums: 
  1. RBI CMS Portal (cms.rbi.org.in).
  2. TRAI DND (1909).
  (Note: National Consumer Helpline is advisory only).

[TOPIC: DEC 2025 TAX ALERTS]
- 'Significant Mismatch' Notices: Deadline Dec 31, 2025.
- Action: Submit feedback on Compliance Portal. Do NOT revise blindly.
[CRITICAL LEGAL RULES]
1. **Tax Demand (Section 143(1))**:
   - Primary Remedy: **Rectification u/s 154**. (Mistake apparent from record).
   - Secondary: Condonation u/s 119(2)(b) (Discretionary).
   - Writ Petition: Last resort only.

2. **Old Property Disputes (Builder Fraud/Wrong Deed)**:
   - **WARNING**: Do NOT advise suing for "Unpaid Black Money". Courts will dismiss this as illegal consideration.
   - **STRATEGY**: File Suit for **Cancellation of Sale Deed** based on FRAUD (Wrong Area/Survey No).
   - **LIMITATION**: Suit must be filed within 3 years of *knowledge* of fraud. User must plead they discovered the discrepancy recently.
   - **Specific Performance**: Impossible after 3 years. Do not suggest it.

3. **Section 80E (Education Loan)**: 
   - Claimant MUST be a 'Borrower' or 'Co-Borrower'. Paying EMI is NOT enough.

4. **Employment Bonds**:
   - Void u/s 27 Contract Act unless for *actual* training costs.
"""

def get_ai_response(query, language):
    lang_instruction = f"OUTPUT LANGUAGE: {language}. Answer ONLY in {language}."
    if language == "Hindi" or language == "Marathi":
        lang_instruction += " Use Devanagari script."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"{KNOWLEDGE_BASE}\n{lang_instruction}"}, 
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except:
        return "Connection Error."

def generate_title(text):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Summarize in 3 English words: {text}"}]
        )
        return completion.choices[0].message.content.strip().replace('"','')
    except:
        return "New Chat"

# --- 4. SESSION ---
if "chats" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.chats = {new_id: {"title": "New Chat", "messages": []}}
    st.session_state.current_chat_id = new_id

def create_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

# --- 5. SIDEBAR (History) ---
with st.sidebar:
    st.markdown("### ≡ &nbsp; Pocket Lawyer", unsafe_allow_html=True)
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        create_chat()
        st.rerun()
    st.markdown("---")
    st.caption("Recents")
    chat_ids = list(st.session_state.chats.keys())
    for c_id in reversed(chat_ids):
        chat_data = st.session_state.chats[c_id]
        if st.button(f"💬 {chat_data['title']}", key=c_id, use_container_width=True):
            st.session_state.current_chat_id = c_id
            st.rerun()

# --- 6. MAIN DISPLAY ---

# TOP BAR LANGUAGE SELECTOR
col_spacer, col_lang = st.columns([6, 1])
with col_lang:
    selected_language = st.selectbox(
        "Language", 
        ["English", "Hindi", "Marathi"], 
        label_visibility="collapsed"
    )

current_id = st.session_state.current_chat_id
current_history = st.session_state.chats[current_id]["messages"]

# A. WELCOME SCREEN
if not current_history:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="welcome-text">Hello, Citizen.</h1>', unsafe_allow_html=True)
    st.markdown(f'<h3 class="sub-text">I can help you in {selected_language}.</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    prompt_to_run = None
    
    with col1:
        if st.button("📢  **Got a Tax Notice?**\n\nHandle 'Significant Mismatch' alerts.", use_container_width=True):
            prompt_to_run = "I received a 'Significant Mismatch' tax notice. What do I do?"
        if st.button("🎓  **Education Loan (80E)**\n\nCan my father claim the deduction?", use_container_width=True):
            prompt_to_run = "Can my father claim Section 80E deduction for my education loan?"
            
    with col2:
        if st.button("🤬  **Recovery Harassment**\n\nAgents calling for unknown loan.", use_container_width=True):
            prompt_to_run = "Recovery agents are harassing me for a loan I didn't take. What are my rights?"
        if st.button("🏠  **Rent Agreements**\n\nIs the 11-month rule mandatory?", use_container_width=True):
            prompt_to_run = "Is it mandatory to make a rent agreement for only 11 months?"

    if prompt_to_run:
        st.session_state.chats[current_id]["messages"].append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)
        with st.chat_message("assistant"):
            with st.spinner(f"Checking Legal Rules in {selected_language}..."):
                response = get_ai_response(prompt_to_run, selected_language)
                st.markdown(response)
        st.session_state.chats[current_id]["messages"].append({"role": "assistant", "content": response})
        st.session_state.chats[current_id]["title"] = generate_title(prompt_to_run)
        st.rerun()

# B. CHAT HISTORY
else:
    st.markdown('<div class="gemini-header">Pocket Lawyer</div>', unsafe_allow_html=True)
    st.caption("Powered by Clear Hai Logic Engine")
    
    for msg in current_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# C. INPUT BAR
if prompt := st.chat_input(f"Ask in {selected_language}..."):
    st.session_state.chats[current_id]["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Thinking in {selected_language}..."):
            response = get_ai_response(prompt, selected_language)
            st.markdown(response)
    
    st.session_state.chats[current_id]["messages"].append({"role": "assistant", "content": response})
    
    if len(st.session_state.chats[current_id]["messages"]) == 2:
        st.session_state.chats[current_id]["title"] = generate_title(prompt)
        st.rerun()
