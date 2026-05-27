import os
from tools.skill_registry import SkillRegistry

def test_skill_registry_register_and_get(tmp_path):
    registry_file = tmp_path / "skills.json"
    registry = SkillRegistry(str(registry_file))
    
    # Register mock skill
    registry.register_skill("mock_skill", "This is a mock skill description", "/path/to/skill.py")
    
    # Load again to verify persistence
    registry2 = SkillRegistry(str(registry_file))
    skill = registry2.get_skill("mock_skill")
    
    assert skill is not None
    assert skill["description"] == "This is a mock skill description"
    assert skill["file_path"] == "/path/to/skill.py"
