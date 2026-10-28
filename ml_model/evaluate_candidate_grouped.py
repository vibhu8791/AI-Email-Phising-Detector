import os
import sys
import csv
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

ROOT_DIR = r"D:\project\Ai Phising Email"
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ml_model.feature_extractor import preprocess_email_text, extract_heuristic_features

csv.field_size_limit(10 * 1024 * 1024)

def load_data(csv_path):
    subjects, senders, bodies, labels = [], [], [], []
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for r in reader:
            subjects.append(r.get("subject", "") or "")
            senders.append(r.get("sender", "") or "")
            bodies.append(r.get("body", "") or "")
            labels.append(int(r.get("label", 0)))
    return subjects, senders, bodies, np.array(labels)

def eval_pipeline(vec, model, subjects, senders, bodies, y_true):
    processed = [preprocess_email_text(s, snd, b) for s, snd, b in zip(subjects, senders, bodies)]
    X_vec = vec.transform(processed)
    phish_idx = list(model.classes_).index(1) if hasattr(model, "classes_") else 1
    y_prob = model.predict_proba(X_vec)[:, phish_idx]
    y_pred = (y_prob >= 0.5).astype(int)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    return {
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

def main():
    print("=" * 70)
    print("ROBUSTNESS BENCHMARK: ORIGINAL TEST SET VS LEAKAGE-RESISTANT GROUPED TEST SET")
    print("=" * 70)

    # 1. Evaluate Candidate Model on the NEW Leakage-Resistant Test Set (test_grouped.csv)
    cand_vec_path = os.path.join(ROOT_DIR, "ml_model", "candidate_models", "tfidf_vectorizer_candidate.joblib")
    cand_model_path = os.path.join(ROOT_DIR, "ml_model", "candidate_models", "phishing_model_candidate.joblib")
    test_grouped_path = os.path.join(ROOT_DIR, "ml_model", "dataset", "splits_grouped", "test_grouped.csv")

    cand_vec = joblib.load(cand_vec_path)
    cand_model = joblib.load(cand_model_path)
    sub_grp, snd_grp, bod_grp, y_grp = load_data(test_grouped_path)

    grouped_res = eval_pipeline(cand_vec, cand_model, sub_grp, snd_grp, bod_grp, y_grp)

    # 2. Evaluate Production/Original Model on the ORIGINAL Test Set (test.csv)
    orig_vec_path = os.path.join(ROOT_DIR, "ml_model", "saved_models", "tfidf_vectorizer.joblib")
    orig_model_path = os.path.join(ROOT_DIR, "ml_model", "saved_models", "phishing_model.joblib")
    test_orig_path = os.path.join(ROOT_DIR, "ml_model", "dataset", "splits", "test.csv")

    orig_vec = joblib.load(orig_vec_path)
    orig_model = joblib.load(orig_model_path)
    sub_orig, snd_orig, bod_orig, y_orig = load_data(test_orig_path)

    orig_res = eval_pipeline(orig_vec, orig_model, sub_orig, snd_orig, bod_orig, y_orig)

    # Also evaluate Baseline 50-sample model on test_grouped.csv for historical context
    base_vec_path = os.path.join(ROOT_DIR, "ml_model", "backup", "tfidf_vectorizer_baseline.joblib")
    base_model_path = os.path.join(ROOT_DIR, "ml_model", "backup", "phishing_model_baseline.joblib")
    base_vec = joblib.load(base_vec_path)
    base_model = joblib.load(base_model_path)
    raw_texts = [f"{s} {snd} {b}" for s, snd, b in zip(sub_grp, snd_grp, bod_grp)]
    X_base = base_vec.transform(raw_texts)
    base_p_idx = list(base_model.classes_).index(1) if hasattr(base_model, "classes_") else 1
    base_probs = base_model.predict_proba(X_base)[:, base_p_idx]
    base_preds = (base_probs >= 0.5).astype(int)
    base_acc = accuracy_score(y_grp, base_preds)
    base_prec = precision_score(y_grp, base_preds, zero_division=0)
    base_rec = recall_score(y_grp, base_preds, zero_division=0)
    base_f1 = f1_score(y_grp, base_preds, zero_division=0)
    base_cm = confusion_matrix(y_grp, base_preds)
    b_tn, b_fp, b_fn, b_tp = base_cm.ravel()

    print("\n" + "=" * 70)
    print("HEAD-TO-HEAD COMPARATIVE EVALUATION RESULTS")
    print("=" * 70)

    print(f"\n[A] ORIGINAL RANDOM-STRATIFIED SPLIT (test.csv):")
    print(f"    - Total Samples:    {len(y_orig)} (Phishing: {int(np.sum(y_orig==1))}, Safe: {int(np.sum(y_orig==0))})")
    print(f"    - Accuracy:         {orig_res['accuracy']*100:.2f}%")
    print(f"    - Precision:        {orig_res['precision']*100:.2f}%")
    print(f"    - Recall:           {orig_res['recall']*100:.2f}%")
    print(f"    - F1-Score:         {orig_res['f1']*100:.2f}%")
    print(f"    - Confusion Matrix: TN={orig_res['tn']}, FP={orig_res['fp']}, FN={orig_res['fn']}, TP={orig_res['tp']}")
    print(f"    - False Positives:  {orig_res['fp']} / {orig_res['tn']+orig_res['fp']} ({orig_res['fp']/(orig_res['tn']+orig_res['fp'])*100:.2f}%)")
    print(f"    - False Negatives:  {orig_res['fn']} / {orig_res['tp']+orig_res['fn']} ({orig_res['fn']/(orig_res['tp']+orig_res['fn'])*100:.2f}%)")

    print(f"\n[B] LEAKAGE-RESISTANT GROUPED SPLIT (test_grouped.csv):")
    print(f"    - Total Samples:    {len(y_grp)} (Phishing: {int(np.sum(y_grp==1))}, Safe: {int(np.sum(y_grp==0))})")
    print(f"    - Accuracy:         {grouped_res['accuracy']*100:.2f}%")
    print(f"    - Precision:        {grouped_res['precision']*100:.2f}%")
    print(f"    - Recall:           {grouped_res['recall']*100:.2f}%")
    print(f"    - F1-Score:         {grouped_res['f1']*100:.2f}%")
    print(f"    - Confusion Matrix: TN={grouped_res['tn']}, FP={grouped_res['fp']}, FN={grouped_res['fn']}, TP={grouped_res['tp']}")
    print(f"    - False Positives:  {grouped_res['fp']} / {grouped_res['tn']+grouped_res['fp']} ({grouped_res['fp']/(grouped_res['tn']+grouped_res['fp'])*100:.2f}%)")
    print(f"    - False Negatives:  {grouped_res['fn']} / {grouped_res['tp']+grouped_res['fn']} ({grouped_res['fn']/(grouped_res['tp']+grouped_res['fn'])*100:.2f}%)")

    print(f"\n[C] BASELINE (50-SAMPLE MODEL) ON GROUPED TEST SET (test_grouped.csv):")
    print(f"    - Accuracy:         {base_acc*100:.2f}%")
    print(f"    - Precision:        {base_prec*100:.2f}%")
    print(f"    - Recall:           {base_rec*100:.2f}%")
    print(f"    - F1-Score:         {base_f1*100:.2f}%")
    print(f"    - Confusion Matrix: TN={b_tn}, FP={b_fp}, FN={b_fn}, TP={b_tp}")
    print(f"    - False Positives:  {b_fp} ({b_fp/(b_tn+b_fp)*100:.2f}%)")
    print(f"    - False Negatives:  {b_fn} ({b_fn/(b_tp+b_fn)*100:.2f}%)")

    # Error audit on Grouped Test Set
    fp_idx = np.where((y_grp == 0) & (grouped_res["y_pred"] == 1))[0]
    fn_idx = np.where((y_grp == 1) & (grouped_res["y_pred"] == 0))[0]

    print("\n" + "-" * 70)
    print(f"LEAKAGE-RESISTANT ERROR AUDIT (FP: {len(fp_idx)}, FN: {len(fn_idx)})")
    print("-" * 70)
    if len(fp_idx) > 0:
        print(f"False Positives:")
        for idx in fp_idx:
            print(f"  * From: {snd_grp[idx][:40]} | Subj: {sub_grp[idx][:40]} | Prob: {grouped_res['y_prob'][idx]:.4f}")
    else:
        print("  * ZERO False Positives observed on the leakage-resistant test set.")

    if len(fn_idx) > 0:
        print(f"False Negatives ({len(fn_idx)} samples):")
        for idx in fn_idx:
            print(f"  * From: {snd_grp[idx][:40]} | Subj: {sub_grp[idx][:40]} | Prob: {grouped_res['y_prob'][idx]:.4f}")
    else:
        print("  * ZERO False Negatives observed on the leakage-resistant test set.")

if __name__ == "__main__":
    main()
