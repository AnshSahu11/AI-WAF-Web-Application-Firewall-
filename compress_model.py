import gzip
import shutil
import os

source_file = "models/isolation_forest.pkl"
target_file = "models/isolation_forest.pkl.gz"

if os.path.exists(source_file):
    print(f"Compressing {source_file}...")
    with open(source_file, 'rb') as f_in:
        with gzip.open(target_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    src_size = os.path.getsize(source_file) / (1024 * 1024)
    target_size = os.path.getsize(target_file) / (1024 * 1024)
    print(f"Original: {src_size:.2f} MB")
    print(f"Compressed: {target_size:.2f} MB")
else:
    print("Source file not found.")
