
"""Semantic scene segmentation and candidate ranking."""
import re
from functools import lru_cache

_SENTENCE = re.compile(r"(?<=[.!?])\s+")


@lru_cache(maxsize=1)
def _model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    except Exception:
        return None


def split_scenes(text: str, visual_hints: list[str] | None = None) -> list[dict]:
    parts = [p.strip() for p in _SENTENCE.split(text.strip()) if p.strip()]
    if not parts and text.strip():
        parts = [text.strip()]
    hints = visual_hints or []
    return [
        {"text": part, "visual_hint": hints[i] if i < len(hints) else None}
        for i, part in enumerate(parts)
    ]


def _tokens(text: str) -> set[str]:
    return {
        word.lower()
        for word in re.findall(r"[a-zA-Z0-9]+", text)
        if len(word) > 2
    }


def rank_candidates(
    scene_text: str, candidates: list[dict]
) -> list[tuple[float, dict, str]]:
    """Rank candidates against narration using semantic similarity.

    Returns raw ranking scores. These scores are not human relevance ratings.
    """
    if not candidates:
        return []

    model = _model()
    if model is not None:
        try:
            import numpy as np

            descriptions = [
                " ".join(
                    str(candidate.get(field) or "")
                    for field in ("description", "tags", "title")
                ).strip()
                for candidate in candidates
            ]
            vectors = model.encode(
                [scene_text, *descriptions],
                normalize_embeddings=True,
            )
            scores = np.dot(vectors[1:], vectors[0]).tolist()
            return sorted(
                [
                    (
                        float(score),
                        candidate,
                        "SentenceTransformer cosine similarity",
                    )
                    for score, candidate in zip(scores, candidates)
                ],
                key=lambda item: item[0],
                reverse=True,
            )
        except Exception:
            pass

    wanted = _tokens(scene_text)
    ranked = []
    for candidate in candidates:
        description = " ".join(
            str(candidate.get(field) or "")
            for field in ("description", "tags", "title")
        )
        words = _tokens(description)
        score = len(wanted & words) / max(1, len(wanted | words))
        ranked.append(
            (score, candidate, "Token Jaccard similarity fallback")
        )

    return sorted(ranked, key=lambda item: item[0], reverse=True)
