DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def normalize_text(text):
    """Normalize spacing while preserving paragraph boundaries."""

    if not text:
        return ""

    normalized_lines = []

    for line in text.splitlines():
        clean_line = " ".join(line.split())

        if clean_line:
            normalized_lines.append(clean_line)

    return "\n".join(normalized_lines)


def split_text_into_chunks(
    text,
    chunk_size=DEFAULT_CHUNK_SIZE,
    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
):
    """Split document text into ordered overlapping chunks."""

    if chunk_size <= 0:
        raise ValueError(
            "Chunk size must be greater than zero."
        )

    if chunk_overlap < 0:
        raise ValueError(
            "Chunk overlap cannot be negative."
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be smaller than chunk size."
        )

    normalized_text = normalize_text(text)

    if not normalized_text:
        return []

    chunks = []
    start_position = 0
    sequence_number = 1
    text_length = len(normalized_text)

    while start_position < text_length:

        end_position = min(
            start_position + chunk_size,
            text_length,
        )

        chunk_text = normalized_text[
            start_position:end_position
        ]

        if end_position < text_length:
            preferred_break = max(
                chunk_text.rfind("\n"),
                chunk_text.rfind(". "),
                chunk_text.rfind(" "),
            )

            minimum_break_position = int(
                chunk_size * 0.60
            )

            if preferred_break >= minimum_break_position:
                end_position = (
                    start_position
                    + preferred_break
                    + 1
                )

                chunk_text = normalized_text[
                    start_position:end_position
                ]

        chunk_text = chunk_text.strip()

        if chunk_text:
            chunks.append(
                {
                    "sequence_number": sequence_number,
                    "content": chunk_text,
                    "character_count": len(chunk_text),
                    "word_count": len(
                        chunk_text.split()
                    ),
                }
            )

            sequence_number += 1

        if end_position >= text_length:
            break

        next_position = (
            end_position - chunk_overlap
        )

        if next_position <= start_position:
            next_position = end_position

        start_position = next_position

    return chunks