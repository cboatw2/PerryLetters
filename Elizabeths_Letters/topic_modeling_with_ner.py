import re
import os
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
import matplotlib.pyplot as plt
import pandas as pd
import spacy

# Load spaCy model for NER
# Install with: python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Please install spaCy model: python -m spacy download en_core_web_sm")
    raise

def remove_named_entities(text, entity_types=['PERSON', 'GPE', 'LOC', 'ORG']):
    """
    Remove named entities from text using spaCy NER.
    
    Args:
        text: Input text string
        entity_types: List of entity types to remove
            - PERSON: People names
            - GPE: Countries, cities, states (Geopolitical entities)
            - LOC: Non-GPE locations (mountains, bodies of water, etc.)
            - ORG: Organizations, companies, agencies, institutions
    
    Returns:
        Text with named entities removed
    """
    doc = nlp(text)
    
    # Collect all entity spans to remove
    entities_to_remove = [ent for ent in doc.ents if ent.label_ in entity_types]
    
    # Sort entities by start position in reverse to maintain indices
    entities_to_remove.sort(key=lambda x: x.start_char, reverse=True)
    
    # Remove entities from text
    cleaned_text = text
    for ent in entities_to_remove:
        cleaned_text = cleaned_text[:ent.start_char] + ' ' + cleaned_text[ent.end_char:]
    
    return cleaned_text

def extract_and_save_entities(documents, output_file='extracted_entities.csv'):
    """
    Extract all named entities from documents and save to CSV.
    Useful for reviewing what's being removed.
    """
    all_entities = []
    
    for i, doc in enumerate(documents):
        spacy_doc = nlp(doc)
        for ent in spacy_doc.ents:
            all_entities.append({
                'document_id': i,
                'entity_text': ent.text,
                'entity_type': ent.label_,
                'context': doc[max(0, ent.start_char-50):min(len(doc), ent.end_char+50)]
            })
    
    df = pd.DataFrame(all_entities)
    df.to_csv(output_file, index=False)
    print(f"\nExtracted {len(all_entities)} named entities")
    print(f"Entity breakdown:")
    print(df['entity_type'].value_counts())
    print(f"\nSaved to: {output_file}")
    
    return df

