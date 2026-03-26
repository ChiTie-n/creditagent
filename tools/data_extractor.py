"""
data_extractor.py
Agent to extract structured borrower data from unstructured text using an LLM.
"""

import os
import json

def extract_persona_data(raw_text: str) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    system_prompt = """You are an AI assistant that extracts borrower information from unstructured text and converts it into a structured JSON format.
Your output MUST BE ONLY valid JSON, with absolutely no markdown formatting, no code blocks, and no extra text.

The JSON schema must follow this structure exactly:
{
    "name": "string",
    "scenario": "string (create a short 3-5 word summary of their situation)",
    "expected_decision": "APPROVE or ESCALATE or DENY",
    "profile": {
        "gender": "male or female",
        "age_group": "18-25, 25-35, 35-45, or 45+",
        "region": "urban, suburban, or rural",
        "employment_type": "employee, business_owner, self_employed, or unemployed"
    },
    "bank_data": {
        "LIMIT_BAL": integer (Credit limit amount extended),
        "SEX": integer (1=Male, 2=Female),
        "EDUCATION": integer (1=Grad school, 2=University, 3=High school, 4=Others),
        "MARRIAGE": integer (1=Married, 2=Single, 3=Others),
        "AGE": integer,
        "PAY_0": integer (delay in months for current repayment, -1=pay duly, 1=1 month delay, 2=2 months delay, etc),
        "PAY_2": integer (delay in months for previous repayment),
        "PAY_3": integer (delay in months for 2 months ago),
        "BILL_AMT1": integer (Amount of bill statement in current month),
        "PAY_AMT1": integer (Amount of previous payment)
    },
    "utility_data": {
        "on_time_rate": float between 0.0 and 1.0,
        "months_history": integer
    },
    "mobile_data": {
        "monthly_volume": integer,
        "consistency_score": float between 0.0 and 1.0
    }
}
If bank data is not mentioned, set "bank_data" to null. If utility data is not mentioned, set "utility_data" to null. If mobile data is not mentioned, set "mobile_data" to null. Infer missing fields with reasonable defaults if necessary based on the risk profile of the narrative, but try to extract as much as possible for accuracy."""

    user_prompt = f"Extract the borrower profile from the following text:\n\n{raw_text}"
    
    response_text = ""
    try:
        if api_key.startswith("AIza"):
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)
            response = model.generate_content(user_prompt)
            response_text = response.text
        elif api_key.startswith("sk-ant"):
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            response_text = message.content[0].text
        else:
            raise ValueError("No valid API key found. Please ensure ANTHROPIC_API_KEY is set in your environment.")
            
        # Clean up the output in case the LLM wrapped it in markdown code blocks
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        parsed_data = json.loads(response_text)
        return parsed_data
        
    except Exception as e:
        print(f"Extraction error: {e}")
        raise e
