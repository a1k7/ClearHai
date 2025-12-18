import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import re
import textwrap
from datetime import datetime, timedelta

# ==============================================================================
# 1. UI/UX CONFIGURATION (DARK GEMINI THEME)
# ==============================================================================
st.set_page_config(
    page_title="Clear Hai? | The Truth Machine", 
    page_icon="✅", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- DARK MODE CSS ---
st.markdown("""
    <style>
    /* Global Background */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 0%, #0f172a 0%, #020617 100%);
        color: #f8fafc;
    }
    .block-container {
        padding-top: 3rem !important;
        max-width: 900px !important;
    }
    
    /* Typography */
    h1, h2, h3 { font-family: 'Inter', sans-serif !important; color: #f8fafc !important; letter-spacing: -0.5px; }
    p, li, div { font-family: 'Inter', sans-serif; color: #cbd5e1 !important; line-height: 1.6; }
    strong { color: #fff; font-weight: 600; }
    
    /* Inputs */
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stNumberInput > div > div > input {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.95) !important; border-right: 1px solid rgba(51, 65, 85, 0.5); }
    
    /* Truth Mode Alert Box */
    .truth-box {
        background-color: #450a0a; 
        border: 1px solid #ef4444; 
        padding: 20px; 
        border-radius: 12px; 
        color: #fca5a5;
        margin-bottom: 20px;
    }

    /* Hide Default Elements */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CORE SETUP & CONSTANTS
# ==============================================================================

client = None 
MODEL_NAME = "llama-3.1-8b-instant" 

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ Groq API Key missing! Check .streamlit/secrets.toml")
    st.stop()

# --- 🚨 CRITICAL CONSTANTS ---
LOAN_SIMULATOR_KEYWORDS = ["LOAN", "MORTGAGE", "FINANCE", "LENDING", "BORROW", "EMI", "HOME LOAN", "HOUSING LOAN"]

VAG_GENERAL_KEYWORDS = {
    "ITR_FILING": ["ITR", "TAX RETURN", "FORM 16", "26AS", "80C", "80D", "TDS REFUND", "SALARY BREAKUP"],
    "EPFO_SERVICES": ["PF", "EPFO", "UAN", "GRATUITY", "PF WITHDRAWAL", "PF TRANSFER", "KYC UPDATE"],
    "BANKING_OPS": ["BANK ACCOUNT OPENING", "ZERO BALANCE", "NRI ACCOUNT", "NOMINEE ADDITION", "FIXED DEPOSIT", "RD"],
    "BANKING_CARDS": ["CREDIT CARD", "DEBIT CARD", "CREDIT LIMIT", "MINIMUM DUE", "BILLING CYCLE"], 
    "BANKING_DISPUTE": ["CHARGEBACK", "ACCOUNT FREEZE", "BLOCKED", "INSURANCE CLAIM", "CREDIT SCORE", "CIBIL"],
    "EDU_ADMISSION": ["COLLEGE ADMISSION", "SCHOLARSHIP", "EDUCATION LOAN", "ENTRANCE EXAM"],
    "EDU_DOCS": ["DEGREE VERIFICATION", "NAME CORRECTION", "CERTIFICATE CORRECTION", "TRANSCRIPT", "SKILL CERTIFICATION"],
    "EDU_INTERNSHIP": ["INTERNSHIP", "AICTE INTERNSHIP", "SUMMER INTERNSHIP", "INTERNSHIP ELIGIBILITY"], 
    "PROP_REG": ["PROPERTY REGISTRATION", "SALE DEED", "AGREEMENT TO SELL", "STAMP DUTY"],
    "PROP_RECORDS": ["MUTATION", "KHATA", "PROPERTY TAX", "ENCUMBRANCE CERTIFICATE", "EC CHECK"],
    "RERA_VERIF": ["RERA VERIFICATION", "RERA CHECK", "RERA COMPLAINT"],
    "POA": ["POWER OF ATTORNEY", "POA RULES", "GPA", "SPA"], 
    "LEGAL_DOCS": ["RENT AGREEMENT", "AFFIDAVIT", "NOTARY", "GAZETTED OFFICER", "POLICE VERIFICATION"],
    "LEGAL_ACTION": ["FIR", "CONSUMER COMPLAINT", "LEGAL NOTICE", "SMALL CLAIMS COURT"],
    "TRAVEL_DOCS": ["OCI CARD", "FRRO", "PASSPORT", "INTERNATIONAL DRIVING PERMIT", "DRIVING LICENSE", "IDP", "VISA", "SCHENGEN"],
    "TRAVEL_RULES": ["ECNR", "EMIGRATION CLEARANCE", "CUSTOMS RULES", "GOLD LIMIT", "CASH LIMIT"],
    "BIZ_REG": ["GST REGISTRATION", "GST RETURN", "MSME", "UDYAM", "SHOP ACT", "GUMASTA", "COMPANY INCORPORATION", "BUSINESS BANK ACCOUNT"],
    "BIZ_IPR": ["TRADEMARK", "BRAND REGISTRATION"],
    "MARRIAGE_DIVORCE": ["MARRIAGE REGISTRATION", "DIVORCE PROCESS", "NAME CHANGE AFTER MARRIAGE"],
    "SUCCESSION": ["LEGAL HEIR", "SUCCESSION CERTIFICATE", "WILL REGISTRATION", "DEATH CERTIFICATE"],
    "CYBER_SAFETY": ["CYBERCRIME", "SIM MISUSE", "ONLINE FRAUD", "ACCOUNT HACKING", "HACKED", "RECOVER ACCOUNT", "DATA BREACH", "DATA LEAK", "1930"],
    "PAN": ["PAN", "PAN CARD", "PERMANENT ACCOUNT NUMBER", "AADHAAR LINKING"],
}

OFFICIAL_PORTALS = {
    "ITR_FILING": "[**Income Tax e-Filing Portal**](https://www.incometax.gov.in/iec/foportal/)",
    "EPFO_SERVICES": "[**EPFO Unified Member Portal**](https://unifiedportal-mem.epfindia.gov.in/memberinterface/)",
    "GST": "[**GST Common Portal**](https://www.gst.gov.in/)",
    "BIZ_REG": "[**Udyam Registration (MSME)**](https://udyamregistration.gov.in/) | [**MCA (Company Inc)**](https://www.mca.gov.in/)",
    "BIZ_IPR": "[**IP India Public Search**](https://ipindiaservices.gov.in/tmrpublicsearch) | [**Trademark e-Filing**](https://ipindiaonline.gov.in/trademarkefiling/)",
    "TRAVEL_DOCS": "[**Passport Seva**](https://www.passportindia.gov.in/) | [**OCI Services**](https://ociservices.gov.in/)",
    "CYBER_SAFETY": "[**National Cyber Crime Reporting Portal**](https://cybercrime.gov.in/) | [**Sanchar Saathi (TAFCOP)**](https://sancharsaathi.gov.in/)",
    "BANKING_DISPUTE": "[**RBI Integrated Ombudsman (CMS)**](https://cms.rbi.org.in/)",
    "BANKING_CARDS": "[**RBI Master Direction on Credit Cards**](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12300&Mode=0)",
    "PAN": "[**NSDL (Protean) PAN**](https://www.onlineservices.nsdl.com/paam/endUserRegisterContact.html) | [**UTIITSL PAN**](https://www.pan.utiitsl.com/)",
    "EDU_ADMISSION": "[**Vidya Lakshmi Portal (Loans)**](https://www.vidyalakshmi.co.in/) | [**National Scholarship Portal**](https://scholarships.gov.in/)"
}

BANK_LINKS = {
    "State Bank of India": "https://sbi.co.in/web/personal-banking/loans/home-loans",
    "HDFC Bank": "https://www.hdfcbank.com/personal/borrow/popular-loans/home-loan",
    "ICICI Bank": "https://www.icicibank.com/personal-banking/loans/home-loan",
    "Punjab National Bank": "https://www.pnbindia.in/home-loan.html",
    "Bank of Baroda": "https://www.bankofbaroda.in/personal-banking/loans/home-loan"
}

# ==============================================================================
# 3. LOGIC CLASSES
# ==============================================================================

class IndianDivorceSystem:
    def get_legal_info(self, divorce_type):
        type_clean = divorce_type.lower()
        if "mutual" in type_clean:
            return {
                "type": "Mutual Consent (Section 13B HMA)",
                "authority": "Family Court (District Court)",
                "timeline": "6 Months (Cooling Off) to 18 Months.",
                "docs": "Joint Petition, Wedding Proof, Settlement Agreement.",
                "note": "Fastest legal route. Both parties must agree."
            }
        else: 
            return {
                "type": "Contested Divorce",
                "authority": "Family Court (District Court)",
                "timeline": "3 to 5+ Years (Depends on evidence/appeals).",
                "docs": "Petition, Evidence of Cruelty/Adultery, Income Affidavit.",
                "note": "Long legal battle. Burden of proof is on the petitioner."
            }

    def check_eligibility_bar(self, years_married):
        if years_married < 1:
            return "❌ LEGAL BARRIER: Under Section 14 of HMA, you generally cannot file for divorce within the first year of marriage."
        return "✅ ELIGIBLE TO FILE: You have completed the mandatory 1-year waiting period post-marriage."

class RBIBankingStandards:
    VALID_OVDS = {"aadhaar", "passport", "voter id", "driving licence", "nrega job card"}
    FEE_STRUCTURE = {
        "Account Opening": 0.00,
        "Monthly Maintenance": 0.00,
        "Annual Maintenance": 0.00,
        "Passbook/Statement": "Free (Digital)"
    }
    TDS_LIMIT_GENERAL = 40000 
    TDS_LIMIT_SENIOR = 50000 

def get_bank_rules(bank_name):
    bn = bank_name.upper()
    if "SBI" in bn or "STATE BANK" in bn:
        return {"Interest_Rate": "8.50% - 9.65%", "Processing_Fee": "0.35% (Max ₹10k)", "Max_FOIR": "50%", "Min_CIBIL": "750"}
    elif "PNB" in bn or "PUNJAB NATIONAL" in bn:
        return {"Interest_Rate": "8.40% - 10.15%", "Processing_Fee": "0.35% + GST", "Max_FOIR": "50%", "Min_CIBIL": "750"}
    elif "BARODA" in bn:
        return {"Interest_Rate": "8.40% - 10.60%", "Processing_Fee": "0.50% (Max ₹15k)", "Max_FOIR": "50%", "Min_CIBIL": "725"}
    elif "BANK OF INDIA" in bn:
        return {"Interest_Rate": "8.30% - 10.75%", "Processing_Fee": "0.25% (Min ₹1.5k)", "Max_FOIR": "50%", "Min_CIBIL": "750"}
    elif "CANARA" in bn:
        return {"Interest_Rate": "8.50% - 11.25%", "Processing_Fee": "0.50% (Min ₹1.5k)", "Max_FOIR": "50%", "Min_CIBIL": "750"}
    elif "UNION" in bn:
        return {"Interest_Rate": "8.35% - 10.75%", "Processing_Fee": "0.50% (Max ₹15k)", "Max_FOIR": "50%", "Min_CIBIL": "750"}
    elif "MAHARASHTRA" in bn:
        return {"Interest_Rate": "8.35% - 10.80%", "Processing_Fee": "0.25% (Waived often)", "Max_FOIR": "50%", "Min_CIBIL": "750"}
    elif "INDIAN BANK" in bn:
        return {"Interest_Rate": "8.40% - 9.90%", "Processing_Fee": "0.23% (Max ₹20k)", "Max_FOIR": "50%", "Min_CIBIL": "750"}
    elif "IOB" in bn or "OVERSEAS" in bn:
        return {"Interest_Rate": "8.40% - 9.70%", "Processing_Fee": "0.50% (Max ₹10k)", "Max_FOIR": "50%", "Min_CIBIL": "750"}
    elif "CENTRAL" in bn:
        return {"Interest_Rate": "8.35% - 9.80%", "Processing_Fee": "0.50% (Max ₹20k)", "Max_FOIR": "50%", "Min_CIBIL": "725"}
    elif "UCO" in bn:
        return {"Interest_Rate": "8.45% - 10.30%", "Processing_Fee": "0.50% (Min ₹1.5k)", "Max_FOIR": "50%", "Min_CIBIL": "725"}
    elif "PUNJAB & SIND" in bn:
        return {"Interest_Rate": "8.50% - 10.00%", "Processing_Fee": "0.50% + GST", "Max_FOIR": "50%", "Min_CIBIL": "750"}
    elif "HDFC" in bn:
        return {"Interest_Rate": "8.75% - 9.40%", "Processing_Fee": "0.50% or ₹3000", "Max_FOIR": "60%", "Min_CIBIL": "760"}
    elif "ICICI" in bn:
        return {"Interest_Rate": "9.00% - 9.10%", "Processing_Fee": "0.50% - 2.00%", "Max_FOIR": "55%", "Min_CIBIL": "750"}
    elif "AXIS" in bn:
        return {"Interest_Rate": "8.75% - 9.15%", "Processing_Fee": "1% (Min ₹10k)", "Max_FOIR": "60%", "Min_CIBIL": "750"}
    elif "KOTAK" in bn:
        return {"Interest_Rate": "8.70% onwards", "Processing_Fee": "0.50% + GST", "Max_FOIR": "60%", "Min_CIBIL": "750"}
    elif "INDUSIND" in bn:
        return {"Interest_Rate": "8.75% - 10.50%", "Processing_Fee": "1.00% + GST", "Max_FOIR": "65%", "Min_CIBIL": "725"}
    elif "YES" in bn:
        return {"Interest_Rate": "9.40% onwards", "Processing_Fee": "1.00% - 2.00%", "Max_FOIR": "60%", "Min_CIBIL": "700"}
    elif "FEDERAL" in bn:
        return {"Interest_Rate": "8.80% - 10.15%", "Processing_Fee": "0.50% (Min ₹3k)", "Max_FOIR": "60%", "Min_CIBIL": "730"}
    else:
        return {"Interest_Rate": "8.50% - 10.50%", "Processing_Fee": "0.50% - 1.00%", "Max_FOIR": "50%", "Min_CIBIL": "750"}

# ==============================================================================
# 4. UTILITY FUNCTIONS
# ==============================================================================

def find_process_details(task):
    query_process = f"Official 2025 guide for {task} India fees documents process"
    try:
        ddgs = DDGS()
        results_proc = ddgs.text(query_process, max_results=3, backend="api")
        research_text = ""
        official_links = []
        for r in results_proc:
            research_text += f"- Source: {r['title']}\n  Snippet: {r['body']}\n"
            if ".gov.in" in r['href']:
                official_links.append(f"[{r['title']}]({r['href']})")
        return research_text, "\n".join(list(set(official_links)))
    except Exception as e:
        return f"Offline Mode: {str(e)}", ""

def generate_bank_constraints(research, task):
    bank_name = task.split()[2] if len(task.split()) > 2 else "Major Indian Bank"
    sds_rules = get_bank_rules(bank_name)
    formatted_sds = "\n".join([f"* **{k}:** {v}" for k, v in sds_rules.items()])
    
    prompt = f"""
    You are an **RBI-Aligned Data Analyst**. Extract only the KEY FACTS for a home loan from the RESEARCH DATA for **{bank_name}**. 
    VERIFIED 2025 CONSTRAINTS:
    {formatted_sds}
    Research Data: {research}
    OUTPUT MUST be a simple bulleted list of 5-7 verified facts.
    """
    try:
        global client
        response = client.chat.completions.create(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
        return response.choices[0].message.content
    except:
        return "Extraction failed."

# ==============================================================================
# 5. THE MASTER PLAN LOGIC (UNCOMPRESSED)
# ==============================================================================

def generate_master_plan(research, task, links_found, mode="GENERAL"):
    task_upper = task.upper()
    safe_task = task
    if "HACK" in task_upper and "RECOVER" in task_upper:
        safe_task = "How to recover a compromised social media account using official support forms"
    
    # Identify Topic
    current_topic_key = None
    for key, keywords in VAG_GENERAL_KEYWORDS.items():
        if any(kw in task_upper for kw in keywords):
            current_topic_key = key
            break
            
    # Inject Golden Link
    if current_topic_key and current_topic_key in OFFICIAL_PORTALS:
        golden_link = OFFICIAL_PORTALS[current_topic_key]
        links_found = f"⭐ **OFFICIAL PORTAL:** {golden_link}\n\n{links_found}"

    # --- FINANCIAL MODE ---
    if mode == "FINANCIAL":
        bank_name = "Major Indian Bank"
        # Try to extract bank name from task
        for bn in ["SBI", "HDFC", "ICICI", "AXIS", "KOTAK", "PNB", "BARODA"]:
            if bn in task_upper:
                bank_name = bn
                break
        
        bank_constraints = generate_bank_constraints(research, task)
        
        for b_key, b_link in BANK_LINKS.items():
            if b_key.upper() in task_upper:
                links_found = f"⭐ **OFFICIAL LOAN PAGE:** [{b_key}]({b_link})\n\n"
                break
        
        specific_constraints = f"VERIFIED CONSTRAINTS: {bank_constraints}"
        disclaimer = "Rates, fees, and terms are subject to periodic revision. Floating-rate loans are linked to external benchmarks."
        eligibility_content = "Assess based on NMI, FOIR, and CIBIL."
        documents_content = "1. **KYC:** PAN, Aadhaar.\n2. **Income Proof:** Salary Slips (3 months) + Form 16 (2 years) OR ITR (3 years for Self-employed).\n3. **Property:** Sale Agreement / Title Deed."
        fees_content = "**Processing Fee:** See 'Bank Constraints' above for exact %."
        timeline_content = "2-4 Weeks."
        extra_logic_output = ""

    # --- GENERAL MODE (The 19 Hardcore Topics) ---
    else:
        specific_constraints = ""
        disclaimer = "Information based on general rules. Confirm details on the official government website."
        eligibility_content = "[List specific eligibility. If none exist, state 'None'.]"
        documents_content = "[List exact mandatory documents.]"
        fees_content = "[List official government fees.]"
        timeline_content = "[Provide a realistic processing timeline.]"
        extra_logic_output = ""

        # 1. TAX & ITR
        if current_topic_key == "ITR_FILING":
            specific_constraints = "Focus on ITR-1 vs ITR-4 and Tax Regimes."
            disclaimer = "Tax liability varies by individual. Consult a CA for complex filings."
            eligibility_content = "**ITR-1:** Resident Individual <₹50L income (Salary/House). **ITR-4:** Presumptive Business Income. **80C:** Max ₹1.5L deduction."
            documents_content = "**Retain (Do NOT Upload):** Form 16 (Employer), Form 26AS (Tax Credit), AIS/TIS (Transaction Summary)."
            fees_content = "**Filing:** Free. **Late Fee:** ₹1,000 or ₹5,000 (Sec 234F). **TDS Refund:** Processed automatically."
            timeline_content = "**Due Date:** 31st July of Assessment Year. **Refund:** 20-45 days."
            extra_logic_output = ""

        # 2. EPFO SERVICES
        elif current_topic_key == "EPFO_SERVICES":
            specific_constraints = "Focus on UAN KYC, Bank Name Match, and differentiating Final (Form 19) vs Partial (Form 31) withdrawal."
            disclaimer = "**CRITICAL:** Your Name in the Bank Account MUST match exactly with your UAN/Aadhaar name. If there is a mismatch, the bank KYC will be rejected."
            eligibility_content = """
            **A. Final Settlement:**
            * **Form 19 (PF Final):** Allowed after 2 months of unemployment.
            * **Form 10C (Pension):** Service > 6 months AND < 10 years.
            
            **B. Partial Withdrawal:**
            * **Form 31 (Advance):** For specific needs (Illness, Marriage, Home Loan).
            """
            documents_content = """
            **Phase 1: Pre-Claim KYC:**
            1. **UAN Linked with Aadhaar** (Verified status).
            2. **Bank Account KYC:** Status must be 'Digitally Signed' by Employer.
            
            **Phase 2: Claim Filing:**
            1. **Cancelled Cheque/Passbook:** Name & IFSC must be visible.
            """
            fees_content = "**Fees:** NIL. **TDS:** 10% if service < 5 years & amount > ₹50k (Submit Form 15G/H)."
            timeline_content = "* **KYC Approval:** 3-7 Days. * **Claim Settlement:** 7-20 Days."
            extra_logic_output = ""

        # 3. INTERNSHIPS
        elif current_topic_key == "EDU_INTERNSHIP":
            specific_constraints = "Focus on AICTE/UGC norms and College NOC."
            disclaimer = "Eligibility and stipends depend on the specific company/organization policy."
            eligibility_content = "**Bonafide Student:** Must be enrolled in a recognized University. **NOC:** No Objection Certificate from HOD/Principal is mandatory."
            documents_content = "1. **NOC / Recommendation Letter** from College.\n2. **Resume/CV**.\n3. **Student ID Card**.\n4. **Bonafide Certificate**."
            fees_content = "**Application Fee:** Generally NIL. (Some training institutes may charge fees)."
            timeline_content = "**Application Window:** Apply 2-3 months prior to summer/winter break."

        # 4. EDUCATION DOCS
        elif current_topic_key == "EDU_DOCS":
            specific_constraints = "Focus on University/Board specific process."
            disclaimer = "Original documents are required for verification. Do not hand over originals to agents."
            eligibility_content = "Student/Alumni of the institution. **Name Change:** Requires Gazette Notification."
            documents_content = "1. **Application Form**.\n2. **Copy of Final Degree/Marksheets**.\n3. **ID Proof**.\n4. **Gazette Notification** (for name change)."
            fees_content = "**Varsity Fees:** ₹500 - ₹5,000 depending on document age and urgency."
            timeline_content = "**15 to 60 Days.**"

        # 5. EDUCATION ADMISSION/LOAN
        elif current_topic_key == "EDU_ADMISSION":
            specific_constraints = "Focus on Entrance Exams (JEE/NEET/CAT) or Portal (Vidya Lakshmi for loans)."
            disclaimer = "Scholarship quotas are state-specific."
            eligibility_content = "**Scholarship:** Income/Merit-based. **Loan:** Admission confirmation letter required."
            documents_content = "1. **Admission Letter**.\n2. **Income Certificate** (for Scholarships).\n3. **KYC of Student & Parent**."
            fees_content = "**Loan Processing:** NIL for schemes < ₹4 Lakhs."
            timeline_content = "**Loan:** 15-30 days. **Admission:** As per counseling schedule."
        # [NEW] SMART INVESTMENT LOGIC
        elif "INVEST" in task_upper:
            # Check Duration (Simple Keyword Check)
            is_long_term = any(x in task_upper for x in ["YEARS", "LONG TERM", "5 YEAR", "10 YEAR"])
            is_short_term = any(x in task_upper for x in ["MONTH", "DAYS", "SHORT TERM", "1 YEAR"])
            
            specific_constraints = "Focus on Inflation-adjusted returns and Tax Efficiency."
            
            if is_long_term: # > 3 Years
                eligibility_content = "**Resident Individual** with valid KYC (PAN/Aadhaar)."
                documents_content = "1. **PAN & Aadhaar**.\n2. **Bank Proof:** Cancelled Cheque.\n3. **CKYC Status:** Central KYC Registry check."
                fees_content = "**Expense Ratio:** ~0.10% - 0.50% (Direct Mutual Funds). **Exit Load:** NIL after 1 year."
                timeline_content = "**Setup:** 1-2 Days. **Growth:** Compounding works best over 5+ years."
                
                # The "Expert" Advice Section
                disclaimer = "**RISK NOTE:** Equity investments are subject to market risks but historically beat inflation over 5+ years."
                eligibility_content += """
                
                ### 💡 Best Options for 6+ Years (Growth Focused):
                1.  **Index Mutual Funds (Nifty 50):**
                    * *Avg Return:* ~12% - 14% (Historical).
                    * *Why:* Low cost, beats inflation, lower tax (12.5% LTCG) than FDs.
                2.  **Sovereign Gold Bonds (SGB):**
                    * *Return:* 2.5% Interest + Gold Price Appreciation.
                    * *Why:* Tax-FREE if held till maturity (8 years). Safe (Govt backed).
                3.  **Corporate FDs (AAA Rated):**
                    * *Return:* ~7.5% - 8.5%.
                    * *Why:* Higher rates than bank FDs, but slightly higher risk.
                """
                extra_logic_output = ""
                
            else: # Short Term (< 3 Years)
                eligibility_content = "**Resident Individual**."
                documents_content = "PAN, Aadhaar, Bank Details."
                fees_content = "NIL for FDs."
                timeline_content = "**FD Creation:** Instant (NetBanking)."
                
                disclaimer = "**TAX WARNING:** Interest from FDs/Debt Funds is added to your income and taxed at your slab rate."
                eligibility_content += """
                
                ### 💡 Best Options for Short Term (Safety First):
                1.  **Bank Fixed Deposit (FD):**
                    * *Return:* ~6.5% - 7.5%.
                    * *Why:* Capital protection.
                2.  **Liquid / Arbitrage Funds:**
                    * *Return:* ~7% (Arbitrage funds are taxed lower like Equity).
                    * *Why:* Better liquidity than FD (No penalty on withdrawal).
                """
                extra_logic_output = ""

        # 6. PROPERTY REGISTRATION
        elif current_topic_key == "PROP_REG":
            disclaimer = "**SCOPE:** This is an estimation guide. Final duty is determined by the Sub-Registrar based on the exact location/zone and Circle Rate."
            eligibility_content = """
            * **Buyer:** Any Individual or Entity.
            * **Concessions:** Women often get **1-2% lower stamp duty** rates (State-specific: e.g., Delhi, UP, Haryana, Punjab).
            """
            documents_content = """
            **For Calculation:**
            1. **Draft Deed** (Agreement to Sell).
            2. **Ready Reckoner / Circle Rate** details for the specific zone.
            
            **For Registration:**
            1. **ID Proofs:** PAN & Aadhaar (Buyer & Seller).
            2. **Witnesses:** 2 Witnesses with ID Proofs.
            3. **Payment Receipt:** Challan for Stamp Duty & Reg Fee.
            """
            fees_content = """
            **1. Stamp Duty (The "Higher Value" Rule):**
            * Calculated on the **HIGHER** of Agreement Value OR Circle Rate.
            * **Typical Rates:** 5% - 7% of Market Value.
            
            **2. Registration Fee:**
            * Typically **1%** of the Value.
            """
            timeline_content = "**Calculation:** Instant. **Registration:** Same Day to 3 Days."
            extra_logic_output = ""

        # 7. PROPERTY RECORDS
        elif current_topic_key == "PROP_RECORDS":
            specific_constraints = "Distinguish between Registration Dept (EC) and Municipal/Revenue Dept (Mutation/Khata)."
            disclaimer = "**TERMINOLOGY ALERT:** 'Khata' is a term primarily used in Karnataka. In other states, this process is known as **Mutation** (e.g., 'Ferfar' in Maharashtra)."
            eligibility_content = """
            * **Applicant:** Current Property Owner or Legal Heir.
            * **Prerequisite:** The Sale Deed must already be registered with the Sub-Registrar.
            """
            documents_content = """
            **For Encumbrance Certificate (EC):**
            1. **Source:** Issued by the **Sub-Registrar's Office** (Registration Dept).
            
            **For Mutation / Khata Transfer:**
            1. **Authority:** Municipal Corporation (Urban) OR Tehsildar (Rural).
            2. **Registered Sale Deed** (Copy).
            3. **Latest Property Tax Receipt**.
            """
            fees_content = "**EC Fees:** Nominal. **Mutation Fees:** State-Specific (Fixed or % of Tax)."
            timeline_content = "**EC:** 1-7 Days. **Mutation:** 15-45 Days."

        # 8. RERA & POA
        elif current_topic_key == "RERA_VERIF" or current_topic_key == "POA":
            specific_constraints = "Focus on Public Search (RERA) or Principal Capacity (POA)."
            disclaimer = "RERA is for project status check. POA must be registered for property sale."
            eligibility_content = "**RERA:** Public Access. **POA:** Principal must be 18+ and sound mind."
            documents_content = "**RERA:** None. **POA:** Draft Deed, Photos, IDs of Principal/Attorney/Witnesses."
            fees_content = "**RERA:** Free. **POA:** ₹100-₹500 (General), 5-7% (Sale POA)."
            timeline_content = "**RERA:** Instant. **POA:** Same Day."

        # 9. LEGAL DOCS (Rent/Affidavit)
        elif current_topic_key == "LEGAL_DOCS":
            if "RENT" in task_upper:
                specific_constraints = "Focus on Registration Act (Section 17) vs Notarization."
                disclaimer = "**CRITICAL LEGAL WARNING:** Notarization is **NOT** a substitute for Registration. If the lease term exceeds 11 months, an unregistered agreement is **inadmissible as evidence** in court."
                eligibility_content = "* **Parties:** Landlord & Tenant (Must be 18+).\n* **Authority:** Sub-Registrar (for Registration) OR Public Notary."
                documents_content = "1. **Draft Agreement** on Stamp Paper.\n2. **ID Proofs:** Aadhaar/PAN.\n3. **Property Proof:** Electricity Bill."
                fees_content = "**Stamp Duty:** Varies by state (Rent + Deposit). **Registration Fee:** ~1%."
                timeline_content = "**Notarized:** Same Day. **Registered:** 2-5 Days."
                extra_logic_output = ""
            elif "AFFIDAVIT" in task_upper:
                specific_constraints = "Focus on Section 193 IPC (False Evidence)."
                disclaimer = "**WARNING:** Swearing a false affidavit is a punishable offence (Perjury)."
                eligibility_content = "* **Deponent:** Must be 18+ years old.\n* **Purpose:** Name Change, Address Proof, etc."
                documents_content = "1. **Draft Content**.\n2. **Non-Judicial Stamp Paper**.\n3. **ID Proof**."
                fees_content = "**Stamp Duty:** ₹10-₹100. **Notary Fee:** ₹50 - ₹300."
                timeline_content = "**Immediate / Same Day.**"
            else: # Notary vs Gazetted
                specific_constraints = "Focus on Notaries Act 1952 vs Administrative Attestation."
                disclaimer = "**LEGAL DISTINCTION:** A Gazetted Officer **cannot** notarize legal deeds."
                eligibility_content = "* **Public Notary:** Practicing Advocate.\n* **Gazetted Officer:** Group A or B Govt Official."
                documents_content = "Original Document + Photocopy."
                fees_content = "**Notary:** Statutory Fees. **Gazetted Officer:** NIL."
                timeline_content = "Immediate."

        # 10. LEGAL ACTION (FIR/Consumer)
        elif current_topic_key == "LEGAL_ACTION":
            if "FIR" in task_upper:
                specific_constraints = "Focus on CrPC (BNSS) Section 154. Concept of 'Zero FIR'."
                disclaimer = "**LEGAL RIGHT:** Police **cannot** refuse to register an FIR for a cognizable offence."
                eligibility_content = "**Victim or Witness:** Any person aware of the offence."
                documents_content = "1. **Written Complaint**.\n2. **Identity Proof**.\n3. **Evidence** (if any)."
                fees_content = "**NIL.** Registering an FIR is a free public service."
                timeline_content = "**Registration:** Immediate."
                extra_logic_output = ""
            elif "VERIFICATION" in task_upper or "PCC" in task_upper:
                specific_constraints = "Distinguish between PCC (Visa/Job) and Tenant Verification."
                disclaimer = "**JURISDICTION:** Apply to the Police Station covering your *current* residence."
                eligibility_content = """
                * **Tenant Verif:** Landlord files.
                * **Employee Verif:** Employer files.
                * **PCC:** Applicant must have resided > 6 months.
                """
                documents_content = "1. **Identity Proof**.\n2. **Address Proof**.\n3. **Photos**."
                fees_content = "**State Specific:** ₹200 - ₹500."
                timeline_content = "3 to 21 Days."
            else: # Consumer
                specific_constraints = "Focus on Consumer Protection Act 2019. e-Daakhil Portal."
                disclaimer = "**PROCEDURE:** Filing a 'Legal Notice' to the company is the standard first step."
                eligibility_content = "**Consumer:** Anyone who bought goods/services for personal use."
                documents_content = "1. **Proof of Purchase**.\n2. **Proof of Deficiency**.\n3. **Legal Notice**."
                fees_content = "**Court Fees:** Up to ₹5 Lakhs claim is NIL."
                timeline_content = "**Admissibility:** 21 Days. **Resolution:** 3-12 Months."

        # 11. BANKING OPERATIONS
        # 11. BANKING OPERATIONS (RBI COMPLIANT 2025)
        # 11. BANKING OPERATIONS
        elif current_topic_key == "BANKING_OPS":
            if "NOMINEE" in task_upper:
                # --- [CORRECTED] LEGAL & REGULATORY COMPLIANCE BLOCK ---
                specific_constraints = "Focus on Banking Regulation Act (Section 45ZA) & Rule 2(1) of Nomination Rules."
                
                # 1. Eligibility Correction: NRIs/Minors ARE allowed.
                eligibility_content = """
                * **Who can nominate:** Account holder (Individual/Sole Proprietor).
                * **Who can be a Nominee:**
                    * **Resident Indian:** Family member, friend, or any trusted person.
                    * **NRI/Foreign National:** Permitted (Subject to repatriation rules).
                    * **Minor:** Permitted, but you must appoint a **Guardian** (Appointee) to receive funds if the minor is <18 at the time of claim.
                """
                
                # 2. Document Correction: Nominee KYC is NOT required.
                documents_content = """
                **You generally do NOT need the Nominee's ID proof or Signature.**
                1. **Form DA-1:** The official statutory form for nomination.
                2. **Nominee Details Required:** Full Name, Age, Address, and Relationship.
                3. **For Minors:** Date of Birth of nominee + Name/Address of the Guardian (Appointee).
                4. **Witness:** Required **ONLY** if the account holder uses a Thumb Impression (illiterate). Literate account holders do NOT need witnesses for nomination.
                """
                
                # 3. Fee Correction: Statutory service, hence free.
                fees_content = "**NIL / Free.** Regulated entities (Banks/Insurers) do not charge for registering a nomination. Acknowledgement is mandatory."
                
                # 4. Process Nuance: Digital vs Physical
                timeline_content = """
                * **Net Banking (Instant):** Look for 'Service Request' > 'Update Nominee'.
                * **Branch (3-7 Days):** Submit physical Form DA-1. Ensure you get an **acknowledgement receipt**.
                """
                
                disclaimer = "**LEGAL NOTE:** Nomination is a 'Trusteeship'. The nominee receives the money as a custodian for the legal heirs, they do not automatically become the owner (unless they are also a legal heir)."
                
                extra_logic_output = ""
        # 12. BANKING CARDS
        elif current_topic_key == "BANKING_CARDS":
            if "CREDIT" in task_upper:
                specific_constraints = "Focus on RBI Master Direction on Credit Cards."
                disclaimer = "**FINANCIAL WARNING:** Paying only 'Minimum Amount Due' attracts massive interest (30-45%)."
                eligibility_content = "Resident, Income > ₹25k, CIBIL 750+."
                documents_content = "1. **KYC**.\n2. **PAN**.\n3. **Income Proof**."
                fees_content = "**Interest:** 3-4% per month. **Annual Fee:** Variable."
                timeline_content = "**Approval:** 3-7 Days."
            else:
                pass # Default logic

        # 13. BANKING DISPUTE
        # 13. BANKING DISPUTE (UPDATED FOR AGGRESSIVE ESCALATION)
        elif current_topic_key == "BANKING_DISPUTE":
            if "FREEZE" in task_upper or "LIEN" in task_upper:
                specific_constraints = "Focus on 'Deficiency of Service' under Consumer Protection Act 2019."
                disclaimer = "**LEGAL REALITY:** For Cyber freezes, the Bank needs a Police NOC to unfreeze. If they delay after NOC, it is a violation."
                
                eligibility_content = "Account Holder with a **Police NOC** or Court Order."
                
                documents_content = """
                1. **Police NOC:** Physical or Digitally Signed copy stating "No Objection" to unfreezing.
                2. **Application Letter:** Citing "Deficiency of Service".
                3. **KYC Documents:** Fresh Pan/Aadhaar (if requested).
                """
                
                fees_content = "**NIL.** Banks cannot charge for removing a lien if the case is cleared."
                timeline_content = "**Nodal Officer:** 7 Working Days (Mandatory turnaround time)."
                
                # INJECTING THE KILLER TEMPLATE
                eligibility_content += """
                
                ### ⚡ Recommended Email Strategy:
                Don't just "Request". **Demand.** Use this template structure:
                * **Subject:** FINAL ESCALATION: Unlawful Lien on Acct [No] - NOC Attached.
                * **Legal Ground:** Cite "Deficiency of Service" for delaying funds after legal clearance.
                * **Ultimatum:** Give them **7 Days** before escalating to RBI Ombudsman.
                """

        # 14. BUSINESS REG
        elif current_topic_key == "BIZ_REG":
            if "SHOP" in task_upper:
                specific_constraints = "State Labour Dept & Intimation vs Registration."
                disclaimer = "Displaying Signboard in local language is mandatory."
                eligibility_content = "0-9 Employees (Intimation). 10+ (Registration)."
                documents_content = "1. **ID Proof**.\n2. **Shop Photo**.\n3. **Address Proof**."
                fees_content = "State Specific (e.g. ₹23.60)."
                timeline_content = "Instant to 7 Days."
            elif "GST" in task_upper:
                specific_constraints = "Focus on Registration Thresholds."
                eligibility_content = "Turnover > ₹40L (Goods) or ₹20L (Services)."
                documents_content = "1. **PAN**.\n2. **Aadhaar**.\n3. **Business Proof**.\n4. **Bank Details**."
                fees_content = "**Govt Fee:** NIL."
                timeline_content = "3-7 Working Days."
                extra_logic_output = ""
            else: # MSME
                specific_constraints = "Focus on Udyam Portal."
                disclaimer = "**FRAUD ALERT:** Udyam Registration is **FREE**."
                eligibility_content = "Micro/Small/Medium based on Investment & Turnover."
                documents_content = "**Aadhaar Number** only."
                fees_content = "**FREE.**"
                timeline_content = "**Instant.**"

        # 15. TRAVEL DOCS
        elif current_topic_key == "TRAVEL_DOCS":
            if "OCI" in task_upper:
                specific_constraints = "MHA OCI Guidelines."
                disclaimer = "**CRITICAL:** OCI is NOT Dual Citizenship."
                eligibility_content = "Foreign National eligible for Indian citizenship in 1950."
                documents_content = "1. **Indian Origin Proof**.\n2. **Renunciation Cert**.\n3. **Foreign Passport**."
                fees_content = "USD 275."
                timeline_content = "4 to 12 Weeks."
            elif "FRRO" in task_upper:
                specific_constraints = "e-FRRO Portal."
                disclaimer = "Register within 14 days if stay > 180 days."
                eligibility_content = "Foreign Nationals visiting India."
                documents_content = "Passport, Visa, Form C."
                fees_content = "NIL (if on time)."
                timeline_content = "3-7 Days."
            elif "VISA" in task_upper:
                specific_constraints = "e-Visa vs Regular Visa."
                disclaimer = "Use ONLY official .gov.in website."
                documents_content = "Passport, Photo."
                fees_content = "$10 to $80."
                timeline_content = "24-72 Hours."
                extra_logic_output = ""
            else: # Passport
                disclaimer = "Police Verification is mandatory."
                eligibility_content = "Indian Citizens."
                documents_content = "Address Proof, DOB Proof."
                fees_content = "Fresh: ₹1,500. Tatkaal: ₹3,500."
                timeline_content = "Normal: 20-30 Days. Tatkaal: 1-3 Days."
                extra_logic_output = ""

        # 16. TRAVEL RULES
        elif current_topic_key == "TRAVEL_RULES":
            specific_constraints = "Baggage Rules 2016."
            disclaimer = "**WARNING:** Gold Allowance applies ONLY if stay > 1 year."
            eligibility_content = "Indian Resident returning."
            documents_content = "Passport."
            fees_content = "**Gold Allowance:** Women ₹1L, Men ₹50k."
            timeline_content = "Instant."

        # 17. TRAVEL INSURANCE
        elif "INSURANCE" in task.upper() and "TRAVEL" in task.upper():
            specific_constraints = "IRDAI regulations."
            disclaimer = "Travel Insurance is a Private Product."
            eligibility_content = "Valid Passport."
            documents_content = "Passport No, Travel Dates."
            fees_content = "Premium + 18% GST."
            timeline_content = "Instant."

        # 18. LIFE EVENTS (Marriage/Divorce)
        elif current_topic_key == "MARRIAGE_DIVORCE":
            legal_sys = IndianDivorceSystem()
            if "DIVORCE" in task_upper:
                info = legal_sys.get_legal_info("Mutual" if "MUTUAL" in task_upper else "Contested")
                eligibility_content = "Valid Marriage. Separation > 1 yr (Mutual)."
                documents_content = info['docs']
                fees_content = "Court Fees: Nominal."
                timeline_content = info['timeline']
                disclaimer = "**AUTHORITY:** Family Court."
            elif "NAME" in task_upper:
                disclaimer = "**IMPORTANT:** Marriage Certificate is usually sufficient proof."
                eligibility_content = "Indian Citizen."
                documents_content = "1. **Marriage Cert**.\n2. **Old IDs**.\n3. **Gazette** (if needed)."
                fees_content = "Aadhaar: ₹50. PAN: ₹107."
                timeline_content = "7-30 Days."
            else: # Marriage
                specific_constraints = "HMA vs SMA."
                disclaimer = "Foreign embassies require Marriage Certificate for visas."
                eligibility_content = "Groom 21+, Bride 18+."
                documents_content = "1. **Proof of Age**.\n2. **Address**.\n3. **Photos**.\n4. **Witnesses**."
                fees_content = "₹100 - ₹500."
                timeline_content = "HMA: 1-7 Days. SMA: 30 Days."
                extra_logic_output = ""

        # 19. SUCCESSION
        elif current_topic_key == "SUCCESSION":
            specific_constraints = "Legal Heir vs Succession Cert."
            disclaimer = "Legal Heir Cert is for low-value govt dues. Succession Cert is for Bank/Property."
            eligibility_content = "Class I Heirs."
            documents_content = "1. **Death Cert**.\n2. **ID Proofs**.\n3. **Affidavit**."
            fees_content = "**Legal Heir:** Nominal. **Succession:** % of assets."
            timeline_content = "Legal Heir: 15-30 Days. Succession: 6-9 Months."

        # 20. DIGITAL SAFETY
        elif current_topic_key == "CYBER_SAFETY":
            if "SIM" in task_upper:
                specific_constraints = "TAFCOP Portal."
                documents_content = "Active Mobile No."
                fees_content = "FREE."
                timeline_content = "Instant."
            elif "HACK" in task_upper:
                specific_constraints = "Platform Recovery."
                documents_content = "Recovery Email."
                fees_content = "FREE."
                timeline_content = "24-48 Hours."
            else:
                specific_constraints = "1930 Helpline."
                disclaimer = "**REALITY CHECK:** Call 1930 immediately."
                documents_content = "Transaction ID."
                fees_content = "NIL."
                timeline_content = "0-60 Mins (Golden Hour)."

        # 21. PAN
        elif current_topic_key == "PAN":
            specific_constraints = "NSDL/UTIITSL."
            eligibility_content = "Any person/entity."
            documents_content = "ID, Address, DOB Proof."
            fees_content = "₹107."
            timeline_content = "15-20 Days."

    # --- FINAL PROMPT GENERATION ---
    prompt = f"""
    You are an **Expert Consultant for complex life tasks in India**. Your primary goal is to ensure the final output is 99% accurate on process and facts.
    
    USER GOAL: {safe_task}
    
    {specific_constraints}
    
    RESEARCH DATA (Use this for context, but DO NOT override the hardcoded facts below):
    {research}
    
    TASK: Create a detailed Master Strategy. The headings and content below are the definitive sources for your response.
    
    OUTPUT FORMAT (Markdown):
    
    ## 🎯 Eligibility & Prerequisites
    {eligibility_content}
    
    ## 📄 Documents / Requirements
    {documents_content}
    
    ## 💰 Costs & Financials
    {fees_content}
    
    ## 👣 Step-by-Step Action Plan
    * [Provide the accurate, sequential process based on the user's specific request. Focus only on the identified topic. Do not mix steps from other processes.]
    
    ## ⏳ Timeline
    {timeline_content}
    
    ## 🔗 Official Links & Resources (Dynamic)
    {links_found}
    
    ## ⚠️ Official Disclaimer (Mandatory)
    {disclaimer}
    
    {extra_logic_output}
    """
    
    try:
        global client
        response = client.chat.completions.create(
            model=MODEL_NAME, 
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Generation Error: {str(e)}"

# ==============================================================================
# 6. FINANCIAL SIMULATOR LOGIC
# ================================

# ==============================================================================
# 6. FINANCIAL SIMULATOR LOGIC (UPDATED WITH EMPLOYER RISK)
# ==============================================================================

def calculate_rejection_risk(salary_input, emis, credit_score, selected_bank, employer_type):
    # salary_input is now a single float/int
    nmi_estimate = float(salary_input) * 0.45 
    current_emis = float(emis) if emis else 0
    estimated_foir = (current_emis / nmi_estimate) if nmi_estimate > 0 else 1.0
    
    risk_foir = ""
    if estimated_foir > 0.60:
        risk_foir = f"High FOIR: Your existing EMIs eat up {(estimated_foir*100):.0f}% of your lending capacity."
    
    risk_cibil = ""
    score = int(credit_score.split('-')[0]) if '-' in credit_score else (750 if credit_score == '800+' else 600)
    if score < 700:
        risk_cibil = "Low Credit Score: Banks prefer 750+ for best rates."
        
    # Employer Category Risk Logic
    conservative_banks = ["SBI", "STATE BANK", "KOTAK", "PNB", "BARODA", "UNION", "BOI", "CANARA", "MAHARASHTRA", "UCO", "IOB", "CENTRAL", "INDIAN BANK", "PUNJAB & SIND"]
    is_conservative_target = any(cb in selected_bank.upper() for cb in conservative_banks)
    
    risks = []
    if risk_foir: risks.append(risk_foir)
    if risk_cibil: risks.append(risk_cibil)
    
    if "Startup" in employer_type or "Self-Employed" in employer_type:
        if is_conservative_target:
            risks.append(f"**Company Categorization Risk:** {selected_bank} is conservative. They often reject 'Startup/Unlisted' profiles even with high CIBIL. Consider HDFC/ICICI or NBFCs.")

    if not risks: 
        return "Very High Approval Likelihood", [], "Your profile looks solid."
    
    # Determine Status based on risks
    if len(risks) >= 2 or "Company Categorization Risk" in str(risks):
        return "Medium/High Rejection Risk", risks, "Try a different bank (Private/NBFC) or reduce EMIs."
    else:
        return "Medium Risk Profile", risks, "Close existing loans to lower FOIR."

# ==============================================================================
# 7. UI INTERFACE
# ==============================================================================

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ❓ Why 'Clear Hai'?")
    st.info("**Because Indian Bureaucracy is a Black Box.**\n\nWe decode the hidden rules so you don't have to pay agents.")
    st.markdown("---")
    st.caption("v2.1 | Data Sources: RBI, MHA, Income Tax Dept.")

# --- MAIN HEADER ---
st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 style='font-size: 3.5rem; margin-bottom: 0;'>✅ Clear Hai?</h1></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #94a3b8; margin-bottom: 40px;'>The 'Truth Machine' for Indian Banks, Visas & Laws.</p>", unsafe_allow_html=True)

# --- TRUST BADGES ---
st.markdown("""
<div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin-bottom: 50px;">
    <div style="background: #1e293b; border: 1px solid #334155; padding: 8px 18px; border-radius: 100px; font-size: 13px; font-weight: 600; color: #e2e8f0;">🛡️ RBI Aligned</div>
    <div style="background: #1e293b; border: 1px solid #334155; padding: 8px 18px; border-radius: 100px; font-size: 13px; font-weight: 600; color: #e2e8f0;">⚖️ Legally Verified</div>
    <div style="background: #1e293b; border: 1px solid #334155; padding: 8px 18px; border-radius: 100px; font-size: 13px; font-weight: 600; color: #e2e8f0;">🚫 No Agents</div>
</div>
""", unsafe_allow_html=True)

# --- DYNAMIC INPUT ---
task = st.text_input("What do you want to do in India?", placeholder="e.g. Apply for PAN Card, ITR Filing, PF Withdrawal, Stamp Duty Calculation")

# --- DETECT MODE ---
is_loan_task = any(kw in task.upper() for kw in LOAN_SIMULATOR_KEYWORDS)
master_plan = None 

# ==============================================================================
# 8. FINANCIAL MODE BLOCK (SIMULATOR)
# ==============================================================================
if is_loan_task:
    st.markdown("### 🏦 Loan Approval Chances Simulator (Financial Mode)")
    
    # Auto-Select Bank
    bank_index = 0
    # Expanded Bank List (18+ Banks)
    bank_list = [
        "State Bank of India (SBI)", "Punjab National Bank (PNB)", "Bank of Baroda", "Canara Bank", 
        "Union Bank of India", "Bank of India", "Indian Bank", "Central Bank of India", 
        "Indian Overseas Bank", "UCO Bank", "Bank of Maharashtra", "Punjab & Sind Bank",
        "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "IndusInd Bank", 
        "Yes Bank", "Federal Bank"
    ]
    
    for i, bank in enumerate(bank_list):
        if bank.upper().split('(')[0].strip() in task.upper() or ("SBI" in task.upper() and "State" in bank):
            bank_index = i
            break
    
    with st.form("rejection_simulator_form"):
        col1, col2 = st.columns(2)
        
        selected_bank = col1.selectbox("1. Which Bank are you applying to?", bank_list, index=bank_index)
        
        employer_type = col1.selectbox("2. Employer Type / Category", 
                                       ["Government / PSU", "MNC / Public Ltd", "Private Ltd", "Startup / Unlisted", "Self-Employed"])
        
        # CHANGED: Use Number Input for Salary
        salary_input = col2.number_input("3. Net Monthly Income (NMI) (₹)", min_value=0, value=50000, step=1000, format="%d")
        
        current_emis = col2.number_input("4. Total Existing EMIs / Month", min_value=0, value=5000, step=1000)
        
        credit_score_selected = st.select_slider("5. Approximate Credit Score (CIBIL)", options=["<650", "650-699", "700-749", "750-800", "800+"], value="750-800")
        
        shock_factor = st.checkbox("🔥 Activate 'Bank Truth Mode' to see hidden risks agents won't tell you.", value=True)
        
        submit_button = st.form_submit_button("Check Loan Approval Chances 🚀", type="primary")

    if submit_button:
        bank_name_full = f"Get a {selected_bank} Home Loan"
        
        with st.status("🧠 Running Bank Validation Check...", expanded=False) as status:
            likelihood, risks, fix = calculate_rejection_risk(salary_input, current_emis, credit_score_selected, selected_bank, employer_type)
            
            research_data, links_found = find_process_details(bank_name_full)
            master_plan = generate_master_plan(research_data, bank_name_full, links_found, mode="FINANCIAL")
            
            status.update(label="✅ Strategy Ready!", state="complete")

        st.divider()
        
        if "High Approval" in likelihood: score_color = "#33cc33" 
        elif "Medium" in likelihood: score_color = "#ff9900"
        else: score_color = "#ff0000"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 3px solid {score_color}; border-radius: 10px;">
            <h1 style="color: {score_color}; font-size: 32px; margin: 0;">{likelihood}</h1>
            <p style="font-size: 18px; margin: 0;">Based on {selected_bank} Rules</p>
        </div>
        """, unsafe_allow_html=True)
        
        if risks:
            st.markdown(f"### ⚠️ Rejection Risks Detected")
            for risk in risks: st.error(f"{risk}")
        
        st.markdown(f"### 🔧 Action Plan")
        st.info(fix)
        
        if shock_factor:
            st.divider()
            st.markdown("""
            <div class="truth-box">
                <h3>🔥 Bank Truth Mode Activated</h3>
                <p><strong>Hidden Rule:</strong> Banks rate your <b>Employer</b> just as strictly as they rate you. If your company is on their internal 'Negative List' (common for startups), even an 800 CIBIL score won't save the application.</p>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 9. GENERAL MODE BLOCK
# ==============================================================================
elif task:
    general_submit = st.button("Generate Strategy 🚀", type="primary")
    if general_submit:
        with st.status("🧠 Searching Official Government Channels...", expanded=True) as status:
            research_data, links_found = find_process_details(task)
            master_plan = generate_master_plan(research_data, task, links_found, mode="GENERAL")
            status.update(label="✅ Strategy Ready!", state="complete")

# ==============================================================================
# 10. RESPONSE CARD RENDERER
# ==============================================================================
if master_plan:
    st.markdown("---")
    st.markdown(f"""
    <div style="background: #0f172a; padding: 40px; border-radius: 24px; border: 1px solid #334155; box-shadow: 0 20px 50px rgba(0,0,0,0.5); color: #e2e8f0; margin-top: 20px;">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 25px; border-bottom: 1px solid #334155; padding-bottom: 20px;">
            <div style="background: #3b82f6; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px;">✨</div>
            <div>
                <span style="font-weight: 700; font-size: 20px; color: #f8fafc; display: block;">Verified Master Strategy</span>
                <span style="font-size: 14px; color: #94a3b8;">Generated for: {task}</span>
            </div>
        </div>
        <div style="line-height: 1.8; font-size: 16px; color: #cbd5e1; font-family: 'Inter', sans-serif;">
            {master_plan}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("📲 Share on WhatsApp", f"https://wa.me/?text=Found a strategy for {task} on ClearHai!", use_container_width=True)

# --- FOOTER ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.caption("Disclaimer: Information generated based on available online data and official guidelines. Always verify with official authorities.")
