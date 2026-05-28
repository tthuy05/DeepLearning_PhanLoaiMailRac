import sys
import os

# Chạy GUI từ thư mục gốc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from GUI.app import main

if __name__ == "__main__":
    main()