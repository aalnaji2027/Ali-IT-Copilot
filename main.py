import streamlit as st

from src.memory.conversation import (
    save_conversation,
    get_conversations,
    clear_conversations
)

from src.memory.notes import (
    save_note,
    get_notes
)

from src.services.logger import logger

st.set_page_config(
    page_title="Ali IT Copilot",
    page_icon="🤖",
    layout="wide"
)

with st.sidebar:
    st.header("🤖 Ali IT Copilot")

    page = st.radio(
        "Navigation",
        [
            "Conversations",
            "Notes"
        ]
    )

    st.write("---")

    st.success("✅ Database Connected")
    st.success("✅ Logging Active")
    st.info("⏳ AI Not Connected")


# =========================
# Conversations Page
# =========================

if page == "Conversations":

    st.title("🤖 Ali IT Copilot")

    history = get_conversations()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Conversations",
            len(history)
        )

    with col2:
        st.metric(
            "Database Status",
            "Online"
        )

    if st.button("🗑 Clear History"):
        clear_conversations()
        st.rerun()

    user_message = st.text_input(
        "Ask me something:",
        key="conversation_input"
    )

    if st.button("Send"):

        logger.info(
            f"User message: {user_message}"
        )

        response = f"Received: {user_message}"

        save_conversation(
            user_message,
            response
        )

        st.success(response)

        logger.info(
            f"Assistant response: {response}"
        )

    st.subheader("Conversation History")

    history = get_conversations()

    for item in history:

        st.write(
            f"**{item[0]}**"
        )

        st.write(
            f"User: {item[1]}"
        )

        st.write(
            f"Assistant: {item[2]}"
        )

        st.divider()


# =========================
# Notes Page
# =========================

if page == "Notes":

    st.title("📝 Notes")

    note_title = st.text_input(
        "Title",
        key="note_title"
    )

    note_content = st.text_area(
        "Content",
        key="note_content"
    )

    if st.button("Save Note"):

        save_note(
            note_title,
            note_content
        )

        st.success(
            "Note saved successfully"
        )

    st.subheader("Saved Notes")

    notes = get_notes()

    for note in notes:

        st.write(
            f"### {note[1]}"
        )

        st.write(
            note[2]
        )

        st.caption(
            f"Created: {note[3]}"
        )

        st.divider()