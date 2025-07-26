try:
    from janome.tokenizer import Tokenizer
    tokenizer = Tokenizer()
    JANOME_AVAILABLE = True
except ImportError:
    tokenizer = None
    JANOME_AVAILABLE = False

def extract_new_vocabulary(text: str, known_words: set) -> list:
    """
    Extract candidate vocabulary (unique nouns) from text that are not in known_words.
    Returns a list of new words.
    """
    if not JANOME_AVAILABLE:
        # Fallback: simple word extraction without morphological analysis
        import re
        words = re.findall(r'\b\w+\b', text)
        new_words = set()
        for word in words:
            if len(word) > 1 and word not in known_words:
                new_words.add(word)
        return sorted(list(new_words))
    
    tokens = tokenizer.tokenize(text)
    new_words = set()
    for token in tokens:
        part = token.part_of_speech
        if part.startswith("名詞"):
            word = token.surface
            if not word or word.isspace():
                continue
            if word in known_words:
                continue
            new_words.add(word)
    return sorted(new_words)

def load_user_dictionary(dict_path: str) -> set:
    """Load user-known vocabulary from a simple text file (one word per line)."""
    words = set()
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                w = line.strip()
                if w:
                    words.add(w)
    except FileNotFoundError:
        pass
    return words

def save_user_dictionary(dict_path: str, words: set):
    """Save the given set of words to the dictionary file."""
    with open(dict_path, 'w', encoding='utf-8') as f:
        for w in sorted(words):
            f.write(w + "\n")