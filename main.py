"""
GST Sahayak - Main Streamlit Application
Hybrid Architecture: Rule Engine + Semantic Search + Multi-Provider LLM Fallback
References: All previous pipeline outputs (Qwen KB, Mistral impl, Gemini design, Nemotron research)
"""

import streamlit as st
from dotenv import load_dotenv

# Local imports
from rule_engine import GSTDueDateCalculator, calculate_late_fee, calculate_tds_194j, itc_eligibility_checker
from nlp.intent_classifier import IntentClassifier
from utils.disclaimers import get_disclaimer, get_legal_notice
from utils.llm_providers import (
    llm_fallback,
    get_available_providers,
    resolve_provider,
    provider_label,
    PROVIDER_CONFIG,
    PROVIDER_PRIORITY,
)

load_dotenv()
st.set_page_config(page_title="GST Sahayak", page_icon="🇮🇳", layout="wide")

# Initialize components
@st.cache_resource
def load_components():
    classifier = IntentClassifier()
    due_date_calc = GSTDueDateCalculator()
    return classifier, due_date_calc

classifier, due_date_calc = load_components()

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "filing_type": "monthly",
        "state": "Karnataka",
        "turnover_crore": 2.0,
        "state_group": "A"
    }
if "llm_provider" not in st.session_state:
    default_provider = resolve_provider() or "auto"
    st.session_state.llm_provider = default_provider

def handle_user_query(query: str):
    """Append user message, process, and store assistant response."""
    st.session_state.messages.append({"role": "user", "content": query})
    response = process_query(query)
    st.session_state.messages.append({"role": "assistant", "content": response})

def process_query(query: str):
    """Hybrid Routing Logic"""
    # 1. Try NLP Classifier
    result = classifier.classify(query)
    
    if result["intent"] != "general" and result["confidence"] > 0.7:
        # High confidence - use local answer
        answer = result["answer"]
        if result.get("action"):
            answer += f"\n\n**Suggested Action**: {result['action']}"
        return answer + get_disclaimer()

    # 2. Keyword/Rule-based routing for specific tools
    q_lower = query.lower()
    
    if any(kw in q_lower for kw in ["due date", "gstr-1", "gstr-3b", "when to file"]):
        profile = st.session_state.user_profile
        due1 = due_date_calc.get_gstr1_due_date(profile["filing_type"])
        due3b = due_date_calc.get_gstr3b_due_date(profile["filing_type"], profile["state_group"])
        return (f"Based on your profile ({profile['filing_type']}, {profile['state']}):\n"
                f"• GSTR-1 due: **{due1}**\n"
                f"• GSTR-3B due: **{due3b}**" + get_disclaimer())

    if "late fee" in q_lower or "penalty" in q_lower:
        # Simple demo: assume 7 days late with liability
        fee = calculate_late_fee(7, True)
        return (f"Example Late Fee (7 days, with liability):\n"
                f"Total: ₹{fee['total_fee']} (CGST ₹{fee['cgst']} + SGST ₹{fee['sgst']})\n"
                f"Max cap: ₹5,000. Interest @18% p.a. also applies." + get_disclaimer())

    if "itc" in q_lower or "input tax credit" in q_lower:
        # Demo values
        result_itc = itc_eligibility_checker(True, True, False, True)
        return f"ITC Check Result: **{result_itc}**" + get_disclaimer()

    if "eway" in q_lower or "e-way bill" in q_lower:
        return ("E-Way Bill Thresholds (2026):\n"
                "• Inter-state: ₹50,000\n"
                "• Intra-state examples: Karnataka ₹50k, Maharashtra ₹1L\n"
                "Validity: 1 day per 200 km (normal cargo)." + get_disclaimer())

    if "tds" in q_lower or "194j" in q_lower:
        tds = calculate_tds_194j(60000, "professional", True)
        return f"Example TDS on ₹60,000 professional fees (with PAN): **₹{tds}**" + get_disclaimer()

    if "composition" in q_lower:
        return ("Composition Scheme (2026):\n"
                "• Goods: Up to ₹1.5 Cr turnover @1%\n"
                "• Services: Up to ₹50 Lakh @6%\n"
                "Restrictions: No ITC, no inter-state sales." + get_disclaimer())

    # 3. Low confidence or complex -> LLM Fallback
    context = "Use GST knowledge base for accurate answers about filing, ITC, e-way bills, late fees, TDS."
    return llm_fallback(
        query,
        context,
        user_profile=st.session_state.user_profile,
        provider=st.session_state.llm_provider,
        disclaimer_fn=get_disclaimer,
    )

