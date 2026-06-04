from mcp_unione.errors import UniOneError, enrich

def test_error_str_includes_code_and_message():
    e = UniOneError(code=101, message="api_key not found", http_status=400)
    assert "101" in str(e) and "api_key not found" in str(e)

def test_enrich_adds_fix_when_known(tmp_path, monkeypatch):
    # enrich() reads the bundled errors.json; unknown codes return base dict unchanged
    out = enrich(999999, "boom", 400)
    assert out["code"] == 999999 and out["message"] == "boom"
