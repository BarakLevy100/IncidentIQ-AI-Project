import google.generativeai as genai
from prompts import get_investigator_prompt, get_auditor_prompt, get_postmortem_prompt


def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)


def run_incident_analysis(model_name: str, prompt_style: str, logs_input: str, length: str):
    model = genai.GenerativeModel(model_name)

    # 1. Primary Analysis
    inv_prompt = get_investigator_prompt(prompt_style, logs_input, length)
    response_investigator = model.generate_content(inv_prompt)
    initial_analysis = response_investigator.text

    # 2. Skeptical Audit
    audit_prompt = get_auditor_prompt(initial_analysis, logs_input, length)
    response_auditor = model.generate_content(audit_prompt)
    audit_critique = response_auditor.text

    return initial_analysis, audit_critique


def generate_postmortem(model_name: str, incident_data: str) -> str:
    """Generates a structured postmortem report using the postmortem prompt function."""
    try:
        model = genai.GenerativeModel(model_name)
        postmortem_prompt = get_postmortem_prompt(incident_data)
        response = model.generate_content(postmortem_prompt)
        return response.text
    except Exception as e:
        return f"Error generating postmortem: {str(e)}"