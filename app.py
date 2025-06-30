import os
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel, Field
from google import genai
import warnings

# --- 1. INITIALIZATION AND CONFIGURATION ---
warnings.filterwarnings("ignore")

# Load API Key from environment variable for production safety
try:
    api_key = "AIzaSyDrZir3-Y1WUAnhrGKy9U37_1Nwe2F5bE8" or os.getenv("GEMNINI_API_KEY")
    if not api_key:
        raise ValueError("GEMNINI_API_KEY environment variable not found.")
    # Initialize the client exactly as requested
    client = genai.Client(api_key=api_key)
    print("✅ Gemini Client initialized successfully.")
except Exception as e:
    print(f"🛑 ERROR initializing Gemini: {e}")
    client = None


# --- 2. SAFETY GUARDRAILS & CORE LOGIC ---
SENSITIVE_KEYWORDS = [
    "suicide", "kill myself", "want to die", "chest pain", "can't breathe",
    "stroke", "unconscious", "severe bleeding", "heart attack", "poison",
]
EMERGENCY_RESPONSE = "If you believe you are experiencing a medical emergency, please dial your local emergency number (e.g., 911 in the US) immediately or go to the nearest emergency room. This service is for informational purposes only and cannot handle medical emergencies."
DISCLAIMER = "Disclaimer: This is for informational purposes only and does not constitute medical advice. Please consult a healthcare professional for any health concerns."

def is_query_sensitive(query: str) -> bool:
    """Checks if a user's query contains any sensitive or emergency-related keywords."""
    return any(keyword in query.lower() for keyword in SENSITIVE_KEYWORDS)

def generate_response(query: str, method: str) -> str:
    """The complete inference pipeline, now supporting multiple prompting techniques."""
    if not client:
        return "Gemini Client not initialized. The GOOGLE_API_KEY may be missing or invalid."
    if is_query_sensitive(query):
        return EMERGENCY_RESPONSE

    # --- This is where we select the prompt based on the user's choice ---
    if method == 'Zero-Shot':
        prompt = f"""You are a helpful and harmless AI assistant for a healthcare organization. Your role is to provide general and safe health information based on the user's question. You must not provide a diagnosis or medical advice. Your response must always end with the following disclaimer, exactly as written: "{DISCLAIMER}"

Question: "{query}"
Answer:"""

    elif method == 'Few-Shot':
        prompt = f"""You are a helpful and harmless AI assistant for a healthcare organization. Your role is to provide general and safe health information. You must not provide a diagnosis or medical advice. Your response must always end with the following disclaimer, exactly as written: "{DISCLAIMER}"

### Example 1
Question: "What are the symptoms of the flu?"
Answer: "Common symptoms of the flu include fever, cough, sore throat, runny or stuffy nose, body aches, headache, chills, and fatigue. Some people may have vomiting and diarrhea, though this is more common in children than adults. {DISCLAIMER}"

### Example 2
Question: "How does paracetamol work?"
Answer: "Paracetamol, also known as acetaminophen, works primarily in the brain to block pain and fever signals. It is thought to inhibit the production of chemicals called prostaglandins, which are involved in pain and inflammation. {DISCLAIMER}"

### Your Turn
Question: "{query}"
Answer:"""

    else:  # Chain-of-Thought (The most robust method)
        prompt = f"""You are a helpful and harmless AI assistant for a healthcare organization. Your task is to answer medical questions safely by following a step-by-step reasoning process.

### Chain-of-Thought Example
Question: "What is hypertension?"

My thought process:
Step 1: Identify the core medical term. The term is "hypertension".
Step 2: Define the term in simple language. Hypertension is the medical term for high blood pressure.
Step 3: Explain its significance. It means the force of blood against the artery walls is consistently too high, which can lead to health problems like heart disease.
Step 4: Mention common contributing factors in general terms. Factors include diet, lack of exercise, genetics, and age.
Step 5: Formulate the final, safe answer by combining the steps and ensuring no medical advice is given.
Step 6: Add the mandatory disclaimer at the end.

Final Answer: "Hypertension is the medical term for high blood pressure. This means the pressure in your blood vessels is consistently too high. Over time, this can damage arteries and lead to serious health issues like heart disease and stroke. General factors that can contribute to hypertension include diet, lifestyle, age, and family history. {DISCLAIMER}"

### Your Turn
Question: "{query}"

My thought process:
Step 1: Identify the core medical term in the user's query.
Step 2: Break down the query and define the key concepts simply.
Step 3: Explain the general context or mechanism without giving specific advice.
Step 4: Formulate the final, safe answer for the user based on the reasoning steps.
Step 5: Add the mandatory disclaimer at the very end.

Final Answer:"""

    try:
        # Call the Gemini API using the client.models.generate_content method
        response = client.models.generate_content(
            model="models/gemini-1.5-flash-latest",
            contents=prompt
        )
        # Extract the final answer, which might be after the model's own "Final Answer:" text
        response_text = response.text.split("Final Answer:")[-1].strip()

    except Exception as e:
        return f"Error communicating with the Gemini API: {e}"

    # Final output guardrail to ensure the disclaimer is always present
    if "disclaimer" not in response_text.lower():
        response_text += f"\n\n{DISCLAIMER}"
        
    return response_text

# --- 3. GRADIO INTERFACE DEFINITION ---
with gr.Blocks(theme=gr.themes.Soft(), title="Prompting Techniques Lab") as interface:
    gr.Markdown("# Healthcare AI Assistant: A Prompting Laboratory")
    gr.Markdown("Experiment with different prompting techniques to see how they affect the AI's response quality and safety. **For emergencies, call your local emergency number immediately.**")
    
    with gr.Row():
        method_selector = gr.Radio(
            ["Zero-Shot", "Few-Shot", "Chain-of-Thought"], 
            label="🔬 Prompting Technique", 
            value="Chain-of-Thought" # Default to the best method
        )
    
    chatbot = gr.Chatbot(label="Conversation", height=500, bubble_full_width=False)
    
    with gr.Row():
        msg_textbox = gr.Textbox(
            label="Your Question", 
            placeholder="e.g., What causes seasonal allergies?",
            scale=7 # Make the textbox wider
        )
        clear_button = gr.ClearButton([msg_textbox, chatbot], scale=1)
    
    def chat_interface(message, history, method):
        # The Gradio interface calls our core logic function with the selected method
        response = generate_response(message, method)
        history.append((message, response))
        return "", history

    msg_textbox.submit(chat_interface, [msg_textbox, chatbot, method_selector], [msg_textbox, chatbot])

# --- 4. LAUNCH THE APP ---
if __name__ == "__main__":
    interface.launch(debug=True)