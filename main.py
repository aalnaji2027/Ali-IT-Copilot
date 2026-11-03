import streamlit as st

from src.memory.conversation import (
    save_conversation,
    get_conversations,
    clear_conversations
)

from src.memory.projects import (
    save_project,
    get_projects
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
st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(
        135deg,
        #07111F 0%,
        #0A192F 50%,
        #10253F 100%
    );
    color: #E6EDF7;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(10, 25, 47, 0.85);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Headers */
h1, h2, h3 {
    color: #F8FAFC !important;
}

/* Input Fields */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background-color: rgba(17,34,64,0.7) !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* Buttons */

.stButton button {

    background: rgba(15, 23, 42, 0.45);

    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);

    color: #EAF2FF;

    border: 1px solid rgba(148, 163, 184, 0.18);

    border-radius: 14px;

    transition: all 0.3s ease;

    box-shadow:
        0 4px 12px rgba(0,0,0,0.15),
        inset 0 1px 0 rgba(255,255,255,0.05);
}

.stButton button:hover {

    background: rgba(30, 58, 95, 0.55);

    border: 1px solid rgba(96, 165, 250, 0.35);

    transform: translateY(-2px);

    box-shadow:
        0 8px 20px rgba(59,130,246,0.15);
}

/* Metric Cards */
[data-testid="metric-container"] {
    background: rgba(17,34,64,0.65);
    backdrop-filter: blur(18px);
    border-radius: 16px;
    padding: 15px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Success Messages */
.stAlert {
    border-radius: 14px;
}

/* Radio Buttons Area */
div[role="radiogroup"] {
    background: rgba(17,34,64,0.4);
    padding: 10px;
    border-radius: 12px;
}

/* Horizontal Line */
hr {
    border-color: rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🤖 Ali IT Copilot")

    page = st.radio(
    "Workspace",
    [
        "💬 Conversations",
        "📝 Notes",
        "📁 Projects"
    ]
)

    st.write("---")

    st.success("✅ Database Connected")
    st.success("✅ Logging Active")
    st.info("⏳ AI Not Connected")


# =========================
# Conversations Page
# =========================

if page == "💬 Conversations":
    

    st.title("🤖 Ali IT Copilot")
    st.caption(
    "Personal AI Workspace • Conversations • Notes • Projects • Future AI Assistance"
)

history = get_conversations()
notes = get_notes()
projects = get_projects()

col1, col2, col3 = st.columns(3)



with col2:
    st.metric(
        "📝 Notes",
        len(notes)
    )

with col3:
    st.metric(
        "📁 Projects",
        len(projects)
    )


    with col1:
        st.metric(
            "Total Conversations",
            len(history)
        )

    

    if st.button("🗑 Clear History"):
        clear_conversations()
        st.rerun()

    



    st.subheader("Conversation History")

history = get_conversations()

for item in history:

    with st.chat_message("user"):
        st.write(item[1])

    with st.chat_message("assistant"):
        st.write(item[2])


user_message = st.chat_input(
    "Message Ali IT Copilot..."
)

if user_message:

    logger.info(
        f"User message: {user_message}"
    )

    response = f"Received: {user_message}"

    save_conversation(
        user_message,
        response
    )

    logger.info(
        f"Assistant response: {response}"
    )

    st.rerun()


# =========================
# Notes Page
# =========================

if page == "📝 Notes":

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
# =========================
# Projects Page
# =========================

if page == "📁 Projects":

    st.title("📁 Projects")

    project_name = st.text_input(
        "Project Name",
        key="project_name"
    )

    project_description = st.text_area(
        "Description",
        key="project_description"
    )

    project_status = st.selectbox(
        "Status",
        [
            "Planned",
            "In Progress",
            "Completed",
            "On Hold"
        ]
    )

    if st.button("Save Project"):

        save_project(
            project_name,
            project_description,
            project_status
        )

        st.success(
            "Project saved successfully"
        )

    st.subheader("Saved Projects")

    projects = get_projects()

    for project in projects:

        st.write(
            f"### {project[1]}"
        )

        st.write(
            project[2]
        )

        st.write(
            f"**Status:** {project[3]}"
        )

        st.divider()