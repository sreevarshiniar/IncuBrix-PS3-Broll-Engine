"""Semantic scene segmentation and ranking. Falls back to lexical scoring if model is unavailable."""
import re
from functools import lru_cache

_SENTENCE = re.compile(r'(?<=[.!?])\s+')

@lru_cache(maxsize=1)
def _model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    except Exception:
        return None

def split_scenes(text: str, visual_hints: list[str] | None = None) -> list[dict]:
    parts = [p.strip() for p in _SENTENCE.split(text.strip()) if p.strip()]
    if not parts and text.strip(): parts = [text.strip()]
    hints = visual_hints or []
    return [{"text": p, "visual_hint": hints[i] if i < len(hints) else None} for i, p in enumerate(parts)]

def _tokens(s: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[a-zA-Z0-9]+", s) if len(w) > 2}

def rank_candidates(scene_text: str, candidates: list[dict]) -> list[tuple[float, dict, str]]:
    if not candidates: return []
    model = _model()
    if model is not None:
        try:
            import numpy as np
            texts = [scene_text] + [c.get("description", "") for c in candidates]
            vectors = model.encode(texts, normalize_embeddings=True)
            scores = np.dot(vectors[1:], vectors[0]).tolist()
            return sorted([(float(s), c, "sentence-transformers/all-MiniLM-L6-v2 cosine similarity") for s, c in zip(scores, candidates)], key=lambda x: x[0], reverse=True)
        except Exception:
            pass
    wanted = _tokens(scene_text)
    ranked = []
    for c in candidates:
        words = _tokens(c.get("description", ""))
        score = len(wanted & words) / max(1, len(wanted | words))
        ranked.append((score, c, "token Jaccard fallback; semantic model unavailable"))
    return sorted(ranked, key=lambda x: x[0], reverse=True)
