import os
from groq import Groq


# ---------------------------------
# Load Groq API Key
# ---------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY environment variable is not set."
    )


# ---------------------------------
# Initialize Groq Client
# ---------------------------------

client = Groq(api_key=GROQ_API_KEY)


# ---------------------------------
# Model Configuration
# ---------------------------------

MODEL_NAME = "llama-3.3-70b-versatile"


# ---------------------------------
# LLM Call Function
# ---------------------------------

def ask_llm(messages, temperature=0.2, max_tokens=800):
    """
    Sends chat messages to Groq LLM.

    Parameters
    ----------
    messages : list
        Chat-format messages:
        [
          {"role":"system","content":"..."},
          {"role":"user","content":"..."}
        ]

    temperature : float
        Sampling temperature.

    max_tokens : int
        Maximum tokens to generate.

    Returns
    -------
    str
        Model response text
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content