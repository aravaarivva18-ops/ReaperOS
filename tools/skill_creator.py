# -*- coding: utf-8 -*-
"""
Dynamic Skills Creator for ReaperOS.
Allows the agent to dynamically register and persist new executable Python skills.
"""

import os
import sys

class SkillCreationError(Exception):
    pass

def save_dynamic_skill(name: str, code: str) -> str:
    """
    Validates Python code syntax and saves it as a dynamic skill in the tools/ directory.
    Returns the absolute path of the generated skill file.
    """
    if not name.isalnum():
        raise SkillCreationError("Skill name must be alphanumeric")

    # Validate Python syntax
    try:
        compile(code, "<string>", "exec")
    except Exception as e:
        raise SkillCreationError(f"Syntax validation failed: {e}")

    tools_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = f"dynamic_skill_{name}.py"
    target_path = os.path.join(tools_dir, file_name)

    try:
        with open(target_path, "w") as f:
            f.write("# -*- coding: utf-8 -*-\n")
            f.write(f'"""Dynamic Skill: {name}"""\n\n')
            f.write(code)
        return target_path
    except Exception as e:
        raise SkillCreationError(f"Failed to write skill file: {e}")
