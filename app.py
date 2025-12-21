import streamlit as st
import os
import uuid
import urllib.parse
from groq import Groq
import datetime

def get_tax_filing_context():
    """
    Calculates the tax filing status dynamically based on today's date.
    Works for any year.
    """
    today = datetime.date.today()
    current_year = today.year
    
    # Context: We are assuming the user wants to file for the IMMEDIATE PAST Financial Year (FY)
    # Example: In Dec 2025, we are filing for FY 2024-25 (AY 2025-26)
    
    # If today is Jan-Mar, we are still in the previous calendar year's cycle logic roughly
    # But let's simplify for standard filing cycle (April to March)
    
    # Target Assessment Year (AY) is usually Current Year + 1 (if currently in FY)
    # But usually users ask about the COMPLETED FY.
    # Let's target the "Relevant AY" which ends on March 31 of next year.
    
    # Logic for the MOST RECENT completed FY:
    relevant_ay_end_year = current_year + 1 if today.month > 3 else current_year
    deadline_normal = datetime.date(current_year, 7, 31)
    deadline_belated = datetime.date(current_year, 12, 31)
    
    status_msg = ""
    
    # Check Status for IMMEDIATE PAST YEAR
    if today <= deadline_normal:
        status_msg = f"Current Status: **Normal Filing Window** (Ends July 31, {current_year}). No Penalty."
    elif today <= deadline_belated:
        status_msg = f"Current Status: **Belated Filing Window** (Ends Dec 31, {current_year}). Penalty: ₹1,000 (if Income < ₹5L) or ₹5,000."
    else:
        status_msg = f"Current Status: **Window Closed**. Only ITR-U (Updated Return) is possible."
        
    return f"Today is {today.strftime('%B %d, %Y')}. {status_msg}"

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

    /* 6. WhatsApp Share Button Style */
    .whatsapp-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #25D366;
        color: white !important;
        padding: 8px 16px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 10px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    .whatsapp-btn:hover {
        transform: scale(1.05);
        background-color: #128C7E;
        color: white !important;
    }

    /* 7. Visibility Controls */
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

# --- 3. LOGIC ENGINE ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"])

