from typing import List
import re

def _split_sentences(text: str) -> List[str]:
    """Split text into sentences by common punctuation marks, filtering empty strings."""
    parts = re.split(r"[.!?。！？]+", text)
    return [s.strip() for s in parts if s.strip()]


def extract_words_by_position(text: str, position) -> List[str]:
    """Extract words from each sentence at the specified numeric position.
    Supports both positive and negative indexing:
    - 0 represents the first word, 1 the second, etc.
    - -1 represents the last word, -2 the second to last
    If index is out of range, falls back to the last word of the sentence.
    """
    # Convert position to integer index (allows string digits)
    if isinstance(position, int):
        idx = position
    elif isinstance(position, str):
        try:
            idx = int(position)
        except ValueError:
            # For non-numeric strings, default to 0 (first word)
            idx = 0
    else:
        idx = 0

    sentences = _split_sentences(text)
    extracted_words: List[str] = []

    for sentence in sentences:
        # Use simple regex to extract words, avoiding external tokenization dependencies
        words = re.findall(r"\b\w+\b", sentence.lower())
        if not words:
            continue

        # Handle positive/negative indexing and out-of-range cases
        if idx >= 0:
            if idx < len(words):
                extracted_words.append(words[idx])
            else:
                extracted_words.append(words[-1])
        else:
            # Negative indexing (e.g., -1 for last word)
            if abs(idx) <= len(words):
                extracted_words.append(words[idx])
            else:
                extracted_words.append(words[-1])

    return extracted_words
