import re
import os
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def load_elizabeth_letters(filepath='EFMPerryTranscribedLetters.txt'):
    """Load and parse Elizabeth's letters from the text file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)
    
    print(f"Loading from: {full_path}")
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    letters = []
    # Split by common delimiters - try multiple patterns
    letter_blocks = re.split(r'\n---+\n|\n\n\n+', content)
    if len(letter_blocks) < 5:
        letter_blocks = re.split(r'\n(?=Letter \d+|From:|Date:)', content)
    
    for block in letter_blocks:
        if block.strip() and len(block.strip()) > 50:
            letter = {}
            lines = block.strip().split('\n')
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
            if not content_text:
                content_text = [line for line in lines if not any(
                    line.startswith(prefix) for prefix in ['Date:', 'From:', 'To:', 'Location:']
                )]
            letter['content'] = ' '.join(content_text).strip()
            if letter.get('content') and len(letter['content']) > 100:
                letters.append(letter)
    return letters

def preprocess_text(text, ner_entities=None):
    """Clean and preprocess text for topic modeling, removing NER entities if provided."""
    if ner_entities:
        text = text.lower()
        for entity in ner_entities:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(entity) + r'\b'
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s\']', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_historical_stopwords():
    """Create custom stopword list for 19th century letters."""
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    custom_stops = set([
        'dear', 'dearest', 'sir', 'madam', 'mrs', 'mr', 'miss',
        'yours', 'sincerely', 'affectionately', 'truly', 
        'respectfully', 'obediently', 'faithfully',
        'thee', 'thy', 'thou', 'thine', 'shall', 'ye',
        'received', 'wrote', 'write', 'letter', 'letters', 'sent', 'send',
        'hope', 'hoped', 'know', 'known', 'think',
        'day', 'today', 'yesterday', 'tomorrow',
    ])
    return list(ENGLISH_STOP_WORDS.union(custom_stops))

def load_ner_entities(csv_path='EFMPerry_NER_entities.csv'):
    """Load named entities from the NER CSV file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, csv_path)
    if not os.path.exists(full_path):
        print(f"Warning: NER entities file not found: {full_path}")
        return set()
    df = pd.read_csv(full_path)
    entities = set(df['entity_name'].str.lower().unique())
    return entities

def extract_topics_lda(documents, n_topics=3, n_top_words=15, ner_entities=None):
    """Extract topics using Latent Dirichlet Allocation (LDA)."""
    processed_docs = [preprocess_text(doc, ner_entities) for doc in documents]
    vectorizer = CountVectorizer(
        max_df=0.85,
        min_df=3,
        max_features=500,
        stop_words=get_historical_stopwords(),
        ngram_range=(1, 2),
        token_pattern=r'\b[a-z]{3,}\b'
    )
    doc_term_matrix = vectorizer.fit_transform(processed_docs)
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=100,
        learning_method='batch',
        doc_topic_prior=0.1,
        topic_word_prior=0.01
    )
    lda_output = lda_model.fit_transform(doc_term_matrix)
    feature_names = vectorizer.get_feature_names_out()
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

def display_topics(topics, method_name="Topic Model"):
    print(f"\n{'='*60}")
    print(f"{method_name} Results")
    print(f"{'='*60}\n")
    for topic in topics:
        print(f"Topic {topic['topic_id']}:")
        print(f"  Top words: {', '.join(topic['top_words'])}")
        print()

def analyze_letter_topics(letters, topic_distribution):
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
    print("Loading Elizabeth F.M. Perry's letters...")
    letters = load_elizabeth_letters()
    print(f"Loaded {len(letters)} letters")
    if len(letters) == 0:
        print("No letters found. Please check the file format.")
        return
    print("\nSample letter:")
    print(f"Date: {letters[0].get('date', 'N/A')}")
    print(f"From: {letters[0].get('from', 'N/A')}")
    print(f"Content preview: {letters[0].get('content', '')[:200]}...")
    documents = [letter.get('content', '') for letter in letters if letter.get('content')]
    print(f"\nProcessing {len(documents)} documents for topic modeling...")

    # Load NER entities and filter them out of the documents
    ner_entities = load_ner_entities('EFMPerry_NER_entities.csv')
    print(f"Filtering {len(ner_entities)} NER entities from topic modeling.")

    n_topics = 3
    n_top_words = 15
    print(f"\nRunning topic modeling with {n_topics} topics...")
    print("\n" + "="*60)
    print("Running LDA (Latent Dirichlet Allocation)...")
    print("="*60)
    lda_topics, lda_distribution, lda_model, lda_vectorizer = extract_topics_lda(
        documents, n_topics=n_topics, n_top_words=n_top_words, ner_entities=ner_entities
    )
    display_topics(lda_topics, "LDA")
    print("\n" + "="*60)
    print("Analyzing letter topics...")
    print("="*60)
    letter_analysis = analyze_letter_topics(letters, lda_distribution)
    print("\nLetters by Dominant Topic (LDA):")
    print(letter_analysis[['date', 'dominant_topic', 'topic_strength', 'preview']])
    output_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(output_dir, 'elizabeth_letters_topics.csv')
    letter_analysis.to_csv(csv_path, index=False)
    print(f"\nDetailed analysis saved to: {csv_path}")
    lda_viz_path = os.path.join(output_dir, 'lda_topics_visualization.png')
    visualize_topics(lda_topics, lda_viz_path)
    print("\n" + "="*60)
    print("Topic Distribution Summary:")
    print("="*60)
    topic_counts = Counter(letter_analysis['dominant_topic'])
    for topic_id, count in sorted(topic_counts.items()):
        print(f"Topic {topic_id}: {count} letters ({count/len(letters)*100:.1f}%)")

if __name__ == "__main__":
    main()