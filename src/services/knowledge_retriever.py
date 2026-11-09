import re

from src.memory.knowledge import (
    search_knowledge_chunks,
)


DEFAULT_RESULT_LIMIT = 5
DEFAULT_CONTEXT_CHARACTER_LIMIT = 12000


ENGLISH_STOP_WORDS = {
    "about",
    "after",
    "again",
    "also",
    "been",
    "before",
    "could",
    "does",
    "from",
    "have",
    "into",
    "more",
    "repository",
    "should",
    "tell",
    "that",
    "their",
    "there",
    "these",
    "they",
    "this",
    "using",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
    "your",
}


ARABIC_STOP_WORDS = {
    "ما",
    "ماذا",
    "من",
    "في",
    "على",
    "إلى",
    "عن",
    "هذا",
    "هذه",
    "ذلك",
    "تلك",
    "التي",
    "الذي",
    "الذين",
    "هل",
    "كيف",
    "متى",
    "أين",
    "لماذا",
    "لدي",
    "عندي",
    "موجود",
    "موجودة",
    "المستند",
    "المستندات",
    "المعرفة",
}


def normalize_query_text(text):
    """Normalize English and Arabic query text for matching."""

    if not text:
        return ""

    normalized_text = text.casefold()

    normalized_text = re.sub(
        r"_+",
        " ",
        normalized_text,
    )

    normalized_text = re.sub(
        r"[^\w]+",
        " ",
        normalized_text,
        flags=re.UNICODE,
    )

    return " ".join(
        normalized_text.split()
    )


def extract_query_terms(query):
    """Extract useful unique English and Arabic query terms."""

    normalized_query = normalize_query_text(
        query
    )

    if not normalized_query:
        return []

    terms = []

    for term in normalized_query.split():

        if len(term) < 3:
            continue

        if term in ENGLISH_STOP_WORDS:
            continue

        if term in ARABIC_STOP_WORDS:
            continue

        if term not in terms:
            terms.append(term)

    return terms


def calculate_relevance_score(
    query,
    query_terms,
    result,
):
    """Calculate deterministic relevance details for one chunk."""

    normalized_query = normalize_query_text(
        query
    )

    normalized_content = normalize_query_text(
        result.get("content", "")
    )

    normalized_file_name = normalize_query_text(
        result.get("file_name", "")
    )

    score = 0
    matched_terms = []

    exact_query_match = bool(
        normalized_query
        and normalized_query in normalized_content
    )

    file_name_query_match = bool(
        normalized_query
        and normalized_query in normalized_file_name
    )

    if exact_query_match:
        score += 100

    if file_name_query_match:
        score += 80

    for term in query_terms:

        content_occurrences = (
            normalized_content.count(term)
        )

        file_name_occurrences = (
            normalized_file_name.count(term)
        )

        if content_occurrences > 0:
            score += min(
                content_occurrences,
                5,
            ) * 10

        if file_name_occurrences > 0:
            score += 20

        if (
            content_occurrences > 0
            or file_name_occurrences > 0
        ):
            matched_terms.append(term)

    if (
        query_terms
        and len(matched_terms) == len(query_terms)
    ):
        score += 30

    file_name_match = any(
        term in normalized_file_name
        for term in query_terms
    )

    return {
        "score": score,
        "matched_terms": matched_terms,
        "exact_query_match": exact_query_match,
        "file_name_query_match": file_name_query_match,
        "file_name_match": file_name_match,
    }


def collect_candidate_chunks(
    query,
    query_terms,
    candidate_limit=50,
):
    """Collect candidate chunks without duplicates."""

    candidates = {}
    search_queries = []

    clean_query = query.strip()

    if clean_query:
        search_queries.append(clean_query)

    for term in query_terms:

        if term not in search_queries:
            search_queries.append(term)

    for search_query in search_queries:

        results = search_knowledge_chunks(
            search_query,
            limit=candidate_limit,
        )

        for result in results:

            chunk_id = result["chunk_id"]

            if chunk_id not in candidates:
                candidates[chunk_id] = result

    return list(
        candidates.values()
    )


