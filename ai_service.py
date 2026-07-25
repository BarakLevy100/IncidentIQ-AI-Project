import google.generativeai as genai
from prompts import get_investigator_prompt, get_auditor_prompt, get_postmortem_prompt


def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)


def run_incident_analysis(model_name: str, prompt_style: str, logs_input: str):
    model = genai.GenerativeModel(model_name)

    # 1. Primary Analysis
    inv_prompt = get_investigator_prompt(prompt_style, logs_input)
    response_investigator = model.generate_content(inv_prompt)
    initial_analysis = response_investigator.text

    # 2. Skeptical Audit
    audit_prompt = get_auditor_prompt(initial_analysis, logs_input)
    response_auditor = model.generate_content(audit_prompt)
    audit_critique = response_auditor.text

    return initial_analysis, audit_critique