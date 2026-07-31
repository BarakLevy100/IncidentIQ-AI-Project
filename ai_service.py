import google.generativeai as genai
from prompts import get_investigator_prompt, get_auditor_prompt, get_postmortem_prompt


def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)


def run_incident_analysis(model_name: str, prompt_style: str, logs_input: str, length: str, target_audience: str):
    """This function executes a two-pass AI pipeline that first analyzes the incident logs, and then acts as a
    skeptical auditor to critique its own initial findings for biases. It utilizes layered error handling
    throughout both steps to gracefully catch API failures or Google safety blocks without crashing the application."""
    try:
        model = genai.GenerativeModel(model_name)

        # 1. Primary Analysis Execution
        try:
            inv_prompt = get_investigator_prompt(prompt_style, logs_input, length, target_audience)
            response_investigator = model.generate_content(inv_prompt)
            initial_analysis = response_investigator.text

        except ValueError:
            # Handle Google Safety/Copyright Blocks
            finish_reason = response_investigator.candidates[
                0].finish_reason if response_investigator.candidates else "Unknown"
            initial_analysis = f"⚠️ **AI Output Blocked.** The API refused to return the response (Finish Reason: {finish_reason}). This usually happens if the AI tries to recite copyrighted documentation verbatim."
            return initial_analysis, "Audit skipped because the initial analysis was blocked."

        except Exception as e:
            # Handle Network Timeouts, API Quotas, or other API crashes
            initial_analysis = f"❌ **API Error during Primary Analysis:** {str(e)}"
            return initial_analysis, "Audit skipped because the primary analysis failed."

        # 2. Skeptical Audit Execution
        try:
            audit_prompt = get_auditor_prompt(initial_analysis, logs_input, length)
            response_auditor = model.generate_content(audit_prompt)
            audit_critique = response_auditor.text

        except ValueError:
            # Handle Google Safety Blocks on the second call
            finish_reason = response_auditor.candidates[0].finish_reason if response_auditor.candidates else "Unknown"
            audit_critique = f"⚠️ **Audit Blocked.** The API refused to return the audit response (Finish Reason: {finish_reason})."

        except Exception as e:
            # Handle API errors that happen during the second call
            audit_critique = f"❌ **API Error during Audit:** {str(e)}"

        return initial_analysis, audit_critique

    except Exception as e:
        # Ultimate Catch-All (e.g., if model initialization fails entirely)
        return f"🚨 **Critical System Error:** {str(e)}", "System failed to initialize the AI model."


def generate_postmortem(model_name: str, incident_data: str) -> str:
    """Generates a structured postmortem report using the postmortem prompt function."""
    try:
        model = genai.GenerativeModel(model_name)
        postmortem_prompt = get_postmortem_prompt(incident_data)
        response = model.generate_content(postmortem_prompt)
        return response.text
    except Exception as e:
        return f"Error generating postmortem: {str(e)}"