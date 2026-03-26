"""
report_generator.py
Call Anthropic Claude API to generate a human-readable credit assessment report.
Falls back gracefully if API key is not set.
"""

import os
from typing import Optional

try:
    import anthropic
    _CLIENT_AVAILABLE = True
except ImportError:
    _CLIENT_AVAILABLE = False


def _get_client() -> Optional[object]:
    if not _CLIENT_AVAILABLE:
        return None
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        return None
    return anthropic.Anthropic(api_key=api_key)


def generate_report(
    borrower_name: str,
    composite_score: int,
    risk_tier: str,
    decision: str,
    financial_score: int,
    alternative_score: int,
    key_strengths: list,
    key_concerns: list,
    is_underbanked: bool,
    shap_summary: dict,
) -> str:
    """
    Generate plain-text credit assessment report via Claude or Gemini API.
    Falls back to a rule-based template if API is unavailable or errors out.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    strengths_text = "\n".join(f"- {s}" for s in key_strengths)
    concerns_text = "\n".join(f"- {c}" for c in key_concerns)

    system_prompt = "You are a senior credit analyst at a fintech company. Generate clear, professional credit assessment reports that are easy for loan officers to understand.\nContext: This is a Vietnamese micro-SME credit assessment. The applicant may be a street vendor, household business owner, or informal sector worker. Alternative data sources include: MoMo, ZaloPay, ViettelPay transactions and EVN/VNPT utility payment history. Loan amounts are in VND (Vietnamese Dong). Generate the report in English but reference Vietnamese context appropriately. Replace generic terms like 'personal credit' with 'business credit' and 'borrower financial history' with 'business financial history'."
    user_prompt = f"""Generate a professional credit assessment report for:

Borrower: {borrower_name}
Composite Credit Score: {composite_score}/1000
Risk Tier: {risk_tier}
Decision: {decision}
Financial Score: {financial_score}/1000
Alternative Data Score: {alternative_score}/1000
Thin-file Applicant: {"Yes" if is_underbanked else "No"}

Key Strengths:
{strengths_text}

Key Concerns:
{concerns_text}

Top SHAP Feature Contributions (positive = risk increasing):
{_format_shap(shap_summary)}

Write a clear 3-paragraph report:
1. Executive Summary (decision + score rationale)
2. Strengths and positive indicators  
3. Risk factors and recommendations

Keep language professional but accessible. Max 300 words."""

    try:
        if api_key.startswith("AIza"):
            # Use Google Gemini API (new SDK) with model fallback chain
            try:
                import time
                import re
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                model_chain = ["gemma-3-27b-it", "gemma-3-12b-it", "gemma-3-4b-it", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
                last_exc = None
                for model_name in model_chain:
                    try:
                        resp = client.models.generate_content(
                            model=model_name,
                            contents=f"{system_prompt}\n\n{user_prompt}",
                            config=types.GenerateContentConfig(
                                max_output_tokens=600,
                            ),
                        )
                        return resp.text
                    except Exception as e:
                        last_exc = e
                        err_str = str(e)
                        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                            # Daily quota — skip immediately; RPM — wait briefly
                            if "PerDay" not in err_str and "daily" not in err_str.lower():
                                m_delay = re.search(r"retry[_\s]delay[^0-9]*(\d+)", err_str, re.IGNORECASE)
                                delay = min(float(m_delay.group(1)), 30.0) if m_delay else 5.0
                                time.sleep(delay)
                            continue
                        raise
                raise RuntimeError(f"All Gemini models exhausted: {last_exc}")
            except ImportError:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)
                response = model.generate_content(user_prompt)
                return response.text
        elif api_key.startswith("sk-ant"):
            # Use Anthropic Claude API
            client = _get_client()
            if client is not None:
                message = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=600,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return message.content[0].text
    except Exception as e:
        print(f"[report_generator] LLM API error: {e}. Using fallback.")

    # ── Fallback template ────────────────────────────────────────────────────
    decision_text = {
        "APPROVE": "approved for credit",
        "ESCALATE": "flagged for manual review",
        "DENY": "declined at this time",
    }.get(decision, decision)

    thin_note = (
        "\n\nNotably, this applicant lacks traditional banking history. "
        "The assessment relied heavily on alternative data sources including "
        "utility payment history and mobile money transaction patterns, "
        "which demonstrated strong financial discipline." if is_underbanked else ""
    )

    return f"""CREDIT ASSESSMENT REPORT — {borrower_name}

EXECUTIVE SUMMARY
{borrower_name} has been {decision_text} with a composite credit score of {composite_score}/1000, placing them in the {risk_tier} category. The assessment combines financial scoring ({financial_score}/1000) with alternative data analysis ({alternative_score}/1000).{thin_note}

STRENGTHS
{strengths_text}

RISK FACTORS & RECOMMENDATIONS
{concerns_text}

This assessment was generated by the CreditAgent AI system and should be reviewed by a qualified credit officer before final disbursement decisions."""


def _format_shap(shap_summary: dict) -> str:
    if not shap_summary:
        return "N/A"
    lines = []
    for feat, val in sorted(shap_summary.items(), key=lambda x: abs(x[1]), reverse=True)[:5]:
        direction = "↑ risk" if val > 0 else "↓ risk"
        lines.append(f"  {feat}: {val:+.3f} ({direction})")
    return "\n".join(lines)
