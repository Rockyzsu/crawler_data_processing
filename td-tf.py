from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(sentences):
    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')  # Remove common English stop words
    
    # Transform sentences into TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(sentences)
    
    # Get feature names (words) for reference
    feature_names = vectorizer.get_feature_names_out()
    
    # Calculate cosine similarity between the first sentence and others
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    return similarities, feature_names,tfidf_matrix

# Example sentences
sentences = [
    "I love reading books",
    "I enjoy reading novels",
]

# Calculate similarities
similarities, features,tfidf_matrix = calculate_similarity(sentences)

# Display results
print(f"Base sentence: {sentences[0]}\n")
for i, similarity in enumerate(similarities, 1):
    print(f"Sentence {i}: {sentences[i]}")
    print(f"Similarity score: {similarity:.4f}\n")

# Show some important words (high TF-IDF in base sentence)
print("Key words from base sentence (with significant TF-IDF weights):")
base_vector = tfidf_matrix[0].toarray()[0]
top_indices = base_vector.argsort()[-5:][::-1]  # Top 5 words
for idx in top_indices:
    print(f"- {features[idx]}: {base_vector[idx]:.4f}")