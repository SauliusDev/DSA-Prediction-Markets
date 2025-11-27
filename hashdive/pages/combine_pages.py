import pandas as pd
import os
from pathlib import Path

def combine_csv_files(input_folder, output_file):
    input_path = Path(input_folder)
    
    csv_files = sorted(input_path.glob('page_*.csv'), key=lambda x: int(x.stem.split('_')[1]))
    
    if not csv_files:
        print(f"No CSV files found in {input_folder}")
        return
    
    print(f"Found {len(csv_files)} CSV files to combine")
    
    dataframes = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            dataframes.append(df)
            print(f"Loaded {csv_file.name}: {len(df)} rows")
        except Exception as e:
            print(f"Error loading {csv_file.name}: {e}")
    
    if not dataframes:
        print("No dataframes to combine")
        return
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    combined_df.to_csv(output_file, index=False)
    
    print(f"\nCombined {len(dataframes)} files into {output_file}")
    print(f"Total rows: {len(combined_df)}")
    print(f"Columns: {list(combined_df.columns)}")

if __name__ == "__main__":
    input_folder = "pages/21-99ss"
    output_file = "pages/combined_21-99ss.csv"
    
    combine_csv_files(input_folder, output_file)

