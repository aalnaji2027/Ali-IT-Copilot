import streamlit as st

from src.memory.conversation import (
    save_conversation,
    get_conversations
)

st.set_page_config(
    page_title="Ali IT Copilot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Ali IT Copilot")

user_message = st.text_input(
    "Ask me something:"
)

if st.button("Send"):

    response = f"Received: {user_message}"

    save_conversation(
        user_message,
        response
    )

    st.success(response)

st.subheader("Conversation History")

history = get_conversations()

for item in history:
    st.write(f"**{item[0]}**")
    st.write(f"User: {item[1]}")
    st.write(f"Assistant: {item[2]}")
    st.divider()