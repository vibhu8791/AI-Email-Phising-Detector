import os
import sys

# Ensure root directory is on sys.path so ml_model can be imported seamlessly
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from ml_model.feature_extractor import (
    extract_urls,
    analyze_url,
    extract_heuristic_features,
    SUSPICIOUS_KEYWORDS,
    SUSPICIOUS_TLDS,
    URL_SHORTENERS
)

__all__ = [
    "extract_urls",
    "analyze_url",
    "extract_heuristic_features",
    "SUSPICIOUS_KEYWORDS",
    "SUSPICIOUS_TLDS",
    "URL_SHORTENERS"
]
