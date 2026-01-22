import pandas as pd
import os

file_path = r"d:\Coding\Time_Table_Management_System\Even Sem Faculty & Class Time Table 2025-26 (19-01-2026).xlsx"

def analyze_excel(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    try:
        xl = pd.ExcelFile(path)
        print(f"File: {os.path.basename(path)}")
        print(f"Sheet Names: {xl.sheet_names}")
        print("-" * 40)

        for sheet in xl.sheet_names:
            print(f"\nScanning Sheet: {sheet}")
            try:
                # Read first few rows to guess structure
                df = pd.read_excel(path, sheet_name=sheet, nrows=10)
                print(f"Columns: {list(df.columns)}")
                print("First 3 rows sample:")
                print(df.head(3).to_string())
                print("-" * 20)
            except Exception as e:
                print(f"Error reading sheet {sheet}: {e}")

    except Exception as e:
        print(f"Error opening Excel file: {e}")

if __name__ == "__main__":
    analyze_excel(file_path)
