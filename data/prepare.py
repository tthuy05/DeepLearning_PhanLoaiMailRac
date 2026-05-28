import os
import sys
import pandas as pd

# Đảm bảo import từ project root
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from utils.clean_dataset import load_and_clean_vn, merge_datasets


def prepare_data():
    print("=" * 60)
    print("STEP 1: Loading cleaned Spam dataset")
    print("=" * 60)
    
    # Load file đã clean sẵn (KHÔNG clean lại)
    df_en = pd.read_csv("data/spam_clean.csv")
    print(f"Loaded spam_clean.csv: {len(df_en)} rows")

    print("\n" + "=" * 60)
    print("STEP 2: Processing Vietnamese dataset")
    print("=" * 60)
    
    df_vn = load_and_clean_vn("data/dataset_vn.csv")
    print(f"Processed dataset_vn.csv: {len(df_vn)} rows")

    print("\n" + "=" * 60)
    print("STEP 3: Merging datasets")
    print("=" * 60)
    
    df_merged = merge_datasets(df_en, df_vn)

    df_merged = df_merged.drop_duplicates(subset=['clean_text'])

    # Lưu merged dataset
    output_path = "data/spam_clean_merged.csv"
    
    df_save = df_merged[['text', 'label', 'clean_text']]
    df_save.to_csv(output_path, index=False, encoding='utf-8')

    print(f"\nSaved merged dataset to {output_path}")
    print(f"Total rows after merge: {len(df_save)}")

    return df_merged


def main():
    df = prepare_data()
    print("\n" + "=" * 60)
    print("ALL DONE!")
    print("=" * 60)


if __name__ == "__main__":
    main()