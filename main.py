import json
import streamlit as st
from ai_service import configure_gemini, run_incident_analysis, generate_postmortem
from utils import create_pdf


def initialize_app():
    """Load external CSS styles and default configuration data on startup."""
    # 1. Load CSS
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Fallback gracefully if style.css isn't created yet

    # 2. Load default logs from JSON
    try:
        with open("scenario_logs.json", "r") as f:
            data = json.load(f)
            return data.get("default_logs", "")
    except FileNotFoundError:
        return ""


def render_sidebar():
    """Render the sidebar controls and return the selected configuration."""
    st.sidebar.header("AI Evaluation Controls")
    selected_model_name = st.sidebar.selectbox(
        "Choose AI Model:",
        ["gemini-3.5-flash"]
    )

    prompt_style = st.sidebar.selectbox(
        "Prompt Variation:",
        ["Standard SRE Analysis", "Strictly Conservative (Low Hallucination)"]
    )

    return selected_model_name, prompt_style


def render_main_ui(default_logs):
    """Render the main input area and buttons, returning the log text and button clicks."""
    st.title("IncidentIQ — AI Incident Response Tool")
    st.write("An AI-powered system for incident analysis, cognitive bias detection, and postmortem generation.")

    logs_input = st.text_area("Paste system logs here:", value=default_logs, height=200)

    col1, col2 = st.columns([1, 1])
    with col1:
        analyze_btn = st.button("Analyze Incident", type="primary", use_container_width=True)

    return logs_input, analyze_btn


def display_results():
    """Display the analysis results in tabs if they exist in session state."""
    if "initial_analysis" in st.session_state:
        st.markdown("---")
        tab1, tab2 = st.tabs(["AI Investigation Report", "Skeptical Audit & Biases"])

        with tab1:
            if "initial_analysis" in st.session_state:
                st.markdown(st.session_state["initial_analysis"])

        with tab2:
            if "audit_critique" in st.session_state:
                st.markdown(st.session_state["audit_critique"])


def main():
    """Main execution function coordinating the Streamlit app flow."""
    # 1. Setup API & Defaults
    configure_gemini(st.secrets["GEMINI_API_KEY"])
    default_logs = initialize_app()

    # 2. Render UI Components
    selected_model, prompt_style = render_sidebar()
    logs_input, analyze_btn = render_main_ui(default_logs)

    # 3. Handle Actions
    if analyze_btn:
        if logs_input.strip():
            with st.spinner(f"AI {selected_model} is analyzing the data..."):
                initial_analysis, audit_critique = run_incident_analysis(
                    selected_model, prompt_style, logs_input
                )
                st.session_state["initial_analysis"] = initial_analysis
                st.session_state["audit_critique"] = audit_critique
                st.success("Analysis complete!")
        else:
            st.warning("Please paste logs before clicking.")

    # 4. Display Results
    display_results()


if __name__ == "__main__":
    main()