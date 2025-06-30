import torch
from fastapi import FastAPI
from pydantic import BaseModel, Field
from peft import PeftModel, PeftConfig
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import gradio as gr
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# --- 1. CONFIGURATION AND SAFETY GUARDRAILS ---
MODEL_PATH = "./healthcare-assistant-lora"
SENSITIVE_KEYWORDS = [
    "suicide", "kill myself", "want to die", "chest pain", "can't breathe",
    "stroke", "unconscious", "severe bleeding", "heart attack", "poison",
    "overdose", "seizure", "choking", "i am hurt"
]
EMERGENCY_RESPONSE = "If you believe you are experiencing a medical emergency, please dial your local emergency number (e.g., 911 in the US) immediately or go to the nearest emergency room. This service is for informational purposes only and cannot handle medical emergencies."
DISCLAIMER = "Disclaimer: This is for informational purposes only and does not constitute medical advice. Please consult a healthcare professional for any health concerns."

def is_query_sensitive(query: str) -> bool:
    return any(keyword in query.lower() for keyword in SENSITIVE_KEYWORDS)

# --- 2. LOAD FINE-TUNED MODEL AND TOKENIZER ---
print("Loading model and tokenizer...")
config = PeftConfig.from_pretrained(MODEL_PATH)
base_model = AutoModelForSeq2SeqLM.from_pretrained(config.base_model_name_or_path, return_dict=True, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
model = PeftModel.from_pretrained(base_model, MODEL_PATH)
model.eval()
# Move model to GPU if available
if torch.cuda.is_available():
    model = model.to('cuda')
print("Model loaded successfully.")

# --- 3. CORE INFERENCE LOGIC ---
def generate_response(query: str) -> str:
    """Combines all three safety layers to generate a safe response."""
    # Layer 1: Input Guardrail
    if is_query_sensitive(query):
        return EMERGENCY_RESPONSE

    # Layer 2: Prompt Engineering
    prompt = f"""### Instruction:
Answer the following medical question accurately and safely. You are a helpful AI assistant, not a doctor. Always include a disclaimer to consult a healthcare professional.

### Question:
{query}

### Answer:"""
    
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = inputs.to('cuda')
        
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=256, do_sample=True, temperature=0.7, top_p=0.9)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Layer 3: Output Guardrail
    if "disclaimer" not in response_text.lower():
        response_text += f"\n\n{DISCLAIMER}"
        
    return response_text

# --- 4. FASTAPI APP AND GRADIO UI ---
app = FastAPI()

class Query(BaseModel):
    text: str = Field(..., title="User Query", example="What are the symptoms of the flu?")

@app.post("/ask", summary="Ask a health question")
async def ask_question(query: Query):
    """API endpoint to get a response from the healthcare assistant."""
    response = generate_response(query.text)
    return {"response": response}

def create_gradio_ui():
    """Builds the Gradio web interface."""
    with gr.Blocks(theme=gr.themes.Soft(), title="Healthcare AI Assistant") as interface:
        gr.Markdown("# Healthcare AI Assistant")
        gr.Markdown("This AI provides general health information. It is not a substitute for a doctor. **For emergencies, call your local emergency number immediately.**")
        
        chatbot = gr.Chatbot(label="Conversation", height=500)
        msg_textbox = gr.Textbox(label="Your Question", placeholder="e.g., What is the difference between a cold and the flu?")
        
        def chat_interface(message, history):
            response = generate_response(message)
            history.append((message, response))
            return "", history

        msg_textbox.submit(chat_interface, [msg_textbox, chatbot], [msg_textbox, chatbot])
        gr.ClearButton([msg_textbox, chatbot])
    
    return interface

# Mount the Gradio UI onto the FastAPI application at the root path
gradio_ui = create_gradio_ui()
app = gr.mount_gradio_app(app, gradio_ui, path="/")