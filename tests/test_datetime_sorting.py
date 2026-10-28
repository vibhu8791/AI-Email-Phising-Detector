import os
import sys
import asyncio
from datetime import datetime, timezone, timedelta

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from database.connection import (
    db_service, 
    parse_to_utc, 
    format_to_ist, 
    normalize_email_timestamps, 
    get_email_sort_key
)

def test_timestamp_parsing_and_conversion():
    print("=" * 70)
    print("TEST 1: PARSING HETEROGENEOUS DATES & CONVERTING TO UTC/IST")
    print("=" * 70)

    # 1. UTC timestamp: 27 Oct 2026 11:06:44 +0000 (corresponds to 16:36:44 IST)
    dt1 = parse_to_utc("Tue, 27 Oct 2026 11:06:44 +0000")
    assert dt1.tzinfo == timezone.utc
    ist1 = format_to_ist(dt1)
    print(f"[PASS] UTC String -> {ist1}")
    assert "27 Oct 2026" in ist1
    assert "04:36 PM IST" in ist1

    # 2. IST timestamp: 27 Oct 2026 20:31:02 +0530 (corresponds to 15:01:02 UTC)
    dt2 = parse_to_utc("Tue, 27 Oct 2026 20:31:02 +0530")
    ist2 = format_to_ist(dt2)
    print(f"[PASS] IST String -> {ist2}")
    assert "27 Oct 2026" in ist2
    assert "08:31 PM IST" in ist2

    # Verify chronological comparison: dt2 (20:31 IST = 15:01 UTC) is NEWER than dt1 (11:06 UTC)
    assert dt2.timestamp() > dt1.timestamp(), "IST 20:31:02 should be newer than UTC 11:06:44"

    # 3. IST with zone name: Wed, 28 Oct 2026 09:27:19 +0530 (IST)
    dt3 = parse_to_utc("Wed, 28 Oct 2026 09:27:19 +0530 (IST)")
    ist3 = format_to_ist(dt3)
    print(f"[PASS] IST with Zone Name -> {ist3}")
    assert "28 Oct 2026" in ist3
    assert "09:27 AM IST" in ist3

    # 4. Naive SQL string: 2026-10-28 09:53:08 (treated as UTC, corresponds to 15:23:08 IST)
    dt4 = parse_to_utc("2026-10-28 09:53:08")
    ist4 = format_to_ist(dt4)
    print(f"[PASS] Naive String -> {ist4}")
    assert "28 Oct 2026" in ist4
    assert "03:23 PM IST" in ist4

    # 5. ISO string with microseconds: 2026-10-28T09:53:08.041350
    dt5 = parse_to_utc(None, fallback_iso="2026-10-28T09:53:08.041350")
    ist5 = format_to_ist(dt5)
    print(f"[PASS] Microsecond ISO -> {ist5}")
    assert "28 Oct 2026" in ist5

    print("\nAll datetime parsing & IST conversion tests passed!")

async def test_mixed_timezone_sorting():
    print("\n" + "=" * 70)
    print("TEST 2: MIXED TIMEZONE & MULTI-DATE NEWEST-FIRST SORTING")
    print("=" * 70)

    # Construct test emails with mixed UTC and IST timestamps across various dates
    test_batch = [
        {
            "id": "sort-test-old-utc",
            "subject": "Oldest Email (Oct 25, 08:00 UTC)",
            "sender": "sender1@example.com",
            "date": "Sun, 25 Oct 2026 08:00:00 +0000",
            "classification": "SAFE",
            "risk_score": 10
        },
        {
            "id": "sort-test-mid-ist",
            "subject": "Middle Email (Oct 27, 20:30 IST = 15:00 UTC)",
            "sender": "sender2@example.com",
            "date": "Tue, 27 Oct 2026 20:30:00 +0530",
            "classification": "SUSPICIOUS",
            "risk_score": 50
        },
        {
            "id": "sort-test-mid-utc",
            "subject": "Earlier Middle Email (Oct 27, 10:00 UTC = 15:30 IST)",
            "sender": "sender3@example.com",
            "date": "Tue, 27 Oct 2026 10:00:00 +0000",
            "classification": "SAFE",
            "risk_score": 15
        },
        {
            "id": "sort-test-newest-iso",
            "subject": "Newest Email (Oct 28, 12:00 UTC = 17:30 IST)",
            "sender": "sender4@example.com",
            "date": "2026-10-28 12:00:00",
            "classification": "PHISHING",
            "risk_score": 90
        }
    ]

    # Save all test emails into database
    for em in test_batch:
        await db_service.save_email(em)

    # Retrieve sorted emails via get_emails()
    res = await db_service.get_emails(limit=200)
    items = res["items"]

    # Filter to our test batch IDs
    test_items = [it for it in items if it["id"].startswith("sort-test-")]
    
    print(f"Retrieved {len(test_items)} test emails in order:")
    for idx, it in enumerate(test_items, 1):
        print(f"  [{idx}] {it['date_display']} (Epoch: {it['timestamp_epoch']}) | Subj: {it['subject']}")

    # Assert exact chronological order: newest to oldest
    assert test_items[0]["id"] == "sort-test-newest-iso", "Newest email must be first"
    assert test_items[1]["id"] == "sort-test-mid-ist", "Oct 27 20:30 IST (15:00 UTC) must be second"
    assert test_items[2]["id"] == "sort-test-mid-utc", "Oct 27 10:00 UTC must be third"
    assert test_items[3]["id"] == "sort-test-old-utc", "Oct 25 email must be last"

    # Verify pagination preserves newest-first ordering
    page1 = await db_service.get_emails(skip=0, limit=2)
    page2 = await db_service.get_emails(skip=2, limit=2)
    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 2
    assert page1["items"][0]["timestamp_epoch"] >= page1["items"][1]["timestamp_epoch"]
    assert page1["items"][1]["timestamp_epoch"] >= page2["items"][0]["timestamp_epoch"]
    print("\n[PASS] Pagination correctly maintains newest-first timestamp order!")

    # Cleanup test records
    for em in test_batch:
        await db_service.delete_email(em["id"])

    print("=" * 70)
    print("ALL DATETIME SORTING & IST DISPLAY TESTS PASSED (100%)")
    print("=" * 70)

def main():
    test_timestamp_parsing_and_conversion()
    asyncio.run(test_mixed_timezone_sorting())

if __name__ == "__main__":
    main()
