from engine.curriculum import CurriculumCreator

def test_curriculum_generation_refactor():
    creator = CurriculumCreator("Refactor our shared database connections")
    tasks = creator.generate_curriculum()
    
    assert len(tasks) == 4
    assert tasks[0]["id"] == "step_1"
    assert "Locate duplicate" in tasks[0]["description"]

def test_curriculum_generation_default():
    creator = CurriculumCreator("Audit the code security parameters")
    tasks = creator.generate_curriculum()
    
    assert len(tasks) == 3
    assert "Formulate technical" in tasks[1]["description"]
