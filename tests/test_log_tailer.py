import os
import pytest
from tools.log_tailer import LogTailer

def test_log_tailer_reads_and_saves_offset(tmp_path):
    log_file = tmp_path / "test.log"
    offset_file = tmp_path / "test.log.offset"
    
    # Write initial logs
    with open(log_file, "w") as f:
        f.write("Line 1\nLine 2\n")
        
    tailer = LogTailer(str(log_file), str(offset_file))
    lines = list(tailer.tail())
    
    assert lines == ["Line 1\n", "Line 2\n"]
    assert os.path.exists(offset_file)
    
    # Check if offset matches file size
    with open(offset_file, "r") as f:
        parts = f.read().strip().split(",")
        offset = int(parts[1]) if len(parts) == 2 else int(parts[0])
        assert offset > 0
        
    # Append more logs and read again (should only read new lines)
    with open(log_file, "a") as f:
        f.write("Line 3\n")
        
    new_lines = list(tailer.tail())
    assert new_lines == ["Line 3\n"]

def test_log_tailer_handles_rotation(tmp_path):
    log_file = tmp_path / "test.log"
    offset_file = tmp_path / "test.log.offset"
    
    # Write initial logs
    with open(log_file, "w") as f:
        f.write("Old Line 1\n")
        
    tailer = LogTailer(str(log_file), str(offset_file))
    list(tailer.tail()) # Saves offset
    
    # Rotate: delete and recreate file (this changes the inode!)
    os.remove(log_file)
    with open(log_file, "w") as f:
        f.write("New Line 1\n")
        
    lines = list(tailer.tail())
    assert lines == ["New Line 1\n"]
