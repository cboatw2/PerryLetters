import re
import os
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
import matplotlib.pyplot as plt
import pandas as pd

def load_ner_entities(csv_path='EFMPerry_NER_entities.csv'):
    """Load named entities from the NER CSV file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, csv_path)
    
    if not os.path.exists(full_path):
        print(f"Warning: NER entities file not found: {full_path}")
        return set()
    
    df = pd.read_csv(full_path)
    
    # Extract unique entity names and convert to lowercase for matching
    entities = set(df['entity_name'].str.lower().unique())
    
    print(f"Loaded {len(entities)} unique named entities from NER")
    print(f"  Persons: {len(df[df['entity_type'] == 'PERSON']['entity_name'].unique())}")
    print(f"  Locations: {len(df[df['entity_type'] == 'LOCATION']['entity_name'].unique())}")
    
    return entities

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
                # Extract letter number from filename
                letter_number_match = re.search(r'(\d+)', filename)
                letter_number = letter_number_match.group(1) if letter_number_match else 'Unknown'
                
                letters.append({
                    'filename': filename,
                    'letter_number': letter_number,
                    'content': content
                })
    
    return letters

def remove_ner_entities(text, ner_entities):
    """Remove named entities from text based on NER results."""
    if not ner_entities:
        return text
    
    # Create a copy of the text
    cleaned_text = text.lower()
    
    # Remove each entity (case-insensitive)
    for entity in ner_entities:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(entity) + r'\b'
        cleaned_text = re.sub(pattern, ' ', cleaned_text, flags=re.IGNORECASE)
    
    return cleaned_text

def preprocess_text_with_ner(text, ner_entities=None):
    """Clean and preprocess text for topic modeling, removing NER entities."""
    
    # First remove named entities if provided
    if ner_entities:
        text = remove_ner_entities(text, ner_entities)
    
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

def extract_topics_lda(documents, n_topics=5, n_top_words=10, ner_entities=None):
    """Extract topics using LDA with optional NER filtering."""
    
    # Preprocess documents with NER filtering
    processed_docs = [preprocess_text_with_ner(doc, ner_entities) for doc in documents]
    
    # Adjust min_df based on corpus size - be more lenient
    min_doc_freq = max(1, len(documents) // 30)  # Changed from 20 to 30
    max_doc_freq = 0.80  # Increased from 0.70
    
    # Create document-term matrix
    vectorizer = CountVectorizer(
        max_df=max_doc_freq,
        min_df=min_doc_freq,
        max_features=2000,  # Increased from 1000
        stop_words=get_historical_stopwords(),
        ngram_range=(1, 2),
        token_pattern=r'\b[a-z]{3,}\b'
    )
    
    doc_term_matrix = vectorizer.fit_transform(processed_docs)
    
    print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")
    print(f"Document-term matrix shape: {doc_term_matrix.shape}")
    
    # Run LDA with adjusted parameters
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=100,  # Increased from 50
        learning_method='batch',
        doc_topic_prior=0.1,  # Lower alpha for more focused topics
        topic_word_prior=0.01,  # Lower beta for more distinct topics
        n_jobs=-1,
        learning_offset=50.0,  # Add learning offset
        evaluate_every=10  # Evaluate perplexity
    )
    
    lda_output = lda_model.fit_transform(doc_term_matrix)
    
    print(f"LDA perplexity: {lda_model.perplexity(doc_term_matrix):.2f}")
    
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

def extract_topics_nmf(documents, n_topics=5, n_top_words=10, ner_entities=None):
    """Extract topics using NMF with optional NER filtering."""
    
    # Preprocess documents with NER filtering
    processed_docs = [preprocess_text_with_ner(doc, ner_entities) for doc in documents]
    
    # Adjust min_df based on corpus size - be more lenient
    min_doc_freq = max(1, len(documents) // 30)  # Changed from 20 to 30
    max_doc_freq = 0.80  # Increased from 0.70
    
    # Create TF-IDF matrix with adjusted parameters
    vectorizer = TfidfVectorizer(
        max_df=max_doc_freq,
        min_df=min_doc_freq,
        max_features=2000,  # Increased from 1000
        stop_words=get_historical_stopwords(),
        ngram_range=(1, 2),
        token_pattern=r'\b[a-z]{3,}\b',
        sublinear_tf=True,
        use_idf=True,
        smooth_idf=True,
        norm='l2'  # Add L2 normalization
    )
    
    tfidf_matrix = vectorizer.fit_transform(processed_docs)
    
    print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    print(f"Matrix sparsity: {(1.0 - tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])):.4f}")
    
    # Run NMF with better parameters
    nmf_model = NMF(
        n_components=n_topics,
        random_state=42,
        max_iter=1000,  # Increased from 500
        init='nndsvda',
        alpha_W=0.001,  # Reduced regularization from 0.01
        alpha_H=0.001,  # Reduced regularization from 0.01
        l1_ratio=0.5,
        solver='mu',
        beta_loss='frobenius',
        tol=1e-4  # Add tolerance for convergence
    )
    
    nmf_output = nmf_model.fit_transform(tfidf_matrix)
    
    # Check if model converged
    print(f"NMF converged in {nmf_model.n_iter_} iterations")
    print(f"Reconstruction error: {nmf_model.reconstruction_err_:.4f}")
    
    # Get feature names
    feature_names = vectorizer.get_feature_names_out()
    
    # Extract top words for each topic with proper normalization
    topics = []
    for topic_idx, topic in enumerate(nmf_model.components_):
        # Sort to get top words
        top_words_idx = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        
        # Get the actual weights (not normalized)
        top_weights = topic[top_words_idx]
        
        topics.append({
            'topic_id': topic_idx,
            'top_words': top_words,
            'word_weights': top_weights  # Use actual weights, not normalized
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
    
    # Increase figure size for better readability
    fig, axes = plt.subplots(n_topics, 1, figsize=(16, 4*n_topics))
    
    if n_topics == 1:
        axes = [axes]
    
    for idx, topic in enumerate(topics):
        words = topic['top_words']
        weights = topic['word_weights']
        
        # Normalize weights to 0-1 range for this topic only
        if weights.max() > 0:
            normalized_weights = weights / weights.max()
        else:
            normalized_weights = weights
        
        # Create color gradient based on normalized weights
        colors = plt.cm.YlOrRd(0.3 + normalized_weights * 0.6)
        
        # Create horizontal bar chart
        y_pos = np.arange(len(words))
        bars = axes[idx].barh(y_pos, weights, color=colors, edgecolor='black', linewidth=0.5)
        
        axes[idx].set_yticks(y_pos)
        axes[idx].set_yticklabels(words, fontsize=11)
        axes[idx].set_xlabel('Weight', fontsize=12, fontweight='bold')
        axes[idx].set_title(f'Topic {idx} - {method_name}', fontsize=14, fontweight='bold', pad=15)
        axes[idx].invert_yaxis()
        axes[idx].grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for i, (bar, weight) in enumerate(zip(bars, weights)):
            if weight > 0:  # Only show label if weight is positive
                axes[idx].text(weight * 1.02, i, f'{weight:.4f}', 
                              va='center', fontsize=9, color='black', fontweight='bold')
    
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
        
        # Calculate topic concentration
        concentration = np.max(topic) / np.sum(topic)
        
        print(f"\nTopic {topic_idx}:")
        print(f"  Concentration: {concentration:.4f}")
        print(f"  Top words: {', '.join(top_words[:5])}")

def main():
    """Main function to run topic modeling with NER filtering."""
    print("="*60)
    print("Elizabeth F.M. Perry Letters - Topic Modeling with NER")
    print("="*60)
    
    # Load NER entities from CSV
    print("\nLoading NER entities from CSV...")
    ner_entities = load_ner_entities('EFMPerry_NER_entities.csv')
    
    # Load letters
    print("\nLoading letters from split directory...")
    letters = load_elizabeth_letters_split()
    
    print(f"Loaded {len(letters)} letters")
    
    # Extract letter contents
    documents = [letter.get('content', '') for letter in letters if letter.get('content')]
    
    print(f"\nProcessing {len(documents)} documents for topic modeling...")
    
    # Determine number of topics based on corpus size
    if len(documents) < 10:
        n_topics = 3
    elif len(documents) < 30:
        n_topics = 5
    elif len(documents) < 50:
        n_topics = 7
    else:
        n_topics = 8  # Reduced from 10 to 8
    
    n_top_words = 15
    
    print(f"\nRunning topic modeling with {n_topics} topics...")
    
    # === WITH NER FILTERING ===
    print("\n" + "="*60)
    print("RUNNING WITH NER FILTERING (People & Locations Removed)")
    print("="*60)
    
    # LDA with NER
    print("\nLDA with NER filtering...")
    lda_topics_ner, lda_distribution_ner, lda_model_ner, lda_vectorizer_ner = extract_topics_lda(
        documents, n_topics=n_topics, n_top_words=n_top_words, ner_entities=ner_entities
    )
    display_topics(lda_topics_ner, "LDA (NER-filtered)")
    analyze_topic_coherence(lda_model_ner, lda_vectorizer_ner, documents)
    
    # NMF with NER
    print("\nNMF with NER filtering...")
    nmf_topics_ner, nmf_distribution_ner, nmf_model_ner, nmf_vectorizer_ner = extract_topics_nmf(
        documents, n_topics=n_topics, n_top_words=n_top_words, ner_entities=ner_entities
    )
    display_topics(nmf_topics_ner, "NMF (NER-filtered)")
    analyze_topic_coherence(nmf_model_ner, nmf_vectorizer_ner, documents)
    
    # === WITHOUT NER FILTERING (for comparison) ===
    print("\n" + "="*60)
    print("COMPARISON: Running WITHOUT NER filtering")
    print("="*60)
    
    lda_topics_no_ner, lda_distribution_no_ner, lda_model_no_ner, lda_vectorizer_no_ner = extract_topics_lda(
        documents, n_topics=n_topics, n_top_words=n_top_words, ner_entities=None
    )
    display_topics(lda_topics_no_ner, "LDA (No NER)")
    
    # Visualize topics
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # With NER filtering
    lda_ner_viz_path = os.path.join(output_dir, 'lda_topics_ner_filtered.png')
    nmf_ner_viz_path = os.path.join(output_dir, 'nmf_topics_ner_filtered.png')
    visualize_topics(lda_topics_ner, lda_ner_viz_path, 'LDA (NER-filtered)')
    visualize_topics(nmf_topics_ner, nmf_ner_viz_path, 'NMF (NER-filtered)')
    
    # Without NER filtering
    lda_no_ner_viz_path = os.path.join(output_dir, 'lda_topics_no_ner.png')
    visualize_topics(lda_topics_no_ner, lda_no_ner_viz_path, 'LDA (No NER)')
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\nTotal letters processed: {len(documents)}")
    print(f"Named entities filtered: {len(ner_entities)}")
    print(f"Number of topics: {n_topics}")
    print(f"\nVisualization files created:")
    print(f"  - {lda_ner_viz_path}")
    print(f"  - {nmf_ner_viz_path}")
    print(f"  - {lda_no_ner_viz_path}")

if __name__ == "__main__":
    main()