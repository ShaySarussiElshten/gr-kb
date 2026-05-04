import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Graph RAG Chatbot", page_icon="🕸️")

st.title("Microservices Graph RAG 🕸️")
st.markdown("Ask questions about the microservices architecture, databases, teams, and their relationships.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("E.g., Which services will be affected if the Redis database goes down?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send request to backend
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Exclude the current prompt from the history we send
            history_to_send = st.session_state.messages[:-1]
            
            response = requests.post(
                f"{BACKEND_URL}/chat", 
                json={
                    "message": prompt,
                    "chat_history": history_to_send
                },
                timeout=60
            )
            
            if response.status_code == 200:
                assistant_response = response.json().get("response", "No response from backend.")
                message_placeholder.markdown(assistant_response)
            else:
                assistant_response = f"Backend error ({response.status_code}): {response.text}"
                message_placeholder.error(assistant_response)
                
        except requests.exceptions.RequestException as e:
            assistant_response = f"Error connecting to the backend: {str(e)}"
            message_placeholder.error(assistant_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
