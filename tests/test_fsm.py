import pytest
from engine.fsm import ReaperFSM, FSMError, InfiniteLoopError

def test_fsm_happy_path():
    fsm = ReaperFSM()
    assert fsm.state == "IDLE"
    
    fsm.transition_to("ANALYZING")
    assert fsm.state == "ANALYZING"
    
    fsm.transition_to("CODING")
    assert fsm.state == "CODING"
    
    fsm.transition_to("VERIFYING")
    assert fsm.state == "VERIFYING"
    
    fsm.transition_to("STABLE")
    assert fsm.state == "STABLE"

def test_fsm_invalid_transition():
    fsm = ReaperFSM()
    with pytest.raises(FSMError):
        fsm.transition_to("CODING")

def test_fsm_loop_detection():
    fsm = ReaperFSM(max_loops=2)
    
    # First correction loop
    fsm.transition_to("ANALYZING")
    fsm.transition_to("CODING")
    fsm.transition_to("VERIFYING")
    
    # Back to analyzing (loop_count = 1)
    fsm.transition_to("ANALYZING")
    fsm.transition_to("CODING")
    fsm.transition_to("VERIFYING")
    
    # Back to analyzing again (loop_count = 2 -> ESCALATED)
    with pytest.raises(InfiniteLoopError):
        fsm.transition_to("ANALYZING")
        
    assert fsm.state == "ESCALATED"
