def extract_text_from_file(uploaded_file) -> str:
    """Decodes a Streamlit UploadedFile byte stream into a UTF-8 string."""
    if uploaded_file is not None:
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception as e:
            return f"Error reading file: {str(e)}"
    return ""