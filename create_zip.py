import zipfile
import os
import sys

def create_zip(source_dir, output_file):
    """Create a zip archive from a directory"""
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)
                print(f"Added {arcname}")
    print(f"Created {output_file}")
    return output_file

if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "dist/windows/amd64/opensuperwhisper-v0.7.0-windows-amd64"
    output = sys.argv[2] if len(sys.argv) > 2 else "dist/windows/amd64/opensuperwhisper-v0.7.0-windows-amd64.zip"
    create_zip(source, output)