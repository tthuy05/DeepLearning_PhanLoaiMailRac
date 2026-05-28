import pickle
from utils.preprocess import clean_text
from rules.rule_engine import get_engine

MODEL_PATH = "model/lr_model.pkl"
VECTORIZER_PATH = "model/tfidf_vectorizer.pkl"

# Lazy loading — chỉ load khi cần
_model = None
_vectorizer = None


def _load_model():
    """Load model LR và TF-IDF vectorizer nếu chưa load."""
    global _model, _vectorizer
    if _model is None:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        # Fix tương thích scikit-learn mới: attribute đã bị loại bỏ
        if not hasattr(_model, "multi_class"):
            _model.multi_class = "auto"
    if _vectorizer is None:
        with open(VECTORIZER_PATH, "rb") as f:
            _vectorizer = pickle.load(f)


def predict_email(text, sender_email=None, use_rules=True):
    """
    Phân loại email: Normal hoặc Spam bằng Logistic Regression.
    Kết hợp rule-based check (nếu có sender info) + LR model.

    Args:
        text: Nội dung email (subject + body)
        sender_email: Địa chỉ email người gửi (optional)
        use_rules: Có dùng rule-based check trước không (default: True)

    Returns: dict với keys:
        - label: "Spam" / "Normal"
        - confidence: float (0-1)
        - display: str hiển thị
        - method: "rule_whitelist" / "rule_keyword" / "model_lr"
        - matched_rules: list (nếu dùng rules)
        - spam_score: float (nếu dùng rules)
    """
    # ─── Step 1: Rule-based check ───
    if use_rules:
        engine = get_engine()

        # Tách subject từ text nếu có
        parts = text.split("\n", 1)
        subject = parts[0] if len(parts) > 1 else ""
        body = parts[1] if len(parts) > 1 else text

        rule_result = engine.classify(
            subject=subject,
            body=body,
            sender_email=sender_email or "",
        )

        # Nếu rule đã quyết định → trả về luôn
        if rule_result["label"] is not None:
            return {
                "label": rule_result["label"],
                "confidence": rule_result["confidence"],
                "display": f"{rule_result['label']} ({rule_result['confidence']:.1%})",
                "method": rule_result["method"],
                "matched_rules": rule_result["matched_rules"],
                "spam_score": rule_result["spam_score"],
                "details": rule_result["details"],
            }

    # ─── Step 2: Fallback sang LR model ───
    _load_model()

    clean = clean_text(text)
    X = _vectorizer.transform([clean])

    prob = _model.predict_proba(X)[0]  # [prob_normal, prob_spam]
    spam_prob = prob[1]

    if spam_prob > 0.5:
        label = "Spam"
        confidence = spam_prob
    else:
        label = "Normal"
        confidence = 1 - spam_prob

    return {
        "label": label,
        "confidence": float(confidence),
        "display": f"{label} ({confidence:.1%})",
        "method": "model_lr",
        "matched_rules": [],
        "spam_score": 0.0,
        "details": "Phân loại bằng Logistic Regression (TF-IDF).",
    }
