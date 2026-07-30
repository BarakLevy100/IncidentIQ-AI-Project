import textwrap

def get_the_length_prompt(length: str):
    """Return the Length constraint formatted for any AI persona."""
    prompt = ""

    if "Short" in length:
        prompt += "\nLength Constraint: Keep the response extremely concise. Use bullet points and focus only on the absolute most critical information."
    elif "Long" in length:
        prompt += "\nLength Constraint: Be exhaustive and highly detailed. Expand on your reasoning for every point and provide a deeply comprehensive analysis."
    else:
        prompt += "\nLength Constraint: Provide a standard, balanced response."

    return prompt


def get_investigator_prompt(style: str, logs: str, length: str, audience: str) -> str:
    """Generates the primary SRE analysis prompt based on selected behavior style."""
    normalized_style = style.strip().lower()

    # 1. Establish the AI's Persona: Who the AI is
        # The standard mode
    if "standard" in normalized_style:
        persona = "You are a Lead Site Reliability Engineer."
    else:
        # The conservative mode
        persona = "You are a highly conservative Site Reliability Engineer. DO NOT make assumptions beyond explicit log entries. If a fact is missing, explicitly state 'Unknown based on logs'."

    # 2. Establish the Target Audience: Who the AI is talking to
    if "Management" in audience:
        audience_instruction = "Your target audience is Management. Focus on business impact, high-level root cause, and clear explanations. Avoid raw code or overly dense technical jargon."
    elif "Engineering" in audience:
        audience_instruction = "Your target audience is Engineering. Be highly technical. Include specific system architecture assumptions, code-level hypotheses, and exact terminal commands."
    else:
        audience_instruction = "Your target audience is the Support Team. Provide clear, actionable steps and straightforward explanations that a Tier-1 or Tier-2 support agent can follow."

    # 3. Build the final prompt
    prompt = f"""
    {persona}

    {audience_instruction}

    Analyze the following logs and provide your response using these exact 5 numbered markdown headings (use '##'):
    1. Timeline of events
    2. Facts vs. Assumptions
    3. Evidence-For vs. Evidence-Against (Format as a Markdown Table)
    4. Top Root-Cause Hypotheses (ranked by confidence)
    5. Recommended Debugging Actions

    Logs:
    {logs}
    """

    prompt += get_the_length_prompt(length)

    return textwrap.dedent(prompt).strip()


def get_auditor_prompt(initial_analysis: str, logs: str, length: str) -> str:
    """Generates the skeptical auditor prompt to critique primary analysis."""
    prompt = f"""
    You are an objective AI system auditor reviewing an AI-generated incident diagnosis. 
    Critique the initial analysis based strictly on the original logs.
    Do not use words like "you" or "yours". Refer to the text as "the initial analysis" or "the AI response".

    Original Analysis:
    {initial_analysis}

    Original Logs:
    {logs}

    Structure your audit report using exactly these 4 Markdown headings (use '##'):
    1. Identify unsupported claims, ungrounded speculation, or hallucinations in the initial analysis.
    2. Highlight any Post Hoc Fallacy (e.g., assuming a deployment caused the failure solely because it preceded the incident).
    3. Point out any Confirmation Bias or Automation Bias in the reasoning.
    4. What critical questions did the initial analysis fail to ask?
    """

    prompt += get_the_length_prompt(length)

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