import requests
import json
import os
from PyPDF2 import PdfReader
from docx import Document

# Retrieve OpenRouter API key from environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set")

# Path to your preloaded document (update this with your file path)
PRELOADED_DOCUMENT_PATH = r"C:\Users\theno\Desktop\project book\لائحة الساعات المعتمدة-علوم الحاسب .docx"

# Utility functions for extracting text from PDFs and Word documents
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

# Function to summarize long text using the OpenRouter API
def summarize_text(text, max_input_length=5000):

    # Truncate the input text to avoid exceeding the token limit
    truncated_text = text[:max_input_length]

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": f"Summarize the following text in 200 words or less:\n\n{truncated_text}"}
                ],
            }),
            timeout=30
        )
        response.raise_for_status()
        api_response = response.json()
        if "choices" in api_response and len(api_response["choices"]) > 0:
            return api_response["choices"][0]["message"]["content"]
        else:
            print("Unexpected API response format during summarization:", api_response)
            return "Summary not available."
    except requests.exceptions.RequestException as e:
        print(f"Error summarizing text: {e}")
        return "Summary not available."

# Function to send messages to OpenRouter API
def send_message_to_model(messages):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "openai/gpt-3.5-turbo",
                "messages": messages,
            }),
            timeout=30
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        api_response = response.json()
        if "choices" in api_response and len(api_response["choices"]) > 0:
            return api_response["choices"][0]["message"]["content"]
        else:
            print("Unexpected API response format:", api_response)
            return "I'm sorry, I encountered an issue. Please try again later."
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with the API: {e}")
        return "I'm sorry, I encountered an issue. Please try again later."

# Preload the document and prepare its content
def preload_document():
    if not os.path.exists(PRELOADED_DOCUMENT_PATH):
        print(f"Preloaded document not found at: {PRELOADED_DOCUMENT_PATH}")
        return None

    if PRELOADED_DOCUMENT_PATH.lower().endswith(".pdf"):
        text = extract_text_from_pdf(PRELOADED_DOCUMENT_PATH)
    elif PRELOADED_DOCUMENT_PATH.lower().endswith(".docx"):
        text = extract_text_from_docx(PRELOADED_DOCUMENT_PATH)
    else:
        print("Unsupported file format for preloaded document.")
        return None

    # Summarize the document content
    summarized_content = summarize_text(text)
    return summarized_content

# Main chatbot function
def chatbot(preloaded_content):
    print("Welcome to the Chatbot! Type 'exit' to end the conversation.")

    messages = []  # Conversation history
    MAX_HISTORY_LENGTH = 10  # Maximum number of messages to keep

    # Inject preloaded content into the conversation
    if preloaded_content:
        messages.append({"role": "system", "content": f"Here is some context: {preloaded_content}"})

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Add user message to the conversation history
        messages.append({"role": "user", "content": user_input})

        # Limit conversation history length
        messages = messages[-MAX_HISTORY_LENGTH:]

        # Get the assistant's response
        assistant_response = send_message_to_model(messages)

        if assistant_response:
            print(f"\nBot: {assistant_response}")
            # Add assistant's response to the conversation history
            messages.append({"role": "assistant", "content": assistant_response})
        else:
            print("\nBot: Sorry, I encountered an issue. Please try again later.")

if __name__ == "__main__":
    # Preload the document content
    preloaded_content = preload_document()

    if preloaded_content is not None:
        # Start the chatbot with the preloaded content
        chatbot(preloaded_content)
    else:
        print("Failed to load document. Exiting.")