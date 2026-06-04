import json
import re
from importlib.resources import files


def _d(name):
    return files("mcp_unione.data").joinpath(name).read_text("utf-8")


def test_manifest_has_expected_slugs():
    m = json.loads(_d("manifest.json"))
    slugs = {e["slug"] for e in m}
    assert {
        "web-api-reference",
        "email-send-params",
        "template-velocity",
        "email-statuses",
        "error-codes",
        "suppression-lists",
    } <= slugs


def test_errors_table_nonempty_and_has_101():
    e = json.loads(_d("errors.json"))
    assert "101" in e and "fix" in e["101"]


def test_statuses_has_delivered_and_extended():
    s = json.loads(_d("statuses.json"))
    assert "delivered" in s["statuses"] and "err_user_unknown" in s["delivery_status"]


def test_no_stray_header_keys_in_statuses():
    s = json.loads(_d("statuses.json"))
    assert "delivery_status" not in s["delivery_status"], "stray header row in delivery_status bucket"
    for bucket, entries in s.items():
        bad = [k for k in entries if not re.match(r'^[a-z][a-z0-9_]*$', k)]
        assert not bad, f"{bucket} has non-snake-case key(s): {bad}"


def test_manifest_count_and_fields():
    m = json.loads(_d("manifest.json"))
    assert len(m) == 20
    for e in m:
        assert {"slug","title","url","keywords","summary"} <= set(e)


def test_errors_table_substantial():
    e = json.loads(_d("errors.json"))
    assert len(e) >= 100
