import textwrap

def get_the_length_prompt(length: str):
    """Return the Length"""
    prompt = ""

    if "Short" in length:
        prompt += "\nLength Constraint: Keep the response extremely concise. Use bullet points and focus only on the absolute most critical information."
    elif "Long" in length:
        prompt += "\nLength Constraint: Be exhaustive and highly detailed. Expand on your reasoning for every hypothesis and provide comprehensive debugging paths."
    else:
        prompt += "\nLength Constraint: Provide a standard, balanced response."

    return prompt

def get_investigator_prompt(style: str, logs: str) -> str:
    """Generates the primary SRE analysis prompt based on selected behavior style."""
    normalized_style = style.strip().lower()

    if "standard" in normalized_style:
        prompt = f"""
        You are a Lead Site Reliability Engineer. 
        Analyze the following logs and provide your response using these exact 4 numbered headings:
        1. Timeline of events
        2. Facts vs. Assumptions
        3. Top Root-Cause Hypotheses (ranked by confidence)
        4. Recommended Debugging Actions

        Logs:
        {logs}
        """
    else:
        # Default to Conservative mode
        prompt = f"""
        You are a highly conservative Site Reliability Engineer. 
        Analyze the following incident data. DO NOT make assumptions beyond explicit log entries. 
        If a fact is missing, explicitly state 'Unknown based on logs'.

        Provide your response using these exact 4 numbered headings:
        1. Timeline of events
        2. Facts vs. Assumptions
        3. Top Root-Cause Hypotheses (ranked by confidence)
        4. Recommended Debugging Actions

        Logs:
        {logs}
        """

    # 2. Audience Modifier
    # if "Management" in audience:
    #    prompt += "\nAudience: Management. Focus on business impact, high-level root cause, and clear explanations. Avoid raw code or overly dense technical jargon."
    # elif "Engineering" in audience:
    #    prompt += "\nAudience: Engineering. Be highly technical. Include specific system architecture assumptions, code-level hypotheses, and exact terminal commands."
    # else:
    #    prompt += "\nAudience: Support Team. Provide clear, actionable steps and straightforward explanations that a Tier-1 or Tier-2 support agent can follow."

    return textwrap.dedent(prompt).strip()


def get_auditor_prompt(initial_analysis: str, logs: str) -> str:
    """Generates the skeptical auditor prompt to critique primary analysis."""
    prompt = f"""
    You are an objective AI system auditor reviewing an AI-generated incident diagnosis. 
    Critique the initial analysis based strictly on the original logs.
    Do not use words like "you" or "yours". Refer to the text as "the initial analysis" or "the AI response".

    Original Analysis:
    {initial_analysis}

    Original Logs:
    {logs}

    Your Job:
    1. Identify unsupported claims, ungrounded speculation, or hallucinations in the initial analysis.
    2. Highlight any Post Hoc Fallacy (e.g., assuming a deployment caused the failure solely because it preceded the incident).
    3. Point out any Confirmation Bias or Automation Bias in the reasoning.
    4. What critical questions did the initial analysis fail to ask?
    """

    return textwrap.dedent(prompt).strip()


def get_postmortem_prompt(incident_data: str) -> str:
    """Generates a blameless Post Incident Report prompt."""
    prompt = f"""
    You are a Lead Reliability Engineer writing a formal, blameless Post-Incident Report (PIR).
    Based on the provided incident raw data, generate a structured postmortem in Markdown format.

    Include these exact Markdown headings (use '##'):
    ## 1. Executive Summary & Impact
    ## 2. Incident Timeline
    ## 3. Root Cause Analysis (5 Whys)
    ## 4. Lessons Learned & Action Items

    Raw Incident Details:
    {incident_data}
    """

    return textwrap.dedent(prompt).strip()