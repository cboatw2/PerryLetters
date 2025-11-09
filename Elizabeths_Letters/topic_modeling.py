import re
import os
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
import matplotlib.pyplot as plt
import pandas as pd

def load_elizabeth_letters(filepath='EFMPerryTranscribedLetters.txt'):
    """Load and parse Elizabeth's letters from the text file."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)
    
    print(f"Loading from: {full_path}")
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    letters = []
    # Split by common delimiters - try multiple patterns
    # First try splitting by "---" or multiple newlines
    letter_blocks = re.split(r'\n---+\n|\n\n\n+', content)
    
    # If that doesn't work well, try other patterns
    if len(letter_blocks) < 5:
        # Try splitting by letter headers (common patterns in transcribed letters)
        letter_blocks = re.split(r'\n(?=Letter \d+|From:|Date:)', content)
    
    for block in letter_blocks:
        if block.strip() and len(block.strip()) > 50:  # Ignore very short blocks
            letter = {}
            lines = block.strip().split('\n')
            
            # Extract metadata and content
            content_text = []
            in_content = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Date:'):
                    letter['date'] = line.replace('Date:', '').strip()
                elif line.startswith('From:'):
                    letter['from'] = line.replace('From:', '').strip()
                elif line.startswith('To:'):
                    letter['to'] = line.replace('To:', '').strip()
                elif line.startswith('Location:'):
                    letter['location'] = line.replace('Location:', '').strip()
                elif line.startswith('Content:'):
                    in_content = True
                    content_text.append(line.replace('Content:', '').strip())
                elif in_content or (not any(line.startswith(prefix) for prefix in ['Date:', 'From:', 'To:', 'Location:'])):
                    content_text.append(line)
            
            # If no explicit content marker, use all non-metadata text
            if not content_text:
                content_text = [line for line in lines if not any(
                    line.startswith(prefix) for prefix in ['Date:', 'From:', 'To:', 'Location:']
                )]
            
            letter['content'] = ' '.join(content_text).strip()
            
            # Only add letters with substantial content
            if letter.get('content') and len(letter['content']) > 100:
                letters.append(letter)
    
    return letters

def preprocess_text(text):
    """Clean and preprocess text for topic modeling."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits but keep some punctuation for context
    text = re.sub(r'[^a-zA-Z\s\']', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# ADD THIS NEW FUNCTION for historical text
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
        'day', 'today', 'yesterday', 'tomorrow',
        
        # Add names if they dominate (adjust based on your corpus)
        # 'perry', 'elizabeth', etc.
    ])
    
    return list(ENGLISH_STOP_WORDS.union(custom_stops))

def extract_topics_lda(documents, n_topics=5, n_top_words=10):
    """Extract topics using Latent Dirichlet Allocation (LDA)."""
    
    # Preprocess documents
    processed_docs = [preprocess_text(doc) for doc in documents]
    
    # Create document-term matrix with improved parameters
    vectorizer = CountVectorizer(
        max_df=0.85,      # Lower threshold - terms in >85% of docs are too common
        min_df=3,         # Require words in at least 3 letters
        max_features=500, # Reduce features for focused topics
        stop_words=get_historical_stopwords(),
        ngram_range=(1, 2),  # Include bigrams for phrases like "your letter"
        token_pattern=r'\b[a-z]{3,}\b'  # Only words 3+ characters
    )
    
    doc_term_matrix = vectorizer.fit_transform(processed_docs)
    
    # Run LDA with adjusted parameters
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=100,        # More iterations for convergence
        learning_method='batch',  # Better for smaller corpora
        doc_topic_prior=0.1,      # Lower alpha for more focused topics
        topic_word_prior=0.01     # Lower beta for more distinct topics
    )
    
    lda_output = lda_model.fit_transform(doc_term_matrix)
    
    # Get feature names (words)
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

