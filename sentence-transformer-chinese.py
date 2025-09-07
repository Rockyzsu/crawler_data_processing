from sentence_transformers import SentenceTransformer, util

MODEL_PATH = './local-models/uer/sbert-base-chinese-nli'  # Path to a lightweight model suitable for CPU

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
    text_a = "过量摄入高糖食物会导致血糖快速升高，长期可能增加 2 型糖尿病的发病风险。"
    # text_b = "昨天我去饭馆吃饭，很开心"
    text_b = "如果经常吃很多含糖量高的东西，血糖会迅速上升，时间久了可能更容易得 2 型糖尿病。"
    text_c = "每天坚持 30 分钟有氧运动，能增强心肺功能，改善身体代谢，降低心血管疾病风险。"
    
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
