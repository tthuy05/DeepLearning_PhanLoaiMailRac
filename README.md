# 📧 Email Classification — Spam Detector

Đồ án phân loại email **Normal / Spam** sử dụng mạng nơ-ron tích chập **CNN (Deep Learning)** kết hợp công cụ phát hiện dựa trên luật **Rule-Based Detection**.

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
│   ├── train_cnn.py            # Huấn luyện mô hình CNN
│   ├── predict_cnn.py          # Hàm phân loại bằng CNN
│   ├── cnn_model.h5            # Mô hình CNN đã huấn luyện
│   └── tokenizer.pkl           # Tokenizer cho mô hình CNN
├── rules/
│   ├── rule_engine.py          # Bộ phát hiện spam/phishing dựa trên rules
│   └── vietnam_spam_rules.py   # Rules phát hiện spam tiếng Việt
├── GUI/
│   └── app.py                  # Giao diện Tkinter (chỉ dùng CNN)
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

### 3. Huấn luyện mô hình CNN
```bash
python -m model.train_cnn
```

### 4. Chạy giao diện chính (GUI)
```bash
python main.py
```

### 5. Kiểm thử nhanh bằng dòng lệnh
```bash
python test.py
```

## 📊 Kết quả mô hình CNN
- **Kiến trúc mạng**: Embedding → Conv1D → GlobalMaxPooling1D → Dense (ReLU) → Dropout → Dense (Sigmoid)
- **Độ chính xác (Accuracy)**: Đạt khoảng ~99% trên tập kiểm thử
- **Ưu điểm**: Khả năng phân tích ngữ cảnh từ ngữ thông qua lớp chập 1 chiều (Conv1D) cực kỳ mạnh mẽ, rất phù hợp cho xử lý ngôn ngữ tự nhiên.

## 🎯 Quy trình phân loại email
Để tối ưu hóa thời gian và độ chính xác, ứng dụng hoạt động theo cơ chế lai (Hybrid):
1. **Rule-Based Check (Kiểm tra theo luật)**:
   * Kiểm tra Whitelist người gửi đáng tin cậy.
   * Lọc từ khóa spam tiếng Việt theo nhóm trọng số nhạy cảm.
   * Nếu phát hiện khớp tuyệt đối các bộ luật này, hệ thống sẽ trả về kết quả ngay lập tức để tiết kiệm chi phí tính toán.
2. **CNN Model Predict (Phân loại mạng nơ-ron)**:
   * Nếu email không vi phạm bất kỳ luật cứng nào, hệ thống sẽ đẩy nội dung văn bản qua bộ tokenizer và đưa vào mô hình Deep Learning CNN để tính toán xác suất Spam.

## 🔑 Lưu ý sử dụng Gmail IMAP

Để đọc email từ Gmail của bạn trực tiếp trên ứng dụng, vui lòng thực hiện:

1. Bật **Xác minh 2 bước (2-Step Verification)** trong cài đặt Tài khoản Google của bạn.
2. Tạo một **Mật khẩu ứng dụng (App Password)** tại: https://myaccount.google.com/apppasswords
3. Sử dụng Mật khẩu ứng dụng vừa tạo (16 ký tự viết liền) để đăng nhập trong giao diện GUI.

## 🛠 Công nghệ sử dụng

- **Python 3.10+**
- **TensorFlow/Keras** — Xây dựng và huấn luyện mô hình CNN
- **scikit-learn** — Hỗ trợ chia tập dữ liệu và đánh giá mô hình
- **NLTK** — Tiền xử lý dữ liệu ngôn ngữ tự nhiên
- **Tkinter** — Lập trình giao diện người dùng trực quan
- **imaplib** — Kết nối cổng IMAP đọc email Gmail an toàn
- **Matplotlib** — Biểu thị quá trình huấn luyện mô hình học sâu
