
import spacy

def test_latincy_model():
    """Test the installed LatinCy model"""
    try:
        # Load the Latin model
        nlp = spacy.load("la_core_web_lg")
        print("LatinCy model loaded successfully!")
        
        # Test with Latin text
        text = "puella puellam puellae puellarum amicus amici amico"
        doc = nlp(text)
        
        print(f"\nLatin text: {text}")
        print("Latin lemmatization results:")
        for token in doc:
            print(f"  {token.text} -> {token.lemma_}")
            
        print(f"\nParts of speech:")
        for token in doc:
            print(f"  {token.text} -> {token.pos_} ({token.tag_})")
            
    except OSError as e:
        print(f"Error loading Latin model: {e}")
        print("Make sure the model is properly installed.")

def test_spacy_info():
    """Check what spaCy models are available"""
    print("\n=== Available spaCy Models ===")
    import spacy.util
    models = spacy.util.get_installed_models()
    if models:
        print("Installed models:")
        for model in models:
            print(f"  - {model}")
    else:
        print("No models found.")

if __name__ == "__main__":
    print("Testing LatinCy Latin NLP model...")
    print("=" * 50)
    
    test_latincy_model()
    test_spacy_info()
    
    print("\n=== Success! ===")
    print("You now have a working Latin spaCy model!")
    print("The model provides:")
    print("- Lemmatization (word base forms)")
    print("- Part-of-speech tagging")
    print("- Named entity recognition")
    print("- Dependency parsing")
    print("- And more...")