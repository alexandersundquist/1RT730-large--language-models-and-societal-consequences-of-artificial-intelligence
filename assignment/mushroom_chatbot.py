import gradio as gr
import random
from google import genai
from google.genai import types
import time
from dotenv import load_dotenv
import os
import mimetypes

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client()
# Use the recommended auto-updated alias for a stable model.
# gemini-2.0-flash is the recommended auto-updated alias for new projects.
chat = client.chats.create(
    model="gemini-2.5-flash",
    # system_instruction="You are a friendly and highly knowledgeable mushroom expert. Provide accurate information about identification, edibility, and related facts about mushrooms. Keep your responses concise and helpful."
)

def response(message: dict | str, history: list):
    """
    Handles multimodal input by uploading files via the API, sending the message, 
    and then deleting the temporary files.
    """
    user_message = ""
    file_paths = []
    
    if isinstance(message, dict):
        user_message = message.get("text", "")
        # The 'files' key returns a list of file paths.
        file_paths = message.get("files", [])
    elif isinstance(message, str):
        user_message = message

    content_parts = []
    uploaded_files = []
    
    try:
        # Process files (images)
        for path in file_paths:
            # FIX: The client.files.upload method requires a keyword argument 'file'.
            # The official documentation shows the correct syntax is client.files.upload(file=path).
            uploaded_file = client.files.upload(file=path)
            content_parts.append(uploaded_file)
            uploaded_files.append(uploaded_file)
            
        # Add the text prompt if it exists
        if user_message:
            content_parts.append(user_message)

        if not content_parts:
            yield "Please provide a question or an image."
            return

        api_response = chat.send_message(content_parts)

        # Stream the text response
        for i in range(len(api_response.text)):
            time.sleep(0.03) 
            yield api_response.text[: i + 1]
            
    except Exception as e:
        print(f"An error occurred: {e}")
        yield f"An error occurred: {e}"
    """
    finally:
        # Clean up uploaded files after the API call finishes, regardless of outcome.
        for f in uploaded_files:
            try:
                client.files.delete(name=f.name)
            except Exception as cleanup_e:
                print(f"Cleanup error for file {f.name}: {cleanup_e}")"""

with gr.Blocks(fill_height=True) as demo:
    chatbot = gr.ChatInterface(
        fn=response,
        title="🍄 Your Personal Mushroom Expert 🐝‍➕",
        type="messages",
        save_history=True,
        chatbot=gr.Chatbot(placeholder="<strong>Your Personal Chatbot</strong><br>Ask Me Anything", height=400),
        textbox=gr.MultimodalTextbox(
            file_count="multiple", 
            file_types=["image"],
            placeholder="Ask a question or upload an image of a mushroom..."
        ),
        theme="ocean",
        multimodal=True,
    )

if __name__ == "__main__":
    demo.launch()