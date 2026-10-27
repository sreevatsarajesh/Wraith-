from wraith.core import fallback, GHOSTS

def test_known_ghosts():
    assert {"geocities", "fortran", "deleted-file"} <= set(GHOSTS)

def test_failure_fallback_is_ghostly():
    assert "👻" in fallback("fortran", "pytest", 1)

def test_deleted_file_fallback_does_not_claim_contents():
    text = fallback("deleted-file", "rm notes.txt", 0)
    assert "contents" in text.lower() or "absence" in text.lower() or "disappearance" in text.lower()
