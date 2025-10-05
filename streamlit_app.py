import streamlit as st
import os
import json
from google.cloud import dialogflowcx_v3beta1 as dialogflow_cx
from google.oauth2 import service_account

# --- Load credentials from Streamlit secrets ---
service_account_info = st.secrets["GCP_SERVICE_ACCOUNT_JSON"]
if isinstance(service_account_info, str):
    service_account_info = json.loads(service_account_info)

credentials = service_account.Credentials.from_service_account_info(service_account_info)

PROJECT_ID = st.secrets["PROJECT_ID"]
AGENT_ID = st.secrets["AGENT_ID"]
LOCATION = st.secrets["LOCATION"]
LANGUAGE_CODE = st.secrets.get("LANGUAGE_CODE", "en")

# Build session client
session_client = dialogflow_cx.SessionsClient(credentials=credentials)
session_path = f"projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/sessions/streamlit-session"

# --- Streamlit UI ---
st.set_page_config(page_title="Dialogflow CX Chatbot", page_icon="🤖")
st.title("🤖 Dialogflow CX Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if user_input := st.chat_input("Type your message"):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send query to Dialogflow CX
    text_input = dialogflow_cx.TextInput(text=user_input)
    query_input = dialogflow_cx.QueryInput(text=text_input, language_code=LANGUAGE_CODE)

    request = dialogflow_cx.DetectIntentRequest(
        session=session_path,
        query_input=query_input,
    )

    response = session_client.detect_intent(request=request)
    bot_reply = response.query_result.response_messages[0].text.text[0] if response.query_result.response_messages else "..."

    # Save bot reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
```