# >>> UPDATED KNOWLEDGE BASE <<<
KNOWLEDGE_BASE = """
[ROLE]
- You are 'Clear Hai', an expert Indian Legal Consultant.
- JURISDICTION: INDIA ONLY.
- You are 'Pocket Lawyer', India's most aggressive and strategic AI Legal Assistant.
- Your goal is NOT just to inform, but to PROTECT and ATTACK legally.
- JURISDICTION: INDIA ONLY (Cite BNS 2023, RBI Circulars, IT Act).
[INSTRUCTION: HOW TO ANSWER]
- Do NOT give generic advice ("File a complaint").
- GIVE ACTIONABLE TOOLS: Templates, Step-by-Step Timelines, and Exact Legal Sections.
- Structure your answer with bold headers.
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
4. **Tone**:
   - Empathetic but fierce. "Don't panic, here is your weapon."
2. **Tax Demand (Section 143(1))**:
   - Primary Remedy: Rectification u/s 154.
   - Secondary: Condonation u/s 119(2)(b).

3. **Property Disputes**:
   - Never advise suing for black money. 
   - Use "Cancellation of Sale Deed" for fraud/wrong description cases.
2. **Merchandise & IP Rights (F1/Fan Gear)**:
   - **NO "Loopholes"**: Do NOT use the word "loophole". Use "Lawful Alternatives".
   - **Passing Off**: Even without a registered trademark, if a design confuses a buyer into thinking it's "Official Merchandise", it is illegal Passing Off.
   - **Parody/Fair Dealing**: Does NOT apply to commercial sale of goods (T-shirts/Posters). Commercial gain negates fair dealing defense in India.
   - **Strategy**: Use generic art styles. Avoid official logos, sponsor names, and likeness rights (faces of drivers).
[TOPIC: RECOVERY AGENT HARASSMENT]
- Violation: Refusing to identify the Agency/Bank violates RBI 'Fair Practices Code'.
- Complaint Forums: 
  1. RBI CMS Portal (cms.rbi.org.in).
  2. TRAI DND (1909).
  (Note: National Consumer Helpline is advisory only).
1. **Inheritance (Son's Claim)**:
   - **Hindu Law (Hindu Succession Act, 1956)**: Son is a **Class I Heir**.
   - **Ancestral Property**: Son has a birthright (Coparcener). Father CANNOT exclude son via Will.
   - **Self-Acquired Property**: Father has 100% control. If Father leaves a valid **Will** giving property to someone else, Son gets NOTHING. Son only inherits if Father dies "Intestate" (without a Will).
   - **Daughters**: Have equal rights as sons (2005 Amendment).
   - **Muslim Law**: Son is a residuary/sharer. Testamentary succession (Will) is limited to 1/3rd of property.
   - **Christian/Parsi**: Governed by Indian Succession Act, 1925.
[TOPIC: DEC 2025 TAX ALERTS]
- 'Significant Mismatch' Notices: Deadline Dec 31, 2025.
- Action: Submit feedback on Compliance Portal. Do NOT revise blindly.
5. **Year-End Delivery Scams (AI Phishing)**:
   - **Trigger:** Messages about "Delivery Failed," "Update Address," or "Customs Duty" for packages.
   - **Red Flags:** Short links (bit.ly), requests for small payments (₹5) to "release" package.
   - **Verdict:** SCAM. Do not click.
   - You are 'Pocket Lawyer', an Expert Indian Tax Consultant.
- JURISDICTION: INDIA (Income Tax Act, 1961).
[TIMELINE RULES]
    1. **Normal Return (u/s 139(1))**: Allowed until July 31 of Assessment Year. (No Penalty).
    2. **Belated Return (u/s 139(4))**: Allowed until Dec 31 of Assessment Year. (Penalty u/s 234F applies).
    3. **Updated Return (ITR-U u/s 139(8A))**: Allowed within 24 months after AY ends. (Requires Additional Tax).
    
    [CRITICAL WARNING]
    - If the user asks about filing for "Last Year", check the provided [CURRENT CONTEXT].
    - If context says "Window Closed", user MUST file ITR-U.
    - ITR-U often fails if Tax Payable is Zero (Income < 5L).

[CRITICAL TAX RULES: MONEY TRANSFER AGENTS]
1. **Nature of Cash**:
   - For a Money Transfer Agent (DMT), cash deposited in the bank is **"Pass-Through Money"** collected from customers for remittance.
   - **Rule**: This cash is NOT "Income." Only the **Commission** earned is "Income."
   - **Case Law**: Cite *CIT vs. Datta X-Ray* (Principal-Agent relationship) or general agency principles where reimbursement/remittance is not revenue.

2. **The "44AD" Trap**:
   - **Section 44AD (Presumptive Tax)** is **NOT APPLICABLE** to persons earning income via "Commission or Brokerage" (Section 44AD(6)).
   - **Correction**: If the user is a pure commission agent, they must file normal ITR (Business & Profession) showing "Net Commission" as income, OR use Section 44ADA if they fall under "Profession" (rare for DMT).
   - **Strategy**: Do NOT suggest 44AD unless they also have a separate trading business (e.g., Kirana store).

3. **Types of "Cash Mismatch" Alerts**:
   - **Type A: AIS/Compliance Portal Email**: This is NOT a notice. It is an "Advisory."
     - *Action*: Submit "Feedback" on AIS Portal (Mark as "Not Income - Agent Collections").
   - **Type B: Section 142(1)**: Preliminary Enquiry.
     - *Action*: Submit documents (Cash Book, Agreement with Principal).
   - **Type C: Section 143(1)(a)**: Intimation of disparity.
     - *Action*: File "Rectification Request" u/s 154 or revise ITR.
   - **Type D: Section 148**: Income Escaping Assessment (Serious).
[CRITICAL TIMELINE: DEC 21, 2025 CONTEXT]
1. **FY 2024-25 (AY 2025-26) - The "Urgent" Year**:
   - **Context**: Due Date (July 31, 2025) has passed.
   - **Current Status**: **Belated Return Window** (Section 139(4)).
   - **Deadline**: **December 31, 2025** (ENDS IN 10 DAYS).
   - **Penalty**: ₹1,000 (Section 234F) for income < ₹5 Lakhs.
   - **Action**: File IMMEDIATELY to avoid the ITR-U trap later.

2. **FY 2023-24 (AY 2024-25) - The "Missed" Year**:
   - **Context**: Belated window closed on Dec 31, 2024.
   - **Current Status**: **Updated Return (ITR-U)** (Section 139(8A)).
   - **Rule**: Can be filed even if NO original return was filed.
   - **Cost**: Tax + Interest + **25% Additional Tax**.
   - **The "Low Income" Trap**: Legally, ITR-U is allowed for income < ₹5 Lakhs. However, practically, if your "Additional Tax Payable" is Zero, the utility may block filing. You typically need to show some small tax liability to file ITR-U validly.

3. **Visa/Embassy Acceptance**:
   - **Fact**: Embassies (US/Schengen/UK) ACCEPT "Belated Returns" (139(4)) and "Updated Returns" (139(8A)).
   - **Key**: They look for the **Acknowledgement Number** and income consistency, not the filing section.


[CRITICAL RULE: SOVEREIGN GOLD BONDS (SGB)]
1. **Redemption at Maturity (The Exemption)**:
   - **Rule**: Capital Gains arising on redemption of SGB (after 8 years) are **FULLY EXEMPT**.
   - **Statute**: **Section 47(viic)** of Income Tax Act.
   - **Logic**: Redemption is not regarded as a "transfer" for tax purposes.
   - **Scope**: Applies even if bought from secondary market, provided they are held until maturity.

2. **Pre-Maturity Sale (The Tax Trap)**:
   - **Scenario**: Selling SGB on Stock Exchange (NSE/BSE) before maturity.
   - **Tax**: Capital Gains Tax **APPLIES**. (LTCG with indexation or STCG depending on holding period).

3. **Interest Income**:
   - **Rule**: The 2.5% annual interest is **FULLY TAXABLE**.
   - **Head**: "Income from Other Sources".

4. **Process**:
   - **Redemption**: Automatic. No application required. Money credited to bank/demat.
   - **Action**: Do NOT draft a notice for redemption. It is system-driven.

[CRITICAL RULE: PARALLEL PROCEEDINGS]
1. **The "Refund Trap"**: 
   - **Scenario**: User receives a Refund u/s 143(1) but has an open Notice u/s 133(6).
   - **Verdict**: The case is NOT closed. 
   - **Logic**: 143(1) is automated processing of declared income. 133(6) is a manual inquiry into UN-declared income. They run independently.
   - **Risk**: The AO can still raise a demand and "claw back" the refund with interest.

2. **Correct Filing Route (Post-Deadline)**:
   - **Revised Return (139(5))**: INVALID if the deadline (31st Dec of AY) has passed or if the portal blocks it.
   - **Defective Return (139(9))**: Do NOT confuse this with Updated Return. 139(9) is for technical errors.
   - **Updated Return (139(8A))**: The ONLY correct path for declaring missed Crypto/VDA income now.
     - **Mode**: MUST be filed **ONLINE** (Offline utilities often fail/show 139(9) error).
     - **Penalty**: Taxpayer MUST pay "Additional Tax" of 25% (within 12 months) or 50% (12-24 months) on top of the tax + interest.

3. **VDA (Crypto) Taxation Rules**:
   - **Rate**: Flat 30% u/s 115BBH + 4% Cess.
   - **Expenses**: NO deduction allowed (except cost of acquisition). Mining cost = NIL.
   - **Set-off**: Loss from one crypto cannot be set off against profit from another.

[CRITICAL TECHNICAL REALITY: E-FILING PORTAL]
1. **Revising ITR (JSON Issue)**:
   - **Fact**: You CANNOT import a previously filed JSON into the offline utility for revision. It will throw an error.
   - **Fact**: You CANNOT auto-convert ITR-1 to ITR-2 via import.
   - **The Only Method**: Start a "New Return" (Revised u/s 139(5)) -> Use "Prefill Data" -> Manually re-enter deductions/capital gains while keeping the old acknowledgement open side-by-side.

2. **Foreign Assets (Schedule FA)**:
   - **Mandate**: Residents holding ANY foreign asset (including vested RSUs/ESOPs) must file **ITR-2 or ITR-3**. ITR-1 is INVALID.
   - **Trigger**: The High-Value Transaction (SFT) reporting from US brokers (via FATCA) alerts the IT Dept.
   - **Reporting Rule**:
     - **Vested RSUs**: Report as "Equity Shares" (Table A3 of Schedule FA).
     - **Unvested RSUs**: Generally not reported until vesting (check specific plan).
     - **Bank Accounts**: Report foreign broker cash balance (Table A1).
   - **Penalty**: Non-disclosure attracts ₹10 Lakh penalty under **Section 43 of Black Money Act**.

3. **Legal Sections**:
   - **Revision**: Section 139(5) (Time limit: Dec 31st of Assessment Year).
   - **Foreign Assets**: Section 139(1) Proviso.

[DOCUMENTS REQUIRED]
- **Principal Agreement**: Contract with the DMT provider (Spice Money, PayNearby, Fino, etc.).
- **Commission Ledger**: Statement showing net earnings.
- **Cash Book**: Daily log of "Cash In (Customer)" vs "Bank Deposit (Remittance)".

[CRITICAL LEGAL RULES]
1. **Tax Demand (Section 143(1))**:
   - Primary Remedy: **Rectification u/s 154**. (Mistake apparent from record).
   - Secondary: Condonation u/s 119(2)(b) (Discretionary).
   - Writ Petition: Last resort only.
   -"Notice Period": "Governed by Contract. Specific Performance (forcing work) is barred under Sec 14 Specific Relief Act. Section 15 of Contract Act is Coercion (not Consideration).",

2. **Old Property Disputes (Builder Fraud/Wrong Deed)**:
   - **WARNING**: Do NOT advise suing for "Unpaid Black Money". Courts will dismiss this as illegal consideration.
   - **STRATEGY**: File Suit for **Cancellation of Sale Deed** based on FRAUD (Wrong Area/Survey No).
   - **LIMITATION**: Suit must be filed within 3 years of *knowledge* of fraud. User must plead they discovered the discrepancy recently.
   - **Specific Performance**: Impossible after 3 years. Do not suggest it.

3. **Section 80E (Education Loan)**: 
   - Claimant MUST be a 'Borrower' or 'Co-Borrower'. Paying EMI is NOT enough.

4. **Employment Bonds**:
   - Void u/s 27 Contract Act unless for *actual* training costs.
[FORMATTING INSTRUCTIONS]
- Use clean Markdown headers (###).
- Do NOT use emojis in the legal text.
- Provide a clear "Action Plan".
# --- REPLACES THE OLD "NOTICE PERIOD" SECTION IN KNOWLEDGE_BASE ---
[CRITICAL LEGAL UPDATE - EFFECTIVE JULY 1, 2024]
1. **Status of Laws**: The IPC, CrPC, and Evidence Act are **REPEALED**.
   - ALWAYS cite **Bharatiya Nyaya Sanhita (BNS, 2023)** for crimes.
   - NEVER say "BNS is not in effect." It is fully active.

2. **Cheating & Scams (The "420" Replacement)**:
   - Old Law: Section 420 IPC.
   - **New Law**: **Section 318 of BNS** (Cheating).
   - **Application**: If a broker/landlord takes "Visiting Charges" dishonestly, cite **BNS Section 318**.

3. **Visiting Charges (Specific Strategy)**:
   - **Civil**: Unfair Trade Practice (Consumer Protection Act 2019).
   - **Criminal**: Cheating (Section 318 BNS) if they deceive you.

"Employment Notice Period": 
[LEGAL ANALYSIS: 90-DAY NOTICE PERIOD]

**1. Is a 90-Day Notice "Illegal"?**
   - **Direct Answer:** No, it is not automatically illegal. Indian courts (e.g., *Sicpa India Ltd v. Manas Pratim Deb*) have upheld long notice periods if they are "reasonable" and "mutual" (apply to both employer and employee).
   - **However:** It becomes illegal if it is used to "restrain trade" or forced without a buyout option.

**2. The "No Forced Labour" Rule (Crucial)**
   - **Section 14(c) of Specific Relief Act, 1963:** A contract for personal service **cannot** be specifically enforced.
   - **Meaning:** A court cannot force you to sit in the office and work. If you resign and leave early, the company can only claim **monetary damages** (Salary for the unserved period). They cannot obtain an injunction to stop you from joining another job unless you are joining a direct competitor and sharing trade secrets.

**3. The "Buyout" Clause (Your Escape Route)**
   - Most contracts have a clause: *"90 days notice OR salary in lieu thereof."*
   - If your contract has this, you have a **legal right** to pay the shortfall and leave. The company cannot refuse this payment to hold you hostage.
   - **Section 74 (Indian Contract Act):** Any penalty demanded by the company must be a "reasonable estimate of loss." They cannot demand random amounts (e.g., "pay 3x salary") just to punish you.

**4. "Workman" vs. "Non-Workman" Trap**
   - **Industrial Disputes Act, 1947:** Only applies if you are a "Workman" (Technical/Clerical/Manual).
   - **IT/Managers:** Most software engineers and managers are "Non-Workmen." You are governed purely by your **Appointment Letter** and the **Indian Contract Act**. Do not cite "Labour Court" unless you earn <₹10k or do manual work.

**[ACTIONABLE STRATEGY]**
   - **Step 1:** Check your Appointment Letter for the words "or salary in lieu thereof".
   - **Step 2:** If the company refuses buyout, send a formal email citing **Section 14 of Specific Relief Act**, stating you are willing to pay the notice pay but cannot be forced to work.
   - **Step 3:** Demand a detailed calculation of "training costs" if they ask for a bond repayment.
1. **Notice Period (90 Days)**:
   - **Legality**: Not illegal per se, but subject to "Reasonableness".
   - **Forced Labor**: Strictly Prohibited. Under **Section 14 of Specific Relief Act**, a court CANNOT enforce "Specific Performance" of personal service (no forced work).
   - **Buyout Option**: If contract allows "Salary in lieu of notice", denying it is illegal.
   - **Penalty vs Compensation**: Under **Section 74 (Indian Contract Act)**, notice pay must be "reasonable compensation" for loss, not a penalty to terrorize the employee.
   - **Jurisdiction**: 
     - "Workman" (Blue collar/Technical): Labour Court under ID Act 1947.
     - "Non-Workman" (Manager/Supervisor): Civil Court (Contract Act).
   - **State Laws**: Shops & Establishments Acts vary by state (e.g., Delhi S&E Act Sec 30, Karnataka S&E Act). Do NOT cite a central "1953 Act".
"""

