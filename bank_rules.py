# ==============================================================================
# 1. bank_rules.py - Extended Structured Data Source (SDS)
# ==============================================================================

BANK_RULESET = {
    # --- PUBLIC SECTOR BANKS (PSBs) ---
    "STATE BANK OF INDIA": {
        "Age": "18 to 70 years (loan maturity)",
        "Benchmark": "EBLR (External Benchmark Lending Rate) linked to Repo Rate",
        "Fee_Structure": "0.35% of loan amount + GST, capped at ₹10,000 + GST (often zero)",
        "Income_Rule": "Based on Net Monthly Income (NMI) and FOIR; no fixed minimum published.",
        "Doc_Years": "2-3 years ITR/Form 16 required for self-employed.",
    },
    
    "PUNJAB NATIONAL BANK": {
        "Age": "21 to 70 years (loan maturity)",
        "Benchmark": "RLLR (Repo Linked Lending Rate)",
        "Fee_Structure": "0.35% of loan amount + GST, with minimum/maximum caps.",
        "Income_Rule": "Based on Net Take Home Pay and repayment capacity.",
        "Doc_Years": "Last 3 months salary slips; 2 years ITR for non-salaried.",
    },
    
    "BANK OF BARODA": {
        "Age": "18 or 21 (scheme dependent) up to a maximum of 70 years.",
        "Benchmark": "Repo/EBLR (External Benchmark Lending Rate)",
        "Fee_Structure": "Usually 0.50% of the loan amount, subject to a minimum/maximum cap.",
        "Income_Rule": "Based on Net Monthly Income and FOIR; no maximum limit.",
        "Doc_Years": "3–6 months salary slips, ITR/Form 16 required.",
    },

    "CANARA BANK": {
        "Age": "18 to 70 years (loan maturity)",
        "Benchmark": "Repo/RLLR (Repo Linked Lending Rate)",
        "Fee_Structure": "0.50% of loan amount + GST, capped at ₹20,000.",
        "Income_Rule": "NMI must meet minimum requirement specified by the branch.",
        "Doc_Years": "Last 3 months salary slip.",
    },
    
    "UNION BANK OF INDIA": {
        "Age": "18 to 75 years (loan maturity)",
        "Benchmark": "EBLR (External Benchmark Lending Rate)",
        "Fee_Structure": "0.50% of loan amount + GST, minimum ₹1500.",
        "Income_Rule": "Net annual income must be adequate to maintain sufficient FOIR.",
        "Doc_Years": "Last 3 months salary slip; 3 years ITR for non-salaried.",
    },
    
    "BANK OF INDIA": {
        "Age": "18 to 70 years (loan maturity)",
        "Benchmark": "RBLR (Repo Based Lending Rate)",
        "Fee_Structure": "0.25% of loan amount + GST, capped at ₹10,000.",
        "Income_Rule": "Minimum Net Monthly Income specified for metro/urban areas.",
        "Doc_Years": "Last 6 months bank statement; 2 years ITR.",
    },

    # --- OTHER PSBs (Using General/Universal Rules for placeholders) ---
    "INDIAN BANK": {
        "Age": "21 to 70 years (loan maturity)",
        "Benchmark": "Repo Linked Lending Rate (RLLR)",
        "Fee_Structure": "0.25% of loan amount + GST.",
        "Income_Rule": "Adequate repayment capacity based on NMI and existing loans.",
        "Doc_Years": "Last 3 months salary slip.",
    },
    "UCO BANK": {
        "Age": "21 to 70 years (loan maturity)",
        "Benchmark": "RLLR",
        "Fee_Structure": "0.25% of loan amount + GST.",
        "Income_Rule": "Based on NMI and FOIR.",
        "Doc_Years": "Last 6 months bank statement.",
    },
    "INDIAN OVERSEAS BANK": {
        "Age": "21 to 60 years (loan maturity)",
        "Benchmark": "RLLR",
        "Fee_Structure": "0.50% of loan amount + GST.",
        "Income_Rule": "Sufficient net monthly income to cover EMIs.",
        "Doc_Years": "3 years ITR/assessment order.",
    },
    "CENTRAL BANK OF INDIA": {
        "Age": "18 to 70 years (loan maturity)",
        "Benchmark": "RBLR",
        "Fee_Structure": "0.50% of loan amount + GST, minimum ₹2,000.",
        "Income_Rule": "Clear repayment capacity based on gross monthly income.",
        "Doc_Years": "Last 6 months bank statement.",
    },
    "BANK OF MAHARASHTRA": {
        "Age": "21 to 70 years (loan maturity)",
        "Benchmark": "RLLR",
        "Fee_Structure": "0.25% of loan amount + GST, capped at ₹20,000.",
        "Income_Rule": "Minimum NMI required; varies by location.",
        "Doc_Years": "Last 3 months salary slip.",
    },
    "PUNJAB & SIND BANK": {
        "Age": "21 to 70 years (loan maturity)",
        "Benchmark": "RLLR",
        "Fee_Structure": "0.40% of loan amount + GST.",
        "Income_Rule": "Minimum monthly income necessary to cover installments.",
        "Doc_Years": "Last 6 months bank statement.",
    },

    # --- PRIVATE SECTOR BANKS (PVBs) ---
    "HDFC BANK": {
        "Age": "21 to 65 years (loan maturity)",
        "Benchmark": "RPLR (Retail Prime Lending Rate) or RLLR",
        "Fee_Structure": "Up to 1.50% of loan amount + GST, minimum ₹3,000.",
        "Income_Rule": "Minimum monthly salary of ₹15,000/month in non-metro and ₹25,000/month in metro cities.",
        "Doc_Years": "Last 3 months salary slips; 3 years ITR for self-employed.",
    },
    "ICICI BANK": {
        "Age": "21 to 65 years (loan maturity)",
        "Benchmark": "ICICI Bank's I-RPLR (ICICI Retail Prime Lending Rate)",
        "Fee_Structure": "Up to 1.50% of loan amount + GST.",
        "Income_Rule": "Based on repayment capacity and FOIR.",
        "Doc_Years": "Last 3 months salary slips.",
    },
    "AXIS BANK": {
        "Age": "21 to 65 years (loan maturity)",
        "Benchmark": "MCLR (Marginal Cost of Funds based Lending Rate) or RLLR",
        "Fee_Structure": "Ranges from 0.5% to 1.0% of loan amount + GST.",
        "Income_Rule": "Specific minimum monthly income often required.",
        "Doc_Years": "2 years ITR/Form 16 minimum.",
    },
    "KOTAK MAHINDRA BANK": {
        "Age": "18 to 65 years (loan maturity)",
        "Benchmark": "RBLR (Repo Based Lending Rate)",
        "Fee_Structure": "Up to 1.50% of loan amount + GST.",
        "Income_Rule": "Minimum net annual income specified.",
        "Doc_Years": "Last 3 months salary slip.",
    },
    "INDUSIND BANK": {
        "Age": "21 to 70 years (loan maturity)",
        "Benchmark": "MCLR or RLLR",
        "Fee_Structure": "0.50% to 1.0% of loan amount + GST.",
        "Income_Rule": "Based on income, debt, and repayment history.",
        "Doc_Years": "Last 3 months salary slips.",
    },
    "YES BANK": {
        "Age": "21 to 65 years (loan maturity)",
        "Benchmark": "MCLR or RLLR",
        "Fee_Structure": "0.50% to 1.0% of loan amount + GST.",
        "Income_Rule": "Minimum net annual income required.",
        "Doc_Years": "3 months salary slip; 2 years ITR.",
    },
    "FEDERAL BANK": {
        "Age": "21 to 60 years (loan maturity)",
        "Benchmark": "RLLR",
        "Fee_Structure": "0.50% of loan amount + GST.",
        "Income_Rule": "Adequate repayment capacity based on NMI.",
        "Doc_Years": "Last 6 months bank statement.",
    },
    "IDFC FIRST BANK": {
        "Age": "21 to 65 years (loan maturity)",
        "Benchmark": "MCLR or RLLR",
        "Fee_Structure": "Up to 1.50% of loan amount + GST.",
        "Income_Rule": "Based on financial stability and credit history.",
        "Doc_Years": "Last 3 months salary slips.",
    },
    
    # --- UNIVERSAL RULES (Serve as defaults/corrections) ---
    "UNIVERSAL_RULES": {
        "Income_Disclaimer": "NEVER state a maximum income limit.",
        "Doc_CIBIL": "Banks pull the CIBIL report themselves; applicant does not submit a report.",
        "Rate_Type": "Home loans are primarily Floating-Rate and linked to an external benchmark.",
        "Tenure_Cap": "Maximum repayment tenure is subject to the age cap (usually 70 years)."
    }
}

def get_bank_rules(bank_name):
    # ... (function body for get_bank_rules remains the same) ...
    normalized_name = bank_name.upper().replace('GET AN ', '').replace(' HOME LOAN', '').strip()
    
    rules = BANK_RULESET.get(normalized_name, {})

    if not rules:
        for key, value in BANK_RULESET.items():
            if normalized_name in key:
                rules = value
                break
    
    return {**BANK_RULESET.get("UNIVERSAL_RULES", {}), **rules}