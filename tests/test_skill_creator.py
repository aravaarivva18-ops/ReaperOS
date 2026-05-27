import os
import pytest
from tools.skill_creator import save_dynamic_skill, SkillCreationError

def test_save_dynamic_skill_success():
    code = """def execute():
    return "Hello from dynamic skill"
"""
    path = save_dynamic_skill("testsynth", code)
    assert os.path.exists(path)
    
    try:
        # Import the dynamically created skill
        import sys
        sys.path.append(os.path.dirname(path))
        import dynamic_skill_testsynth as skill
        assert skill.execute() == "Hello from dynamic skill"
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_save_dynamic_skill_syntax_error():
    bad_code = "def execute(: print('broken syntax')"
    with pytest.raises(SkillCreationError):
        save_dynamic_skill("bad", bad_code)
