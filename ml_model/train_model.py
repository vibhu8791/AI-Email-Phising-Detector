import os
import sys
import csv
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib

def prepare_data(csv_path: str):
    texts = []
    labels = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = int(row['label'])
            subject = row.get('subject', '')
            sender = row.get('sender', '')
            body = row.get('body', '')
            combined = f"{subject} {sender} {body}"
            texts.append(combined)
            labels.append(label)
    return texts, labels

def train_and_save():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, 'dataset', 'phishing_dataset.csv')
    saved_models_dir = os.path.join(base_dir, 'saved_models')
    os.makedirs(saved_models_dir, exist_ok=True)

    print(f"Loading dataset from {dataset_path}...")
    X, y = prepare_data(dataset_path)
    print(f"Total samples: {len(X)} (Phishing: {sum(1 for l in y if l == 1)}, Safe: {sum(1 for l in y if l == 0)})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print("Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=10000,
        sublinear_tf=True,
        stop_words='english'
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Training Logistic Regression Model...")
    model = LogisticRegression(
        C=1.5,
        max_iter=1000,
        class_weight='balanced',
        random_state=42
    )
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n================ MODEL EVALUATION ================")
    print(f"Test Accuracy: {acc * 100:.2f}%\n")
    print(classification_report(y_test, y_pred, target_names=['Safe', 'Phishing']))
    print(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
    print(f"===================================================\n")

    # Save artifacts
    vectorizer_path = os.path.join(saved_models_dir, 'tfidf_vectorizer.joblib')
    model_path = os.path.join(saved_models_dir, 'phishing_model.joblib')

    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(model, model_path)
    print(f"Saved Vectorizer -> {vectorizer_path}")
    print(f"Saved Model      -> {model_path}")

    # Sanity checks
    test_phish = "URGENT: Your PayPal account is frozen. Click http://192.168.1.1/pay to unlock."
    test_safe = "Team, here is the agenda for tomorrow's sprint planning sync."
    for sample in [test_phish, test_safe]:
        vec = vectorizer.transform([sample])
        prob = model.predict_proba(vec)[0][1]
        print(f"Sanity Check: '{sample[:40]}...' => Phishing Probability: {prob * 100:.1f}%")

if __name__ == '__main__':
    train_and_save()
