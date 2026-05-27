import pytest
from engine.rag_engine import LocalRAGEngine

def test_rag_engine_index_and_search():
    engine = LocalRAGEngine()
    
    # Index some mock docs
    engine.index_document(
        doc_id="doc1",
        content="ReaperOS is a self-healing agentic runtime operating system.\n\nIt handles processes using Python and SQLite."
    )
    engine.index_document(
        doc_id="doc2",
        content="Apple is a tech company making premium hardware.\n\nThey designed the Mac Studio."
    )
    
    # Query for operating system details
    results = engine.search("What is ReaperOS?", top_k=1)
    
    assert len(results) == 1
    assert results[0]["doc_id"] == "doc1"
    assert "self-healing agentic runtime" in results[0]["text"]
