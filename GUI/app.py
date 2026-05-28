import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

from model.predict_cnn import predict_email as predict_cnn
from model.predict_lr import predict_email as predict_lr
from email_reader.imap_reader import fetch_emails

# Mapping tên hiển thị → hàm predict
MODEL_OPTIONS = {
    "CNN (Deep Learning)": predict_cnn,
    "Logistic Regression (TF-IDF)": predict_lr,
}


class EmailClassifierApp:
    """Giao diện phân loại email Spam/Normal."""

    def __init__(self, root):
        self.root = root
        self.root.title("Email Classification — Spam Detector")
        self.root.geometry("820x620")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        # Style cơ bản
        style = ttk.Style()
        style.theme_use("clam")

        # Cấu hình bỏ viền nét đứt khi focus/click cho Button và Notebook Tab
        style.layout("TButton", [
            ('Button.border', {'sticky': 'nswe', 'border': '1', 'children': [
                ('Button.padding', {'sticky': 'nswe', 'children': [
                    ('Button.label', {'sticky': 'nswe'})
                ]})
            ]})
        ])
        style.layout("TNotebook.Tab", [
            ('Notebook.tab', {'sticky': 'nswe', 'children': [
                ('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [
                    ('Notebook.label', {'side': 'top', 'sticky': ''})
                ]})
            ]})
        ])

        # Tạo notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Tab 1: Nhập tay
        self._build_manual_tab()

        # Tab 2: Đọc từ Gmail
        self._build_gmail_tab()

    # ================================================================
    # TAB 1 — Nhập nội dung email thủ công
    # ================================================================
    def _build_manual_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Nhập Email  ")

        # --- Chọn thuật toán ---
        frm_algo = ttk.LabelFrame(tab, text="Thuật toán phân loại")
        frm_algo.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(frm_algo, text="Chọn thuật toán:").grid(
            row=0, column=0, padx=8, pady=6, sticky=tk.W
        )
        self.cmb_algo = ttk.Combobox(
            frm_algo, values=list(MODEL_OPTIONS.keys()),
            state="readonly", width=30
        )
        self.cmb_algo.grid(row=0, column=1, padx=8, pady=6, sticky=tk.W)
        self.cmb_algo.current(0)
        frm_algo.columnconfigure(1, weight=1)

        # --- Sender ---
        frm_sender = ttk.LabelFrame(tab, text="Thông tin người gửi")
        frm_sender.pack(fill=tk.X, padx=10, pady=(5, 5))

        ttk.Label(frm_sender, text="Email người gửi:").grid(
            row=0, column=0, padx=8, pady=6, sticky=tk.W
        )
        self.entry_sender = ttk.Entry(frm_sender, width=50)
        self.entry_sender.grid(row=0, column=1, padx=8, pady=6, sticky=tk.EW)
        self.entry_sender.insert(0, "example@gmail.com")
        frm_sender.columnconfigure(1, weight=1)

        # --- Nội dung email ---
        frm_content = ttk.LabelFrame(tab, text="Nội dung email")
        frm_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.txt_email = scrolledtext.ScrolledText(
            frm_content, wrap=tk.WORD, height=10, font=("Consolas", 10)
        )
        self.txt_email.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.txt_email.insert(
            tk.END, "Nhập hoặc paste nội dung email vào đây..."
        )
        # Xóa placeholder khi click
        self.txt_email.bind("<FocusIn>", self._clear_placeholder)

        # --- Nút phân loại ---
        frm_btn = ttk.Frame(tab)
        frm_btn.pack(fill=tk.X, padx=10, pady=5)

        self.btn_classify = ttk.Button(
            frm_btn, text="Phân loại", command=self._on_classify
        )
        self.btn_classify.pack(side=tk.LEFT, padx=5)

        self.btn_clear = ttk.Button(
            frm_btn, text="Xóa", command=self._on_clear
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        self.lbl_status = ttk.Label(frm_btn, text="")
        self.lbl_status.pack(side=tk.LEFT, padx=15)

        # --- Kết quả ---
        frm_result = ttk.LabelFrame(tab, text="Kết quả phân loại")
        frm_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.txt_result = scrolledtext.ScrolledText(
            frm_result, wrap=tk.WORD, height=8, font=("Consolas", 10),
            state=tk.DISABLED, bg="#fafafa"
        )
        self.txt_result.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Cấu hình tag màu cho kết quả
        self.txt_result.tag_configure("spam", foreground="#d32f2f", font=("Consolas", 11, "bold"))
        self.txt_result.tag_configure("normal", foreground="#388e3c", font=("Consolas", 11, "bold"))
        self.txt_result.tag_configure("info", foreground="#555555")

    def _clear_placeholder(self, event):
        content = self.txt_email.get("1.0", tk.END).strip()
        if content == "Nhập hoặc paste nội dung email vào đây...":
            self.txt_email.delete("1.0", tk.END)

    def _on_classify(self):
        text = self.txt_email.get("1.0", tk.END).strip()
        sender = self.entry_sender.get().strip()

        if not text or text == "Nhập hoặc paste nội dung email vào đây...":
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập nội dung email.")
            return

        self.btn_classify.config(state=tk.DISABLED)
        self.lbl_status.config(text="Đang phân loại...")

        # Lấy hàm predict theo thuật toán được chọn
        algo_name = self.cmb_algo.get()
        predict_fn = MODEL_OPTIONS.get(algo_name, predict_cnn)

        # Chạy predict trên thread riêng để GUI không bị đơ
        def _predict():
            try:
                result = predict_fn(
                    text=text,
                    sender_email=sender if sender else None,
                    use_rules=True
                )
                self.root.after(0, lambda: self._show_result(result))
            except Exception as e:
                err_msg = str(e)
                self.root.after(
                    0,
                    lambda msg=err_msg: messagebox.showerror("Lỗi", f"Không thể phân loại:\n{msg}")
                )
            finally:
                self.root.after(0, lambda: self.btn_classify.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.lbl_status.config(text=""))

        threading.Thread(target=_predict, daemon=True).start()

    def _show_result(self, result):
        """Hiển thị kết quả phân loại lên ô kết quả."""
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete("1.0", tk.END)

        label = result["label"]
        tag = "spam" if label == "Spam" else "normal"

        self.txt_result.insert(tk.END, f"  Kết quả: {label}\n", tag)
        self.txt_result.insert(tk.END, f"  Độ tin cậy: {result['confidence']:.1%}\n", "info")
        self.txt_result.insert(tk.END, f"  Phương pháp: {result['method']}\n", "info")

        if result.get("matched_rules"):
            self.txt_result.insert(tk.END, f"\n  Rules khớp:\n", "info")
            for rule in result["matched_rules"]:
                name = rule.get("group_name", "")
                kws = ", ".join(rule.get("matched_keywords", [])[:3])
                self.txt_result.insert(tk.END, f"    - {name}: {kws}\n", "info")

        if result.get("spam_score", 0) > 0:
            self.txt_result.insert(
                tk.END, f"\n  Spam score: {result['spam_score']:.1f}\n", "info"
            )

        if result.get("details"):
            self.txt_result.insert(tk.END, f"\n  Chi tiết: {result['details']}\n", "info")

        self.txt_result.config(state=tk.DISABLED)

    def _on_clear(self):
        self.txt_email.delete("1.0", tk.END)
        self.entry_sender.delete(0, tk.END)
        self.entry_sender.insert(0, "example@gmail.com")
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.config(state=tk.DISABLED)
        self.lbl_status.config(text="")

    # ================================================================
    # TAB 2 — Đọc email từ Gmail qua IMAP
    # ================================================================
    def _build_gmail_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Gmail IMAP  ")

        # --- Đăng nhập ---
        frm_login = ttk.LabelFrame(tab, text="Đăng nhập Gmail (IMAP)")
        frm_login.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(frm_login, text="Email:").grid(row=0, column=0, padx=8, pady=4, sticky=tk.W)
        self.entry_gmail = ttk.Entry(frm_login, width=35)
        self.entry_gmail.grid(row=0, column=1, padx=8, pady=4, sticky=tk.EW)

        ttk.Label(frm_login, text="App Password:").grid(row=1, column=0, padx=8, pady=4, sticky=tk.W)
        self.entry_password = ttk.Entry(frm_login, width=35, show="*")
        self.entry_password.grid(row=1, column=1, padx=8, pady=4, sticky=tk.EW)

        ttk.Label(frm_login, text="Số email lấy:").grid(row=2, column=0, padx=8, pady=4, sticky=tk.W)
        self.spin_count = ttk.Spinbox(frm_login, from_=1, to=20, width=5)
        self.spin_count.grid(row=2, column=1, padx=8, pady=4, sticky=tk.W)
        self.spin_count.set(5)

        ttk.Label(frm_login, text="Thuật toán:").grid(row=3, column=0, padx=8, pady=4, sticky=tk.W)
        self.cmb_gmail_algo = ttk.Combobox(
            frm_login, values=list(MODEL_OPTIONS.keys()),
            state="readonly", width=30
        )
        self.cmb_gmail_algo.grid(row=3, column=1, padx=8, pady=4, sticky=tk.W)
        self.cmb_gmail_algo.current(0)

        frm_login.columnconfigure(1, weight=1)

        frm_gmail_btn = ttk.Frame(tab)
        frm_gmail_btn.pack(fill=tk.X, padx=10, pady=5)

        self.btn_fetch = ttk.Button(
            frm_gmail_btn, text="Lấy email & Phân loại",
            command=self._on_fetch_gmail
        )
        self.btn_fetch.pack(side=tk.LEFT, padx=5)

        self.lbl_gmail_status = ttk.Label(frm_gmail_btn, text="")
        self.lbl_gmail_status.pack(side=tk.LEFT, padx=15)

        # --- Tip ---
        ttk.Label(
            tab,
            text="Lưu ý: Cần bật 2-Step Verification và dùng App Password (không phải mật khẩu thường).",
            foreground="#888888", font=("Segoe UI", 8)
        ).pack(padx=12, pady=(0, 3), anchor=tk.W)

        # --- Kết quả ---
        frm_gmail_result = ttk.LabelFrame(tab, text="Kết quả")
        frm_gmail_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.txt_gmail_result = scrolledtext.ScrolledText(
            frm_gmail_result, wrap=tk.WORD, height=12, font=("Consolas", 10),
            state=tk.DISABLED, bg="#fafafa"
        )
        self.txt_gmail_result.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.txt_gmail_result.tag_configure("spam", foreground="#d32f2f", font=("Consolas", 10, "bold"))
        self.txt_gmail_result.tag_configure("normal", foreground="#388e3c", font=("Consolas", 10, "bold"))
        self.txt_gmail_result.tag_configure("header", foreground="#1565c0", font=("Consolas", 10, "bold"))
        self.txt_gmail_result.tag_configure("info", foreground="#555555")

    def _on_fetch_gmail(self):
        email_addr = self.entry_gmail.get().strip()
        password = self.entry_password.get().strip()

        if not email_addr or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập email và app password.")
            return

        try:
            count = int(self.spin_count.get())
        except ValueError:
            count = 5

        self.btn_fetch.config(state=tk.DISABLED)
        self.lbl_gmail_status.config(text="Đang kết nối Gmail...")

        # Lấy hàm predict theo thuật toán được chọn
        algo_name = self.cmb_gmail_algo.get()
        predict_fn = MODEL_OPTIONS.get(algo_name, predict_cnn)

        def _fetch_and_classify():
            try:
                emails = fetch_emails(email_addr, password, count=count)
                results = []
                for i, em in enumerate(emails):
                    # Ghép subject + body để predict
                    full_text = f"{em.get('subject', '')}\n{em.get('body', '')}"
                    pred = predict_fn(
                        text=full_text,
                        sender_email=em.get("sender", ""),
                        use_rules=True
                    )
                    results.append((em, pred))

                self.root.after(0, lambda: self._show_gmail_results(results))
            except Exception as e:
                err_msg = str(e)
                self.root.after(
                    0,
                    lambda msg=err_msg: messagebox.showerror("Lỗi kết nối", f"Không thể lấy email:\n{msg}")
                )
            finally:
                self.root.after(0, lambda: self.btn_fetch.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.lbl_gmail_status.config(text=""))

        threading.Thread(target=_fetch_and_classify, daemon=True).start()

    def _show_gmail_results(self, results):
        """Hiển thị kết quả phân loại các email từ Gmail."""
        self.txt_gmail_result.config(state=tk.NORMAL)
        self.txt_gmail_result.delete("1.0", tk.END)

        if not results:
            self.txt_gmail_result.insert(tk.END, "Không tìm thấy email nào.\n")
            self.txt_gmail_result.config(state=tk.DISABLED)
            return

        spam_count = sum(1 for _, r in results if r["label"] == "Spam")
        normal_count = len(results) - spam_count

        self.txt_gmail_result.insert(
            tk.END,
            f"Tổng: {len(results)} email  |  Normal: {normal_count}  |  Spam: {spam_count}\n",
            "header"
        )
        self.txt_gmail_result.insert(tk.END, "=" * 60 + "\n\n")

        for i, (em, pred) in enumerate(results, 1):
            label = pred["label"]
            tag = "spam" if label == "Spam" else "normal"

            self.txt_gmail_result.insert(tk.END, f"--- Email {i} ---\n", "header")
            self.txt_gmail_result.insert(
                tk.END, f"  Từ: {em.get('sender', 'N/A')}\n", "info"
            )
            self.txt_gmail_result.insert(
                tk.END, f"  Tiêu đề: {em.get('subject', '(không có)')}\n", "info"
            )
            self.txt_gmail_result.insert(tk.END, f"  Phân loại: {label}", tag)
            self.txt_gmail_result.insert(
                tk.END, f"  ({pred['confidence']:.1%} — {pred['method']})\n\n", "info"
            )

        self.txt_gmail_result.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = EmailClassifierApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
