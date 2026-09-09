"""Create a ZIP from the sample project for testing."""
import zipfile
import os
from pathlib import Path

def create_sample_zip():
    sample_dir = Path(__file__).parent.parent / "sample-projects" / "demo-project"
    output_path = Path(__file__).parent.parent / "backend" / "tests" / "fixtures" / "demo-project.zip"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(sample_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(sample_dir.parent)
                zf.write(file_path, arcname)
    
    print(f"Created {output_path} ({output_path.stat().st_size} bytes)")

if __name__ == "__main__":
    create_sample_zip()