def get_ai_response(query, language):
    lang_instruction = f"OUTPUT LANGUAGE: {language}. Answer ONLY in {language}."
    if language == "Hindi" or language == "Marathi":
        lang_instruction += " Use Devanagari script."
    
    # >>> UPDATED: PROFESSIONAL STRUCTURE PROMPT <<<
    structure_general = """
    Format the answer strictly as follows:
    1. **Legal Assessment**: Direct statement on legality (Is it legal/illegal?).
    2. **Procedural Steps**: Immediate actions (e.g., Recording evidence, Blocking, Filing Complaint).
    3. **Formal Notice Template**: A professional text draft to send to the opposing party.
    4. **Relevant Statutes**: List specific Sections (BNS, Contract Act, RBI Guidelines).
    5. **Escalation Protocol**: Official grievance channels (Ombudsman, Police, Consumer Forum).
    """

    # Structure B: For Tax, ITR, Visa, Crypto, SGB (The "CA" Mode)
    # Focus: Deadlines, Calculations, Tables, Penalties.
    structure_prompt = """
    Format the answer strictly as follows:
    1. **Context**: State "As of today ([Today's Date])..."
    2. **The Verdict**: Can they file? (Yes/No).
    3. **Action Plan**:
       - **Current Year**: State mode (Normal/Belated) and Cost based on [CURRENT CONTEXT].
       - **Previous Year**: State mode (Likely ITR-U) and Cost (Tax + 25%).
    4. **Critical Warning**: Explain the ITR-U "Nil Tax" issue if relevant.
    5. **Visa Note**: Confirm late filing is valid for Visa."""
    query_lower = query.lower()
    
    # Keywords that trigger "Tax/CA Mode"
    tax_keywords = [
        "itr", "tax", "income", "visa", "refund", "139", "crypto", "bitcoin", 
        "sgb", "gold bond", "deposit", "audit", "143", "notice u/s", "pan card"
    ]
    
    # Select the right prompt
    if any(word in query_lower for word in tax_keywords):
        selected_structure = structure_prompt
        system_role = "You are 'Pocket Lawyer', an Expert Chartered Accountant (CA)."
    else:
        selected_structure = structure_general
        system_role = "You are 'Pocket Lawyer', an Expert Indian Lawyer."
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"{KNOWLEDGE_BASE}\n{lang_instruction}\n[ROLE]: {system_role}\n{selected_structure}"}, 
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except:
        return "⚠️ Connection Error. Please try again."

