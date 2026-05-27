import pytest
from engine.checkpoints import StateCheckpointer

def test_checkpointer_save_and_rollback():
    checkpointer = StateCheckpointer()
    state = {"step": 1, "data": "initial"}
    
    # Save checkpoint
    checkpointer.create_checkpoint("chk1", state)
    
    # Mutate state
    state["step"] = 2
    state["data"] = "mutated"
    checkpointer.create_checkpoint("chk2", state)
    
    # Rollback to chk1
    restored = checkpointer.rollback_to("chk1")
    assert restored["step"] == 1
    assert restored["data"] == "initial"
    assert len(checkpointer.history) == 1

def test_checkpointer_missing_checkpoint():
    checkpointer = StateCheckpointer()
    with pytest.raises(KeyError):
        checkpointer.rollback_to("non_existent")
