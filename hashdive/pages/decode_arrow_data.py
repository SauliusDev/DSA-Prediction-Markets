import json
import base64
import pyarrow as pa
import pandas as pd
from pathlib import Path

def decode_arrow_from_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    arrow_data = data.get('delta', {}).get('newElement', {}).get('arrowDataFrame', {})
    
    if not arrow_data:
        print(f"No arrowDataFrame found in {json_file}")
        return None
    
    base64_data = arrow_data.get('data', '')
    if not base64_data:
        print(f"No data field found in {json_file}")
        return None
    
    binary_data = base64.b64decode(base64_data)
    
    reader = pa.ipc.open_stream(binary_data)
    table = reader.read_all()
    
    df = table.to_pandas()
    
    return df

def process_all_responses(temp_dir='temp'):
    temp_path = Path(temp_dir)
    
    all_dataframes = {}
    
    for json_file in sorted(temp_path.glob('response*.json')):
        try:
            df = decode_arrow_from_json(json_file)
            if df is not None:
                all_dataframes[json_file.name] = df
                print(f"\n{json_file.name}:")
                print(f"  Shape: {df.shape}")
                print(f"  Columns: {list(df.columns)}")
                
                output_csv = temp_path / f"{json_file.stem}_decoded.csv"
                df.to_csv(output_csv, index=False)
                print(f"  Saved to: {output_csv}")
                
        except Exception as e:
            pass
    
    return all_dataframes

if __name__ == "__main__":
    dataframes = process_all_responses()
    
    print(f"\n\nTotal dataframes decoded: {len(dataframes)}")
    
    if 'response34.json' in dataframes:
        print("\n\nSample from response34.json (first 10 rows):")
        print(dataframes['response34.json'].head(10))

