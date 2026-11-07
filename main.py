from pathlib import Path

import streamlit as st

from src.memory.conversation import (
    save_conversation,
    get_conversations,
    clear_conversations,
)

from src.memory.projects import (
    save_project,
    get_projects,
)

from src.memory.knowledge import (
    save_document,
    get_documents,
    search_documents,
    get_document_statistics,
    delete_document,
    index_document_chunks,
    get_document_chunk_count,
    get_document_chunks,
    delete_document_chunks,
    get_index_statistics,
    search_knowledge_chunks,
)

from src.memory.notes import (
    save_note,
    get_notes,
)

from src.services.document_reader import (
    create_document_preview,
    extract_document_text,
)

from src.services.text_chunker import (
    split_text_into_chunks,
)

from src.services.logger import logger


# =========================
# Streamlit Configuration
# =========================

st.set_page_config(
    page_title="Ali IT Copilot",
    page_icon="🤖",
    layout="wide",
)


# =========================
# Glassy Navy Theme
# =========================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #07111F 0%,
            #0A192F 50%,
            #10253F 100%
        );
        color: #E6EDF7;
    }

    [data-testid="stSidebar"] {
        background: rgba(10, 25, 47, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    h1,
    h2,
    h3,
    h4 {
        color: #F8FAFC !important;
    }

    p,
    label,
    .stCaption {
        color: #D6E2F0;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(17, 34, 64, 0.7) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    [data-testid="stFileUploader"] {
        background: rgba(17, 34, 64, 0.45);
        padding: 16px;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }

    .stButton button {
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        color: #EAF2FF;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        transition: all 0.3s ease;
        box-shadow:
            0 4px 12px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }

    .stButton button:hover {
        background: rgba(30, 58, 95, 0.55);
        border: 1px solid rgba(96, 165, 250, 0.35);
        transform: translateY(-2px);
        box-shadow:
            0 8px 20px rgba(59, 130, 246, 0.15);
    }

    [data-testid="stMetric"] {
        background: rgba(17, 34, 64, 0.65);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-radius: 16px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stMetricLabel"] {
        color: #BBD1EA;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF;
    }

    [data-testid="stChatMessage"] {
        background: rgba(17, 34, 64, 0.45);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 16px;
        padding: 12px;
    }

    [data-testid="stExpander"] {
        background: rgba(17, 34, 64, 0.35);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 14px;
    }

    .stAlert {
        border-radius: 14px;
    }

    div[role="radiogroup"] {
        background: rgba(17, 34, 64, 0.4);
        padding: 10px;
        border-radius: 12px;
    }

    hr {
        border-color: rgba(255, 255, 255, 0.08);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# Sidebar Navigation
# =========================

with st.sidebar:
    st.header("🤖 Ali IT Copilot")

    page = st.radio(
        "Workspace",
        [
            "💬 Conversations",
            "📝 Notes",
            "📁 Projects",
            "📚 Knowledge",
        ],
    )

    st.divider()

    st.success("✅ Database Connected")
    st.success("✅ Logging Active")
    st.info("⏳ AI Not Connected")


# =========================
# Conversations Page
# =========================

if page == "💬 Conversations":

    st.title("🤖 Ali IT Copilot")

    st.caption(
        "Personal AI Workspace • Conversations • Notes • "
        "Projects • Knowledge Assistance"
    )

    history = get_conversations()
    notes = get_notes()
    projects = get_projects()

    conversation_col, note_col, project_col = st.columns(3)

    with conversation_col:
        st.metric(
            "💬 Conversations",
            len(history),
        )

    with note_col:
        st.metric(
            "📝 Notes",
            len(notes),
        )

    with project_col:
        st.metric(
            "📁 Projects",
            len(projects),
        )

    if st.button(
        "🗑 Clear History",
        key="clear_conversation_history",
    ):
        clear_conversations()

        logger.info(
            "Conversation history cleared"
        )

        st.rerun()

    st.subheader("Conversation History")

    if not history:
        st.info(
            "No conversations have been saved yet."
        )

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
            response,
        )

        logger.info(
            f"Assistant response: {response}"
        )

        st.rerun()


# =========================
# Notes Page
# =========================

elif page == "📝 Notes":

    st.title("📝 Notes")

    st.caption(
        "Create and maintain personal notes in your workspace."
    )

    note_title = st.text_input(
        "Title",
        key="note_title",
    )

    note_content = st.text_area(
        "Content",
        key="note_content",
    )

    if st.button(
        "Save Note",
        key="save_note_button",
    ):

        if not note_title.strip():
            st.warning(
                "Please enter a note title."
            )

        elif not note_content.strip():
            st.warning(
                "Please enter note content."
            )

        else:
            save_note(
                note_title.strip(),
                note_content.strip(),
            )

            logger.info(
                f"Note saved: {note_title.strip()}"
            )

            st.success(
                "Note saved successfully."
            )

            st.rerun()

    st.divider()

    st.subheader("Saved Notes")

    notes = get_notes()

    if not notes:
        st.info(
            "No notes have been saved yet."
        )

    for note in notes:

        st.markdown(
            f"### {note[1]}"
        )

        st.write(
            note[2]
        )

        if len(note) > 3:
            st.caption(
                f"Created: {note[3]}"
            )

        st.divider()


# =========================
# Projects Page
# =========================

elif page == "📁 Projects":

    st.title("📁 Projects")

    st.caption(
        "Create projects and track their current status."
    )

    project_name = st.text_input(
        "Project Name",
        key="project_name",
    )

    project_description = st.text_area(
        "Description",
        key="project_description",
    )

    project_status = st.selectbox(
        "Status",
        [
            "Planned",
            "In Progress",
            "Completed",
            "On Hold",
        ],
        key="project_status",
    )

    if st.button(
        "Save Project",
        key="save_project_button",
    ):

        if not project_name.strip():
            st.warning(
                "Please enter a project name."
            )

        elif not project_description.strip():
            st.warning(
                "Please enter a project description."
            )

        else:
            save_project(
                project_name.strip(),
                project_description.strip(),
                project_status,
            )

            logger.info(
                f"Project saved: {project_name.strip()}"
            )

            st.success(
                "Project saved successfully."
            )

            st.rerun()

    st.divider()

    st.subheader("Saved Projects")

    projects = get_projects()

    if not projects:
        st.info(
            "No projects have been saved yet."
        )

    for project in projects:

        st.markdown(
            f"### {project[1]}"
        )

        st.write(
            project[2]
        )

        st.write(
            f"**Status:** {project[3]}"
        )

        st.divider()


# =========================
# Knowledge Page
# =========================

elif page == "📚 Knowledge":

    st.title("📚 Knowledge Repository")

    st.caption(
        "Upload, preview, index, search, and manage documents "
        "used by Ali IT Copilot."
    )

    # =========================
    # Repository Statistics
    # =========================

    statistics = get_document_statistics()
    index_statistics = get_index_statistics()

    stat_col1, stat_col2, stat_col3, stat_col4 = (
        st.columns(4)
    )

    with stat_col1:
        st.metric(
            "📄 Total Documents",
            statistics["total_documents"],
        )

    with stat_col2:
        st.metric(
            "🗂 Unique Files",
            statistics["unique_file_names"],
        )

    with stat_col3:
        st.metric(
            "🧩 Indexed Chunks",
            index_statistics["total_chunks"],
        )

    with stat_col4:
        st.metric(
            "🔎 Indexed Documents",
            index_statistics["indexed_documents"],
        )

    st.caption(
        f"Indexed words: "
        f"{index_statistics['indexed_words']:,}"
    )

    st.divider()

    # =========================
    # Document Upload
    # =========================

    st.subheader("Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=[
            "pdf",
            "docx",
            "txt",
        ],
        key="knowledge_file_uploader",
    )

    if uploaded_file is not None:

        st.caption(
            f"Selected file: {uploaded_file.name}"
        )

        if st.button(
            "Upload to Knowledge Repository",
            key="upload_knowledge_document",
        ):

            try:
                knowledge_directory = Path(
                    "knowledge"
                )

                knowledge_directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                safe_file_name = Path(
                    uploaded_file.name
                ).name

                file_path = (
                    knowledge_directory
                    / safe_file_name
                )

                document_saved = save_document(
                    safe_file_name,
                    str(file_path),
                )

                if document_saved:

                    with file_path.open("wb") as file:
                        file.write(
                            uploaded_file.getbuffer()
                        )

                    logger.info(
                        f"Knowledge document uploaded: "
                        f"{safe_file_name}"
                    )

                    st.success(
                        "Document uploaded successfully."
                    )

                    st.rerun()

                else:
                    st.warning(
                        "This document is already registered "
                        "in the knowledge repository."
                    )

            except Exception as error:

                logger.exception(
                    "Knowledge document upload failed"
                )

                st.error(
                    f"Document upload failed: {error}"
                )

    st.divider()

    # =========================
    # Indexed Knowledge Search
    # =========================

    st.subheader(
        "🔎 Search Indexed Knowledge"
    )

    st.caption(
        "Search inside the content of all indexed "
        "knowledge documents."
    )

    knowledge_query = st.text_input(
        "Knowledge search query",
        placeholder=(
            "Example: Project Management Professional"
        ),
        key="indexed_knowledge_search",
    )

    search_limit = st.slider(
        "Maximum passages",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
        key="knowledge_search_limit",
    )

    if knowledge_query.strip():

        try:
            knowledge_results = (
                search_knowledge_chunks(
                    knowledge_query.strip(),
                    limit=search_limit,
                )
            )

            if not knowledge_results:
                st.info(
                    "No indexed passages matched this query. "
                    "Try a shorter keyword or index more documents."
                )

            else:
                st.success(
                    f"Found {len(knowledge_results)} "
                    f"matching passage(s)."
                )

                for result_number, result in enumerate(
                    knowledge_results,
                    start=1,
                ):

                    result_title = (
                        f"Result {result_number}: "
                        f"{result['file_name']} • "
                        f"Chunk {result['sequence_number']}"
                    )

                    with st.expander(
                        result_title,
                        expanded=result_number == 1,
                    ):

                        st.caption(
                            f"Source: {result['file_name']} • "
                            f"Chunk: "
                            f"{result['sequence_number']} • "
                            f"Words: {result['word_count']} • "
                            f"Characters: "
                            f"{result['character_count']}"
                        )

                        st.write(
                            result["content"]
                        )

                        st.caption(
                            f"Saved path: "
                            f"{result['file_path']}"
                        )

        except Exception as error:

            logger.exception(
                "Indexed knowledge search failed"
            )

            st.error(
                f"Knowledge search failed: {error}"
            )

    else:

        if index_statistics["total_chunks"] > 0:
            st.info(
                "Enter a keyword or phrase to search "
                "the indexed knowledge repository."
            )

        else:
            st.warning(
                "No indexed knowledge is available. "
                "Index at least one document first."
            )

    st.divider()

    # =========================
    # Saved Documents
    # =========================

    st.subheader("Saved Documents")

    search_term = st.text_input(
        "Search knowledge documents",
        placeholder="Search by file name or saved path...",
        key="knowledge_search",
    )

    if search_term.strip():
        documents = search_documents(
            search_term.strip()
        )
    else:
        documents = get_documents()

    if not documents:

        if search_term.strip():
            st.info(
                f'No documents found matching '
                f'"{search_term.strip()}".'
            )

        else:
            st.info(
                "No documents have been added "
                "to the repository yet."
            )

    else:
        st.caption(
            f"{len(documents)} document(s) displayed"
        )

        for document in documents:

            document_id = document[0]
            file_name = document[1]
            file_path = document[2]

            document_column, delete_column = (
                st.columns([5, 1])
            )

            with document_column:

                st.markdown(
                    f"### 📄 {file_name}"
                )

                st.caption(
                    file_path
                )

                physical_file = Path(
                    file_path
                )

                if physical_file.exists():

                    file_size_kb = (
                        physical_file.stat().st_size
                        / 1024
                    )

                    st.success(
                        "File available",
                        icon="✅",
                    )

                    st.caption(
                        f"Type: "
                        f"{physical_file.suffix.upper()} • "
                        f"Size: {file_size_kb:.1f} KB"
                    )

                    # =========================
                    # Document Preview
                    # =========================

                    preview_state_key = (
                        f"document_preview_"
                        f"{document_id}"
                    )

                    if st.button(
                        "Preview Content",
                        key=(
                            f"preview_button_"
                            f"{document_id}"
                        ),
                    ):

                        with st.spinner(
                            f"Reading {file_name}..."
                        ):
                            st.session_state[
                                preview_state_key
                            ] = create_document_preview(
                                file_path
                            )

                    if (
                        preview_state_key
                        in st.session_state
                    ):

                        preview_result = (
                            st.session_state[
                                preview_state_key
                            ]
                        )

                        if preview_result["success"]:

                            preview_col1, preview_col2 = (
                                st.columns(2)
                            )

                            with preview_col1:
                                st.metric(
                                    "Words",
                                    preview_result[
                                        "word_count"
                                    ],
                                )

                            with preview_col2:
                                st.metric(
                                    "Characters",
                                    preview_result[
                                        "character_count"
                                    ],
                                )

                            with st.expander(
                                "Document Content",
                                expanded=True,
                            ):
                                st.text_area(
                                    "Extracted text",
                                    value=preview_result[
                                        "preview"
                                    ],
                                    height=350,
                                    disabled=True,
                                    key=(
                                        f"preview_text_"
                                        f"{document_id}"
                                    ),
                                )

                                if preview_result[
                                    "preview_shortened"
                                ]:
                                    st.info(
                                        "The preview shows the first "
                                        "5,000 characters. The complete "
                                        "document text was extracted."
                                    )

                            if st.button(
                                "Close Preview",
                                key=(
                                    f"close_preview_"
                                    f"{document_id}"
                                ),
                            ):
                                del st.session_state[
                                    preview_state_key
                                ]

                                st.rerun()

                        else:
                            st.warning(
                                preview_result["error"],
                                icon="⚠️",
                            )

                    # =========================
                    # Knowledge Index
                    # =========================

                    st.markdown(
                        "#### Knowledge Index"
                    )

                    chunk_count = (
                        get_document_chunk_count(
                            document_id
                        )
                    )

                    if chunk_count > 0:

                        st.success(
                            f"Indexed with "
                            f"{chunk_count} "
                            f"knowledge chunk(s).",
                            icon="🧩",
                        )

                        index_button_label = (
                            "Re-index Document"
                        )

                    else:
                        st.info(
                            "This document has not been "
                            "indexed yet.",
                            icon="ℹ️",
                        )

                        index_button_label = (
                            "Index Document"
                        )

                    if st.button(
                        index_button_label,
                        key=(
                            f"index_document_"
                            f"{document_id}"
                        ),
                    ):

                        with st.spinner(
                            f"Extracting and indexing "
                            f"{file_name}..."
                        ):

                            extraction_result = (
                                extract_document_text(
                                    file_path
                                )
                            )

                            if not extraction_result[
                                "success"
                            ]:
                                st.error(
                                    "Indexing failed: "
                                    f"{extraction_result['error']}"
                                )

                            else:
                                chunks = (
                                    split_text_into_chunks(
                                        extraction_result[
                                            "text"
                                        ]
                                    )
                                )

                                if not chunks:
                                    st.error(
                                        "No usable knowledge "
                                        "chunks were produced."
                                    )

                                else:
                                    saved_chunk_count = (
                                        index_document_chunks(
                                            document_id,
                                            chunks,
                                        )
                                    )

                                    logger.info(
                                        f"Knowledge document "
                                        f"indexed: {file_name}; "
                                        f"chunks: "
                                        f"{saved_chunk_count}"
                                    )

                                    st.success(
                                        f"{file_name} was "
                                        f"indexed into "
                                        f"{saved_chunk_count} "
                                        f"chunk(s)."
                                    )

                                    st.rerun()

                    if chunk_count > 0:

                        with st.expander(
                            "View Indexed Chunks",
                            expanded=False,
                        ):

                            indexed_chunks = (
                                get_document_chunks(
                                    document_id
                                )
                            )

                            for indexed_chunk in (
                                indexed_chunks
                            ):

                                st.markdown(
                                    f"**Chunk "
                                    f"{indexed_chunk['sequence_number']}**"
                                )

                                st.caption(
                                    f"{indexed_chunk['word_count']} "
                                    f"words • "
                                    f"{indexed_chunk['character_count']} "
                                    f"characters"
                                )

                                st.text_area(
                                    "Chunk content",
                                    value=indexed_chunk[
                                        "content"
                                    ],
                                    height=160,
                                    disabled=True,
                                    key=(
                                        f"chunk_content_"
                                        f"{indexed_chunk['id']}"
                                    ),
                                    label_visibility=(
                                        "collapsed"
                                    ),
                                )

                                st.divider()

                        if st.button(
                            "Remove Index",
                            key=(
                                f"remove_index_"
                                f"{document_id}"
                            ),
                            type="secondary",
                        ):

                            removed_count = (
                                delete_document_chunks(
                                    document_id
                                )
                            )

                            logger.info(
                                f"Knowledge index removed: "
                                f"{file_name}; chunks: "
                                f"{removed_count}"
                            )

                            st.success(
                                f"Removed "
                                f"{removed_count} "
                                f"indexed chunk(s)."
                            )

                            st.rerun()

                else:
                    st.warning(
                        "The database record exists, but the "
                        "physical file could not be found.",
                        icon="⚠️",
                    )

            with delete_column:

                if st.button(
                    "Delete",
                    key=(
                        f"delete_document_"
                        f"{document_id}"
                    ),
                    type="secondary",
                ):

                    delete_document_chunks(
                        document_id
                    )

                    deleted_path = (
                        delete_document(
                            document_id
                        )
                    )

                    if deleted_path:

                        logger.info(
                            f"Knowledge record deleted: "
                            f"{file_name}"
                        )

                        st.success(
                            f"{file_name} was removed "
                            f"from the repository."
                        )

                        preview_state_key = (
                            f"document_preview_"
                            f"{document_id}"
                        )

                        if (
                            preview_state_key
                            in st.session_state
                        ):
                            del st.session_state[
                                preview_state_key
                            ]

                        st.rerun()

                    else:
                        st.error(
                            "The document record "
                            "could not be found."
                        )

            st.divider()