def extract_topics_nmf(documents, n_topics=5, n_top_words=10):
    """Extract topics using Non-negative Matrix Factorization (NMF)."""
    
    # Preprocess documents
    processed_docs = [preprocess_text(doc) for doc in documents]
    
    # Create TF-IDF matrix with improved parameters
    vectorizer = TfidfVectorizer(
        max_df=0.85,
        min_df=3,
        max_features=500,
        stop_words=get_historical_stopwords(),
        ngram_range=(1, 2),
        token_pattern=r'\b[a-z]{3,}\b',
        sublinear_tf=True  # Use log scaling for term frequency
    )
    
    tfidf_matrix = vectorizer.fit_transform(processed_docs)
    
    # Run NMF with adjusted parameters
    nmf_model = NMF(
        n_components=n_topics,
        random_state=42,
        max_iter=1000,
        alpha_W=0.1,      # Regularization for document-topic matrix
        alpha_H=0.1,      # Regularization for topic-word matrix
        l1_ratio=0.5      # Balance between L1 and L2 regularization
    )
    
    nmf_output = nmf_model.fit_transform(tfidf_matrix)
    
    # Get feature names
    feature_names = vectorizer.get_feature_names_out()
    
    # Extract top words for each topic
    topics = []
    for topic_idx, topic in enumerate(nmf_model.components_):
        top_words_idx = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics.append({
            'topic_id': topic_idx,
            'top_words': top_words,
            'word_weights': topic[top_words_idx]
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

def analyze_letter_topics(letters, topic_distribution):
    """Analyze which topics appear in which letters."""
    results = []
    
    for i, letter in enumerate(letters):
        if i < len(topic_distribution):
            dominant_topic = topic_distribution[i].argmax()
            topic_strength = topic_distribution[i][dominant_topic]
            
            results.append({
                'letter_index': i,
                'date': letter.get('date', 'Unknown'),
                'from': letter.get('from', 'Unknown'),
                'to': letter.get('to', 'Unknown'),
                'dominant_topic': dominant_topic,
                'topic_strength': topic_strength,
                'preview': letter.get('content', '')[:100] + '...'
            })
    
    return pd.DataFrame(results)

def visualize_topics(topics, save_path='topics_visualization.png'):
    """Create a visualization of topics and their top words."""
    n_topics = len(topics)
    fig, axes = plt.subplots(n_topics, 1, figsize=(12, 3*n_topics))
    
    if n_topics == 1:
        axes = [axes]
    
    for idx, topic in enumerate(topics):
        words = topic['top_words']
        weights = topic['word_weights']
        
        axes[idx].barh(words, weights, color='#8b4513')
        axes[idx].set_title(f'Topic {idx}', fontsize=14, fontweight='bold')
        axes[idx].set_xlabel('Word Weight')
        axes[idx].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to: {save_path}")
    plt.close()

def main():
    """Main function to run topic modeling."""
    print("Loading Elizabeth F.M. Perry's letters...")
    letters = load_elizabeth_letters()
    
    print(f"Loaded {len(letters)} letters")
    
    if len(letters) == 0:
        print("No letters found. Please check the file format.")
        print("\nShowing first 500 characters of the file to help debug:")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, 'EFMPerryTranscribedLetters.txt'), 'r', encoding='utf-8') as f:
            print(f.read(500))
        return
    
    # Show sample letter
    print("\nSample letter:")
    print(f"Date: {letters[0].get('date', 'N/A')}")
    print(f"From: {letters[0].get('from', 'N/A')}")
    print(f"Content preview: {letters[0].get('content', '')[:200]}...")
    
    # Extract letter contents
    documents = [letter.get('content', '') for letter in letters if letter.get('content')]
    
    print(f"\nProcessing {len(documents)} documents for topic modeling...")
    
    # Adjust number of topics based on corpus size
    if len(documents) < 10:
        n_topics = 3
    elif len(documents) < 30:
        n_topics = 5
    else:
        n_topics = 7  # More topics for larger corpora
    
    n_top_words = 15  # Show more words per topic for better interpretation
    
    print(f"\nRunning topic modeling with {n_topics} topics...")
    
    # LDA Topic Modeling
    print("\n" + "="*60)
    print("Running LDA (Latent Dirichlet Allocation)...")
    print("="*60)
    lda_topics, lda_distribution, lda_model, lda_vectorizer = extract_topics_lda(
        documents, n_topics=n_topics, n_top_words=n_top_words
    )
    display_topics(lda_topics, "LDA")
    
    # NMF Topic Modeling
    print("\n" + "="*60)
    print("Running NMF (Non-negative Matrix Factorization)...")
    print("="*60)
    nmf_topics, nmf_distribution, nmf_model, nmf_vectorizer = extract_topics_nmf(
        documents, n_topics=n_topics, n_top_words=n_top_words
    )
    display_topics(nmf_topics, "NMF")
    
    # Analyze letters by topic
    print("\n" + "="*60)
    print("Analyzing letter topics...")
    print("="*60)
    letter_analysis = analyze_letter_topics(letters, lda_distribution)
    print("\nLetters by Dominant Topic (LDA):")
    print(letter_analysis[['date', 'dominant_topic', 'topic_strength', 'preview']])
    
    # Save results
    output_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(output_dir, 'elizabeth_letters_topics.csv')
    letter_analysis.to_csv(csv_path, index=False)
    print(f"\nDetailed analysis saved to: {csv_path}")
    
    # Visualize topics
    lda_viz_path = os.path.join(output_dir, 'lda_topics_visualization.png')
    nmf_viz_path = os.path.join(output_dir, 'nmf_topics_visualization.png')
    visualize_topics(lda_topics, lda_viz_path)
    visualize_topics(nmf_topics, nmf_viz_path)
    
    # Topic distribution summary
    print("\n" + "="*60)
    print("Topic Distribution Summary:")
    print("="*60)
    topic_counts = Counter(letter_analysis['dominant_topic'])
    for topic_id, count in sorted(topic_counts.items()):
        print(f"Topic {topic_id}: {count} letters ({count/len(letters)*100:.1f}%)")

if __name__ == "__main__":
    main()