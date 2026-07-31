import streamlit as st
from pdf_creator import create_pdf
from file_handler import extract_text_from_file

def render_sidebar():
    """Render the sidebar controls and return the selected configuration."""
    st.sidebar.header("AI Evaluation Controls")
    selected_model_name = st.sidebar.selectbox(
        "Choose AI Model:",
        ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"]
    )

    st.sidebar.markdown("---")
    st.sidebar.header("Analysis Settings")

    prompt_style = st.sidebar.selectbox(
        "Prompt Variation:",
        ["Standard Analysis", "Strictly Conservative (Low Hallucination)"],
        help="Conservative mode restricts the AI to strict, verifiable data from the logs only."
    )

    target_audience = st.sidebar.selectbox(
        "Target Audience:",
        ["Engineering", "Management", "Support Team"]
    )

    response_length = st.sidebar.radio(
        "Analyze Response Length:",
        options=["Short", "Normal", "Long"],
        index=1,
        horizontal=True
    )

    return selected_model_name, prompt_style, response_length, target_audience


def render_main_ui(example_logs_dict):
    """Render the main input area and buttons, returning the log text and button clicks."""
    st.title("IncidentIQ — AI Incident Response Tool")
    st.write("An AI-powered system for incident analysis, cognitive bias detection, and postmortem generation.")

    # 1. The file uploader
    uploaded_file = st.file_uploader("Upload Incident Logs", type=["txt", "json", "log", "csv"])

    # 2. The example dropdown menu
    example_keys = ["Select an example..."] + list(example_logs_dict.keys())
    selected_example = st.selectbox("Or test with a sample incident:", example_keys)

    logs_input = ""

    # 3. Determine which data to use
    if uploaded_file:
        logs_input = extract_text_from_file(uploaded_file)
        st.success("File successfully loaded!")
    elif selected_example != "Select an example..." and selected_example in example_logs_dict:
        logs_input = example_logs_dict[selected_example]
        st.info(f"Loaded sample dataset: {selected_example}")
        with st.expander("View Sample Logs"):
            st.code(logs_input, language="text")
    else:
        logs_input = st.text_area("Or paste raw incident logs here:", height=200)

    col1, col2 = st.columns([1, 1])
    with col1:
        analyze_btn = st.button("Analyze Incident", type="primary", use_container_width=True)
    with col2:
        postmortem_btn = st.button("Generate Postmortem", use_container_width=True)

    return logs_input, analyze_btn, postmortem_btn


def display_results():
    """Display the analysis and postmortem results in tabs if they exist in session state."""
    if "initial_analysis" in st.session_state or "postmortem_result" in st.session_state:
        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["AI Investigation Report", "Skeptical Audit & Biases", "Postmortem"])

        with tab1:
            if "initial_analysis" in st.session_state:
                st.markdown(st.session_state["initial_analysis"])

        with tab2:
            if "audit_critique" in st.session_state:
                st.markdown(st.session_state["audit_critique"])

        with tab3:
            if "postmortem_result" in st.session_state:
                st.markdown(st.session_state["postmortem_result"])


def render_export_sidebar(model_name, prompt_style, target_audience, response_length):
    """Check for results and render the PDF export button in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.header("Export Options")

    has_data = any(key in st.session_state for key in ["initial_analysis", "audit_critique", "postmortem_result"])

    if has_data:
        dossier_parts = []

        if "postmortem_result" in st.session_state:
            dossier_parts.append(f"## Formal Postmortem\n{st.session_state['postmortem_result']}")

        if "initial_analysis" in st.session_state:
            dossier_parts.append(f"## AI Investigation Report\n{st.session_state['initial_analysis']}")

        if "audit_critique" in st.session_state:
            dossier_parts.append(f"## Skeptical Audit & Biases\n{st.session_state['audit_critique']}")

        full_dossier = "\n\n---\n\n".join(dossier_parts)
        pdf_bytes = create_pdf(full_dossier.strip(), model_name, prompt_style, target_audience, response_length)

        st.sidebar.download_button(
            label="📄 Download Current Report (PDF)",
            data=pdf_bytes,
            file_name="IncidentIQ_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.sidebar.info("Run an analysis or generate a postmortem to enable PDF export.")