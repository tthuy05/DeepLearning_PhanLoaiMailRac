import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from model.predict_cnn import predict_email

def run_test():
    test_cases = [
        # ===== Spam (English) =====
        {
            "text": "Win a FREE iPhone now!!! Click here to claim your prize",
            "sender": "promo@randomspam.com"
        },

        # ===== Spam (Vietnamese) =====
        {
            "text": "Chúc mừng bạn đã trúng thưởng 1 chiếc xe SH! Nhấn link để nhận ngay!!!",
            "sender": "khuyenmai@trungthuong.vn"
        },
        {
            "text": "Tài khoản của bạn bị khóa, vui lòng xác minh ngay lập tức để tránh bị xóa.",
            "sender": "security@fakebank.vn"
        },
        {
            "text": "Vay tiền nhanh lãi suất thấp, không cần thế chấp, đăng ký ngay!",
            "sender": "vaynhanh@loan247.vn"
        },

        # ===== Normal (Vietnamese Gmail) =====
        {
            "text": "Ê tối nay đi ăn không?",
            "sender": "tuanle123@gmail.com"
        },
        {
            "text": "Mai nhớ nộp bài deadline môn Deep Learning nha",
            "sender": "classmate@gmail.com"
        },
        {
            "text": "Anh gửi em tài liệu học tập, check giúp anh nhé",
            "sender": "giangvien@gmail.com"
        },

        # ===== Mixed =====
        {
            "text": "Hello, bạn đã nhận được tài liệu chưa?",
            "sender": "friend@gmail.com"
        },
        {
            "text": "Click ngay để nhận ưu đãi cực lớn!!!",
            "sender": "ads@marketing.vn"
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i} ===")
        result = predict_email(
            text=case["text"],
            sender_email=case["sender"],
            use_rules=True
        )

        print(f"Text: {case['text']}")
        print(f"Sender: {case['sender']}")
        print(f"Label: {result['label']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Display: {result['display']}")
        print(f"Method: {result['method']}")
        print(f"Matched Rules: {result['matched_rules']}")
        print(f"Spam Score: {result['spam_score']}")
        print(f"Details: {result['details']}")


if __name__ == "__main__":
    run_test()