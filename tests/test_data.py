import json
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
