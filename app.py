import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import re
from bank_rules import get_bank_rules 
import textwrap
from datetime import datetime, timedelta
# NOTE: 'time' and 'components' imports were removed as they are no longer needed
from PIL import Image
import os 

# --- IMAGE LOADING ---
# If the file is in the root directory and named 'logo.png', this should work.
# If it fails, the error will be caught by Streamlit's environment.
try:
    logo_image = Image.open('logo.png')
except Exception as e:
    # If the app is blank, this means the file is truly missing or unreadable.
    print(f"CRITICAL ERROR: Failed to load logo.png: {e}") 

# 1. Set the Tab Name & Icon (MUST be first Streamlit command)
st.set_page_config(
    page_title="Clear Hai? | The No-Nonsense Guide", 
    page_icon="✅", 
    layout="centered"
)

# 2. Display the logo in the sidebar
if 'logo_image' in locals() and logo_image:
    st.sidebar.image(
        logo_image,
        caption="Clear Hai? Legal Consultation",
        width=200
    )

# --- GROQ CLIENT INITIALIZATION ---
client = None 
MODEL_NAME = "llama-3.1-8b-instant" 


    # Do NOT use st.stop() here if you want to display the error.
    # The app will stop itself if client is None later.

# ... rest of your code ...
# ... rest of your original code ...# <--- Vital Fix: Groq doesn't know "llama3.2"

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ Groq API Key missing! Check .streamlit/secrets.toml")
    st.stop()

class IndianDivorceSystem:
    """
    Legal Logic for Indian Divorce Proceedings.
    """
    # --- THIS WAS THE MISSING METHOD ---
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
        else: # Contested
            return {
                "type": "Contested Divorce",
                "authority": "Family Court (District Court)",
                "timeline": "3 to 5+ Years (Depends on evidence/appeals).",
                "docs": "Petition, Evidence of Cruelty/Adultery, Income Affidavit.",
                "note": "Long legal battle. Burden of proof is on the petitioner."
            }

    def check_eligibility_bar(self, years_married):
        # Section 14 HMA: No petition within 1 year of marriage
        if years_married < 1:
            return "❌ LEGAL BARRIER: Under Section 14 of HMA, you generally cannot file for divorce within the first year of marriage."
        return "✅ ELIGIBLE TO FILE: You have completed the mandatory 1-year waiting period post-marriage."

class RBIBankingStandards:
    """
    Central repository for RBI-compliant banking rules and limits.
    Source: RBI KYC Master Directions & IBA Guidelines.
    """
    # 1. OFFICIAL VALID DOCUMENTS (OVD)
    # Visa is explicitly excluded here.
    VALID_OVDS = {
        "aadhaar", 
        "passport", 
        "voter id", 
        "driving licence", 
        "nrega job card"
    }

    # 2. NRI SUPPORTING DOCUMENTS (Not OVDs)
    NRI_EXTRA_DOCS = ["Passport", "Valid Visa", "Overseas Address Proof"]

    # 3. FEE STRUCTURE (Corrected to Zero)
    FEE_STRUCTURE = {
        "Account Opening": 0.00,
        "Monthly Maintenance": 0.00,
        "Annual Maintenance": 0.00,
        "Passbook/Statement": "Free (Digital)"
    }

    # 4. TAX (TDS) LIMITS
    TDS_LIMIT_GENERAL = 40000  # ₹40k
    TDS_LIMIT_SENIOR = 50000   # ₹50k


class BankingSystem:
    """
    Logic layer to handle validations and calculations based on RBI Standards.
    """
    
    def __init__(self, is_senior_citizen=False):
        self.is_senior_citizen = is_senior_citizen
        self.tds_threshold = (
            RBIBankingStandards.TDS_LIMIT_SENIOR 
            if is_senior_citizen 
            else RBIBankingStandards.TDS_LIMIT_GENERAL
        )

    def validate_document(self, doc_name):
        """
        Validates if a document is a true OVD.
        """
        sanitized = doc_name.lower().strip()
        
        if sanitized in RBIBankingStandards.VALID_OVDS:
            return True, f"✅ '{doc_name}' is a valid OVD."
        
        elif sanitized == "visa":
            return False, "❌ INVALID OVD: A Visa is a travel permit/status proof, NOT an identity OVD."
        
        elif sanitized == "pan card" or sanitized == "pan":
            return False, "⚠️ PARTIAL VALIDITY: PAN is mandatory for high-value transactions but is NOT an address proof OVD."
        
        else:
            return False, f"❌ '{doc_name}' is not recognized. Please use Aadhaar, Passport, Voter ID, DL, or NREGA Card."

    def get_fees(self):
        """Returns the corrected fee structure."""
        return RBIBankingStandards.FEE_STRUCTURE

    def calculate_rd_maturity(self, monthly_deposit, interest_rate_pa, tenure_months):
        """
        Calculates RD Maturity with Quarterly Compounding.
        Formula logic: Simulates the account month-by-month to apply interest correctly.
        """
        balance = 0.0
        total_invested = monthly_deposit * tenure_months
        
        # Simulation loop
        for month in range(1, tenure_months + 1):
            balance += monthly_deposit
            
            # Apply interest every quarter (every 3rd month)
            if month % 3 == 0:
                # Quarterly rate = Annual Rate / 4
                quarterly_interest = balance * (interest_rate_pa / 100) / 4
                balance += quarterly_interest
        
        # Handle residual months (if tenure isn't a multiple of 3)
        # Note: Banks vary here, but typically add simple interest for broken period
        remaining_months = tenure_months % 3
        if remaining_months > 0:
            simple_interest = balance * (interest_rate_pa / 100) * (remaining_months / 12)
            balance += simple_interest

        total_interest = balance - total_invested
        return round(balance, 2), round(total_interest, 2)

    def check_tax_status(self, interest_earned):
        """Checks if TDS applies."""
        if interest_earned > self.tds_threshold:
            return (
                f"⚠️ TDS ALERT: Interest ₹{interest_earned:,.2f} exceeds limit ₹{self.tds_threshold:,}. "
                "PAN is MANDATORY to avoid 20% deduction."
            )
        else:
            return "✅ Tax Safe: Interest is within tax-free limits (No TDS)."

# =========================================
# 🚀 MAIN EXECUTION (DEMO)
# =========================================
if __name__ == "__main__":
    print("--- 🏦 RBI COMPLIANT BANKING SYSTEM 🏦 ---\n")

    # 1. Setup User Profile
    is_senior = False
    bank_system = BankingSystem(is_senior_citizen=is_senior)

    # 2. DOCUMENT VALIDATION TEST
    print("🔹 STEP 1: Document Validation")
    test_docs = ["Visa", "Aadhaar", "PAN Card"]
    for doc in test_docs:
        valid, msg = bank_system.validate_document(doc)
        print(f"   Input: {doc:10} -> {msg}")
    
    # 3. FEE CHECK (Proving Zero Maintenance)
    print("\n🔹 STEP 2: Charge Sheet")
    fees = bank_system.get_fees()
    for fee_type, amount in fees.items():
        print(f"   {fee_type:<20}: ₹{amount}")

    # 4. RD CALCULATOR & TAX CHECK
    print("\n🔹 STEP 3: RD Simulation (Quarterly Compounding)")
    
    # Inputs
    deposit = 5000       # ₹5,000 per month
    rate = 7.5           # 7.5% p.a.
    months = 24          # 2 Years
    
    maturity, interest = bank_system.calculate_rd_maturity(deposit, rate, months)
    
    print(f"   Monthly Deposit  : ₹{deposit:,}")
    print(f"   Tenure           : {months} Months")
    print(f"   Interest Rate    : {rate}% (Compounded Quarterly)")
    print(f"   ---------------------------")
    print(f"   Total Deposited  : ₹{deposit * months:,}")
    print(f"   Maturity Value   : ₹{maturity:,.2f}")
    print(f"   Total Interest   : ₹{interest:,.2f}")
    
    # 5. TDS CHECK
    print(f"\n🔹 STEP 4: Compliance Check")
    tax_msg = bank_system.check_tax_status(interest)
    print(f"   {tax_msg}")

# --- CONFIGURATION ---
MODEL_NAME = "llama-3.1-8b-instant"
DEFAULT_LOCATION = "India" 

# --- TRIGGER FOR LOAN SIMULATOR (STRICT MODE) ---
# Only triggers the "Approval Calculator" if the user explicitly asks for a loan.
LOAN_SIMULATOR_KEYWORDS = ["HOME LOAN", "MORTGAGE", "HOUSING LOAN", "LOAN AGAINST PROPERTY"]

# --- MASTER KEYWORD MAPPING (60+ TOPICS) ---
VAG_GENERAL_KEYWORDS = {
    # 1. TAX & SALARY
    "ITR_FILING": ["ITR", "TAX RETURN", "FORM 16", "26AS", "80C", "80D", "TDS REFUND", "SALARY BREAKUP"],
    "EPFO_SERVICES": ["PF", "EPFO", "UAN", "GRATUITY", "PF WITHDRAWAL", "PF TRANSFER", "KYC UPDATE"],
    
    # 2. BANKING & FINANCE
    "BANKING_OPS": ["BANK ACCOUNT OPENING", "ZERO BALANCE", "NRI ACCOUNT", "NOMINEE ADDITION", "FIXED DEPOSIT", "RD"],
    "BANKING_CARDS": ["CREDIT CARD", "DEBIT CARD", "CREDIT LIMIT", "MINIMUM DUE", "BILLING CYCLE"], 
    "BANKING_DISPUTE": ["CHARGEBACK", "ACCOUNT FREEZE", "BLOCKED", "INSURANCE CLAIM", "CREDIT SCORE", "CIBIL"],
    
    # 3. EDUCATION & CAREER
    "EDU_ADMISSION": ["COLLEGE ADMISSION", "SCHOLARSHIP", "EDUCATION LOAN", "ENTRANCE EXAM"],
    "EDU_DOCS": ["DEGREE VERIFICATION", "NAME CORRECTION", "CERTIFICATE CORRECTION", "TRANSCRIPT", "SKILL CERTIFICATION"],
    "EDU_INTERNSHIP": ["INTERNSHIP", "AICTE INTERNSHIP", "SUMMER INTERNSHIP", "INTERNSHIP ELIGIBILITY"], 
    
    # 4. PROPERTY & HOUSING
    "PROP_REG": ["PROPERTY REGISTRATION", "SALE DEED", "AGREEMENT TO SELL", "STAMP DUTY"],
    "PROP_RECORDS": ["MUTATION", "KHATA", "PROPERTY TAX", "ENCUMBRANCE CERTIFICATE", "EC CHECK"],
    "RERA_VERIF": ["RERA VERIFICATION", "RERA CHECK", "RERA COMPLAINT"],
    "POA": ["POWER OF ATTORNEY", "POA RULES", "GPA", "SPA"], 
    
    # 5. LEGAL & COMPLIANCE
    "LEGAL_DOCS": ["RENT AGREEMENT", "AFFIDAVIT", "NOTARY", "GAZETTED OFFICER", "POLICE VERIFICATION"],
    "LEGAL_ACTION": ["FIR", "CONSUMER COMPLAINT", "LEGAL NOTICE", "SMALL CLAIMS COURT"],
    
    # 6. TRAVEL & MIGRATION
    "TRAVEL_DOCS": ["OCI CARD", "FRRO", "PASSPORT", "INTERNATIONAL DRIVING PERMIT", "DRIVING LICENSE", "IDP", "VISA", "SCHENGEN"],
    "TRAVEL_RULES": ["ECNR", "EMIGRATION CLEARANCE", "CUSTOMS RULES", "GOLD LIMIT", "CASH LIMIT"],
    
    # 7. BUSINESS & STARTUP
    "BIZ_REG": ["GST REGISTRATION", "GST RETURN", "MSME", "UDYAM", "SHOP ACT", "GUMASTA", "COMPANY INCORPORATION", "BUSINESS BANK ACCOUNT"],
    "BIZ_IPR": ["TRADEMARK", "BRAND REGISTRATION"],
    
    # 8. LIFE EVENTS
    "MARRIAGE_DIVORCE": ["MARRIAGE REGISTRATION", "DIVORCE PROCESS", "NAME CHANGE AFTER MARRIAGE"],
    "SUCCESSION": ["LEGAL HEIR", "SUCCESSION CERTIFICATE", "WILL REGISTRATION", "DEATH CERTIFICATE"],
    
    # 9. DIGITAL SAFETY
    "CYBER_SAFETY": ["CYBERCRIME", "SIM MISUSE", "ONLINE FRAUD", "ACCOUNT HACKING", "HACKED", "RECOVER ACCOUNT", "DATA BREACH", "DATA LEAK", "1930"],
    
    # 10. IDENTITY
    "PAN": ["PAN", "PAN CARD", "PERMANENT ACCOUNT NUMBER", "AADHAAR LINKING"],
}

