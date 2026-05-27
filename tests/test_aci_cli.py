import os
from tools.aci_cli import ACIEngine

def test_aci_list_files(tmp_path):
    # Setup mock workspace files
    (tmp_path / "src").mkdir()
    with open(tmp_path / "src" / "main.py", "w") as f:
        f.write("print('test')\n")
    with open(tmp_path / "README.md", "w") as f:
        f.write("# Hello\n")
        
    aci = ACIEngine(str(tmp_path))
    files = aci.list_files()
    
    assert "README.md" in files
    assert "src/main.py" in files

def test_aci_read_file_lines(tmp_path):
    target = tmp_path / "lines.txt"
    with open(target, "w") as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\n")
        
    aci = ACIEngine(str(tmp_path))
    lines = aci.read_file_lines("lines.txt", start=2, end=3)
    
    assert lines == ["Line 2\n", "Line 3\n"]