# ============ UI ============
st.title("🇮🇳 GST Sahayak")
st.caption("Your AI-Powered GST & Tax Compliance Helper | Academic Social Impact Project")

# Sidebar - User Profile
with st.sidebar:
    st.header("Your Profile")
    st.session_state.user_profile["filing_type"] = st.selectbox(
        "Filing Type", ["monthly", "qrmp"], 
        index=0 if st.session_state.user_profile["filing_type"] == "monthly" else 1
    )
    st.session_state.user_profile["state"] = st.selectbox(
        "State", ["Karnataka", "Maharashtra", "Delhi", "Gujarat", "Tamil Nadu"], index=0
    )
    st.session_state.user_profile["state_group"] = st.selectbox("State Group (for QRMP)", ["A", "B"], index=0)
    st.session_state.user_profile["turnover_crore"] = st.slider("Annual Turnover (₹ Crore)", 0.5, 10.0, 2.0, 0.5)

    st.divider()
    st.markdown("**AI Provider**")
    available = get_available_providers()
    provider_options = ["auto"] + [p for p in PROVIDER_PRIORITY if p in available]
    if not available:
        st.caption("No API key found. Add one in `.env` (see `.env.example`).")
        provider_options = ["auto"] + PROVIDER_PRIORITY

    current = st.session_state.llm_provider
    if current not in provider_options:
        current = provider_options[0]

    selected = st.selectbox(
        "LLM for complex queries",
        provider_options,
        index=provider_options.index(current),
        format_func=lambda p: "Auto (first available key)" if p == "auto" else provider_label(p),
    )
    st.session_state.llm_provider = selected

    active = resolve_provider(selected)
    if active:
        st.caption(f"Active: **{provider_label(active)}**")
    else:
        st.caption("Active: **Local rules only** (no API key)")

    st.divider()
    st.markdown("**Quick Tools**")
    if st.button("Check GSTR-3B Due Date"):
        st.session_state.pending_query = "What is my GSTR-3B due date?"
        st.rerun()
    if st.button("Calculate Late Fee (7 days)"):
        st.session_state.pending_query = "Calculate late fee for 7 days delay"
        st.rerun()
    if st.button("ITC Eligibility Checker"):
        st.session_state.pending_query = "Can I claim ITC?"
        st.rerun()

# Process pending quick-reply / sidebar queries
if st.session_state.pending_query:
    with st.spinner("Thinking..."):
        handle_user_query(st.session_state.pending_query)
    st.session_state.pending_query = None
    st.rerun()

# Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about GST, ITC, due dates, late fees, e-way bills..."):
    with st.spinner("Thinking..."):
        handle_user_query(prompt)
    st.rerun()

# Footer
st.markdown("---")
active_llm = resolve_provider(st.session_state.llm_provider)
llm_tag = provider_label(active_llm) if active_llm else "Local only"
st.caption(get_legal_notice() + f" | Hybrid AI (Local + {llm_tag}) | Mobile Friendly")

# Quick Reply Buttons at bottom for demo
st.markdown("**Quick Replies:**")
cols = st.columns(4)
with cols[0]:
    if st.button("GSTR-1 Due Date?"):
        st.session_state.pending_query = "What is GSTR-1 due date?"
        st.rerun()
with cols[1]:
    if st.button("Late Fee for 10 days?"):
        st.session_state.pending_query = "Late fee for 10 days with liability"
        st.rerun()
with cols[2]:
    if st.button("Do I need E-way bill?"):
        st.session_state.pending_query = "E-way bill threshold for ₹60,000 inter-state"
        st.rerun()
with cols[3]:
    if st.button("Composition Scheme?"):
        st.session_state.pending_query = "Am I eligible for composition scheme?"
        st.rerun()