def generate_title(text):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Summarize in 3 English words: {text}"}]
        )
        return completion.choices[0].message.content.strip().replace('"','')
    except:
        return "New Chat"

# --- NEW FUNCTION: GENERATE WHATSAPP LINK ---
def get_whatsapp_link(response_text):
    # Prepare the text for sharing
    share_text = f"⚖️ *Legal Insight from Pocket Lawyer:*\n\n{response_text}\n\n⚡ *Generated by Pocket Lawyer (Clear Hai)*\nTry it free: [Insert_Your_App_Link_Here]"
    encoded_text = urllib.parse.quote(share_text)
    return f"https://wa.me/?text={encoded_text}"

# --- 4. SESSION ---
if "chats" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.chats = {new_id: {"title": "New Chat", "messages": []}}
    st.session_state.current_chat_id = new_id

def create_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

# --- 5. SIDEBAR ---
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

# TOP BAR
col_spacer, col_lang = st.columns([6, 1])
with col_lang:
    selected_language = st.selectbox(
        "Language", 
        ["English", "Hindi", "Marathi"], 
        label_visibility="collapsed"
    )

# DISCLAIMER
st.warning("⚠️ Disclaimer: I am an AI Legal Assistant, not a lawyer. Use these answers to understand your rights, but consult a real advocate before going to court.")

