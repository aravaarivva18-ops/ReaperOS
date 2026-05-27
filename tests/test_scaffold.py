from engine.scaffold import EvolutionScaffold

def test_scaffold_adaptation():
    scaffold = EvolutionScaffold()
    assert scaffold.get_system_prompt_addition() == ""
    
    # Adapt to timeout error
    strategy = scaffold.adapt_to_error("Task Timeout expired after 5 seconds")
    assert strategy == "AGGRESSIVE_TIMEOUT_GATING"
    
    prompt = scaffold.get_system_prompt_addition()
    assert "Code execution is timing out" in prompt

def test_scaffold_adaptation_permission():
    scaffold = EvolutionScaffold()
    
    # Adapt to permission error
    strategy = scaffold.adapt_to_error("Permission denied to write to /root")
    assert strategy == "SAFE_SANDBOX_ISOLATION"
    
    prompt = scaffold.get_system_prompt_addition()
    assert "SAFE_SANDBOX_ISOLATION" in scaffold.active_strategies
    assert "isolated sandboxes" in prompt
