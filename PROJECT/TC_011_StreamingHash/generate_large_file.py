import os

def generate_large_file(file_path, target_size_mb):
    target_size_bytes = target_size_mb * 1024 * 1024
    line_content = "This is a repeating line to make the file large. " * 10 # ~500 bytes per line
    
    print(f"Generating large file: {file_path} (Target size: {target_size_mb} MB)")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        current_size = 0
        while current_size < target_size_bytes:
            f.write(line_content + "\n")
            current_size += len(line_content.encode('utf-8')) + 1 # +1 for newline character
            if current_size % (10 * 1024 * 1024) < len(line_content.encode('utf-8')): # Print progress every 10MB
                print(f"  {current_size / (1024 * 1024):.2f} MB written...")
    
    print(f"File generation complete. Actual size: {os.path.getsize(file_path) / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    output_dir = "E:\\SourceAnalyzer.git\\PROJECT\\TC_011_StreamingHash"
    output_file = os.path.join(output_dir, "LargeFile.txt")
    
    # Set your desired file size in MB here
    target_size_mb = 100 # Example: 100 MB. Adjust as needed.
    
    os.makedirs(output_dir, exist_ok=True)
    generate_large_file(output_file, target_size_mb)
