import os
import sys
import csv
import hashlib
import random
from collections import defaultdict
from typing import Dict, List, Tuple

csv.field_size_limit(10 * 1024 * 1024)

ROOT_DIR = r"D:\project\Ai Phising Email"
MASTER_CSV = os.path.join(ROOT_DIR, "ml_model", "dataset", "phishing_dataset.csv")
OUTPUT_DIR = os.path.join(ROOT_DIR, "ml_model", "dataset", "splits_grouped")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def normalize_body(body: str) -> str:
    return " ".join((body or "").strip().lower().split())

def normalize_subject(subj: str) -> str:
    return " ".join((subj or "").strip().lower().split())

def get_group_key(subject: str, body: str) -> str:
    norm_b = normalize_body(body)
    # If body is substantial, group strictly by body
    if len(norm_b) >= 20:
        return hashlib.sha256(norm_b.encode("utf-8", errors="ignore")).hexdigest()
    else:
        # If body is tiny or empty, group by combination of subject + body
        combo = f"SUBJ:{normalize_subject(subject)} ||| BODY:{norm_b}"
        return hashlib.sha256(combo.encode("utf-8", errors="ignore")).hexdigest()

def main():
    print("=" * 70)
    print("CREATING LEAKAGE-RESISTANT GROUPED DATASET SPLITS")
    print("=" * 70)

    # 1. Load Master Dataset
    records = []
    with open(MASTER_CSV, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append({
                "label": int(r["label"]),
                "subject": r.get("subject", "") or "",
                "sender": r.get("sender", "") or "",
                "body": r.get("body", "") or ""
            })

    total_records = len(records)
    print(f"Loaded master dataset: {total_records} records.")

    # 2. Cluster into Groups
    groups = defaultdict(list)
    for idx, r in enumerate(records):
        g_key = get_group_key(r["subject"], r["body"])
        groups[g_key].append(r)

    print(f"Total unique template groups identified: {len(groups)}")

    # 3. Check for Label Conflicts within Groups
    conflicts = []
    for g_key, items in groups.items():
        labels = set(x["label"] for x in items)
        if len(labels) > 1:
            conflicts.append((g_key, items))

    print(f"\n--- Conflicting Labels Within Template Groups ---")
    if conflicts:
        print(f"WARNING: Found {len(conflicts)} template groups with conflicting labels!")
        for g_key, items in conflicts[:5]:
            print(f"  Group {g_key[:8]}: {len(items)} samples, labels: {[x['label'] for x in items]}")
            for it in items:
                print(f"    - Label {it['label']} | From: {it['sender'][:30]} | Subj: {it['subject'][:40]}")
    else:
        print("[PASS] Zero conflicting labels found within any template group.")

    # 4. Group Splitting with Priority on Zero Leakage
    # Separate groups by majority label
    random.seed(42)

    phish_groups = []
    safe_groups = []

    for g_key, items in groups.items():
        # majority label
        avg_label = sum(x["label"] for x in items) / len(items)
        if avg_label >= 0.5:
            phish_groups.append((g_key, items))
        else:
            safe_groups.append((g_key, items))

    random.shuffle(phish_groups)
    random.shuffle(safe_groups)

    print(f"\nGroup summary by class:")
    print(f"  Phishing groups: {len(phish_groups)} (containing {sum(len(it) for _, it in phish_groups)} emails)")
    print(f"  Safe groups:     {len(safe_groups)} (containing {sum(len(it) for _, it in safe_groups)} emails)")

    # Partition groups into ~70% train, ~15% val, ~15% test
    def partition_groups(group_list, train_pct=0.70, val_pct=0.15):
        total_emails = sum(len(it) for _, it in group_list)
        train_target = int(total_emails * train_pct)
        val_target = int(total_emails * val_pct)

        train_g, val_g, test_g = [], [], []
        train_cnt, val_cnt = 0, 0

        for g_key, items in group_list:
            n = len(items)
            if train_cnt + n <= train_target or (train_cnt < train_target and val_cnt >= val_target):
                train_g.append((g_key, items))
                train_cnt += n
            elif val_cnt + n <= val_target or val_cnt < val_target:
                val_g.append((g_key, items))
                val_cnt += n
            else:
                test_g.append((g_key, items))

        return train_g, val_g, test_g

    p_tr, p_va, p_te = partition_groups(phish_groups)
    s_tr, s_va, s_te = partition_groups(safe_groups)

    train_data = [x for _, items in (p_tr + s_tr) for x in items]
    val_data = [x for _, items in (p_va + s_va) for x in items]
    test_data = [x for _, items in (p_te + s_te) for x in items]

    random.shuffle(train_data)
    random.shuffle(val_data)
    random.shuffle(test_data)

    # 5. Report Exact Counts and Class Distribution
    def split_stats(name, data):
        tot = len(data)
        phish = sum(1 for x in data if x["label"] == 1)
        safe = tot - phish
        print(f"  {name:12}: {tot:5} total emails | Phishing: {phish:5} ({phish/tot*100:5.2f}%) | Safe: {safe:5} ({safe/tot*100:5.2f}%)")

    print("\n--- Leakage-Resistant Grouped Split Statistics ---")
    split_stats("Train", train_data)
    split_stats("Validation", val_data)
    split_stats("Test", test_data)

    # 6. Verification: Strict Check of Zero Group/Body Leakage
    train_groups = set(g for g, _ in (p_tr + s_tr))
    val_groups = set(g for g, _ in (p_va + s_va))
    test_groups = set(g for g, _ in (p_te + s_te))

    tr_va_overlap = train_groups.intersection(val_groups)
    tr_te_overlap = train_groups.intersection(test_groups)
    va_te_overlap = val_groups.intersection(test_groups)

    print("\n--- Zero-Leakage Verification ---")
    print(f"  Train & Val Group Overlap:  {len(tr_va_overlap)}")
    print(f"  Train & Test Group Overlap: {len(tr_te_overlap)}")
    print(f"  Val & Test Group Overlap:   {len(va_te_overlap)}")

    assert len(tr_va_overlap) == 0, "Train and Val share groups!"
    assert len(tr_te_overlap) == 0, "Train and Test share groups!"
    assert len(va_te_overlap) == 0, "Val and Test share groups!"

    # Also check normalized body strings directly
    train_bodies = set(normalize_body(x["body"]) for x in train_data if len(normalize_body(x["body"])) >= 20)
    val_bodies = set(normalize_body(x["body"]) for x in val_data if len(normalize_body(x["body"])) >= 20)
    test_bodies = set(normalize_body(x["body"]) for x in test_data if len(normalize_body(x["body"])) >= 20)

    b_tr_va = train_bodies.intersection(val_bodies)
    b_tr_te = train_bodies.intersection(test_bodies)
    b_va_te = val_bodies.intersection(test_bodies)

    print(f"  Normalized Body Overlaps (Train/Val):  {len(b_tr_va)}")
    print(f"  Normalized Body Overlaps (Train/Test): {len(b_tr_te)}")
    print(f"  Normalized Body Overlaps (Val/Test):   {len(b_va_te)}")

    assert len(b_tr_va) == 0, "Normalized body overlap in Train and Val!"
    assert len(b_tr_te) == 0, "Normalized body overlap in Train and Test!"
    assert len(b_va_te) == 0, "Normalized body overlap in Val and Test!"

    print("VERIFICATION COMPLETE: Exactly ZERO template or body overlap across all three splits!")

    # 7. Write to splits_grouped/
    for name, data in [("train_grouped.csv", train_data), ("val_grouped.csv", val_data), ("test_grouped.csv", test_data)]:
        out_path = os.path.join(OUTPUT_DIR, name)
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["label", "subject", "sender", "body"])
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved: {out_path} ({len(data)} rows)")

if __name__ == "__main__":
    main()