def rank_knowledge_results(
    query,
    maximum_results=DEFAULT_RESULT_LIMIT,
    minimum_score=10,
    context_character_limit=(
        DEFAULT_CONTEXT_CHARACTER_LIMIT
    ),
):
    """
    Retrieve, rank, deduplicate, and limit knowledge chunks.

    Results include relevance score, matched terms,
    and retrieval rank.
    """

    clean_query = query.strip()

    if not clean_query:
        return []

    safe_result_limit = max(
        1,
        min(
            int(maximum_results),
            20,
        ),
    )

    safe_context_limit = max(
        1000,
        min(
            int(context_character_limit),
            50000,
        ),
    )

    query_terms = extract_query_terms(
        clean_query
    )

    if not query_terms:
        return []

    candidates = collect_candidate_chunks(
        query=clean_query,
        query_terms=query_terms,
    )

    scored_results = []

    for result in candidates:

        score_details = calculate_relevance_score(
            query=clean_query,
            query_terms=query_terms,
            result=result,
        )

        matched_term_count = len(
            score_details["matched_terms"]
        )

        query_term_count = len(query_terms)

        query_term_coverage = (
            matched_term_count / query_term_count
            if query_term_count
            else 0.0
        )

        minimum_required_terms = (
            1
            if query_term_count <= 2
            else max(
                2,
                (query_term_count + 1) // 2,
            )
        )

        weak_match = (
            (
                matched_term_count
                < minimum_required_terms
                or query_term_coverage < 0.5
            )
            and not score_details[
                "exact_query_match"
            ]
            and not score_details[
                "file_name_match"
            ]
        )

        if weak_match:
            continue

        if (
            score_details["score"]
            < minimum_score
        ):
            continue

        ranked_result = dict(
            result
        )

        ranked_result["relevance_score"] = (
            score_details["score"]
        )

        ranked_result["matched_terms"] = (
            score_details["matched_terms"]
        )

        ranked_result["exact_query_match"] = (
            score_details["exact_query_match"]
        )

        ranked_result["file_name_match"] = (
            score_details["file_name_match"]
        )

        ranked_result["query_term_coverage"] = (
            query_term_coverage
        )

        scored_results.append(
            ranked_result
        )

    scored_results.sort(
        key=lambda item: (
            -item["relevance_score"],
            item["file_name"].casefold(),
            item["sequence_number"],
        )
    )

    selected_results = []
    selected_characters = 0
    selected_document_counts = {}

    for result in scored_results:
        document_id = result["document_id"]

        if (
            selected_document_counts.get(
                document_id,
                0,
            )
            >= 3
        ):
            continue

        result_characters = len(
            result["content"]
        )

        would_exceed_limit = (
            bool(selected_results)
            and (
                selected_characters
                + result_characters
                > safe_context_limit
            )
        )

        if would_exceed_limit:
            continue

        selected_results.append(
            result
        )

        selected_characters += (
            result_characters
        )

        selected_document_counts[document_id] = (
            selected_document_counts.get(
                document_id,
                0,
            )
            + 1
        )

        if (
            len(selected_results)
            >= safe_result_limit
        ):
            break

    for rank, result in enumerate(
        selected_results,
        start=1,
    ):
        result["retrieval_rank"] = rank

    return selected_results


def get_retrieval_diagnostics(
    query,
    results,
):
    """Return diagnostics for logging and interface testing."""

    query_terms = extract_query_terms(
        query
    )

    return {
        "query": query.strip(),
        "query_terms": query_terms,
        "result_count": len(results),
        "total_characters": sum(
            len(result["content"])
            for result in results
        ),
        "sources": [
            {
                "file_name": result[
                    "file_name"
                ],
                "sequence_number": result[
                    "sequence_number"
                ],
                "relevance_score": result[
                    "relevance_score"
                ],
                "matched_terms": result[
                    "matched_terms"
                ],
                "query_term_coverage": result[
                    "query_term_coverage"
                ],
                "retrieval_rank": result[
                    "retrieval_rank"
                ],
            }
            for result in results
        ],
    }