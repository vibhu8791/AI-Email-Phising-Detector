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
    classification_report, confusion_matrix, roc_auc_score
)

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from ml_model.feature_extractor import preprocess_email_text

csv.field_size_limit(10 * 1024 * 1024)

DATASET_DIR = os.path.join(root_dir, "ml_model", "dataset")
SPLITS_DIR = os.path.join(DATASET_DIR, "splits")
SAVED_DIR = os.path.join(root_dir, "ml_model", "saved_models")
os.makedirs(SAVED_DIR, exist_ok=True)

def load_split(split_name: str) -> Tuple[List[str], List[int]]:
    path = os.path.join(SPLITS_DIR, split_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Split file not found: {path}. Run build_dataset.py first.")
    
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
    # cm: [[TN, FP], [FN, TP]]
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

def run_model_experiments():
    print("==================================================================")
    print("PHASE 2: ML MODEL EXPERIMENTATION & VALIDATION BENCHMARKING")
    print("==================================================================")

    print("Loading preprocessed Train and Validation splits...")
    X_train, y_train = load_split("train.csv")
    X_val, y_val = load_split("val.csv")
    print(f"Loaded: Train = {len(X_train)} samples, Validation = {len(X_val)} samples.")

    # 1. TF-IDF Vectorizer Experiments
    print("\n--- 1. Evaluating TF-IDF Configuration on Validation Set ---")
    tfidf_configs = [
        {"name": "TFIDF-Word-Unigram (max 10k)", "ngram": (1, 1), "max_feat": 10000, "sublinear": True},
        {"name": "TFIDF-Word-Bigram (max 15k)", "ngram": (1, 2), "max_feat": 15000, "sublinear": True},
        {"name": "TFIDF-Word-Bigram (max 25k)", "ngram": (1, 2), "max_feat": 25000, "sublinear": True},
        {"name": "TFIDF-Word-Bigram NoSublinear (15k)", "ngram": (1, 2), "max_feat": 15000, "sublinear": False},
    ]

    for cfg in tfidf_configs:
        vec = TfidfVectorizer(
            ngram_range=cfg["ngram"],
            max_features=cfg["max_feat"],
            sublinear_tf=cfg["sublinear"],
            min_df=2,
            max_df=0.98,
            stop_words="english"
        )
        X_tr_vec = vec.fit_transform(X_train)
        X_val_vec = vec.transform(X_val)

        # Baseline Logistic Regression for comparison
        m = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        m.fit(X_tr_vec, y_train)
        preds = m.predict(X_val_vec)
        probs = m.predict_proba(X_val_vec)[:, 1]
        metrics = evaluate_predictions(y_val, preds, probs)
        print(f"  [{cfg['name']}]: Acc: {metrics['accuracy']*100:.2f}% | Prec: {metrics['precision']*100:.2f}% | Rec: {metrics['recall']*100:.2f}% | F1: {metrics['f1']*100:.2f}% | AUC: {metrics['roc_auc']:.4f}")

    # Optimal TF-IDF chosen based on validation F1 & coverage:
    # ngram_range=(1, 2), max_features=15000, sublinear_tf=True
    print("\nSelected TF-IDF Vectorizer: ngram_range=(1, 2), max_features=15000, sublinear_tf=True, min_df=2")
    final_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=15000,
        sublinear_tf=True,
        min_df=2,
        max_df=0.98,
        stop_words="english"
    )
    X_train_vec = final_vectorizer.fit_transform(X_train)
    X_val_vec = final_vectorizer.transform(X_val)

    # 2. Classifier Comparison on Validation Set
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

    best_model_info = None
    best_f1 = -1.0

    for cand in candidates:
        name = cand["name"]
        clf = cand["model"]
        clf.fit(X_train_vec, y_train)

        preds = clf.predict(X_val_vec)
        # Class probability for class 1
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
            best_model_info = (name, clf, metrics)

    print(f"\n==================================================================")
    print(f"CHAMPION MODEL SELECTED: {best_model_info[0]}")
    print(f"Validation F1: {best_model_info[2]['f1']*100:.2f}% | Precision: {best_model_info[2]['precision']*100:.2f}% | Recall: {best_model_info[2]['recall']*100:.2f}%")
    print(f"==================================================================")

    # Save artifacts
    winning_model = best_model_info[1]
    vec_path = os.path.join(SAVED_DIR, "tfidf_vectorizer.joblib")
    model_path = os.path.join(SAVED_DIR, "phishing_model.joblib")

    joblib.dump(final_vectorizer, vec_path)
    joblib.dump(winning_model, model_path)
    print(f"Artifacts successfully saved to:")
    print(f"  Vectorizer: {vec_path}")
    print(f"  Model:      {model_path}")

    # Verify probability mapping
    phish_idx = list(winning_model.classes_).index(1)
    print(f"Verified Model Class Index for Phishing (1): {phish_idx} (classes_ = {winning_model.classes_})")

    return final_vectorizer, winning_model

if __name__ == "__main__":
    run_model_experiments()
