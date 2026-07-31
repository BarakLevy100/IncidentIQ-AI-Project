import json
import streamlit as st
from ai_service import configure_gemini, run_incident_analysis, generate_postmortem
from ui_components import render_sidebar, render_main_ui, display_results, render_export_sidebar

API_KEY = st.secrets["GEMINI_API_KEY"] # put the api key here or create the folder .streamlit and the file secrets.toml and put there GEMINI_API_KEY = "YOUR API KEY".


def initialize_app():
    """Load external CSS styles and default configuration data on startup."""
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    try:
        with open("scenario_logs.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def check_and_clear_state_for_new_logs(current_logs):
    """Clear the data of the analysis, audit and postmortem only if the user is giving different logs."""
    if st.session_state.get("last_processed_logs") != current_logs:
        st.session_state.pop("initial_analysis", None)
        st.session_state.pop("audit_critique", None)
        st.session_state.pop("postmortem_result", None)
        st.session_state["last_processed_logs"] = current_logs


def main():
    """Main execution function coordinating the Streamlit app flow."""
    # 1. Setup API
    configure_gemini(API_KEY)

    # 2. Gets all the logs from the JSON file
    example_logs_dict = initialize_app()

    # 3. Render UI Components
    selected_model, prompt_style, response_length, target_audience = render_sidebar()
    logs_input, analyze_btn, postmortem_btn = render_main_ui(example_logs_dict)

    # 4. Handle Actions
    if analyze_btn:
        if logs_input.strip():
            check_and_clear_state_for_new_logs(logs_input)

            with st.spinner(f"AI {selected_model} is analyzing the data..."):
                initial_analysis, audit_critique = run_incident_analysis(
                    selected_model, prompt_style, logs_input, response_length, target_audience
                )
                st.session_state["initial_analysis"] = initial_analysis
                st.session_state["audit_critique"] = audit_critique
                st.success("Analysis complete!")
        else:
            st.warning("Please paste logs before clicking.")

    if postmortem_btn:
        if logs_input.strip():
            check_and_clear_state_for_new_logs(logs_input)

            with st.spinner(f"Generating postmortem via {selected_model}..."):
                postmortem_md = generate_postmortem(selected_model, logs_input)
                st.session_state["postmortem_result"] = postmortem_md
                st.success("Postmortem generated!")
        else:
            st.warning("Please paste logs before generating a postmortem.")

    # 5. Display Results and Export Options
    display_results()
    render_export_sidebar(selected_model, prompt_style, target_audience, response_length)

if __name__ == "__main__":
    main()