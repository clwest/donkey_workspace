from assistants.utils.thought_integrity import analyze_thought_integrity


def test_analyze_thought_integrity():
    assert analyze_thought_integrity("") == "empty"
    assert analyze_thought_integrity("   ") == "empty"
    assert analyze_thought_integrity("```json") == "markdown_stub"
    assert analyze_thought_integrity("ERROR: something") == "error_log"
    assert analyze_thought_integrity("This is a valid thought.") == "valid"