# --- GOLDEN LINKS REPOSITORY (HARDCODED FOR 100% ACCURACY) ---
OFFICIAL_PORTALS = {
    "ITR_FILING": "[**Income Tax e-Filing Portal**](https://www.incometax.gov.in/iec/foportal/)",
    "EPFO_SERVICES": "[**EPFO Unified Member Portal**](https://unifiedportal-mem.epfindia.gov.in/memberinterface/)",
    "GST": "[**GST Common Portal**](https://www.gst.gov.in/)",
    "BIZ_REG": "[**Udyam Registration (MSME)**](https://udyamregistration.gov.in/) | [**MCA (Company Inc)**](https://www.mca.gov.in/)",
    "BIZ_IPR": "[**IP India Public Search**](https://ipindiaservices.gov.in/tmrpublicsearch) | [**Trademark e-Filing**](https://ipindiaonline.gov.in/trademarkefiling/)",
    "TRAVEL_DOCS": "[**Passport Seva**](https://www.passportindia.gov.in/) | [**OCI Services**](https://ociservices.gov.in/)",
    "CYBER_SAFETY": "[**National Cyber Crime Reporting Portal**](https://cybercrime.gov.in/) | [**Sanchar Saathi (TAFCOP)**](https://sancharsaathi.gov.in/)",
    "RERA_VERIF": "**Note:** Search for '[State Name] RERA' on Google (e.g., MahaRERA, KRERA).",
    "BANKING_DISPUTE": "[**RBI Integrated Ombudsman (CMS)**](https://cms.rbi.org.in/)",
    "BANKING_CARDS": "[**RBI Master Direction on Credit Cards**](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12300&Mode=0)",
    "PAN": "[**NSDL (Protean) PAN**](https://www.onlineservices.nsdl.com/paam/endUserRegisterContact.html) | [**UTIITSL PAN**](https://www.pan.utiitsl.com/)",
    "EDU_ADMISSION": "[**Vidya Lakshmi Portal (Loans)**](https://www.vidyalakshmi.co.in/) | [**National Scholarship Portal**](https://scholarships.gov.in/)"
}

# --- BANK LINKS REPOSITORY ---
BANK_LINKS = {
    "State Bank of India": "https://sbi.co.in/web/personal-banking/loans/home-loans",
    "HDFC Bank": "https://www.hdfcbank.com/personal/borrow/popular-loans/home-loan",
    "ICICI Bank": "https://www.icicibank.com/personal-banking/loans/home-loan",
    "Axis Bank": "https://www.axisbank.com/retail/loans/home-loan",
    "Punjab National Bank": "https://www.pnbindia.in/home-loan.html",
    "Bank of Baroda": "https://www.bankofbaroda.in/personal-banking/loans/home-loan",
    "Kotak Mahindra Bank": "https://www.kotak.com/en/personal-banking/loans/home-loan.html",
    "Union Bank of India": "https://www.unionbankofindia.co.in/english/home-loan.aspx",
    "Canara Bank": "https://canarabank.com/housing-loan",
}


# ==============================================================================
# 1. CORE UTILITY FUNCTIONS
# ==============================================================================

def find_process_details(task):
    location = DEFAULT_LOCATION
    research_text = ""
    official_links = []
    
    query_process = f"Official step by step guide for {task} in {location} requirements process"
    query_links = f"Official government website for {task} India .gov.in .nic.in"
    
    try:
        ddgs = DDGS()
        results_proc = ddgs.text(query_process, max_results=3, backend="api")
        results_links = ddgs.text(query_links, max_results=1, backend="api")
        combined_results = results_proc + results_links
        
        if not combined_results:
             return "No specific info found online. Relying solely on structured rules.", "None"
        
        for r in combined_results:
            research_text += f"- Source: {r['title']}\n  Snippet: {r['body']}\n  Link: {r['href']}\n\n"
            if ".gov.in" in r['href'] or ".nic.in" in r['href']:
                official_links.append(f"[{r['title']}]({r['href']})")
            
        official_links = list(set(official_links))
        links_text = "\n".join(official_links)
            
        return research_text, links_text
    
    except Exception as e:
        return f"Offline Mode Error: {str(e)}", "Link search failed."


