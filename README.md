# 📧 Email Classification — Spam Detector

Đồ án phân loại email **Normal / Spam** sử dụng **CNN (Deep Learning)**, **Logistic Regression (TF-IDF)** và **Rule-Based Detection**.

## 📁 Cấu trúc dự án

```
EmailClassification/
├── main.py                     # Entry point — khởi chạy GUI
├── test.py                     # Test phân loại với email mẫu
├── requirements.txt            # Danh sách thư viện
├── data/
│   ├── spam_assassin.csv       # Dataset gốc (Spam Assassin)
│   ├── spam_clean.csv          # Dataset đã tiền xử lý
│   ├── spam_clean_merged.csv   # Dataset merged (EN + VN)
│   ├── dataset_vn.csv          # Dataset tiếng Việt
│   ├── dataset_vn.py           # Script tạo dataset VN
│   └── prepare.py              # Script merge datasets
├── model/
│   ├── train_cnn.py            # Huấn luyện model CNN
│   ├── train_lr.py             # Huấn luyện model Logistic Regression
│   ├── predict_cnn.py          # Hàm phân loại bằng CNN
│   ├── predict_lr.py           # Hàm phân loại bằng Logistic Regression
│   ├── cnn_model.h5            # Model CNN đã huấn luyện
│   ├── tokenizer.pkl           # Tokenizer cho CNN
│   ├── lr_model.pkl            # Model LR đã huấn luyện
│   └── tfidf_vectorizer.pkl    # TF-IDF Vectorizer cho LR
├── rules/
│   ├── rule_engine.py          # Bộ phát hiện spam/phishing dựa trên rules
│   └── vietnam_spam_rules.py   # Rules phát hiện spam tiếng Việt
├── GUI/
│   └── app.py                  # Giao diện Tkinter
├── email_reader/
│   └── imap_reader.py          # Đọc email từ Gmail qua IMAP
├── utils/
│   ├── preprocess.py           # Tiền xử lý text
│   ├── clean_dataset.py        # Làm sạch dataset
│   ├── save_clean_data.py      # Lưu dataset đã clean
│   └── logger.py               # Logging utility
└── logs/
    ├── train.log               # Log huấn luyện
    ├── fit/                    # TensorBoard logs
    └── charts/                 # Biểu đồ training
```

## 🔧 Cài đặt

```bash
# Cài đặt thư viện
pip install -r requirements.txt
```

## 🚀 Sử dụng

### 1. Tiền xử lý dataset (nếu chưa có `spam_clean.csv`)
```bash
python -m utils.save_clean_data
```

### 2. Merge dataset (EN + VN)
```bash
python -m data.prepare
```

### 3. Huấn luyện model CNN
```bash
python -m model.train_cnn
```

### 4. Huấn luyện model Logistic Regression
```bash
python -m model.train_lr
```

### 5. Chạy GUI
```bash
python main.py
```

### 6. Test nhanh qua CLI
```bash
python test.py
```

## 📊 Kết quả

### CNN (Deep Learning)
- **Model**: Embedding → Conv1D → GlobalMaxPooling1D → Dense → Dropout → Sigmoid
- **Accuracy**: ~99%

### Logistic Regression (TF-IDF)
- **Model**: TF-IDF Vectorizer + Logistic Regression
- **Accuracy**: ~98.8%
- **ROC-AUC**: ~99.9%

### Rule-Based Detection
- Whitelist domain/sender đáng tin cậy
- Keyword matching theo nhóm (có trọng số)
- Suspicious domain/sender pattern detection
- Hỗ trợ nhận diện spam tiếng Việt

## 🎯 Thuật toán phân loại

Giao diện cho phép chọn thuật toán:
1. **CNN (Deep Learning)** — Mạng nơ-ron tích chập
2. **Logistic Regression (TF-IDF)** — Hồi quy logistic với TF-IDF

Quy trình phân loại: Rule-based check trước → Model AI sau (nếu rules không đủ evidence).

## 🔑 Lưu ý sử dụng Gmail IMAP

Để đọc email từ Gmail, bạn cần:

1. Bật **2-Step Verification** trong cài đặt Google Account
2. Tạo **App Password** tại: https://myaccount.google.com/apppasswords
3. Sử dụng App Password (không phải mật khẩu thường) trong GUI

## 🛠 Công nghệ

- **Python 3.10+**
- **TensorFlow/Keras** — Mô hình CNN
- **scikit-learn** — Logistic Regression, đánh giá model
- **NLTK** — Tiền xử lý ngôn ngữ tự nhiên
- **Tkinter** — Giao diện người dùng
- **imaplib** — Đọc email qua IMAP
- **Matplotlib** — Biểu đồ training
