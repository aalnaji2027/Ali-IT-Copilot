from ollama import Client


DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_HOST = "http://localhost:11434"

SYSTEM_PROMPT = """
You are Ali IT Copilot, a private local AI assistant.

Use the supplied knowledge context when it is relevant.

Rules:
1. Base document-related answers on the supplied context.
2. Do not invent facts that are absent from the context.
3. If the context is insufficient, clearly say so.
4. Mention the source document names used in the answer.
5. Keep answers clear, practical, and concise.
6. Reply in the same language used by the user.
""".strip()


def get_client():
    """Create a client connected to local Ollama."""

    return Client(
        host=DEFAULT_HOST
    )


def check_local_ai():
    """Check the Ollama connection and model availability."""

    try:
        client = get_client()
        response = client.list()

        model_names = []

        for model in response.models:
            model_name = (
                getattr(model, "model", None)
                or getattr(model, "name", None)
                or ""
            )

            if model_name:
                model_names.append(model_name)

        model_available = any(
            model_name == DEFAULT_MODEL
            for model_name in model_names
        )

        return {
            "connected": True,
            "model_available": model_available,
            "model": DEFAULT_MODEL,
            "models": model_names,
            "error": "",
        }

    except Exception as error:
        return {
            "connected": False,
            "model_available": False,
            "model": DEFAULT_MODEL,
            "models": [],
            "error": str(error),
        }


def build_knowledge_context(
    knowledge_results,
):
    """Convert retrieved chunks into grounded model context."""

    if not knowledge_results:
        return (
            "No matching indexed knowledge passages "
            "were retrieved."
        )

    context_sections = []

    for result_number, result in enumerate(
        knowledge_results,
        start=1,
    ):
        context_sections.append(
            "\n".join(
                [
                    f"[Source {result_number}]",
                    f"Document: {result['file_name']}",
                    (
                        "Chunk: "
                        f"{result['sequence_number']}"
                    ),
                    "Content:",
                    result["content"],
                ]
            )
        )

    return "\n\n".join(
        context_sections
    )


def generate_local_response(
    user_message,
    knowledge_results=None,
    conversation_history=None,
):
    """Generate a local, knowledge-grounded answer."""

    knowledge_results = (
        knowledge_results or []
    )

    conversation_history = (
        conversation_history or []
    )

    knowledge_context = build_knowledge_context(
        knowledge_results
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    for history_item in conversation_history[-6:]:

        messages.append(
            {
                "role": "user",
                "content": history_item["user"],
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": history_item["assistant"],
            }
        )

    grounded_prompt = f"""
Knowledge context:

{knowledge_context}

User question:

{user_message}

Answer using the knowledge context when relevant.
If the supplied context is insufficient, clearly say so.
""".strip()

    messages.append(
        {
            "role": "user",
            "content": grounded_prompt,
        }
    )

    try:
        client = get_client()

        response = client.chat(
            model=DEFAULT_MODEL,
            messages=messages,
            options={
                "temperature": 0.2,
                "num_ctx": 8192,
            },
        )

        response_text = (
            response.message.content.strip()
        )

        if not response_text:
            raise ValueError(
                "The local model returned an empty response."
            )

        sources = []

        seen_sources = set()

        for result in knowledge_results:
            source_key = (
                result["file_name"],
                result["sequence_number"],
            )

            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)

            sources.append(
                {
                    "file_name": result["file_name"],
                    "sequence_number": result[
                        "sequence_number"
                    ],
                }
            )

        return {
            "success": True,
            "response": response_text,
            "model": DEFAULT_MODEL,
            "sources": sources,
            "error": "",
        }

    except Exception as error:
        return {
            "success": False,
            "response": "",
            "model": DEFAULT_MODEL,
            "sources": [],
            "error": str(error),
        }