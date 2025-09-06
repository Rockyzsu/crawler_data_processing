from Levenshtein import distance  # Need to install python-Levenshtein

def text_similarity_simple(text1, text2):
    # Calculate edit distance
    edit_dist = distance(text1, text2)
    # Normalize similarity (ranges from 0 to 1, where 1 means identical)
    max_len = max(len(text1), len(text2))
    return 1 - edit_dist / max_len if max_len > 0 else 1.0

# Examples

text_a = "The quick brown fox jumps over the lazy dog"
text_b = "The quick brown fox jumps over the sleepy dog"

print(f"Similarity between A and B: {text_similarity_simple(text_a, text_b):.2f}")  # Approximately  0.91