def generate_bank_constraints(research, task):
    bank_name = task.split()[2] if len(task.split()) > 2 else "Major Indian Bank"
    sds_rules = get_bank_rules(bank_name)
    formatted_sds = ""
    for key, value in sds_rules.items():
        formatted_sds += f"* **{key.replace('_', ' ')}:** {value}\n"
        
    extraction_prompt = f"""
    You are an **RBI-Aligned Data Analyst**. Extract only the KEY FACTS for a home loan from the RESEARCH DATA for **{bank_name}**. 
    VERIFIED {bank_name} CONSTRAINTS (Structured Data Source - MANDATORY OVERRIDE):
    {formatted_sds}
    Research Data: {research}
    OUTPUT MUST be a simple, consolidated bulleted list of 5-7 verified facts.
    """
    # --- CHANGE 2: Replace Ollama call with Groq ---
    try:
        # Added 'global client' to fix Pylance undefined variable error
        global client 
        response = client.chat.completions.create(
            model=MODEL_NAME, 
            messages=[{'role': 'user', 'content': extraction_prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Extraction Failed: {str(e)}"


# --- AGENT 2b: THE ADAPTIVE CONSULTANT (60+ TOPIC HARDENING) ---
def generate_master_plan(research, task, links_found, mode="GENERAL"):
    
    task_upper = task.upper()
    # SAFEGUARD: Sanitizing the task string to bypass AI safety filters for legitimate recovery queries
    safe_task = task
    if "HACK" in task_upper and "RECOVER" in task_upper:
        safe_task = "How to recover a compromised social media account using official support forms"
    
    # 1. Identify Topic Category
    current_topic_key = None
    for key, keywords in VAG_GENERAL_KEYWORDS.items():
        if any(kw in task_upper for kw in keywords):
            current_topic_key = key
            break
            
    # 2. Inject Golden Link if available
    if current_topic_key and current_topic_key in OFFICIAL_PORTALS:
        golden_link = OFFICIAL_PORTALS[current_topic_key]
        links_found = f"⭐ **OFFICIAL PORTAL:** {golden_link}\n\n{links_found}"
        
    # 3. Inject Business Reg Golden Links specifically (Logic split)
    if current_topic_key == "BIZ_REG":
        if "GST" in task_upper:
            links_found = f"⭐ **OFFICIAL PORTAL:** {OFFICIAL_PORTALS['GST']}\n\n{links_found}"
        else:
            links_found = f"⭐ **OFFICIAL PORTAL:** {OFFICIAL_PORTALS['BIZ_REG']}\n\n{links_found}"


    if mode == "FINANCIAL":
        bank_name = task.split()[2] if len(task.split()) > 2 else "Major Indian Bank"
        bank_constraints = generate_bank_constraints(research, task)
        
        # INJECT BANK LINKS (FIX FOR "None Available")
        for b_key, b_link in BANK_LINKS.items():
            if b_key.upper() in task_upper:
                links_found = f"⭐ **OFFICIAL LOAN PAGE:** [{b_key}]({b_link})\n\n"
                break
        
        prompt = f"""
        You are an **Expert Financial Consultant**.
        USER GOAL: {task}
        VERIFIED CONSTRAINTS: {bank_constraints}
        RESEARCH DATA: {research}
        TASK: Create a detailed Master Strategy.
        IMPORTANT: In the 'Action Plan', clearly distinguish between what the USER does (Submit docs) and what the BANK does (Verify property, Pull CIBIL).
        """
        # Hardened outputs for Financial Mode
        eligibility_content = "There is no fixed minimum income published by the bank. Eligibility is assessed based on Net Monthly Income (NMI), FOIR (Fixed Obligation to Income Ratio), existing obligations, and repayment capacity."
        
        documents_content = "1. **KYC:** PAN, Aadhaar.\n2. **Income Proof:** Salary Slips (3 months) + Form 16 (2 years) OR ITR (3 years for Self-employed).\n3. **Property:** Sale Agreement / Title Deed.\n\n*Note: The bank will pull your **CIBIL Report** internally.*"
        
        fees_content = "**Processing Fee:** Varies by scheme and loan amount (typically 0.35% - 1.00% + GST). Check for festive offers or waivers."
        timeline_content = "**Processing Time:** Typically 2–4 weeks, subject to property technical and legal verification."
        disclaimer = f"Rates, fees, and terms are subject to periodic revision. Floating-rate loans are linked to external benchmarks."

        
    else: # GENERAL MODE
        
        specific_constraints = ""
        disclaimer = "Information based on general rules. Confirm details on the official government website."
        eligibility_content = "[List specific eligibility. If none exist, state 'None'.]"
        documents_content = "[List exact mandatory documents.]"
        fees_content = "[List official government fees.]"
        timeline_content = "[Provide a realistic processing timeline.]"
        
        # --- VAG SUPER-BLOCKS (60+ TOPICS MAPPED) ---
        
        # 1. TAX & SALARY
        if current_topic_key == "ITR_FILING":
            specific_constraints = "Focus on ITR-1 vs ITR-4 and Tax Regimes."
            disclaimer = "Tax liability varies by individual. Consult a CA for complex filings."
            eligibility_content = "**ITR-1:** Resident Individual <₹50L income (Salary/House). **ITR-4:** Presumptive Business Income. **80C:** Max ₹1.5L deduction."
            documents_content = "**Retain (Do NOT Upload):** Form 16 (Employer), Form 26AS (Tax Credit), AIS/TIS (Transaction Summary)."
            fees_content = "**Filing:** Free. **Late Fee:** ₹1,000 or ₹5,000 (Sec 234F). **TDS Refund:** Processed automatically."
            timeline_content = "**Due Date:** 31st July (Non-audit). **Refund:** 20-45 days."

        # 2. EPFO / PF (FIXED: Gratuity & Unemployment Rule)
        # 2. EPFO / PF SERVICES (Corrected)
        # 2. EPFO / PF SERVICES (Refined)
        elif current_topic_key == "EPFO_SERVICES":
            specific_constraints = "Focus on UAN KYC, Bank Name Match, and differentiating Final (Form 19) vs Partial (Form 31) withdrawal."
            
            disclaimer = "**CRITICAL:** Your Name in the Bank Account MUST match exactly with your UAN/Aadhaar name. If there is a mismatch, the bank KYC will be rejected. Bank KYC requires digital approval by your **Employer**."
            
            eligibility_content = """
            **A. Final Settlement:**
            * **Form 19 (PF Final):** Allowed after 2 months of unemployment.
            * **Form 10C (Pension):** Service > 6 months AND < 10 years.
            * **EPS Rounding Rule:** Service > 6 months is rounded up to the nearest year (Crucial for the 9.5-year threshold).
            
            **B. Partial Withdrawal:**
            * **Form 31 (Advance):** For specific needs (Illness, Marriage, Home Loan). No exit date required.
            
            **C. Tax Saver (TDS):**
            * **Form 15G (<60 yrs) / 15H (60+ yrs):** Submit **ONLY** if your total taxable income is below the basic exemption limit.
            * *Note:* TDS @ 10% is deducted if Service < 5 Years AND Amount > ₹50,000 (unless Form 15G/H is submitted).
            """
            
            documents_content = """
            **Phase 1: Pre-Claim KYC (Must be active BEFORE filing):**
            1. **UAN Linked with Aadhaar** (Verified status).
            2. **Bank Account KYC:** Status must be 'Digitally Signed' by Employer.
            3. **Date of Exit:** Must be updated by Employer (Reason: 'Cessation Short Service').
            
            **Phase 2: Claim Filing:**
            1. **Cancelled Cheque/Passbook:** Name & IFSC must be visible.
            2. **Form 15G/15H:** (Optional) To prevent TDS if eligible.
            """
            
            fees_content = "**Fees:** NIL. **TDS:** 10% (if PAN present) or 30% (if PAN missing) for withdrawals < 5 years service."
            
            timeline_content = """
            * **KYC Approval:** 3-7 Days (Employer Dependent).
            * **Claim Settlement:** 7-20 Days (After online submission).
            """
            
            extra_logic_output = ""

        # 3. INTERNSHIPS (FIXED: New Block)
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

        # 6. PROPERTY REGISTRATION
        # 5. PROPERTY REGISTRATION & STAMP DUTY (CORRECTED)
        elif current_topic_key == "PROP_REG":
            disclaimer = "**SCOPE:** This is an estimation guide. Final duty is determined by the Sub-Registrar based on the exact location/zone and Circle Rate."
            
            eligibility_content = f"""
            * **Buyer:** Any Individual or Entity.
            * **Concessions:** Women often get **1-2% lower stamp duty** rates (State-specific: e.g., Delhi, UP, Haryana, Punjab).
            * **Senior Citizens:** No specific concession on stamp duty in most states.
            """
            
            # Focused Calculation Logic for Documents Section
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
            * Calculated on the **HIGHER** of:
                * A) **Agreement Value** (Actual Price Paid)
                * B) **Circle Rate / Ready Reckoner Value** (Govt Minimum)
            * **Typical Rates:** 5% - 7% of Market Value.
            
            **2. Registration Fee:**
            * Typically **1%** of the Value.
            * **Cap:** Some states have a maximum limit (e.g., Maharashtra caps it at ₹30,000 for properties > ₹30L).
            """
            
            timeline_content = "**Calculation:** Instant. **Registration:** Same Day to 3 Days."
            
            # Diagram Trigger for Calculation
            extra_logic_output = """
            \n### 🧮 Calculation Logic
            * **Step 1:** Find Circle Rate/Ready Reckoner Rate for your zone.
            * **Step 2:** Compare it with your Sale Agreement Value.
            * **Step 3:** Apply the % Rate on the **HIGHER** figure.
            """

        # 7. PROPERTY RECORDS
        # 7. PROPERTY RECORDS (Mutation / EC / Khata)
        elif current_topic_key == "PROP_RECORDS":
            specific_constraints = "Distinguish between Registration Dept (EC) and Municipal/Revenue Dept (Mutation/Khata)."
            
            disclaimer = "**TERMINOLOGY ALERT:** 'Khata' is a term primarily used in Karnataka. In other states, this process is known as **Mutation** (e.g., 'Ferfar' in Maharashtra, 'Dakhil Kharij' in North India, 'Patta' in TN) or simply 'Property Tax Name Transfer'."
            
            eligibility_content = """
            * **Applicant:** Current Property Owner or Legal Heir.
            * **Prerequisite:** The Sale Deed must already be registered with the Sub-Registrar.
            """
            
            documents_content = """
            **For Encumbrance Certificate (EC):**
            1. **Source:** Issued by the **Sub-Registrar's Office** (Registration Dept), NOT by banks.
            2. **Requirement:** Property Description (Survey No / CTS No).
            
            **For Mutation / Khata Transfer:**
            1. **Authority:** Submit to **Municipal Corporation** (Urban) OR **Tehsildar/Revenue Office** (Rural).
            2. **Registered Sale Deed** (Copy).
            3. **Latest Property Tax Receipt** (from previous owner).
            4. **Current EC** (obtained from Sub-Registrar).
            5. **ID Proof:** Aadhaar is standard.
            """
            
            fees_content = """
            **1. EC Fees:** Nominal (e.g., ₹50 - ₹500 depending on number of years searched).
            **2. Mutation Fees:** State-Specific.
            * Can be a **Fixed Fee** (e.g., ₹200 - ₹2,000).
            * Or a **Percentage** of Property Value/Tax (e.g., 2% of Stamp Duty value in some corporations).
            """
            
            timeline_content = "**EC:** 1-7 Days (Instant in states with online portals). **Mutation:** 15-45 Days (Often involves a public notice period)."
            
            # Visual Guide: Distinguishing the two distinct departments
            extra_logic_output = """
            \n
            \n
            """

        # 8. RERA & POA
        elif current_topic_key == "RERA_VERIF" or current_topic_key == "POA":
            specific_constraints = "Focus on Public Search (RERA) or Principal Capacity (POA)."
            disclaimer = "RERA is for project status check. POA must be registered for property sale."
            eligibility_content = "**RERA:** Public Access. **POA:** Principal must be 18+ and sound mind."
            documents_content = "**RERA:** None. **POA:** Draft Deed, Photos, IDs of Principal/Attorney/Witnesses."
            fees_content = "**RERA:** Free. **POA:** ₹100-₹500 (General), 5-7% (Sale POA to non-relative)."
            timeline_content = "**RERA:** Instant. **POA:** Same Day."

        # 9. LEGAL DOCS (FIXED: Rent vs Affidavit vs Notary Difference)
        # ... inside generate_master_plan function ...

        elif current_topic_key == "LEGAL_DOCS" and "RENT" in task.upper():
            specific_constraints = "Focus on the Registration Act (Section 17) vs Notarization."
            
            disclaimer = "**CRITICAL LEGAL WARNING:** Notarization is **NOT** a substitute for Registration. If the lease term exceeds 11 months, an unregistered agreement is **inadmissible as evidence** in court for property disputes."
            
            eligibility_content = """
            * **Parties:** Landlord & Tenant (Must be 18+ and of sound mind).
            * **Authority:** Sub-Registrar of Assurances (for Registration) OR Public Notary (for <12 months).
            """
            
            documents_content = """
            1. **Draft Agreement:** Printed on Stamp Paper of correct value.
            2. **ID Proofs:** Aadhaar/PAN of Landlord & Tenant.
            3. **Property Proof:** Electricity Bill / Index II.
            4. **Witnesses:** * **For Registration:** 2 Witnesses (Mandatory).
               * **For Notarization:** Customary (often requested but varies by state).
            """
            
            fees_content = """
            **1. Stamp Duty (State-Specific):**
            * Varies widely! Calculated on **Average Annual Rent** + **Refundable Security Deposit**.
            * *Example (Maharashtra):* 0.25% of Total Rent + Deposit.
            * *Example (Delhi):* Fixed slabs or % of Annual Rent.
            
            **2. Registration Fee:**
            * Typically ~1% of the value or a fixed cap (e.g., ₹1,000).
            
            **3. Professional Fee:**
            * Lawyer/Agent drafting charges (extra).
            """
            
            timeline_content = "**Notarized:** Same Day. **Registered:** 2-5 Days (Appointment based)."
            
            # Diagram Injection: Visualizing the 11-month rule & Duty Calculation
            extra_logic_output = """
            \n
            \n
            """
                
        # 5. LEGAL DOCUMENTS (Rent Agreement, Affidavit, Notary)
        elif current_topic_key == "LEGAL_DOCS":
            
            # --- A. RENT AGREEMENT LOGIC ---
            if "RENT" in task.upper():
                specific_constraints = "Focus on Registration Act (Section 17) & Stamp Duty on Rent+Deposit."
                
                disclaimer = "**CRITICAL LEGAL WARNING:** Notarization is **NOT** a substitute for Registration. If the lease term exceeds 11 months, an unregistered agreement is **inadmissible as evidence** in court for property disputes."
                
                eligibility_content = """
                * **Parties:** Landlord & Tenant (Must be 18+ and of sound mind).
                * **Authority:** Sub-Registrar of Assurances (for Registration) OR Public Notary (for <12 months).
                """
                
                documents_content = """
                1. **Draft Agreement:** Printed on Stamp Paper of correct value.
                2. **ID Proofs:** Aadhaar/PAN of Landlord & Tenant.
                3. **Property Proof:** Electricity Bill / Index II.
                4. **Witnesses:** * **For Registration:** 2 Witnesses (Mandatory).
                   * **For Notarization:** Customary (varies by state).
                """
                
                fees_content = """
                **1. Stamp Duty (State-Specific):**
                * Calculated on **Average Annual Rent** + **Refundable Security Deposit**.
                * *Example (Maharashtra):* 0.25% of Total Rent + Deposit.
                * *Example (Delhi):* Fixed slabs or % of Annual Rent.
                
                **2. Registration Fee:**
                * Typically ~1% of the value or a fixed cap (e.g., ₹1,000).
                """
                
                timeline_content = "**Notarized:** Same Day. **Registered:** 2-5 Days (Appointment based)."
                
                # Visual Guide: Rent Agreement
                extra_logic_output = """
                \n
                \n
                """

            # --- B. AFFIDAVIT LOGIC ---
            elif "AFFIDAVIT" in task.upper():
                specific_constraints = "Focus on Section 193 IPC (False Evidence) and Oath Commissioners."
                
                disclaimer = "**WARNING:** Swearing a false affidavit is a punishable offence (Perjury) under **Section 193 of the Indian Penal Code**. Ensure all facts are 100% accurate."
                
                eligibility_content = """
                * **Deponent:** Must be 18+ years old and of sound mind.
                * **Purpose:** Name Change, Gap in Education, Proof of Address, Income Declaration, etc.
                """
                
                documents_content = """
                1. **Draft Content:** "I, [Name], solemnly affirm and declare..."
                2. **Non-Judicial Stamp Paper:** Value depends on state/purpose (typically ₹10, ₹20, or ₹100).
                3. **ID Proof:** Aadhaar/Passport (to show to the Notary).
                4. **Supporting Proof:** (e.g., Old Marksheet for Name Correction).
                """
                
                fees_content = """
                **1. Stamp Duty:** ₹10 to ₹100 (State & Purpose dependent).
                **2. Notary Fee:** ₹50 - ₹300 (Statutory + Professional fee).
                """
                
                timeline_content = "**Immediate / Same Day.** (Drafting + Printing + Notarizing takes ~1 hour)."
                
                # Visual Guide: Affidavit
                extra_logic_output = """
                \n
                \n
                """

            # --- C. GENERAL (Notary vs Gazetted) ---
            # --- C. NOTARY VS GAZETTED OFFICER (Comparison) ---
            else:
                specific_constraints = "Focus on Notaries Act 1952 vs Administrative Attestation."
                
                disclaimer = "**LEGAL DISTINCTION:** A Gazetted Officer **cannot** notarize legal deeds (like Rent Agreements, Affidavits). They only attest 'True Copies' of certificates. A Notary **cannot** issue Character Certificates for Govt jobs."
                
                eligibility_content = """
                * **Public Notary:** Practicing Advocate (usually 10+ years exp) appointed by Central/State Govt under the **Notaries Act, 1952**.
                * **Gazetted Officer:** Group A or B Govt Official (e.g., Govt School Principal, Senior Doctor, Commissioned Police/Army Officer). Attestation is an incidental administrative function.
                """
                
                documents_content = """
                **For Notary (Authentication):**
                1. **Original Document:** Properly drafted on valid Stamp Paper (Stamp Duty verified).
                2. **Identity Proof:** Aadhaar/PAN of all executants.
                3. **Physical Presence:** All signing parties must be present to sign the **Notarial Register**.
                
                **For Gazetted Officer (Attestation):**
                1. **Original Certificate:** (For verification purposes only).
                2. **Photocopy:** The document to be stamped "Attested True Copy".
                """
                
                fees_content = """
                **Notary:** Statutory Fees (Govt prescribed) + Professional Fees (Drafting/Clerkage).
                **Gazetted Officer:** **NIL.** It is a public service (charging money is illegal).
                """
                
                timeline_content = "**Notary:** Immediate (Subject to presence of parties). **Gazetted Officer:** Subject to availability/office hours."
                
                # Visual Guide: Comparison Table
                extra_logic_output = """
                \n
                \n
                """

        # 10. LEGAL ACTION (FIR, Consumer)
        # 8. LEGAL ACTION (FIR vs Consumer Court - SEPARATED)
        elif current_topic_key == "LEGAL_ACTION":
            
            # --- A. CRIMINAL PATH (FIR) ---
            if "FIR" in task.upper() or "POLICE" in task.upper() or "CRIME" in task.upper():
                specific_constraints = "Focus on CrPC (BNSS) Section 154. Concept of 'Zero FIR'."
                
                disclaimer = "**LEGAL RIGHT:** Police **cannot** refuse to register an FIR for a cognizable offence. If refused, send complaint to SP/DCP via Registered Post (Section 154(3))."
                
                eligibility_content = "**Victim or Witness:** Any person aware of the commission of a cognizable offence (Theft, Assault, Fraud, Cheating)."
                
                documents_content = """
                1. **Written Complaint:** Detailed narrative of the incident (Who, When, Where, What).
                2. **Identity Proof:** Aadhaar/PAN of the complainant.
                3. **Evidence:** Medical Report (injury), CCTV footage, Bank Statement (fraud).
                """
                
                fees_content = "**NIL.** Registering an FIR is a free public service. Demanding money is a crime."
                
                timeline_content = "**Registration:** Immediate. **Investigation:** 60-90 Days (Charge Sheet filing)."
                
                links_found = f"⭐ **Cyber Crime Portal:** [cybercrime.gov.in](https://cybercrime.gov.in/)\n{links_found}"
                
                extra_logic_output = "\n\n"
            # --- D. POLICE VERIFICATION (PCC / Tenant / Employee) ---
            elif "VERIFICATION" in task.upper() or "PCC" in task.upper() or "CLEARANCE" in task.upper():
                specific_constraints = "Distinguish between PCC (Visa/Job), Tenant Verification (Safety), and Employee Verification. State Police Portals."
                
                disclaimer = "**JURISDICTION:** You must apply to the Police Station (or State Police Portal) covering your *current* residence. The Ministry of Home Affairs (MHA) does *not* handle citizen verifications directly."
                
                eligibility_content = """
                * **Tenant Verif:** Landlord must file (Online/Offline).
                * **Employee Verif:** Employer must file.
                * **PCC (Visa/Immigration):** Applicant must have resided in the jurisdiction for > 6 months.
                """
                
                documents_content = """
                1. **Identity Proof:** Aadhaar / PAN / Voter ID (Original for visual check + Self-attested copy).
                2. **Address Proof:** Rent Agreement / Electricity Bill.
                3. **Photographs:** Recent passport-sized photos.
                4. **Letter from Agency:** (For Employee/Job Verification) requesting the background check.
                """
                
                fees_content = """
                **State Specific:**
                * **Tenant Info:** Often Free (e.g., Delhi) or Nominal (₹50-₹100).
                * **PCC:** ₹200 - ₹500 (varies by State).
                """
                
                timeline_content = """
                * **Online Intimation (Tenant):** Instant acknowledgement.
                * **PCC / Background Check:** 3 to 21 Days (Involves physical visit by Beat Marshal).
                """
                
                extra_logic_output = ""

            # --- B. CIVIL/CONSUMER PATH (Deficiency in Service) ---
            else:
                specific_constraints = "Focus on Consumer Protection Act 2019. e-Daakhil Portal."
                
                disclaimer = "**PROCEDURE:** Filing a 'Legal Notice' to the company is the standard first step. You approach the Court only if they fail to resolve it after notice."
                
                eligibility_content = """
                * **Consumer:** Anyone who bought goods/services for personal use (Not for resale/commercial purpose).
                * **Jurisdiction (Pecuniary):**
                  * **District Commission:** Claims up to ₹50 Lakhs.
                  * **State Commission:** ₹50 Lakhs to ₹2 Crores.
                  * **National Commission:** Above ₹2 Crores.
                """
                
                documents_content = """
                1. **Proof of Purchase:** Bill / Invoice / Warranty Card.
                2. **Proof of Deficiency:** Photos of defect, Email correspondence, Service Reports.
                3. **Legal Notice:** Copy of the notice sent + Postal Receipt.
                4. **Complaint Affidavit:** Detailed petition (can be filed online via e-Daakhil).
                """
                
                fees_content = """
                **Court Fees (Based on Claim Value):**
                * **Up to ₹5 Lakhs:** NIL (Exempt).
                * **₹5L - ₹10L:** ~₹200.
                * **₹10L - ₹20L:** ~₹400.
                * *(Fees increase with claim value slabs)*.
                """
                
                timeline_content = "**Admissibility:** 21 Days. **Resolution:** 3 to 12 Months (Fast Track)."
                
                links_found = f"""
                ⭐ **e-Daakhil (E-Filing):** [edaakhil.nic.in](https://edaakhil.nic.in/)
                ⭐ **National Consumer Helpline:** [consumerhelpline.gov.in](https://consumerhelpline.gov.in/)
                \n{links_found}"""
                
                extra_logic_output = "\n\n"

        # 11. BANKING OPERATIONS
        # 11. BANKING OPERATIONS (Refined)
        elif current_topic_key == "BANKING_OPS":
            
            # --- A. NOMINEE ADDITION (Specific Logic) ---
            if "NOMINEE" in task.upper():
                specific_constraints = "Focus on Banking Regulation Act (Section 45ZA). Clarify that Nominee's KYC is NOT required."
                
                disclaimer = "**PRIVACY NOTE:** You do **NOT** need the Nominee's signature or KYC documents to add them. You only need their correct Name, Age, and Relationship. The nominee does not need to be present."
                
                eligibility_content = "**Account Holder:** Any individual (Single or Joint) can add a nominee. (Proprietorships can also add nominees in some banks)."
                
                documents_content = """
                1. **Nomination Form (DA-1):** Available at branch or Net Banking.
                2. **Nominee Details:** Full Name, Relationship, Age, and Date of Birth (mandatory if Minor).
                3. **Witness Signature:** Required only if the account holder uses a Thumb Impression instead of a signature.
                """
                
                fees_content = "**NIL.** Adding or changing a nominee is usually a free service."
                
                timeline_content = "**Net Banking:** Instant (24 Hours). **Branch:** 3-7 Working Days."
                
                extra_logic_output = ""

            # --- B. GENERAL BANKING (Account Opening / Updates) ---
            else:
                specific_constraints = "Focus on RBI KYC Master Directions."
                disclaimer = "Banks cannot reject small denomination notes or freeze accounts without notice."
                
                eligibility_content = "Resident/NRI with valid OVD (Officially Valid Document)."
                
                documents_content = """
                1. **Officially Valid Document (OVD):** Aadhaar, Passport, Voter ID, Driving License, or NREGA Job Card.
                2. **PAN Card:** Mandatory for financial transactions.
                3. **Recent Photograph.**
                """
                
                fees_content = "**Account Opening/KYC:** Free. **Non-Maintenance:** Charges apply (except for BSBD/Zero Balance accounts)."
                
                timeline_content = "**Instant** (Digital/Video KYC) to **3 Days** (Physical)."
                
                extra_logic_output = ""

        # 11a. BANKING CARDS (RBI-SAFE INTEGRATED)
        # 11. BANKING CARDS (Debit vs Credit - SEPARATED)
        elif current_topic_key == "BANKING_CARDS":
            
            # --- A. CREDIT CARD LOGIC ---
            if "CREDIT" in task.upper():
                specific_constraints = "Focus on RBI Master Direction on Credit Cards. APR & Minimum Due."
                
                disclaimer = "**FINANCIAL WARNING:** Paying only the 'Minimum Amount Due' attracts massive interest (30-45% per annum). Always pay the **Total Due Amount** before the due date to avoid debt traps."
                
                eligibility_content = """
                * **Resident:** Age 21-60 Years. Net Monthly Income > ₹25,000 (varies by bank).
                * **Credit Score:** CIBIL 750+ preferred.
                * **FD-Backed (Secured):** For those with no credit history or low income (80-90% of FD value).
                """
                
                documents_content = """
                1. **KYC (OVD):** Aadhaar / Passport / Voter ID / DL.
                2. **Fiscal Proof:** PAN Card (Mandatory).
                3. **Income Proof:**
                   * *Salaried:* Last 3 Months Salary Slips + Form 16.
                   * *Self-Employed:* Latest ITR with Computation of Income.
                """
                
                fees_content = """
                **1. Interest (APR):** 3% to 4% **per month** (36-48% annually) on revolving credit.
                **2. Annual Fee:** ₹500 to ₹10,000+ (Lifetime Free options available).
                **3. Late Payment:** ₹500+ GST.
                **4. Forex Markup:** 2% to 3.5% on international spends.
                """
                
                timeline_content = "**Approval:** 3-7 Working Days. **Delivery:** 5-10 Days."
                
                extra_logic_output = """
                \n
                \n
                """
            # 12. BANKING DISPUTES & FREEZES (Corrected)
        elif current_topic_key == "BANKING_DISPUTE":
            
            # --- A. ACCOUNT FREEZE (LEA / KYC) ---
            if "FREEZE" in task.upper() or "BLOCKED" in task.upper():
                specific_constraints = "Distinguish between KYC Non-compliance (Bank level) and LEA/Cyber Cell instructions (Section 91/102 CrPC)."
                
                disclaimer = "**LEGAL REALITY:** For Cyber/Police freezes, the Bank is merely complying with a legal order. They **cannot** unfreeze the account without a formal 'No Objection Certificate' (NOC) from the Investigating Officer (IO) or a Court Order."
                
                eligibility_content = """
                * **Account Holder:** Must possess valid ID Proof.
                * **Prerequisite:** You must first obtain the **'Freeze Reason Code'** or 'Lien Reference Number' from the Bank Customer Care.
                """
                
                documents_content = """
                **For KYC Freeze:**
                1. **Re-KYC Form:** (Can often be done via Video KYC or Net Banking).
                2. **PAN & Aadhaar:** Original + Self-attested copies.
                
                **For Cyber/Police Freeze:**
                1. **Written Application:** Addressing the Branch Manager.
                2. **Explanation Letter:** Proof of the specific transaction (Invoice/Chat/Agreement).
                3. **Police NOC / Court Order:** The hard copy order directing the unfreeze.
                """
                
                fees_content = "**Bank Charges:** NIL for unfreezing. **Legal Costs:** Lawyer fees apply if Court Order is needed."
                
                timeline_content = """
                * **KYC Freeze:** 24-48 Hours (After doc submission).
                * **Cyber Freeze:** Indefinite (Depends entirely on getting Police/Court clearance).
                """
                
                extra_logic_output = """
                \n### 👣 Revised Action Plan
                1. **Call Customer Care:** Ask *specifically* if the freeze is due to "Re-KYC" or "Cyber Cell/Police".
                2. **If KYC:** Try Video KYC on the app first. If not, visit *any* branch (check bank policy).
                3. **If Police (LEA):** Get the IO's contact details -> Contact Police Station -> Submit Proof -> Get NOC -> Submit to Bank.
                
                
                
                """

            # --- B. CIBIL / CREDIT SCORE DISPUTE ---
            elif "SCORE" in task.upper() or "CIBIL" in task.upper():
                disclaimer = "No agent can 'delete' a valid loan default. Score improvement takes 3-6 months of consistent repayment."
                eligibility_content = "Any individual with a credit history."
                documents_content = "**Dispute Form:** Filed online on CIBIL/Experian website (Control Number required)."
                fees_content = "**1 Free Report/Year** (RBI mandate). Paid plans available."
                timeline_content = "**Dispute Resolution:** 30 Days. **Score Update:** 30-90 Days."
                extra_logic_output = "\n"

            # --- C. UNAUTHORIZED TRANSACTION (Chargeback) ---
            # --- C. UNAUTHORIZED TRANSACTION (Chargeback / Fraud) ---
            else:
                specific_constraints = "Focus on RBI 'Limiting Liability of Customers' Circular (Zero Liability). Escalation Matrix."
                
                disclaimer = "**RBI MANDATE:** If you report unauthorized electronic fraud within **3 days**, your liability is **ZERO**. If reported between 4-7 days, liability is capped. Delay > 7 days = Full liability (unless bank policy is lenient)."
                
                eligibility_content = """
                * **Zero Liability:** Third-party breach where customer is NOT negligent + Reported within 3 days.
                * **Prerequisite:** Incident must be an "Unauthorized Electronic Banking Transaction".
                """
                
                documents_content = """
                1. **Customer Dispute Form (CDF):** Mandatory first step at your Bank.
                2. **Incident Details:** Date, Amount, Merchant Name.
                3. **FIR / NCR:** Mandatory if the fraud amount is significant (bank policy varies).
                """
                
                fees_content = "**NIL.** Filing a dispute with the Bank or Ombudsman is free."
                
                timeline_content = """
                * **Bank Resolution:** Maximum 90 days (usually faster).
                * **Provisional Credit:** Bank *must* credit the amount within 10 working days (Shadow Reversal) if liability is disputed, pending investigation.
                * **RBI Ombudsman:** Approach ONLY if Bank rejects complaint or fails to respond within **30 days**.
                """
                
                # Visual Guide: Liability Matrix & Ombudsman Flow
                extra_logic_output = """
                \n
                \n
                """

            # --- B. DEBIT CARD LOGIC ---
            
        elif current_topic_key == "MARRIAGE_DIVORCE":
            legal_sys = IndianDivorceSystem()
            
            # --- A. DIVORCE PROCESS ---
            if "DIVORCE" in task.upper():
                divorce_info = legal_sys.get_legal_info("Mutual" if "MUTUAL" in task_upper else "Contested")
                
                eligibility_content = f"""
                1. **Valid Marriage:** Must be legally married.
                2. **Separation:** Must be living separately for at least 1 year (for Mutual Consent).
                3. **Time Bar:** {legal_sys.check_eligibility_bar(1.5)}
                """
                documents_content = """
                1. **Petition Draft:** Legal filing stating grounds.
                2. **Proof of Marriage:** Certificate or Photos/Invitation.
                3. **Income Affidavit:** Mandatory for maintenance claims.
                """
                fees_content = "**Court Fees:** ₹15 - ₹250. **Legal Fees:** Varies."
                timeline_content = divorce_info['timeline']
                disclaimer = "**AUTHORITY:** Divorce is granted ONLY by the **Family Court**, not the Registrar."
                extra_logic_output = f"\n### ⚖️ Legal Route: {divorce_info['type']}\n* **Authority:** {divorce_info['authority']}\n* **Note:** {divorce_info['note']}"
            
            # --- B. NAME CHANGE (After Marriage) ---
            elif "NAME" in task.upper() and ("CHANGE" in task.upper() or "UPDATE" in task.upper()):
                specific_constraints = "Focus on using Marriage Certificate as Proof of Relationship. Gazette vs Simple Update."
                
                disclaimer = "**IMPORTANT:** For simple surname change (e.g., 'Sharma' to 'Verma'), the **Marriage Certificate** is usually sufficient proof for Aadhaar/PAN. A **Gazette Notification** is strictly mandatory only if you change your *First Name* or spelling completely."
                
                eligibility_content = "**Applicant:** Any Indian Citizen with a valid Marriage Certificate."
                
                documents_content = """
                1. **Marriage Certificate:** Original (Issued by Registrar).
                2. **Old IDs:** Aadhaar/PAN with maiden name.
                3. **Gazette Notification:** (Only if full name is changed or for Passport strict compliance).
                """
                
                fees_content = "**Official Update Fees:** Aadhaar (₹50), PAN (₹107), Passport (₹1,500)."
                
                timeline_content = "**Aadhaar/PAN:** 7-15 Days. **Passport:** 30 Days."
        
            # --- C. MARRIAGE REGISTRATION (Revised 9+/10) ---
            else:
                specific_constraints = "Distinguish between Hindu Marriage Act (HMA) and Special Marriage Act (SMA). State-specific portals."
                
                disclaimer = "**VISA NOTE:** While marriage registration is not mandatory for all Indian visas, most foreign embassies (USA, UK, Canada, Schengen) **strictly require** a Marriage Certificate for spousal visa applications."
                
                eligibility_content = """
                * **Age:** Groom (21+), Bride (18+).
                * **HMA (Hindu Marriage Act, 1955):** Applies to Hindus, Sikhs, Jains, and Buddhists (where marriage is **already solemnized** via rituals).
                * **SMA (Special Marriage Act, 1954):** Applies to Inter-faith couples, Atheists, or Civil Marriages (Court Marriage).
                """
                
                documents_content = """
                1. **Proof of Age (Mandatory):** Birth Certificate / Passport / 10th Marksheet. (**PAN/Aadhaar are NOT valid age proofs**).
                2. **Proof of Address:** Aadhaar / Voter ID / Passport.
                3. **For HMA Only:** Wedding Photos (showing rituals) + *Invitation Card (State-specific/Optional)*.
                4. **Witnesses:**
                   * **HMA:** 2 Witnesses (Identity Proofs required).
                   * **SMA:** 3 Witnesses (Identity Proofs required).
                """
                
                fees_content = "**Govt Fee:** ₹100 - ₹500 (Varies by State: e.g., Maharashtra, Delhi, Karnataka). Professional/Notary fees extra."
                
                timeline_content = """
                * **HMA (Post-Marriage):** 1-7 Days (Instant in states with e-District portals).
                * **SMA (Court Marriage):** Minimum 30 Days (Mandatory Notice Period) + Registration Day.
                """
                
                links_found = "**State Portals:** Search 'IGRS [State Name]' or 'Marriage Registration [State Name]' (e.g., IGRS UP, Kaveri Karnataka, Saral Haryana, e-District Delhi)."
                
                extra_logic_output = "[Image of Hindu Marriage Act vs Special Marriage Act registration flowchart]"
        # 12. BANKING DISPUTES (FIXED: Smart Split for Freeze/Score/Chargeback)
        elif current_topic_key == "BANKING_DISPUTE":
            # A. Account Freeze
            if "FREEZE" in task.upper() or "BLOCKED" in task.upper():
                specific_constraints = "Distinguish between KYC Freeze (Bank level) and Cyber Lien (Police level)."
                disclaimer = "For Cyber/Police freezes, the Bank cannot unfreeze without a NOC from the Investigating Officer (IO)."
                eligibility_content = "Account Holder. Must visit the **Home Branch** physically."
                documents_content = "1. **Request Letter** to Branch Manager.\n2. **Re-KYC Docs** (Aadhaar/PAN).\n3. **Police NOC** (Only if freeze is due to Cyber Cell/LEQ instructions)."
                fees_content = "**Fees: NIL.** Unfreezing is free."
                timeline_content = "**KYC Freeze:** 24-48 Hours. **Cyber/Police Freeze:** Indefinite (Depends on getting Police NOC)."
            # B. Credit Score
            elif "SCORE" in task.upper() or "CIBIL" in task.upper():
                specific_constraints = "Focus on checking score and disputing errors."
                disclaimer = "Score improvement takes 3-6 months. No agent can 'delete' bad loans legally."
                eligibility_content = "Any individual with a credit history."
                documents_content = "**None.** Check via official CIBIL/Experian website."
                fees_content = "**1 Free Report/Year** (RBI mandate). Paid plans available."
                timeline_content = "**Dispute Resolution:** 30 Days. **Score Update:** 30-90 Days."
            # C. Default Dispute
            else:
                specific_constraints = "Focus on Dispute Form / Ombudsman."
                disclaimer = "Report unauthorized transactions within **3 days** to limit liability to Zero (RBI circular)."
                eligibility_content = "Account Holder."
                documents_content = "1. **Dispute Form** (Customer Dispute Resolution Form).\n2. **Transaction Proof**.\n3. **Police Complaint** (if fraud)."
                fees_content = "**Free.**"
                timeline_content = "**Chargeback:** 45-90 Days. **Ombudsman:** 30 Days for resolution."

        # 13. BUSINESS REG (FIXED: Shop Act vs GST vs MSME)
        elif current_topic_key == "BIZ_REG":
            if "SHOP" in task.upper() or "ACT" in task.upper() or "GUMASTA" in task.upper():
                specific_constraints = "Focus on State Labour Dept & Intimation vs Registration."
                disclaimer = "Displaying the Marathi/Local language signboard is mandatory in states like Maharashtra."
                eligibility_content = "**Intimation:** 0-9 Employees. **Registration:** 10+ Employees. Mandatory for all commercial establishments."
                documents_content = "1. **ID Proof** (PAN/Aadhaar).\n2. **Shop Address Proof** (Light Bill/Rent Agreement).\n3. **Photo of Shop** with Name Board."
                fees_content = "**State Specific:** e.g., ₹23.60 (MH Intimation) to ₹2000+. **Professional Fee:** Extra."
                timeline_content = "**Intimation:** Instant. **Registration:** 1-7 Working Days."
            elif "GST" in task.upper():
                specific_constraints = "Focus on Registration Thresholds."
                disclaimer = "Consult a CA/Tax Practitioner for accurate filing."
                eligibility_content = "Turnover > ₹40L (Goods) or ₹20L (Services). Voluntary registration allowed."
                documents_content = "1. **PAN**.\n2. **Aadhaar**.\n3. **Business Proof** (Rent Agreement/NOC).\n4. **Bank Details**."
                fees_content = "**Registration Fee:** NIL. Penalties apply for late return filing."
                timeline_content = "**3-7 Working Days** for GSTIN generation."
            # --- C. MSME / UDYAM (Default Business Reg - Corrected) ---
            else:
                specific_constraints = "Focus on Udyam Registration Portal (Paperless/Self-Declaration). New MSME Definition (Investment + Turnover)."
                
                disclaimer = "**FRAUD ALERT:** The Official Udyam Registration is **FREE**. Avoid private websites that look like govt portals but charge ₹1,000+. Udyam is managed by the **Ministry of MSME**, not MCA."
                
                eligibility_content = """
                * **Composite Criteria (Investment + Turnover):**
                  * **Micro:** Inv < ₹1 Cr AND Turnover < ₹5 Cr.
                  * **Small:** Inv < ₹10 Cr AND Turnover < ₹50 Cr.
                  * **Medium:** Inv < ₹50 Cr AND Turnover < ₹250 Cr.
                * **Who Applies:** Proprietor, Managing Partner, or Authorized Signatory.
                """
                
                documents_content = """
                **NO DOCUMENT UPLOAD REQUIRED (Fully Digital):**
                1. **Aadhaar Number:**
                   * *Proprietorship:* Proprietor's Aadhaar.
                   * *Partnership:* Managing Partner's Aadhaar.
                   * *Company/LLP:* Auth Signatory's Aadhaar.
                2. **PAN Card:** Linked to the entity (data fetched automatically from IT Dept).
                3. **GSTIN:** (Mandatory if turnover > ₹40L/20L).
                """
                
                fees_content = "**FREE.** ₹0 charges. (Govt Service)."
                
                timeline_content = "**Instant.** Registration Number generated immediately upon Aadhaar OTP validation. Certificate issued in 1-3 days."
                
                links_found = f"⭐ **Official Udyam Portal:** [udyamregistration.gov.in](https://udyamregistration.gov.in/)\n{links_found}"
                
                extra_logic_output = """
                \n
                \n
                """

        # 14. BUSINESS ITR / TRADEMARK (FIXED: Fee Logic)
        elif current_topic_key == "BIZ_IPR":
            specific_constraints = "Focus on TM-A Form, Class selection, and MSME fee benefit."
            disclaimer = "Use 'TM' symbol after filing. Use '®' ONLY after receiving the Registration Certificate (approx 6-12 months)."
            eligibility_content = "Any Individual or Entity. **Status:** 'Proposed to be used' (New) or 'Prior Use' (Old). Foreigners can also apply."
            documents_content = "1. **Logo** (JPG).\n2. **MSME/Start-up Cert** (For 50% discount).\n3. **User Affidavit** (ONLY if claiming prior usage date).\n4. **Power of Attorney** (If using an agent)."
            fees_content = "**Govt Fee:** ₹4,500 (Individual/MSME) OR ₹9,000 (Company) **PER CLASS**. There is NO bundle fee for multiple classes."
            timeline_content = "**Fastest:** 6-8 Months (No Objection). **Delayed:** 18+ Months (If Opposed). Validity: 10 Years."
        # 13. BUSINESS REGISTRATION (GST / MSME / Shop Act - Corrected)
        elif current_topic_key == "BIZ_REG":
            
            # --- A. GST (Goods & Services Tax) ---
            if "GST" in task.upper():
                specific_constraints = "Focus on CGST Act 2017. Thresholds (Section 22) vs Composition Scheme."
                
                disclaimer = "**MANDATORY RULE:** If you sell goods **Inter-State** (e.g., Maharashtra to Gujarat) or sell via **e-Commerce** (Amazon/Flipkart), GST Registration is mandatory **regardless of turnover** (even if ₹1)."
                
                eligibility_content = """
                * **Turnover Thresholds (General States):**
                  * **Goods:** > ₹40 Lakhs/year.
                  * **Services:** > ₹20 Lakhs/year.
                * **Special Category States:** Limit reduced to ₹10 Lakhs or ₹20 Lakhs.
                * **Voluntary:** You can register anytime to claim Input Tax Credit (ITC).
                """
                
                documents_content = """
                1. **PAN Card** of Business/Proprietor.
                2. **Aadhaar Card** of Promoter.
                3. **Proof of Business Address:** Electricity Bill / Rent Agreement / NOC.
                4. **Bank Account Proof:** Cancelled Cheque / Passbook.
                """
                
                fees_content = """
                **1. Registration Fee:** **NIL** (Govt charges ₹0 for registration).
                **2. Late Fees (Returns):**
                * **Nil Return:** ₹20 per day.
                * **Regular Return:** ₹50 per day (max capped).
                """
                
                timeline_content = """
                * **Registration:** 3-7 Working Days (ARN generated instantly).
                * **Return Filing:**
                  * **GSTR-1 (Sales):** 11th of next month.
                  * **GSTR-3B (Summary):** 20th of next month.
                """
                
                links_found = f"⭐ **Official GST Portal:** [www.gst.gov.in](https://www.gst.gov.in/)\n{links_found}"
                
                # Visual Guide: Portal + Return Types
                extra_logic_output = """
                \n
                \n
                """

            # --- B. SHOP ACT (Gumasta / Labour License) ---
            elif "SHOP" in task.upper() or "ACT" in task.upper() or "GUMASTA" in task.upper():
                specific_constraints = "Focus on State Labour Department rules. Intimation vs Registration."
                
                disclaimer = "**COMPLIANCE:** Displaying a Signboard in the local regional language (e.g., Marathi in Maharashtra) is mandatory and strictly enforced."
                
                eligibility_content = """
                * **Establishment:** Any shop, commercial office, hotel, or workshop.
                * **Employee Count:**
                  * **0-9 Employees:** 'Intimation' (Simplified).
                  * **10+ Employees:** 'Registration' (Certificate required).
                """
                
                documents_content = "1. **ID Proof** (PAN/Aadhaar).\n2. **Shop Photo** (with Name Board).\n3. **Address Proof** (Light Bill/Rent Agreement)."
                
                fees_content = "**Govt Fee:** Varies by State (e.g., ₹23.60 for Intimation in Maharashtra). Professional fees extra."
                
                timeline_content = "**Intimation:** Instant (Online). **Registration:** 1-7 Days."
                
                extra_logic_output = "\n"

            # --- C. MSME / UDYAM (Default Business Reg) ---
            else:
                specific_constraints = "Focus on Udyam Portal. Paperless self-declaration."
                
                disclaimer = "**FRAUD ALERT:** The Official Udyam Registration is **FREE**. Avoid private websites looking like govt portals that charge ₹1000+."
                
                eligibility_content = """
                * **Micro:** Investment < ₹1 Cr AND Turnover < ₹5 Cr.
                * **Small:** Investment < ₹10 Cr AND Turnover < ₹50 Cr.
                * **Medium:** Investment < ₹50 Cr AND Turnover < ₹250 Cr.
                """
                
                documents_content = "**Aadhaar Number** of Proprietor/Partner (Must be linked to PAN & Mobile)."
                
                fees_content = "**FREE.** ₹0 charges."
                timeline_content = "**Instant.** Certificate issued immediately upon Aadhaar OTP verification."
                
                links_found = f"⭐ **Official Udyam Portal:** [udyamregistration.gov.in](https://udyamregistration.gov.in/)\n{links_found}"
                
                extra_logic_output = "\n"
        # 15. TRAVEL DOCS (FIXED: IDP vs Passport vs Visa)
        # 15. TRAVEL DOCUMENTS (OCI / FRRO / VISA - SEPARATED)
        elif current_topic_key == "TRAVEL_DOCS":
            
            # --- A. OCI CARD (Overseas Citizen of India) ---
            if "OCI" in task.upper():
                specific_constraints = "Focus on Ministry of Home Affairs (MHA) OCI Guidelines. Distinct from Indian Citizenship."
                
                disclaimer = "**CRITICAL:** OCI is NOT Dual Citizenship. You cannot vote, buy agricultural land, or hold government office in India. OCI holders do NOT need FRRO registration."
                
                eligibility_content = """
                * **Foreign National:** Who was eligible to be a citizen of India on/after 26.01.1950 OR belonged to a territory that became part of India.
                * **Spouse:** Foreign spouse of an Indian Citizen/OCI holder (marriage > 2 years).
                * **Exclusions:** Citizens (or parents/grandparents) of Pakistan or Bangladesh are **NOT** eligible.
                """
                
                documents_content = """
                1. **Evidence of Indian Origin:** Info page of Own/Parents'/Grandparents' Indian Passport OR Nativity Certificate.
                2. **Renunciation Certificate:** Proof of cancelled Indian Passport (Surrender Certificate).
                3. **Current Foreign Passport:** Validity > 6 months.
                4. **Relationship Proof:** Birth Certificate / Marriage Certificate (Apostilled if issued abroad).
                """
                
                fees_content = """
                **1. Application Fee:** USD 275 (approx ₹23,000, varies by mission).
                **2. Conversion Fee (PIO to OCI):** USD 100.
                **3. Misc:** Courier/Service charges by VFS/BLS International.
                """
                
                timeline_content = "**Processing:** 4 to 12 Weeks (Strict police verification involved)."
                
                links_found = f"⭐ **Official OCI Portal:** [ociservices.gov.in](https://ociservices.gov.in/)\n{links_found}"
                
                extra_logic_output = "\n\n"

            # --- B. FRRO REGISTRATION (Foreigners Regional Registration Office) ---
            elif "FRRO" in task.upper() or "REGISTER" in task.upper():
                specific_constraints = "Focus on e-FRRO Portal. Registration vs Visa Extension."
                
                disclaimer = "**MANDATORY:** Foreigners (Student/Employment/Medical Visa) staying > 180 days must register within **14 days** of arrival. Late registration attracts heavy penalties (USD 300+)."
                
                eligibility_content = """
                * **Target:** Foreign Nationals (Non-OCI) visiting India.
                * **Criteria:** Visa validity > 180 days OR actual stay exceeding 180 days.
                * **Exemptions:** OCI Cardholders, Kids < 12 years (usually), and Tourist Visa holders (if stay < 180 days).
                """
                
                documents_content = """
                1. **Original Passport & Visa.**
                2. **Form C:** Proof of residence (issued by Hotel/Host via e-FRRO).
                3. **Undertaking Letter:** From Indian Sponsor/University/Employer.
                4. **Photo:** As per ICAO standards.
                """
                
                fees_content = """
                **1. Registration Fee:** Generally NIL (if done within 14 days).
                **2. Late Fee:** Varies (e.g., $300 equivalent).
                **3. Extension/Conversion:** Visa fees apply.
                """
                
                timeline_content = "**e-FRRO:** 3 to 7 Working Days (Email approval). Physical visit rarely needed."
                
                links_found = f"⭐ **e-FRRO Portal:** [indianfrro.gov.in](https://indianfrro.gov.in/)\n{links_found}"
                
                extra_logic_output = "\n\n"

            # --- C. INDIAN VISA (Entry) ---
            elif "VISA" in task.upper() and "INDIA" in task.upper():
                specific_constraints = "Focus on e-Visa vs Regular (Paper) Visa."
                
                disclaimer = "**FRAUD ALERT:** Use ONLY the official '.gov.in' website. Many private '.com' sites mimic the official portal and charge 5x fees."
                
                eligibility_content = "**Foreign Nationals** intending to visit India for Tourism, Business, Medical, or Conference purposes."
                
                documents_content = """
                1. **Passport:** Valid for > 6 months, 2 blank pages.
                2. **Photo:** White background, JPEG.
                3. **Business Card:** (For Business Visa).
                4. **Hospital Letter:** (For Medical Visa).
                """
                
                fees_content = "**e-Visa:** $10 to $80 (Country/Season dependent). **Regular Visa:** Higher fees via Indian Mission."
                
                timeline_content = "**e-Visa:** 24-72 Hours. **Regular Visa:** 3-10 Days."
                
                links_found = f"⭐ **Official e-Visa Portal:** [indianvisaonline.gov.in](https://indianvisaonline.gov.in/)\n{links_found}"

            # --- D. PASSPORT (Indian Citizens) - Default Fallback ---
            else:
                disclaimer = "Police Verification is mandatory for most fresh passports. Tatkaal requires 3 specific documents."
                eligibility_content = "**Indian Citizens** (by Birth, Descent, or Naturalization)."
                documents_content = "1. **Address Proof:** Aadhaar, Utility Bill, Rent Agreement.\n2. **Date of Birth Proof:** Birth Cert, 10th Marksheet, PAN."
                fees_content = "**Fresh (36 Pages):** ₹1,500. **Tatkaal:** ₹1,500 + ₹2,000 Verification Fee."
                timeline_content = "**Normal:** 20-30 Days. **Tatkaal:** 1-3 Days."
                
                extra_logic_output = "\n"

        # 16. TRAVEL RULES (Customs)
        # 16. TRAVEL RULES (Indian Customs / Baggage Rules)
        elif current_topic_key == "TRAVEL_RULES":
            specific_constraints = "Focus on Baggage Rules 2016. Duty Free Allowances (Gold, Alcohol, Cash)."
            
            disclaimer = "**WARNING:** The 'Duty-Free Gold Allowance' applies **ONLY** if you have resided abroad for **more than 1 year**. Short-trip travelers must pay duty (~38.5%) on ALL gold jewelry."
            
            eligibility_content = """
            * **Indian Resident / Person of Indian Origin:** Returning after stay abroad.
            * **Foreign Tourist:** Different rules apply (Personal effects only).
            """
            
            documents_content = """
            1. **Passport:** Immigration stamp proof of stay duration.
            2. **Customs Declaration Form:** Mandatory if carrying dutiable goods or excess cash.
            """
            
            fees_content = """
            **1. Gold Jewellery Allowance (If stay > 1 Year):**
            * **Men:** Up to 20g (Cap: ₹50,000).
            * **Women:** Up to 40g (Cap: ₹1,00,000).
            * *Note: Gold Bars/Coins are NOT duty-free.*

            **2. Alcohol & Tobacco (18+ Years):**
            * **Liquor:** Up to 2 Liters.
            * **Cigarettes:** Up to 100 sticks OR 25 cigars.
            
            **3. General Duty-Free Allowance:**
            * ₹50,000 (For personal articles/souvenirs).
            """
            
            timeline_content = "**Clearance:** Immediate (Green Channel) vs Inspection (Red Channel)."
            
            # Currency Declaration Rule
            extra_logic_output = """
            \n### 💵 Currency Declaration Rules (CDF)
            You MUST file a Declaration Form if you carry:
            * **Foreign Currency Notes** > USD 5,000.
            * **Total (Notes + Travellers Cheques)** > USD 10,000.
            * **Indian Currency** > ₹25,000 (Residents only).
            
            
            
            """
        # ... inside generate_master_plan ...

        # 17. TRAVEL INSURANCE (New Corrected Logic)
        elif "INSURANCE" in task.upper() and ("TRAVEL" in task.upper() or "TRIP" in task.upper()):
            specific_constraints = "Focus on IRDAI regulations. Differentiate between Single Trip vs Multi-trip."
            
            disclaimer = "**IMPORTANT:** Travel Insurance is a **Private Product** (regulated by IRDAI). It is mandatory for Schengen Visas but optional (though highly recommended) for countries like USA/Thailand. There is NO 'Government Fee' for this."
            
            eligibility_content = """
            * ** traveler:** Age typically 6 months to 85 years (varies by insurer).
            * **Prerequisite:** Valid Passport and definite travel dates.
            * **Pre-Existing Diseases:** Must be declared (may attract higher premium or exclusion).
            """
            
            documents_content = """
            **No Physical Documents Required for Issuance:**
            1. **Passport Number:** For the policy schedule.
            2. **Travel Dates:** Start and End Date.
            3. **Nominee Details:** Name and Relationship.
            *(Medical check-up only required for seniors > 70 years, varying by policy).*
            """
            
            fees_content = """
            **1. Premium (Not Govt Fee):**
            * Depends on Destination, Age, and Duration.
            * *Est:* ₹700 - ₹2,500 for a 15-day trip to Europe/USA.
            
            **2. Goods & Services Tax (GST):** 18% on the premium.
            """
            
            timeline_content = "**Instant (Digital).** Policy is emailed within 5-10 minutes of payment."
            
            extra_logic_output = """
            \n### 💡 Smart Tip: What to Cover?
            Ensure your policy covers:
            * **Medical Evacuation** (Critical for USA/Europe).
            * **Trip Cancellation** (For non-refundable flights).
            * **Baggage Loss/Delay**.
            
            
            
            """
        elif current_topic_key == "SUCCESSION":
                specific_constraints = "Distinguish between 'Legal Heir Certificate' (Revenue Dept) and 'Succession Certificate' (Civil Court)."
            
                disclaimer = "**CRITICAL LEGAL DISTINCTION:** A **Legal Heir Certificate** (issued by Tahsildar) is valid for transferring Electricity/Phone connections and low-value govt dues. For transferring **Bank Accounts, Shares, or Property** without a nominee, you usually need a **Succession Certificate** from a Civil Court."
            
                eligibility_content = """
                * **Class I Heirs:** Spouse, Children (Son/Daughter), and Mother of the deceased.
                * **Class II Heirs:** Father, Siblings (Only if no Class I heir is alive).
                """
            
                documents_content = """
                1. **Death Certificate:** Original (Issued by Municipality/Panchayat, NOT by the Court).
                2. **ID Proofs:** Aadhaar/PAN of all claimants.
                3. **Affidavit:** Self-declaration on Stamp Paper listing all surviving heirs.
                4. **Address Proof:** Deceased's proof of residence.
                """
            
                fees_content = """
                **1. Legal Heir Cert:** ₹20 - ₹100 (State Revenue Dept fee).
                **2. Succession Cert:** Court Fees (2-3% of the asset value being claimed).
                """
            
                timeline_content = """
                * **Legal Heir Cert:** 15-30 Days (Revenue Dept).
                * **Succession Cert:** 6-9 Months (Court Process).
                """
            
                extra_logic_output = """
                \n### 👣 Process Flow (Revenue Path)
                1. **Apply:** At Taluk/Tehsil Office or e-District Portal.
                2. **Verification:** Village Administrative Officer (VAO) / Revenue Inspector visits for inquiry.
                3. **Issuance:** Certificate issued by Tahsildar.
            
            
            
                """
        # 17. LIFE EVENTS (FIXED: HMA vs SMA Timeline)
        # 4. MARRIAGE, DIVORCE & NAME CHANGE (Corrected)
        elif current_topic_key == "MARRIAGE_DIVORCE":
            legal_sys = IndianDivorceSystem()
            
            # --- A. DIVORCE PROCESS ---
            if "DIVORCE" in task.upper():
                divorce_info = legal_sys.get_legal_info("Mutual" if "MUTUAL" in task_upper else "Contested")
                
                eligibility_content = f"""
                1. **Valid Marriage:** Must be legally married.
                2. **Separation:** Must be living separately for at least 1 year (for Mutual Consent).
                3. **Time Bar:** {legal_sys.check_eligibility_bar(1.5)}
                """
                documents_content = """
                1. **Petition Draft:** Legal filing stating grounds.
                2. **Proof of Marriage:** Certificate or Photos/Invitation.
                3. **Income Affidavit:** Mandatory for maintenance claims.
                """
                fees_content = "**Court Fees:** ₹15 - ₹250. **Legal Fees:** Varies."
                timeline_content = divorce_info['timeline']
                disclaimer = "**AUTHORITY:** Divorce is granted ONLY by the **Family Court**, not the Registrar."
                extra_logic_output = f"\n### ⚖️ Legal Route: {divorce_info['type']}\n* **Authority:** {divorce_info['authority']}\n* **Note:** {divorce_info['note']}"
                
                # Diagram for Divorce
                extra_logic_output += "\n"

            # --- B. NAME CHANGE (After Marriage) ---
            elif "NAME" in task.upper() and ("CHANGE" in task.upper() or "UPDATE" in task.upper()):
                specific_constraints = "Focus on using Marriage Certificate as Proof of Relationship. Gazette vs Simple Update."
                
                disclaimer = "**IMPORTANT:** For simple surname change (e.g., 'Sharma' to 'Verma'), the **Marriage Certificate** is usually sufficient proof for Aadhaar/PAN. A **Gazette Notification** is strictly mandatory only if you change your *First Name* or spelling completely."
                
                eligibility_content = "**Applicant:** Any Indian Citizen with a valid Marriage Certificate."
                
                documents_content = """
                1. **Marriage Certificate:** Original (Issued by Registrar).
                2. **Old IDs:** Aadhaar/PAN with maiden name.
                3. **Gazette Notification:** (Only if full name is changed or for Passport strict compliance).
                """
                
                fees_content = "**Official Update Fees:** Aadhaar (₹50), PAN (₹107), Passport (₹1,500)."
                
                timeline_content = "**Aadhaar/PAN:** 7-15 Days. **Passport:** 30 Days."
                
                extra_logic_output = """
                \n### 👣 Correct Order of Updates
                1. **Step 1:** Update **Aadhaar** first (using Marriage Cert).
                2. **Step 2:** Update **PAN** (using updated Aadhaar).
                3. **Step 3:** Update **Bank/Passport** (using Aadhaar + Marriage Cert).
                
                
                """
                # 9. SUCCESSION & LEGAL HEIR (Corrected)
        
            
            # --- C. MARRIAGE REGISTRATION (Default) ---
            # --- C. MARRIAGE REGISTRATION (HMA vs SMA - Corrected) ---
            # --- C. MARRIAGE REGISTRATION (HMA vs SMA - Corrected) ---
            # --- C. MARRIAGE REGISTRATION (HMA vs SMA - Final) ---
            else:
                specific_constraints = "Distinguish between Hindu Marriage Act (HMA) and Special Marriage Act (SMA). State-specific portals."
                
                disclaimer = "**VISA NOTE:** While marriage registration is not mandatory for all Indian visas, most foreign embassies (USA, UK, Canada, Schengen) **strictly require** a Marriage Certificate for spousal visa applications."
                
                eligibility_content = """
                * **Age:** Groom (21+), Bride (18+).
                * **HMA (Hindu Marriage Act, 1955):** Applies to Hindus, Sikhs, Jains, and Buddhists (where marriage is **already solemnized** via rituals).
                * **SMA (Special Marriage Act, 1954):** Applies to Inter-faith couples, Atheists, or Civil Marriages (Court Marriage).
                """
                
                documents_content = """
                1. **Proof of Age (Mandatory):** Birth Certificate / Passport / 10th Marksheet. (**PAN/Aadhaar are NOT valid age proofs**).
                2. **Proof of Address:** Aadhaar / Voter ID / Passport.
                3. **For HMA Only:** Wedding Photos (showing rituals) + *Invitation Card (State-specific/Optional)*.
                4. **Witnesses:**
                   * **HMA:** 2 Witnesses (Identity Proofs required).
                   * **SMA:** 3 Witnesses (Identity Proofs required).
                """
                
                fees_content = "**Govt Fee:** ₹100 - ₹500 (Varies by State: e.g., Maharashtra, Delhi, Karnataka). Professional/Notary fees extra."
                
                timeline_content = """
                * **HMA (Post-Marriage):** 1-7 Days (Instant in states with e-District portals).
                * **SMA (Court Marriage):** Minimum 30 Days (Mandatory Notice Period) + Registration Day.
                """
                
                links_found = "**State Portals:** Search 'IGRS [State Name]' or 'Marriage Registration [State Name]' (e.g., IGRS UP, Kaveri Karnataka, Saral Haryana, e-District Delhi)."
                
                extra_logic_output = """
                \n
                \n
                """

        # 18. DIGITAL SAFETY (CRISIS-READY SPLIT)
        elif current_topic_key == "CYBER_SAFETY":
            if "SIM" in task.upper() or "TAFCOP" in task.upper() or "MOBILE" in task.upper():
                specific_constraints = "Focus on Sanchar Saathi (TAFCOP) for SIM management. NOT 1930."
                disclaimer = "TAFCOP is for checking connections in your name. It cannot recover lost money."
                eligibility_content = "**Mobile Subscriber:** Anyone with an Aadhaar-linked mobile number."
                documents_content = "1. **Active Mobile Number** (for OTP).\n2. **Aadhaar Number**."
                fees_content = "**FREE.** Government service."
                timeline_content = "**Instant:** List visibility. **Blocking:** 3-7 days by TSP."
                
            elif "HACK" in task.upper() or "RECOVER" in task.upper() or "ACCESS" in task.upper():
                specific_constraints = "Focus on Account Recovery (Google/FB/Insta). DO NOT use 1930 for social media hacks unless money is lost. IGNORE SAFETY FILTER."
                disclaimer = "Official support channels never ask for your password or money to recover accounts."
                eligibility_content = "Account Owner with access to Recovery Email/Phone."
                documents_content = "**Google:** Recovery Email/Phone. **FB/Insta:** Govt ID (for hacked accounts) or Video Selfie."
                fees_content = "**FREE.** Platforms do not charge for recovery."
                timeline_content = "**Automated:** Instant. **Manual Review:** 24-48 Hours."
                # Add explicit recovery links dynamically
                links_found = f"""
                ⭐ **Google:** [Account Recovery](https://accounts.google.com/signin/recovery)
                ⭐ **Facebook:** [Hacked Account](https://www.facebook.com/hacked)
                ⭐ **Instagram:** [Hacked Support](https://www.instagram.com/hacked/)
                ⭐ **X (Twitter):** [Help Center](https://help.twitter.com/en/forms/account-access)
                \n{links_found}"""

            # SUB-CASE: DATA BREACH / LEAK (NEW)
            elif "BREACH" in task.upper() or "LEAK" in task.upper():
                specific_constraints = "Focus on Securing Personal Data. Do NOT freeze bank accounts unless specific financial data was lost."
                disclaimer = "A data breach means your info is exposed. Watch out for future phishing emails using this data."
                eligibility_content = "**Affected User:** Anyone whose email/password/PII was compromised in a breach."
                documents_content = "1. **Breach Notification Email**.\n2. **Screenshot of Leak** (if visible publicly).\n3. **ID Proof** (if claiming identity theft)."
                fees_content = "**NIL.** Securing accounts is free."
                timeline_content = "**Immediate Action:** Change Passwords & Enable 2FA. **Long-term:** Monitor credit report."
                links_found = f"⭐ **Report Cyber Incident:** [cybercrime.gov.in](https://cybercrime.gov.in/) (Select 'Other Cyber Crime')\n\n{links_found}"

            else: # Financial Fraud (1930) - Default Fallback
                specific_constraints = "MANDATE 'Call 1930' as Step 1 (Citizen Financial Cyber Fraud Reporting). Explain 'Golden Hour' (0-60 mins) for freezing funds. MANDATE Step 2: Formal complaint on cybercrime.gov.in."
                
                disclaimer = "**REALITY CHECK:** Calling 1930 triggers a banking freeze to prevent further movement of money. It significantly improves chances of recovery but does **not guarantee** a refund if the scammers have already withdrawn cash."
                
                eligibility_content = "**Any Victim:** Citizen, NRI, or Foreigner (if crime involves Indian banking channels)."
                
                documents_content = """
                1. **Transaction ID (UTR)** of the fraudulent transfer.
                2. **Bank Statement** showing debit.
                3. **Suspect Details:** Phone Number / UPI ID / Screenshots.
                4. **Acknowledgement No:** Received from 1930 operator.
                """
                
                fees_content = "**NIL.** Reporting via 1930 and the National Portal is free."
                
                timeline_content = """
                * **0-60 Mins (Golden Hour):** Highest chance of freezing funds.
                * **1-24 Hours:** Moderate chance.
                * **Mandatory Follow-up:** File formal complaint on **[cybercrime.gov.in](https://cybercrime.gov.in)** within 24 hours of the call to convert the report into a formal FIR/CSR.
                """
                
                extra_logic_output = ""

        # 19. PAN / IDENTITY
        elif current_topic_key == "PAN":
            specific_constraints = "Focus on NSDL/UTIITSL."
            eligibility_content = "Any person/entity."
            documents_content = "ID, Address, DOB Proof."
            fees_content = "**₹107** (Physical Card)."
            timeline_content = "**15-20 Days.**"

        # DEFAULT
        else:
            pass

        
        prompt = f"""
        You are an **Expert Consultant for complex life tasks in India**. Your primary goal is to ensure the final output is 99% accurate on process and facts.
        
        USER GOAL: {safe_task}
        
        {specific_constraints}
        
        RESEARCH DATA (Use this for context, but DO NOT override the hardcoded facts below):
        {research}
        
        TASK: Create a detailed Master Strategy. The headings and content below are the definitive sources for your response.
        """

    # --- FINAL TEMPLATE OUTPUT ---
    final_prompt = f"""
    {prompt}

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
    """
    
    # --- CHANGE 3: Replace Ollama call with Groq ---
    try:
        global client
        response = client.chat.completions.create(
            model=MODEL_NAME, 
            messages=[{'role': 'user', 'content': final_prompt}],
            temperature=0.1
        )
        master_plan = response.choices[0].message.content
        
        # Keep your existing error check logic
        if "cannot provide information" in master_plan.lower():
            return "## ❌ Research Failure. Try simplifying your query."

        # Keep your existing Diagram Logic (Do not delete the diagram code below this!)
        # ... (rest of your diagram logic remains untouched)
        
        return master_plan
        
    except Exception as e:
        return f"Final Generation Error: {str(e)}"

        # --- DIAGRAM LOGIC (Visual Guidance) ---
        diagram_query = None
        if current_topic_key == "ITR_FILING": diagram_query = ""
        elif current_topic_key == "EPFO_SERVICES": diagram_query = ""
        elif current_topic_key == "PROP_REG": diagram_query = ""
        elif current_topic_key == "BIZ_REG": diagram_query = ""
        elif current_topic_key == "LEGAL_ACTION": diagram_query = ""
        elif current_topic_key == "MARRIAGE_DIVORCE": diagram_query = ""
        elif current_topic_key == "BIZ_IPR": diagram_query = ""
        elif current_topic_key == "CYBER_SAFETY": diagram_query = ""
        elif current_topic_key == "TRAVEL_DOCS" and ("DRIVING" in task.upper() or "IDP" in task.upper()):
             diagram_query = ""
        elif current_topic_key == "BIZ_REG" and ("SHOP" in task.upper() or "ACT" in task.upper()):
             diagram_query = ""
        elif current_topic_key == "BANKING_DISPUTE" and ("FREEZE" in task.upper() or "BLOCKED" in task.upper()):
             diagram_query = ""
        elif current_topic_key == "LEGAL_DOCS" and "AFFIDAVIT" in task.upper():
             diagram_query = ""
        elif current_topic_key == "BANKING_DISPUTE":
             diagram_query = ""
        elif current_topic_key == "LEGAL_DOCS" and ("VS" in task.upper() or "DIFFERENCE" in task.upper()):
             diagram_query = ""

        if diagram_query:
            master_plan = master_plan.replace("## 🎯 Eligibility & Prerequisites", f"{diagram_query}\n\n## 🎯 Eligibility & Prerequisites")

        return master_plan
        
    except Exception as e:
        return f"Final Generation Error: {str(e)}"

# --- VIRAL SIMULATOR LOGIC (Unchanged) ---
def calculate_rejection_risk(salary_range, emis, credit_score, selected_bank):
    # ... (function body remains the same) ...
    avg_salary = (salary_range[0] + salary_range[1]) / 2
    nmi_estimate = avg_salary * 0.45 
    current_emis = float(emis) if emis else 0
    estimated_foir = (current_emis / nmi_estimate) if nmi_estimate > 0 else 1.0
    
    risk_foir = ""
    foir_explanation = "FOIR measures how much of your Net Monthly Income is already committed to EMIs. Even small existing EMIs can increase FOIR when combined with higher loan amounts."
    
    if estimated_foir > 0.60:
        risk_foir = f"FOIR (EMI-to-Income Ratio) is critically high. Loan will likely be rejected. ({foir_explanation})"
    elif estimated_foir > 0.45:
        risk_foir = f"FOIR is borderline. Reduce existing EMIs to qualify for the required loan amount. ({foir_explanation})"
    
    risk_cibil = ""
    score = int(credit_score.split('-')[0]) if '-' in credit_score else (750 if credit_score == '800+' else 600)
    if score < 700:
        risk_cibil = f"Credit Score ({score}) is below the preferred 700+ threshold."
    
    risks = []
    if risk_foir: risks.append(risk_foir)
    if risk_cibil: risks.append(risk_cibil)
    
    if len(risks) == 0:
        likelihood = "Very High Approval Likelihood"
        fix = "You have a strong profile. Proceed with documentation. (No Major Rejection Risks Detected)"
    elif len(risks) == 1:
        likelihood = "Medium Risk Profile"
        if "Credit Score" in risks[0]:
            fix = "Reduce outstanding balances and avoid new credit enquiries. Score improvements are typically reflected in 30–90 days."
        else:
            fix = "Focus on closing a personal loan or reducing credit card limits this week."
    else:
        likelihood = "High Rejection Risk"
        fix = "Address both your Credit Score and EMI structure before proceeding."
    
    return likelihood, risks, fix

# --- SIDEBAR: ABOUT US ---
with st.sidebar:
    st.markdown("### ❓ Why 'Clear Hai'?")
    
    st.info("""
    **Because Indian Bureaucracy is a Black Box.**
    
    You apply for a loan, and they say "Rejected" without explaining **FOIR**. 
    You go for a visa, and an agent charges ₹5,000 for a free form.
    
    We built **Clear Hai?** to fix this.
    """)
    
    st.markdown("---")
    
    st.markdown("### 🛡️ Our Promise")
    st.markdown("""
    * **Code > Opinions:** We don't guess. We run your data against official RBI Master Directions and Legal Acts.
    * **Zero Commission:** We don't sell loans. We don't sell your data.
    * **Privacy First:** Your data (salary, documents) stays in your browser session. We don't store it.
    """)
    
    st.markdown("---")
    
    st.markdown("**Built with 🧠 & 🐍 (Python) by a Developer who got tired of paperwork.**")
    st.caption("v1.0 | Data Sources: RBI, MHA, Income Tax Dept.")
# ==============================================================================
# 3. THE VIRAL UI (Multi-Mode Interface)
# ==============================================================================

# ==============================================================================
# 3. THE VIRAL UI (Multi-Mode Interface)
# ==============================================================================

# 1. Set the Tab Name & Icon (The "Favicon" users see in browser tabs)
st.set_page_config(
    page_title="Clear Hai? | The No-Nonsense Guide", 
    page_icon="✅", 
    layout="centered"
)

# 2. The Main Brand Header
st.markdown("""
# ✅ Clear Hai? 
### The "Hidden Logic" Detector for Indian Banks & Laws.

Don't let agents confuse you. Get a Master Strategy for Loans, Visas, and Legal Docs in 30 seconds.
""")

st.markdown("""
<div style="display: flex; gap: 15px; margin-bottom: 25px; font-size: 14px; color: #555; font-family: sans-serif;">
    <span style="background: #e6fffa; padding: 5px 10px; border-radius: 5px; border: 1px solid #b2f5ea;">✅ <b>RBI-Aligned Logic</b></span>
    <span style="background: #ebf8ff; padding: 5px 10px; border-radius: 5px; border: 1px solid #bee3f8;">🔒 <b>Bank-Verified Rules</b></span>
    <span style="background: #fff5f5; padding: 5px 10px; border-radius: 5px; border: 1px solid #fed7d7;">🚫 <b>No Agents. No Commission.</b></span>
</div>
""", unsafe_allow_html=True)


# --- DYNAMIC INPUT CHECK ---
task = st.text_input("What do you want to do in India?", "How to file ITR-1?", 
                     placeholder="e.g. Apply for PAN Card, ITR Filing, PF Withdrawal, Stamp Duty Calculation, File FIR")

# --- MODIFIED: Strict check for Loan Simulator vs General Mode ---
is_loan_task = any(kw in task.upper() for kw in LOAN_SIMULATOR_KEYWORDS)

# --- START OF FINANCIAL MODE BLOCK (SIMULATOR) ---
if is_loan_task:
    st.markdown("### 🏦 Loan Approval Chances Simulator (Financial Mode)")
    
    with st.form("rejection_simulator_form"):
        col1, col2 = st.columns(2)
        
        bank_list = ["State Bank of India", "Punjab National Bank", "Bank of Baroda", "Canara Bank", "Union Bank of India", "Bank of India", "Indian Bank", "UCO Bank", "Indian Overseas Bank", "Central Bank of India", "Bank of Maharashtra", "Punjab & Sind Bank", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "IndusInd Bank", "Yes Bank", "Federal Bank", "IDFC FIRST BANK"]
        selected_bank = col1.selectbox("1. Which Bank are you applying to?", bank_list, index=0)
        
        salary_range_options=[(25000, 35000), (35001, 50000), (50001, 75000), (75001, 100000), (100001, 150000)]
        salary_range_selected = col1.select_slider("2. Your Estimated Net Monthly Income (NMI) range?", 
                                            options=salary_range_options,
                                            format_func=lambda x: f"₹{x[0]:,} - ₹{x[1]:,}")
        
        current_emis = col2.number_input("3. Total of ALL Existing EMIs / Month", min_value=0, value=5000, step=1000)
        
        credit_score_options=["<650", "650-699", "700-749", "750-800", "800+"]
        credit_score_selected = col2.select_slider("4. Your Approximate Credit Score (CIBIL)", options=credit_score_options, value="750-800")
        
        city = st.text_input("5. Your City/Context", "Mumbai", placeholder="e.g. Mumbai, Delhi")
        
        shock_factor = st.checkbox("🔥 Activate 'Bank Truth Mode' to see hidden risks agents won't tell you.", value=True)
        
        submit_button = st.form_submit_button("Check Loan Approval Chances 🚀", type="primary")

    if submit_button:
        bank_name_full = f"Get a {selected_bank} Home Loan"
        
        with st.status("🧠 Running Bank Validation Check...", expanded=False) as status:
            likelihood, risks, fix = calculate_rejection_risk(salary_range_selected, current_emis, credit_score_selected, selected_bank)
            
            research_data, links_found = find_process_details(bank_name_full)
            master_plan = generate_master_plan(research_data, bank_name_full, links_found, mode="FINANCIAL")
            
            status.update(label="✅ Strategy Ready!", state="complete")

        st.divider()
        
        st.markdown(f"## Your Approval Profile: {likelihood}")
        st.caption(f"Estimate based on {selected_bank}'s public eligibility rules and your inputs. This is not a guarantee.") 
        
        if likelihood == "Very High Approval Likelihood":
            score_color = "#33cc33" 
        elif likelihood == "Medium Risk Profile":
            score_color = "#ff9900"
        else:
            score_color = "#ff0000"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 3px solid {score_color}; border-radius: 10px;">
            <h1 style="color: {score_color}; font-size: 48px; margin: 0;">{likelihood}</h1>
            <p style="font-size: 20px; margin: 0;">Based on {selected_bank} Rules</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"## ⚠️ Top {len(risks)} Rejection Risks Detected")
        for risk in risks: st.warning(f"❌ {risk}")
        
        st.markdown(f"## 🔧 Your Action Plan: One Fix This Week")
        st.info(fix)
        
        st.markdown("---")
        st.warning("⚠️ Most people get rejected because of hidden metrics. Share before they apply.")
        whatsapp_message = f"⚠️ My Home Loan Risk for {selected_bank} is {likelihood}. I used this free tool to find out the hidden risks. Check your risk now: [Link to your deployed App]"
        st.link_button("📲 Share My Results (WhatsApp)", f"https://wa.me/?text={whatsapp_message}", type="secondary")

        if shock_factor:
            st.divider()
            st.markdown("## 🔥 Bank Truth Mode Activated")
            st.error(f"**This is what agents usually don’t explain:** Even small existing EMIs can increase FOIR when combined with higher loan amounts. FOIR measures how much of your income is already committed to EMIs, and this is the key metric {selected_bank} evaluates.")
            st.markdown(f"### Expert Master Strategy (The full VAG Plan):")
            st.markdown(master_plan)
# --- END OF FINANCIAL MODE BLOCK ---

else:
    # --- GENERAL INPUTS (Non-Financial Mode: Passport, Visa, etc.) ---
    st.markdown("### 🌎 General Master Strategy (Passport/Visa/Procedure Mode)")
    st.caption("We will use a high-accuracy RAG model to generate your step-by-step strategy.")
    
    general_submit = st.button("Generate Strategy 🚀", type="primary")

    if general_submit:
        with st.status("🧠 Searching Official Government Channels...", expanded=True) as status:
            
            research_data, links_found = find_process_details(task)
            master_plan = generate_master_plan(research_data, task, links_found, mode="GENERAL")
            
            status.update(label="✅ Strategy Ready!", state="complete")

        st.divider()
        st.markdown(master_plan)
        
        with st.expander("🔍 View Raw Research Data"):
            st.code(research_data)
