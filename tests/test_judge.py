from tools.judge import CodeJudge

def test_code_judge_clean_code():
    judge = CodeJudge()
    code = """def connect_db():
    import sqlite3
    return sqlite3.connect("db.sqlite")
"""
    res = judge.evaluate_code("db.py", code)
    assert res["passed"] is True
    assert res["score"] == 100
    assert len(res["violations"]) == 0

def test_code_judge_violations():
    judge = CodeJudge()
    bad_code = """def connect():
    api_key = "12345-SUPER-SECRET" # violation
    pass # violation
"""
    res = judge.evaluate_code("secret.py", bad_code)
    assert res["passed"] is False
    assert res["score"] < 70
    assert len(res["violations"]) == 2