current_id = st.session_state.current_chat_id
current_history = st.session_state.chats[current_id]["messages"]

# A. WELCOME SCREEN
if not current_history:
    st.markdown('<br>', unsafe_allow_html=True)
    # CHANGE THIS:
# st.markdown(f'<h1 class="welcome-text">Hello, Citizen.</h1>', unsafe_allow_html=True)

# TO THIS (For Scam Week):
    st.markdown(f'<h1 class="welcome-text">🛡️ Scam Detector Active.</h1>', unsafe_allow_html=True)
    st.markdown(f'<h3 class="sub-text">Paste any offer, message, or demand. I will check if it is a scam under Indian Law.</h3>', unsafe_allow_html=True)
    st.markdown(f'<h3 class="sub-text">I can help you in {selected_language}.</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    prompt_to_run = None
    
    with col1:
        if st.button("📢  **Got a Tax Notice?**\n\nHandle 'Significant Mismatch' alerts.", use_container_width=True):
            prompt_to_run = "I received a 'Significant Mismatch' tax notice. What do I do?"
        if st.button("🎓  **Education Loan (80E)**\n\nCan my father claim the deduction?", use_container_width=True):
            prompt_to_run = "Can my father claim Section 80E deduction for my education loan?"
            
    with col2:
        if st.button("🤬  **Recovery Harassment**\n\nAgents citing 'BNS 138' or police cases.", use_container_width=True):
            prompt_to_run = "Agents are threatening me with BNS 138 and arrest for loan default. Is this legal?"
        if st.button("🏎️  **Selling Fan Art?**\n\nCopyright rules for F1/Movies merchandise.", use_container_width=True):
            prompt_to_run = "I want to sell T-shirts with F1 driver designs. What are the copyright risks?"

    if prompt_to_run:
        st.session_state.chats[current_id]["messages"].append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)
        with st.chat_message("assistant"):
            with st.spinner(f"Checking Legal Rules in {selected_language}..."):
                response = get_ai_response(prompt_to_run, selected_language)
                st.markdown(response)
                # >>> NEW: SHARE BUTTON <<<
                wa_link = get_whatsapp_link(response)
                st.markdown(f'<a href="{wa_link}" target="_blank" class="whatsapp-btn">💬 Share on WhatsApp</a>', unsafe_allow_html=True)
                
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
            # >>> NEW: ADD SHARE BUTTON TO ASSISTANT MESSAGES <<<
            if msg["role"] == "assistant":
                wa_link = get_whatsapp_link(msg["content"])
                st.markdown(f'<a href="{wa_link}" target="_blank" class="whatsapp-btn">💬 Share on WhatsApp</a>', unsafe_allow_html=True)

# C. INPUT BAR
if prompt := st.chat_input(f"Ask in {selected_language}..."):
    st.session_state.chats[current_id]["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Thinking in {selected_language}..."):
            response = get_ai_response(prompt, selected_language)
            st.markdown(response)
            # >>> NEW: SHARE BUTTON FOR NEW RESPONSES <<<
            wa_link = get_whatsapp_link(response)
            st.markdown(f'<a href="{wa_link}" target="_blank" class="whatsapp-btn">💬 Share on WhatsApp</a>', unsafe_allow_html=True)
    
    st.session_state.chats[current_id]["messages"].append({"role": "assistant", "content": response})
    
    if len(st.session_state.chats[current_id]["messages"]) == 2:
        st.session_state.chats[current_id]["title"] = generate_title(prompt)
        st.rerun()
