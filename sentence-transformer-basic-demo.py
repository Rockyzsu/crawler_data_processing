from sentence_transformers import SentenceTransformer, util

MODEL_PATH = './local-models/all-MiniLM-L6-v2'  # Path to a lightweight model suitable for CPU

def calculate_similarity(text1, text2, model):
    """
    Calculate cosine similarity between two texts using a pre-trained model
    
    Parameters:
        text1 (str): First text to compare
        text2 (str): Second text to compare
        model: Pre-loaded SentenceTransformer model
        
    Returns:
        float: Cosine similarity score between 0 and 1
    """
    # Generate embeddings for both texts
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    
    # Calculate and return cosine similarity
    return util.cos_sim(embedding1, embedding2).item()


def main():
    # Define the three texts for comparison
    text_a = "Artificial intelligence is transforming modern society through automation and data analysis."
    text_b = "Machine learning algorithms are changing contemporary culture by automating processes and analyzing information."
    text_c = "Climate change affects global weather patterns and requires immediate environmental action."
    
    # Load a pre-trained SentenceTransformer model
    # Using a lightweight model suitable for general purpose similarity tasks
    model = SentenceTransformer(MODEL_PATH)
    
    # Calculate similarity scores
    similarity_ab = calculate_similarity(text_a, text_b, model)
    similarity_ac = calculate_similarity(text_a, text_c, model)
    
    # Display results with formatted output
    print(f"Text A: {text_a}\n")
    print(f"Text B: {text_b}")
    print(f"Similarity between A and B: {similarity_ab:.4f}")
    print("\n" + "-"*50 + "\n")
    print(f"Text C: {text_c}")
    print(f"Similarity between A and C: {similarity_ac:.4f}")
    
    # Provide a simple interpretation of the results
    print("\nInterpretation:")
    print(f"- A and B are {'highly similar' if similarity_ab > 0.7 else 'moderately similar' if similarity_ab > 0.4 else 'not very similar'}")
    print(f"- A and C are {'highly similar' if similarity_ac > 0.7 else 'moderately similar' if similarity_ac > 0.4 else 'not very similar'}")

if __name__ == "__main__":
    main()
