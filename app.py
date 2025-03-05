import re
import streamlit as st
import groq

# --- Configuration ---
st.set_page_config(
    page_title="Coding Algorithm Assistant Chatbot",
    page_icon=":computer:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- CSS Styling ---
st.markdown(
    """
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #000000; /* Black background */
        color: #d4ff00; /* Neon Green text */
    }

    .stApp {
        max-width: 800px;
        margin: 0 auto;
        padding: 30px;
        background-color: #120539; /* Dark Purple background */
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(139, 0, 255, 0.3); /* Purple glow */
    }

    .stApp h1 {
        color: #f000ff !important; /* Pink header */
        text-align: center;
    }

    .stApp .stTextInput>label {
        color: #d4ff00; /* Neon Green label */
    }

    .stApp .stButton>button {
        background-image: linear-gradient(to right, #f000ff, #5f00ff); /* Gradient button */
        color: #ffffff; /* White text */
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .stApp .stButton>button:hover {
        background-image: linear-gradient(to right, #d400e0, #4f00e0); /* Darker gradient */
    }

    .stApp .stAlert {
        background-color: #0a0224; /* Darker Purple */
        color: #ff4081; /* Pink Accent Color */
        border: 1px solid #ff4081; /* Pink border */
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }

    .stApp .page-label>label {
        color: #d4ff00 !important; /* Neon Green label */
    }

    .stApp .algorithm-output {
        margin-top: 10px;  /* Reduced margin */
        padding: 10px; /* Reduced padding */
        background-color: #1e0857; /* Darker Purple/Blue */
        border: 1px solid #a000ff; /* Bright Purple border */
        border-radius: 5px;
        white-space: pre-wrap;
        color: #d4ff00; /* Neon Green text */
        font-size: 1.1em;
        line-height: 1.4;   /* Reduced line-height */
    }

    .stApp .algorithm-output h3 {
        font-size: 1.2em; /* Reduced font size */
        margin-bottom: 0.3em; /* Reduced margin */
        color: #f000ff; /* Pink Header */
    }

    .stApp .algorithm-output p {
        margin-bottom: 0.7em; /* Reduced margin */
    }

    .stApp p {
        color: #d4ff00; /* Neon Green text */
    }

    .stApp #generated-algorithm {
        color: #d4ff00; /* Neon Green text */
    }

    .stApp .dynamic-typing-note {
        font-style: italic;
        color: #9fa2a8; /* Light Gray */
        margin-top: 0.3em;  /* Reduced margin */
    }
    .message {
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 5px;
    }

    .user-message {
        background-color: #333333; /* Darker background for user messages */
        color: #ffffff;
        text-align: right;
        margin-left: 20%;
    }

    .bot-message {
        background-color: #1A0544; /* Dark Purple Background for bot messages */
        color: #d4ff00;
        text-align: left;
        margin-right: 20%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Initialize Groq Client ---
try:
    groq_api_key = "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"
    client = groq.Client(api_key=groq_api_key)
    model_available = True
except Exception as e:
    st.error(f"Error initializing Groq client: {e}")
    model_available = False


def get_algorithm(problem_description, programming_language="Any"):
    """
    Generate an algorithm explanation for a given coding problem, with examples at each step,
    and adapting to dynamic typing.

    Args:
        problem_description (str): The description of the coding problem.
        programming_language (str): The programming language the algorithm should be based on
                                  ("Any" for no preference).

    Returns:
        tuple: (str algorithm_explanation, bool assumes_dynamic_typing)
               Returns both the explanation and a flag indicating if it's dynamically typed.
    """

    prompt = f"Explain the algorithm to solve the following coding problem:\n\n{problem_description}\n\n"
    assumes_dynamic_typing = False
    dynamic_typing_note = ""  # Initialize the note

    if programming_language != "Any":
        prompt += f"Explain it in terms of concepts relevant to {programming_language}.\n"

    if programming_language in ["Python", "JavaScript"]:
        prompt += "Explain the algorithm, *emphasizing how dynamic typing affects the implementation.* Specifically, discuss how the lack of compile-time type checking influences the design and how you would handle potential type errors at runtime. For example, in Python, you don't need to declare the type of a variable before assigning it a value. How does this affect the algorithm?\n"
        assumes_dynamic_typing = True
        prompt += "When providing examples, make them valid Python or JavaScript code snippets that illustrate the concept of dynamic typing (e.g., assigning different types to the same variable, checking types at runtime). *Also, explicitly state that you are using a dynamically-typed approach in the explanation.*"  # Dynamic typing examples
        dynamic_typing_note = "<p class='dynamic-typing-note'>Note: This explanation assumes a dynamically typed language like Python or JavaScript.</p>" #Added so the user get to know
    else:
        prompt += "Explain the algorithm.\n"

    prompt += "Provide a step-by-step explanation of the algorithm. Do NOT provide any actual code. Focus on the logic and steps involved. Only give the algorithm."
    prompt += "If I ask something beyond algorithm for coding such as other fields, tell me that it is beyond my limits"
    prompt += "Organize the explanation into clear sections with headings and subheadings to improve readability."
    prompt += "Use concise language and avoid unnecessary jargon. Prioritize clarity and ease of understanding."
    prompt += "For each step in the algorithm, provide a concise example illustrating that step. Make sure that you follow the explanation in each step. Do not creat a random examples."  # NEW: Step-by-step examples

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.3, # Lower temperature!
            top_p=0.5       # Lower top_p!
        )

        output = response.choices[0].message.content
        cleaned_output = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL).strip()
        cleaned_output = re.sub(r'```.*?```', '', output, flags=re.DOTALL).strip()
        cleaned_output = re.sub(r"Algorithm:.*", '', cleaned_output, flags=re.DOTALL).strip()

        # Include the dynamic typing note in the explanation itself
        if assumes_dynamic_typing:
            cleaned_output += dynamic_typing_note

        return cleaned_output, assumes_dynamic_typing

    except Exception as e:
        st.error(f"Error generating algorithm explanation: {e}")
        return None, False


# --- Streamlit App ---
st.title("Coding Algorithm Assistant Chatbot")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Describe your coding problem..."):
    # Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get the bots responce
    algorithm_explanation, assumes_dynamic_typing = get_algorithm(prompt)

    # Display bot message in chat message container
    with st.chat_message("assistant"):
        st.markdown(algorithm_explanation or "Sorry, I encountered an error generating the algorithm explanation.") #Always show a response
        if assumes_dynamic_typing:
            st.markdown("<p class='dynamic-typing-note'>Note: This explanation assumes a dynamically typed language like Python or JavaScript.</p>", unsafe_allow_html=True) #Always show the note in Dynamic typing
    st.session_state.messages.append({"role": "assistant", "content": algorithm_explanation if algorithm_explanation else "Sorry, I encountered an error generating the algorithm explanation."})
