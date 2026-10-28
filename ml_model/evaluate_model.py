import os
import sys
import csv
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ml_model.feature_extractor import preprocess_email_text, extract_heuristic_features

def load_test_split(test_csv_path):
    subjects, senders, bodies, labels = [], [], [], []
    with open(test_csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for r in reader:
            subjects.append(r.get("subject", "") or "")
            senders.append(r.get("sender", "") or "")
            bodies.append(r.get("body", "") or "")
            labels.append(int(r.get("label", 0)))
    return subjects, senders, bodies, np.array(labels)

def evaluate_baseline(subjects, senders, bodies, y_true):
    vec_path = os.path.join(ROOT_DIR, "ml_model", "backup", "tfidf_vectorizer_baseline.joblib")
    model_path = os.path.join(ROOT_DIR, "ml_model", "backup", "phishing_model_baseline.joblib")

    if not os.path.exists(vec_path) or not os.path.exists(model_path):
        print("[-] Baseline model artifacts not found in ml_model/backup/")
        return None

    vec = joblib.load(vec_path)
    model = joblib.load(model_path)

    # Baseline combined text representation
    raw_texts = [f"{s} {snd} {b}" for s, snd, b in zip(subjects, senders, bodies)]
    X_vec = vec.transform(raw_texts)
    
    phish_idx = list(model.classes_).index(1) if hasattr(model, 'classes_') else 1
    y_prob = model.predict_proba(X_vec)[:, phish_idx]
    y_pred = (y_prob >= 0.5).astype(int)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    tn, fp, fn, tp = cm.ravel()

    return {
        "model_name": "Baseline (50-sample Logistic Regression)",
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "cm": cm,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "y_prob": y_prob,
        "y_pred": y_pred
    }

def evaluate_improved(subjects, senders, bodies, y_true):
    vec_path = os.path.join(ROOT_DIR, "ml_model", "saved_models", "tfidf_vectorizer.joblib")
    model_path = os.path.join(ROOT_DIR, "ml_model", "saved_models", "phishing_model.joblib")

    if not os.path.exists(vec_path) or not os.path.exists(model_path):
        print("[-] Improved model artifacts not found in ml_model/saved_models/")
        return None

    vec = joblib.load(vec_path)
    model = joblib.load(model_path)

    # Unified preprocessing identical to training
    processed_texts = [preprocess_email_text(s, snd, b) for s, snd, b in zip(subjects, senders, bodies)]
    X_vec = vec.transform(processed_texts)

    phish_idx = list(model.classes_).index(1) if hasattr(model, 'classes_') else 1
    y_prob = model.predict_proba(X_vec)[:, phish_idx]
    y_pred = (y_prob >= 0.5).astype(int)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    tn, fp, fn, tp = cm.ravel()

    return {
        "model_name": "Improved Model (Calibrated Linear SVM, 5005-sample corpus)",
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "cm": cm,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "y_prob": y_prob,
        "y_pred": y_pred
    }

def evaluate_hybrid(subjects, senders, bodies, y_true):
    from backend.app.services.analyzer import analyzer

    hybrid_preds = []
    risk_scores = []
    
    for s, snd, b in zip(subjects, senders, bodies):
        res = analyzer.analyze(s, snd, b)
        risk = res["risk_score"]
        risk_scores.append(risk)
        # Classify as phishing if final_risk >= 50 (or classification in ["SUSPICIOUS", "PHISHING"])
        # Standard decision boundary for binary comparison:
        is_phish = 1 if risk >= 50 else 0
        hybrid_preds.append(is_phish)

    y_pred = np.array(hybrid_preds)
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    return {
        "model_name": "Full Hybrid System (ML + Heuristics + Calibration)",
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "cm": cm,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "risk_scores": risk_scores,
        "y_pred": y_pred
    }

def main():
    test_csv = os.path.join(ROOT_DIR, "ml_model", "dataset", "splits", "test.csv")
    print("=" * 70)
    print("AI PHISHING DETECTION SYSTEM: RIGOROUS INDEPENDENT TEST BENCHMARK")
    print("=" * 70)
    print(f"Loading Untouched Test Split: {test_csv}")
    subjects, senders, bodies, y_true = load_test_split(test_csv)
    n_total = len(y_true)
    n_phish = int(np.sum(y_true == 1))
    n_safe = int(np.sum(y_true == 0))
    print(f"Total Test Samples: {n_total} (Phishing: {n_phish} [{n_phish/n_total*100:.1f}%], Legitimate/Safe: {n_safe} [{n_safe/n_total*100:.1f}%])\n")

    baseline_res = evaluate_baseline(subjects, senders, bodies, y_true)
    improved_res = evaluate_improved(subjects, senders, bodies, y_true)

    print("\n" + "=" * 70)
    print("EVALUATION COMPARISON: BASELINE vs IMPROVED ML MODEL")
    print("=" * 70)

    if baseline_res:
        print(f"\n[1] BASELINE MODEL ({baseline_res['model_name']}):")
        print(f"    - Accuracy:         {baseline_res['accuracy']*100:.2f}%")
        print(f"    - Precision:        {baseline_res['precision']*100:.2f}%")
        print(f"    - Recall:           {baseline_res['recall']*100:.2f}%")
        print(f"    - F1-Score:         {baseline_res['f1']*100:.2f}%")
        print(f"    - Confusion Matrix: TN={baseline_res['tn']}, FP={baseline_res['fp']}, FN={baseline_res['fn']}, TP={baseline_res['tp']}")
        print(f"    - False Positives (Legitimate flagged as Phishing): {baseline_res['fp']} / {n_safe} ({baseline_res['fp']/n_safe*100:.2f}%)")
        print(f"    - False Negatives (Phishing missed as Legitimate):  {baseline_res['fn']} / {n_phish} ({baseline_res['fn']/n_phish*100:.2f}%)")

    if improved_res:
        print(f"\n[2] IMPROVED MODEL ({improved_res['model_name']}):")
        print(f"    - Accuracy:         {improved_res['accuracy']*100:.2f}%")
        print(f"    - Precision:        {improved_res['precision']*100:.2f}%")
        print(f"    - Recall:           {improved_res['recall']*100:.2f}%")
        print(f"    - F1-Score:         {improved_res['f1']*100:.2f}%")
        print(f"    - Confusion Matrix: TN={improved_res['tn']}, FP={improved_res['fp']}, FN={improved_res['fn']}, TP={improved_res['tp']}")
        print(f"    - False Positives (Legitimate flagged as Phishing): {improved_res['fp']} / {n_safe} ({improved_res['fp']/n_safe*100:.2f}%)")
        print(f"    - False Negatives (Phishing missed as Legitimate):  {improved_res['fn']} / {n_phish} ({improved_res['fn']/n_phish*100:.2f}%)")

    # Detailed Error Analysis on Improved Model
    if improved_res:
        fp_indices = np.where((y_true == 0) & (improved_res['y_pred'] == 1))[0]
        fn_indices = np.where((y_true == 1) & (improved_res['y_pred'] == 0))[0]

        print("\n" + "-" * 70)
        print(f"IMPROVED MODEL ERROR ANALYSIS (FP Count: {len(fp_indices)}, FN Count: {len(fn_indices)})")
        print("-" * 70)
        if len(fp_indices) > 0:
            print(f"Sample False Positives (First {min(3, len(fp_indices))}):")
            for idx in fp_indices[:3]:
                print(f"  * From: {senders[idx][:40]} | Subject: {subjects[idx][:40]} | Prob: {improved_res['y_prob'][idx]:.3f}")
        else:
            print("  * Zero False Positives observed on the test set.")

        if len(fn_indices) > 0:
            print(f"Sample False Negatives (First {min(3, len(fn_indices))}):")
            for idx in fn_indices[:3]:
                print(f"  * From: {senders[idx][:40]} | Subject: {subjects[idx][:40]} | Prob: {improved_res['y_prob'][idx]:.3f}")
        else:
            print("  * Zero False Negatives observed on the test set.")

    # High-Value Domain & Edge Case Test
    print("\n" + "=" * 70)
    print("SPECIAL TARGETED HARD-CASE BENCHMARK (False Positive Resistance)")
    print("=" * 70)
    hard_cases = [
        {
            "name": "Official Google Security Alert",
            "sender": "Google <no-reply@accounts.google.com>",
            "subject": "Security alert: New sign-in from Chrome on Windows",
            "body": "A new sign-in occurred on your Google Account from a Windows device. If this was you, you do not need to do anything. If this wasn't you, review your devices at https://myaccount.google.com/device-activity immediately.",
            "expected": "SAFE"
        },
        {
            "name": "Urgent Corporate Legal Review",
            "sender": "Sarah Jenkins <legal@enterprise-corp.com>",
            "subject": "URGENT: Please review NDA draft by 5:00 PM today",
            "body": "Hi Team, please find attached the revised mutual NDA for Project Horizon. We need legal signoff by 5:00 PM sharp to submit to the client. Let me know if you have objections.",
            "expected": "SAFE"
        },
        {
            "name": "Official Apple ID Receipt",
            "sender": "Apple <no_reply@email.apple.com>",
            "subject": "Your receipt from Apple for iCloud+ storage",
            "body": "Thank you for your subscription. Your payment of $0.99 for 50GB iCloud storage has been processed. Manage your Apple ID at https://appleid.apple.com.",
            "expected": "SAFE"
        },
        {
            "name": "PayPal Credential Harvesting Attack",
            "sender": "PayPal Support <service-notice@paypal-security-update24.com>",
            "subject": "URGENT: Your account has been limited due to suspicious activity",
            "body": "Dear customer, your PayPal account has been temporarily restricted. Click http://192.168.1.55/paypal/login.php to verify your identity within 24 hours or your account will be permanently closed.",
            "expected": "PHISHING"
        },
        {
            "name": "CEO Wire Fraud Impersonation",
            "sender": "Mark Zuckerberg <ceo-direct@vip-offices-global.com>",
            "subject": "Immediate Wire Transfer Required - Confidential",
            "body": "I am currently in an urgent meeting with our acquisition partners. Please execute an immediate wire transfer of $45,000 to the attached vendor account today. Keep this strictly confidential.",
            "expected": "PHISHING"
        }
    ]

    from backend.app.services.analyzer import analyzer

    for hc in hard_cases:
        res = analyzer.analyze(hc["subject"], hc["sender"], hc["body"])
        verdict = res["classification"]
        risk = res["risk_score"]
        ml_p = res["ml_phishing_probability"]
        status = "PASSED" if verdict == hc["expected"] else "FAILED"
        print(f"[{status}] {hc['name']}:")
        print(f"      Expected: {hc['expected']} | Actual: {verdict} (Risk Score: {risk}/100, ML Prob: {ml_p})")
        if res["detected_flags"]:
            print(f"      Flags: {res['detected_flags'][:2]}")

if __name__ == "__main__":
    main()
