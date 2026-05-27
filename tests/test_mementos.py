import os
from tools.mementos import ReflectiveMementos

def test_mementos_add_and_query(tmp_path):
    memento_file = tmp_path / "reflections.json"
    mementos = ReflectiveMementos(str(memento_file))
    
    # Save a reflection
    mementos.add_reflection("Infinite loops on pytest fail", "Bound maximum iterations to 3 using an FSM loop guard")
    
    # Re-instantiate and query
    mementos2 = ReflectiveMementos(str(memento_file))
    results = mementos2.query_reflection("pytest")
    
    assert len(results) == 1
    assert "FSM loop guard" in results[0]["solution"]
