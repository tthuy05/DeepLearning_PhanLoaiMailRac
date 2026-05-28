import numpy as np
import pandas as pd
import pickle
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend, lưu chart thay vì show
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, TensorBoard

import os
import datetime
from utils.logger import setup_logger

logger = setup_logger()

MAX_WORDS = 10000
MAX_LEN = 200
MODEL_PATH = "model/cnn_model.h5"
TOKENIZER_PATH = "model/tokenizer.pkl"


def train():
    logger.info("Loading cleaned dataset...")
    df = pd.read_csv("data/spam_clean_merged.csv")

    # Kiểm tra cột cần thiết
    for col in ['clean_text', 'label']:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in dataset.")
    df = df.dropna(subset=['clean_text', 'label'])

    texts = df['clean_text']
    labels = df['label']  # 0 = Normal (ham), 1 = Spam

    logger.info(f"Dataset size: {len(df)}")
    logger.info(f"Label distribution:\n{labels.value_counts().to_string()}")

    # Tokenization
    tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)

    sequences = tokenizer.texts_to_sequences(texts)
    X = pad_sequences(sequences, maxlen=MAX_LEN)
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # =====================
    # CNN Model (2-class)
    # =====================
    model = Sequential([
        Embedding(MAX_WORDS, 128, input_length=MAX_LEN),
        Conv1D(128, 5, activation='relu'),
        GlobalMaxPooling1D(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')  # Binary classification
    ])

    model.compile(
        loss='binary_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    model.summary(print_fn=logger.info)

    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard = TensorBoard(log_dir=log_dir)

    logger.info("Start training...")

    history = model.fit(
        X_train, y_train,
        epochs=10,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stop, tensorboard]
    )

    # =====================
    # Evaluation
    # =====================
    y_pred = (model.predict(X_test) > 0.5).astype(int).flatten()

    logger.info("\n=== CLASSIFICATION REPORT ===")
    report = classification_report(y_test, y_pred, target_names=['Normal', 'Spam'])
    logger.info("\n" + report)

    logger.info("\n=== CONFUSION MATRIX ===")
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"\n{cm}")

    # =====================
    # Save model & tokenizer
    # =====================
    model.save(MODEL_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")

    with open(TOKENIZER_PATH, "wb") as f:
        pickle.dump(tokenizer, f)
    logger.info(f"Tokenizer saved to {TOKENIZER_PATH}")

    # =====================
    # Save charts
    # =====================
    os.makedirs("logs/charts", exist_ok=True)

    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.legend()
    plt.title("Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")

    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Val Accuracy')
    plt.legend()
    plt.title("Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")

    plt.tight_layout()
    chart_path = "logs/charts/training_history.png"
    plt.savefig(chart_path, dpi=150)
    plt.close()
    logger.info(f"Training charts saved to {chart_path}")

    logger.info("Training complete!")


if __name__ == "__main__":
    train()