def load_elizabeth_letters_split(directory='efmperry_letters_split'):
    """Load letters from the split directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    letters_dir = os.path.join(script_dir, directory)
    
    if not os.path.exists(letters_dir):
        raise FileNotFoundError(f"Directory not found: {letters_dir}")
    
    letters = []
    
    # Get all .txt files in the directory
    txt_files = sorted([f for f in os.listdir(letters_dir) if f.endswith('.txt')])
    
    print(f"Found {len(txt_files)} letter files")
    
    for filename in txt_files:
        filepath = os.path.join(letters_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            if len(content) > 100:  # Only include substantial letters
                letters.append({
                    'filename': filename,
                    'content': content,
                    # Extract date from filename if present (adjust pattern as needed)
                    'date': re.search(r'\d{4}-\d{2}-\d{2}', filename).group() if re.search(r'\d{4}-\d{2}-\d{2}', filename) else 'Unknown'
                })
    
    return letters

def preprocess_text_with_ner(text, remove_entities=True):
    """Clean and preprocess text for topic modeling, optionally removing named entities."""
    
    # First remove named entities if requested
    if remove_entities:
        text = remove_named_entities(text, entity_types=['PERSON', 'GPE', 'LOC', 'ORG'])
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits but keep some punctuation for context
    text = re.sub(r'[^a-zA-Z\s\']', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def get_historical_stopwords():
    """Create custom stopword list for 19th century letters."""
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    
    # Add common letter-specific and 19th century terms
    custom_stops = set([
        # Letter formalities
        'dear', 'dearest', 'sir', 'madam', 'mrs', 'mr', 'miss',
        'yours', 'sincerely', 'affectionately', 'truly', 
        'respectfully', 'obediently', 'faithfully',
        
        # Common 19th c. epistolary phrases
        'thee', 'thy', 'thou', 'thine', 'shall', 'ye',
        
        # Very common verbs/aux that may not add meaning
        'received', 'wrote', 'write', 'letter', 'letters',
        
        # Time references that appear frequently
        'day', 'today', 'yesterday', 'tomorrow', 'week', 'month',
        
        # Common pronouns and possessives
        'said', 'says', 'think', 'thought', 'know', 'knew',
    ])
    
    return list(ENGLISH_STOP_WORDS.union(custom_stops))

def extract_topics_lda(documents, n_topics=5, n_top_words=10, remove_entities=True):
    """Extract topics using LDA with optional NER preprocessing."""
    
    # Preprocess documents with NER
    processed_docs = [preprocess_text_with_ner(doc, remove_entities=remove_entities) 
                      for doc in documents]
    
    # Adjust min_df based on corpus size
    min_doc_freq = max(2, len(documents) // 20)  # At least 2, or 5% of documents
    max_doc_freq = 0.70  # Appear in no more than 70% of documents
    
    # Create document-term matrix
    vectorizer = CountVectorizer(
        max_df=max_doc_freq,
        min_df=min_doc_freq,
        max_features=1000,  # Increased from 500
        stop_words=get_historical_stopwords(),
        ngram_range=(1, 2),
        token_pattern=r'\b[a-z]{3,}\b'
    )
    
    doc_term_matrix = vectorizer.fit_transform(processed_docs)
    
    print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")
    print(f"Document-term matrix shape: {doc_term_matrix.shape}")
    
    # Run LDA with adjusted hyperparameters
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=50,  # Increased iterations
        learning_method='batch',
        doc_topic_prior=0.5,  # Higher alpha for more mixed topics
        topic_word_prior=0.1,  # Higher beta for smoother word distributions
        n_jobs=-1  # Use all CPU cores
    )
    
    lda_output = lda_model.fit_transform(doc_term_matrix)
    
    # Get feature names
    feature_names = vectorizer.get_feature_names_out()
    
    # Extract top words for each topic
    topics = []
    for topic_idx, topic in enumerate(lda_model.components_):
        top_words_idx = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics.append({
            'topic_id': topic_idx,
            'top_words': top_words,
            'word_weights': topic[top_words_idx]
        })
    
    return topics, lda_output, lda_model, vectorizer

def extract_topics_nmf(documents, n_topics=5, n_top_words=10, remove_entities=True):
    """Extract topics using NMF with optional NER preprocessing."""
    
    # Preprocess documents with NER
    processed_docs = [preprocess_text_with_ner(doc, remove_entities=remove_entities) 
                      for doc in documents]
    
    # Adjust min_df based on corpus size
    min_doc_freq = max(2, len(documents) // 20)
    max_doc_freq = 0.70
    
    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer(
        max_df=max_doc_freq,
        min_df=min_doc_freq,
        max_features=1000,  # Increased from 500
        stop_words=get_historical_stopwords(),
        ngram_range=(1, 2),
        token_pattern=r'\b[a-z]{3,}\b',
        sublinear_tf=True,
        use_idf=True,
        smooth_idf=True
    )
    
    tfidf_matrix = vectorizer.fit_transform(processed_docs)
    
    print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    
    # Run NMF with adjusted parameters
    nmf_model = NMF(
        n_components=n_topics,
        random_state=42,
        max_iter=500,  # Increased iterations
        init='nndsvda',  # Better initialization for sparse data
        alpha_W=0.01,  # Reduced regularization
        alpha_H=0.01,
        l1_ratio=0.5,
        solver='mu',  # Multiplicative update solver
        beta_loss='frobenius'
    )
    
    nmf_output = nmf_model.fit_transform(tfidf_matrix)
    
    # Get feature names
    feature_names = vectorizer.get_feature_names_out()
    
    # Extract top words for each topic with normalized weights
    topics = []
    for topic_idx, topic in enumerate(nmf_model.components_):
        # Normalize the topic weights for better visualization
        normalized_topic = topic / topic.sum()
        top_words_idx = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics.append({
            'topic_id': topic_idx,
            'top_words': top_words,
            'word_weights': normalized_topic[top_words_idx] * 100  # Scale for visibility
        })
    
    return topics, nmf_output, nmf_model, vectorizer

def display_topics(topics, method_name="Topic Model"):
    """Display topics in a readable format."""
    print(f"\n{'='*60}")
    print(f"{method_name} Results")
    print(f"{'='*60}\n")
    
    for topic in topics:
        print(f"Topic {topic['topic_id']}:")
        print(f"  Top words: {', '.join(topic['top_words'])}")
        print()

def visualize_topics(topics, save_path='topics_visualization.png', method_name='LDA'):
    """Create a visualization of topics and their top words."""
    n_topics = len(topics)
    fig, axes = plt.subplots(n_topics, 1, figsize=(14, 3.5*n_topics))
    
    if n_topics == 1:
        axes = [axes]
    
    for idx, topic in enumerate(topics):
        words = topic['top_words']
        weights = topic['word_weights']
        
        # Create color gradient
        colors = plt.cm.YlOrRd(np.linspace(0.4, 0.8, len(words)))
        
        bars = axes[idx].barh(range(len(words)), weights, color=colors)
        axes[idx].set_yticks(range(len(words)))
        axes[idx].set_yticklabels(words, fontsize=10)
        axes[idx].set_xlabel('Weight', fontsize=11)
        axes[idx].set_title(f'Topic {idx} - {method_name}', fontsize=13, fontweight='bold', pad=10)
        axes[idx].invert_yaxis()
        
        # Add value labels on bars
        for i, (bar, weight) in enumerate(zip(bars, weights)):
            axes[idx].text(weight, i, f' {weight:.3f}', 
                          va='center', fontsize=9, color='black')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Visualization saved to: {save_path}")
    plt.close()

def analyze_topic_coherence(model, vectorizer, documents, n_top_words=10):
    """Calculate and display topic coherence metrics."""
    feature_names = vectorizer.get_feature_names_out()
    
    print("\nTopic Coherence Analysis:")
    print("=" * 60)
    
    for topic_idx, topic in enumerate(model.components_):
        top_words_idx = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        
        # Calculate topic concentration (higher = more focused topic)
        concentration = np.max(topic) / np.sum(topic)
        
        print(f"\nTopic {topic_idx}:")
        print(f"  Concentration: {concentration:.4f}")
        print(f"  Top words: {', '.join(top_words[:5])}")

def main():
    """Main function to run topic modeling with NER."""
    print("Loading Elizabeth F.M. Perry's letters from split directory...")
    letters = load_elizabeth_letters_split()
    
    print(f"Loaded {len(letters)} letters")
    
    # Extract letter contents
    documents = [letter.get('content', '') for letter in letters if letter.get('content')]
    
    print(f"\nProcessing {len(documents)} documents for topic modeling with NER...")
    
    # Extract and save named entities for review
    print("\nExtracting named entities...")
    entities_df = extract_and_save_entities(documents, 'extracted_entities.csv')
    
    # Determine number of topics based on corpus size
    if len(documents) < 10:
        n_topics = 3
    elif len(documents) < 30:
        n_topics = 5
    elif len(documents) < 50:
        n_topics = 7
    else:
        n_topics = 10
    
    n_top_words = 15
    
    print(f"\nRunning topic modeling with {n_topics} topics (NER-cleaned)...")
    
    # LDA with NER
    print("\n" + "="*60)
    print("Running LDA with Named Entity Removal...")
    print("="*60)
    lda_topics, lda_distribution, lda_model, lda_vectorizer = extract_topics_lda(
        documents, n_topics=n_topics, n_top_words=n_top_words, remove_entities=True
    )
    display_topics(lda_topics, "LDA (NER-cleaned)")
    analyze_topic_coherence(lda_model, lda_vectorizer, documents)
    
    # NMF with NER
    print("\n" + "="*60)
    print("Running NMF with Named Entity Removal...")
    print("="*60)
    nmf_topics, nmf_distribution, nmf_model, nmf_vectorizer = extract_topics_nmf(
        documents, n_topics=n_topics, n_top_words=n_top_words, remove_entities=True
    )
    display_topics(nmf_topics, "NMF (NER-cleaned)")
    analyze_topic_coherence(nmf_model, nmf_vectorizer, documents)
    
    # Visualize topics with improved function
    output_dir = os.path.dirname(os.path.abspath(__file__))
    lda_viz_path = os.path.join(output_dir, 'lda_topics_ner_cleaned.png')
    nmf_viz_path = os.path.join(output_dir, 'nmf_topics_ner_cleaned.png')
    visualize_topics(lda_topics, lda_viz_path, 'LDA')
    visualize_topics(nmf_topics, nmf_viz_path, 'NMF')
    
    print("\n" + "="*60)
    print("Comparison: Before and After NER")
    print("="*60)
    print("\nRun without NER for comparison...")
    
    # Run without NER for comparison
    lda_topics_no_ner, _, lda_model_no_ner, lda_vectorizer_no_ner = extract_topics_lda(
        documents, n_topics=n_topics, n_top_words=n_top_words, remove_entities=False
    )
    display_topics(lda_topics_no_ner, "LDA (without NER)")
    
    # Visualize comparison
    lda_no_ner_viz_path = os.path.join(output_dir, 'lda_topics_no_ner.png')
    visualize_topics(lda_topics_no_ner, lda_no_ner_viz_path, 'LDA (No NER)')

if __name__ == "__main__":
    main()