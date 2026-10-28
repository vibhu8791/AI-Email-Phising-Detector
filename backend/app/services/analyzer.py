import os
import sys
import logging
from typing import Dict, Any, Optional
import joblib

logger = logging.getLogger("app.analyzer")

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from ml_model.feature_extractor import extract_heuristic_features, preprocess_email_text

class PhishingAnalyzer:
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.is_loaded = False
        self._load_models()

    def _load_models(self):
        saved_dir = os.path.join(root_dir, "ml_model", "saved_models")
        vec_path = os.path.join(saved_dir, "tfidf_vectorizer.joblib")
        model_path = os.path.join(saved_dir, "phishing_model.joblib")

        # If not present yet, train them automatically
        if not os.path.exists(vec_path) or not os.path.exists(model_path):
            try:
                logger.info("ML model artifacts not found. Training model automatically...")
                from ml_model.train_model import train_and_save
                train_and_save()
            except Exception as e:
                logger.error(f"Failed to auto-train model: {e}")
                return

        try:
            self.vectorizer = joblib.load(vec_path)
            self.model = joblib.load(model_path)
            self.is_loaded = True
            logger.info("Successfully loaded TF-IDF Vectorizer and Logistic Regression Model.")
        except Exception as e:
            logger.error(f"Error loading model artifacts: {e}")
            self.is_loaded = False

    def predict_ml_probability(self, text: str) -> float:
        """Return probability (0.0 - 1.0) of text being a phishing email."""
        if not self.is_loaded or self.vectorizer is None or self.model is None:
            # Fallback heuristic probability if model loading failed
            return 0.5
        try:
            vec = self.vectorizer.transform([text])
            # Dynamically resolve index for class 1 (phishing)
            phish_idx = list(self.model.classes_).index(1) if hasattr(self.model, 'classes_') else 1
            prob = float(self.model.predict_proba(vec)[0][phish_idx])
            return prob
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 0.5

    def analyze(self, subject: str, sender: str, body: str, recipient: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive Phishing Analysis Pipeline.
        Combines Scikit-learn ML probability with rule-based heuristic signals.
        Returns risk score (0-100), classification, and threat explanation.
        """
        subject = subject or ""
        sender = sender or ""
        body = body or ""

        # 1. Scikit-learn TF-IDF + Calibrated Linear SVM / Logistic Regression
        # Use identical unified preprocessing pipeline as used during training
        preprocessed_text = preprocess_email_text(subject, sender, body)
        ml_prob = self.predict_ml_probability(preprocessed_text)

        # 2. Heuristic & Rule-Based Feature Analysis
        heuristic_res = extract_heuristic_features(subject, sender, body)
        heuristic_score = heuristic_res["heuristic_score"]
        detected_flags = list(heuristic_res["detected_flags"])

        # 3. Phishing Risk Score Calculation (0 - 100)
        # Balanced Alignment: 70% weight from ML Model, 30% weight from Heuristics
        base_score = (ml_prob * 70.0) + (heuristic_score * 0.30)

        # High-threat heuristic boost (e.g. raw IP domain or severe sender spoofing)
        if any("raw IP address" in flag for flag in detected_flags):
            base_score = max(base_score, 85.0)
        if any("Sender domain mismatch" in flag for flag in detected_flags):
            base_score = max(base_score, 75.0)

        # Calibrate & clamp
        final_risk = int(round(min(100.0, max(0.0, base_score))))

        # 4. Multi-tier classification: SAFE (0-35), SUSPICIOUS (36-69), PHISHING (70-100)
        if final_risk >= 70:
            classification = "PHISHING"
            if not detected_flags:
                detected_flags.append("AI Model detected strong linguistic and structural patterns typical of phishing campaigns.")
        elif final_risk >= 36:
            classification = "SUSPICIOUS"
            if not detected_flags:
                detected_flags.append("Unusual communication patterns or moderate risk indicators detected.")
        else:
            classification = "SAFE"
            if not detected_flags:
                detected_flags.append("No significant phishing indicators or anomalous links identified.")

        return {
            "ml_phishing_probability": round(ml_prob, 3),
            "heuristic_score": round(heuristic_score, 1),
            "risk_score": final_risk,
            "classification": classification,
            "detected_flags": detected_flags,
            "keyword_matches": heuristic_res["keyword_matches"],
            "extracted_urls": heuristic_res["extracted_urls"],
            "url_details": heuristic_res["url_analyses"]
        }

analyzer = PhishingAnalyzer()
