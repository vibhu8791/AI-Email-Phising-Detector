import os
import sys
import csv
import joblib
import numpy as np
from typing import List, Tuple, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import ComplementNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)

ROOT_DIR = r"D:\project\Ai Phising Email"
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ml_model.feature_extractor import preprocess_email_text

csv.field_size_limit(10 * 1024 * 1024)

DATASET_DIR = os.path.join(ROOT_DIR, "ml_model", "dataset")
SPLITS_DIR = os.path.join(DATASET_DIR, "splits_grouped")
CANDIDATE_DIR = os.path.join(ROOT_DIR, "ml_model", "candidate_models")
os.makedirs(CANDIDATE_DIR, exist_ok=True)

def load_split(split_name: str) -> Tuple[List[str], List[int]]:
    path = os.path.join(SPLITS_DIR, split_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Split file not found: {path}.")
    
    texts = []
    labels = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = preprocess_email_text(
                subject=row.get("subject", ""),
                sender=row.get("sender", ""),
                body=row.get("body", "")
            )
            texts.append(cleaned)
            labels.append(int(row["label"]))
    return texts, labels

def evaluate_predictions(y_true, y_pred, y_prob=None) -> Dict[str, Any]:
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, pos_label=1, zero_division=0)
    rec = recall_score(y_true, y_pred, pos_label=1, zero_division=0)
    f1 = f1_score(y_true, y_pred, pos_label=1, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    auc = roc_auc_score(y_true, y_prob) if y_prob is not None else 0.0

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": auc,
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
        "cm": cm
    }

def main():
    print("=" * 70)
    print("TRAINING CANDIDATE MODEL ON LEAKAGE-RESISTANT GROUPED SPLITS")
    print("=" * 70)

    print("Loading preprocessed Train and Validation splits from splits_grouped/...")
    X_train, y_train = load_split("train_grouped.csv")
    X_val, y_val = load_split("val_grouped.csv")
    print(f"Loaded: Train = {len(X_train)} samples, Validation = {len(X_val)} samples.")

    # 1. Fit TF-IDF Vectorizer strictly on train_grouped
    print("\n--- 1. Fitting TF-IDF Vectorizer on Train Data Only ---")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=15000,
        sublinear_tf=True,
        min_df=2,
        max_df=0.98,
        stop_words="english"
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    print(f"Vocabulary Size: {len(vectorizer.vocabulary_)} features")

    # 2. Classifier Candidates Benchmarked on val_grouped
    print("\n--- 2. Comparing Classifier Candidates on Validation Set ---")
    candidates = [
        {
            "name": "Logistic Regression (C=1.0, Default)",
            "model": LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        },
        {
            "name": "Logistic Regression (C=2.5, Balanced)",
            "model": LogisticRegression(C=2.5, max_iter=1000, class_weight="balanced", random_state=42)
        },
        {
            "name": "Linear SVM (Calibrated L2)",
            "model": CalibratedClassifierCV(
                estimator=LinearSVC(C=1.0, max_iter=2000, dual=False, random_state=42),
                cv=5
            )
        },
        {
            "name": "SGDClassifier (log_loss, ElasticNet)",
            "model": SGDClassifier(loss="log_loss", penalty="elasticnet", l1_ratio=0.15, max_iter=1000, random_state=42)
        },
        {
            "name": "Complement Naive Bayes",
            "model": ComplementNB(alpha=0.5)
        }
    ]

    best_cand = None
    best_f1 = -1.0

    for cand in candidates:
        name = cand["name"]
        clf = cand["model"]
        clf.fit(X_train_vec, y_train)

        preds = clf.predict(X_val_vec)
        classes_list = list(clf.classes_)
        phish_idx = classes_list.index(1)
        probs = clf.predict_proba(X_val_vec)[:, phish_idx]

        metrics = evaluate_predictions(y_val, preds, probs)
        print(f"\n  Candidate: {name}")
        print(f"    Accuracy:  {metrics['accuracy']*100:.2f}%")
        print(f"    Precision: {metrics['precision']*100:.2f}% (FP: {metrics['fp']})")
        print(f"    Recall:    {metrics['recall']*100:.2f}% (FN: {metrics['fn']})")
        print(f"    F1-Score:  {metrics['f1']*100:.2f}%")
        print(f"    ROC-AUC:   {metrics['roc_auc']:.4f}")

        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            best_cand = (name, clf, metrics)

    print(f"\n==================================================================")
    print(f"CHAMPION CANDIDATE SELECTED: {best_cand[0]}")
    print(f"Validation F1: {best_cand[2]['f1']*100:.2f}% | Precision: {best_cand[2]['precision']*100:.2f}% | Recall: {best_cand[2]['recall']*100:.2f}%")
    print(f"==================================================================")

    # 3. Save Candidate in Isolated Directory (ml_model/candidate_models/)
    winning_model = best_cand[1]
    vec_path = os.path.join(CANDIDATE_DIR, "tfidf_vectorizer_candidate.joblib")
    model_path = os.path.join(CANDIDATE_DIR, "phishing_model_candidate.joblib")

    joblib.dump(vectorizer, vec_path)
    joblib.dump(winning_model, model_path)
    print(f"\nCandidate artifacts safely saved to isolated directory:")
    print(f"  Vectorizer: {vec_path}")
    print(f"  Model:      {model_path}")
    print(f"NOTICE: Live production artifacts in ml_model/saved_models/ remain UNCHANGED.")

if __name__ == "__main__":
    main()
