"""
Đọc email từ Gmail qua IMAP.

Yêu cầu:
  - Bật 2-Step Verification trên Google Account
  - Tạo App Password tại: https://myaccount.google.com/apppasswords
  - Dùng App Password thay cho mật khẩu thường
"""

import imaplib
import email
from email.header import decode_header
import re


def _decode_mime_header(header_value):
    """Decode MIME encoded header (subject, sender name, ...)."""
    if not header_value:
        return ""

    decoded_parts = decode_header(header_value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or "utf-8", errors="replace"))
            except (LookupError, UnicodeDecodeError):
                result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def _extract_body(msg):
    """
    Trích xuất nội dung text từ email message.
    Ưu tiên text/plain, fallback sang text/html (strip tags).
    """
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            # Bỏ qua attachment
            if part.get("Content-Disposition") is not None:
                continue

            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                charset = part.get_content_charset() or "utf-8"
                text = payload.decode(charset, errors="replace")
            except Exception:
                continue

            if content_type == "text/plain":
                body = text
                break  # Ưu tiên plain text
            elif content_type == "text/html" and not body:
                # Strip HTML tags đơn giản
                body = re.sub(r"<[^>]+>", " ", text)
                body = re.sub(r"\s+", " ", body).strip()
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or "utf-8"
            body = payload.decode(charset, errors="replace")

            if msg.get_content_type() == "text/html":
                body = re.sub(r"<[^>]+>", " ", body)
                body = re.sub(r"\s+", " ", body).strip()
        except Exception:
            body = ""

    # Giới hạn độ dài body để tránh quá nặng khi predict
    max_chars = 2000
    if len(body) > max_chars:
        body = body[:max_chars] + "..."

    return body.strip()


def _extract_sender_email(from_header):
    """Trích xuất email address từ header From."""
    if not from_header:
        return ""
    # Tìm pattern <email@domain.com>
    match = re.search(r"<([^>]+)>", from_header)
    if match:
        return match.group(1)
    # Nếu không có <>, thử lấy trực tiếp
    match = re.search(r"[\w.+-]+@[\w.-]+", from_header)
    if match:
        return match.group(0)
    return from_header


def fetch_emails(email_address, app_password, count=5, folder="INBOX"):
    """
    Kết nối Gmail IMAP và lấy N email mới nhất.

    Args:
        email_address: Địa chỉ Gmail
        app_password: App Password (16 ký tự, không dùng mật khẩu thường)
        count: Số email cần lấy (mặc định 5)
        folder: Thư mục email (mặc định INBOX)

    Returns:
        list of dict, mỗi dict gồm:
            - sender: email người gửi
            - sender_name: tên hiển thị
            - subject: tiêu đề
            - body: nội dung text
            - date: ngày gửi
    """
    results = []

    # Kết nối IMAP SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)

    try:
        imap.login(email_address, app_password)
        imap.select(folder, readonly=True)

        # Tìm tất cả email trong folder
        status, messages = imap.search(None, "ALL")
        if status != "OK":
            return results

        mail_ids = messages[0].split()
        if not mail_ids:
            return results

        # Lấy N email mới nhất (cuối list = mới nhất)
        latest_ids = mail_ids[-count:]
        latest_ids.reverse()  # Mới nhất lên đầu

        for mid in latest_ids:
            status, msg_data = imap.fetch(mid, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode header fields
            from_raw = _decode_mime_header(msg.get("From", ""))
            subject = _decode_mime_header(msg.get("Subject", ""))
            date_str = msg.get("Date", "")

            sender_email = _extract_sender_email(from_raw)
            body = _extract_body(msg)

            results.append({
                "sender": sender_email,
                "sender_name": from_raw,
                "subject": subject,
                "body": body,
                "date": date_str,
            })

    finally:
        try:
            imap.logout()
        except Exception:
            pass

    return results
